# modules/responsiveness_checker.py - Responsiveness checking
import requests
from bs4 import BeautifulSoup
import re

class ResponsivenessChecker:
    """Check website responsiveness"""
    
    def __init__(self, test_case_manager=None):
        self.test_case_manager = test_case_manager
    
    def check_responsiveness(self, url):
        """Check responsiveness of a web page"""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Viewport Meta Tag Check
            viewport_test_cases = self._check_viewport(soup, url)
            test_cases.extend(viewport_test_cases)
            
            # 2. Responsive Design Elements Check
            responsive_test_cases = self._check_responsive_elements(soup, url)
            test_cases.extend(responsive_test_cases)
            
            # 3. Mobile-First Design Check
            mobile_test_cases = self._check_mobile_design(soup, url)
            test_cases.extend(mobile_test_cases)
            
            # 4. Image Responsiveness Check
            image_test_cases = self._check_responsive_images(soup, url)
            test_cases.extend(image_test_cases)
            
            # 5. Touch Targets Check
            touch_test_cases = self._check_touch_targets(soup, url)
            test_cases.extend(touch_test_cases)
            
            # 6. Responsive Typography Check
            typography_test_cases = self._check_responsive_typography(soup, url)
            test_cases.extend(typography_test_cases)
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_responsive_test_case(
                url=url,
                module="Responsiveness Check",
                description="Check website responsiveness",
                test_steps="1. Load webpage\n2. Analyze responsive design\n3. Check mobile compatibility",
                expected_result="Responsiveness check completed successfully",
                actual_result=f"Error during responsiveness check: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def _check_viewport(self, soup, url):
        """Check viewport meta tag"""
        test_cases = []
        
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        
        if viewport:
            viewport_content = viewport.get('content', '')
            
            # Check for essential viewport properties
            has_width = 'width=' in viewport_content
            has_initial_scale = 'initial-scale=' in viewport_content
            
            if has_width and has_initial_scale:
                test_cases.append(self._create_responsive_test_case(
                    url=url,
                    module="Viewport Meta Tag",
                    description="Check viewport meta tag configuration",
                    test_steps="1. Find viewport meta tag\n2. Check content\n3. Verify essential properties",
                    expected_result="Viewport should have width and initial-scale",
                    actual_result=f"Proper viewport tag: {viewport_content}",
                    status="Pass",
                    severity="High"
                ))
            else:
                missing = []
                if not has_width:
                    missing.append("width")
                if not has_initial_scale:
                    missing.append("initial-scale")
                
                test_cases.append(self._create_responsive_test_case(
                    url=url,
                    module="Viewport Meta Tag",
                    description="Check viewport meta tag configuration",
                    test_steps="1. Find viewport meta tag\n2. Check content\n3. Verify essential properties",
                    expected_result="Viewport should have width and initial-scale",
                    actual_result=f"Viewport missing: {', '.join(missing)}",
                    status="Fail",
                    severity="High",
                    resolutions="Add missing viewport properties: width=device-width, initial-scale=1.0"
                ))
        else:
            test_cases.append(self._create_responsive_test_case(
                url=url,
                module="Viewport Meta Tag",
                description="Check for viewport meta tag",
                test_steps="1. Look for viewport meta tag\n2. Check if present",
                expected_result="Page must have viewport meta tag",
                actual_result="No viewport meta tag found",
                status="Fail",
                severity="Critical",
                resolutions="Add viewport meta tag: <meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            ))
        
        return test_cases
    
    def _check_responsive_elements(self, soup, url):
        """Check for responsive design elements"""
        test_cases = []
        
        # Check for responsive CSS framework classes
        responsive_classes = ['container', 'row', 'col-', 'grid-', 'flex', 'responsive']
        
        elements_with_responsive_classes = []
        for element in soup.find_all(class_=True):
            classes = element.get('class', [])
            if any(resp_class in str(classes) for resp_class in responsive_classes):
                elements_with_responsive_classes.append(element.name)
        
        if elements_with_responsive_classes:
            test_cases.append(self._create_responsive_test_case(
                url=url,
                module="Responsive Design Elements",
                description="Check for responsive design patterns",
                test_steps="1. Look for responsive CSS classes\n2. Check for grid/flex systems\n3. Analyze layout structure",
                expected_result="Page should use responsive design patterns",
                actual_result=f"Found responsive elements: {len(set(elements_with_responsive_classes))} types",
                status="Pass",
                severity="Medium"
            ))
        
        # Check for media queries in inline styles
        style_content = ''
        for style in soup.find_all('style'):
            if style.string:
                style_content += style.string
        
        media_query_count = style_content.count('@media')
        if media_query_count > 0:
            test_cases.append(self._create_responsive_test_case(
                url=url,
                module="CSS Media Queries",
                description="Check for responsive media queries",
                test_steps="1. Search for @media rules\n2. Count media queries\n3. Check breakpoints",
                expected_result="Page should use media queries for responsiveness",
                actual_result=f"Found {media_query_count} media queries",
                status="Pass",
                severity="Medium"
            ))
        else:
            # Check if there are external stylesheets that might contain media queries
            external_css = len(soup.find_all('link', rel='stylesheet'))
            if external_css > 0:
                test_cases.append(self._create_responsive_test_case(
                    url=url,
                    module="CSS Media Queries",
                    description="Check for responsive media queries",
                    test_steps="1. Search for @media rules\n2. Check inline styles\n3. Note external CSS",
                    expected_result="Page should use media queries for responsiveness",
                    actual_result="No inline media queries found (check external CSS)",
                    status="Info",
                    severity="Medium"
                ))
        
        return test_cases
    
    def _check_mobile_design(self, soup, url):
        """Check mobile-specific design elements"""
        test_cases = []
        
        # Check for hamburger menu (common mobile pattern)
        hamburger_indicators = ['navbar-toggler', 'menu-toggle', 'hamburger', 'nav-toggle']
        found_hamburger = False
        
        for element in soup.find_all(class_=True):
            classes = ' '.join(element.get('class', [])).lower()
            if any(indicator in classes for indicator in hamburger_indicators):
                found_hamburger = True
                break
        
        if found_hamburger:
            test_cases.append(self._create_responsive_test_case(
                url=url,
                module="Mobile Navigation",
                description="Check for mobile navigation patterns",
                test_steps="1. Look for mobile navigation elements\n2. Check for hamburger menu\n3. Analyze navigation structure",
                expected_result="Mobile sites should have appropriate navigation",
                actual_result="Found mobile navigation pattern (hamburger menu)",
                status="Pass",
                severity="Low"
            ))
        
        # Check for touch-friendly buttons
        buttons = soup.find_all(['button', 'a', 'input'])
        potentially_small_targets = []
        
        for button in buttons:
            # Check for small-looking buttons (this is heuristic)
            classes = ' '.join(button.get('class', [])).lower()
            text = button.get_text(strip=True)
            
            # Look for indicators of small buttons
            if ('btn-sm' in classes or 'small' in classes) and len(text) < 20:
                potentially_small_targets.append(button.name)
        
        if potentially_small_targets:
            test_cases.append(self._create_responsive_test_case(
                url=url,
                module="Touch Targets",
                description="Check for mobile-friendly touch targets",
                test_steps="1. Identify interactive elements\n2. Check size indicators\n3. Evaluate touch-friendliness",
                expected_result="Touch targets should be at least 44x44 pixels",
                actual_result=f"Found {len(potentially_small_targets)} potentially small touch targets",
                status="Warning",
                severity="Low",
                resolutions="Ensure all interactive elements are at least 44x44 pixels on mobile"
            ))
        
        return test_cases
    
    def _check_responsive_images(self, soup, url):
        """Check image responsiveness"""
        test_cases = []
        images = soup.find_all('img')
        
        if not images:
            return test_cases
        
        responsive_images = 0
        non_responsive_images = 0
        
        for img in images:
            # Check for responsive image attributes
            srcset = img.get('srcset')
            sizes = img.get('sizes')
            has_max_width = 'max-width: 100%' in str(img)
            
            if srcset or sizes or has_max_width:
                responsive_images += 1
            else:
                # Check if image might be in a responsive container
                parent = img.parent
                parent_classes = ' '.join(parent.get('class', [])) if parent else ''
                if any(resp in parent_classes.lower() for resp in ['img-fluid', 'responsive', 'max-width']):
                    responsive_images += 1
                else:
                    non_responsive_images += 1
        
        if responsive_images > 0:
            responsive_percentage = (responsive_images / len(images)) * 100
            
            if responsive_percentage >= 80:
                test_cases.append(self._create_responsive_test_case(
                    url=url,
                    module="Responsive Images",
                    description="Check image responsiveness",
                    test_steps="1. Find all images\n2. Check responsive attributes\n3. Calculate responsive percentage",
                    expected_result="Images should be responsive",
                    actual_result=f"{responsive_percentage:.1f}% of images are responsive",
                    status="Pass",
                    severity="Medium"
                ))
            else:
                test_cases.append(self._create_responsive_test_case(
                    url=url,
                    module="Responsive Images",
                    description="Check image responsiveness",
                    test_steps="1. Find all images\n2. Check responsive attributes\n3. Calculate responsive percentage",
                    expected_result="Images should be responsive",
                    actual_result=f"Only {responsive_percentage:.1f}% of images are responsive",
                    status="Warning",
                    severity="Medium",
                    resolutions="Make images responsive with max-width: 100%, height: auto, or srcset/sizes attributes"
                ))
        
        return test_cases
    
    def _check_touch_targets(self, soup, url):
        """Check touch target sizing"""
        test_cases = []
        
        # This is a simplified check
        interactive_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        
        if interactive_elements:
            test_cases.append(self._create_responsive_test_case(
                url=url,
                module="Interactive Elements",
                description="Check interactive elements for mobile",
                test_steps="1. Count interactive elements\n2. Check mobile compatibility\n3. Evaluate touch targets",
                expected_result="Interactive elements should be mobile-friendly",
                actual_result=f"Found {len(interactive_elements)} interactive elements",
                status="Info",
                severity="Low",
                comments="Ensure touch targets are at least 44x44 pixels on mobile devices"
            ))
        
        return test_cases
    
    def _check_responsive_typography(self, soup, url):
        """Check responsive typography"""
        test_cases = []
        
        # Look for relative font units in styles
        style_content = ''
        for style in soup.find_all('style'):
            if style.string:
                style_content += style.string
        
        relative_units = ['em', 'rem', '%', 'vw', 'vh']
        absolute_units = ['px', 'pt', 'cm', 'mm', 'in']
        
        relative_count = sum(style_content.count(unit) for unit in relative_units)
        absolute_count = sum(style_content.count(unit) for unit in absolute_units)
        
        if relative_count > 0:
            test_cases.append(self._create_responsive_test_case(
                url=url,
                module="Responsive Typography",
                description="Check typography units for responsiveness",
                test_steps="1. Analyze font size units\n2. Check for relative units\n3. Evaluate responsiveness",
                expected_result="Typography should use relative units for responsiveness",
                actual_result=f"Using relative units ({relative_count} instances)",
                status="Pass",
                severity="Low"
            ))
        elif absolute_count > 0:
            test_cases.append(self._create_responsive_test_case(
                url=url,
                module="Responsive Typography",
                description="Check typography units for responsiveness",
                test_steps="1. Analyze font size units\n2. Check for relative units\n3. Evaluate responsiveness",
                expected_result="Typography should use relative units for responsiveness",
                actual_result="Using absolute units (px, pt) which may not scale well",
                status="Warning",
                severity="Low",
                resolutions="Consider using relative units (em, rem, %) for better responsiveness"
            ))
        
        return test_cases
    
    def _create_responsive_test_case(self, **kwargs):
        """Helper method to create responsiveness test cases"""
        if self.test_case_manager:
            return self.test_case_manager.create_test_case(
                test_type="Responsiveness Check",
                module=kwargs.get('module', 'Responsiveness'),
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