"""
BRREG (Brønnøysundregistrene) API client for fetching Norwegian company data.
"""

import requests
import time
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BRREGClient:
    """Client for interacting with BRREG's Enhetsregisteret API."""
    
    BASE_URL = "https://data.brreg.no/enhetsregisteret/api"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Norwegian-Companies-Crawler/1.0'
        })
    
    def search_companies(self, query: str = "", page: int = 0, size: int = 20) -> Dict:
        """
        Search for companies in BRREG.
        
        Args:
            query: Search query (company name, org number, etc.)
            page: Page number (0-based)
            size: Number of results per page (max 20)
            
        Returns:
            Dict containing search results
        """
        url = f"{self.BASE_URL}/enheter"
        params = {
            'navn': query,
            'page': page,
            'size': min(size, 20)  # BRREG limits to 20 per page
        }
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error searching companies: {e}")
            return {}
    
    def get_company_by_org_number(self, org_number: str) -> Optional[Dict]:
        """
        Get company details by organization number.
        
        Args:
            org_number: Norwegian organization number
            
        Returns:
            Company data dict or None if not found
        """
        url = f"{self.BASE_URL}/enheter/{org_number}"
        
        try:
            response = self.session.get(url)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error fetching company {org_number}: {e}")
            return None
    
    def get_all_companies(self, max_pages: int = 100) -> List[Dict]:
        """
        Fetch all companies with pagination.
        
        Args:
            max_pages: Maximum number of pages to fetch
            
        Returns:
            List of company dictionaries
        """
        companies = []
        page = 0
        
        while page < max_pages:
            logger.info(f"Fetching page {page + 1}")
            result = self.search_companies(page=page, size=20)
            
            if not result or '_embedded' not in result:
                break
                
            page_companies = result['_embedded'].get('enheter', [])
            if not page_companies:
                break
                
            companies.extend(page_companies)
            
            # Check if there are more pages
            if page >= result.get('page', {}).get('totalPages', 0) - 1:
                break
                
            page += 1
            time.sleep(0.1)  # Be nice to the API
        
        logger.info(f"Fetched {len(companies)} companies total")
        return companies
    
    def search_active_companies(self, max_companies: int = 1000) -> List[Dict]:
        """
        Search for active companies (not deleted/dissolved).
        
        Args:
            max_companies: Maximum number of companies to return
            
        Returns:
            List of active company dictionaries
        """
        companies = []
        page = 0
        
        while len(companies) < max_companies:
            result = self.search_companies(page=page, size=20)
            
            if not result or '_embedded' not in result:
                break
                
            page_companies = result['_embedded'].get('enheter', [])
            if not page_companies:
                break
            
            # Filter for active companies
            for company in page_companies:
                if company.get('slettedato') is None:  # Not deleted
                    companies.append(company)
                    if len(companies) >= max_companies:
                        break
            
            # Check if there are more pages
            if page >= result.get('page', {}).get('totalPages', 0) - 1:
                break
                
            page += 1
            time.sleep(0.1)  # Be nice to the API
        
        logger.info(f"Found {len(companies)} active companies")
        return companies[:max_companies]
