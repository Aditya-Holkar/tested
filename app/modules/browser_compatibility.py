# modules/browser_compatibility.py - Browser compatibility testing
import requests
from bs4 import BeautifulSoup
import re

class BrowserCompatibility:
    """Check browser compatibility issues"""
    
    def __init__(self, test_case_manager=None):
        self.test_case_manager = test_case_manager
    
    def check_compatibility(self, url):
        """Check browser compatibility"""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. HTML5 Compatibility Check
            html5_test_cases = self._check_html5_compatibility(soup, url)
            test_cases.extend(html5_test_cases)
            
            # 2. CSS Compatibility Check
            css_test_cases = self._check_css_compatibility(soup, url)
            test_cases.extend(css_test_cases)
            
            # 3. JavaScript Compatibility Check
            js_test_cases = self._check_javascript_compatibility(soup, url)
            test_cases.extend(js_test_cases)
            
            # 4. Vendor Prefix Check
            vendor_test_cases = self._check_vendor_prefixes(soup, url)
            test_cases.extend(vendor_test_cases)
            
            # 5. Cross-Browser Features Check
            feature_test_cases = self._check_browser_features(soup, url)
            test_cases.extend(feature_test_cases)
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="Browser Compatibility",
                description="Check browser compatibility",
                test_steps="1. Load webpage\n2. Analyze compatibility issues\n3. Check cross-browser support",
                expected_result="Compatibility check completed successfully",
                actual_result=f"Error during compatibility check: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def _check_html5_compatibility(self, soup, url):
        """Check HTML5 elements and features"""
        test_cases = []
        
        # Check for HTML5 doctype
        doctype = None
        for item in soup.contents:
            if isinstance(item, str) and '<!DOCTYPE' in item:
                doctype = item
                break
        
        if doctype and 'html' in doctype.lower():
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="HTML5 Doctype",
                description="Check for HTML5 doctype",
                test_steps="1. Check document type declaration\n2. Verify HTML5 doctype",
                expected_result="Page should use HTML5 doctype",
                actual_result="HTML5 doctype found",
                status="Pass",
                severity="Medium"
            ))
        else:
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="HTML5 Doctype",
                description="Check for HTML5 doctype",
                test_steps="1. Check document type declaration\n2. Verify HTML5 doctype",
                expected_result="Page should use HTML5 doctype",
                actual_result="No HTML5 doctype found",
                status="Fail",
                severity="Medium",
                resolutions="Add HTML5 doctype: <!DOCTYPE html>"
            ))
        
        # Check for HTML5 semantic elements
        html5_elements = ['header', 'nav', 'main', 'article', 'section', 
                         'aside', 'footer', 'figure', 'figcaption', 'time',
                         'mark', 'summary', 'details']
        
        found_elements = []
        for element in html5_elements:
            if soup.find(element):
                found_elements.append(element)
        
        if found_elements:
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="HTML5 Semantic Elements",
                description="Check for HTML5 semantic elements",
                test_steps="1. Search for HTML5 semantic elements\n2. Count found elements\n3. Check usage",
                expected_result="Page should use HTML5 semantic elements",
                actual_result=f"Found {len(found_elements)} HTML5 semantic elements: {', '.join(found_elements[:5])}",
                status="Pass",
                severity="Low"
            ))
        
        # Check for deprecated elements
        deprecated_elements = ['center', 'font', 'strike', 'u', 'big', 'tt',
                              'frameset', 'frame', 'noframes', 'acronym', 'applet',
                              'basefont', 'dir', 'isindex']
        
        found_deprecated = []
        for element in deprecated_elements:
            if soup.find(element):
                found_deprecated.append(element)
        
        if found_deprecated:
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="Deprecated HTML Elements",
                description="Check for deprecated HTML elements",
                test_steps="1. Search for deprecated elements\n2. Identify issues\n3. Check compatibility",
                expected_result="Avoid deprecated HTML elements",
                actual_result=f"Found deprecated elements: {', '.join(found_deprecated)}",
                status="Fail",
                severity="Medium",
                resolutions="Replace deprecated HTML elements with modern equivalents"
            ))
        
        return test_cases
    
    def _check_css_compatibility(self, soup, url):
        """Check CSS compatibility issues"""
        test_cases = []
        
        # Extract CSS from style tags
        css_content = ''
        for style in soup.find_all('style'):
            if style.string:
                css_content += style.string
        
        # Check for CSS Grid and Flexbox (modern features)
        grid_features = ['display: grid', 'grid-template', 'grid-area', 'grid-gap']
        flexbox_features = ['display: flex', 'flex-direction', 'justify-content', 'align-items']
        
        has_grid = any(feature in css_content for feature in grid_features)
        has_flexbox = any(feature in css_content for feature in flexbox_features)
        
        if has_grid:
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="CSS Grid",
                description="Check for CSS Grid usage",
                test_steps="1. Search for CSS Grid properties\n2. Check browser support",
                expected_result="CSS Grid should have fallbacks for older browsers",
                actual_result="CSS Grid detected",
                status="Info",
                severity="Low",
                comments="CSS Grid has good modern browser support but limited IE support"
            ))
        
        if has_flexbox:
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="CSS Flexbox",
                description="Check for CSS Flexbox usage",
                test_steps="1. Search for Flexbox properties\n2. Check browser support",
                expected_result="Flexbox should have vendor prefixes if needed",
                actual_result="CSS Flexbox detected",
                status="Info",
                severity="Low"
            ))
        
        # Check for CSS Custom Properties (CSS Variables)
        if 'var(--' in css_content or '--' in css_content:
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="CSS Custom Properties",
                description="Check for CSS Variables usage",
                test_steps="1. Search for CSS custom properties\n2. Check browser support",
                expected_result="CSS Variables need fallbacks for older browsers",
                actual_result="CSS Custom Properties (Variables) detected",
                status="Info",
                severity="Low",
                comments="CSS Variables have limited support in older browsers"
            ))
        
        return test_cases
    
    def _check_javascript_compatibility(self, soup, url):
        """Check JavaScript compatibility"""
        test_cases = []
        
        # Check for modern JavaScript features in inline scripts
        modern_js_features = ['let ', 'const ', '=>', 'class ', 'async ', 'await ']
        
        for script in soup.find_all('script'):
            script_content = script.string or ''
            
            found_features = []
            for feature in modern_js_features:
                if feature in script_content:
                    found_features.append(feature.strip())
            
            if found_features:
                test_cases.append(self._create_compatibility_test_case(
                    url=url,
                    module="Modern JavaScript",
                    description="Check for modern JavaScript features",
                    test_steps="1. Analyze inline JavaScript\n2. Check for ES6+ features\n3. Evaluate compatibility",
                    expected_result="Modern JavaScript should be transpiled for older browsers",
                    actual_result=f"Found modern JS features: {', '.join(found_features)}",
                    status="Info",
                    severity="Low",
                    comments="Consider transpiling ES6+ code for better browser compatibility"
                ))
                break
        
        # Check for browser-specific code
        browser_specific = ['navigator.userAgent', 'MSIE', 'Trident', 'Edge',
                           'Chrome', 'Firefox', 'Safari', 'Opera']
        
        for script in soup.find_all('script'):
            script_content = script.string or ''
            
            found_browser_code = []
            for code in browser_specific:
                if code in script_content:
                    found_browser_code.append(code)
            
            if found_browser_code:
                test_cases.append(self._create_compatibility_test_case(
                    url=url,
                    module="Browser Detection",
                    description="Check for browser-specific code",
                    test_steps="1. Search for browser detection code\n2. Analyze user agent checks\n3. Evaluate approach",
                    expected_result="Avoid browser detection, use feature detection instead",
                    actual_result=f"Found browser-specific code: {', '.join(found_browser_code[:3])}",
                    status="Warning",
                    severity="Low",
                    resolutions="Replace browser detection with feature detection using Modernizr or similar"
                ))
                break
        
        return test_cases
    
    def _check_vendor_prefixes(self, soup, url):
        """Check for CSS vendor prefixes"""
        test_cases = []
        
        css_content = ''
        for style in soup.find_all('style'):
            if style.string:
                css_content += style.string
        
        vendor_prefixes = {
            '-webkit-': 'WebKit (Chrome, Safari, newer Opera)',
            '-moz-': 'Mozilla Firefox',
            '-ms-': 'Microsoft Internet Explorer/Edge',
            '-o-': 'Old Opera'
        }
        
        found_prefixes = []
        for prefix in vendor_prefixes:
            if prefix in css_content:
                found_prefixes.append(prefix)
        
        if found_prefixes:
            prefix_info = [vendor_prefixes[prefix] for prefix in found_prefixes]
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="CSS Vendor Prefixes",
                description="Check for CSS vendor prefixes",
                test_steps="1. Search for vendor prefixes\n2. Identify which browsers targeted\n3. Check necessity",
                expected_result="Vendor prefixes should be used when necessary",
                actual_result=f"Found prefixes for: {', '.join(prefix_info)}",
                status="Info",
                severity="Low",
                comments="Consider using Autoprefixer to manage vendor prefixes automatically"
            ))
        
        return test_cases
    
    def _check_browser_features(self, soup, url):
        """Check for potentially problematic browser features"""
        test_cases = []
        
        # Check for Flash content (deprecated)
        flash_indicators = ['embed', 'object']
        flash_elements = []
        
        for element in soup.find_all(flash_indicators):
            if element.get('type') == 'application/x-shockwave-flash':
                flash_elements.append(element.name)
        
        if flash_elements:
            test_cases.append(self._create_compatibility_test_case(
                url=url,
                module="Flash Content",
                description="Check for Adobe Flash content",
                test_steps="1. Search for Flash embeds\n2. Check for Flash content\n3. Evaluate compatibility",
                expected_result="Avoid Flash content (deprecated)",
                actual_result=f"Found Flash content in {len(flash_elements)} elements",
                status="Fail",
                severity="High",
                resolutions="Replace Flash content with HTML5 alternatives (canvas, video, SVG)"
            ))
        
        # Check for outdated technologies
        outdated_tech = {
            'Silverlight': 'application/x-silverlight',
            'Java Applet': 'application/x-java-applet',
            'ActiveX': 'clsid:'
        }
        
        for tech, indicator in outdated_tech.items():
            if indicator in str(soup):
                test_cases.append(self._create_compatibility_test_case(
                    url=url,
                    module=f"{tech} Content",
                    description=f"Check for {tech} content",
                    test_steps=f"1. Search for {tech} indicators\n2. Check for outdated technology\n3. Evaluate compatibility",
                    expected_result=f"Avoid {tech} content (obsolete)",
                    actual_result=f"Found {tech} content",
                    status="Fail",
                    severity="High",
                    resolutions=f"Replace {tech} content with modern web technologies"
                ))
        
        return test_cases
    
    def _create_compatibility_test_case(self, **kwargs):
        """Helper method to create compatibility test cases"""
        if self.test_case_manager:
            return self.test_case_manager.create_test_case(
                test_type="Browser Compatibility",
                module=kwargs.get('module', 'Browser Compatibility'),
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