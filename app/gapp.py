import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from urllib.parse import urlparse, urljoin, urldefrag, parse_qs
from datetime import datetime
import csv
import json
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
from openpyxl import Workbook
import os
import textblob  # For spell checking
from textblob import TextBlob
import cssutils  # For CSS parsing
import subprocess
import webbrowser
from collections import Counter
import math
from html import escape
import io
import psutil
import sys
import warnings
warnings.filterwarnings('ignore')

# Install required packages if not available
required_packages = [
    ('textblob', 'textblob'),
    ('cssutils', 'cssutils'),
    ('pandas', 'pandas'),
    ('openpyxl', 'openpyxl'),
    ('psutil', 'psutil'),
    ('lighthouse', 'lighthouse-audit'),
    ('axe-core', 'axe-selenium-python'),
    ('speedtest-cli', 'speedtest-cli')
]

for package_name, install_name in required_packages:
    try:
        __import__(package_name)
    except ImportError:
        print(f"Installing {package_name}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', install_name])

# ============================================================================
# TEST CASE DATA STRUCTURE AND CONSTANTS
# ============================================================================

# Test Case Columns as per requirements
TEST_CASE_COLUMNS = [
    'Test ID',                      # Unique identifier for test case
    'Module',                       # Module/Root URL's next page
    'Test Links/Data',              # URL or data being tested
    'Test Case Description',        # Detailed description of test case
    'Pre-Conditions',               # Pre-requisites for test
    'Test Steps',                   # Step-by-step test procedure
    'Expected Result',              # Expected outcome
    'Actual Result',                # Actual outcome after test
    'Status',                       # Pass/Fail/Blocked/Not Run
    'Severity',                     # Critical/High/Medium/Low
    'Case Pass/Fail',               # Final verdict
    'Comments/Bug ID',              # Bug reference or comments
    'Resolutions'                   # Resolution steps if failed
]

# Test severity levels
SEVERITY_LEVELS = ['Critical', 'High', 'Medium', 'Low', 'Info']

# Test status options
TEST_STATUS = ['Pass', 'Fail', 'Blocked', 'Not Run', 'In Progress']

# Performance Metrics Thresholds
PERFORMANCE_THRESHOLDS = {
    'load_time': 3000,  # 3 seconds in milliseconds
    'page_size': 500,   # 500KB
    'requests': 50,     # 50 requests
    'dom_elements': 1500,  # DOM elements
    'tti': 3500,        # Time to Interactive in ms
    'fcp': 2000,        # First Contentful Paint in ms
}

# Accessibility Standards
ACCESSIBILITY_STANDARDS = {
    'WCAG2A': 'WCAG 2.0 Level A',
    'WCAG2AA': 'WCAG 2.0 Level AA',
    'WCAG2AAA': 'WCAG 2.0 Level AAA',
    'SECTION508': 'Section 508'
}

# ============================================================================
# WEBSITE LINK CHECKER CLASS
# ============================================================================

class WebsiteLinkChecker:
    

    
   
    
    def __init__(self, root, url=None):
        """
        Initialize the Website Comprehensive Tester application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.url = url
        self._status_result = None 
        self.root.title("Website Comprehensive Tester")
        self.root.geometry("1400x1000")
        self.root.resizable(True, True)
        
        # Initialize data storage
        self.current_results = []           # Link check results
        self.extracted_links = []           # Links extracted from website
        self.button_test_results = []       # Button test results
        self.spelling_results = []          # Spelling check results
        self.font_results = []              # Font analysis results
        self.responsiveness_results = []    # Responsiveness check results
        self.browser_compatibility_results = []  # Browser compatibility results
        self.seo_results = []               # SEO analysis results
        self.performance_results = []       # Performance analysis results (NEW)
        self.accessibility_results = []     # Accessibility test results (NEW)
        self.test_cases = []                # Detailed test cases
        
        # Initialize test case counter
        self.test_case_counter = 1
        
        self.setup_ui()

    def check_status(self, url):
        """Check HTTP status of a URL and create test case."""
        # Copy your original check_status logic here directly
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
                'final_url': response.url if hasattr(response, 'url') else url
            }
            
            # Create test case
            test_case = self.create_test_case(
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
                comments=f"Final URL: {response.url}" if hasattr(response, 'url') else "",
                resolutions="Check URL correctness, server configuration, or network connectivity" if test_status == "Fail" else ""
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
                'final_url': url
            }
            
            # Create test case for error
            test_case = self.create_test_case(
                test_type="Link Status Check",
                module="URL Validation",
                test_data=url,
                description=f"Check HTTP status code for URL: {url}",
                pre_conditions="1. Network connectivity\n2. URL is accessible",
                test_steps=f"1. Send GET request to {url}\n2. Wait for response\n3. Check status code",
                expected_result=f"HTTP status code should be 200 OK",
                actual_result=f"Request failed with error: {error_msg}",
                status="Fail",
                severity="Critical",
                comments="Connection error or timeout",
                resolutions="1. Check network connectivity\n2. Verify URL is correct\n3. Check if server is reachable"
            )
            
            return result_display, result_structured, test_case    
    
    # ============================================================================
    # UI SETUP
    # ============================================================================


    
    def setup_ui(self):
        """Setup the user interface with all widgets and frames."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create a canvas with scrollbar for the entire interface
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Option selection
        ttk.Label(scrollable_frame, text="Select Input Method:", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        option_frame = ttk.Frame(scrollable_frame)
        option_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        self.option_var = tk.StringVar(value="manual")
        
        ttk.Radiobutton(option_frame, text="📝 Manual Input (Paste URLs)", 
                       variable=self.option_var, value="manual", 
                       command=self.toggle_input_method).pack(side=tk.LEFT, padx=(0, 20))
        ttk.Radiobutton(option_frame, text="🔍 Extract from Website", 
                       variable=self.option_var, value="extract", 
                       command=self.toggle_input_method).pack(side=tk.LEFT)
        
        # Manual Input Frame
        self.manual_frame = ttk.LabelFrame(scrollable_frame, text="Manual URL Input", padding="10")
        self.manual_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.manual_frame, text="Enter URLs (one per line):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.urls_text = scrolledtext.ScrolledText(self.manual_frame, height=8, width=90)
        self.urls_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(self.manual_frame, text="📥 Load URLs", 
                  command=self.load_manual_urls).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        # Extract Frame
        self.extract_frame = ttk.LabelFrame(scrollable_frame, text="Extract Links from Website", padding="10")
        self.extract_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(self.extract_frame, text="Website URL:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.website_entry = ttk.Entry(self.extract_frame, width=60)
        self.website_entry.grid(row=0, column=1, padx=5)
        self.website_entry.insert(0, "https://example.com")
        
        extract_btn_frame = ttk.Frame(self.extract_frame)
        extract_btn_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        ttk.Button(extract_btn_frame, text="🔍 Extract Links", 
                  command=self.extract_links).pack(side=tk.LEFT, padx=(0,10))
        ttk.Button(extract_btn_frame, text="🧹 Clear", 
                  command=self.clear_all).pack(side=tk.LEFT)
        
        # Max links label for extract mode
        ttk.Label(self.extract_frame, text="Max Links to Extract:").grid(row=2, column=0, sticky=tk.W, pady=(10,5))
        self.max_links_var = tk.StringVar(value="500")
        max_spin = ttk.Spinbox(self.extract_frame, from_=10, to=5000, 
                              textvariable=self.max_links_var, width=10)
        max_spin.grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Testing Options Frame
        options_frame = ttk.LabelFrame(scrollable_frame, text="Testing Options", padding="10")
        options_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Create checkboxes for different tests - Two columns layout
        test_options = [
            # Column 1
            ("🔗 Link Status Checking", "link_check_var", True),
            ("✍️ Spelling & Grammar Check", "spell_check_var", False),
            ("📱 Responsiveness Check", "responsive_check_var", False),
            ("🏎️ Performance Analysis", "performance_check_var", False),  # NEW
            ("📊 Advanced Report Generation", "report_check_var", False),  # NEW
            
            # Column 2
            ("🔘 Button Functionality Testing", "button_test_var", True),
            ("🔤 Font Analysis", "font_check_var", False),
            ("🌐 Cross-Browser Compatibility", "browser_check_var", False),
            ("🔍 SEO Analysis", "seo_check_var", False),
            ("♿ Accessibility Testing", "accessibility_check_var", False),  # NEW
        ]
        
        # Create checkboxes in grid layout
        for i, (text, var_name, default_value) in enumerate(test_options):
            row = i % 5
            column = 0 if i < 5 else 1
            
            var = tk.BooleanVar(value=default_value)
            setattr(self, var_name, var)
            
            cb = ttk.Checkbutton(options_frame, text=text, variable=var)
            cb.grid(row=row, column=column, sticky=tk.W, padx=10, pady=2)
        
        # Links preview (shared by both modes)
        ttk.Label(scrollable_frame, text="Links to Test Preview:").grid(row=5, column=0, sticky=tk.W, pady=(20,5))
        self.links_preview = scrolledtext.ScrolledText(scrollable_frame, height=6, width=90, state=tk.DISABLED)
        self.links_preview.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Check button frame
        check_frame = ttk.Frame(scrollable_frame)
        check_frame.grid(row=7, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        self.check_btn = ttk.Button(check_frame, text="🚀 Run Selected Tests", 
                                   command=self.run_selected_tests, state=tk.DISABLED)
        self.check_btn.pack(side=tk.LEFT, padx=(0,10))
        
        self.export_btn = ttk.Button(check_frame, text="📤 Export Report", 
                                    command=self.export_report, state=tk.DISABLED)
        self.export_btn.pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(scrollable_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Stats frame
        self.stats_label = ttk.Label(scrollable_frame, text="")
        self.stats_label.grid(row=9, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Create Notebook for tabs
        self.notebook = ttk.Notebook(scrollable_frame)
        self.notebook.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20,5))
        
        # Tab 1: Link Status Results
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="🔗 Link Status")
        self.results_text = scrolledtext.ScrolledText(self.results_frame, height=12, width=90, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 2: Button Test Results
        self.buttons_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.buttons_frame, text="🔘 Button Tests")
        self.buttons_text = scrolledtext.ScrolledText(self.buttons_frame, height=12, width=90, state=tk.DISABLED)
        self.buttons_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 3: Spelling Check Results
        self.spelling_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.spelling_frame, text="✍️ Spelling")
        self.spelling_text = scrolledtext.ScrolledText(self.spelling_frame, height=12, width=90, state=tk.DISABLED)
        self.spelling_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 4: Font Analysis Results
        self.fonts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.fonts_frame, text="🔤 Fonts")
        self.fonts_text = scrolledtext.ScrolledText(self.fonts_frame, height=12, width=90, state=tk.DISABLED)
        self.fonts_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 5: Responsiveness Results
        self.responsive_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.responsive_frame, text="📱 Responsive")
        self.responsive_text = scrolledtext.ScrolledText(self.responsive_frame, height=12, width=90, state=tk.DISABLED)
        self.responsive_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 6: Browser Compatibility Results
        self.browser_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.browser_frame, text="🌐 Browser")
        self.browser_text = scrolledtext.ScrolledText(self.browser_frame, height=12, width=90, state=tk.DISABLED)
        self.browser_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 7: SEO Analysis Results
        self.seo_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.seo_frame, text="🔍 SEO Analysis")
        self.seo_text = scrolledtext.ScrolledText(self.seo_frame, height=12, width=90, state=tk.DISABLED)
        self.seo_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 8: Performance Analysis Results (NEW)
        self.performance_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.performance_frame, text="🏎️ Performance")
        self.performance_text = scrolledtext.ScrolledText(self.performance_frame, height=12, width=90, state=tk.DISABLED)
        self.performance_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 9: Accessibility Testing Results (NEW)
        self.accessibility_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.accessibility_frame, text="♿ Accessibility")
        self.accessibility_text = scrolledtext.ScrolledText(self.accessibility_frame, height=12, width=90, state=tk.DISABLED)
        self.accessibility_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 10: Test Cases
        self.testcases_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.testcases_frame, text="📋 Test Cases")
        
        # Create a frame with scrollbar for test cases
        testcases_canvas = tk.Canvas(self.testcases_frame)
        testcases_scrollbar = ttk.Scrollbar(self.testcases_frame, orient="vertical", command=testcases_canvas.yview)
        self.testcases_content = ttk.Frame(testcases_canvas)
        
        self.testcases_content.bind(
            "<Configure>",
            lambda e: testcases_canvas.configure(scrollregion=testcases_canvas.bbox("all"))
        )
        
        testcases_canvas.create_window((0, 0), window=self.testcases_content, anchor="nw")
        testcases_canvas.configure(yscrollcommand=testcases_scrollbar.set)
        
        # Treeview for displaying test cases
        self.testcases_tree = ttk.Treeview(self.testcases_content, columns=TEST_CASE_COLUMNS, 
                                          show='headings', height=15)
        
        # Define column headings
        for col in TEST_CASE_COLUMNS:
            self.testcases_tree.heading(col, text=col)
            self.testcases_tree.column(col, width=100, minwidth=50)
        
        # Adjust column widths
        column_widths = {
            'Test ID': 70,
            'Module': 150,
            'Test Links/Data': 200,
            'Test Case Description': 250,
            'Pre-Conditions': 150,
            'Test Steps': 250,
            'Expected Result': 200,
            'Actual Result': 200,
            'Status': 100,
            'Severity': 100,
            'Case Pass/Fail': 100,
            'Comments/Bug ID': 150,
            'Resolutions': 200
        }
        
        for col, width in column_widths.items():
            self.testcases_tree.column(col, width=width)
        
        # Add scrollbar to treeview
        tree_scrollbar = ttk.Scrollbar(self.testcases_content, orient="vertical", command=self.testcases_tree.yview)
        self.testcases_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Pack treeview and scrollbar
        self.testcases_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure grid weights for test cases frame
        testcases_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        testcases_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.testcases_content.columnconfigure(0, weight=1)
        self.testcases_content.rowconfigure(0, weight=1)
        self.testcases_frame.columnconfigure(0, weight=1)
        self.testcases_frame.rowconfigure(0, weight=1)
        
        # Configure grid weights for main window
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
        scrollable_frame.columnconfigure(1, weight=1)
        
        # Initialize with manual input visible
        self.toggle_input_method()
    
    # ============================================================================
    # UI HELPER FUNCTIONS
    # ============================================================================
    
    def toggle_input_method(self):
        """Show/hide the appropriate input method frames based on selection."""
        if self.option_var.get() == "manual":
            self.manual_frame.grid()
            self.extract_frame.grid_remove()
        else:
            self.manual_frame.grid_remove()
            self.extract_frame.grid()
    
    def load_manual_urls(self):
        """Load URLs from manual input text area with duplicate checking."""
        urls_text = self.urls_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showwarning("Warning", "Please enter URLs in the text area")
            return
        
        # Parse URLs - one per line, filter empty lines
        raw_urls = urls_text.split('\n')
        unique_urls = []
        duplicate_count = 0
        
        for url in raw_urls:
            url = url.strip()
            if url:
                # Add http:// if no protocol specified
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                
                # Check for duplicates
                if not self.is_duplicate_url(url, unique_urls):
                    unique_urls.append(url)
                else:
                    duplicate_count += 1
        
        self.extracted_links = unique_urls
        
        if not self.extracted_links:
            messagebox.showwarning("Warning", "No valid URLs found")
            return
        
        self.update_links_preview()
        self.check_btn.config(state=tk.NORMAL)
        
        message_text = f"Loaded {len(self.extracted_links)} unique URLs"
        if duplicate_count > 0:
            message_text += f" (skipped {duplicate_count} duplicate URLs)"
        
        messagebox.showinfo("Success", message_text)
        
    def extract_links(self):
        """Extract links from a website URL with duplicate checking."""
        website_url = self.website_entry.get().strip()
        if not website_url:
            messagebox.showwarning("Warning", "Please enter a website URL")
            return
        
        self.progress.start()
        self.check_btn.config(state=tk.DISABLED)
        
        def extract_worker():
            try:
                self.extracted_links = self.scrape_all_links(website_url)
                
                self.root.after(0, lambda: self.update_links_preview())
                self.root.after(0, lambda: self.progress.stop())
                self.root.after(0, lambda: self.check_btn.config(state=tk.NORMAL if self.extracted_links else tk.DISABLED))
                
                if not self.extracted_links:
                    self.root.after(0, lambda: messagebox.showwarning("Warning", "No links extracted from the website"))
                else:
                    # Remove duplicates from final list
                    initial_count = len(self.extracted_links)
                    self.extracted_links = self.remove_duplicate_urls(self.extracted_links)
                    final_count = len(self.extracted_links)
                    duplicates_removed = initial_count - final_count
                    
                    message_text = f"Extracted {final_count} unique links from {website_url}"
                    if duplicates_removed > 0:
                        message_text += f" (removed {duplicates_removed} duplicates)"
                    
                    self.root.after(0, lambda: messagebox.showinfo("Success", message_text))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to extract links: {str(e)}"))
                self.root.after(0, lambda: self.progress.stop())
        
        threading.Thread(target=extract_worker, daemon=True).start()
        
    def scrape_all_links(self, base_url, max_depth=2, max_links=1000):
        """Recursively scrape links from website with duplicate checking."""
        visited = set()
        to_visit = [(base_url, 0)]
        all_links = set()
        duplicate_count = 0
        
        while to_visit and len(all_links) < max_links:
            url, depth = to_visit.pop(0)
            
            if url in visited or depth > max_depth:
                continue
                
            visited.add(url)
            
            try:
                parsed = urlparse(url)
                response = requests.get(url, timeout=10, verify=False)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract all links
                for link in soup.find_all(['a', 'link', 'script', 'img'], href=True):
                    href = link['href']
                    full_url = urljoin(url, href)
                    full_url = urldefrag(full_url)[0]  # Remove fragments
                    
                    # Filter same domain and common paths
                    if self.is_relevant_link(full_url, base_url):
                        # Check if this is a duplicate before adding
                        is_duplicate = False
                        for existing_link in all_links:
                            if self.get_base_url(full_url) == self.get_base_url(existing_link):
                                is_duplicate = True
                                duplicate_count += 1
                                break
                        
                        if not is_duplicate:
                            all_links.add(full_url)
                
                # Also extract paths from forms, etc.
                for form in soup.find_all('form', action=True):
                    action = form['action']
                    full_url = urljoin(url, action)
                    if self.is_relevant_link(full_url, base_url):
                        # Check for duplicate
                        is_duplicate = False
                        for existing_link in all_links:
                            if self.get_base_url(full_url) == self.get_base_url(existing_link):
                                is_duplicate = True
                                duplicate_count += 1
                                break
                        
                        if not is_duplicate:
                            all_links.add(full_url)
                
                time.sleep(0.5)  # Be respectful
                
            except:
                continue
        
        # Convert to list and limit
        max_links_int = int(self.max_links_var.get())
        links_list = list(all_links)[:max_links_int]
        
        # Remove any remaining duplicates from the final list
        links_list = self.remove_duplicate_urls(links_list)
        
        # Log duplicates if any
        if duplicate_count > 0:
            print(f"Found and skipped {duplicate_count} duplicate links during scraping")
        
        return links_list
    
    def is_relevant_link(self, link, base_url):
        """Filter relevant links for same domain."""
        base_domain = urlparse(base_url).netloc
        link_domain = urlparse(link).netloc
        
        # Same domain or subdomain
        if base_domain == link_domain or link_domain.endswith('.' + base_domain):
            return True
        
        # Common paths/files (even cross-domain if useful)
        path = urlparse(link).path.lower()
        useful_extensions = ['.php', '.asp', '.aspx', '.jsp', '.html', '.htm']
        if any(path.endswith(ext) for ext in useful_extensions) or not path.endswith('/'):
            return True
        
        return False
    
    def update_links_preview(self):
        """Update the links preview text area with duplicate information."""
        self.links_preview.config(state=tk.NORMAL)
        self.links_preview.delete(1.0, tk.END)
        
        if not self.extracted_links:
            self.links_preview.insert(tk.END, "No links loaded.\n")
        else:
            # Check for duplicates in the final list
            unique_count = len(self.extracted_links)
            duplicates_info = ""
            
            # Quick duplicate check
            seen = set()
            duplicates = []
            for url in self.extracted_links:
                base = self.get_base_url(url)
                if base in seen:
                    duplicates.append(url)
                else:
                    seen.add(base)
            
            if duplicates:
                unique_count = len(seen)
                duplicates_info = f" (⚠️ {len(duplicates)} duplicates detected)"
            
            self.links_preview.insert(tk.END, f"Total unique links: {unique_count}{duplicates_info}\n")
            self.links_preview.insert(tk.END, "="*60 + "\n")
            
            preview_count = min(20, len(self.extracted_links))
            for i, link in enumerate(self.extracted_links[:preview_count]):
                # Check if this is a duplicate
                is_duplicate = i >= len(seen)
                duplicate_marker = " ⚠️ DUPLICATE" if is_duplicate else ""
                self.links_preview.insert(tk.END, f"{i+1:3d}. {link}{duplicate_marker}\n")
            
            if len(self.extracted_links) > preview_count:
                self.links_preview.insert(tk.END, f"\n... and {len(self.extracted_links) - preview_count} more links\n")
        
        self.links_preview.config(state=tk.DISABLED)
        
    # ============================================================================
    # MAIN TEST EXECUTION
    # ============================================================================
    
    def run_selected_tests(self):
        """Run all selected tests based on checkbox selections with duplicate checking."""
        if not self.extracted_links:
            messagebox.showwarning("Warning", "No links to test.")
            return
        
        # Remove duplicates from extracted links before testing
        initial_count = len(self.extracted_links)
        self.extracted_links = self.remove_duplicate_urls(self.extracted_links)
        final_count = len(self.extracted_links)
        
        if initial_count != final_count:
            duplicates_removed = initial_count - final_count
            messagebox.showinfo("Duplicate URLs Removed", 
                              f"Removed {duplicates_removed} duplicate URLs before testing.\n"
                              f"Testing {final_count} unique URLs.")
        
        # Reset all results
        self.current_results = []
        self.button_test_results = []
        self.spelling_results = []
        self.font_results = []
        self.responsiveness_results = []
        self.browser_compatibility_results = []
        self.seo_results = []
        self.performance_results = []  # Reset performance results
        self.accessibility_results = []  # Reset accessibility results
        self.test_cases = []
        self.test_case_counter = 1
        
        # Clear all text areas
        text_widgets = [
            self.results_text, self.buttons_text, self.spelling_text,
            self.fonts_text, self.responsive_text, self.browser_text,
            self.seo_text, self.performance_text, self.accessibility_text  # Added new text areas
        ]
        
        for text_widget in text_widgets:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
        
        # Clear test cases tree
        for item in self.testcases_tree.get_children():
            self.testcases_tree.delete(item)
        
        self.progress.start()
        self.check_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        
        def run_all_tests():
            try:
                # Test 1: Link Status Check
                if self.link_check_var.get():
                    self.root.after(0, self.update_results, "🔗 Starting Link Status Check...\n")
                    self.test_links()
                
                # Test 2: Button Testing
                if self.button_test_var.get():
                    self.root.after(0, self.update_buttons_results, "🔘 Starting Button Testing...\n")
                    self.test_buttons()
                
                # Test 3: Spelling Check
                if self.spell_check_var.get():
                    self.root.after(0, self.update_spelling_results, "✍️ Starting Spelling Check...\n")
                    self.test_spelling()
                
                # Test 4: Font Analysis
                if self.font_check_var.get():
                    self.root.after(0, self.update_font_results, "🔤 Starting Font Analysis...\n")
                    self.test_fonts()
                
                # Test 5: Responsiveness Check
                if self.responsive_check_var.get():
                    self.root.after(0, self.update_responsive_results, "📱 Starting Responsiveness Check...\n")
                    self.test_responsiveness()
                
                # Test 6: Browser Compatibility
                if self.browser_check_var.get():
                    self.root.after(0, self.update_browser_results, "🌐 Starting Browser Compatibility Check...\n")
                    self.test_browser_compatibility()
                
                # Test 7: SEO Analysis
                if self.seo_check_var.get():
                    self.root.after(0, self.update_seo_results, "🔍 Starting SEO Analysis...\n")
                    self.test_seo()
                
                # Test 8: Performance Analysis (NEW)
                if self.performance_check_var.get():
                    self.root.after(0, self.update_performance_results, "🏎️ Starting Performance Analysis...\n")
                    self.test_performance()
                
                # Test 9: Accessibility Testing (NEW)
                if self.accessibility_check_var.get():
                    self.root.after(0, self.update_accessibility_results, "♿ Starting Accessibility Testing...\n")
                    self.test_accessibility()
                
                # Update test cases display
                self.root.after(0, self.update_test_cases_display)
                self.root.after(0, self.all_tests_complete)
                
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Test failed: {str(e)}"))
                self.root.after(0, self.progress.stop)
                self.root.after(0, lambda: self.check_btn.config(state=tk.NORMAL))
        
        threading.Thread(target=run_all_tests, daemon=True).start()
        
    # ============================================================================
    # TEST EXECUTION METHODS
    # ============================================================================
    
    def test_links(self):
        """Test all extracted links for status, skipping duplicates."""
        # Track tested URLs to avoid testing duplicates
        tested_urls = set()
        urls_to_test = []
        
        # Filter out duplicates
        for url in self.extracted_links:
            base_url = self.get_base_url(url)
            if base_url not in tested_urls:
                tested_urls.add(base_url)
                urls_to_test.append(url)
        
        if len(urls_to_test) < len(self.extracted_links):
            duplicates_skipped = len(self.extracted_links) - len(urls_to_test)
            self.root.after(0, self.update_results, f"⚠️ Skipping {duplicates_skipped} duplicate URLs for testing\n")
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_url = {executor.submit(self.check_status, url): url for url in urls_to_test}
            
            for future in as_completed(future_to_url):
                result_display, result_structured, test_case = future.result()
                self.current_results.append(result_structured)
                if test_case:
                    self.test_cases.append(test_case)
                self.root.after(0, self.update_results, result_display)

    def remove_duplicates(self):
        """Manually remove duplicate URLs from the current list."""
        if not self.extracted_links:
            messagebox.showinfo("No URLs", "No URLs loaded to remove duplicates from.")
            return
        
        initial_count = len(self.extracted_links)
        self.extracted_links = self.remove_duplicate_urls(self.extracted_links)
        final_count = len(self.extracted_links)
        
        duplicates_removed = initial_count - final_count
        
        if duplicates_removed > 0:
            self.update_links_preview()
            messagebox.showinfo("Duplicates Removed", 
                              f"Removed {duplicates_removed} duplicate URLs.\n"
                              f"Now have {final_count} unique URLs.")
        else:
            messagebox.showinfo("No Duplicates", "No duplicate URLs found.")   
                
    def test_buttons(self):
        """Test buttons on successful pages."""
        if not self.current_results:
            return
        
        working_urls = [r['url'] for r in self.current_results 
                       if r['status_category'] == 'Success' and r['status_code'] == 200]
        
        if not working_urls:
            self.root.after(0, self.update_buttons_results, "No working pages found for button testing.\n")
            return
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_url = {executor.submit(self.test_buttons_on_page, url): url for url in working_urls}
            
            for future in as_completed(future_to_url):
                button_results = future.result()
                if button_results:
                    self.button_test_results.extend(button_results)
                    for result in button_results:
                        self.test_cases.append(result['test_case'])
                        self.root.after(0, self.update_buttons_results, result['display_text'])

    def test_buttons_on_page(self, url):
        """Test buttons on a specific page."""
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            buttons = soup.find_all(['button', 'input', 'a'], 
                                attrs={'type': ['button', 'submit']})
            
            button_results = []
            for button in buttons[:10]:  # Limit to 10 buttons per page
                button_text = button.get_text(strip=True) or button.get('value', '') or button.get('aria-label', '')
                button_type = button.name if button.name != 'input' else f"input[{button.get('type', 'button')}]"
                
                # Create a test case for each button
                test_case = self.create_test_case(
                    test_type="Button Functionality",
                    module="Button Testing",
                    test_data=f"{url} - {button_text[:50]}",
                    description=f"Test button functionality: {button_text[:100]}",
                    pre_conditions="1. Page loads successfully\n2. Button is visible",
                    test_steps=f"1. Navigate to {url}\n2. Locate button: {button_text[:50]}\n3. Click the button",
                    expected_result="Button should perform its intended action",
                    actual_result=f"Button found: {button_type} with text: {button_text[:100]}",
                    status="Not Run",  # Manual testing needed
                    severity="Medium",
                    comments="Manual testing required for button functionality",
                    resolutions="Test button manually to verify functionality"
                )
                
                button_results.append({
                    'url': url,
                    'button_text': button_text,
                    'button_type': button_type,
                    'display_text': f"🔘 Found button: {button_text[:50]} on {url}",
                    'test_case': test_case
                })
            
            return button_results
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Button Functionality",
                module="Button Testing",
                test_data=url,
                description=f"Test button functionality on {url}",
                pre_conditions="Page loads successfully",
                test_steps=f"1. Navigate to {url}\n2. Find buttons\n3. Test functionality",
                expected_result="Buttons should be functional",
                actual_result=f"Error testing buttons: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            )
            
            return [{
                'url': url,
                'button_text': '',
                'button_type': '',
                'display_text': f"❌ Error testing buttons on {url}: {str(e)[:100]}",
                'test_case': error_test_case
            }]
    
    def test_spelling(self):
        """Check spelling on working pages."""
        if not self.current_results:
            return
        
        working_urls = [r['url'] for r in self.current_results 
                       if r['status_category'] == 'Success' and r['status_code'] == 200]
        
        if not working_urls:
            self.root.after(0, self.update_spelling_results, "No working pages found for spelling check.\n")
            return
        
        for url in working_urls:
            try:
                spelling_test_cases = self.check_spelling_on_page(url)
                if spelling_test_cases:
                    self.spelling_results.extend(spelling_test_cases)
                    for test_case in spelling_test_cases:
                        self.test_cases.append(test_case)
                        self.root.after(0, self.update_spelling_results, 
                                       f"📝 {url}\nIssue: {test_case['Actual Result'][:100]}...\n")
            except Exception as e:
                error_test_case = self.create_test_case(
                    test_type="Spelling Check",
                    module="Spelling Analysis",
                    test_data=url,
                    description="Check for spelling and grammar errors on webpage",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Extract text content\n3. Analyze spelling",
                    expected_result="No spelling errors found",
                    actual_result=f"Error checking spelling: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium"
                )
                self.test_cases.append(error_test_case)
                self.root.after(0, self.update_spelling_results, 
                               f"❌ Error checking spelling on {url}: {str(e)[:100]}\n")
    
    def test_fonts(self):
        """Analyze fonts on working pages."""
        if not self.current_results:
            return
        
        working_urls = [r['url'] for r in self.current_results 
                       if r['status_category'] == 'Success' and r['status_code'] == 200]
        
        if not working_urls:
            self.root.after(0, self.update_font_results, "No working pages found for font analysis.\n")
            return
        
        for url in working_urls[:3]:  # Limit to 3 pages to avoid overwhelming
            try:
                font_test_cases = self.analyze_fonts_on_page(url)
                if font_test_cases:
                    self.font_results.extend(font_test_cases)
                    for test_case in font_test_cases:
                        self.test_cases.append(test_case)
                        # Display each line of analysis
                        self.root.after(0, self.update_font_results, 
                                       f"🔤 {test_case['Module']}: {test_case['Actual Result'][:100]}...\n")
            except Exception as e:
                error_test_case = self.create_test_case(
                    test_type="Font Analysis",
                    module="Font Analysis",
                    test_data=url,
                    description="Analyze fonts used on webpage",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Extract font declarations\n3. Analyze font usage",
                    expected_result="Font analysis completed successfully",
                    actual_result=f"Error analyzing fonts: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium"
                )
                self.test_cases.append(error_test_case)
                self.root.after(0, self.update_font_results, 
                               f"❌ Error analyzing fonts on {url}: {str(e)[:100]}\n")
    
    def test_responsiveness(self):
        """Check responsiveness of working pages."""
        if not self.current_results:
            return
        
        working_urls = [r['url'] for r in self.current_results 
                       if r['status_category'] == 'Success' and r['status_code'] == 200]
        
        if not working_urls:
            self.root.after(0, self.update_responsive_results, "No working pages found for responsiveness check.\n")
            return
        
        for url in working_urls[:3]:  # Limit to 3 pages
            try:
                responsive_test_cases = self.check_responsiveness(url)
                if responsive_test_cases:
                    self.responsiveness_results.extend(responsive_test_cases)
                    for test_case in responsive_test_cases:
                        self.test_cases.append(test_case)
                        # Display each line of analysis
                        self.root.after(0, self.update_responsive_results, 
                                       f"📱 {test_case['Module']}: {test_case['Actual Result'][:100]}...\n")
            except Exception as e:
                error_test_case = self.create_test_case(
                    test_type="Responsiveness Check",
                    module="Responsiveness Analysis",
                    test_data=url,
                    description="Check webpage responsiveness",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Check viewport meta tag\n3. Analyze responsive elements",
                    expected_result="Page is responsive across devices",
                    actual_result=f"Error checking responsiveness: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium"
                )
                self.test_cases.append(error_test_case)
                self.root.after(0, self.update_responsive_results, 
                               f"❌ Error checking responsiveness on {url}: {str(e)[:100]}\n")
    
    def test_browser_compatibility(self):
        """Check cross-browser compatibility."""
        if not self.current_results:
            return
        
        working_urls = [r['url'] for r in self.current_results 
                       if r['status_category'] == 'Success' and r['status_code'] == 200]
        
        if not working_urls:
            self.root.after(0, self.update_browser_results, "No working pages found for browser compatibility check.\n")
            return
        
        for url in working_urls[:3]:  # Limit to 3 pages
            try:
                browser_test_cases = self.check_browser_compatibility(url)
                if browser_test_cases:
                    self.browser_compatibility_results.extend(browser_test_cases)
                    for test_case in browser_test_cases:
                        self.test_cases.append(test_case)
                        # Display each line of analysis
                        self.root.after(0, self.update_browser_results, 
                                       f"🌐 {test_case['Module']}: {test_case['Actual Result'][:100]}...\n")
            except Exception as e:
                error_test_case = self.create_test_case(
                    test_type="Browser Compatibility",
                    module="Browser Compatibility Analysis",
                    test_data=url,
                    description="Check cross-browser compatibility",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Check HTML5 compliance\n3. Analyze browser-specific code",
                    expected_result="Page is compatible with major browsers",
                    actual_result=f"Error checking browser compatibility: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium"
                )
                self.test_cases.append(error_test_case)
                self.root.after(0, self.update_browser_results, 
                               f"❌ Error checking browser compatibility on {url}: {str(e)[:100]}\n")
    
    def test_seo(self):
        """Perform SEO analysis on working pages."""
        if not self.current_results:
            return
        
        working_urls = [r['url'] for r in self.current_results 
                       if r['status_category'] == 'Success' and r['status_code'] == 200]
        
        if not working_urls:
            self.root.after(0, self.update_seo_results, "No working pages found for SEO analysis.\n")
            return
        
        for url in working_urls[:3]:  # Limit to 3 pages for SEO analysis
            try:
                seo_test_cases = self.perform_seo_analysis(url)
                if seo_test_cases:
                    self.seo_results.extend(seo_test_cases)
                    for test_case in seo_test_cases:
                        self.test_cases.append(test_case)
                        # Display each line of analysis
                        self.root.after(0, self.update_seo_results, 
                                       f"🔍 {test_case['Module']}: {test_case['Actual Result'][:100]}...\n")
            except Exception as e:
                error_test_case = self.create_test_case(
                    test_type="SEO Analysis",
                    module="SEO Analysis",
                    test_data=url,
                    description="Perform SEO analysis on webpage",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Extract meta tags\n3. Analyze SEO elements",
                    expected_result="SEO analysis completed successfully",
                    actual_result=f"Error during SEO analysis: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium"
                )
                self.test_cases.append(error_test_case)
                self.root.after(0, self.update_seo_results, 
                               f"❌ Error performing SEO analysis on {url}: {str(e)[:100]}\n")
    
    # ============================================================================
    # PERFORMANCE ANALYSIS METHODS (NEW)
    # ============================================================================
    
    def test_performance(self):
        """Perform comprehensive performance analysis on working pages."""
        if not self.current_results:
            return
        
        working_urls = [r['url'] for r in self.current_results 
                       if r['status_category'] == 'Success' and r['status_code'] == 200]
        
        if not working_urls:
            self.root.after(0, self.update_performance_results, "No working pages found for performance analysis.\n")
            return
        
        for url in working_urls[:3]:  # Limit to 3 pages for performance analysis
            try:
                performance_test_cases = self.perform_performance_analysis(url)
                if performance_test_cases:
                    self.performance_results.extend(performance_test_cases)
                    for test_case in performance_test_cases:
                        self.test_cases.append(test_case)
                        # Display each line of analysis
                        self.root.after(0, self.update_performance_results, 
                                       f"🏎️ {test_case['Module']}: {test_case['Actual Result'][:100]}...\n")
            except Exception as e:
                error_test_case = self.create_test_case(
                    test_type="Performance Analysis",
                    module="Performance Analysis",
                    test_data=url,
                    description="Perform performance analysis on webpage",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Measure load times\n3. Analyze performance metrics",
                    expected_result="Performance analysis completed successfully",
                    actual_result=f"Error during performance analysis: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium"
                )
                self.test_cases.append(error_test_case)
                self.root.after(0, self.update_performance_results, 
                               f"❌ Error performing performance analysis on {url}: {str(e)[:100]}\n")
    
    def perform_performance_analysis(self, url):
        """Perform comprehensive performance analysis on a webpage."""
        test_cases = []
        performance_score = 100  # Start with perfect score
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Page Load Time Analysis
            load_time_test_cases = self.analyze_page_load_times(url, response)
            test_cases.extend(load_time_test_cases)
            
            # 2. Resource Analysis
            resource_test_cases = self.analyze_page_resources(soup, url, response)
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
            error_test_case = self.create_test_case(
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
    
    def analyze_page_load_times(self, url, response):
        """Analyze page load times and performance metrics."""
        test_cases = []
        
        try:
            # Calculate total load time
            load_time = response.elapsed.total_seconds() * 1000  # Convert to milliseconds
            page_size_kb = len(response.content) / 1024
            
            # Test 1: Total Load Time
            if load_time <= PERFORMANCE_THRESHOLDS['load_time']:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Page Load Time",
                    test_data=url,
                    description="Measure total page load time",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Send HTTP request\n2. Measure response time\n3. Calculate load time",
                    expected_result=f"Page should load within {PERFORMANCE_THRESHOLDS['load_time']}ms",
                    actual_result=f"Total load time: {load_time:.0f}ms (Good)",
                    status="Pass",
                    severity="High",
                    comments="Page loads quickly",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Page Load Time",
                    test_data=url,
                    description="Measure total page load time",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Send HTTP request\n2. Measure response time\n3. Calculate load time",
                    expected_result=f"Page should load within {PERFORMANCE_THRESHOLDS['load_time']}ms",
                    actual_result=f"Total load time: {load_time:.0f}ms (Slow)",
                    status="Fail",
                    severity="High",
                    comments="Page load time exceeds recommended threshold",
                    resolutions="Optimize server response time, compress resources, use CDN"
                ))
            
            # Test 2: Page Size
            if page_size_kb <= PERFORMANCE_THRESHOLDS['page_size']:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Page Size",
                    test_data=url,
                    description="Calculate total page size",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Get response content\n2. Calculate size\n3. Check against threshold",
                    expected_result=f"Page should be under {PERFORMANCE_THRESHOLDS['page_size']}KB",
                    actual_result=f"Page size: {page_size_kb:.1f}KB (Good)",
                    status="Pass",
                    severity="Medium",
                    comments="Page size is optimal",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Page Size",
                    test_data=url,
                    description="Calculate total page size",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Get response content\n2. Calculate size\n3. Check against threshold",
                    expected_result=f"Page should be under {PERFORMANCE_THRESHOLDS['page_size']}KB",
                    actual_result=f"Page size: {page_size_kb:.1f}KB (Large)",
                    status="Fail",
                    severity="Medium",
                    comments="Large page size affects loading speed",
                    resolutions="Compress images, minify CSS/JS, remove unused code"
                ))
            
            # Test 3: Time to First Byte (TTFB) estimation
            ttfb = load_time * 0.3  # Rough estimation
            
            if ttfb <= 500:  # Good TTFB
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Time to First Byte (TTFB)",
                    test_data=url,
                    description="Estimate Time to First Byte",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Measure initial response time\n2. Calculate TTFB\n3. Check performance",
                    expected_result="TTFB should be under 500ms",
                    actual_result=f"Estimated TTFB: {ttfb:.0f}ms (Good)",
                    status="Pass",
                    severity="Medium",
                    comments="Server responds quickly",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Time to First Byte (TTFB)",
                    test_data=url,
                    description="Estimate Time to First Byte",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Measure initial response time\n2. Calculate TTFB\n3. Check performance",
                    expected_result="TTFB should be under 500ms",
                    actual_result=f"Estimated TTFB: {ttfb:.0f}ms (Slow)",
                    status="Fail",
                    severity="Medium",
                    comments="Server response time is slow",
                    resolutions="Optimize server configuration, use caching, upgrade hosting"
                ))
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Performance Analysis",
                module="Load Time Analysis",
                test_data=url,
                description="Analyze page load times",
                pre_conditions="Page loaded successfully",
                test_steps="1. Measure load time\n2. Calculate page size\n3. Estimate TTFB",
                expected_result="Load time analysis completed successfully",
                actual_result=f"Error analyzing load times: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Load time analysis failed",
                resolutions="Check network connection and server accessibility"
            )
            return [error_test_case]
    
    def analyze_page_resources(self, soup, url, response):
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
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Resource Count",
                    test_data=url,
                    description="Count total page resources",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Parse HTML\n2. Count CSS, JS, and image files\n3. Calculate total",
                    expected_result=f"Total resources should be under {PERFORMANCE_THRESHOLDS['requests']}",
                    actual_result=f"Total resources: {total_resources} (CSS: {css_files}, JS: {js_files}, Images: {images})",
                    status="Pass",
                    severity="Medium",
                    comments="Reasonable number of resources",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Resource Count",
                    test_data=url,
                    description="Count total page resources",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Parse HTML\n2. Count CSS, JS, and image files\n3. Calculate total",
                    expected_result=f"Total resources should be under {PERFORMANCE_THRESHOLDS['requests']}",
                    actual_result=f"Total resources: {total_resources} (Too many)",
                    status="Fail",
                    severity="Medium",
                    comments="Excessive resources slow down page loading",
                    resolutions="Combine CSS/JS files, use image sprites, lazy load images"
                ))
            
            # Test 2: CSS File Count
            if css_files <= 5:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="CSS Files",
                    test_data=url,
                    description="Count CSS files",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Parse HTML\n2. Count CSS link tags\n3. Check count",
                    expected_result="CSS files should be 5 or fewer",
                    actual_result=f"CSS files: {css_files} (Good)",
                    status="Pass",
                    severity="Low",
                    comments="Reasonable number of CSS files",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="CSS Files",
                    test_data=url,
                    description="Count CSS files",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Parse HTML\n2. Count CSS link tags\n3. Check count",
                    expected_result="CSS files should be 5 or fewer",
                    actual_result=f"CSS files: {css_files} (Too many)",
                    status="Fail",
                    severity="Low",
                    comments="Multiple CSS files increase HTTP requests",
                    resolutions="Combine CSS files, minify CSS, use CSS delivery optimization"
                ))
            
            # Test 3: JavaScript File Count
            if js_files <= 10:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="JavaScript Files",
                    test_data=url,
                    description="Count JavaScript files",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Parse HTML\n2. Count script tags with src\n3. Check count",
                    expected_result="JS files should be 10 or fewer",
                    actual_result=f"JavaScript files: {js_files} (Good)",
                    status="Pass",
                    severity="Low",
                    comments="Reasonable number of JS files",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="JavaScript Files",
                    test_data=url,
                    description="Count JavaScript files",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Parse HTML\n2. Count script tags with src\n3. Check count",
                    expected_result="JS files should be 10 or fewer",
                    actual_result=f"JavaScript files: {js_files} (Too many)",
                    status="Fail",
                    severity="Low",
                    comments="Multiple JS files increase HTTP requests and parsing time",
                    resolutions="Combine JS files, minify JavaScript, load non-critical JS asynchronously"
                ))
            
            # Test 4: DOM Complexity
            dom_elements = len(soup.find_all())
            
            if dom_elements <= PERFORMANCE_THRESHOLDS['dom_elements']:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="DOM Complexity",
                    test_data=url,
                    description="Count DOM elements",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Parse HTML\n2. Count all elements\n3. Check complexity",
                    expected_result=f"DOM elements should be under {PERFORMANCE_THRESHOLDS['dom_elements']}",
                    actual_result=f"DOM elements: {dom_elements} (Good)",
                    status="Pass",
                    severity="Low",
                    comments="DOM complexity is reasonable",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="DOM Complexity",
                    test_data=url,
                    description="Count DOM elements",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Parse HTML\n2. Count all elements\n3. Check complexity",
                    expected_result=f"DOM elements should be under {PERFORMANCE_THRESHOLDS['dom_elements']}",
                    actual_result=f"DOM elements: {dom_elements} (Complex)",
                    status="Fail",
                    severity="Low",
                    comments="Complex DOM slows down rendering and JavaScript execution",
                    resolutions="Simplify HTML structure, remove unnecessary elements, use efficient selectors"
                ))
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Performance Analysis",
                module="Resource Analysis",
                test_data=url,
                description="Analyze page resources",
                pre_conditions="Page loaded successfully",
                test_steps="1. Parse HTML\n2. Count resources\n3. Analyze impact",
                expected_result="Resource analysis completed successfully",
                actual_result=f"Error analyzing resources: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Resource analysis failed",
                resolutions=""
            )
            return [error_test_case]
    
    def analyze_network_performance(self, url):
        """Analyze network-related performance factors."""
        test_cases = []
        
        try:
            # Test 1: HTTP/2 Support
            try:
                response = requests.get(url, timeout=5, verify=False)
                http_version = response.raw.version
                
                if http_version == 11:
                    test_cases.append(self.create_test_case(
                        test_type="Performance Analysis",
                        module="HTTP Version",
                        test_data=url,
                        description="Check HTTP version",
                        pre_conditions="Page loaded successfully",
                        test_steps="1. Send HTTP request\n2. Check protocol version\n3. Determine if HTTP/2",
                        expected_result="Server should support HTTP/2 for better performance",
                        actual_result="Using HTTP/1.1",
                        status="Warning",
                        severity="Medium",
                        comments="HTTP/1.1 is slower than HTTP/2 for multiple requests",
                        resolutions="Upgrade to HTTP/2 for multiplexing and header compression"
                    ))
                else:
                    test_cases.append(self.create_test_case(
                        test_type="Performance Analysis",
                        module="HTTP Version",
                        test_data=url,
                        description="Check HTTP version",
                        pre_conditions="Page loaded successfully",
                        test_steps="1. Send HTTP request\n2. Check protocol version\n3. Determine if HTTP/2",
                        expected_result="Server should support HTTP/2 for better performance",
                        actual_result="Using HTTP/2 or higher",
                        status="Pass",
                        severity="Low",
                        comments="HTTP/2 improves performance with multiplexing",
                        resolutions=""
                    ))
            except:
                pass
            
            # Test 2: GZIP Compression Check
            try:
                headers = {'Accept-Encoding': 'gzip, deflate'}
                response = requests.get(url, headers=headers, timeout=5, verify=False)
                
                if 'gzip' in response.headers.get('Content-Encoding', ''):
                    test_cases.append(self.create_test_case(
                        test_type="Performance Analysis",
                        module="GZIP Compression",
                        test_data=url,
                        description="Check if GZIP compression is enabled",
                        pre_conditions="Page loaded successfully",
                        test_steps="1. Send request with Accept-Encoding header\n2. Check response headers\n3. Verify compression",
                        expected_result="Server should use GZIP compression",
                        actual_result="GZIP compression enabled",
                        status="Pass",
                        severity="Medium",
                        comments="Compression reduces file sizes and improves load times",
                        resolutions=""
                    ))
                else:
                    test_cases.append(self.create_test_case(
                        test_type="Performance Analysis",
                        module="GZIP Compression",
                        test_data=url,
                        description="Check if GZIP compression is enabled",
                        pre_conditions="Page loaded successfully",
                        test_steps="1. Send request with Accept-Encoding header\n2. Check response headers\n3. Verify compression",
                        expected_result="Server should use GZIP compression",
                        actual_result="GZIP compression not enabled",
                        status="Fail",
                        severity="Medium",
                        comments="Missing compression increases transfer size",
                        resolutions="Enable GZIP compression on server for text-based resources"
                    ))
            except:
                pass
            
            # Test 3: CDN Usage Check
            parsed_url = urlparse(url)
            cdn_domains = ['cloudflare', 'akamai', 'fastly', 'cloudfront', 'azureedge', 'googleusercontent']
            
            is_cdn = any(cdn in parsed_url.netloc.lower() for cdn in cdn_domains)
            
            if is_cdn:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="CDN Usage",
                    test_data=url,
                    description="Check if CDN is being used",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Analyze domain\n2. Check for CDN patterns\n3. Determine CDN usage",
                    expected_result="CDN should be used for better global performance",
                    actual_result="CDN detected",
                    status="Pass",
                    severity="Low",
                    comments="CDN improves global load times and reliability",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="CDN Usage",
                    test_data=url,
                    description="Check if CDN is being used",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Analyze domain\n2. Check for CDN patterns\n3. Determine CDN usage",
                    expected_result="CDN should be used for better global performance",
                    actual_result="No CDN detected",
                    status="Warning",
                    severity="Low",
                    comments="CDN can significantly improve performance for global users",
                    resolutions="Consider using a CDN for static assets (images, CSS, JS)"
                ))
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Performance Analysis",
                module="Network Analysis",
                test_data=url,
                description="Analyze network performance",
                pre_conditions="Page loaded successfully",
                test_steps="1. Check HTTP version\n2. Verify compression\n3. Analyze CDN usage",
                expected_result="Network analysis completed successfully",
                actual_result=f"Error analyzing network: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Network analysis failed",
                resolutions=""
            )
            return [error_test_case]
    
    def analyze_caching(self, response, url):
        """Analyze caching headers and configuration."""
        test_cases = []
        
        try:
            headers = response.headers
            
            # Test 1: Cache-Control Header
            cache_control = headers.get('Cache-Control', '')
            
            if cache_control:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Cache Headers",
                    test_data=url,
                    description="Check Cache-Control headers",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Check response headers\n2. Look for Cache-Control\n3. Analyze caching directives",
                    expected_result="Cache-Control headers should be present",
                    actual_result=f"Cache-Control: {cache_control[:100]}",
                    status="Pass",
                    severity="Medium",
                    comments="Caching headers improve repeat visit performance",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Cache Headers",
                    test_data=url,
                    description="Check Cache-Control headers",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Check response headers\n2. Look for Cache-Control\n3. Analyze caching directives",
                    expected_result="Cache-Control headers should be present",
                    actual_result="No Cache-Control header found",
                    status="Fail",
                    severity="Medium",
                    comments="Missing caching headers reduces performance on repeat visits",
                    resolutions="Add Cache-Control headers for static resources (e.g., max-age=31536000)"
                ))
            
            # Test 2: ETag Header
            etag = headers.get('ETag', '')
            
            if etag:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="ETag Header",
                    test_data=url,
                    description="Check for ETag header",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Check response headers\n2. Look for ETag\n3. Verify conditional requests support",
                    expected_result="ETag should be present for conditional requests",
                    actual_result="ETag header found",
                    status="Pass",
                    severity="Low",
                    comments="ETag enables conditional requests and efficient caching",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="ETag Header",
                    test_data=url,
                    description="Check for ETag header",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Check response headers\n2. Look for ETag\n3. Verify conditional requests support",
                    expected_result="ETag should be present for conditional requests",
                    actual_result="No ETag header found",
                    status="Warning",
                    severity="Low",
                    comments="Missing ETag reduces caching efficiency",
                    resolutions="Add ETag headers for better cache validation"
                ))
            
            # Test 3: Expires Header
            expires = headers.get('Expires', '')
            
            if expires:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Expires Header",
                    test_data=url,
                    description="Check for Expires header",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Check response headers\n2. Look for Expires\n3. Verify expiration date",
                    expected_result="Expires header should be present for HTTP/1.0 compatibility",
                    actual_result="Expires header found",
                    status="Pass",
                    severity="Low",
                    comments="Expires header provides fallback caching for older clients",
                    resolutions=""
                ))
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Performance Analysis",
                module="Cache Analysis",
                test_data=url,
                description="Analyze caching configuration",
                pre_conditions="Page loaded successfully",
                test_steps="1. Check cache headers\n2. Analyze caching directives\n3. Evaluate cache efficiency",
                expected_result="Cache analysis completed successfully",
                actual_result=f"Error analyzing cache: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Cache analysis failed",
                resolutions=""
            )
            return [error_test_case]
    
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
                    test_cases.append(self.create_test_case(
                        test_type="Performance Analysis",
                        module="Inline JavaScript",
                        test_data=url,
                        description="Check size of inline JavaScript",
                        pre_conditions="Page loaded successfully",
                        test_steps="1. Find inline script tags\n2. Calculate total size\n3. Check if excessive",
                        expected_result="Inline JS should be minimal (under 10KB)",
                        actual_result=f"Inline JS size: {total_inline_size/1024:.1f}KB (Large)",
                        status="Fail",
                        severity="Low",
                        comments="Large inline JavaScript blocks rendering",
                        resolutions="Move inline JavaScript to external files, defer non-critical JS"
                    ))
                else:
                    test_cases.append(self.create_test_case(
                        test_type="Performance Analysis",
                        module="Inline JavaScript",
                        test_data=url,
                        description="Check size of inline JavaScript",
                        pre_conditions="Page loaded successfully",
                        test_steps="1. Find inline script tags\n2. Calculate total size\n3. Check if excessive",
                        expected_result="Inline JS should be minimal (under 10KB)",
                        actual_result=f"Inline JS size: {total_inline_size/1024:.1f}KB (Good)",
                        status="Pass",
                        severity="Low",
                        comments="Inline JavaScript is reasonable",
                        resolutions=""
                    ))
            
            # Test 2: JavaScript Loading Strategy
            async_scripts = soup.find_all('script', attrs={'async': True})
            defer_scripts = soup.find_all('script', defer=True)
            
            if async_scripts or defer_scripts:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="JS Loading Strategy",
                    test_data=url,
                    description="Check JavaScript loading attributes",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find script tags\n2. Check async/defer attributes\n3. Analyze loading strategy",
                    expected_result="Non-critical JS should use async/defer",
                    actual_result=f"Async scripts: {len(async_scripts)}, Defer scripts: {len(defer_scripts)}",
                    status="Pass",
                    severity="Low",
                    comments="Using async/defer improves page load performance",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="JS Loading Strategy",
                    test_data=url,
                    description="Check JavaScript loading attributes",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find script tags\n2. Check async/defer attributes\n3. Analyze loading strategy",
                    expected_result="Non-critical JS should use async/defer",
                    actual_result="No async or defer attributes found",
                    status="Warning",
                    severity="Low",
                    comments="Missing async/defer can block page rendering",
                    resolutions="Add async/defer attributes to non-critical JavaScript files"
                ))
            
            # Test 3: JavaScript Frameworks Detection
            js_frameworks = {
                'jQuery': ['jquery', '$.', 'jQuery.'],
                'React': ['react', 'ReactDOM'],
                'Vue': ['vue', 'Vue.'],
                'Angular': ['angular', 'ng-'],
                'Bootstrap': ['bootstrap']
            }
            
            detected_frameworks = []
            for framework, indicators in js_frameworks.items():
                for script in scripts:
                    script_content = script.string or ''
                    script_src = script.get('src', '')
                    
                    if any(indicator.lower() in str(script_content).lower() for indicator in indicators) or \
                       any(indicator.lower() in script_src.lower() for indicator in indicators):
                        if framework not in detected_frameworks:
                            detected_frameworks.append(framework)
            
            if detected_frameworks:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="JavaScript Frameworks",
                    test_data=url,
                    description="Detect JavaScript frameworks",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Analyze script tags\n2. Detect framework patterns\n3. List detected frameworks",
                    expected_result="Frameworks should be optimized for performance",
                    actual_result=f"Detected frameworks: {', '.join(detected_frameworks)}",
                    status="Info",
                    severity="Low",
                    comments="Using JavaScript frameworks",
                    resolutions="Minify framework code, use production builds, implement code splitting"
                ))
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Performance Analysis",
                module="JavaScript Analysis",
                test_data=url,
                description="Analyze JavaScript performance",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find script tags\n2. Analyze loading strategy\n3. Detect frameworks",
                expected_result="JavaScript analysis completed successfully",
                actual_result=f"Error analyzing JavaScript: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="JavaScript analysis failed",
                resolutions=""
            )
            return [error_test_case]
    
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
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Inline CSS",
                    test_data=url,
                    description="Check size of inline CSS",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find style tags\n2. Calculate total size\n3. Check if excessive",
                    expected_result="Inline CSS should be minimal (under 5KB)",
                    actual_result=f"Inline CSS size: {total_inline_css/1024:.1f}KB (Large)",
                    status="Fail",
                    severity="Low",
                    comments="Large inline CSS blocks rendering",
                    resolutions="Move inline CSS to external files, optimize critical CSS"
                ))
            elif total_inline_css > 0:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Inline CSS",
                    test_data=url,
                    description="Check size of inline CSS",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find style tags\n2. Calculate total size\n3. Check if excessive",
                    expected_result="Inline CSS should be minimal (under 5KB)",
                    actual_result=f"Inline CSS size: {total_inline_css/1024:.1f}KB (Good)",
                    status="Pass",
                    severity="Low",
                    comments="Inline CSS is reasonable",
                    resolutions=""
                ))
            
            # Test 2: CSS Delivery Optimization
            if css_links:
                render_blocking_css = []
                for css in css_links:
                    media = css.get('media', 'all')
                    if media == 'all' or 'screen' in media:
                        render_blocking_css.append(css)
                
                if render_blocking_css:
                    test_cases.append(self.create_test_case(
                        test_type="Performance Analysis",
                        module="CSS Delivery",
                        test_data=url,
                        description="Check CSS delivery optimization",
                        pre_conditions="Page loaded successfully",
                        test_steps="1. Find CSS link tags\n2. Check media attributes\n3. Identify render-blocking CSS",
                        expected_result="CSS should be optimized for delivery",
                        actual_result=f"Render-blocking CSS files: {len(render_blocking_css)}",
                        status="Warning",
                        severity="Medium",
                        comments="Render-blocking CSS delays page display",
                        resolutions="Use media attributes, load CSS asynchronously, inline critical CSS"
                    ))
            
            # Test 3: CSS Frameworks Detection
            css_frameworks = {
                'Bootstrap': ['bootstrap'],
                'Foundation': ['foundation'],
                'Bulma': ['bulma'],
                'Tailwind': ['tailwind'],
                'Materialize': ['materialize']
            }
            
            detected_frameworks = []
            for framework, indicators in css_frameworks.items():
                for css in css_links:
                    href = css.get('href', '')
                    if any(indicator in href.lower() for indicator in indicators):
                        if framework not in detected_frameworks:
                            detected_frameworks.append(framework)
            
            if detected_frameworks:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="CSS Frameworks",
                    test_data=url,
                    description="Detect CSS frameworks",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Analyze CSS links\n2. Detect framework patterns\n3. List detected frameworks",
                    expected_result="CSS frameworks should be optimized",
                    actual_result=f"Detected frameworks: {', '.join(detected_frameworks)}",
                    status="Info",
                    severity="Low",
                    comments="Using CSS frameworks",
                    resolutions="Purge unused CSS, minify framework code, use CDN versions"
                ))
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Performance Analysis",
                module="CSS Analysis",
                test_data=url,
                description="Analyze CSS performance",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find CSS resources\n2. Analyze delivery\n3. Detect frameworks",
                expected_result="CSS analysis completed successfully",
                actual_result=f"Error analyzing CSS: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="CSS analysis failed",
                resolutions=""
            )
            return [error_test_case]
    
    def analyze_image_performance(self, soup, url):
        """Analyze image optimization and performance."""
        test_cases = []
        
        try:
            images = soup.find_all('img')
            
            if not images:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Image Analysis",
                    test_data=url,
                    description="Check image optimization",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find image tags\n2. Analyze image attributes\n3. Check optimization",
                    expected_result="Images should be optimized for web",
                    actual_result="No images found on page",
                    status="Pass",
                    severity="Low",
                    comments="No images to analyze",
                    resolutions=""
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
            
            if modern_format_percent > 50:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Image Formats",
                    test_data=url,
                    description="Check for modern image formats",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find all images\n2. Check file extensions\n3. Count modern formats",
                    expected_result="Use modern formats (WebP, AVIF) when possible",
                    actual_result=f"Modern formats: {modern_format_percent:.1f}% (Good)",
                    status="Pass",
                    severity="Low",
                    comments="Using modern image formats improves performance",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Image Formats",
                    test_data=url,
                    description="Check for modern image formats",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find all images\n2. Check file extensions\n3. Count modern formats",
                    expected_result="Use modern formats (WebP, AVIF) when possible",
                    actual_result=f"Modern formats: {modern_format_percent:.1f}% (Low)",
                    status="Warning",
                    severity="Low",
                    comments="Modern image formats provide better compression",
                    resolutions="Convert images to WebP/AVIF format with fallbacks for older browsers"
                ))
            
            # Test 2: Lazy Loading
            lazy_images = sum(1 for img in images if img.get('loading') == 'lazy')
            
            if lazy_images > 0:
                lazy_percent = (lazy_images / total_images) * 100
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Lazy Loading",
                    test_data=url,
                    description="Check for lazy loading of images",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find image tags\n2. Check loading attribute\n3. Count lazy loaded images",
                    expected_result="Below-the-fold images should use lazy loading",
                    actual_result=f"Lazy loaded images: {lazy_percent:.1f}%",
                    status="Pass" if lazy_percent > 30 else "Warning",
                    severity="Low",
                    comments="Lazy loading improves initial page load",
                    resolutions="Add loading='lazy' to below-the-fold images"
                ))
            
            # Test 3: Image Dimensions
            images_with_dimensions = 0
            for img in images:
                if img.get('width') and img.get('height'):
                    images_with_dimensions += 1
            
            dimensions_percent = (images_with_dimensions / total_images) * 100
            
            if dimensions_percent > 80:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Image Dimensions",
                    test_data=url,
                    description="Check for explicit image dimensions",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find image tags\n2. Check width/height attributes\n3. Count images with dimensions",
                    expected_result="Images should have explicit dimensions",
                    actual_result=f"Images with dimensions: {dimensions_percent:.1f}% (Good)",
                    status="Pass",
                    severity="Low",
                    comments="Explicit dimensions prevent layout shifts",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Performance Analysis",
                    module="Image Dimensions",
                    test_data=url,
                    description="Check for explicit image dimensions",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find image tags\n2. Check width/height attributes\n3. Count images with dimensions",
                    expected_result="Images should have explicit dimensions",
                    actual_result=f"Images with dimensions: {dimensions_percent:.1f}% (Low)",
                    status="Warning",
                    severity="Low",
                    comments="Missing dimensions cause layout shifts (Cumulative Layout Shift)",
                    resolutions="Add width and height attributes to all images"
                ))
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Performance Analysis",
                module="Image Analysis",
                test_data=url,
                description="Analyze image performance",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find image tags\n2. Analyze formats and attributes\n3. Check optimization",
                expected_result="Image analysis completed successfully",
                actual_result=f"Error analyzing images: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Image analysis failed",
                resolutions=""
            )
            return [error_test_case]
    
    def calculate_performance_score(self, performance_test_cases, url):
        """Calculate overall performance score based on test results."""
        if not performance_test_cases:
            return self.create_test_case(
                test_type="Performance Analysis",
                module="Performance Score",
                test_data=url,
                description="Calculate overall performance score",
                pre_conditions="All performance tests completed",
                test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
                expected_result="High performance score indicates good optimization",
                actual_result="No performance tests were performed",
                status="Fail",
                severity="Medium",
                comments="Performance analysis was not completed",
                resolutions="Run performance analysis to get comprehensive results"
            )
        
        # Weight factors based on severity
        severity_weights = {
            'Critical': 10,
            'High': 5,
            'Medium': 3,
            'Low': 1,
            'Info': 0,
            'Warning': 2
        }
        
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
            status = "Pass"
        elif performance_score >= 80:
            grade = "B (Good)"
            status = "Pass"
        elif performance_score >= 70:
            grade = "C (Average)"
            status = "Warning"
        elif performance_score >= 60:
            grade = "D (Needs Improvement)"
            status = "Fail"
        else:
            grade = "F (Poor)"
            status = "Fail"
        
        # Count test results
        passed_tests = sum(1 for tc in performance_test_cases if tc.get('Status', '').lower() in ['pass', 'passed'])
        failed_tests = sum(1 for tc in performance_test_cases if tc.get('Status', '').lower() == 'fail')
        warning_tests = sum(1 for tc in performance_test_cases if tc.get('Status', '').lower() == 'warning')
        
        return self.create_test_case(
            test_type="Performance Analysis",
            module="Performance Score",
            test_data=url,
            description="Calculate overall performance score",
            pre_conditions="All performance tests completed",
            test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
            expected_result="High performance score indicates good optimization",
            actual_result=f"Performance Score: {performance_score:.1f}% - {grade}. Passed: {passed_tests}, Failed: {failed_tests}, Warnings: {warning_tests}",
            status=status,
            severity="High" if performance_score < 70 else "Medium",
            comments=f"Based on analysis of {len(performance_test_cases)} performance factors",
            resolutions="Address failed tests to improve performance score" if performance_score < 80 else "Maintain current optimizations and monitor regularly"
        )
    
    # ============================================================================
    # ACCESSIBILITY TESTING METHODS (NEW)
    # ============================================================================
    
    def test_accessibility(self):
        """Perform comprehensive accessibility testing on working pages."""
        if not self.current_results:
            return
        
        working_urls = [r['url'] for r in self.current_results 
                       if r['status_category'] == 'Success' and r['status_code'] == 200]
        
        if not working_urls:
            self.root.after(0, self.update_accessibility_results, "No working pages found for accessibility testing.\n")
            return
        
        for url in working_urls[:3]:  # Limit to 3 pages for accessibility testing
            try:
                accessibility_test_cases = self.perform_accessibility_analysis(url)
                if accessibility_test_cases:
                    self.accessibility_results.extend(accessibility_test_cases)
                    for test_case in accessibility_test_cases:
                        self.test_cases.append(test_case)
                        # Display each line of analysis
                        self.root.after(0, self.update_accessibility_results, 
                                       f"♿ {test_case['Module']}: {test_case['Actual Result'][:100]}...\n")
            except Exception as e:
                error_test_case = self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Accessibility Analysis",
                    test_data=url,
                    description="Perform accessibility analysis on webpage",
                    pre_conditions="Page must load successfully",
                    test_steps="1. Load webpage\n2. Check accessibility features\n3. Analyze compliance",
                    expected_result="Accessibility analysis completed successfully",
                    actual_result=f"Error during accessibility analysis: {str(e)[:100]}",
                    status="Fail",
                    severity="Medium"
                )
                self.test_cases.append(error_test_case)
                self.root.after(0, self.update_accessibility_results, 
                               f"❌ Error performing accessibility analysis on {url}: {str(e)[:100]}\n")
    
    def perform_accessibility_analysis(self, url):
        """Perform comprehensive accessibility analysis on a webpage."""
        test_cases = []
        accessibility_score = 100  # Start with perfect score
        
        try:
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
            error_test_case = self.create_test_case(
                test_type="Accessibility Testing",
                module="Accessibility Analysis",
                test_data=url,
                description="Perform comprehensive accessibility analysis",
                pre_conditions="Page must load successfully",
                test_steps="1. Load webpage\n2. Check accessibility features\n3. Analyze compliance",
                expected_result="Accessibility analysis completed successfully",
                actual_result=f"Error during accessibility analysis: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Accessibility analysis failed due to error",
                resolutions="Check network connectivity and webpage accessibility"
            )
            return [error_test_case]
    
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
            'footer': soup.find_all(['footer']),
            'figure': soup.find_all(['figure']),
            'figcaption': soup.find_all(['figcaption']),
            'time': soup.find_all(['time']),
            'mark': soup.find_all(['mark']),
            'summary': soup.find_all(['summary']),
            'details': soup.find_all(['details'])
        }
        
        total_semantic = sum(len(elements) for elements in semantic_elements.values())
        
        if total_semantic > 0:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Semantic HTML",
                test_data=url,
                description="Check for semantic HTML elements",
                pre_conditions="Page loaded successfully",
                test_steps="1. Parse HTML\n2. Count semantic elements\n3. Evaluate semantic structure",
                expected_result="Page should use semantic HTML elements",
                actual_result=f"Found {total_semantic} semantic HTML elements",
                status="Pass",
                severity="Medium",
                comments="Semantic HTML improves screen reader navigation",
                resolutions=""
            ))
            
            # List found semantic elements
            found_elements = [elem for elem, count in semantic_elements.items() if count]
            if found_elements:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Semantic Elements Used",
                    test_data=url,
                    description="Identify specific semantic elements used",
                    pre_conditions="Page uses semantic HTML",
                    test_steps="1. List all semantic elements\n2. Categorize by type\n3. Check proper usage",
                    expected_result="Appropriate semantic elements should be used",
                    actual_result=f"Elements found: {', '.join(found_elements)}",
                    status="Info",
                    severity="Low",
                    comments="Good semantic structure",
                    resolutions=""
                ))
        else:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Semantic HTML",
                test_data=url,
                description="Check for semantic HTML elements",
                pre_conditions="Page loaded successfully",
                test_steps="1. Parse HTML\n2. Count semantic elements\n3. Evaluate semantic structure",
                expected_result="Page should use semantic HTML elements",
                actual_result="No semantic HTML elements found",
                status="Fail",
                severity="High",
                comments="Missing semantic HTML reduces accessibility for screen readers",
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
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Heading H1",
                    test_data=url,
                    description="Check for single H1 heading",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find all H1 elements\n2. Count occurrences\n3. Check if exactly one",
                    expected_result="Page should have exactly one H1 heading",
                    actual_result=f"Found 1 H1 heading (Good)",
                    status="Pass",
                    severity="High",
                    comments="Single H1 provides clear page structure",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Heading H1",
                    test_data=url,
                    description="Check for single H1 heading",
                    pre_conditions="Page loaded successfully",
                    test_steps="1. Find all H1 elements\n2. Count occurrences\n3. Check if exactly one",
                    expected_result="Page should have exactly one H1 heading",
                    actual_result=f"Found {h1_count} H1 headings (Should be exactly 1)",
                    status="Fail",
                    severity="High",
                    comments="Multiple H1 headings confuse screen reader users",
                    resolutions="Ensure only one H1 per page, representing main content"
                ))
        else:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Heading H1",
                test_data=url,
                description="Check for single H1 heading",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find all H1 elements\n2. Count occurrences\n3. Check if exactly one",
                expected_result="Page should have exactly one H1 heading",
                actual_result="No H1 heading found",
                status="Fail",
                severity="Critical",
                comments="Missing H1 makes page structure unclear for screen readers",
                resolutions="Add a descriptive H1 heading at the beginning of main content"
            ))
        
        # Test 3: Logical heading order
        heading_issues = []
        prev_level = 0
        
        # Find all headings in document order
        all_headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        for heading in all_headings:
            level = int(heading.name[1])
            
            # Check for skipped levels
            if level > prev_level + 1:
                heading_issues.append(f"Skipped from H{prev_level} to H{level}")
            
            prev_level = level
        
        if heading_issues:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Heading Hierarchy",
                test_data=url,
                description="Check logical heading order",
                pre_conditions="Page has headings",
                test_steps="1. Find all headings\n2. Check hierarchy\n3. Identify skips",
                expected_result="Headings should follow logical hierarchy (H1 > H2 > H3...)",
                actual_result=f"Issues found: {', '.join(heading_issues[:3])}",
                status="Fail",
                severity="Medium",
                comments="Skipped heading levels confuse screen reader users",
                resolutions="Maintain sequential heading levels without skipping"
            ))
        else:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Heading Hierarchy",
                test_data=url,
                description="Check logical heading order",
                pre_conditions="Page has headings",
                test_steps="1. Find all headings\n2. Check hierarchy\n3. Identify skips",
                expected_result="Headings should follow logical hierarchy (H1 > H2 > H3...)",
                actual_result="Heading hierarchy is logical",
                status="Pass",
                severity="Medium",
                comments="Good heading structure for navigation",
                resolutions=""
            ))
        
        return test_cases
    
    def analyze_aria_attributes(self, soup, url):
        """Analyze ARIA (Accessible Rich Internet Applications) attributes."""
        test_cases = []
        
        # Find elements with ARIA attributes
        aria_elements = soup.find_all(attrs={"aria-": True})
        aria_labels = soup.find_all(attrs={"aria-label": True})
        aria_describedby = soup.find_all(attrs={"aria-describedby": True})
        aria_labelledby = soup.find_all(attrs={"aria-labelledby": True})
        aria_hidden = soup.find_all(attrs={"aria-hidden": True})
        
        # Test 1: ARIA usage
        if aria_elements:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="ARIA Usage",
                test_data=url,
                description="Check for ARIA attributes usage",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find elements with ARIA attributes\n2. Count usage\n3. Evaluate implementation",
                expected_result="ARIA should be used appropriately to enhance accessibility",
                actual_result=f"Found {len(aria_elements)} elements with ARIA attributes",
                status="Pass",
                severity="Low",
                comments="ARIA attributes enhance accessibility for complex widgets",
                resolutions=""
            ))
            
            # Test 2: ARIA labels
            if aria_labels:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="ARIA Labels",
                    test_data=url,
                    description="Check for ARIA labels",
                    pre_conditions="ARIA attributes found",
                    test_steps="1. Find elements with aria-label\n2. Check label quality\n3. Evaluate usefulness",
                    expected_result="Interactive elements should have aria-label when needed",
                    actual_result=f"Found {len(aria_labels)} elements with aria-label",
                    status="Pass",
                    severity="Medium",
                    comments="ARIA labels provide accessible names for elements",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="ARIA Labels",
                    test_data=url,
                    description="Check for ARIA labels",
                    pre_conditions="ARIA attributes found",
                    test_steps="1. Find elements with aria-label\n2. Check label quality\n3. Evaluate usefulness",
                    expected_result="Interactive elements should have aria-label when needed",
                    actual_result="No aria-label attributes found",
                    status="Warning",
                    severity="Low",
                    comments="aria-label can improve accessibility for icon buttons and complex controls",
                    resolutions="Add aria-label to interactive elements without visible text"
                ))
            
            # Test 3: ARIA describedby/labelledby
            if aria_describedby or aria_labelledby:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="ARIA Relationships",
                    test_data=url,
                    description="Check for ARIA relationship attributes",
                    pre_conditions="ARIA attributes found",
                    test_steps="1. Find aria-describedby\n2. Find aria-labelledby\n3. Check relationships",
                    expected_result="Complex elements should use relationship attributes",
                    actual_result=f"aria-describedby: {len(aria_describedby)}, aria-labelledby: {len(aria_labelledby)}",
                    status="Pass",
                    severity="Low",
                    comments="ARIA relationships connect elements for better understanding",
                    resolutions=""
                ))
            
            # Test 4: ARIA hidden elements
            if aria_hidden:
                hidden_true = sum(1 for elem in aria_hidden if elem.get('aria-hidden', '').lower() == 'true')
                
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="ARIA Hidden",
                    test_data=url,
                    description="Check for aria-hidden elements",
                    pre_conditions="ARIA attributes found",
                    test_steps="1. Find aria-hidden attributes\n2. Check if set to true\n3. Evaluate appropriateness",
                    expected_result="Decorative elements should be hidden from screen readers",
                    actual_result=f"Found {hidden_true} elements hidden from screen readers",
                    status="Info",
                    severity="Low",
                    comments="Proper use of aria-hidden improves screen reader experience",
                    resolutions=""
                ))
        
        else:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="ARIA Usage",
                test_data=url,
                description="Check for ARIA attributes usage",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find elements with ARIA attributes\n2. Count usage\n3. Evaluate implementation",
                expected_result="ARIA should be used appropriately to enhance accessibility",
                actual_result="No ARIA attributes found",
                status="Info",
                severity="Low",
                comments="ARIA not used (may be acceptable for simple pages)",
                resolutions="Consider adding ARIA attributes for complex interactive elements"
            ))
        
        # Test 5: Check for invalid ARIA roles
        invalid_roles = []
        for elem in aria_elements:
            role = elem.get('role', '')
            if role and role not in self._get_valid_aria_roles():
                invalid_roles.append(role)
        
        if invalid_roles:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="ARIA Role Validation",
                test_data=url,
                description="Check for invalid ARIA roles",
                pre_conditions="ARIA attributes found",
                test_steps="1. Find all role attributes\n2. Validate against ARIA specification\n3. Identify invalid roles",
                expected_result="ARIA roles should be valid according to specification",
                actual_result=f"Invalid roles found: {', '.join(set(invalid_roles)[:5])}",
                status="Fail",
                severity="Medium",
                comments="Invalid ARIA roles may not work as expected with assistive technologies",
                resolutions="Use only valid ARIA roles from WAI-ARIA specification"
            ))
        
        return test_cases
    
    def _get_valid_aria_roles(self):
        """Return list of valid ARIA roles."""
        return [
            'alert', 'alertdialog', 'application', 'article', 'banner', 'button',
            'cell', 'checkbox', 'columnheader', 'combobox', 'complementary',
            'contentinfo', 'definition', 'dialog', 'directory', 'document',
            'feed', 'figure', 'form', 'grid', 'gridcell', 'group', 'heading',
            'img', 'link', 'list', 'listbox', 'listitem', 'log', 'main',
            'marquee', 'math', 'menu', 'menubar', 'menuitem', 'menuitemcheckbox',
            'menuitemradio', 'navigation', 'none', 'note', 'option', 'presentation',
            'progressbar', 'radio', 'radiogroup', 'region', 'row', 'rowgroup',
            'rowheader', 'scrollbar', 'search', 'searchbox', 'separator',
            'slider', 'spinbutton', 'status', 'switch', 'tab', 'table',
            'tablist', 'tabpanel', 'term', 'textbox', 'timer', 'toolbar',
            'tooltip', 'tree', 'treegrid', 'treeitem'
        ]
    
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
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Keyboard Focus",
                test_data=url,
                description="Check for keyboard focusable elements",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find interactive elements\n2. Check if focusable\n3. Count focusable elements",
                expected_result="All interactive elements should be keyboard focusable",
                actual_result=f"Found {len(focusable_elements)} focusable elements",
                status="Pass",
                severity="High",
                comments="Elements can receive keyboard focus",
                resolutions=""
            ))
        else:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Keyboard Focus",
                test_data=url,
                description="Check for keyboard focusable elements",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find interactive elements\n2. Check if focusable\n3. Count focusable elements",
                expected_result="All interactive elements should be keyboard focusable",
                actual_result="No focusable elements found",
                status="Warning",
                severity="Medium",
                comments="Page may lack interactive elements or they may not be keyboard accessible",
                resolutions="Ensure all interactive elements can receive keyboard focus"
            ))
        
        # Test 2: Tabindex usage
        tabindex_elements = soup.find_all(attrs={"tabindex": True})
        tabindex_values = {}
        
        for elem in tabindex_elements:
            tabindex = elem.get('tabindex', '')
            if tabindex:
                if tabindex not in tabindex_values:
                    tabindex_values[tabindex] = 0
                tabindex_values[tabindex] += 1
        
        if tabindex_elements:
            # Check for problematic tabindex values
            problematic = []
            for value in tabindex_values:
                if value.startswith('-') or value == '0':
                    continue
                if int(value) > 0:
                    problematic.append(value)
            
            if problematic:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Tabindex Values",
                    test_data=url,
                    description="Check for problematic tabindex values",
                    pre_conditions="tabindex attributes found",
                    test_steps="1. Find tabindex attributes\n2. Check values\n3. Identify problematic values",
                    expected_result="tabindex should be 0 or negative, not positive",
                    actual_result=f"Found positive tabindex values: {', '.join(problematic)}",
                    status="Fail",
                    severity="Medium",
                    comments="Positive tabindex values disrupt natural tab order",
                    resolutions="Change positive tabindex values to 0 or remove them"
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Tabindex Usage",
                    test_data=url,
                    description="Check tabindex attribute usage",
                    pre_conditions="tabindex attributes found",
                    test_steps="1. Find tabindex attributes\n2. Check values\n3. Evaluate implementation",
                    expected_result="tabindex should be used appropriately",
                    actual_result=f"Found {len(tabindex_elements)} elements with tabindex",
                    status="Info",
                    severity="Low",
                    comments="tabindex attributes present",
                    resolutions=""
                ))
        
        # Test 3: Skip links
        skip_links = soup.find_all('a', href=lambda x: x and '#main' in x or 'skip' in (x or '').lower())
        
        if skip_links:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Skip Links",
                test_data=url,
                description="Check for skip navigation links",
                pre_conditions="Page loaded successfully",
                test_steps="1. Look for skip links\n2. Check functionality\n3. Evaluate implementation",
                expected_result="Long pages should have skip links for keyboard users",
                actual_result=f"Found {len(skip_links)} skip link(s)",
                status="Pass",
                severity="Medium",
                comments="Skip links improve navigation for keyboard users",
                resolutions=""
            ))
        else:
            # Check if page is long enough to need skip links
            content_length = len(soup.get_text())
            if content_length > 5000:  # 5000 characters threshold
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Skip Links",
                    test_data=url,
                    description="Check for skip navigation links",
                    pre_conditions="Page has substantial content",
                    test_steps="1. Check content length\n2. Look for skip links\n3. Determine need",
                    expected_result="Long pages should have skip links for keyboard users",
                    actual_result="No skip links found for long page",
                    status="Warning",
                    severity="Medium",
                    comments="Long pages without skip links are difficult to navigate with keyboard",
                    resolutions="Add skip-to-content link at beginning of page"
                ))
        
        # Test 4: Focus indicators
        # This is harder to check from HTML alone, but we can check CSS
        style_content = ''
        for style in soup.find_all('style'):
            if style.string:
                style_content += style.string
        
        focus_selectors = [':focus', ':focus-visible', 'outline', 'box-shadow']
        has_focus_styles = any(selector in style_content for selector in focus_selectors)
        
        if has_focus_styles:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Focus Indicators",
                test_data=url,
                description="Check for visible focus indicators",
                pre_conditions="Page loaded successfully",
                test_steps="1. Check CSS for focus styles\n2. Look for outline/box-shadow\n3. Evaluate visibility",
                expected_result="Focus indicators should be clearly visible",
                actual_result="Focus styles found in CSS",
                status="Pass",
                severity="High",
                comments="Visible focus indicators help keyboard users",
                resolutions=""
            ))
        else:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Focus Indicators",
                test_data=url,
                description="Check for visible focus indicators",
                pre_conditions="Page loaded successfully",
                test_steps="1. Check CSS for focus styles\n2. Look for outline/box-shadow\n3. Evaluate visibility",
                expected_result="Focus indicators should be clearly visible",
                actual_result="No focus styles found in CSS",
                status="Warning",
                severity="High",
                comments="Missing focus indicators make keyboard navigation difficult",
                resolutions="Add CSS for :focus and :focus-visible states with clear visual indicators"
            ))
        
        return test_cases
    
    def analyze_color_contrast(self, soup, url):
        """Analyze color contrast for accessibility."""
        test_cases = []
        
        # Note: Full color contrast analysis requires rendering the page
        # This is a simplified analysis that checks for common issues
        
        # Test 1: Check for color-dependent information
        color_dependent_text = []
        for elem in soup.find_all(['span', 'div', 'p', 'a']):
            style = elem.get('style', '').lower()
            text = elem.get_text(strip=True)
            
            if text and any(color_indicator in style for color_indicator in ['color:', 'background:', 'rgb', 'hsl', '#']):
                # Check for color-only indicators
                if any(pattern in text.lower() for pattern in ['red', 'green', 'blue', 'color', 'colored']):
                    color_dependent_text.append(text[:50])
        
        if color_dependent_text:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Color-Dependent Information",
                test_data=url,
                description="Check for information conveyed only by color",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find text elements\n2. Check for color-only indicators\n3. Identify color-dependent information",
                expected_result="Information should not be conveyed by color alone",
                actual_result=f"Found {len(color_dependent_text)} instances of potentially color-only information",
                status="Warning",
                severity="Medium",
                comments="Color-only information is inaccessible to color-blind users",
                resolutions="Add text labels or patterns along with color coding"
            ))
        
        # Test 2: Check inline styles for potential low contrast
        potential_low_contrast = []
        for elem in soup.find_all(style=True):
            style = elem.get('style', '').lower()
            if 'color:' in style and 'background:' in style:
                # Extract color values (simplified check)
                color_match = re.search(r'color:\s*(#[0-9a-f]{3,6}|rgb\([^)]+\)|hsl\([^)]+\))', style)
                bg_match = re.search(r'background(?:-color)?:\s*(#[0-9a-f]{3,6}|rgb\([^)]+\)|hsl\([^)]+\))', style)
                
                if color_match and bg_match:
                    # Note: Actual contrast calculation would require parsing color values
                    potential_low_contrast.append(elem.name)
        
        if potential_low_contrast:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Inline Style Contrast",
                test_data=url,
                description="Check inline styles for potential contrast issues",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find elements with inline styles\n2. Extract color and background\n3. Identify potential issues",
                expected_result="Text should have sufficient color contrast",
                actual_result=f"Found {len(potential_low_contrast)} elements with both color and background styles",
                status="Warning",
                severity="Medium",
                comments="Inline styles may have contrast issues. Manual verification needed.",
                resolutions="Use color contrast checking tools to verify minimum 4.5:1 ratio for normal text"
            ))
        
        # Test 3: Check for sufficient link contrast
        links_with_styles = soup.find_all('a', style=True)
        styled_links_count = len(links_with_styles)
        
        if styled_links_count > 0:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Link Styling",
                test_data=url,
                description="Check styled links for contrast",
                pre_conditions="Page has styled links",
                test_steps="1. Find styled links\n2. Check for color styling\n3. Evaluate contrast requirements",
                expected_result="Links should have sufficient contrast and clear visual distinction",
                actual_result=f"Found {styled_links_count} links with inline styles",
                status="Info",
                severity="Low",
                comments="Styled links should maintain sufficient contrast from surrounding text",
                resolutions="Ensure link color has 3:1 contrast with surrounding text and 4.5:1 with background"
            ))
        
        return test_cases
    
    def analyze_form_accessibility(self, soup, url):
        """Analyze form accessibility."""
        test_cases = []
        
        forms = soup.find_all('form')
        
        if not forms:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Form Accessibility",
                test_data=url,
                description="Check form accessibility features",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find forms\n2. Check accessibility attributes\n3. Evaluate form structure",
                expected_result="Forms should be accessible to all users",
                actual_result="No forms found on page",
                status="Pass",
                severity="Low",
                comments="No forms to analyze",
                resolutions=""
            ))
            return test_cases
        
        # Test 1: Form labels
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
            
            if label_percentage >= 90:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Form Labels",
                    test_data=f"{url} - {form_id}",
                    description="Check form input labels",
                    pre_conditions="Form found on page",
                    test_steps="1. Find form inputs\n2. Check for associated labels\n3. Calculate labeled percentage",
                    expected_result="All form inputs should have associated labels",
                    actual_result=f"{label_percentage:.1f}% of inputs have labels",
                    status="Pass",
                    severity="High",
                    comments="Good form labeling",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Form Labels",
                    test_data=f"{url} - {form_id}",
                    description="Check form input labels",
                    pre_conditions="Form found on page",
                    test_steps="1. Find form inputs\n2. Check for associated labels\n3. Calculate labeled percentage",
                    expected_result="All form inputs should have associated labels",
                    actual_result=f"Only {label_percentage:.1f}% of inputs have labels",
                    status="Fail",
                    severity="High",
                    comments="Missing labels make forms inaccessible to screen reader users",
                    resolutions="Add labels for all form inputs using <label> elements or aria-label/aria-labelledby"
                ))
            
            # Test 2: Required fields indication
            required_inputs = form.find_all(attrs={'required': True})
            aria_required = form.find_all(attrs={'aria-required': 'true'})
            
            if required_inputs or aria_required:
                total_required = len(required_inputs) + len(aria_required)
                
                # Check for required field indicators
                required_text = form.get_text().lower()
                has_asterisk = '*' in form.get_text()
                has_required_text = 'required' in required_text
                
                if has_asterisk or has_required_text:
                    test_cases.append(self.create_test_case(
                        test_type="Accessibility Testing",
                        module="Required Fields",
                        test_data=f"{url} - {form_id}",
                        description="Check required fields indication",
                        pre_conditions="Form has required fields",
                        test_steps="1. Find required fields\n2. Check for visual indicators\n3. Check for accessible indication",
                        expected_result="Required fields should be clearly indicated",
                        actual_result=f"Found {total_required} required fields with indicators",
                        status="Pass",
                        severity="Medium",
                        comments="Required fields are properly indicated",
                        resolutions=""
                    ))
                else:
                    test_cases.append(self.create_test_case(
                        test_type="Accessibility Testing",
                        module="Required Fields",
                        test_data=f"{url} - {form_id}",
                        description="Check required fields indication",
                        pre_conditions="Form has required fields",
                        test_steps="1. Find required fields\n2. Check for visual indicators\n3. Check for accessible indication",
                        expected_result="Required fields should be clearly indicated",
                        actual_result=f"Found {total_required} required fields but no clear indicators",
                        status="Fail",
                        severity="Medium",
                        comments="Required fields not clearly indicated for all users",
                        resolutions="Add visual indicators (asterisks) and aria-required attributes"
                    ))
            
            # Test 3: Error handling
            error_elements = form.find_all(attrs={'aria-invalid': 'true'})
            error_messages = form.find_all(attrs={'aria-errormessage': True})
            
            if error_elements or error_messages:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Form Error Handling",
                    test_data=f"{url} - {form_id}",
                    description="Check form error accessibility",
                    pre_conditions="Form found on page",
                    test_steps="1. Check for error attributes\n2. Look for error messages\n3. Evaluate accessibility",
                    expected_result="Form errors should be accessible",
                    actual_result=f"Found error handling attributes",
                    status="Pass",
                    severity="Medium",
                    comments="Form has accessible error handling",
                    resolutions=""
                ))
        
        # Test 4: Form instructions
        for form_idx, form in enumerate(forms):
            form_id = form.get('id', f'form_{form_idx}')
            
            # Check for form instructions
            instructions = []
            
            # Look for aria-describedby
            aria_describedby = form.get('aria-describedby')
            if aria_describedby:
                instructions.append('aria-describedby')
            
            # Look for legend in fieldset
            fieldsets = form.find_all('fieldset')
            for fieldset in fieldsets:
                legend = fieldset.find('legend')
                if legend and legend.get_text(strip=True):
                    instructions.append('fieldset with legend')
            
            # Look for descriptive text near form
            form_text = form.get_text(strip=True)
            if len(form_text) > 100:  # Arbitrary threshold for descriptive form
                instructions.append('descriptive text')
            
            if instructions:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Form Instructions",
                    test_data=f"{url} - {form_id}",
                    description="Check for form instructions",
                    pre_conditions="Form found on page",
                    test_steps="1. Look for form instructions\n2. Check for aria-describedby\n3. Check for fieldset legends",
                    expected_result="Complex forms should have instructions",
                    actual_result=f"Found form instructions: {', '.join(instructions)}",
                    status="Pass",
                    severity="Low",
                    comments="Form has accessible instructions",
                    resolutions=""
                ))
        
        return test_cases
    
    def analyze_media_accessibility(self, soup, url):
        """Analyze media (images, videos, audio) accessibility."""
        test_cases = []
        
        # Test 1: Image alt text (already covered in SEO, but from accessibility perspective)
        images = soup.find_all('img')
        decorative_images = []
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
                
                if role == 'presentation' or aria_hidden == 'true':
                    decorative_images.append(img)
                else:
                    # Could be decorative but missing proper markup
                    images_missing_alt.append(img)
            else:
                informative_images.append(img)
        
        total_images = len(images)
        
        if total_images > 0:
            # Test for informative images with alt text
            informative_with_alt = len(informative_images)
            informative_percentage = (informative_with_alt / total_images) * 100
            
            if informative_percentage >= 90:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Image Alt Text",
                    test_data=url,
                    description="Check image alternative text",
                    pre_conditions="Page has images",
                    test_steps="1. Find all images\n2. Check alt attributes\n3. Categorize images",
                    expected_result="Informative images should have descriptive alt text",
                    actual_result=f"{informative_percentage:.1f}% of images have proper alt text",
                    status="Pass",
                    severity="High",
                    comments="Good image accessibility",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Image Alt Text",
                    test_data=url,
                    description="Check image alternative text",
                    pre_conditions="Page has images",
                    test_steps="1. Find all images\n2. Check alt attributes\n3. Categorize images",
                    expected_result="Informative images should have descriptive alt text",
                    actual_result=f"Only {informative_percentage:.1f}% of images have proper alt text",
                    status="Fail",
                    severity="High",
                    comments="Missing alt text makes images inaccessible to screen reader users",
                    resolutions="Add descriptive alt text to informative images, add empty alt to decorative images"
                ))
            
            # Test for decorative image markup
            if decorative_images:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Decorative Images",
                    test_data=url,
                    description="Check decorative image markup",
                    pre_conditions="Page has decorative images",
                    test_steps="1. Find images with empty alt\n2. Check decorative markup\n3. Evaluate accessibility",
                    expected_result="Decorative images should be properly marked",
                    actual_result=f"Found {len(decorative_images)} decorative images",
                    status="Pass",
                    severity="Low",
                    comments="Decorative images are properly marked",
                    resolutions=""
                ))
        
        # Test 2: Video accessibility
        videos = soup.find_all('video')
        
        if videos:
            accessible_videos = []
            for video in videos:
                # Check for tracks (captions)
                tracks = video.find_all('track')
                has_captions = any(track.get('kind') == 'captions' for track in tracks)
                
                # Check for audio description
                has_description = any(track.get('kind') == 'descriptions' for track in tracks)
                
                if has_captions or has_description:
                    accessible_videos.append(video)
            
            if accessible_videos:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Video Accessibility",
                    test_data=url,
                    description="Check video accessibility features",
                    pre_conditions="Page has videos",
                    test_steps="1. Find video elements\n2. Check for captions\n3. Check for audio descriptions",
                    expected_result="Videos should have captions and audio descriptions",
                    actual_result=f"{len(accessible_videos)}/{len(videos)} videos have accessibility features",
                    status="Pass",
                    severity="High",
                    comments="Videos have accessibility features",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Video Accessibility",
                    test_data=url,
                    description="Check video accessibility features",
                    pre_conditions="Page has videos",
                    test_steps="1. Find video elements\n2. Check for captions\n3. Check for audio descriptions",
                    expected_result="Videos should have captions and audio descriptions",
                    actual_result=f"None of the {len(videos)} videos have accessibility features",
                    status="Fail",
                    severity="High",
                    comments="Videos without captions are inaccessible to deaf/hard-of-hearing users",
                    resolutions="Add captions using <track> elements with kind='captions'"
                ))
        
        # Test 3: Audio accessibility
        audio_elements = soup.find_all('audio')
        
        if audio_elements:
            accessible_audio = []
            for audio in audio_elements:
                # Check for transcripts or captions
                tracks = audio.find_all('track')
                has_captions = any(track.get('kind') == 'subtitles' for track in tracks)
                
                # Check for text transcript link
                parent = audio.parent
                sibling_text = parent.get_text() if parent else ''
                has_transcript = 'transcript' in sibling_text.lower() or 'caption' in sibling_text.lower()
                
                if has_captions or has_transcript:
                    accessible_audio.append(audio)
            
            if accessible_audio:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Audio Accessibility",
                    test_data=url,
                    description="Check audio accessibility features",
                    pre_conditions="Page has audio elements",
                    test_steps="1. Find audio elements\n2. Check for captions/transcripts\n3. Evaluate accessibility",
                    expected_result="Audio should have captions or transcripts",
                    actual_result=f"{len(accessible_audio)}/{len(audio_elements)} audio elements have accessibility features",
                    status="Pass",
                    severity="High",
                    comments="Audio has accessibility features",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Audio Accessibility",
                    test_data=url,
                    description="Check audio accessibility features",
                    pre_conditions="Page has audio elements",
                    test_steps="1. Find audio elements\n2. Check for captions/transcripts\n3. Evaluate accessibility",
                    expected_result="Audio should have captions or transcripts",
                    actual_result=f"None of the {len(audio_elements)} audio elements have accessibility features",
                    status="Fail",
                    severity="High",
                    comments="Audio without transcripts is inaccessible to deaf/hard-of-hearing users",
                    resolutions="Provide transcripts or captions for all audio content"
                ))
        
        # Test 4: Canvas accessibility
        canvas_elements = soup.find_all('canvas')
        
        if canvas_elements:
            accessible_canvas = []
            for canvas in canvas_elements:
                # Check for fallback content
                fallback = canvas.get_text(strip=True)
                aria_label = canvas.get('aria-label')
                aria_labelledby = canvas.get('aria-labelledby')
                
                if fallback or aria_label or aria_labelledby:
                    accessible_canvas.append(canvas)
            
            if accessible_canvas:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Canvas Accessibility",
                    test_data=url,
                    description="Check canvas accessibility",
                    pre_conditions="Page has canvas elements",
                    test_steps="1. Find canvas elements\n2. Check for fallback content\n3. Check for ARIA labels",
                    expected_result="Canvas should have accessible fallback",
                    actual_result=f"{len(accessible_canvas)}/{len(canvas_elements)} canvas elements have accessibility features",
                    status="Pass",
                    severity="Medium",
                    comments="Canvas elements have accessibility features",
                    resolutions=""
                ))
            else:
                test_cases.append(self.create_test_case(
                    test_type="Accessibility Testing",
                    module="Canvas Accessibility",
                    test_data=url,
                    description="Check canvas accessibility",
                    pre_conditions="Page has canvas elements",
                    test_steps="1. Find canvas elements\n2. Check for fallback content\n3. Check for ARIA labels",
                    expected_result="Canvas should have accessible fallback",
                    actual_result=f"None of the {len(canvas_elements)} canvas elements have accessibility features",
                    status="Fail",
                    severity="Medium",
                    comments="Canvas without fallback content is inaccessible to screen reader users",
                    resolutions="Add fallback content or ARIA labels to canvas elements"
                ))
        
        return test_cases
    
    def analyze_language_accessibility(self, soup, url):
        """Analyze language and reading accessibility."""
        test_cases = []
        
        # Test 1: Page language declaration
        html_tag = soup.find('html')
        lang = html_tag.get('lang') if html_tag else None
        
        if lang:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Page Language",
                test_data=url,
                description="Check page language declaration",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find html tag\n2. Check lang attribute\n3. Verify language code",
                expected_result="Page should declare primary language",
                actual_result=f"Language declared: {lang}",
                status="Pass",
                severity="High",
                comments="Language declaration helps screen readers and translation tools",
                resolutions=""
            ))
        else:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Page Language",
                test_data=url,
                description="Check page language declaration",
                pre_conditions="Page loaded successfully",
                test_steps="1. Find html tag\n2. Check lang attribute\n3. Verify language code",
                expected_result="Page should declare primary language",
                actual_result="No language declared",
                status="Fail",
                severity="High",
                comments="Missing language declaration affects screen reader pronunciation",
                resolutions="Add lang attribute to html tag (e.g., lang='en')"
            ))
        
        # Test 2: Language changes within page
        lang_changes = soup.find_all(attrs={'lang': True})
        if lang_changes:
            # Exclude the html tag
            lang_changes = [elem for elem in lang_changes if elem.name != 'html']
            
            if lang_changes:
                unique_langs = set()
                for elem in lang_changes:
                    elem_lang = elem.get('lang', '')
                    if elem_lang and elem_lang != lang:
                        unique_langs.add(elem_lang)
                
                if unique_langs:
                    test_cases.append(self.create_test_case(
                        test_type="Accessibility Testing",
                        module="Language Changes",
                        test_data=url,
                        description="Check for language changes within page",
                        pre_conditions="Page has content in multiple languages",
                        test_steps="1. Find elements with lang attribute\n2. Identify language changes\n3. Check proper markup",
                        expected_result="Language changes should be properly marked",
                        actual_result=f"Found content in other languages: {', '.join(unique_langs)}",
                        status="Pass",
                        severity="Medium",
                        comments="Language changes are properly marked",
                        resolutions=""
                    ))
        
        # Test 3: Reading order and linear layout
        # Check for CSS floats and positioning that might affect reading order
        style_content = ''
        for style in soup.find_all('style'):
            if style.string:
                style_content += style.string
        
        # Look for layout techniques that might disrupt reading order
        layout_patterns = {
            'float': 'float:',
            'absolute': 'position: absolute',
            'fixed': 'position: fixed',
            'grid': 'display: grid',
            'flex': 'display: flex'
        }
        
        found_patterns = []
        for pattern_name, pattern in layout_patterns.items():
            if pattern in style_content:
                found_patterns.append(pattern_name)
        
        if found_patterns:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Layout Techniques",
                test_data=url,
                description="Check layout techniques for reading order",
                pre_conditions="Page uses CSS layout",
                test_steps="1. Analyze CSS\n2. Identify layout techniques\n3. Check for reading order issues",
                expected_result="Layout should maintain logical reading order",
                actual_result=f"Uses layout techniques: {', '.join(found_patterns)}",
                status="Info",
                severity="Low",
                comments="Advanced layout techniques may affect reading order",
                resolutions="Ensure visual order matches DOM order for keyboard navigation"
            ))
        
        # Test 4: Text spacing
        # Check for fixed line heights that might cause issues
        line_height_patterns = ['line-height:', 'line-height :']
        has_fixed_line_height = any(pattern in style_content for pattern in line_height_patterns)
        
        if has_fixed_line_height:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Text Spacing",
                test_data=url,
                description="Check text spacing properties",
                pre_conditions="Page has CSS styling",
                test_steps="1. Check CSS for line-height\n2. Look for fixed values\n3. Evaluate flexibility",
                expected_result="Text spacing should be adjustable by users",
                actual_result="Fixed line heights found",
                status="Warning",
                severity="Low",
                comments="Fixed line heights may not accommodate user preferences",
                resolutions="Use relative units (em, rem) for line-height instead of fixed pixels"
            ))
        
        # Test 5: Text resizing
        # Check for fixed font sizes
        font_size_patterns = ['font-size:', 'font-size :']
        has_fixed_font_sizes = any(pattern in style_content for pattern in font_size_patterns)
        
        if has_fixed_font_sizes:
            test_cases.append(self.create_test_case(
                test_type="Accessibility Testing",
                module="Text Resizing",
                test_data=url,
                description="Check font size properties",
                pre_conditions="Page has CSS styling",
                test_steps="1. Check CSS for font-size\n2. Look for fixed values\n3. Evaluate resizability",
                expected_result="Text should be resizable without loss of content",
                actual_result="Fixed font sizes found",
                status="Warning",
                severity="Low",
                comments="Fixed font sizes may prevent text resizing",
                resolutions="Use relative units (em, rem, %) for font sizes"
            ))
        
        return test_cases
    
    def calculate_accessibility_score(self, accessibility_test_cases, url):
        """Calculate overall accessibility score based on test results."""
        if not accessibility_test_cases:
            return self.create_test_case(
                test_type="Accessibility Testing",
                module="Accessibility Score",
                test_data=url,
                description="Calculate overall accessibility score",
                pre_conditions="All accessibility tests completed",
                test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
                expected_result="High accessibility score indicates good compliance",
                actual_result="No accessibility tests were performed",
                status="Fail",
                severity="Medium",
                comments="Accessibility analysis was not completed",
                resolutions="Run accessibility analysis to get comprehensive results"
            )
        
        # Weight factors based on severity
        severity_weights = {
            'Critical': 10,
            'High': 5,
            'Medium': 3,
            'Low': 1,
            'Info': 0,
            'Warning': 2
        }
        
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
        
        return self.create_test_case(
            test_type="Accessibility Testing",
            module="Accessibility Score",
            test_data=url,
            description="Calculate overall accessibility score",
            pre_conditions="All accessibility tests completed",
            test_steps="1. Collect all test results\n2. Calculate score based on passes/fails\n3. Weight by severity",
            expected_result="High accessibility score indicates good compliance",
            actual_result=f"Accessibility Score: {accessibility_score:.1f}% - {grade}. Passed: {passed_tests}, Failed: {failed_tests}, Warnings: {warning_tests}",
            status=status_result,
            severity="High" if accessibility_score < 70 else "Medium",
            comments=f"Based on analysis of {len(accessibility_test_cases)} accessibility factors",
            resolutions="Address failed tests to improve accessibility score" if accessibility_score < 80 else "Maintain current accessibility features and monitor regularly"
        )
    
    # ============================================================================
    # TEST CASE CREATION HELPER FUNCTIONS
    # ============================================================================
    
    def create_test_case(self, test_type, module, test_data, description, pre_conditions,
                        test_steps, expected_result, actual_result, status, 
                        severity="Medium", comments="", resolutions=""):
        """
        Create a standardized test case dictionary.
        
        Args:
            test_type: Type of test (Link Check, Button Test, etc.)
            module: Module/Root URL's next page
            test_data: URL or data being tested
            description: Detailed description of test case
            pre_conditions: Pre-requisites for test
            test_steps: Step-by-step test procedure
            expected_result: Expected outcome
            actual_result: Actual outcome after test
            status: Pass/Fail/Blocked/Not Run
            severity: Critical/High/Medium/Low/Info
            comments: Bug reference or comments
            resolutions: Resolution steps if failed
            
        Returns:
            Dictionary with test case data
        """
        test_id = f"TC{self.test_case_counter:04d}"
        self.test_case_counter += 1
        
        # Determine pass/fail based on status
        case_pass_fail = "Pass" if status.lower() in ["pass", "passed"] else "Fail"
        
        test_case = {
            'Test ID': test_id,
            'Module': module,
            'Test Links/Data': str(test_data)[:500],  # Limit length
            'Test Case Description': description,
            'Pre-Conditions': pre_conditions,
            'Test Steps': test_steps,
            'Expected Result': expected_result,
            'Actual Result': str(actual_result)[:500],  # Limit length
            'Status': status,
            'Severity': severity,
            'Case Pass/Fail': case_pass_fail,
            'Comments/Bug ID': comments,
            'Resolutions': resolutions,
            'Test Type': test_type,  # Internal field for categorization
            'Timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return test_case
    
    # ============================================================================
    # UI UPDATE FUNCTIONS FOR NEW TABS
    # ============================================================================
    
    def update_performance_results(self, result):
        """Update performance analysis results text area."""
        self.performance_text.config(state=tk.NORMAL)
        self.performance_text.insert(tk.END, result)
        self.performance_text.see(tk.END)
        self.performance_text.config(state=tk.DISABLED)
    
    def update_accessibility_results(self, result):
        """Update accessibility testing results text area."""
        self.accessibility_text.config(state=tk.NORMAL)
        self.accessibility_text.insert(tk.END, result)
        self.accessibility_text.see(tk.END)
        self.accessibility_text.config(state=tk.DISABLED)
    
    # ============================================================================
    # ENHANCED REPORT GENERATION (NEW)
    # ============================================================================
    
    def export_report(self):
        """Export test results to various formats with enhanced reporting."""
        if not any([self.current_results, self.button_test_results, self.spelling_results, 
                   self.font_results, self.responsiveness_results, self.browser_compatibility_results,
                   self.seo_results, self.performance_results, self.accessibility_results]):
            messagebox.showwarning("Warning", "No results to export.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"website_comprehensive_test_{timestamp}"
        
        filetypes = [
            ("Excel Report", "*.xlsx"),
            ("PDF Report", "*.pdf"),
            ("HTML Report", "*.html"),
            ("JSON Report", "*.json"),
            ("CSV Report", "*.csv"),
            ("Executive Summary (PDF)", "*_executive.pdf"),
            ("Complete Report Package", "*.zip"),
            ("All Formats", "*.*")
        ]
        
        filename = filedialog.asksaveasfilename(
            initialfile=default_name,
            defaultextension=".xlsx",
            filetypes=filetypes
        )
        
        if not filename:
            return
        
        try:
            if filename.endswith('.xlsx'):
                self.export_excel(filename)
            elif filename.endswith('.pdf'):
                self.export_pdf(filename)
            elif filename.endswith('.html'):
                self.export_html(filename)
            elif filename.endswith('.json'):
                self.export_json(filename)
            elif filename.endswith('.csv'):
                self.export_csv(filename)
            elif filename.endswith('_executive.pdf'):
                self.export_executive_summary(filename)
            elif filename.endswith('.zip'):
                self.export_complete_package(filename)
            else:
                # Default to Excel
                base_name = filename.rsplit('.', 1)[0]
                self.export_excel(base_name + '.xlsx')
            
            messagebox.showinfo("Success", f"Report exported: {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def export_complete_package(self, filename):
        """Export complete report package with all formats."""
        import zipfile
        import tempfile
        import os
        
        base_name = filename.replace('.zip', '')
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Export all formats
            formats = {
                'excel': '.xlsx',
                'html': '.html',
                'json': '.json',
                'csv': '_summary.csv',
                'pdf': '_executive.pdf'
            }
            
            exported_files = []
            
            # Export Excel
            excel_file = os.path.join(temp_dir, f"{os.path.basename(base_name)}.xlsx")
            self.export_excel(excel_file)
            exported_files.append(excel_file)
            
            # Export HTML
            html_file = os.path.join(temp_dir, f"{os.path.basename(base_name)}.html")
            self.export_html(html_file)
            exported_files.append(html_file)
            
            # Export JSON
            json_file = os.path.join(temp_dir, f"{os.path.basename(base_name)}.json")
            self.export_json(json_file)
            exported_files.append(json_file)
            
            # Export CSV Summary
            csv_file = os.path.join(temp_dir, f"{os.path.basename(base_name)}_summary.csv")
            self.export_summary_csv(csv_file)
            exported_files.append(csv_file)
            
            # Export Executive Summary PDF
            pdf_file = os.path.join(temp_dir, f"{os.path.basename(base_name)}_executive.pdf")
            self.export_executive_summary(pdf_file)
            exported_files.append(pdf_file)
            
            # Create zip file
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file in exported_files:
                    if os.path.exists(file):
                        zipf.write(file, os.path.basename(file))
            
        finally:
            # Clean up temp files
            for file in exported_files:
                if os.path.exists(file):
                    os.remove(file)
            os.rmdir(temp_dir)
    
    def export_executive_summary(self, filename):
        """Export executive summary PDF report."""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.pdfgen import canvas
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            
            # Create PDF document
            doc = SimpleDocTemplate(filename, pagesize=letter)
            story = []
            
            # Styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2c3e50')
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=16,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.HexColor('#3498db')
            )
            
            subheading_style = ParagraphStyle(
                'CustomSubheading',
                parent=styles['Heading3'],
                fontSize=14,
                spaceBefore=15,
                spaceAfter=8,
                textColor=colors.HexColor('#7f8c8d')
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6
            )
            
            # Title
            story.append(Paragraph("Website Comprehensive Test Report", title_style))
            story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                                 ParagraphStyle('Date', parent=styles['Normal'], alignment=TA_CENTER)))
            story.append(Spacer(1, 20))
            
            # Executive Summary Section
            story.append(Paragraph("Executive Summary", heading_style))
            
            # Generate summary statistics
            summary_data = self.generate_executive_summary()
            
            for section in summary_data:
                story.append(Paragraph(section['title'], subheading_style))
                
                # Create table for metrics
                table_data = []
                for metric in section['metrics']:
                    table_data.append([metric['label'], metric['value'], metric['status']])
                
                if table_data:
                    table = Table(table_data, colWidths=[3*inch, 2*inch, 1*inch])
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ecf0f1')),
                        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')])
                    ]))
                    story.append(table)
                    story.append(Spacer(1, 10))
            
            # Key Findings Section
            story.append(Paragraph("Key Findings", heading_style))
            
            findings = self.generate_key_findings()
            for i, finding in enumerate(findings[:5], 1):  # Top 5 findings
                story.append(Paragraph(f"{i}. {finding}", normal_style))
            
            story.append(Spacer(1, 20))
            
            # Recommendations Section
            story.append(Paragraph("Recommendations", heading_style))
            
            recommendations = self.generate_recommendations()
            for i, rec in enumerate(recommendations[:5], 1):  # Top 5 recommendations
                story.append(Paragraph(f"{i}. {rec}", normal_style))
            
            story.append(Spacer(1, 20))
            
            # Overall Assessment
            story.append(Paragraph("Overall Assessment", heading_style))
            
            assessment = self.generate_overall_assessment()
            for para in assessment:
                story.append(Paragraph(para, normal_style))
            
            # Build PDF
            doc.build(story)
            
        except ImportError:
            # Fallback to HTML executive summary if reportlab not available
            self.export_html_executive_summary(filename)
    
    def generate_executive_summary(self):
        """Generate data for executive summary."""
        summary_sections = []
        
        # Overall Statistics
        overall_stats = {
            'title': 'Overall Statistics',
            'metrics': [
                {'label': 'Total URLs Tested', 'value': len(self.extracted_links), 'status': 'Info'},
                {'label': 'Total Test Cases', 'value': len(self.test_cases), 'status': 'Info'},
                {'label': 'Pass Rate', 'value': f"{(sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass') / len(self.test_cases) * 100):.1f}%", 
                 'status': 'Good' if (sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass') / len(self.test_cases)) > 0.8 else 'Needs Improvement'}
            ]
        }
        
        if self.performance_results:
            perf_score = self._extract_score(self.performance_results, "Performance Score")
            overall_stats['metrics'].append({
                'label': 'Performance Score',
                'value': f"{perf_score}%",
                'status': self._get_status_from_score(perf_score)
            })
        
        if self.accessibility_results:
            acc_score = self._extract_score(self.accessibility_results, "Accessibility Score")
            overall_stats['metrics'].append({
                'label': 'Accessibility Score',
                'value': f"{acc_score}%",
                'status': self._get_status_from_score(acc_score)
            })
        
        if self.seo_results:
            seo_score = self._extract_score(self.seo_results, "SEO Score")
            overall_stats['metrics'].append({
                'label': 'SEO Score',
                'value': f"{seo_score}%",
                'status': self._get_status_from_score(seo_score)
            })
        
        summary_sections.append(overall_stats)
        
        # Issue Breakdown
        if self.test_cases:
            severity_counts = {}
            for tc in self.test_cases:
                severity = tc.get('Severity', 'Medium')
                status = tc.get('Status', '')
                if status.lower() == 'fail':
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            issue_metrics = []
            for severity in ['Critical', 'High', 'Medium', 'Low']:
                count = severity_counts.get(severity, 0)
                issue_metrics.append({
                    'label': f'{severity} Issues',
                    'value': str(count),
                    'status': 'Critical' if severity == 'Critical' and count > 0 else 'High' if severity == 'High' and count > 0 else 'Medium' if severity == 'Medium' and count > 0 else 'Good'
                })
            
            summary_sections.append({
                'title': 'Issue Severity Breakdown',
                'metrics': issue_metrics
            })
        
        # Test Coverage
        enabled_tests = []
        if self.link_check_var.get(): enabled_tests.append("Link Status")
        if self.button_test_var.get(): enabled_tests.append("Button Testing")
        if self.spell_check_var.get(): enabled_tests.append("Spelling")
        if self.font_check_var.get(): enabled_tests.append("Font Analysis")
        if self.responsive_check_var.get(): enabled_tests.append("Responsiveness")
        if self.browser_check_var.get(): enabled_tests.append("Browser Compatibility")
        if self.seo_check_var.get(): enabled_tests.append("SEO Analysis")
        if self.performance_check_var.get(): enabled_tests.append("Performance")
        if self.accessibility_check_var.get(): enabled_tests.append("Accessibility")
        
        summary_sections.append({
            'title': 'Test Coverage',
            'metrics': [{
                'label': 'Tests Performed',
                'value': ', '.join(enabled_tests),
                'status': 'Good' if len(enabled_tests) > 3 else 'Limited'
            }]
        })
        
        return summary_sections
    
    def _extract_score(self, results, module_name):
        """Extract score from test results."""
        for result in results:
            if isinstance(result, dict) and result.get('Module') == module_name:
                actual = result.get('Actual Result', '')
                match = re.search(r'(\d+(\.\d+)?)%', actual)
                if match:
                    return float(match.group(1))
        return 0.0
    
    def _get_status_from_score(self, score):
        """Get status label from score."""
        if score >= 90:
            return 'Excellent'
        elif score >= 80:
            return 'Good'
        elif score >= 70:
            return 'Fair'
        elif score >= 60:
            return 'Needs Improvement'
        else:
            return 'Poor'
    
    def generate_key_findings(self):
        """Generate key findings from test results."""
        findings = []
        
        # Collect findings from failed test cases
        for tc in self.test_cases:
            if tc.get('Status', '').lower() == 'fail' and tc.get('Severity') in ['Critical', 'High']:
                finding = f"{tc.get('Module')}: {tc.get('Actual Result', '')[:100]}"
                if tc.get('Severity') == 'Critical':
                    finding = f"🔴 CRITICAL: {finding}"
                else:
                    finding = f"🟡 HIGH: {finding}"
                findings.append(finding)
        
        # Add performance findings
        if self.performance_results:
            perf_issues = [r for r in self.performance_results if isinstance(r, dict) and r.get('Status', '').lower() == 'fail']
            for issue in perf_issues[:3]:  # Top 3 performance issues
                findings.append(f"🏎️ Performance: {issue.get('Module', '')} - {issue.get('Actual Result', '')[:80]}")
        
        # Add accessibility findings
        if self.accessibility_results:
            acc_issues = [r for r in self.accessibility_results if isinstance(r, dict) and r.get('Status', '').lower() == 'fail']
            for issue in acc_issues[:3]:  # Top 3 accessibility issues
                findings.append(f"♿ Accessibility: {issue.get('Module', '')} - {issue.get('Actual Result', '')[:80]}")
        
        return findings
    
    def generate_recommendations(self):
        """Generate recommendations based on findings."""
        recommendations = []
        
        # Performance recommendations
        if self.performance_results:
            perf_fails = [r for r in self.performance_results if isinstance(r, dict) and r.get('Status', '').lower() == 'fail']
            if perf_fails:
                recommendations.append("Optimize page load performance by compressing images and minifying CSS/JS.")
                recommendations.append("Implement caching strategies for static assets.")
                recommendations.append("Consider using a CDN for global performance improvement.")
        
        # Accessibility recommendations
        if self.accessibility_results:
            acc_fails = [r for r in self.accessibility_results if isinstance(r, dict) and r.get('Status', '').lower() == 'fail']
            if acc_fails:
                recommendations.append("Improve accessibility by adding proper alt text to images.")
                recommendations.append("Ensure all interactive elements are keyboard accessible.")
                recommendations.append("Verify color contrast meets WCAG guidelines.")
        
        # SEO recommendations
        if self.seo_results:
            seo_fails = [r for r in self.seo_results if isinstance(r, dict) and r.get('Status', '').lower() == 'fail']
            if seo_fails:
                recommendations.append("Optimize meta tags and heading structure for better SEO.")
                recommendations.append("Ensure all pages have unique and descriptive title tags.")
                recommendations.append("Improve mobile friendliness for better search rankings.")
        
        # General recommendations
        if len(self.test_cases) > 0:
            fail_rate = sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Fail') / len(self.test_cases)
            if fail_rate > 0.3:
                recommendations.append("Address critical and high-severity issues as priority.")
                recommendations.append("Implement automated testing in development pipeline.")
                recommendations.append("Conduct regular accessibility and performance audits.")
        
        return recommendations
    
    def generate_overall_assessment(self):
        """Generate overall assessment paragraphs."""
        assessment = []
        
        total_tests = len(self.test_cases)
        if total_tests == 0:
            assessment.append("No tests were performed.")
            return assessment
        
        passed_tests = sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass')
        pass_rate = (passed_tests / total_tests) * 100
        
        # Overall pass rate assessment
        if pass_rate >= 90:
            assessment.append(f"The website shows excellent overall quality with a {pass_rate:.1f}% pass rate.")
            assessment.append("Most tests passed successfully, indicating good development practices.")
        elif pass_rate >= 80:
            assessment.append(f"The website shows good overall quality with a {pass_rate:.1f}% pass rate.")
            assessment.append("Some areas need improvement but overall performance is satisfactory.")
        elif pass_rate >= 70:
            assessment.append(f"The website shows average quality with a {pass_rate:.1f}% pass rate.")
            assessment.append("Several areas require attention to improve overall quality.")
        else:
            assessment.append(f"The website shows poor quality with only {pass_rate:.1f}% pass rate.")
            assessment.append("Significant improvements are needed across multiple areas.")
        
        # Critical issues assessment
        critical_issues = sum(1 for tc in self.test_cases if tc.get('Severity') == 'Critical' and tc['Case Pass/Fail'] == 'Fail')
        if critical_issues > 0:
            assessment.append(f"⚠️ There are {critical_issues} critical issues that must be addressed immediately.")
        
        # Performance assessment
        if self.performance_results:
            perf_score = self._extract_score(self.performance_results, "Performance Score")
            if perf_score >= 80:
                assessment.append("✅ Performance metrics are within acceptable ranges.")
            else:
                assessment.append("⚠️ Performance optimization is recommended to improve user experience.")
        
        # Accessibility assessment
        if self.accessibility_results:
            acc_score = self._extract_score(self.accessibility_results, "Accessibility Score")
            if acc_score >= 80:
                assessment.append("✅ Accessibility compliance is good, meeting most WCAG guidelines.")
            else:
                assessment.append("⚠️ Accessibility improvements are needed for better inclusivity.")
        
        # SEO assessment
        if self.seo_results:
            seo_score = self._extract_score(self.seo_results, "SEO Score")
            if seo_score >= 80:
                assessment.append("✅ SEO optimization is effective for search engine visibility.")
            else:
                assessment.append("⚠️ SEO improvements could enhance search engine rankings.")
        
        return assessment
    
    def export_summary_csv(self, filename):
        """Export summary CSV report."""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Website Comprehensive Test - Executive Summary'])
            writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'])
            writer.writerow([])
            
            # Overall Statistics
            writer.writerow(['Overall Statistics'])
            writer.writerow(['Metric', 'Value', 'Status'])
            
            overall_stats = self.generate_executive_summary()[0]['metrics']
            for metric in overall_stats:
                writer.writerow([metric['label'], metric['value'], metric['status']])
            
            writer.writerow([])
            
            # Issue Breakdown
            writer.writerow(['Issue Breakdown by Severity'])
            writer.writerow(['Severity', 'Count', 'Priority'])
            
            if self.test_cases:
                severity_counts = {}
                for tc in self.test_cases:
                    severity = tc.get('Severity', 'Medium')
                    status = tc.get('Status', '')
                    if status.lower() == 'fail':
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                for severity in ['Critical', 'High', 'Medium', 'Low']:
                    count = severity_counts.get(severity, 0)
                    priority = 'Immediate' if severity == 'Critical' and count > 0 else 'High' if severity == 'High' and count > 0 else 'Medium' if severity == 'Medium' and count > 0 else 'Low'
                    writer.writerow([severity, count, priority])
            
            writer.writerow([])
            
            # Key Recommendations
            writer.writerow(['Top Recommendations'])
            recommendations = self.generate_recommendations()
            for i, rec in enumerate(recommendations[:10], 1):
                writer.writerow([f'{i}.', rec])
    
    def export_html_executive_summary(self, filename):
        """Export HTML executive summary (fallback when PDF not available)."""
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Website Test - Executive Summary</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 20px; }
        .section { margin: 30px 0; }
        .section-title { color: #2c3e50; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }
        .metric { margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
        .metric-label { font-weight: bold; color: #34495e; }
        .metric-value { color: #2c3e50; }
        .status-good { color: #27ae60; }
        .status-warning { color: #f39c12; }
        .status-critical { color: #e74c3c; }
        table { width: 100%; border-collapse: collapse; margin: 15px 0; }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background-color: #3498db; color: white; }
        .recommendation { background: #e8f4fc; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Website Comprehensive Test Report</h1>
        <h3>Executive Summary</h3>
        <p>Generated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>
    
    <div class="section">
        <h2 class="section-title">Overall Assessment</h2>
        """ + ''.join(f'<p>{para}</p>' for para in self.generate_overall_assessment()) + """
    </div>
    
    <div class="section">
        <h2 class="section-title">Key Metrics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
                <th>Status</th>
            </tr>
"""
        
        # Add metrics from executive summary
        summary_data = self.generate_executive_summary()
        for section in summary_data:
            for metric in section['metrics']:
                status_class = 'status-good' if metric['status'] in ['Good', 'Excellent'] else 'status-warning' if metric['status'] in ['Fair', 'Needs Improvement'] else 'status-critical'
                html_content += f"""
            <tr>
                <td>{metric['label']}</td>
                <td>{metric['value']}</td>
                <td class="{status_class}">{metric['status']}</td>
            </tr>
"""
        
        html_content += """
        </table>
    </div>
    
    <div class="section">
        <h2 class="section-title">Top Recommendations</h2>
"""
        
        recommendations = self.generate_recommendations()
        for rec in recommendations[:10]:
            html_content += f"""
        <div class="recommendation">
            {rec}
        </div>
"""
        
        html_content += """
    </div>
    
    <div class="section">
        <h2 class="section-title">Next Steps</h2>
        <ol>
            <li>Review critical and high-priority issues</li>
            <li>Implement performance optimizations</li>
            <li>Address accessibility compliance gaps</li>
            <li>Optimize for search engines</li>
            <li>Schedule follow-up testing after improvements</li>
        </ol>
    </div>
    
    <div class="section">
        <p><em>This report was generated by Website Comprehensive Tester. For detailed results, refer to the complete test report.</em></p>
    </div>
</body>
</html>
"""
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    # ============================================================================
    # COMPLETE EXPORT FUNCTIONS (Updated with new features)
    # ============================================================================
    
    def export_excel(self, filename):
        """Export to Excel with multiple sheets including all new features."""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Existing sheets (keeping previous functionality)
            
            # Sheet 1: Test Cases
            if self.test_cases:
                test_cases_data = []
                for tc in self.test_cases:
                    row = {col: tc.get(col, '') for col in TEST_CASE_COLUMNS}
                    test_cases_data.append(row)
                
                test_cases_df = pd.DataFrame(test_cases_data)
                test_cases_df.to_excel(writer, sheet_name='Test Cases', index=False)
            
            # Sheet 2: Link Results
            if self.current_results:
                link_data = []
                for result in self.current_results:
                    clean_result = result.copy()
                    if 'display_text' in clean_result:
                        del clean_result['display_text']
                    link_data.append(clean_result)
                
                link_df = pd.DataFrame(link_data)
                link_df.to_excel(writer, sheet_name='Link Results', index=False)
            
            # Sheet 3: Performance Analysis (NEW)
            if self.performance_results:
                perf_data = []
                for perf_test_case in self.performance_results:
                    if isinstance(perf_test_case, dict):
                        perf_data.append({
                            'Page URL': perf_test_case.get('Test Links/Data', ''),
                            'Module': perf_test_case.get('Module', ''),
                            'Description': perf_test_case.get('Test Case Description', ''),
                            'Result': perf_test_case.get('Actual Result', '')[:200],
                            'Status': perf_test_case.get('Status', ''),
                            'Severity': perf_test_case.get('Severity', 'Medium'),
                            'Score Impact': self._get_perf_score_impact(perf_test_case.get('Actual Result', ''), perf_test_case.get('Status', '')),
                            'Recommendation': perf_test_case.get('Resolutions', ''),
                            'Comments': perf_test_case.get('Comments/Bug ID', '')
                        })
                
                if perf_data:
                    perf_df = pd.DataFrame(perf_data)
                    perf_df.to_excel(writer, sheet_name='Performance Analysis', index=False)
            
            # Sheet 4: Accessibility Testing (NEW)
            if self.accessibility_results:
                acc_data = []
                for acc_test_case in self.accessibility_results:
                    if isinstance(acc_test_case, dict):
                        acc_data.append({
                            'Page URL': acc_test_case.get('Test Links/Data', ''),
                            'Module': acc_test_case.get('Module', ''),
                            'Description': acc_test_case.get('Test Case Description', ''),
                            'Result': acc_test_case.get('Actual Result', '')[:200],
                            'Status': acc_test_case.get('Status', ''),
                            'Severity': acc_test_case.get('Severity', 'Medium'),
                            'WCAG Level': self._get_wcag_level(acc_test_case.get('Module', '')),
                            'Recommendation': acc_test_case.get('Resolutions', ''),
                            'Comments': acc_test_case.get('Comments/Bug ID', '')
                        })
                
                if acc_data:
                    acc_df = pd.DataFrame(acc_data)
                    acc_df.to_excel(writer, sheet_name='Accessibility Testing', index=False)
            
            # Sheet 5: Executive Summary (NEW)
            exec_summary = self.generate_executive_summary_data()
            exec_df = pd.DataFrame(exec_summary)
            exec_df.to_excel(writer, sheet_name='Executive Summary', index=False)
            
            # Sheet 6: Recommendations (NEW)
            recommendations = self.generate_detailed_recommendations()
            rec_df = pd.DataFrame(recommendations)
            rec_df.to_excel(writer, sheet_name='Recommendations', index=False)
            
            # Sheet 7: Dashboard Summary (NEW)
            dashboard_data = self.generate_dashboard_data()
            dashboard_df = pd.DataFrame(dashboard_data)
            dashboard_df.to_excel(writer, sheet_name='Dashboard', index=False)
            
            # Auto-adjust column widths
            workbook = writer.book
            for sheet_name in workbook.sheetnames:
                worksheet = workbook[sheet_name]
                
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            cell_value = str(cell.value) if cell.value else ""
                            line_count = cell_value.count('\n') + 1
                            max_line_length = max([len(line) for line in cell_value.split('\n')] + [0])
                            
                            if max_line_length > max_length:
                                max_length = max_line_length
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                worksheet.freeze_panes = 'A2'
    
    def _get_perf_score_impact(self, actual_result, status):
        """Get performance score impact."""
        actual_lower = str(actual_result).lower()
        status_lower = str(status).lower()
        
        if status_lower == 'fail':
            if 'slow' in actual_lower or 'exceed' in actual_lower or 'too many' in actual_lower:
                return 'High Negative Impact'
            else:
                return 'Medium Negative Impact'
        elif status_lower == 'pass':
            if 'fast' in actual_lower or 'optimal' in actual_lower or 'good' in actual_lower:
                return 'High Positive Impact'
            else:
                return 'Positive Impact'
        elif status_lower == 'warning':
            return 'Low Negative Impact'
        else:
            return 'Neutral Impact'
    
    def _get_wcag_level(self, module):
        """Get WCAG level for accessibility module."""
        module_lower = str(module).lower()
        
        if any(term in module_lower for term in ['color', 'contrast', 'audio', 'caption']):
            return 'WCAG 2.1 AA'
        elif any(term in module_lower for term in ['keyboard', 'focus', 'label', 'alt']):
            return 'WCAG 2.1 A'
        elif any(term in module_lower for term in ['aria', 'semantic', 'language']):
            return 'WCAG 2.1 AA'
        else:
            return 'WCAG 2.1 A'
    
    def generate_executive_summary_data(self):
        """Generate data for executive summary sheet."""
        data = []
        
        # Overall stats
        total_tests = len(self.test_cases)
        passed_tests = sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass')
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        data.append({'Category': 'Overall', 'Metric': 'Total Test Cases', 'Value': total_tests})
        data.append({'Category': 'Overall', 'Metric': 'Passed Tests', 'Value': passed_tests})
        data.append({'Category': 'Overall', 'Metric': 'Pass Rate', 'Value': f'{pass_rate:.1f}%'})
        
        # Performance score
        if self.performance_results:
            perf_score = self._extract_score(self.performance_results, "Performance Score")
            data.append({'Category': 'Performance', 'Metric': 'Overall Score', 'Value': f'{perf_score:.1f}%'})
        
        # Accessibility score
        if self.accessibility_results:
            acc_score = self._extract_score(self.accessibility_results, "Accessibility Score")
            data.append({'Category': 'Accessibility', 'Metric': 'Overall Score', 'Value': f'{acc_score:.1f}%'})
        
        # SEO score
        if self.seo_results:
            seo_score = self._extract_score(self.seo_results, "SEO Score")
            data.append({'Category': 'SEO', 'Metric': 'Overall Score', 'Value': f'{seo_score:.1f}%'})
        
        return data
    
    def generate_detailed_recommendations(self):
        """Generate detailed recommendations for Excel export."""
        recommendations = []
        
        # Performance recommendations
        if self.performance_results:
            perf_issues = [r for r in self.performance_results if isinstance(r, dict) and r.get('Status', '').lower() == 'fail']
            for issue in perf_issues:
                recommendations.append({
                    'Category': 'Performance',
                    'Issue': issue.get('Module', ''),
                    'Description': issue.get('Actual Result', '')[:150],
                    'Priority': 'High' if issue.get('Severity') in ['Critical', 'High'] else 'Medium',
                    'Action': issue.get('Resolutions', '')
                })
        
        # Accessibility recommendations
        if self.accessibility_results:
            acc_issues = [r for r in self.accessibility_results if isinstance(r, dict) and r.get('Status', '').lower() == 'fail']
            for issue in acc_issues:
                recommendations.append({
                    'Category': 'Accessibility',
                    'Issue': issue.get('Module', ''),
                    'Description': issue.get('Actual Result', '')[:150],
                    'Priority': 'High' if issue.get('Severity') in ['Critical', 'High'] else 'Medium',
                    'Action': issue.get('Resolutions', '')
                })
        
        # SEO recommendations
        if self.seo_results:
            seo_issues = [r for r in self.seo_results if isinstance(r, dict) and r.get('Status', '').lower() == 'fail']
            for issue in seo_issues:
                recommendations.append({
                    'Category': 'SEO',
                    'Issue': issue.get('Module', ''),
                    'Description': issue.get('Actual Result', '')[:150],
                    'Priority': 'High' if issue.get('Severity') in ['Critical', 'High'] else 'Medium',
                    'Action': issue.get('Resolutions', '')
                })
        
        return recommendations
    
    def generate_dashboard_data(self):
        """Generate dashboard data for quick overview."""
        data = []
        
        # Basic metrics
        data.append({'Metric': 'URLs Tested', 'Value': len(self.extracted_links)})
        data.append({'Metric': 'Total Test Cases', 'Value': len(self.test_cases)})
        
        if self.test_cases:
            passed = sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass')
            data.append({'Metric': 'Pass Rate', 'Value': f'{(passed/len(self.test_cases)*100):.1f}%'})
        
        # Performance metrics
        if self.performance_results:
            perf_score = self._extract_score(self.performance_results, "Performance Score")
            data.append({'Metric': 'Performance Score', 'Value': f'{perf_score:.1f}%'})
        
        # Accessibility metrics
        if self.accessibility_results:
            acc_score = self._extract_score(self.accessibility_results, "Accessibility Score")
            data.append({'Metric': 'Accessibility Score', 'Value': f'{acc_score:.1f}%'})
        
        # SEO metrics
        if self.seo_results:
            seo_score = self._extract_score(self.seo_results, "SEO Score")
            data.append({'Metric': 'SEO Score', 'Value': f'{seo_score:.1f}%'})
        
        return data
    
    # ============================================================================
    # UI UPDATE FUNCTIONS FOR ALL TABS
    # ============================================================================
    
    def update_results(self, result):
        """Update link status results text area."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, result + "\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)
    
    def update_buttons_results(self, result):
        """Update button test results text area."""
        self.buttons_text.config(state=tk.NORMAL)
        self.buttons_text.insert(tk.END, result)
        self.buttons_text.see(tk.END)
        self.buttons_text.config(state=tk.DISABLED)
    
    def update_spelling_results(self, result):
        """Update spelling check results text area."""
        self.spelling_text.config(state=tk.NORMAL)
        self.spelling_text.insert(tk.END, result)
        self.spelling_text.see(tk.END)
        self.spelling_text.config(state=tk.DISABLED)
    
    def update_font_results(self, result):
        """Update font analysis results text area."""
        self.fonts_text.config(state=tk.NORMAL)
        self.fonts_text.insert(tk.END, result)
        self.fonts_text.see(tk.END)
        self.fonts_text.config(state=tk.DISABLED)
    
    def update_responsive_results(self, result):
        """Update responsiveness check results text area."""
        self.responsive_text.config(state=tk.NORMAL)
        self.responsive_text.insert(tk.END, result)
        self.responsive_text.see(tk.END)
        self.responsive_text.config(state=tk.DISABLED)
    
    def update_browser_results(self, result):
        """Update browser compatibility results text area."""
        self.browser_text.config(state=tk.NORMAL)
        self.browser_text.insert(tk.END, result)
        self.browser_text.see(tk.END)
        self.browser_text.config(state=tk.DISABLED)
    
    def update_seo_results(self, result):
        """Update SEO analysis results text area."""
        self.seo_text.config(state=tk.NORMAL)
        self.seo_text.insert(tk.END, result)
        self.seo_text.see(tk.END)
        self.seo_text.config(state=tk.DISABLED)
    
    def update_test_cases_display(self):
        """Update the test cases treeview with all collected test cases."""
        # Clear existing items
        for item in self.testcases_tree.get_children():
            self.testcases_tree.delete(item)
        
        # Add test cases to treeview
        for test_case in self.test_cases:
            values = [test_case.get(col, '') for col in TEST_CASE_COLUMNS]
            self.testcases_tree.insert('', 'end', values=values)
        
        # Auto-size columns based on content
        for col in TEST_CASE_COLUMNS:
            self.testcases_tree.column(col, width=tk.font.Font().measure(col) + 20)
    
    def all_tests_complete(self):
        """Handle completion of all tests."""
        self.progress.stop()
        self.check_btn.config(state=tk.NORMAL)
        self.export_btn.config(state=tk.NORMAL)
        
        # Update stats
        self.update_stats()
        
        # Update test cases display
        self.update_test_cases_display()
        
        # Add completion messages to each tab
        completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        if self.link_check_var.get():
            summary = self.generate_summary()
            self.results_text.config(state=tk.NORMAL)
            self.results_text.insert(tk.END, "\n" + "="*100 + "\n" + summary + "\n")
            self.results_text.insert(tk.END, f"\n✅ Link testing completed at {completion_time}\n")
            self.results_text.config(state=tk.DISABLED)
        
        if self.button_test_var.get() and self.button_test_results:
            button_summary = self.generate_button_summary()
            self.buttons_text.config(state=tk.NORMAL)
            self.buttons_text.insert(tk.END, "\n" + "="*100 + "\n" + button_summary + "\n")
            self.buttons_text.insert(tk.END, f"\n✅ Button testing completed at {completion_time}\n")
            self.buttons_text.config(state=tk.DISABLED)
        
        # Add completion messages to other tabs
        tabs = [
            (self.spell_check_var, self.spelling_text, "Spelling check"),
            (self.font_check_var, self.fonts_text, "Font analysis"),
            (self.responsive_check_var, self.responsive_text, "Responsiveness check"),
            (self.browser_check_var, self.browser_text, "Browser compatibility check"),
            (self.seo_check_var, self.seo_text, "SEO analysis check"),
            (self.performance_check_var, self.performance_text, "Performance analysis"),
            (self.accessibility_check_var, self.accessibility_text, "Accessibility testing")
        ]
        
        for var, text_widget, test_name in tabs:
            if var.get():
                text_widget.config(state=tk.NORMAL)
                text_widget.insert(tk.END, f"\n✅ {test_name} completed at {completion_time}\n")
                text_widget.config(state=tk.DISABLED)
        
        # Show test cases summary
        if self.test_cases:
            self.root.after(0, lambda: messagebox.showinfo("Test Complete", 
                f"All tests completed!\n\n"
                f"Total Test Cases: {len(self.test_cases)}\n"
                f"Passed: {sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass')}\n"
                f"Failed: {sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Fail')}\n"
                f"See 'Test Cases' tab for details."))
    
    def update_stats(self):
        """Update statistics label."""
        total_links = len(self.current_results) if self.current_results else 0
        successful_links = len([r for r in self.current_results if r['status_category'] == 'Success']) if self.current_results else 0
        failed_links = total_links - successful_links
        
        stats_parts = [f"📊 Links: {total_links} total | {successful_links} OK | {failed_links} failed"]
        
        if self.button_test_var.get() and self.button_test_results:
            button_total = len(self.button_test_results)
            button_working = len([r for r in self.button_test_results if r.get('test_status_code') and 200 <= r['test_status_code'] < 400])
            stats_parts.append(f" | 🔘 Buttons: {button_total} tested | {button_working} working")
        
        if self.spell_check_var.get() and self.spelling_results:
            stats_parts.append(f" | ✍️ Spelling: {len(self.spelling_results)} test cases")
        
        if self.font_check_var.get() and self.font_results:
            stats_parts.append(f" | 🔤 Fonts: {len(self.font_results)} test cases")
        
        if self.responsive_check_var.get() and self.responsiveness_results:
            stats_parts.append(f" | 📱 Responsive: {len(self.responsiveness_results)} test cases")
        
        if self.browser_check_var.get() and self.browser_compatibility_results:
            stats_parts.append(f" | 🌐 Browser: {len(self.browser_compatibility_results)} test cases")
        
        if self.seo_check_var.get() and self.seo_results:
            stats_parts.append(f" | 🔍 SEO: {len(self.seo_results)} test cases")
        
        if self.performance_check_var.get() and self.performance_results:
            stats_parts.append(f" | 🏎️ Performance: {len(self.performance_results)} test cases")
        
        if self.accessibility_check_var.get() and self.accessibility_results:
            stats_parts.append(f" | ♿ Accessibility: {len(self.accessibility_results)} test cases")
        
        if self.test_cases:
            passed_cases = sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass')
            failed_cases = sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Fail')
            stats_parts.append(f" | 📋 Test Cases: {len(self.test_cases)} total | {passed_cases} passed | {failed_cases} failed")
        
        self.stats_label.config(text="".join(stats_parts))
    
    def generate_summary(self):
        """Generate summary of test results."""
        total = len(self.current_results)
        cat_counts = {}
        for r in self.current_results:
            cat = r['status_category']
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        
        summary_lines = ["📈 SCAN SUMMARY"]
        summary_lines.append(f"{'='*50}")
        input_method = "Manual Input" if self.option_var.get() == "manual" else f"Extracted from: {self.website_entry.get()}"
        summary_lines.append(f"Input Method: {input_method}")
        summary_lines.append(f"Total Links Tested: {total}")
        
        # Add enabled tests
        enabled_tests = []
        if self.link_check_var.get(): enabled_tests.append("Link Status")
        if self.button_test_var.get(): enabled_tests.append("Button Testing")
        if self.spell_check_var.get(): enabled_tests.append("Spelling Check")
        if self.font_check_var.get(): enabled_tests.append("Font Analysis")
        if self.responsive_check_var.get(): enabled_tests.append("Responsiveness")
        if self.browser_check_var.get(): enabled_tests.append("Browser Compatibility")
        if self.seo_check_var.get(): enabled_tests.append("SEO Analysis")
        if self.performance_check_var.get(): enabled_tests.append("Performance Analysis")
        if self.accessibility_check_var.get(): enabled_tests.append("Accessibility Testing")
        
        summary_lines.append(f"Tests Enabled: {', '.join(enabled_tests)}")
        summary_lines.append(f"Total Test Cases Generated: {len(self.test_cases)}")
        summary_lines.append(f"{'='*50}")
        
        for category, count in sorted(cat_counts.items()):
            emoji = {"Success": "✅", "Redirect": "🔄", "Client Error": "❌", 
                    "Server Error": "🚫", "Error": "⚠️"}.get(category, "📋")
            summary_lines.append(f"{emoji} {category}: {count}")
        
        summary_lines.append(f"Scan completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(summary_lines)
    
    # ============================================================================
    # CLEANUP FUNCTIONS
    # ============================================================================
    
    def clear_all(self):
        """Clear all data and reset UI."""
        # Clear all text areas
        text_widgets = [
            self.links_preview, self.results_text, self.buttons_text, 
            self.spelling_text, self.fonts_text, self.responsive_text, 
            self.browser_text, self.seo_text, self.performance_text, 
            self.accessibility_text
        ]
        
        for text_widget in text_widgets:
            text_widget.config(state=tk.NORMAL)
            text_widget.delete(1.0, tk.END)
            text_widget.config(state=tk.DISABLED)
        
        # Clear manual input
        self.urls_text.delete("1.0", tk.END)
        
        # Clear test cases tree
        for item in self.testcases_tree.get_children():
            self.testcases_tree.delete(item)
        
        # Clear all data
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
        self.test_cases = []
        self.test_case_counter = 1
        
        # Reset UI
        self.check_btn.config(state=tk.DISABLED)
        self.export_btn.config(state=tk.DISABLED)
        self.stats_label.config(text="")
        
        # Reset checkboxes to defaults
        self.link_check_var.set(True)
        self.button_test_var.set(True)
        self.spell_check_var.set(False)
        self.font_check_var.set(False)
        self.responsive_check_var.set(False)
        self.browser_check_var.set(False)
        self.seo_check_var.set(False)
        self.performance_check_var.set(False)
        self.accessibility_check_var.set(False)
    
    # ============================================================================
    # HELPER FUNCTIONS FOR DUPLICATE CHECKING
    # ============================================================================
    
    def is_duplicate_url(self, url, url_list):
        """Check if a URL is duplicate in the list."""
        url = url.lower().strip()
        
        if url.endswith('/'):
            url = url.rstrip('/')
        
        url_no_protocol = re.sub(r'^https?://', '', url)
        
        for existing_url in url_list:
            existing = existing_url.lower().strip()
            if existing.endswith('/'):
                existing = existing.rstrip('/')
            
            existing_no_protocol = re.sub(r'^https?://', '', existing)
            
            if (url == existing or 
                url_no_protocol == existing_no_protocol or
                url == existing.replace('https://', 'http://') or
                url.replace('https://', 'http://') == existing):
                return True
            
            if self.get_base_url(url) == self.get_base_url(existing):
                return True
        
        return False
    
    def get_base_url(self, url):
        """Get base URL without fragments, query parameters, and trailing slash."""
        try:
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            
            if base_url.endswith('/'):
                base_url = base_url.rstrip('/')
            
            return base_url
        except:
            return url.lower().strip()
    
    def remove_duplicate_urls(self, url_list):
        """Remove duplicate URLs from a list."""
        unique_urls = []
        seen_bases = set()
        
        for url in url_list:
            base_url = self.get_base_url(url)
            
            if base_url not in seen_bases:
                seen_bases.add(base_url)
                unique_urls.append(url)
        
        return unique_urls

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Install required packages
    required_packages = [
        ('textblob', 'textblob'),
        ('cssutils', 'cssutils'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('psutil', 'psutil')
    ]
    
    for package_name, install_name in required_packages:
        try:
            __import__(package_name)
        except ImportError:
            print(f"Installing {package_name}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', install_name])
    
    # Create and run the application
    root = tk.Tk()
    app = WebsiteLinkChecker(root)
    root.mainloop()