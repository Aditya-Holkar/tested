# modules/accessibility_tester.py - Accessibility testing
from bs4 import BeautifulSoup
import re
from modules.constants import VALID_ARIA_ROLES

class AccessibilityTester:
    """Test website accessibility"""
    
    def __init__(self, test_case_manager=None):
        self.test_case_manager = test_case_manager
    
    def analyze_accessibility(self, url):
        """Perform comprehensive accessibility analysis"""
        test_cases = []
        
        try:
            import requests
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Semantic HTML Analysis
            semantic_test_cases = self.analyze_semantic_html(soup, url)
            test_cases.extend(semantic_test_cases)
            
            # 2. ARIA Attributes Analysis
            aria_test_cases = self.analyze_aria_attributes(soup, url)
            test_cases.extend(aria_test_cases)
            
            # 3. Keyboard Navigation
            keyboard_test_cases = self.analyze_keyboard_accessibility(soup, url)
            test_cases.extend(keyboard_test_cases)
            
            # 4. Color Contrast Analysis
            contrast_test_cases = self.analyze_color_contrast(soup, url)
            test_cases.extend(contrast_test_cases)
            
            # 5. Form Accessibility
            form_test_cases = self.analyze_form_accessibility(soup, url)
            test_cases.extend(form_test_cases)
            
            # 6. Media Accessibility
            media_test_cases = self.analyze_media_accessibility(soup, url)
            test_cases.extend(media_test_cases)
            
            # 7. Language and Reading
            language_test_cases = self.analyze_language_accessibility(soup, url)
            test_cases.extend(language_test_cases)
            
            # 8. Overall Accessibility Score
            score_test_case = self.calculate_accessibility_score(test_cases, url)
            test_cases.append(score_test_case)
            
            return test_cases
            
        except Exception as e:
            if self.test_case_manager:
                error_test_case = self.test_case_manager.create_test_case(
                    test_type="Accessibility Testing",
                    module="Accessibility Analysis",
                    test_data=url,
                    description="Perform comprehensive accessibility analysis",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Check accessibility features\n3. Analyze compliance",
                    expected_result="Accessibility analysis completed successfully",
                    actual_result=f"Error during accessibility analysis: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium"
                )
                return [error_test_case]
            return []
    
    def analyze_semantic_html(self, soup, url):
        """Analyze semantic HTML structure for accessibility."""
        test_cases = []
        
        # Test 1: Use of semantic elements
        semantic_elements = {
            'header': soup.find_all(['header']),
            'nav': soup.find_all(['nav']),
            'main': soup.find_all(['main']),
            'article': soup.find_all(['article']),
            'section': soup.find_all(['section']),
            'aside': soup.find_all(['aside']),
            'footer': soup.find_all(['footer'])
        }
        
        total_semantic = sum(len(elements) for elements in semantic_elements.values())
        
        if total_semantic > 0:
            test_cases.append(self._create_accessibility_test_case(
                url=url,
                module="Semantic HTML",
                description="Check for semantic HTML elements",
                test_steps="1. Parse HTML\n2. Count semantic elements\n3. Evaluate semantic structure",
                expected_result="Page should use semantic HTML elements",
                actual_result=f"Found {total_semantic} semantic HTML elements",
                status="Pass",
                severity="Medium"
            ))
        else:
            test_cases.append(self._create_accessibility_test_case(
                url=url,
                module="Semantic HTML",
                description="Check for semantic HTML elements",
                test_steps="1. Parse HTML\n2. Count semantic elements\n3. Evaluate semantic structure",
                expected_result="Page should use semantic HTML elements",
                actual_result="No semantic HTML elements found",
                status="Fail",
                severity="High",
                resolutions="Replace div/span with appropriate semantic elements (header, nav, main, article, section, footer)"
            ))
        
        # Test 2: Heading hierarchy
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = soup.find_all(f'h{i}')
        
        # Check for h1
        if headings['h1']:
            h1_count = len(headings['h1'])
            if h1_count == 1:
                test_cases.append(self._create_accessibility_test_case(
                    url=url,
                    module="Heading H1",
                    description="Check for single H1 heading",
                    test_steps="1. Find all H1 elements\n2. Count occurrences\n3. Check if exactly one",
                    expected_result="Page should have exactly one H1 heading",
                    actual_result=f"Found 1 H1 heading (Good)",
                    status="Pass",
                    severity="High"
                ))
            else:
                test_cases.append(self._create_accessibility_test_case(
                    url=url,
                    module="Heading H1",
                    description="Check for single H1 heading",
                    test_steps="1. Find all H1 elements\n2. Count occurrences\n3. Check if exactly one",
                    expected_result="Page should have exactly one H1 heading",
                    actual_result=f"Found {h1_count} H1 headings (Should be exactly 1)",
                    status="Fail",
                    severity="High",
                    resolutions="Ensure only one H1 per page, representing main content"
                ))
        else:
            test_cases.append(self._create_accessibility_test_case(
                url=url,
                module="Heading H1",
                description="Check for single H1 heading",
                test_steps="1. Find all H1 elements\n2. Count occurrences\n3. Check if exactly one",
                expected_result="Page should have exactly one H1 heading",
                actual_result="No H1 heading found",
                status="Fail",
                severity="Critical",
                resolutions="Add a descriptive H1 heading at the beginning of main content"
            ))
        
        return test_cases
    
    def analyze_aria_attributes(self, soup, url):
        """Analyze ARIA (Accessible Rich Internet Applications) attributes."""
        test_cases = []
        
        # Find elements with ARIA attributes
        aria_elements = soup.find_all(attrs={"aria-": True})
        
        if aria_elements:
            test_cases.append(self._create_accessibility_test_case(
                url=url,
                module="ARIA Usage",
                description="Check for ARIA attributes usage",
                test_steps="1. Find elements with ARIA attributes\n2. Count usage\n3. Evaluate implementation",
                expected_result="ARIA should be used appropriately to enhance accessibility",
                actual_result=f"Found {len(aria_elements)} elements with ARIA attributes",
                status="Pass",
                severity="Low"
            ))
            
            # Check for invalid ARIA roles
            invalid_roles = []
            for elem in aria_elements:
                role = elem.get('role', '')
                if role and role not in VALID_ARIA_ROLES:
                    invalid_roles.append(role)
            
            if invalid_roles:
                test_cases.append(self._create_accessibility_test_case(
                    url=url,
                    module="ARIA Role Validation",
                    description="Check for invalid ARIA roles",
                    test_steps="1. Find all role attributes\n2. Validate against ARIA specification\n3. Identify invalid roles",
                    expected_result="ARIA roles should be valid according to specification",
                    actual_result=f"Invalid roles found: {', '.join(set(invalid_roles)[:5])}",
                    status="Fail",
                    severity="Medium",
                    resolutions="Use only valid ARIA roles from WAI-ARIA specification"
                ))
        
        return test_cases
    
    def analyze_keyboard_accessibility(self, soup, url):
        """Analyze keyboard navigation accessibility."""
        test_cases = []
        
        # Find interactive elements
        interactive_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        
        # Test 1: Focusable elements
        focusable_elements = []
        for elem in interactive_elements:
            if elem.name == 'a' and elem.get('href'):
                focusable_elements.append(elem)
            elif elem.name == 'button':
                focusable_elements.append(elem)
            elif elem.name == 'input' and elem.get('type') not in ['hidden']:
                focusable_elements.append(elem)
            elif elem.name in ['select', 'textarea']:
                focusable_elements.append(elem)
        
        if focusable_elements:
            test_cases.append(self._create_accessibility_test_case(
                url=url,
                module="Keyboard Focus",
                description="Check for keyboard focusable elements",
                test_steps="1. Find interactive elements\n2. Check if focusable\n3. Count focusable elements",
                expected_result="All interactive elements should be keyboard focusable",
                actual_result=f"Found {len(focusable_elements)} focusable elements",
                status="Pass",
                severity="High"
            ))
        
        return test_cases
    
    def analyze_color_contrast(self, soup, url):
        """Analyze color contrast for accessibility."""
        test_cases = []
        
        # Check for color-dependent information
        color_dependent_text = []
        for elem in soup.find_all(['span', 'div', 'p', 'a']):
            style = elem.get('style', '').lower()
            text = elem.get_text(strip=True)
            
            if text and any(color_indicator in style for color_indicator in ['color:', 'background:', 'rgb', 'hsl', '#']):
                if any(pattern in text.lower() for pattern in ['red', 'green', 'blue', 'color', 'colored']):
                    color_dependent_text.append(text[:50])
        
        if color_dependent_text:
            test_cases.append(self._create_accessibility_test_case(
                url=url,
                module="Color-Dependent Information",
                description="Check for information conveyed only by color",
                test_steps="1. Find text elements\n2. Check for color-only indicators\n3. Identify color-dependent information",
                expected_result="Information should not be conveyed by color alone",
                actual_result=f"Found {len(color_dependent_text)} instances of potentially color-only information",
                status="Warning",
                severity="Medium",
                resolutions="Add text labels or patterns along with color coding"
            ))
        
        return test_cases
    
    def analyze_form_accessibility(self, soup, url):
        """Analyze form accessibility."""
        test_cases = []
        forms = soup.find_all('form')
        
        if not forms:
            test_cases.append(self._create_accessibility_test_case(
                url=url,
                module="Form Accessibility",
                description="Check form accessibility features",
                test_steps="1. Find forms\n2. Check accessibility attributes\n3. Evaluate form structure",
                expected_result="Forms should be accessible to all users",
                actual_result="No forms found on page",
                status="Pass",
                severity="Low"
            ))
            return test_cases
        
        for form_idx, form in enumerate(forms):
            form_id = form.get('id', f'form_{form_idx}')
            inputs = form.find_all(['input', 'select', 'textarea'])
            
            labeled_inputs = 0
            for inp in inputs:
                # Check for label association
                input_id = inp.get('id')
                input_name = inp.get('name')
                aria_label = inp.get('aria-label')
                aria_labelledby = inp.get('aria-labelledby')
                
                has_label = False
                
                if input_id:
                    # Check for label with for attribute
                    label = soup.find('label', attrs={'for': input_id})
                    if label and label.get_text(strip=True):
                        has_label = True
                
                if not has_label and (aria_label or aria_labelledby):
                    has_label = True
                
                if not has_label and input_name:
                    # Check for wrapping label
                    parent = inp.parent
                    if parent.name == 'label':
                        has_label = True
                
                if has_label:
                    labeled_inputs += 1
            
            label_percentage = (labeled_inputs / len(inputs)) * 100 if inputs else 0
            
            if label_percentage < 90:
                test_cases.append(self._create_accessibility_test_case(
                    url=f"{url} - {form_id}",
                    module="Form Labels",
                    description="Check form input labels",
                    test_steps="1. Find form inputs\n2. Check for associated labels\n3. Calculate labeled percentage",
                    expected_result="All form inputs should have associated labels",
                    actual_result=f"Only {label_percentage:.1f}% of inputs have labels",
                    status="Fail",
                    severity="High",
                    resolutions="Add labels for all form inputs using <label> elements or aria-label/aria-labelledby"
                ))
        
        return test_cases
    
    def analyze_media_accessibility(self, soup, url):
        """Analyze media (images, videos, audio) accessibility."""
        test_cases = []
        
        # Test 1: Image alt text
        images = soup.find_all('img')
        informative_images = []
        images_missing_alt = []
        
        for img in images:
            alt = img.get('alt', '')
            
            if alt is None:
                images_missing_alt.append(img)
            elif alt.strip() == '':
                # Check if it's decorative
                role = img.get('role', '')
                aria_hidden = img.get('aria-hidden', '')
                
                if not (role == 'presentation' or aria_hidden == 'true'):
                    images_missing_alt.append(img)
            else:
                informative_images.append(img)
        
        total_images = len(images)
        
        if total_images > 0:
            informative_with_alt = len(informative_images)
            informative_percentage = (informative_with_alt / total_images) * 100
            
            if informative_percentage < 90:
                test_cases.append(self._create_accessibility_test_case(
                    url=url,
                    module="Image Alt Text",
                    description="Check image alternative text",
                    test_steps="1. Find all images\n2. Check alt attributes\n3. Categorize images",
                    expected_result="Informative images should have descriptive alt text",
                    actual_result=f"Only {informative_percentage:.1f}% of images have proper alt text",
                    status="Fail",
                    severity="High",
                    resolutions="Add descriptive alt text to informative images, add empty alt to decorative images"
                ))
        
        return test_cases
    
    def analyze_language_accessibility(self, soup, url):
        """Analyze language and reading accessibility."""
        test_cases = []
        
        # Test 1: Page language declaration
        html_tag = soup.find('html')
        lang = html_tag.get('lang') if html_tag else None
        
        if lang:
            test_cases.append(self._create_accessibility_test_case(
                url=url,
                module="Page Language",
                description="Check page language declaration",
                test_steps="1. Find html tag\n2. Check lang attribute\n3. Verify language code",
                expected_result="Page should declare primary language",
                actual_result=f"Language declared: {lang}",
                status="Pass",
                severity="High"
            ))
        else:
            test_cases.append(self._create_accessibility_test_case(
                url=url,
                module="Page Language",
                description="Check page language declaration",
                test_steps="1. Find html tag\n2. Check lang attribute\n3. Verify language code",
                expected_result="Page should declare primary language",
                actual_result="No language declared",
                status="Fail",
                severity="High",
                resolutions="Add lang attribute to html tag (e.g., lang='en')"
            ))
        
        return test_cases
    
    def calculate_accessibility_score(self, accessibility_test_cases, url):
        """Calculate overall accessibility score based on test results."""
        if not accessibility_test_cases:
            return self._create_accessibility_test_case(
                url=url,
                module="Accessibility Score",
                description="Calculate overall accessibility score",
                test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
                expected_result="High accessibility score indicates good compliance",
                actual_result="No accessibility tests were performed",
                status="Fail",
                severity="Medium"
            )
        
        # Weight factors based on severity
        severity_weights = {'Critical': 10, 'High': 5, 'Medium': 3, 'Low': 1, 'Info': 0, 'Warning': 2}
        
        total_weight = 0
        passed_weight = 0
        
        for test_case in accessibility_test_cases:
            severity = test_case.get('Severity', 'Medium')
            status = test_case.get('Status', 'Fail')
            
            weight = severity_weights.get(severity, 1)
            total_weight += weight
            
            if status.lower() in ['pass', 'passed', 'warning', 'info']:
                passed_weight += weight
        
        if total_weight > 0:
            accessibility_score = (passed_weight / total_weight) * 100
        else:
            accessibility_score = 0
        
        # Determine grade
        if accessibility_score >= 90:
            grade = "A (Excellent)"
            status_result = "Pass"
        elif accessibility_score >= 80:
            grade = "B (Good)"
            status_result = "Pass"
        elif accessibility_score >= 70:
            grade = "C (Average)"
            status_result = "Warning"
        elif accessibility_score >= 60:
            grade = "D (Needs Improvement)"
            status_result = "Fail"
        else:
            grade = "F (Poor)"
            status_result = "Fail"
        
        # Count test results
        passed_tests = sum(1 for tc in accessibility_test_cases if tc.get('Status', '').lower() in ['pass', 'passed'])
        failed_tests = sum(1 for tc in accessibility_test_cases if tc.get('Status', '').lower() == 'fail')
        warning_tests = sum(1 for tc in accessibility_test_cases if tc.get('Status', '').lower() == 'warning')
        
        return self._create_accessibility_test_case(
            url=url,
            module="Accessibility Score",
            description="Calculate overall accessibility score",
            test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
            expected_result="High accessibility score indicates good compliance",
            actual_result=f"Accessibility Score: {accessibility_score:.1f}% - {grade}. Passed: {passed_tests}, Failed: {failed_tests}, Warnings: {warning_tests}",
            status=status_result,
            severity="High" if accessibility_score < 70 else "Medium",
            resolutions="Address failed tests to improve accessibility score" if accessibility_score < 80 else "Maintain current accessibility features and monitor regularly"
        )
    
    def _create_accessibility_test_case(self, **kwargs):
        """Helper method to create accessibility test cases"""
        if self.test_case_manager:
            return self.test_case_manager.create_test_case(
                test_type="Accessibility Testing",
                module=kwargs.get('module', 'Accessibility'),
                test_data=kwargs.get('url', ''),
                description=kwargs.get('description', ''),
                pre_conditions="Page must load successfully",
                test_steps=kwargs.get('test_steps', ''),
                expected_result=kwargs.get('expected_result', ''),
                actual_result=kwargs.get('actual_result', ''),
                status=kwargs.get('status', 'Not Run'),
                severity=kwargs.get('severity', 'Medium'),
                comments=kwargs.get('comments', ''),
                resolutions=kwargs.get('resolutions', '')
            )
        return None