"""
Domain discovery module for finding websites associated with Norwegian companies.
"""

import requests
import re
import socket
import whois
from typing import List, Set, Optional
import logging
from urllib.parse import urlparse, urljoin
import time

logger = logging.getLogger(__name__)


class DomainFinder:
    """Finds domains associated with Norwegian companies."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Norwegian-Companies-Domain-Finder/1.0'
        })
        self.session.timeout = 10
    
    def find_domains_for_company(self, company_data: dict) -> Set[str]:
        """
        Find all domains associated with a company.
        
        Args:
            company_data: Company data from BRREG
            
        Returns:
            Set of unique domains
        """
        domains = set()
        
        company_name = company_data.get('navn', '')
        org_number = company_data.get('organisasjonsnummer', '')
        
        logger.info(f"Finding domains for {company_name} ({org_number})")
        
        # Try different approaches to find domains
        domains.update(self._guess_domains_from_name(company_name))
        domains.update(self._search_whois_by_org_number(org_number))
        domains.update(self._search_common_patterns(company_name))
        
        # Verify domains are actually accessible
        verified_domains = set()
        for domain in domains:
            if self._verify_domain(domain):
                verified_domains.add(domain)
        
        return verified_domains
    
    def _guess_domains_from_name(self, company_name: str) -> Set[str]:
        """
        Generate potential domain names from company name.
        
        Args:
            company_name: Company name
            
        Returns:
            Set of potential domains
        """
        if not company_name:
            return set()
        
        domains = set()
        
        # Clean company name
        clean_name = re.sub(r'\s+', '', company_name.lower())
        clean_name = re.sub(r'[^a-z0-9]', '', clean_name)
        
        # Remove common Norwegian company suffixes
        suffixes_to_remove = ['as', 'asa', 'ba', 'da', 'iks', 'ks', 'nuf', 'sa', 'sf']
        for suffix in suffixes_to_remove:
            if clean_name.endswith(suffix):
                clean_name = clean_name[:-len(suffix)]
                break
        
        if len(clean_name) >= 3:  # Avoid very short names
            # Try common Norwegian TLDs
            tlds = ['.no', '.com', '.org', '.net']
            for tld in tlds:
                domains.add(f"{clean_name}{tld}")
        
        return domains
    
    def _search_whois_by_org_number(self, org_number: str) -> Set[str]:
        """
        Search for domains registered to the organization number.
        
        Args:
            org_number: Norwegian organization number
            
        Returns:
            Set of domains found
        """
        domains = set()
        
        # This is a placeholder - in practice, you might need access to
        # specialized WHOIS databases or services that allow reverse lookup
        # by organization number
        
        return domains
    
    def _search_common_patterns(self, company_name: str) -> Set[str]:
        """
        Search for domains using common naming patterns.
        
        Args:
            company_name: Company name
            
        Returns:
            Set of potential domains
        """
        domains = set()
        
        if not company_name:
            return domains
        
        # Extract words from company name
        words = re.findall(r'\b[a-zA-Z]+\b', company_name.lower())
        
        if len(words) >= 1:
            # Single word
            main_word = words[0]
            if len(main_word) >= 3:
                domains.add(f"{main_word}.no")
                domains.add(f"{main_word}.com")
        
        if len(words) >= 2:
            # Two words combined
            combined = ''.join(words[:2])
            if len(combined) >= 4:
                domains.add(f"{combined}.no")
                domains.add(f"{combined}.com")
            
            # Two words with dash
            dashed = '-'.join(words[:2])
            domains.add(f"{dashed}.no")
            domains.add(f"{dashed}.com")
        
        return domains
    
    def _verify_domain(self, domain: str) -> bool:
        """
        Verify if a domain exists and is accessible.
        
        Args:
            domain: Domain to verify
            
        Returns:
            True if domain is accessible
        """
        try:
            # First check DNS resolution
            socket.gethostbyname(domain)
            
            # Then try HTTP request
            try:
                response = self.session.head(f"http://{domain}", timeout=5)
                return True
            except:
                try:
                    response = self.session.head(f"https://{domain}", timeout=5)
                    return True
                except:
                    pass
            
            # If HTTP fails but DNS works, still consider it valid
            return True
            
        except (socket.gaierror, socket.timeout, requests.RequestException):
            return False
    
    def find_domains_from_website(self, website_url: str) -> Set[str]:
        """
        Extract additional domains from a company's main website.
        
        Args:
            website_url: Main website URL
            
        Returns:
            Set of additional domains found
        """
        domains = set()
        
        try:
            response = self.session.get(website_url, timeout=10)
            if response.status_code == 200:
                # Look for additional domains in the page content
                domain_pattern = r'https?://([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
                found_domains = re.findall(domain_pattern, response.text)
                
                for domain in found_domains:
                    # Filter to keep only relevant domains (Norwegian or related)
                    if any(tld in domain for tld in ['.no', '.com', '.org', '.net']):
                        domains.add(domain)
        
        except requests.RequestException as e:
            logger.debug(f"Could not fetch {website_url}: {e}")
        
        return domains
