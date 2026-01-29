# modules/link_checker.py - Link status checking (UPDATED)
import requests
import time
from datetime import datetime
from urllib.parse import urlparse
import concurrent.futures

class LinkChecker:
    """Handle link status checking"""
    
    def __init__(self, test_case_manager=None):
        """Initialize LinkChecker with optional test case manager"""
        self.test_case_manager = test_case_manager
    
    def check_status(self, url):
        """Check HTTP status of a URL"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                url = "http://" + url
            
            start_time = time.time()
            response = requests.get(url, timeout=8, allow_redirects=True, verify=False)
            response_time = int((time.time() - start_time) * 1000)
            
            status_code = response.status_code
            status_text = response.reason
            
            # Status categorization
            if 200 <= status_code < 300:
                status_category = "Success"
                status_emoji = "✅"
                test_status = "Pass"
                severity = "Low"
            elif 300 <= status_code < 400:
                status_category = "Redirect"
                status_emoji = "🔄"
                test_status = "Pass"
                severity = "Low"
            elif 400 <= status_code < 500:
                status_category = "Client Error"
                status_emoji = "❌"
                test_status = "Fail"
                severity = "High"
            else:
                status_category = "Server Error"
                status_emoji = "🚫"
                test_status = "Fail"
                severity = "Critical"
            
            result_display = f"{status_emoji} {status_code} ({response_time}ms) - {url}"
            
            result_structured = {
                'url': url,
                'status_code': status_code,
                'status_text': status_text,
                'status_category': status_category,
                'response_time_ms': response_time,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'final_url': response.url if hasattr(response, 'url') else url,
                'display_text': result_display
            }
            
            # Create test case if manager provided
            test_case = None
            if self.test_case_manager:
                test_case = self.test_case_manager.create_link_test_case(
                    url=url,
                    status_code=status_code,
                    status_text=status_text,
                    response_time=response_time,
                    status_category=status_category,
                    test_status=test_status,
                    severity=severity,
                    final_url=response.url if hasattr(response, 'url') else url
                )
            
            return result_display, result_structured, test_case
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e).split('\n')[0]
            result_display = f"❌ ERROR ({error_msg[:30]}...) - {url}"
            
            result_structured = {
                'url': url,
                'status_code': None,
                'status_text': error_msg,
                'status_category': 'Error',
                'response_time_ms': 0,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'final_url': url,
                'display_text': result_display
            }
            
            # Create test case for error if manager provided
            test_case = None
            if self.test_case_manager:
                test_case = self.test_case_manager.create_error_test_case(
                    url=url,
                    error_msg=error_msg,
                    test_type="Link Status Check"
                )
            
            return result_display, result_structured, test_case
    
    def test_links(self, urls, max_workers=10):
        """Test multiple links"""
        results = []
        test_cases = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_url = {executor.submit(self.check_status, url): url for url in urls}
            
            # Process completed tasks
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    result_display, result_structured, test_case = future.result()
                    results.append(result_structured)
                    if test_case:
                        test_cases.append(test_case)
                except Exception as e:
                    # Handle any exceptions from individual checks
                    error_result = {
                        'url': future_to_url[future],
                        'status_code': None,
                        'status_text': str(e),
                        'status_category': 'Error',
                        'response_time_ms': 0,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'final_url': future_to_url[future],
                        'display_text': f"❌ ERROR - {future_to_url[future]}"
                    }
                    results.append(error_result)
        
        return results, test_cases