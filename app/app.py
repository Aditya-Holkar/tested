# app.py - Main Flask application
from flask import Flask, render_template, request, jsonify, send_file, session
import json
import numpy as np
import os
from datetime import datetime
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import modules
from config import Config
from modules.url_processor import URLProcessor
from modules.link_checker import LinkChecker
from modules.performance_analyzer import PerformanceAnalyzer
from modules.accessibility_tester import AccessibilityTester
from modules.test_case_manager import TestCaseManager
from modules.seo_analyzer import SEOAnalyzer
from modules.button_tester import ButtonTester
from modules.spelling_checker import SpellingChecker
from modules.font_analyzer import FontAnalyzer
from modules.responsiveness_checker import ResponsivenessChecker
from modules.browser_compatibility import BrowserCompatibility
from modules.report_generator import ReportGenerator

application = Flask(__name__)
app.config.from_object(Config)
tester_data = {}
# Global variables for session storage
# app.secret_key = 'your-secret-key-here'  

class WebsiteTester:
    """Main website tester class"""
    
    def __init__(self):
        self.test_case_manager = TestCaseManager()
        self.url_processor = URLProcessor()
        self.link_checker = LinkChecker(self.test_case_manager)
        self.performance_analyzer = PerformanceAnalyzer(self.test_case_manager)
        self.accessibility_tester = AccessibilityTester(self.test_case_manager)
        self.seo_analyzer = SEOAnalyzer(self.test_case_manager)
        self.button_tester = ButtonTester(self.test_case_manager)
        self.spelling_checker = SpellingChecker(self.test_case_manager)
        self.font_analyzer = FontAnalyzer(self.test_case_manager)
        self.responsiveness_checker = ResponsivenessChecker(self.test_case_manager)
        self.browser_compatibility = BrowserCompatibility(self.test_case_manager)
        self.report_generator = ReportGenerator()
        
        # Data storage
        self.extracted_links = []
        self.current_results = []
        self.button_test_results = []
        self.spelling_results = []
        self.font_results = []
        self.responsiveness_results = []
        self.browser_compatibility_results = []
        self.seo_results = []
        self.performance_results = []
        self.accessibility_results = []
    
    def clear_all(self):
        """Clear all data"""
        self.extracted_links = []
        self.current_results = []
        self.button_test_results = []
        self.spelling_results = []
        self.font_results = []
        self.responsiveness_results = []
        self.browser_compatibility_results = []
        self.seo_results = []
        self.performance_results = []
        self.accessibility_results = []
        self.test_case_manager.clear_test_cases()
    
    def extract_links(self, website_url, max_links=500):
        """Extract links from website"""
        try:
            self.extracted_links = self.url_processor.scrape_all_links(
                website_url, 
                max_depth=2, 
                max_links=max_links
            )
            return True, f"Extracted {len(self.extracted_links)} unique links"
        except Exception as e:
            return False, f"Failed to extract links: {str(e)}"
    
    def run_tests(self, urls, test_options):
        """Run selected tests on URLs"""
        # Clear previous results
        self.clear_all()
        
        # Remove duplicates
        self.extracted_links = self.url_processor.remove_duplicate_urls(urls)
        
        if not self.extracted_links:
            return False, "No valid URLs to test"
        
        results = {}
        
        # Run tests based on options
        if test_options.get('link_check', True):
            results['link_results'] = self.run_link_tests()
        
        if test_options.get('performance_check', False):
            results['performance_results'] = self.run_performance_tests()
        
        if test_options.get('accessibility_check', False):
            results['accessibility_results'] = self.run_accessibility_tests()
        
        if test_options.get('seo_check', False):
            results['seo_results'] = self.run_seo_tests()
        
        if test_options.get('button_test', True):
            results['button_results'] = self.run_button_tests()
        
        if test_options.get('spell_check', False):
            results['spelling_results'] = self.run_spelling_tests()
        
        # Add more tests as needed...
        
        return True, "Tests completed successfully"
    
    def run_link_tests(self):
        """Run link status tests"""
        results = []
        test_cases = []
        
        for url in self.extracted_links[:50]:  # Limit to 50 URLs for demo
            result_display, result_structured, test_case = self.link_checker.check_status(url)
            results.append(result_structured)
            if test_case:
                test_cases.append(test_case)
        
        self.current_results = results
        return results
    
    def run_performance_tests(self):
        """Run performance tests on successful URLs"""
        results = []
        successful_urls = [r['url'] for r in self.current_results 
                          if r.get('status_category') == 'Success' and r.get('status_code') == 200]
        
        for url in successful_urls[:3]:  # Limit to 3 URLs
            test_cases = self.performance_analyzer.analyze_performance(url)
            results.extend(test_cases)
        
        self.performance_results = results
        return results
    
    def run_accessibility_tests(self):
        """Run accessibility tests on successful URLs"""
        results = []
        successful_urls = [r['url'] for r in self.current_results 
                          if r.get('status_category') == 'Success' and r.get('status_code') == 200]
        
        for url in successful_urls[:3]:  # Limit to 3 URLs
            test_cases = self.accessibility_tester.analyze_accessibility(url)
            results.extend(test_cases)
        
        self.accessibility_results = results
        return results
    
    def run_seo_tests(self):
        """Run SEO tests on successful URLs"""
        results = []
        successful_urls = [r['url'] for r in self.current_results 
                          if r.get('status_category') == 'Success' and r.get('status_code') == 200]
        
        for url in successful_urls[:3]:  # Limit to 3 URLs
            test_cases = self.seo_analyzer.analyze_seo(url)
            results.extend(test_cases)
        
        self.seo_results = results
        return results
    
    def run_button_tests(self):
        """Run button tests on successful URLs"""
        results = []
        successful_urls = [r['url'] for r in self.current_results 
                          if r.get('status_category') == 'Success' and r.get('status_code') == 200]
        
        for url in successful_urls[:3]:  # Limit to 3 URLs
            test_cases = self.button_tester.test_buttons_on_page(url)
            results.extend(test_cases)
        
        self.button_test_results = results
        return results
    
    def run_spelling_tests(self):
        """Run spelling tests on successful URLs"""
        results = []
        successful_urls = [r['url'] for r in self.current_results 
                          if r.get('status_category') == 'Success' and r.get('status_code') == 200]
        
        for url in successful_urls[:3]:  # Limit to 3 URLs
            test_cases = self.spelling_checker.check_spelling_on_page(url)
            results.extend(test_cases)
        
        self.spelling_results = results
        return results
    
    def get_summary(self):
        """Get test summary"""
        stats = self.test_case_manager.get_statistics()
        
        summary = {
            'total_urls': len(self.extracted_links),
            'total_test_cases': stats['total'],
            'passed_test_cases': stats['passed'],
            'failed_test_cases': stats['failed'],
            'pass_rate': stats['pass_rate'],
            'link_results': len(self.current_results),
            'performance_results': len(self.performance_results),
            'accessibility_results': len(self.accessibility_results),
            'seo_results': len(self.seo_results),
            'button_results': len(self.button_test_results),
            'spelling_results': len(self.spelling_results)
        }
        
        return summary
    
    def export_report(self, format='json'):
        """Export report in specified format"""
        all_data = {
            'summary': self.get_summary(),
            'test_cases': self.test_case_manager.get_all_test_cases(),
            'link_results': self.current_results,
            'performance_results': self.performance_results,
            'accessibility_results': self.accessibility_results,
            'seo_results': self.seo_results,
            'button_results': self.button_test_results,
            'spelling_results': self.spelling_results,
            'font_results': self.font_results,
            'responsiveness_results': self.responsiveness_results,
            'browser_compatibility_results': self.browser_compatibility_results,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.report_generator.generate_report(all_data, format)

# Initialize website tester
tester = WebsiteTester()

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/extract-links', methods=['POST'])
def extract_links():
    """Extract links from website"""
    data = request.json
    website_url = data.get('website_url', '').strip()
    max_links = int(data.get('max_links', 500))
    
    if not website_url:
        return jsonify({'success': False, 'message': 'Please enter a website URL'})
    
    success, message = tester.extract_links(website_url, max_links)
    
    if success:
        # Store in session
        session['extracted_links'] = tester.extracted_links
        return jsonify({
            'success': True,
            'message': message,
            'links': tester.extracted_links[:20],  # Return first 20 for preview
            'total_links': len(tester.extracted_links)
        })
    else:
        return jsonify({'success': False, 'message': message})

@app.route('/run-tests', methods=['POST'])
def run_tests():
    """Run selected tests"""
    data = request.json
    urls = data.get('urls', [])
    test_options = data.get('test_options', {})
    
    if not urls:
        # Use URLs from session if available
        urls = session.get('extracted_links', [])
    
    if not urls:
        return jsonify({'success': False, 'message': 'No URLs to test'})
    
    # Run tests
    success, message = tester.run_tests(urls, test_options)
    
    if success:
        summary = tester.get_summary()
        return jsonify({
            'success': True,
            'message': message,
            'summary': summary,
            'test_cases': tester.test_case_manager.get_all_test_cases()[:50]  # First 50 for display
        })
    else:
        return jsonify({'success': False, 'message': message})

@app.route('/export-report', methods=['POST'])
def export_report():
    """Export test report"""
    data = request.json
    format_type = data.get('format', 'json')
    
    try:
        # Collect all data from tester
        all_data = {
            'summary': tester.get_summary(),
            'test_cases': tester.test_case_manager.get_all_test_cases(),
            'link_results': tester.current_results,
            'performance_results': tester.performance_results,
            'accessibility_results': tester.accessibility_results,
            'seo_results': tester.seo_results,
            'button_results': tester.button_test_results,
            'spelling_results': tester.spelling_results,
            'font_results': tester.font_results,
            'responsiveness_results': tester.responsiveness_results,
            'browser_compatibility_results': tester.browser_compatibility_results,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if format_type == 'json':
            report_data = tester.report_generator.generate_report(all_data, 'json')
            return jsonify(json.loads(report_data))
        elif format_type == 'csv':
            report_data = tester.report_generator.generate_report(all_data, 'csv')
            return report_data, 200, {'Content-Type': 'text/csv', 
                                     'Content-Disposition': 'attachment; filename="report.csv"'}
        elif format_type == 'html':
            report_data = tester.report_generator.generate_report(all_data, 'html')
            return report_data, 200, {'Content-Type': 'text/html'}
        elif format_type == 'excel':
            report_data = tester.report_generator.generate_report(all_data, 'detailed_excel')
            return report_data, 200, {
                'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'Content-Disposition': 'attachment; filename="website_test_report.xlsx"'
            }
        else:
            return jsonify({'success': False, 'message': f'Unsupported format: {format_type}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Export failed: {str(e)}'})

@app.route('/get-test-cases')
def get_test_cases():
    """Get all test cases"""
    test_cases = tester.test_case_manager.get_all_test_cases()
    return jsonify({'test_cases': test_cases})

@app.route('/clear-all', methods=['POST'])
def clear_all():
    """Clear all test data"""
    tester.clear_all()
    session.clear()
    return jsonify({'success': True, 'message': 'All data cleared'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

