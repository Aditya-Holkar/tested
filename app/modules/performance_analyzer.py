# modules/performance_analyzer.py - Performance analysis
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from config import PERFORMANCE_THRESHOLDS
from modules.test_case_manager import TestCaseManager

class PerformanceAnalyzer:
    """Analyze website performance"""
    
    def __init__(self, test_case_manager=None):
        self.test_case_manager = test_case_manager
    
    def analyze_performance(self, url):
        """Perform comprehensive performance analysis"""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Page Load Time Analysis
            load_time_test_cases = self.analyze_page_load_times(url, response)
            test_cases.extend(load_time_test_cases)
            
            # 2. Resource Analysis
            resource_test_cases = self.analyze_page_resources(soup, url)
            test_cases.extend(resource_test_cases)
            
            # 3. Network Analysis
            network_test_cases = self.analyze_network_performance(url)
            test_cases.extend(network_test_cases)
            
            # 4. Cache Analysis
            cache_test_cases = self.analyze_caching(response, url)
            test_cases.extend(cache_test_cases)
            
            # 5. JavaScript Performance
            js_test_cases = self.analyze_javascript_performance(soup, url)
            test_cases.extend(js_test_cases)
            
            # 6. CSS Performance
            css_test_cases = self.analyze_css_performance(soup, url)
            test_cases.extend(css_test_cases)
            
            # 7. Image Optimization
            image_test_cases = self.analyze_image_performance(soup, url)
            test_cases.extend(image_test_cases)
            
            # 8. Overall Performance Score
            score_test_case = self.calculate_performance_score(test_cases, url)
            test_cases.append(score_test_case)
            
            return test_cases
            
        except Exception as e:
            if self.test_case_manager:
                error_test_case = self.test_case_manager.create_test_case(
                    test_type="Performance Analysis",
                    module="Performance Analysis",
                    test_data=url,
                    description="Perform comprehensive performance analysis",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Measure performance metrics\n3. Analyze bottlenecks",
                    expected_result="Performance analysis completed successfully",
                    actual_result=f"Error during performance analysis: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium",
                    comments="Performance analysis failed due to error",
                    resolutions="Check network connectivity and webpage accessibility"
                )
                return [error_test_case]
            return []
    
    def analyze_page_load_times(self, url, response):
        """Analyze page load times and performance metrics."""
        test_cases = []
        
        try:
            # Calculate total load time
            load_time = response.elapsed.total_seconds() * 1000  # Convert to milliseconds
            page_size_kb = len(response.content) / 1024
            
            # Test 1: Total Load Time
            if load_time <= PERFORMANCE_THRESHOLDS['load_time']:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Page Load Time",
                    description="Measure total page load time",
                    test_steps="1. Send HTTP request\n2. Measure response time\n3. Calculate load time",
                    expected_result=f"Page should load within {PERFORMANCE_THRESHOLDS['load_time']}ms",
                    actual_result=f"Total load time: {load_time:.0f}ms (Good)",
                    status="Pass",
                    severity="High"
                ))
            else:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Page Load Time",
                    description="Measure total page load time",
                    test_steps="1. Send HTTP request\n2. Measure response time\n3. Calculate load time",
                    expected_result=f"Page should load within {PERFORMANCE_THRESHOLDS['load_time']}ms",
                    actual_result=f"Total load time: {load_time:.0f}ms (Slow)",
                    status="Fail",
                    severity="High",
                    resolutions="Optimize server response time, compress resources, use CDN"
                ))
            
            # Test 2: Page Size
            if page_size_kb <= PERFORMANCE_THRESHOLDS['page_size']:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Page Size",
                    description="Calculate total page size",
                    test_steps="1. Get response content\n2. Calculate size\n3. Check against threshold",
                    expected_result=f"Page should be under {PERFORMANCE_THRESHOLDS['page_size']}KB",
                    actual_result=f"Page size: {page_size_kb:.1f}KB (Good)",
                    status="Pass",
                    severity="Medium"
                ))
            else:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Page Size",
                    description="Calculate total page size",
                    test_steps="1. Get response content\n2. Calculate size\n3. Check against threshold",
                    expected_result=f"Page should be under {PERFORMANCE_THRESHOLDS['page_size']}KB",
                    actual_result=f"Page size: {page_size_kb:.1f}KB (Large)",
                    status="Fail",
                    severity="Medium",
                    resolutions="Compress images, minify CSS/JS, remove unused code"
                ))
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_performance_test_case(
                url=url,
                module="Load Time Analysis",
                description="Analyze page load times",
                test_steps="1. Measure load time\n2. Calculate page size\n3. Estimate TTFB",
                expected_result="Load time analysis completed successfully",
                actual_result=f"Error analyzing load times: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def analyze_page_resources(self, soup, url):
        """Analyze page resources and their impact on performance."""
        test_cases = []
        
        try:
            # Count resources
            css_files = len(soup.find_all('link', rel='stylesheet'))
            js_files = len(soup.find_all('script', src=True))
            images = len(soup.find_all('img', src=True))
            total_resources = css_files + js_files + images
            
            # Test 1: Total Resource Count
            if total_resources <= PERFORMANCE_THRESHOLDS['requests']:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Resource Count",
                    description="Count total page resources",
                    test_steps="1. Parse HTML\n2. Count CSS, JS, and image files\n3. Calculate total",
                    expected_result=f"Total resources should be under {PERFORMANCE_THRESHOLDS['requests']}",
                    actual_result=f"Total resources: {total_resources} (CSS: {css_files}, JS: {js_files}, Images: {images})",
                    status="Pass",
                    severity="Medium"
                ))
            else:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Resource Count",
                    description="Count total page resources",
                    test_steps="1. Parse HTML\n2. Count CSS, JS, and image files\n3. Calculate total",
                    expected_result=f"Total resources should be under {PERFORMANCE_THRESHOLDS['requests']}",
                    actual_result=f"Total resources: {total_resources} (Too many)",
                    status="Fail",
                    severity="Medium",
                    resolutions="Combine CSS/JS files, use image sprites, lazy load images"
                ))
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_performance_test_case(
                url=url,
                module="Resource Analysis",
                description="Analyze page resources",
                test_steps="1. Parse HTML\n2. Count resources\n3. Analyze impact",
                expected_result="Resource analysis completed successfully",
                actual_result=f"Error analyzing resources: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def analyze_network_performance(self, url):
        """Analyze network-related performance factors."""
        test_cases = []
        
        try:
            # Test 1: GZIP Compression Check
            headers = {'Accept-Encoding': 'gzip, deflate'}
            response = requests.get(url, headers=headers, timeout=5, verify=False)
            
            if 'gzip' in response.headers.get('Content-Encoding', ''):
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="GZIP Compression",
                    description="Check if GZIP compression is enabled",
                    test_steps="1. Send request with Accept-Encoding header\n2. Check response headers\n3. Verify compression",
                    expected_result="Server should use GZIP compression",
                    actual_result="GZIP compression enabled",
                    status="Pass",
                    severity="Medium"
                ))
            else:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="GZIP Compression",
                    description="Check if GZIP compression is enabled",
                    test_steps="1. Send request with Accept-Encoding header\n2. Check response headers\n3. Verify compression",
                    expected_result="Server should use GZIP compression",
                    actual_result="GZIP compression not enabled",
                    status="Fail",
                    severity="Medium",
                    resolutions="Enable GZIP compression on server for text-based resources"
                ))
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_performance_test_case(
                url=url,
                module="Network Analysis",
                description="Analyze network performance",
                test_steps="1. Check HTTP version\n2. Verify compression\n3. Analyze CDN usage",
                expected_result="Network analysis completed successfully",
                actual_result=f"Error analyzing network: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def analyze_caching(self, response, url):
        """Analyze caching headers and configuration."""
        test_cases = []
        
        try:
            headers = response.headers
            cache_control = headers.get('Cache-Control', '')
            
            if cache_control:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Cache Headers",
                    description="Check Cache-Control headers",
                    test_steps="1. Check response headers\n2. Look for Cache-Control\n3. Analyze caching directives",
                    expected_result="Cache-Control headers should be present",
                    actual_result=f"Cache-Control: {cache_control[:100]}",
                    status="Pass",
                    severity="Medium"
                ))
            else:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Cache Headers",
                    description="Check Cache-Control headers",
                    test_steps="1. Check response headers\n2. Look for Cache-Control\n3. Analyze caching directives",
                    expected_result="Cache-Control headers should be present",
                    actual_result="No Cache-Control header found",
                    status="Fail",
                    severity="Medium",
                    resolutions="Add Cache-Control headers for static resources (e.g., max-age=31536000)"
                ))
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_performance_test_case(
                url=url,
                module="Cache Analysis",
                description="Analyze caching configuration",
                test_steps="1. Check cache headers\n2. Analyze caching directives\n3. Evaluate cache efficiency",
                expected_result="Cache analysis completed successfully",
                actual_result=f"Error analyzing cache: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def analyze_javascript_performance(self, soup, url):
        """Analyze JavaScript performance factors."""
        test_cases = []
        
        try:
            # Find all script tags
            scripts = soup.find_all('script')
            
            # Test 1: Inline JavaScript
            inline_scripts = [s for s in scripts if s.string and s.string.strip()]
            
            if inline_scripts:
                total_inline_size = sum(len(s.string or '') for s in inline_scripts)
                
                if total_inline_size > 10000:  # 10KB threshold
                    test_cases.append(self._create_performance_test_case(
                        url=url,
                        module="Inline JavaScript",
                        description="Check size of inline JavaScript",
                        test_steps="1. Find inline script tags\n2. Calculate total size\n3. Check if excessive",
                        expected_result="Inline JS should be minimal (under 10KB)",
                        actual_result=f"Inline JS size: {total_inline_size/1024:.1f}KB (Large)",
                        status="Fail",
                        severity="Low",
                        resolutions="Move inline JavaScript to external files, defer non-critical JS"
                    ))
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_performance_test_case(
                url=url,
                module="JavaScript Analysis",
                description="Analyze JavaScript performance",
                test_steps="1. Find script tags\n2. Analyze loading strategy\n3. Detect frameworks",
                expected_result="JavaScript analysis completed successfully",
                actual_result=f"Error analyzing JavaScript: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def analyze_css_performance(self, soup, url):
        """Analyze CSS performance factors."""
        test_cases = []
        
        try:
            # Find all CSS links
            css_links = soup.find_all('link', rel='stylesheet')
            style_tags = soup.find_all('style')
            
            # Test 1: Inline CSS
            total_inline_css = 0
            for style in style_tags:
                if style.string:
                    total_inline_css += len(style.string)
            
            if total_inline_css > 5000:  # 5KB threshold
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Inline CSS",
                    description="Check size of inline CSS",
                    test_steps="1. Find style tags\n2. Calculate total size\n3. Check if excessive",
                    expected_result="Inline CSS should be minimal (under 5KB)",
                    actual_result=f"Inline CSS size: {total_inline_css/1024:.1f}KB (Large)",
                    status="Fail",
                    severity="Low",
                    resolutions="Move inline CSS to external files, optimize critical CSS"
                ))
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_performance_test_case(
                url=url,
                module="CSS Analysis",
                description="Analyze CSS performance",
                test_steps="1. Find CSS resources\n2. Analyze delivery\n3. Detect frameworks",
                expected_result="CSS analysis completed successfully",
                actual_result=f"Error analyzing CSS: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def analyze_image_performance(self, soup, url):
        """Analyze image optimization and performance."""
        test_cases = []
        
        try:
            images = soup.find_all('img')
            
            if not images:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Image Analysis",
                    description="Check image optimization",
                    test_steps="1. Find image tags\n2. Analyze image attributes\n3. Check optimization",
                    expected_result="Images should be optimized for web",
                    actual_result="No images found on page",
                    status="Pass",
                    severity="Low"
                ))
                return test_cases
            
            # Test 1: Image Format Analysis
            modern_formats = 0
            total_images = len(images)
            
            for img in images:
                src = img.get('src', '').lower()
                if any(fmt in src for fmt in ['.webp', '.avif']):
                    modern_formats += 1
            
            modern_format_percent = (modern_formats / total_images) * 100
            
            if modern_format_percent < 50:
                test_cases.append(self._create_performance_test_case(
                    url=url,
                    module="Image Formats",
                    description="Check for modern image formats",
                    test_steps="1. Find all images\n2. Check file extensions\n3. Count modern formats",
                    expected_result="Use modern formats (WebP, AVIF) when possible",
                    actual_result=f"Modern formats: {modern_format_percent:.1f}% (Low)",
                    status="Warning",
                    severity="Low",
                    resolutions="Convert images to WebP/AVIF format with fallbacks for older browsers"
                ))
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_performance_test_case(
                url=url,
                module="Image Analysis",
                description="Analyze image performance",
                test_steps="1. Find image tags\n2. Analyze formats and attributes\n3. Check optimization",
                expected_result="Image analysis completed successfully",
                actual_result=f"Error analyzing images: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def calculate_performance_score(self, performance_test_cases, url):
        """Calculate overall performance score based on test results."""
        if not performance_test_cases:
            return self._create_performance_test_case(
                url=url,
                module="Performance Score",
                description="Calculate overall performance score",
                test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
                expected_result="High performance score indicates good optimization",
                actual_result="No performance tests were performed",
                status="Fail",
                severity="Medium"
            )
        
        # Weight factors based on severity
        severity_weights = {'Critical': 10, 'High': 5, 'Medium': 3, 'Low': 1, 'Info': 0, 'Warning': 2}
        
        total_weight = 0
        passed_weight = 0
        
        for test_case in performance_test_cases:
            severity = test_case.get('Severity', 'Medium')
            status = test_case.get('Status', 'Fail')
            
            weight = severity_weights.get(severity, 1)
            total_weight += weight
            
            if status.lower() in ['pass', 'passed', 'warning', 'info']:
                passed_weight += weight
        
        if total_weight > 0:
            performance_score = (passed_weight / total_weight) * 100
        else:
            performance_score = 0
        
        # Determine grade
        if performance_score >= 90:
            grade = "A (Excellent)"
            status_result = "Pass"
        elif performance_score >= 80:
            grade = "B (Good)"
            status_result = "Pass"
        elif performance_score >= 70:
            grade = "C (Average)"
            status_result = "Warning"
        elif performance_score >= 60:
            grade = "D (Needs Improvement)"
            status_result = "Fail"
        else:
            grade = "F (Poor)"
            status_result = "Fail"
        
        # Count test results
        passed_tests = sum(1 for tc in performance_test_cases if tc.get('Status', '').lower() in ['pass', 'passed'])
        failed_tests = sum(1 for tc in performance_test_cases if tc.get('Status', '').lower() == 'fail')
        warning_tests = sum(1 for tc in performance_test_cases if tc.get('Status', '').lower() == 'warning')
        
        return self._create_performance_test_case(
            url=url,
            module="Performance Score",
            description="Calculate overall performance score",
            test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
            expected_result="High performance score indicates good optimization",
            actual_result=f"Performance Score: {performance_score:.1f}% - {grade}. Passed: {passed_tests}, Failed: {failed_tests}, Warnings: {warning_tests}",
            status=status_result,
            severity="High" if performance_score < 70 else "Medium",
            resolutions="Address failed tests to improve performance score" if performance_score < 80 else "Maintain current optimizations and monitor regularly"
        )
    
    def _create_performance_test_case(self, **kwargs):
        """Helper method to create performance test cases"""
        if self.test_case_manager:
            return self.test_case_manager.create_test_case(
                test_type="Performance Analysis",
                module=kwargs.get('module', 'Performance'),
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