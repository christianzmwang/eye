#!/usr/bin/env python3
"""
Norwegian Companies Domain Finder

Finds websites associated with the 1000 biggest Norwegian private companies
by revenue, using data from BRREG (Brønnøysundregistrene).

Output format:
- Organization number
- Name of business  
- Unique domains associated with the organization number
"""

import json
import csv
import logging
import argparse
from datetime import datetime
from typing import List, Dict
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from brreg_client import BRREGClient
from domain_finder import DomainFinder
from company_analyzer import CompanyAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('norwegian_companies.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Find domains for top Norwegian companies')
    parser.add_argument('--max-companies', type=int, default=1000, 
                       help='Maximum number of companies to process (default: 1000)')
    parser.add_argument('--output-format', choices=['json', 'csv'], default='json',
                       help='Output format (default: json)')
    parser.add_argument('--output-file', type=str, default='norwegian_companies_domains.json',
                       help='Output file name')
    parser.add_argument('--min-employees', type=int, default=10,
                       help='Minimum number of employees to filter companies (default: 10)')
    
    args = parser.parse_args()
    
    logger.info(f"Starting Norwegian Companies Domain Finder")
    logger.info(f"Target: {args.max_companies} companies")
    logger.info(f"Minimum employees: {args.min_employees}")
    logger.info(f"Output format: {args.output_format}")
    
    # Initialize clients
    brreg_client = BRREGClient()
    domain_finder = DomainFinder()
    company_analyzer = CompanyAnalyzer()
    
    # Step 1: Fetch companies from BRREG
    logger.info("Step 1: Fetching companies from BRREG...")
    all_companies = brreg_client.search_active_companies(max_companies=args.max_companies * 3)
    
    if not all_companies:
        logger.error("No companies found. Exiting.")
        return
    
    logger.info(f"Found {len(all_companies)} active companies")
    
    # Step 2: Filter for larger companies (likely to have higher revenue)
    logger.info("Step 2: Filtering for larger companies...")
    large_companies = company_analyzer.filter_large_companies(
        all_companies, 
        min_employees=args.min_employees
    )
    
    logger.info(f"Found {len(large_companies)} companies with {args.min_employees}+ employees")
    
    # Step 3: Enrich company data with revenue estimates
    logger.info("Step 3: Analyzing companies and estimating revenue...")
    enriched_companies = []
    
    for i, company in enumerate(large_companies):
        if i % 100 == 0:
            logger.info(f"Processed {i}/{len(large_companies)} companies...")
        
        enriched = company_analyzer.enrich_company_data(company)
        enriched_companies.append(enriched)
    
    # Step 4: Sort by estimated revenue
    logger.info("Step 4: Sorting companies by estimated revenue...")
    sorted_companies = company_analyzer.sort_by_revenue_estimate(enriched_companies)
    
    # Take top companies
    top_companies = sorted_companies[:args.max_companies]
    logger.info(f"Selected top {len(top_companies)} companies by estimated revenue")
    
    # Step 5: Find domains for each company
    logger.info("Step 5: Finding domains for companies...")
    results = []
    
    for i, company in enumerate(top_companies):
        logger.info(f"Processing {i+1}/{len(top_companies)}: {company.get('navn', 'Unknown')}")
        
        # Find domains
        domains = domain_finder.find_domains_for_company(company)
        
        # Create result entry
        result = {
            'organization_number': company.get('organisasjonsnummer', ''),
            'business_name': company.get('navn', ''),
            'unique_domains': list(domains),
            'estimated_revenue': company.get('estimated_revenue'),
            'employees': company.get('antallAnsatte'),
            'industry': company.get('industry_category', 'unknown'),
            'municipality': company.get('forretningsadresse', {}).get('kommune', ''),
            'founded': company.get('stiftelsesdato', ''),
            'nace_code': company.get('naeringskode1', {}).get('kode', '')
        }
        
        results.append(result)
        
        # Print progress
        if domains:
            logger.info(f"  Found domains: {', '.join(list(domains)[:3])}{'...' if len(domains) > 3 else ''}")
        else:
            logger.info(f"  No domains found")
    
    # Step 6: Save results
    logger.info(f"Step 6: Saving results to {args.output_file}...")
    
    if args.output_format == 'json':
        save_json_results(results, args.output_file)
    else:
        save_csv_results(results, args.output_file)
    
    # Print summary
    total_domains = sum(len(result['unique_domains']) for result in results)
    companies_with_domains = sum(1 for result in results if result['unique_domains'])
    
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Total companies processed: {len(results)}")
    logger.info(f"Companies with domains found: {companies_with_domains}")
    logger.info(f"Total unique domains found: {total_domains}")
    logger.info(f"Average domains per company: {total_domains / len(results):.2f}")
    logger.info(f"Results saved to: {args.output_file}")
    
    # Print top 10 results as preview
    logger.info("\nTOP 10 COMPANIES BY ESTIMATED REVENUE:")
    logger.info("-" * 80)
    for i, result in enumerate(results[:10]):
        domains_str = ', '.join(result['unique_domains'][:2])
        if len(result['unique_domains']) > 2:
            domains_str += f" (+{len(result['unique_domains']) - 2} more)"
        
        logger.info(f"{i+1:2d}. {result['business_name'][:40]:<40} | {result['organization_number']} | {domains_str}")


def save_json_results(results: List[Dict], filename: str):
    """Save results to JSON file."""
    output_data = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_companies': len(results),
            'total_domains': sum(len(result['unique_domains']) for result in results)
        },
        'companies': results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)


def save_csv_results(results: List[Dict], filename: str):
    """Save results to CSV file."""
    # Change extension to .csv
    if filename.endswith('.json'):
        filename = filename.replace('.json', '.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow([
            'Organization Number',
            'Business Name', 
            'Unique Domains',
            'Domain Count',
            'Estimated Revenue (NOK)',
            'Employees',
            'Industry',
            'Municipality',
            'Founded',
            'NACE Code'
        ])
        
        # Write data
        for result in results:
            domains_str = '; '.join(result['unique_domains'])
            writer.writerow([
                result['organization_number'],
                result['business_name'],
                domains_str,
                len(result['unique_domains']),
                result['estimated_revenue'],
                result['employees'],
                result['industry'],
                result['municipality'],
                result['founded'],
                result['nace_code']
            ])


if __name__ == '__main__':
    main()
