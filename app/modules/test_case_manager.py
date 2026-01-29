# modules/test_case_manager.py - Test case management
from datetime import datetime
from config import TEST_CASE_COLUMNS

class TestCaseManager:
    """Manage test case creation and storage"""
    
    def __init__(self):
        self.test_cases = []
        self.test_case_counter = 1
    
    def create_test_case(self, **kwargs):
        """Create a standardized test case dictionary."""
        test_id = f"TC{self.test_case_counter:04d}"
        self.test_case_counter += 1
        
        # Determine pass/fail based on status
        status = kwargs.get('status', 'Not Run')
        case_pass_fail = "Pass" if status.lower() in ["pass", "passed"] else "Fail"
        
        test_case = {
            'Test ID': test_id,
            'Module': kwargs.get('module', 'Unknown'),
            'Test Links/Data': str(kwargs.get('test_data', ''))[:500],
            'Test Case Description': kwargs.get('description', ''),
            'Pre-Conditions': kwargs.get('pre_conditions', ''),
            'Test Steps': kwargs.get('test_steps', ''),
            'Expected Result': kwargs.get('expected_result', ''),
            'Actual Result': str(kwargs.get('actual_result', ''))[:500],
            'Status': status,
            'Severity': kwargs.get('severity', 'Medium'),
            'Case Pass/Fail': case_pass_fail,
            'Comments/Bug ID': kwargs.get('comments', ''),
            'Resolutions': kwargs.get('resolutions', ''),
            'Test Type': kwargs.get('test_type', ''),
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        self.test_cases.append(test_case)
        return test_case
    
    def create_link_test_case(self, **kwargs):
        """Create test case for link checking"""
        url = kwargs.get('url', '')
        status_code = kwargs.get('status_code', 0)
        status_text = kwargs.get('status_text', '')
        response_time = kwargs.get('response_time', 0)
        status_category = kwargs.get('status_category', '')
        test_status = kwargs.get('test_status', 'Fail')
        severity = kwargs.get('severity', 'Medium')
        final_url = kwargs.get('final_url', '')
        
        return self.create_test_case(
            test_type="Link Status Check",
            module="URL Validation",
            test_data=url,
            description=f"Check HTTP status code for URL: {url}",
            pre_conditions="1. Network connectivity\n2. URL is accessible",
            test_steps=f"1. Send GET request to {url}\n2. Wait for response\n3. Check status code",
            expected_result=f"HTTP status code should be 200 OK",
            actual_result=f"Status: {status_code} {status_text}, Response Time: {response_time}ms, Category: {status_category}",
            status=test_status,
            severity=severity,
            comments=f"Final URL: {final_url}" if final_url else "",
            resolutions="Check URL correctness, server configuration, or network connectivity" if test_status == "Fail" else ""
        )
    
    def create_error_test_case(self, **kwargs):
        """Create test case for errors"""
        url = kwargs.get('url', '')
        error_msg = kwargs.get('error_msg', '')
        test_type = kwargs.get('test_type', 'Unknown')
        
        return self.create_test_case(
            test_type=test_type,
            module="Error Testing",
            test_data=url,
            description=f"Check for error on URL: {url}",
            pre_conditions="1. Network connectivity\n2. URL is accessible",
            test_steps=f"1. Send request to {url}\n2. Wait for response\n3. Check for errors",
            expected_result="Request should complete successfully",
            actual_result=f"Request failed with error: {error_msg}",
            status="Fail",
            severity="Critical",
            comments="Connection error or timeout",
            resolutions="1. Check network connectivity\n2. Verify URL is correct\n3. Check if server is reachable"
        )
    
    def get_all_test_cases(self):
        """Get all test cases"""
        return self.test_cases
    
    def get_test_cases_by_type(self, test_type):
        """Get test cases filtered by type"""
        return [tc for tc in self.test_cases if tc.get('Test Type') == test_type]
    
    def clear_test_cases(self):
        """Clear all test cases"""
        self.test_cases = []
        self.test_case_counter = 1
    
    def get_statistics(self):
        """Get test case statistics"""
        if not self.test_cases:
            return {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'pass_rate': 0
            }
        
        total = len(self.test_cases)
        passed = sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass')
        
        return {
            'total': total,
            'passed': passed,
            'failed': total - passed,
            'pass_rate': (passed / total * 100) if total > 0 else 0
        }