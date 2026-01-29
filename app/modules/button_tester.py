# modules/button_tester.py - Button testing functions
import requests
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class ButtonTester:
    """Test button functionality on web pages including click events"""
    
    def __init__(self, test_case_manager=None):
        self.test_case_manager = test_case_manager
        self.click_test_results = []
    
    def test_buttons_on_page(self, url):
        """Test buttons on a specific page including click event execution"""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all button elements
            buttons = soup.find_all(['button', 'input', 'a'], 
                                attrs={'type': ['button', 'submit', 'reset']})
            
            if not buttons:
                # Also check for anchor tags that look like buttons
                buttons = soup.find_all('a', class_=lambda x: x and any(
                    cls in str(x).lower() for cls in ['btn', 'button', 'cta']
                ))
            
            if not buttons:
                test_cases.append(self._create_button_test_case(
                    url=url,
                    module="Button Detection",
                    description="Check for buttons on page",
                    test_steps="1. Load webpage\n2. Search for button elements\n3. Count found buttons",
                    expected_result="Page should have interactive elements",
                    actual_result="No buttons found on page",
                    status="Info",
                    severity="Low",
                    comments="No button elements detected"
                ))
                return test_cases
            
            # Test each button
            for idx, button in enumerate(buttons[:10]):  # Limit to 10 buttons
                button_test_cases = self._analyze_button(button, url, idx)
                test_cases.extend(button_test_cases)
                
                # Test click event execution for buttons with handlers
                click_test_case = self._test_click_event(button, url, idx)
                if click_test_case:
                    test_cases.append(click_test_case)
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_button_test_case(
                url=url,
                module="Button Testing",
                description="Test button functionality",
                test_steps="1. Load webpage\n2. Find buttons\n3. Analyze functionality",
                expected_result="Button testing completed successfully",
                actual_result=f"Error testing buttons: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def _analyze_button(self, button, url, index):
        """Analyze individual button"""
        test_cases = []
        
        # Extract button information
        button_type = button.name
        button_text = self._get_button_text(button)
        button_id = button.get('id', f'button_{index}')
        button_class = button.get('class', [])
        
        # Create basic button info test case
        test_cases.append(self._create_button_test_case(
            url=url,
            module=f"Button Analysis - {button_id}",
            description=f"Analyze button: {button_text[:50]}",
            test_steps="1. Identify button element\n2. Extract attributes\n3. Analyze properties",
            expected_result="Button should have proper attributes",
            actual_result=f"Type: {button_type}, Text: '{button_text[:30]}', ID: {button_id}, Classes: {button_class[:3]}",
            status="Info",
            severity="Low"
        ))
        
        # Check for accessibility attributes
        aria_label = button.get('aria-label')
        if not aria_label and button_text:
            # Button has text but no aria-label (might be okay if text is descriptive)
            pass
        elif not aria_label and not button_text:
            test_cases.append(self._create_button_test_case(
                url=url,
                module=f"Button Accessibility - {button_id}",
                description="Check button accessibility",
                test_steps="1. Check for aria-label\n2. Check for visible text\n3. Evaluate accessibility",
                expected_result="Buttons should be accessible",
                actual_result="Button has no visible text and no aria-label",
                status="Fail",
                severity="Medium",
                resolutions="Add aria-label or visible text to the button"
            ))
        
        # Check for disabled state
        if button.get('disabled'):
            test_cases.append(self._create_button_test_case(
                url=url,
                module=f"Button State - {button_id}",
                description="Check button state",
                test_steps="1. Check disabled attribute\n2. Verify state indication",
                expected_result="Disabled buttons should be clearly indicated",
                actual_result="Button is disabled",
                status="Info",
                severity="Low"
            ))
        
        # Check for form association
        if button_type == 'input' and button.get('type') in ['submit', 'reset']:
            form = button.find_parent('form')
            if form:
                test_cases.append(self._create_button_test_case(
                    url=url,
                    module=f"Button Function - {button_id}",
                    description="Check form button functionality",
                    test_steps="1. Check form association\n2. Verify button type",
                    expected_result="Form buttons should be properly associated",
                    actual_result="Button is associated with a form",
                    status="Info",
                    severity="Low"
                ))
        
        # Check for JavaScript handlers
        onclick = button.get('onclick')
        if onclick:
            test_cases.append(self._create_button_test_case(
                url=url,
                module=f"Button Behavior - {button_id}",
                description="Check button JavaScript behavior",
                test_steps="1. Check onclick attribute\n2. Analyze JavaScript code",
                expected_result="Button should have appropriate behavior",
                actual_result=f"Button has onclick handler: {onclick[:100]}",
                status="Info",
                severity="Low"
            ))
        
        # Check for event listeners in script tags
        event_listeners = self._find_event_listeners_in_scripts(button, url)
        if event_listeners:
            test_cases.append(self._create_button_test_case(
                url=url,
                module=f"Button Event Listeners - {button_id}",
                description="Check button event listeners",
                test_steps="1. Search for event listeners\n2. Check attached JavaScript",
                expected_result="Button should have proper event handling",
                actual_result=f"Found event listeners: {', '.join(event_listeners)}",
                status="Info",
                severity="Low"
            ))
        
        # Check for proper styling (basic)
        if button_class:
            has_button_class = any('btn' in str(cls).lower() for cls in button_class)
            if not has_button_class:
                test_cases.append(self._create_button_test_case(
                    url=url,
                    module=f"Button Styling - {button_id}",
                    description="Check button styling",
                    test_steps="1. Check CSS classes\n2. Verify button styling",
                    expected_result="Buttons should have appropriate styling",
                    actual_result="Button may lack proper styling classes",
                    status="Warning",
                    severity="Low",
                    resolutions="Add appropriate CSS classes for button styling"
                ))
        
        return test_cases
    
    def _test_click_event(self, button, base_url, index):
        """Test if click event will execute and extract function names"""
        button_id = button.get('id', f'button_{index}')
        button_text = self._get_button_text(button)
        
        # Check for onclick attribute
        onclick = button.get('onclick', '')
        
        # Check for href attribute (for anchor tags)
        href = button.get('href', '') if button.name == 'a' else ''
        
        # Check for form action
        form_action = ''
        if button.name == 'input' and button.get('type') == 'submit':
            form = button.find_parent('form')
            if form:
                form_action = form.get('action', '')
        
        # Extract function names from onclick
        function_names = []
        if onclick:
            # Extract function calls from onclick attribute
            functions = re.findall(r'(\w+)\s*\(', onclick)
            function_names.extend(functions)
        
        # Determine if click will execute
        will_execute = False
        redirected_url = ''
        execution_details = ''
        
        if onclick:
            will_execute = True
            execution_details = f"Will execute onclick: {onclick[:50]}"
        elif href:
            will_execute = True
            redirected_url = urljoin(base_url, href)
            execution_details = f"Will navigate to: {redirected_url}"
        elif form_action:
            will_execute = True
            redirected_url = urljoin(base_url, form_action)
            execution_details = f"Will submit form to: {redirected_url}"
        elif button.get('type') in ['submit', 'reset']:
            will_execute = True
            execution_details = "Form button - will submit/reset form"
        else:
            will_execute = False
            execution_details = "No click handler detected"
        
        # Create test case for click event
        actual_result_parts = [
            f"Click will execute: {will_execute}",
            f"Execution details: {execution_details}"
        ]
        
        if function_names:
            actual_result_parts.append(f"Function names: {', '.join(function_names)}")
        
        if redirected_url:
            actual_result_parts.append(f"Redirected URL: {redirected_url}")
        
        # Store click test result for reporting
        self.click_test_results.append({
            'button_id': button_id,
            'button_text': button_text,
            'will_execute': will_execute,
            'function_names': function_names,
            'redirected_url': redirected_url,
            'execution_details': execution_details
        })
        
        return self._create_button_test_case(
            url=base_url,
            module=f"Click Event Test - {button_id}",
            description=f"Test click event for button: {button_text[:30]}",
            test_steps="1. Inspect button attributes\n2. Check for click handlers\n3. Analyze function calls",
            expected_result="Button should have proper click behavior",
            actual_result=" | ".join(actual_result_parts),
            status="Pass" if will_execute else "Warning",
            severity="Medium",
            comments=f"Button: {button_text[:50]}",
            function_names=", ".join(function_names) if function_names else "None",
            redirected_url=redirected_url or "None"
        )
    
    def _find_event_listeners_in_scripts(self, button, url):
        """Find event listeners attached to button via JavaScript"""
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            scripts = soup.find_all('script')
            
            event_listeners = []
            button_id = button.get('id', '')
            button_classes = button.get('class', [])
            
            for script in scripts:
                if script.string:
                    script_content = script.string
                    
                    # Look for addEventListener or jQuery bindings
                    if button_id:
                        # Check for ID-based selectors
                        patterns = [
                            f"addEventListener\\s*\\([^)]*['\"]{re.escape(button_id)}['\"][^)]*\\)",
                            f"\\.addEventListener\\s*\\([^)]*['\"]click['\"][^)]*\\)",
                            f"\\$\\s*\\(['\"]#{re.escape(button_id)}['\"]\\)\\.(click|bind|on)\\(",
                            f"document\\.getElementById\\s*\\(['\"]{re.escape(button_id)}['\"]\\)"
                        ]
                        
                        for pattern in patterns:
                            if re.search(pattern, script_content, re.IGNORECASE | re.DOTALL):
                                event_listeners.append("click event listener (by ID)")
                    
                    # Check for class-based selectors
                    for cls in button_classes:
                        patterns = [
                            f"\\.{re.escape(cls)}\\.(click|bind|on)\\(",
                            f"\\$\\s*\\(['\"]\\.{re.escape(cls)}['\"]\\)\\.(click|bind|on)\\(",
                            f"querySelectorAll\\s*\\(['\"]\\.{re.escape(cls)}['\"]\\)"
                        ]
                        
                        for pattern in patterns:
                            if re.search(pattern, script_content, re.IGNORECASE | re.DOTALL):
                                event_listeners.append(f"event listener (by class .{cls})")
            
            return list(set(event_listeners))
        except:
            return []
    
    def _get_button_text(self, button):
        """Extract text from button element"""
        if button.name == 'input':
            return button.get('value', '') or button.get('aria-label', '') or ''
        elif button.name == 'button':
            return button.get_text(strip=True) or button.get('aria-label', '') or ''
        elif button.name == 'a':
            return button.get_text(strip=True) or button.get('aria-label', '') or button.get('title', '') or ''
        return ''
    
    def _create_button_test_case(self, **kwargs):
        """Helper method to create button test cases"""
        if self.test_case_manager:
            return self.test_case_manager.create_test_case(
                test_type="Button Testing",
                module=kwargs.get('module', 'Button Testing'),
                test_data=kwargs.get('url', ''),
                description=kwargs.get('description', ''),
                pre_conditions="Page must load successfully",
                test_steps=kwargs.get('test_steps', ''),
                expected_result=kwargs.get('expected_result', ''),
                actual_result=kwargs.get('actual_result', ''),
                status=kwargs.get('status', 'Not Run'),
                severity=kwargs.get('severity', 'Medium'),
                comments=kwargs.get('comments', ''),
                resolutions=kwargs.get('resolutions', ''),
                function_names=kwargs.get('function_names', ''),  # New field
                redirected_url=kwargs.get('redirected_url', '')  # New field
            )
        return None
    
    def get_click_test_summary(self):
        """Get summary of click test results"""
        total_buttons = len(self.click_test_results)
        executing_buttons = sum(1 for r in self.click_test_results if r['will_execute'])
        non_executing_buttons = total_buttons - executing_buttons
        
        return {
            'total_buttons_tested': total_buttons,
            'buttons_with_click_events': executing_buttons,
            'buttons_without_click_events': non_executing_buttons,
            'buttons_with_functions': sum(1 for r in self.click_test_results if r['function_names']),
            'buttons_with_redirects': sum(1 for r in self.click_test_results if r['redirected_url']),
            'click_test_results': self.click_test_results
        }