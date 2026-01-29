# modules/seo_analyzer.py - SEO analysis functions
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import math

class SEOAnalyzer:
    """Analyze SEO aspects of a website"""
    
    def __init__(self, test_case_manager=None):
        self.test_case_manager = test_case_manager
    
    def analyze_seo(self, url):
        """Perform comprehensive SEO analysis"""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Meta Tags Analysis
            meta_test_cases = self.analyze_meta_tags(soup, url)
            test_cases.extend(meta_test_cases)
            
            # 2. Title Analysis
            title_test_cases = self.analyze_title(soup, url)
            test_cases.extend(title_test_cases)
            
            # 3. Heading Structure Analysis
            heading_test_cases = self.analyze_headings(soup, url)
            test_cases.extend(heading_test_cases)
            
            # 4. Content Analysis
            content_test_cases = self.analyze_content(soup, url)
            test_cases.extend(content_test_cases)
            
            # 5. URL Structure Analysis
            url_test_cases = self.analyze_url_structure(url)
            test_cases.extend(url_test_cases)
            
            # 6. Image Optimization Analysis
            image_test_cases = self.analyze_images_seo(soup, url)
            test_cases.extend(image_test_cases)
            
            # 7. Mobile Friendliness Analysis
            mobile_test_cases = self.analyze_mobile_friendliness(soup, url)
            test_cases.extend(mobile_test_cases)
            
            # 8. Technical SEO Analysis
            technical_test_cases = self.analyze_technical_seo(soup, url, response)
            test_cases.extend(technical_test_cases)
            
            # 9. Overall SEO Score
            score_test_case = self.calculate_seo_score(test_cases, url)
            test_cases.append(score_test_case)
            
            return test_cases
            
        except Exception as e:
            if self.test_case_manager:
                error_test_case = self.test_case_manager.create_test_case(
                    test_type="SEO Analysis",
                    module="SEO Analysis",
                    test_data=url,
                    description="Perform comprehensive SEO analysis",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Extract SEO elements\n3. Analyze SEO factors",
                    expected_result="SEO analysis completed successfully",
                    actual_result=f"Error during SEO analysis: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium",
                    comments="SEO analysis failed due to error",
                    resolutions="Check network connectivity and webpage accessibility"
                )
                return [error_test_case]
            return []
    
    def analyze_meta_tags(self, soup, url):
        """Analyze meta tags for SEO"""
        test_cases = []
        
        # Check for meta description
        meta_description = soup.find('meta', attrs={'name': 'description'})
        if meta_description:
            description = meta_description.get('content', '')
            desc_length = len(description)
            
            if 150 <= desc_length <= 160:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="Meta Description",
                    description="Check meta description length and content",
                    test_steps="1. Find meta description tag\n2. Check length\n3. Analyze content",
                    expected_result="Meta description should be 150-160 characters",
                    actual_result=f"Meta description length: {desc_length} characters (Good)",
                    status="Pass",
                    severity="Medium"
                ))
            else:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="Meta Description",
                    description="Check meta description length and content",
                    test_steps="1. Find meta description tag\n2. Check length\n3. Analyze content",
                    expected_result="Meta description should be 150-160 characters",
                    actual_result=f"Meta description length: {desc_length} characters (Needs adjustment)",
                    status="Fail" if desc_length == 0 else "Warning",
                    severity="Medium",
                    resolutions="Optimize meta description to be 150-160 characters with relevant keywords"
                ))
        else:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Meta Description",
                description="Check for meta description tag",
                test_steps="1. Look for meta description tag\n2. Check if present",
                expected_result="Page should have meta description",
                actual_result="No meta description found",
                status="Fail",
                severity="High",
                resolutions="Add meta description tag with relevant page summary"
            ))
        
        # Check for meta keywords (less important now)
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Meta Keywords",
                description="Check for meta keywords",
                test_steps="1. Find meta keywords tag\n2. Check usage",
                expected_result="Meta keywords are optional but can be included",
                actual_result="Meta keywords found",
                status="Info",
                severity="Low",
                comments="Meta keywords have limited SEO value but can be included"
            ))
        
        # Check for viewport meta tag
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Viewport Meta Tag",
                description="Check for viewport meta tag",
                test_steps="1. Find viewport meta tag\n2. Check content",
                expected_result="Page should have viewport meta tag for mobile responsiveness",
                actual_result="Viewport meta tag found",
                status="Pass",
                severity="Medium"
            ))
        else:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Viewport Meta Tag",
                description="Check for viewport meta tag",
                test_steps="1. Find viewport meta tag\n2. Check if present",
                expected_result="Page should have viewport meta tag for mobile responsiveness",
                actual_result="No viewport meta tag found",
                status="Fail",
                severity="Medium",
                resolutions="Add viewport meta tag: <meta name='viewport' content='width=device-width, initial-scale=1.0'>"
            ))
        
        # Check for robots meta tag
        robots = soup.find('meta', attrs={'name': 'robots'})
        if robots:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Robots Meta Tag",
                description="Check robots meta tag",
                test_steps="1. Find robots meta tag\n2. Check directives",
                expected_result="Robots meta tag should allow indexing",
                actual_result=f"Robots meta tag found: {robots.get('content', '')}",
                status="Pass",
                severity="Low"
            ))
        
        return test_cases
    
    def analyze_title(self, soup, url):
        """Analyze page title for SEO"""
        test_cases = []
        
        title_tag = soup.find('title')
        if title_tag:
            title_text = title_tag.get_text(strip=True)
            title_length = len(title_text)
            
            if 50 <= title_length <= 60:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="Page Title",
                    description="Check page title length and content",
                    test_steps="1. Find title tag\n2. Check length\n3. Analyze content",
                    expected_result="Title should be 50-60 characters",
                    actual_result=f"Title length: {title_length} characters (Good): {title_text[:50]}...",
                    status="Pass",
                    severity="High"
                ))
            else:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="Page Title",
                    description="Check page title length and content",
                    test_steps="1. Find title tag\n2. Check length\n3. Analyze content",
                    expected_result="Title should be 50-60 characters",
                    actual_result=f"Title length: {title_length} characters (Needs adjustment): {title_text[:50]}...",
                    status="Fail" if title_length == 0 else "Warning",
                    severity="High",
                    resolutions="Optimize title to be 50-60 characters with primary keywords first"
                ))
            
            # Check for keyword in title
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.split('/')
            relevant_keywords = [part for part in path_parts if part and len(part) > 3]
            
            if relevant_keywords:
                keyword_found = any(keyword.lower() in title_text.lower() for keyword in relevant_keywords)
                if keyword_found:
                    test_cases.append(self._create_seo_test_case(
                        url=url,
                        module="Title Keywords",
                        description="Check for relevant keywords in title",
                        test_steps="1. Extract relevant keywords from URL\n2. Check if in title\n3. Verify placement",
                        expected_result="Title should contain relevant keywords",
                        actual_result="Relevant keywords found in title",
                        status="Pass",
                        severity="Medium"
                    ))
        else:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Page Title",
                description="Check for page title",
                test_steps="1. Look for title tag\n2. Check if present",
                expected_result="Page must have a title tag",
                actual_result="No title tag found",
                status="Fail",
                severity="Critical",
                resolutions="Add descriptive title tag to the page"
            ))
        
        return test_cases
    
    def analyze_headings(self, soup, url):
        """Analyze heading structure for SEO"""
        test_cases = []
        
        # Count headings
        headings = {}
        for i in range(1, 7):
            headings[f'h{i}'] = soup.find_all(f'h{i}')
        
        total_headings = sum(len(h) for h in headings.values())
        
        if total_headings > 0:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Heading Structure",
                description="Check heading hierarchy",
                test_steps="1. Count all heading tags\n2. Check hierarchy\n3. Analyze structure",
                expected_result="Page should use proper heading hierarchy",
                actual_result=f"Total headings: {total_headings} (H1: {len(headings['h1'])}, H2: {len(headings['h2'])}, H3: {len(headings['h3'])})",
                status="Pass" if len(headings['h1']) > 0 else "Warning",
                severity="Medium",
                comments="Good heading structure improves content organization"
            ))
            
            # Check for single H1
            if len(headings['h1']) == 1:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="H1 Heading",
                    description="Check for single H1 heading",
                    test_steps="1. Count H1 tags\n2. Verify only one exists\n3. Check content",
                    expected_result="Page should have exactly one H1 heading",
                    actual_result="Found exactly one H1 heading",
                    status="Pass",
                    severity="High"
                ))
            elif len(headings['h1']) > 1:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="H1 Heading",
                    description="Check for single H1 heading",
                    test_steps="1. Count H1 tags\n2. Verify only one exists\n3. Check content",
                    expected_result="Page should have exactly one H1 heading",
                    actual_result=f"Found {len(headings['h1'])} H1 headings (should be exactly one)",
                    status="Fail",
                    severity="High",
                    resolutions="Ensure only one H1 tag per page, representing main content"
                ))
            else:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="H1 Heading",
                    description="Check for H1 heading",
                    test_steps="1. Look for H1 tags\n2. Check if present",
                    expected_result="Page should have at least one H1 heading",
                    actual_result="No H1 heading found",
                    status="Fail",
                    severity="High",
                    resolutions="Add a descriptive H1 heading representing the main content"
                ))
        else:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Heading Structure",
                description="Check heading structure",
                test_steps="1. Look for heading tags\n2. Check if any exist",
                expected_result="Page should use headings for content structure",
                actual_result="No heading tags found",
                status="Fail",
                severity="Medium",
                resolutions="Add heading tags (H1, H2, H3) to structure content"
            ))
        
        return test_cases
    
    def analyze_content(self, soup, url):
        """Analyze page content for SEO"""
        test_cases = []
        
        # Get all text content
        all_text = soup.get_text()
        text_length = len(all_text)
        
        if text_length < 300:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Content Length",
                description="Check page content length",
                test_steps="1. Extract all text\n2. Calculate length\n3. Check minimum requirements",
                expected_result="Page should have sufficient content (minimum 300 words)",
                actual_result=f"Content length: {text_length} characters (Too short)",
                status="Fail",
                severity="Medium",
                resolutions="Add more relevant content to the page"
            ))
        elif text_length < 1000:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Content Length",
                description="Check page content length",
                test_steps="1. Extract all text\n2. Calculate length\n3. Check minimum requirements",
                expected_result="Page should have sufficient content",
                actual_result=f"Content length: {text_length} characters (Adequate)",
                status="Pass",
                severity="Low"
            ))
        else:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Content Length",
                description="Check page content length",
                test_steps="1. Extract all text\n2. Calculate length\n3. Check minimum requirements",
                expected_result="Page should have sufficient content",
                actual_result=f"Content length: {text_length} characters (Good)",
                status="Pass",
                severity="Low"
            ))
        
        # Check for keyword density (basic check)
        parsed_url = urlparse(url)
        path_keywords = [part for part in parsed_url.path.split('/') if part and len(part) > 3]
        
        if path_keywords:
            main_keyword = path_keywords[-1].replace('-', ' ').replace('_', ' ')
            keyword_count = all_text.lower().count(main_keyword.lower())
            
            if keyword_count > 0:
                # Estimate word count (rough approximation)
                word_count = len(all_text.split())
                density = (keyword_count / max(word_count, 1)) * 100
                
                if 1 <= density <= 3:
                    test_cases.append(self._create_seo_test_case(
                        url=url,
                        module="Keyword Usage",
                        description="Check keyword usage in content",
                        test_steps="1. Identify main keyword\n2. Count occurrences\n3. Calculate density",
                        expected_result="Keyword density should be 1-3%",
                        actual_result=f"Keyword '{main_keyword}' density: {density:.1f}% (Good)",
                        status="Pass",
                        severity="Low"
                    ))
                elif density > 3:
                    test_cases.append(self._create_seo_test_case(
                        url=url,
                        module="Keyword Usage",
                        description="Check keyword usage in content",
                        test_steps="1. Identify main keyword\n2. Count occurrences\n3. Calculate density",
                        expected_result="Keyword density should be 1-3%",
                        actual_result=f"Keyword '{main_keyword}' density: {density:.1f}% (Too high - risk of keyword stuffing)",
                        status="Warning",
                        severity="Low",
                        resolutions="Reduce keyword usage to avoid keyword stuffing"
                    ))
        
        return test_cases
    
    def analyze_url_structure(self, url):
        """Analyze URL structure for SEO"""
        test_cases = []
        parsed_url = urlparse(url)
        
        # Check URL length
        url_length = len(url)
        if url_length <= 100:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="URL Length",
                description="Check URL length",
                test_steps="1. Measure URL length\n2. Check if within limits",
                expected_result="URL should be short and descriptive",
                actual_result=f"URL length: {url_length} characters (Good)",
                status="Pass",
                severity="Low"
            ))
        else:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="URL Length",
                description="Check URL length",
                test_steps="1. Measure URL length\n2. Check if within limits",
                expected_result="URL should be short and descriptive",
                actual_result=f"URL length: {url_length} characters (Too long)",
                status="Warning",
                severity="Low",
                resolutions="Shorten URL by removing unnecessary parameters"
            ))
        
        # Check for keywords in URL
        path = parsed_url.path
        if path and len(path) > 1:
            # Check if URL is descriptive
            has_keywords = any(char.isalpha() for char in path.replace('/', '').replace('-', '').replace('_', ''))
            
            if has_keywords:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="URL Keywords",
                    description="Check for keywords in URL",
                    test_steps="1. Analyze URL path\n2. Check for descriptive words",
                    expected_result="URL should contain descriptive keywords",
                    actual_result="URL contains descriptive keywords",
                    status="Pass",
                    severity="Low"
                ))
            else:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="URL Keywords",
                    description="Check for keywords in URL",
                    test_steps="1. Analyze URL path\n2. Check for descriptive words",
                    expected_result="URL should contain descriptive keywords",
                    actual_result="URL lacks descriptive keywords",
                    status="Warning",
                    severity="Low",
                    resolutions="Use descriptive keywords in URL slugs"
                ))
        
        # Check for special characters
        if '%' in url or '?' in url or '&' in url or '=' in url:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="URL Parameters",
                description="Check for URL parameters",
                test_steps="1. Check for query parameters\n2. Analyze parameter usage",
                expected_result="URL should avoid excessive parameters",
                actual_result="URL contains parameters or special characters",
                status="Info",
                severity="Low",
                comments="Consider using clean URLs without parameters when possible"
            ))
        
        return test_cases
    
    def analyze_images_seo(self, soup, url):
        """Analyze image optimization for SEO"""
        test_cases = []
        images = soup.find_all('img')
        
        if not images:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Image SEO",
                description="Check image optimization",
                test_steps="1. Find image tags\n2. Check alt attributes\n3. Analyze optimization",
                expected_result="Images should be optimized for SEO",
                actual_result="No images found on page",
                status="Pass",
                severity="Low"
            ))
            return test_cases
        
        # Check for alt text
        images_with_alt = 0
        images_without_alt = 0
        
        for img in images:
            alt = img.get('alt', '')
            if alt and alt.strip():
                images_with_alt += 1
            else:
                images_without_alt += 1
        
        alt_percentage = (images_with_alt / len(images)) * 100
        
        if alt_percentage >= 90:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Image Alt Text",
                description="Check image alt attributes",
                test_steps="1. Find all images\n2. Check alt attributes\n3. Calculate percentage",
                expected_result="All images should have descriptive alt text",
                actual_result=f"{alt_percentage:.1f}% of images have alt text (Good)",
                status="Pass",
                severity="Medium"
            ))
        else:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Image Alt Text",
                description="Check image alt attributes",
                test_steps="1. Find all images\n2. Check alt attributes\n3. Calculate percentage",
                expected_result="All images should have descriptive alt text",
                actual_result=f"Only {alt_percentage:.1f}% of images have alt text",
                status="Fail",
                severity="Medium",
                resolutions="Add descriptive alt text to all images"
            ))
        
        # Check for image file names
        descriptive_filenames = 0
        for img in images:
            src = img.get('src', '')
            if src:
                filename = src.split('/')[-1].split('.')[0].lower()
                # Check if filename is descriptive (not just numbers)
                if any(char.isalpha() for char in filename) and len(filename) > 3:
                    descriptive_filenames += 1
        
        if descriptive_filenames > 0:
            filename_percentage = (descriptive_filenames / len(images)) * 100
            if filename_percentage >= 50:
                test_cases.append(self._create_seo_test_case(
                    url=url,
                    module="Image Filenames",
                    description="Check image filename descriptiveness",
                    test_steps="1. Extract image filenames\n2. Check for descriptive names\n3. Calculate percentage",
                    expected_result="Image filenames should be descriptive",
                    actual_result=f"{filename_percentage:.1f}% of images have descriptive filenames",
                    status="Pass",
                    severity="Low"
                ))
        
        return test_cases
    
    def analyze_mobile_friendliness(self, soup, url):
        """Analyze mobile friendliness for SEO"""
        test_cases = []
        
        # Check viewport tag (already checked in meta tags)
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if viewport:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Mobile Viewport",
                description="Check viewport meta tag for mobile",
                test_steps="1. Find viewport meta tag\n2. Check content",
                expected_result="Page should have viewport tag for mobile",
                actual_result="Viewport meta tag found",
                status="Pass",
                severity="Medium"
            ))
        
        # Check for tap targets (basic check)
        interactive_elements = soup.find_all(['a', 'button', 'input', 'select', 'textarea'])
        if interactive_elements:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Mobile Interaction",
                description="Check interactive elements for mobile",
                test_steps="1. Count interactive elements\n2. Check mobile compatibility",
                expected_result="Interactive elements should be mobile-friendly",
                actual_result=f"Found {len(interactive_elements)} interactive elements",
                status="Info",
                severity="Low",
                comments="Ensure tap targets are at least 44x44 pixels for mobile"
            ))
        
        # Check for mobile-only content (basic)
        media_queries = str(soup).lower().count('@media')
        if media_queries > 0:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Responsive Design",
                description="Check for responsive design CSS",
                test_steps="1. Check for media queries\n2. Count occurrences",
                expected_result="Page should use responsive design",
                actual_result=f"Found {media_queries} media queries",
                status="Pass",
                severity="Low"
            ))
        
        return test_cases
    
    def analyze_technical_seo(self, soup, url, response):
        """Analyze technical SEO factors"""
        test_cases = []
        
        # Check for canonical tag
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Canonical Tag",
                description="Check for canonical URL tag",
                test_steps="1. Look for canonical link tag\n2. Check if present",
                expected_result="Page should have canonical tag",
                actual_result="Canonical tag found",
                status="Pass",
                severity="Medium"
            ))
        else:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Canonical Tag",
                description="Check for canonical URL tag",
                test_steps="1. Look for canonical link tag\n2. Check if present",
                expected_result="Page should have canonical tag",
                actual_result="No canonical tag found",
                status="Warning",
                severity="Low",
                resolutions="Add canonical tag to prevent duplicate content issues"
            ))
        
        # Check for structured data (basic check)
        script_tags = soup.find_all('script', attrs={'type': 'application/ld+json'})
        if script_tags:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Structured Data",
                description="Check for structured data",
                test_steps="1. Look for JSON-LD scripts\n2. Check if present",
                expected_result="Page should use structured data",
                actual_result=f"Found {len(script_tags)} structured data scripts",
                status="Pass",
                severity="Low"
            ))
        
        # Check for sitemap reference (in robots.txt would be better)
        robots_links = soup.find_all('a', href=lambda x: x and 'sitemap' in x.lower())
        if robots_links:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Sitemap Reference",
                description="Check for sitemap references",
                test_steps="1. Look for sitemap links\n2. Check if present",
                expected_result="Site should reference sitemap",
                actual_result="Sitemap reference found",
                status="Pass",
                severity="Low"
            ))
        
        # Check response headers
        headers = response.headers
        if 'X-Robots-Tag' in headers:
            test_cases.append(self._create_seo_test_case(
                url=url,
                module="Robots Headers",
                description="Check robots HTTP headers",
                test_steps="1. Check response headers\n2. Look for robots directives",
                expected_result="Robots headers should allow indexing",
                actual_result=f"X-Robots-Tag found: {headers.get('X-Robots-Tag')}",
                status="Info",
                severity="Low"
            ))
        
        return test_cases
    
    def calculate_seo_score(self, seo_test_cases, url):
        """Calculate overall SEO score based on test results"""
        if not seo_test_cases:
            return self._create_seo_test_case(
                url=url,
                module="SEO Score",
                description="Calculate overall SEO score",
                test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
                expected_result="High SEO score indicates good optimization",
                actual_result="No SEO tests were performed",
                status="Fail",
                severity="Medium"
            )
        
        # Weight factors based on severity
        severity_weights = {'Critical': 10, 'High': 5, 'Medium': 3, 'Low': 1, 'Info': 0, 'Warning': 2}
        
        total_weight = 0
        passed_weight = 0
        
        for test_case in seo_test_cases:
            severity = test_case.get('Severity', 'Medium')
            status = test_case.get('Status', 'Fail')
            
            weight = severity_weights.get(severity, 1)
            total_weight += weight
            
            if status.lower() in ['pass', 'passed', 'warning', 'info']:
                passed_weight += weight
        
        if total_weight > 0:
            seo_score = (passed_weight / total_weight) * 100
        else:
            seo_score = 0
        
        # Determine grade
        if seo_score >= 90:
            grade = "A (Excellent)"
            status_result = "Pass"
        elif seo_score >= 80:
            grade = "B (Good)"
            status_result = "Pass"
        elif seo_score >= 70:
            grade = "C (Average)"
            status_result = "Warning"
        elif seo_score >= 60:
            grade = "D (Needs Improvement)"
            status_result = "Fail"
        else:
            grade = "F (Poor)"
            status_result = "Fail"
        
        # Count test results
        passed_tests = sum(1 for tc in seo_test_cases if tc.get('Status', '').lower() in ['pass', 'passed'])
        failed_tests = sum(1 for tc in seo_test_cases if tc.get('Status', '').lower() == 'fail')
        warning_tests = sum(1 for tc in seo_test_cases if tc.get('Status', '').lower() == 'warning')
        
        return self._create_seo_test_case(
            url=url,
            module="SEO Score",
            description="Calculate overall SEO score",
            test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
            expected_result="High SEO score indicates good optimization",
            actual_result=f"SEO Score: {seo_score:.1f}% - {grade}. Passed: {passed_tests}, Failed: {failed_tests}, Warnings: {warning_tests}",
            status=status_result,
            severity="High" if seo_score < 70 else "Medium",
            resolutions="Address failed tests to improve SEO score" if seo_score < 80 else "Maintain current SEO optimizations and monitor regularly"
        )
    
    def _create_seo_test_case(self, **kwargs):
        """Helper method to create SEO test cases"""
        if self.test_case_manager:
            return self.test_case_manager.create_test_case(
                test_type="SEO Analysis",
                module=kwargs.get('module', 'SEO'),
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