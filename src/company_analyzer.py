"""
Company analysis module for processing Norwegian companies and finding revenue data.
"""

import requests
import re
from typing import List, Dict, Optional
import logging
import time

logger = logging.getLogger(__name__)


class CompanyAnalyzer:
    """Analyzes Norwegian companies to extract revenue and other financial data."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Norwegian-Companies-Analyzer/1.0'
        })
    
    def enrich_company_data(self, company: Dict) -> Dict:
        """
        Enrich company data with additional information including revenue estimates.
        
        Args:
            company: Basic company data from BRREG
            
        Returns:
            Enriched company data
        """
        enriched = company.copy()
        
        # Add estimated revenue (placeholder - in real implementation,
        # this could use various data sources)
        revenue_estimate = self._estimate_revenue(company)
        enriched['estimated_revenue'] = revenue_estimate
        
        # Add company size classification
        enriched['size_category'] = self._classify_company_size(company)
        
        # Add industry classification
        enriched['industry_category'] = self._get_industry_category(company)
        
        return enriched
    
    def _estimate_revenue(self, company: Dict) -> Optional[int]:
        """
        Estimate company revenue based on available data.
        
        Note: This is a simplified estimation. In practice, you would use:
        - Publicly available financial reports
        - Industry databases
        - Employee count correlations
        - Other business intelligence sources
        
        Args:
            company: Company data
            
        Returns:
            Estimated revenue in NOK or None
        """
        # Get number of employees if available
        employees = company.get('antallAnsatte')
        
        if employees is None:
            return None
        
        # Very rough revenue estimation based on employee count
        # These are just placeholder calculations
        if employees == 0:
            return 1000000  # 1M NOK for very small companies
        elif employees <= 10:
            return employees * 2000000  # 2M NOK per employee for small companies
        elif employees <= 50:
            return employees * 1500000  # 1.5M NOK per employee for medium companies
        elif employees <= 250:
            return employees * 1200000  # 1.2M NOK per employee for larger companies
        else:
            return employees * 1000000  # 1M NOK per employee for large companies
    
    def _classify_company_size(self, company: Dict) -> str:
        """
        Classify company size based on employee count.
        
        Args:
            company: Company data
            
        Returns:
            Size category string
        """
        employees = company.get('antallAnsatte', 0)
        
        if employees == 0:
            return 'micro'
        elif employees <= 10:
            return 'small'
        elif employees <= 50:
            return 'medium'
        elif employees <= 250:
            return 'large'
        else:
            return 'very_large'
    
    def _get_industry_category(self, company: Dict) -> str:
        """
        Get simplified industry category from NACE code.
        
        Args:
            company: Company data
            
        Returns:
            Industry category string
        """
        nace_code = company.get('naeringskode1', {}).get('kode', '')
        
        if not nace_code:
            return 'unknown'
        
        # Simplified NACE code mapping
        code_num = nace_code[:2] if len(nace_code) >= 2 else ''
        
        industry_mapping = {
            '01': 'agriculture',
            '02': 'agriculture', 
            '03': 'agriculture',
            '05': 'mining',
            '06': 'mining',
            '07': 'mining',
            '08': 'mining',
            '09': 'mining',
            '10': 'manufacturing',
            '11': 'manufacturing',
            '12': 'manufacturing',
            '13': 'manufacturing',
            '14': 'manufacturing',
            '15': 'manufacturing',
            '16': 'manufacturing',
            '17': 'manufacturing',
            '18': 'manufacturing',
            '19': 'manufacturing',
            '20': 'manufacturing',
            '21': 'manufacturing',
            '22': 'manufacturing',
            '23': 'manufacturing',
            '24': 'manufacturing',
            '25': 'manufacturing',
            '26': 'manufacturing',
            '27': 'manufacturing',
            '28': 'manufacturing',
            '29': 'manufacturing',
            '30': 'manufacturing',
            '31': 'manufacturing',
            '32': 'manufacturing',
            '33': 'manufacturing',
            '35': 'utilities',
            '36': 'utilities',
            '37': 'utilities',
            '38': 'utilities',
            '39': 'utilities',
            '41': 'construction',
            '42': 'construction',
            '43': 'construction',
            '45': 'trade',
            '46': 'trade',
            '47': 'trade',
            '49': 'transport',
            '50': 'transport',
            '51': 'transport',
            '52': 'transport',
            '53': 'transport',
            '55': 'accommodation',
            '56': 'accommodation',
            '58': 'information',
            '59': 'information',
            '60': 'information',
            '61': 'information',
            '62': 'information',
            '63': 'information',
            '64': 'finance',
            '65': 'finance',
            '66': 'finance',
            '68': 'real_estate',
            '69': 'professional',
            '70': 'professional',
            '71': 'professional',
            '72': 'professional',
            '73': 'professional',
            '74': 'professional',
            '75': 'professional',
            '77': 'services',
            '78': 'services',
            '79': 'services',
            '80': 'services',
            '81': 'services',
            '82': 'services',
            '84': 'public',
            '85': 'education',
            '86': 'health',
            '87': 'health',
            '88': 'health',
            '90': 'arts',
            '91': 'arts',
            '92': 'arts',
            '93': 'arts',
            '94': 'other',
            '95': 'other',
            '96': 'other',
            '97': 'other',
            '98': 'other',
            '99': 'other',
        }
        
        return industry_mapping.get(code_num, 'other')
    
    def filter_large_companies(self, companies: List[Dict], min_employees: int = 10) -> List[Dict]:
        """
        Filter companies to include only larger ones.
        
        Args:
            companies: List of company data
            min_employees: Minimum number of employees
            
        Returns:
            Filtered list of companies
        """
        filtered = []
        
        for company in companies:
            employees = company.get('antallAnsatte')
            if employees is not None and employees >= min_employees:
                filtered.append(company)
        
        return filtered
    
    def sort_by_revenue_estimate(self, companies: List[Dict]) -> List[Dict]:
        """
        Sort companies by estimated revenue (highest first).
        
        Args:
            companies: List of enriched company data
            
        Returns:
            Sorted list of companies
        """
        def get_revenue(company):
            revenue = company.get('estimated_revenue')
            return revenue if revenue is not None else 0
        
        return sorted(companies, key=get_revenue, reverse=True)
