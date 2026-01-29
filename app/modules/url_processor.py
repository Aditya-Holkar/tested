# modules/url_processor.py - URL processing utilities
import re
from urllib.parse import urlparse, urljoin, urldefrag
import requests
from bs4 import BeautifulSoup
import time

class URLProcessor:
    """Handle URL processing and extraction"""
    
    @staticmethod
    def normalize_url(url):
        """Normalize URL by adding protocol if missing"""
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        return url
    
    @staticmethod
    def get_base_url(url):
        """Get base URL without fragments, query parameters, and trailing slash."""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            if base_url.endswith('/'):
                base_url = base_url.rstrip('/')
            return base_url
        except:
            return url.lower().strip()
    
    @staticmethod
    def is_duplicate_url(url, url_list):
        """Check if a URL is duplicate in the list."""
        url = url.lower().strip()
        if url.endswith('/'):
            url = url.rstrip('/')
        
        url_no_protocol = re.sub(r'^https?://', '', url)
        
        for existing_url in url_list:
            existing = existing_url.lower().strip()
            if existing.endswith('/'):
                existing = existing.rstrip('/')
            
            existing_no_protocol = re.sub(r'^https?://', '', existing)
            
            if (url == existing or 
                url_no_protocol == existing_no_protocol or
                url == existing.replace('https://', 'http://') or
                url.replace('https://', 'http://') == existing):
                return True
            
            if URLProcessor.get_base_url(url) == URLProcessor.get_base_url(existing):
                return True
        
        return False
    
    @staticmethod
    def remove_duplicate_urls(url_list):
        """Remove duplicate URLs from a list."""
        unique_urls = []
        seen_bases = set()
        
        for url in url_list:
            base_url = URLProcessor.get_base_url(url)
            if base_url not in seen_bases:
                seen_bases.add(base_url)
                unique_urls.append(url)
        
        return unique_urls
    
    @staticmethod
    def scrape_all_links(base_url, max_depth=2, max_links=1000):
        """Recursively scrape links from website with duplicate checking."""
        from modules.url_processor import URLProcessor
        
        visited = set()
        to_visit = [(base_url, 0)]
        all_links = set()
        
        while to_visit and len(all_links) < max_links:
            url, depth = to_visit.pop(0)
            
            if url in visited or depth > max_depth:
                continue
                
            visited.add(url)
            
            try:
                parsed = urlparse(url)
                response = requests.get(url, timeout=10, verify=False)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract all links
                for link in soup.find_all(['a', 'link', 'script', 'img'], href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    full_url = urldefrag(full_url)[0]  # Remove fragments
                    
                    # Filter relevant links
                    if URLProcessor.is_relevant_link(full_url, base_url):
                        all_links.add(full_url)
                
                # Also extract paths from forms
                for form in soup.find_all('form', action=True):
                    action = form['action']
                    full_url = urljoin(url, action)
                    if URLProcessor.is_relevant_link(full_url, base_url):
                        all_links.add(full_url)
                
                time.sleep(0.5)  # Be respectful
                
            except:
                continue
        
        # Convert to list
        links_list = list(all_links)[:max_links]
        # Remove any remaining duplicates
        links_list = URLProcessor.remove_duplicate_urls(links_list)
        
        return links_list
    
    @staticmethod
    def is_relevant_link(link, base_url):
        """Filter relevant links for same domain."""
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link).netloc
        
        # Same domain or subdomain
        if base_domain == link_domain or link_domain.endswith('.' + base_domain):
            return True
        
        # Common paths/files (even cross-domain if useful)
        path = urlparse(link).path.lower()
        useful_extensions = ['.php', '.asp', '.aspx', '.jsp', '.html', '.htm']
        if any(path.endswith(ext) for ext in useful_extensions) or not path.endswith('/'):
            return True
        
        return False