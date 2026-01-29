# modules/font_analyzer.py - Font analysis
import requests
from bs4 import BeautifulSoup
import re
import cssutils
from io import StringIO

class FontAnalyzer:
    """Analyze fonts used on web pages"""
    
    def __init__(self, test_case_manager=None):
        self.test_case_manager = test_case_manager
    
    def analyze_fonts(self, url):
        """Analyze fonts on a web page"""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract font information from various sources
            font_info = self._extract_font_information(soup, url)
            
            if not font_info['fonts_found']:
                test_cases.append(self._create_font_test_case(
                    url=url,
                    module="Font Analysis",
                    description="Check fonts used on page",
                    test_steps="1. Extract font declarations\n2. Analyze font usage\n3. Check font stack",
                    expected_result="Page should use appropriate fonts",
                    actual_result="No explicit font declarations found",
                    status="Info",
                    severity="Low"
                ))
                return test_cases
            
            # Analyze font stack
            font_stack_test_cases = self._analyze_font_stack(font_info, url)
            test_cases.extend(font_stack_test_cases)
            
            # Analyze font sizes
            font_size_test_cases = self._analyze_font_sizes(font_info, url)
            test_cases.extend(font_size_test_cases)
            
            # Analyze web font usage
            webfont_test_cases = self._analyze_webfonts(font_info, url)
            test_cases.extend(webfont_test_cases)
            
            # Analyze font loading
            font_loading_test_cases = self._analyze_font_loading(font_info, url)
            test_cases.extend(font_loading_test_cases)
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_font_test_case(
                url=url,
                module="Font Analysis",
                description="Analyze fonts used on page",
                test_steps="1. Extract font declarations\n2. Analyze font usage\n3. Check optimization",
                expected_result="Font analysis completed successfully",
                actual_result=f"Error during font analysis: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def _extract_font_information(self, soup, url):
        """Extract font information from page"""
        font_info = {
            'fonts_found': False,
            'font_families': set(),
            'font_sizes': [],
            'web_fonts': [],
            'inline_styles': [],
            'external_stylesheets': [],
            'font_face_rules': []
        }
        
        # Extract from inline styles
        for element in soup.find_all(style=True):
            style_content = element['style']
            font_families = self._extract_font_families_from_css(style_content)
            font_sizes = self._extract_font_sizes_from_css(style_content)
            
            if font_families or font_sizes:
                font_info['fonts_found'] = True
                font_info['font_families'].update(font_families)
                font_info['font_sizes'].extend(font_sizes)
                font_info['inline_styles'].append({
                    'element': element.name,
                    'styles': style_content
                })
        
        # Extract from style tags
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                font_families = self._extract_font_families_from_css(style_tag.string)
                font_sizes = self._extract_font_sizes_from_css(style_tag.string)
                font_faces = self._extract_font_face_rules(style_tag.string)
                
                if font_families or font_sizes or font_faces:
                    font_info['fonts_found'] = True
                    font_info['font_families'].update(font_families)
                    font_info['font_sizes'].extend(font_sizes)
                    font_info['font_face_rules'].extend(font_faces)
        
        # Extract from external stylesheets
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href:
                font_info['external_stylesheets'].append(href)
        
        # Check for web font imports in head
        for element in soup.find_all(['link', 'style']):
            if element.name == 'link' and element.get('rel') == ['stylesheet']:
                href = element.get('href', '')
                if any(webfont in href.lower() for webfont in ['fonts.googleapis', 'fonts.gstatic', 'typekit', 'fontawesome']):
                    font_info['web_fonts'].append(href)
                    font_info['fonts_found'] = True
        
        return font_info
    
    def _extract_font_families_from_css(self, css_content):
        """Extract font families from CSS"""
        font_families = []
        
        # Simple regex for font-family
        font_family_pattern = r'font-family\s*:\s*([^;]+)'
        matches = re.findall(font_family_pattern, css_content, re.IGNORECASE)
        
        for match in matches:
            # Clean up the match
            fonts = match.strip()
            # Remove quotes and split by comma
            fonts = fonts.replace('"', '').replace("'", '')
            font_list = [f.strip() for f in fonts.split(',')]
            font_families.extend(font_list)
        
        return font_families
    
    def _extract_font_sizes_from_css(self, css_content):
        """Extract font sizes from CSS"""
        font_sizes = []
        
        # Regex for font-size
        font_size_pattern = r'font-size\s*:\s*([^;]+)'
        matches = re.findall(font_size_pattern, css_content, re.IGNORECASE)
        
        for match in matches:
            size = match.strip()
            font_sizes.append(size)
        
        return font_sizes
    
    def _extract_font_face_rules(self, css_content):
        """Extract @font-face rules from CSS"""
        font_faces = []
        
        # Regex for @font-face rules
        font_face_pattern = r'@font-face\s*\{[^}]+\}'
        matches = re.findall(font_face_pattern, css_content, re.IGNORECASE | re.DOTALL)
        
        for match in matches:
            font_faces.append(match)
        
        return font_faces
    
    def _analyze_font_stack(self, font_info, url):
        """Analyze font stack for fallbacks"""
        test_cases = []
        font_families = list(font_info['font_families'])
        
        if not font_families:
            return test_cases
        
        # Check for font stacks (multiple fallbacks)
        for font_declaration in font_families:
            fonts = [f.strip() for f in font_declaration.split(',')]
            
            if len(fonts) > 1:
                test_cases.append(self._create_font_test_case(
                    url=url,
                    module="Font Stack",
                    description="Check font fallback stack",
                    test_steps="1. Analyze font-family declarations\n2. Check for fallback fonts\n3. Evaluate stack quality",
                    expected_result="Font declarations should include fallback fonts",
                    actual_result=f"Good font stack found: {', '.join(fonts[:3])}...",
                    status="Pass",
                    severity="Low"
                ))
            else:
                test_cases.append(self._create_font_test_case(
                    url=url,
                    module="Font Stack",
                    description="Check font fallback stack",
                    test_steps="1. Analyze font-family declarations\n2. Check for fallback fonts\n3. Evaluate stack quality",
                    expected_result="Font declarations should include fallback fonts",
                    actual_result=f"Single font without fallbacks: {fonts[0]}",
                    status="Warning",
                    severity="Low",
                    resolutions="Add fallback fonts to font stack (e.g., Arial, sans-serif)"
                ))
        
        # Check for system fonts vs web fonts
        system_fonts = {'Arial', 'Helvetica', 'Times New Roman', 'Georgia', 'Verdana', 
                       'Tahoma', 'Trebuchet MS', 'Courier New', 'sans-serif', 'serif', 'monospace'}
        
        web_font_count = 0
        system_font_count = 0
        
        for font in font_families:
            if any(sys_font in font for sys_font in system_fonts):
                system_font_count += 1
            else:
                web_font_count += 1
        
        if web_font_count > 0:
            test_cases.append(self._create_font_test_case(
                url=url,
                module="Font Types",
                description="Check font types used",
                test_steps="1. Categorize fonts\n2. Count web vs system fonts\n3. Analyze usage",
                expected_result="Mix of web and system fonts is acceptable",
                actual_result=f"Web fonts: {web_font_count}, System fonts: {system_font_count}",
                status="Info",
                severity="Low"
            ))
        
        return test_cases
    
    def _analyze_font_sizes(self, font_info, url):
        """Analyze font sizes for readability"""
        test_cases = []
        font_sizes = font_info['font_sizes']
        
        if not font_sizes:
            return test_cases
        
        # Analyze font size values
        problematic_sizes = []
        good_sizes = []
        
        for size in font_sizes:
            size_lower = size.lower()
            
            # Check for absolute units
            if 'px' in size_lower:
                try:
                    px_value = float(size_lower.replace('px', '').strip())
                    if px_value < 12:
                        problematic_sizes.append(f"{size} (too small)")
                    elif px_value > 24:
                        problematic_sizes.append(f"{size} (very large)")
                    else:
                        good_sizes.append(size)
                except:
                    pass
            elif 'pt' in size_lower:
                try:
                    pt_value = float(size_lower.replace('pt', '').strip())
                    if pt_value < 10:
                        problematic_sizes.append(f"{size} (too small)")
                    else:
                        good_sizes.append(size)
                except:
                    pass
            elif any(unit in size_lower for unit in ['em', 'rem', '%']):
                # Relative units are good for accessibility
                good_sizes.append(size)
            elif size_lower in ['xx-small', 'x-small', 'small']:
                problematic_sizes.append(f"{size} (too small)")
            else:
                good_sizes.append(size)
        
        if problematic_sizes:
            test_cases.append(self._create_font_test_case(
                url=url,
                module="Font Sizes",
                description="Check font size readability",
                test_steps="1. Extract font sizes\n2. Check for accessibility\n3. Identify issues",
                expected_result="Font sizes should be readable",
                actual_result=f"Problematic sizes: {', '.join(problematic_sizes[:3])}",
                status="Warning",
                severity="Low",
                resolutions="Increase font sizes below 12px for better readability"
            ))
        
        if good_sizes:
            test_cases.append(self._create_font_test_case(
                url=url,
                module="Font Sizes",
                description="Check font size usage",
                test_steps="1. Extract font sizes\n2. Analyze units used\n3. Evaluate readability",
                expected_result="Font sizes should use appropriate units",
                actual_result=f"Using {len(good_sizes)} acceptable font sizes",
                status="Pass",
                severity="Low"
            ))
        
        return test_cases
    
    def _analyze_webfonts(self, font_info, url):
        """Analyze web font usage"""
        test_cases = []
        web_fonts = font_info['web_fonts']
        
        if not web_fonts:
            return test_cases
        
        # Check for Google Fonts
        google_fonts = [f for f in web_fonts if 'fonts.googleapis' in f]
        if google_fonts:
            test_cases.append(self._create_font_test_case(
                url=url,
                module="Web Fonts",
                description="Check web font usage",
                test_steps="1. Identify web font imports\n2. Check sources\n3. Analyze performance impact",
                expected_result="Web fonts should be optimized",
                actual_result=f"Using Google Fonts: {len(google_fonts)} font families",
                status="Info",
                severity="Low",
                comments="Consider font-display: swap for better performance"
            ))
        
        # Check for multiple web font requests
        if len(web_fonts) > 3:
            test_cases.append(self._create_font_test_case(
                url=url,
                module="Web Font Performance",
                description="Check web font performance",
                test_steps="1. Count web font requests\n2. Analyze performance impact\n3. Check optimization",
                expected_result="Minimize web font requests",
                actual_result=f"Multiple web font requests: {len(web_fonts)}",
                status="Warning",
                severity="Low",
                resolutions="Combine web font requests or reduce number of font families"
            ))
        
        return test_cases
    
    def _analyze_font_loading(self, font_info, url):
        """Analyze font loading strategy"""
        test_cases = []
        
        # Check for font-display property (would need CSS parsing)
        # This is a simplified check
        
        # Check for font preloading
        soup = BeautifulSoup(requests.get(url, timeout=5).content, 'html.parser')
        preload_links = soup.find_all('link', rel='preload')
        font_preloads = [link for link in preload_links if 'font' in link.get('as', '').lower()]
        
        if font_preloads:
            test_cases.append(self._create_font_test_case(
                url=url,
                module="Font Loading",
                description="Check font loading optimization",
                test_steps="1. Check for font preloading\n2. Analyze loading strategy\n3. Evaluate performance",
                expected_result="Critical fonts should be preloaded",
                actual_result="Font preloading detected",
                status="Pass",
                severity="Low"
            ))
        
        return test_cases
    
    def _create_font_test_case(self, **kwargs):
        """Helper method to create font test cases"""
        if self.test_case_manager:
            return self.test_case_manager.create_test_case(
                test_type="Font Analysis",
                module=kwargs.get('module', 'Font Analysis'),
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