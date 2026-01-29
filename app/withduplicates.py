import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from urllib.parse import urlparse, urljoin, urldefrag
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
# from PIL import Image
import io

# Install required packages if not available
try:
    from textblob import TextBlob
except ImportError:
    subprocess.check_call(['pip', 'install', 'textblob'])
    from textblob import TextBlob

try:
    import cssutils
except ImportError:
    subprocess.check_call(['pip', 'install', 'cssutils'])
    import cssutils

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

# ============================================================================
# WEBSITE LINK CHECKER CLASS
# ============================================================================

class WebsiteLinkChecker:
    def __init__(self, root):
        """
        Initialize the Website Comprehensive Tester application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Website Comprehensive Tester")
        self.root.geometry("1200x900")
        self.root.resizable(True, True)
        
        # Initialize data storage
        self.current_results = []           # Link check results
        self.extracted_links = []           # Links extracted from website
        self.button_test_results = []       # Button test results
        self.spelling_results = []          # Spelling check results
        self.font_results = []              # Font analysis results
        self.responsiveness_results = []    # Responsiveness check results
        self.browser_compatibility_results = []  # Browser compatibility results
        self.test_cases = []                # Detailed test cases
        
        # Initialize test case counter
        self.test_case_counter = 1
        
        self.setup_ui()
        
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
        
        # Create checkboxes for different tests
        self.link_check_var = tk.BooleanVar(value=True)
        self.link_check_cb = ttk.Checkbutton(options_frame, text="🔗 Link Status Checking", 
                                            variable=self.link_check_var)
        self.link_check_cb.grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.button_test_var = tk.BooleanVar(value=True)
        self.button_test_cb = ttk.Checkbutton(options_frame, text="🔘 Button Functionality Testing", 
                                             variable=self.button_test_var)
        self.button_test_cb.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.spell_check_var = tk.BooleanVar(value=False)
        self.spell_check_cb = ttk.Checkbutton(options_frame, text="✍️ Spelling & Grammar Check", 
                                             variable=self.spell_check_var)
        self.spell_check_cb.grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.font_check_var = tk.BooleanVar(value=False)
        self.font_check_cb = ttk.Checkbutton(options_frame, text="🔤 Font Analysis", 
                                           variable=self.font_check_var)
        self.font_check_cb.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        self.responsive_check_var = tk.BooleanVar(value=False)
        self.responsive_check_cb = ttk.Checkbutton(options_frame, text="📱 Responsiveness Check", 
                                                  variable=self.responsive_check_var)
        self.responsive_check_cb.grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        
        self.browser_check_var = tk.BooleanVar(value=False)
        self.browser_check_cb = ttk.Checkbutton(options_frame, text="🌐 Cross-Browser Compatibility", 
                                               variable=self.browser_check_var)
        self.browser_check_cb.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
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
        
        # Tab 7: Test Cases (NEW)
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
        self.testcases_tree.column('Test ID', width=70)
        self.testcases_tree.column('Module', width=150)
        self.testcases_tree.column('Test Links/Data', width=200)
        self.testcases_tree.column('Test Case Description', width=250)
        self.testcases_tree.column('Pre-Conditions', width=150)
        self.testcases_tree.column('Test Steps', width=250)
        self.testcases_tree.column('Expected Result', width=200)
        self.testcases_tree.column('Actual Result', width=200)
        self.testcases_tree.column('Status', width=100)
        self.testcases_tree.column('Severity', width=100)
        self.testcases_tree.column('Case Pass/Fail', width=100)
        self.testcases_tree.column('Comments/Bug ID', width=150)
        self.testcases_tree.column('Resolutions', width=200)
        
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
        """Load URLs from manual input text area."""
        urls_text = self.urls_text.get("1.0", tk.END).strip()
        if not urls_text:
            messagebox.showwarning("Warning", "Please enter URLs in the text area")
            return
        
        # Parse URLs - one per line, filter empty lines
        raw_urls = urls_text.split('\n')
        self.extracted_links = []
        
        for url in raw_urls:
            url = url.strip()
            if url:
                # Add http:// if no protocol specified
                if not url.startswith(('http://', 'https://')):
                    url = 'http://' + url
                self.extracted_links.append(url)
        
        if not self.extracted_links:
            messagebox.showwarning("Warning", "No valid URLs found")
            return
        
        self.update_links_preview()
        self.check_btn.config(state=tk.NORMAL)
        messagebox.showinfo("Success", f"Loaded {len(self.extracted_links)} URLs")
    
    def extract_links(self):
        """Extract links from a website URL."""
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
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Extracted {len(self.extracted_links)} links from {website_url}"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to extract links: {str(e)}"))
                self.root.after(0, lambda: self.progress.stop())
        
        threading.Thread(target=extract_worker, daemon=True).start()
    
    def scrape_all_links(self, base_url, max_depth=2, max_links=1000):
        """Recursively scrape links from website."""
        visited = set()
        to_visit = [(base_url, 0)]
        all_links = set()
        
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
                        all_links.add(full_url)
                
                # Also extract paths from forms, etc.
                for form in soup.find_all('form', action=True):
                    action = form['action']
                    full_url = urljoin(url, action)
                    if self.is_relevant_link(full_url, base_url):
                        all_links.add(full_url)
                
                time.sleep(0.5)  # Be respectful
                
            except:
                continue
        
        # Convert to list and limit
        max_links_int = int(self.max_links_var.get())
        links_list = list(all_links)[:max_links_int]
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
        """Update the links preview text area."""
        self.links_preview.config(state=tk.NORMAL)
        self.links_preview.delete(1.0, tk.END)
        
        if not self.extracted_links:
            self.links_preview.insert(tk.END, "No links loaded.\n")
        else:
            preview_count = min(20, len(self.extracted_links))
            for i, link in enumerate(self.extracted_links[:preview_count]):
                self.links_preview.insert(tk.END, f"{i+1:3d}. {link}\n")
            
            if len(self.extracted_links) > preview_count:
                self.links_preview.insert(tk.END, f"\n... and {len(self.extracted_links) - preview_count} more\n")
                self.links_preview.insert(tk.END, f"Total links to test: {len(self.extracted_links)}\n")
        
        self.links_preview.config(state=tk.DISABLED)
    
    # ============================================================================
    # MAIN TEST EXECUTION
    # ============================================================================
    
    def run_selected_tests(self):
        """Run all selected tests based on checkbox selections."""
        if not self.extracted_links:
            messagebox.showwarning("Warning", "No links to test.")
            return
        
        # Reset all results
        self.current_results = []
        self.button_test_results = []
        self.spelling_results = []
        self.font_results = []
        self.responsiveness_results = []
        self.browser_compatibility_results = []
        self.test_cases = []
        self.test_case_counter = 1
        
        # Clear all text areas
        for text_widget in [self.results_text, self.buttons_text, self.spelling_text, 
                           self.fonts_text, self.responsive_text, self.browser_text]:
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
        """Test all extracted links for status."""
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_url = {executor.submit(self.check_status, url): url for url in self.extracted_links}
            
            for future in as_completed(future_to_url):
                result_display, result_structured, test_case = future.result()
                self.current_results.append(result_structured)
                if test_case:
                    self.test_cases.append(test_case)
                self.root.after(0, self.update_results, result_display)
    
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
    # CORE TESTING FUNCTIONS
    # ============================================================================
    
    def check_status(self, url):
        """Check HTTP status of a URL and create test case."""
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
    
    def test_buttons_on_page(self, url):
        """Test buttons on a working page and create test cases."""
        button_results = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all clickable elements that could be buttons
            button_elements = soup.find_all(['button', 'input', 'a'], 
                                           attrs={'type': ['submit', 'button']})
            
            # Also find elements with button-like classes
            button_like_elements = soup.find_all(class_=re.compile(r'btn|button|submit', re.I))
            
            all_elements = set(button_elements + button_like_elements)
            
            for element in all_elements:
                button_info = self.extract_button_info(element, url)
                if button_info:
                    # Test the button action
                    test_result = self.test_button_action(button_info, url)
                    if test_result:
                        button_results.append(test_result)
                        
        except Exception as e:
            pass
        
        return button_results
    
    def check_spelling_on_page(self, url):
        """Check spelling on a webpage and create test cases."""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get all text content
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            lines = text.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if len(line) > 10:  # Only check lines with meaningful content
                    blob = TextBlob(line)
                    # Check for spelling errors
                    corrected = blob.correct()
                    if str(blob) != str(corrected):
                        # Create test case for spelling error
                        test_case = self.create_test_case(
                            test_type="Spelling Check",
                            module="Content Validation",
                            test_data=url,
                            description=f"Check spelling on line {line_num} of webpage",
                            pre_conditions="1. Page loaded successfully\n2. Text content extracted",
                            test_steps=f"1. Extract text from webpage\n2. Analyze line {line_num}\n3. Check spelling",
                            expected_result="No spelling errors found",
                            actual_result=f"Spelling error found on line {line_num}: '{line[:50]}...' → Suggested: '{str(corrected)[:50]}...'",
                            status="Fail",
                            severity="Low",
                            comments=f"Original: {line[:100]}",
                            resolutions="Review and correct spelling in content"
                        )
                        test_cases.append(test_case)
            
            # If no spelling errors found, create a passing test case
            if not test_cases:
                test_case = self.create_test_case(
                    test_type="Spelling Check",
                    module="Content Validation",
                    test_data=url,
                    description="Check spelling on entire webpage",
                    pre_conditions="1. Page loaded successfully\n2. Text content extracted",
                    test_steps="1. Extract all text from webpage\n2. Analyze spelling\n3. Check grammar",
                    expected_result="No spelling errors found",
                    actual_result="No spelling errors detected on the webpage",
                    status="Pass",
                    severity="Low",
                    comments="Spelling check completed successfully",
                    resolutions=""
                )
                test_cases.append(test_case)
            
            return test_cases[:10]  # Return only first 10 test cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Spelling Check",
                module="Content Validation",
                test_data=url,
                description="Check spelling on webpage",
                pre_conditions="1. Page loaded successfully\n2. Text content extracted",
                test_steps="1. Extract text from webpage\n2. Analyze spelling\n3. Check grammar",
                expected_result="No spelling errors found",
                actual_result=f"Error during spelling check: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Spelling check failed due to error",
                resolutions="Check network connectivity and webpage accessibility"
            )
            return [error_test_case]
    
    def analyze_fonts_on_page(self, url):
        """Analyze fonts used on a webpage and create test cases."""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            font_declarations = []
            
            # Check inline styles
            for tag in soup.find_all(style=True):
                style = tag['style']
                if 'font-family' in style.lower():
                    match = re.search(r'font-family\s*:\s*([^;]+)', style, re.IGNORECASE)
                    if match:
                        font_family = match.group(1).strip()
                        font_declarations.append(f"Inline: {font_family}")
            
            # Check style tags
            for style_tag in soup.find_all('style'):
                css_content = style_tag.string
                if css_content:
                    font_matches = re.findall(r'font-family\s*:\s*([^;]+)', css_content, re.IGNORECASE)
                    for match in font_matches:
                        font_declarations.append(f"Internal CSS: {match.strip()}")
            
            # Check link tags for external CSS
            for link in soup.find_all('link', rel='stylesheet'):
                css_url = urljoin(url, link.get('href', ''))
                try:
                    css_response = requests.get(css_url, timeout=5, verify=False)
                    font_matches = re.findall(r'font-family\s*:\s*([^;]+)', css_response.text, re.IGNORECASE)
                    for match in font_matches:
                        font_declarations.append(f"External CSS: {match.strip()}")
                except:
                    pass
            
            # Create test cases based on findings
            if font_declarations:
                # Count font occurrences
                font_counts = {}
                for declaration in font_declarations:
                    font_name = declaration.split(':')[-1].strip()
                    if font_name:
                        font_counts[font_name] = font_counts.get(font_name, 0) + 1
                
                # Test case for font analysis summary
                summary_test_case = self.create_test_case(
                    test_type="Font Analysis",
                    module="Typography Analysis",
                    test_data=url,
                    description="Analyze font usage on webpage",
                    pre_conditions="1. Page loaded successfully\n2. CSS files accessible",
                    test_steps="1. Extract all font declarations\n2. Count font usage\n3. Check web-safe fonts",
                    expected_result="Web-safe fonts used appropriately",
                    actual_result=f"Found {len(font_declarations)} font declarations, {len(font_counts)} unique fonts",
                    status="Pass" if font_declarations else "Fail",
                    severity="Low",
                    comments=f"Fonts used: {', '.join(list(font_counts.keys())[:5])}" if font_counts else "No fonts detected",
                    resolutions=""
                )
                test_cases.append(summary_test_case)
                
                # Check for web-safe fonts
                web_safe_fonts = ['Arial', 'Helvetica', 'Times New Roman', 'Times', 'Courier New', 
                                 'Courier', 'Georgia', 'Palatino', 'Garamond', 'Bookman', 
                                 'Comic Sans MS', 'Trebuchet MS', 'Arial Black', 'Impact',
                                 'Verdana', 'Tahoma', 'Geneva']
                
                non_web_safe_found = []
                for font in font_counts.keys():
                    font_lower = font.lower()
                    is_web_safe = any(web_font.lower() in font_lower for web_font in web_safe_fonts)
                    if not is_web_safe and font_lower not in ['inherit', 'initial', 'unset']:
                        non_web_safe_found.append(font)
                
                if non_web_safe_found:
                    web_safe_test_case = self.create_test_case(
                        test_type="Font Analysis",
                        module="Web-Safe Font Check",
                        test_data=url,
                        description="Check if non-web-safe fonts are used",
                        pre_conditions="1. Font analysis completed\n2. Font list extracted",
                        test_steps="1. Check each font against web-safe font list\n2. Identify non-web-safe fonts",
                        expected_result="Only web-safe fonts should be used",
                        actual_result=f"Non-web-safe fonts detected: {', '.join(non_web_safe_found[:3])}",
                        status="Fail",
                        severity="Medium",
                        comments="Non-web-safe fonts may not display consistently across devices",
                        resolutions="Replace non-web-safe fonts with web-safe alternatives or use web fonts with fallbacks"
                    )
                    test_cases.append(web_safe_test_case)
                else:
                    web_safe_test_case = self.create_test_case(
                        test_type="Font Analysis",
                        module="Web-Safe Font Check",
                        test_data=url,
                        description="Check if non-web-safe fonts are used",
                        pre_conditions="1. Font analysis completed\n2. Font list extracted",
                        test_steps="1. Check each font against web-safe font list\n2. Identify non-web-safe fonts",
                        expected_result="Only web-safe fonts should be used",
                        actual_result="All fonts are web-safe",
                        status="Pass",
                        severity="Low",
                        comments="Fonts display consistently across devices",
                        resolutions=""
                    )
                    test_cases.append(web_safe_test_case)
            else:
                # No fonts found
                no_fonts_test_case = self.create_test_case(
                    test_type="Font Analysis",
                    module="Typography Analysis",
                    test_data=url,
                    description="Analyze font usage on webpage",
                    pre_conditions="1. Page loaded successfully\n2. CSS files accessible",
                    test_steps="1. Extract all font declarations\n2. Count font usage\n3. Check web-safe fonts",
                    expected_result="Font declarations should be present",
                    actual_result="No font declarations found on this page",
                    status="Fail",
                    severity="Low",
                    comments="Page may be using default browser fonts",
                    resolutions="Add explicit font declarations for better typography control"
                )
                test_cases.append(no_fonts_test_case)
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Font Analysis",
                module="Typography Analysis",
                test_data=url,
                description="Analyze font usage on webpage",
                pre_conditions="1. Page loaded successfully\n2. CSS files accessible",
                test_steps="1. Extract all font declarations\n2. Count font usage\n3. Check web-safe fonts",
                expected_result="Font analysis completed successfully",
                actual_result=f"Error during font analysis: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Font analysis failed due to error",
                resolutions="Check network connectivity and CSS file accessibility"
            )
            return [error_test_case]
    
    def check_responsiveness(self, url):
        """Check page responsiveness and create test cases."""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Check viewport meta tag
            viewport = soup.find('meta', attrs={'name': 'viewport'})
            
            viewport_test_case = self.create_test_case(
                test_type="Responsiveness Check",
                module="Viewport Meta Tag",
                test_data=url,
                description="Check for viewport meta tag",
                pre_conditions="1. Page loaded successfully\n2. HTML parsed",
                test_steps="1. Parse HTML\n2. Look for viewport meta tag\n3. Check viewport content",
                expected_result="Viewport meta tag with width=device-width should be present",
                actual_result=f"Viewport tag: {'Found' if viewport else 'Not found'}",
                status="Pass" if viewport else "Fail",
                severity="High" if not viewport else "Low",
                comments=f"Content: {viewport.get('content') if viewport else 'N/A'}",
                resolutions="Add <meta name='viewport' content='width=device-width, initial-scale=1'>" if not viewport else ""
            )
            test_cases.append(viewport_test_case)
            
            if viewport:
                content = viewport.get('content', '')
                width_check = 'width=device-width' in content
                scale_check = 'initial-scale=1' in content
                
                if not width_check or not scale_check:
                    viewport_detail_test_case = self.create_test_case(
                        test_type="Responsiveness Check",
                        module="Viewport Configuration",
                        test_data=url,
                        description="Check viewport meta tag configuration",
                        pre_conditions="1. Viewport meta tag exists\n2. HTML parsed",
                        test_steps="1. Check for width=device-width\n2. Check for initial-scale=1\n3. Verify viewport settings",
                        expected_result="Viewport should have width=device-width and initial-scale=1",
                        actual_result=f"width=device-width: {width_check}, initial-scale=1: {scale_check}",
                        status="Fail",
                        severity="Medium",
                        comments=f"Current viewport content: {content}",
                        resolutions="Update viewport meta tag to include width=device-width, initial-scale=1"
                    )
                    test_cases.append(viewport_detail_test_case)
            
            # 2. Check responsive images
            total_images = len(soup.find_all('img'))
            responsive_images = 0
            
            for img in soup.find_all('img'):
                # Check for responsive attributes
                is_responsive = False
                
                # Check inline styles
                style = img.get('style', '').lower()
                if 'max-width: 100%' in style or 'width: 100%' in style:
                    is_responsive = True
                
                # Check classes
                img_class = img.get('class', [])
                if any('responsive' in cls.lower() or 'img-fluid' in cls.lower() 
                       or 'fluid' in cls.lower() for cls in img_class):
                    is_responsive = True
                
                # Check for srcset attribute
                if img.get('srcset'):
                    is_responsive = True
                
                # Check for sizes attribute
                if img.get('sizes'):
                    is_responsive = True
                
                if is_responsive:
                    responsive_images += 1
            
            responsive_percent = (responsive_images / total_images * 100) if total_images > 0 else 0
            
            images_test_case = self.create_test_case(
                test_type="Responsiveness Check",
                module="Image Responsiveness",
                test_data=url,
                description="Check if images are responsive",
                pre_conditions="1. Page loaded successfully\n2. Images identified",
                test_steps="1. Count total images\n2. Check each image for responsive attributes\n3. Calculate responsive percentage",
                expected_result="All images should be responsive (100%)",
                actual_result=f"{responsive_images}/{total_images} images responsive ({responsive_percent:.1f}%)",
                status="Pass" if responsive_percent >= 70 else "Fail",
                severity="Medium" if responsive_percent < 70 else "Low",
                comments=f"Responsive images use max-width: 100%, img-fluid class, or srcset attribute",
                resolutions="Add responsive attributes to images: max-width: 100%, height: auto, or use srcset" if responsive_percent < 70 else ""
            )
            test_cases.append(images_test_case)
            
            # 3. Check for media queries
            media_query_count = 0
            
            # Check internal CSS
            for style_tag in soup.find_all('style'):
                if style_tag.string:
                    media_queries = re.findall(r'@media[^{]+\{', style_tag.string)
                    media_query_count += len(media_queries)
            
            media_test_case = self.create_test_case(
                test_type="Responsiveness Check",
                module="CSS Media Queries",
                test_data=url,
                description="Check for CSS media queries",
                pre_conditions="1. Page loaded successfully\n2. CSS content accessible",
                test_steps="1. Extract CSS content\n2. Count @media rules\n3. Check breakpoints",
                expected_result="Media queries should be present for responsive design",
                actual_result=f"Found {media_query_count} media query(ies)",
                status="Pass" if media_query_count > 0 else "Fail",
                severity="Medium" if media_query_count == 0 else "Low",
                comments="Media queries enable responsive layouts for different screen sizes",
                resolutions="Add CSS media queries for different screen sizes (mobile, tablet, desktop)" if media_query_count == 0 else ""
            )
            test_cases.append(media_test_case)
            
            # 4. Overall responsiveness assessment
            score_factors = []
            if viewport: score_factors.append(1)
            if responsive_percent >= 70: score_factors.append(1)
            if media_query_count > 0: score_factors.append(1)
            
            responsiveness_score = (len(score_factors) / 3) * 100
            
            overall_test_case = self.create_test_case(
                test_type="Responsiveness Check",
                module="Overall Assessment",
                test_data=url,
                description="Overall responsiveness assessment",
                pre_conditions="All responsiveness checks completed",
                test_steps="1. Evaluate viewport\n2. Assess image responsiveness\n3. Check media queries\n4. Calculate overall score",
                expected_result="Page should be fully responsive (score >= 80%)",
                actual_result=f"Responsiveness score: {responsiveness_score:.1f}%",
                status="Pass" if responsiveness_score >= 80 else "Fail",
                severity="High" if responsiveness_score < 60 else "Medium" if responsiveness_score < 80 else "Low",
                comments=f"Score based on: Viewport ({'Yes' if viewport else 'No'}), Images ({responsive_percent:.1f}%), Media Queries ({media_query_count})",
                resolutions="Improve viewport configuration, image responsiveness, and add media queries" if responsiveness_score < 80 else ""
            )
            test_cases.append(overall_test_case)
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Responsiveness Check",
                module="Responsiveness Analysis",
                test_data=url,
                description="Check webpage responsiveness",
                pre_conditions="1. Page loaded successfully\n2. HTML parsed",
                test_steps="1. Check viewport meta tag\n2. Analyze image responsiveness\n3. Check media queries",
                expected_result="Responsiveness analysis completed successfully",
                actual_result=f"Error during responsiveness check: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Responsiveness check failed due to error",
                resolutions="Check network connectivity and webpage accessibility"
            )
            return [error_test_case]
    
    def check_browser_compatibility(self, url):
        """Check cross-browser compatibility and create test cases."""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 1. Check HTML5 doctype
            html5_doctype = '<!DOCTYPE html>' in response.text[:1000]
            
            doctype_test_case = self.create_test_case(
                test_type="Browser Compatibility",
                module="HTML5 Doctype",
                test_data=url,
                description="Check for HTML5 doctype declaration",
                pre_conditions="1. Page loaded successfully\n2. HTML content accessible",
                test_steps="1. Check first 1000 characters of HTML\n2. Look for <!DOCTYPE html>",
                expected_result="HTML5 doctype should be present",
                actual_result=f"HTML5 doctype: {'Found' if html5_doctype else 'Not found'}",
                status="Pass" if html5_doctype else "Fail",
                severity="High" if not html5_doctype else "Low",
                comments="HTML5 doctype ensures modern browser compatibility",
                resolutions="Add <!DOCTYPE html> at the beginning of HTML document" if not html5_doctype else ""
            )
            test_cases.append(doctype_test_case)
            
            # 2. Check for deprecated elements
            deprecated_elements = {
                'applet': 'Use <object> instead',
                'basefont': 'Use CSS font properties',
                'center': 'Use CSS text-align',
                'dir': 'Use <ul>',
                'font': 'Use CSS font properties',
                'frame': 'Use CSS and modern layout',
                'frameset': 'Use modern layout techniques',
                'noframes': 'Obsolete with frames',
                'strike': 'Use <del> or CSS',
                'tt': 'Use CSS font-family',
                'u': 'Use CSS text-decoration',
                'xmp': 'Use <pre> or <code>'
            }
            
            found_deprecated = []
            for tag_name in deprecated_elements:
                if soup.find(tag_name):
                    found_deprecated.append(tag_name)
            
            deprecated_test_case = self.create_test_case(
                test_type="Browser Compatibility",
                module="Deprecated HTML Elements",
                test_data=url,
                description="Check for deprecated HTML elements",
                pre_conditions="1. Page loaded successfully\n2. HTML parsed",
                test_steps="1. Check for deprecated elements\n2. Identify usage\n3. Record findings",
                expected_result="No deprecated HTML elements should be used",
                actual_result=f"Found {len(found_deprecated)} deprecated element(s): {', '.join(found_deprecated[:5])}" if found_deprecated else "No deprecated elements found",
                status="Fail" if found_deprecated else "Pass",
                severity="Medium" if found_deprecated else "Low",
                comments="Deprecated elements may not work in modern browsers",
                resolutions="Replace deprecated elements with modern alternatives" if found_deprecated else ""
            )
            test_cases.append(deprecated_test_case)
            
            # 3. Check for vendor prefixes in CSS
            css3_features = ['transform', 'transition', 'animation', 'flex', 'grid', 'gradient']
            missing_prefixes = []
            
            # Check internal CSS
            for style_tag in soup.find_all('style'):
                css_content = style_tag.string or ''
                for feature in css3_features:
                    if feature in css_content.lower():
                        # Check for vendor prefixes
                        prefixes = ['-webkit-', '-moz-', '-ms-', '-o-']
                        has_prefix = any(f"{prefix}{feature}" in css_content.lower() for prefix in prefixes)
                        
                        if not has_prefix and feature not in ['grid', 'gradient']:  # grid and gradient often need prefixes
                            missing_prefixes.append(feature)
            
            if missing_prefixes:
                prefixes_test_case = self.create_test_case(
                    test_type="Browser Compatibility",
                    module="CSS Vendor Prefixes",
                    test_data=url,
                    description="Check for CSS vendor prefixes",
                    pre_conditions="1. Page loaded successfully\n2. CSS content accessible",
                    test_steps="1. Extract CSS content\n2. Check CSS3 features\n3. Verify vendor prefixes",
                    expected_result="CSS3 features should have vendor prefixes for cross-browser compatibility",
                    actual_result=f"Missing vendor prefixes for: {', '.join(set(missing_prefixes))}",
                    status="Fail",
                    severity="Medium",
                    comments="Vendor prefixes ensure CSS3 features work in all browsers",
                    resolutions="Add vendor prefixes (-webkit-, -moz-, -ms-, -o-) for CSS3 features"
                )
                test_cases.append(prefixes_test_case)
            
            # 4. Check for Flash content
            flash_elements = soup.find_all(['object', 'embed'], 
                                         attrs={'type': 'application/x-shockwave-flash'})
            
            if flash_elements:
                flash_test_case = self.create_test_case(
                    test_type="Browser Compatibility",
                    module="Flash Content",
                    test_data=url,
                    description="Check for Flash content",
                    pre_conditions="1. Page loaded successfully\n2. HTML parsed",
                    test_steps="1. Look for Flash objects and embeds\n2. Check MIME types",
                    expected_result="No Flash content should be present",
                    actual_result=f"Found {len(flash_elements)} Flash element(s)",
                    status="Fail",
                    severity="Critical",
                    comments="Flash is deprecated and not supported in modern browsers",
                    resolutions="Replace Flash content with HTML5 alternatives (Canvas, WebGL, or JavaScript animations)"
                )
                test_cases.append(flash_test_case)
            
            # 5. Overall compatibility assessment
            compatibility_issues = 0
            if not html5_doctype: compatibility_issues += 1
            if found_deprecated: compatibility_issues += 1
            if missing_prefixes: compatibility_issues += 1
            if flash_elements: compatibility_issues += 1
            
            compatibility_score = 100 - (compatibility_issues * 25)
            
            overall_test_case = self.create_test_case(
                test_type="Browser Compatibility",
                module="Overall Assessment",
                test_data=url,
                description="Overall browser compatibility assessment",
                pre_conditions="All browser compatibility checks completed",
                test_steps="1. Evaluate HTML5 compliance\n2. Check deprecated elements\n3. Verify CSS prefixes\n4. Assess technology usage",
                expected_result="High browser compatibility (score >= 80%)",
                actual_result=f"Browser compatibility score: {compatibility_score:.1f}%",
                status="Pass" if compatibility_score >= 80 else "Fail",
                severity="High" if compatibility_score < 60 else "Medium" if compatibility_score < 80 else "Low",
                comments=f"Issues found: {compatibility_issues}",
                resolutions="Fix identified issues to improve cross-browser compatibility" if compatibility_score < 80 else ""
            )
            test_cases.append(overall_test_case)
            
            return test_cases
            
        except Exception as e:
            error_test_case = self.create_test_case(
                test_type="Browser Compatibility",
                module="Browser Compatibility Analysis",
                test_data=url,
                description="Check cross-browser compatibility",
                pre_conditions="1. Page loaded successfully\n2. HTML parsed",
                test_steps="1. Check HTML5 doctype\n2. Look for deprecated elements\n3. Verify CSS prefixes\n4. Check for deprecated technologies",
                expected_result="Browser compatibility analysis completed successfully",
                actual_result=f"Error during browser compatibility check: {str(e)[:100]}",
                status="Fail",
                severity="Medium",
                comments="Browser compatibility check failed due to error",
                resolutions="Check network connectivity and webpage accessibility"
            )
            return [error_test_case]
    
    def extract_button_info(self, element, base_url):
        """Extract information about a button element."""
        info = {
            'page_url': base_url,
            'element_type': element.name,
            'text': self.get_button_text(element),
            'id': element.get('id', ''),
            'class': ' '.join(element.get('class', [])),
            'name': element.get('name', ''),
            'type': element.get('type', ''),
            'value': element.get('value', ''),
        }
        
        # Get the action URL
        if element.name == 'a':
            info['action_url'] = urljoin(base_url, element.get('href', ''))
            info['method'] = 'GET'
        elif element.name == 'form':
            info['action_url'] = urljoin(base_url, element.get('action', base_url))
            info['method'] = element.get('method', 'GET').upper()
        else:
            # For button/input inside form
            parent_form = element.find_parent('form')
            if parent_form:
                info['action_url'] = urljoin(base_url, parent_form.get('action', base_url))
                info['method'] = parent_form.get('method', 'GET').upper()
            else:
                info['action_url'] = base_url
                info['method'] = 'POST'
        
        info['action_url'] = urldefrag(info['action_url'])[0]  # Remove fragments
        
        return info
    
    def get_button_text(self, element):
        """Extract text from button element."""
        if element.name == 'input':
            return element.get('value', '')
        elif element.name == 'button':
            return element.get_text(strip=True)
        elif element.name == 'a':
            return element.get_text(strip=True)
        return ''
    
    def test_button_action(self, button_info, base_url):
        """Test if a button action works and create test case."""
        try:
            action_url = button_info['action_url']
            
            if not action_url or action_url == base_url:
                return None
            
            start_time = time.time()
            if button_info['method'] == 'POST':
                response = requests.post(action_url, timeout=8, allow_redirects=True, 
                                        data={'test': 'test'}, verify=False)
            else:
                response = requests.get(action_url, timeout=8, allow_redirects=True, verify=False)
            
            response_time = int((time.time() - start_time) * 1000)
            
            # Determine test result
            if 200 <= response.status_code < 400:
                test_status = "Pass"
                severity = "Low"
            else:
                test_status = "Fail"
                severity = "High"
            
            button_test_result = {
                **button_info,
                'test_status_code': response.status_code,
                'test_response_time': response_time,
                'test_final_url': response.url,
                'test_redirected': len(response.history) > 0,
                'test_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Create display text
            status_emoji = "✅" if test_status == "Pass" else "❌"
            button_text = button_info['text'][:50] + "..." if len(button_info['text']) > 50 else button_info['text']
            
            display_text = (f"{status_emoji} Button: '{button_text}' "
                          f"(Type: {button_info['element_type']}) "
                          f"→ {response.status_code} ({response_time}ms) "
                          f"Page: {base_url}\n"
                          f"   Action URL: {action_url} → Final: {response.url}\n")
            
            button_test_result['display_text'] = display_text
            
            # Create test case
            test_case = self.create_test_case(
                test_type="Button Functionality",
                module="Interactive Elements",
                test_data=f"Button: {button_text} on {base_url}",
                description=f"Test button functionality: {button_text}",
                pre_conditions=f"1. Page loaded: {base_url}\n2. Button element identified\n3. Button is clickable",
                test_steps=f"1. Identify button element\n2. Extract button properties\n3. Simulate button click/action\n4. Check response",
                expected_result=f"Button should respond with status code 200-399",
                actual_result=f"Status: {response.status_code}, Response Time: {response_time}ms, Redirected: {'Yes' if len(response.history) > 0 else 'No'}",
                status=test_status,
                severity=severity,
                comments=f"Button ID: {button_info['id']}, Classes: {button_info['class']}, Type: {button_info['type']}",
                resolutions="Check button configuration, form submission, or server-side processing" if test_status == "Fail" else ""
            )
            
            button_test_result['test_case'] = test_case
            return button_test_result
            
        except Exception as e:
            # Create error result
            button_test_result = {
                **button_info,
                'test_status_code': None,
                'test_response_time': 0,
                'test_final_url': button_info['action_url'],
                'test_redirected': False,
                'test_error': str(e)[:200],
                'test_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            button_text = button_info['text'][:50] + "..." if len(button_info['text']) > 50 else button_info['text']
            display_text = (f"❌ Button: '{button_text}' "
                          f"(Type: {button_info['element_type']}) "
                          f"→ ERROR: {str(e)[:50]}... "
                          f"Page: {base_url}\n"
                          f"   Action URL: {button_info['action_url']}\n")
            
            button_test_result['display_text'] = display_text
            
            # Create test case for error
            test_case = self.create_test_case(
                test_type="Button Functionality",
                module="Interactive Elements",
                test_data=f"Button: {button_text} on {base_url}",
                description=f"Test button functionality: {button_text}",
                pre_conditions=f"1. Page loaded: {base_url}\n2. Button element identified\n3. Button is clickable",
                test_steps=f"1. Identify button element\n2. Extract button properties\n3. Simulate button click/action\n4. Check response",
                expected_result=f"Button should respond with status code 200-399",
                actual_result=f"Request failed with error: {str(e)[:100]}",
                status="Fail",
                severity="High",
                comments=f"Button ID: {button_info['id']}, Action URL: {button_info['action_url']}",
                resolutions="1. Check if action URL is valid\n2. Verify network connectivity\n3. Check server-side processing"
            )
            
            button_test_result['test_case'] = test_case
            return button_test_result
    
    # ============================================================================
    # UI UPDATE FUNCTIONS
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
            (self.browser_check_var, self.browser_text, "Browser compatibility check")
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
        
        summary_lines.append(f"Tests Enabled: {', '.join(enabled_tests)}")
        summary_lines.append(f"Total Test Cases Generated: {len(self.test_cases)}")
        summary_lines.append(f"{'='*50}")
        
        for category, count in sorted(cat_counts.items()):
            emoji = {"Success": "✅", "Redirect": "🔄", "Client Error": "❌", 
                    "Server Error": "🚫", "Error": "⚠️"}.get(category, "📋")
            summary_lines.append(f"{emoji} {category}: {count}")
        
        summary_lines.append(f"Scan completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(summary_lines)
    
    def generate_button_summary(self):
        """Generate summary of button test results."""
        total = len(self.button_test_results)
        working = len([r for r in self.button_test_results if r.get('test_status_code') and 200 <= r['test_status_code'] < 400])
        errors = total - working
        
        summary_lines = ["🔘 BUTTON TEST SUMMARY"]
        summary_lines.append(f"{'='*50}")
        summary_lines.append(f"Total Buttons Found: {total}")
        summary_lines.append(f"Working Buttons: {working}")
        summary_lines.append(f"Error Buttons: {errors}")
        summary_lines.append(f"{'='*50}")
        
        # Group by element type
        type_counts = {}
        for r in self.button_test_results:
            elem_type = r.get('element_type', 'unknown')
            type_counts[elem_type] = type_counts.get(elem_type, 0) + 1
        
        for elem_type, count in sorted(type_counts.items()):
            summary_lines.append(f"{elem_type}: {count}")
        
        summary_lines.append(f"{'='*50}")
        summary_lines.append(f"Button test completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(summary_lines)
    
    # ============================================================================
    # EXPORT FUNCTIONS
    # ============================================================================
    
    # ============================================================================
    # EXPORT FUNCTIONS
    # ============================================================================
    
    def export_report(self):
        """Export test results to various formats."""
        if not any([self.current_results, self.button_test_results, self.spelling_results, 
                   self.font_results, self.responsiveness_results, self.browser_compatibility_results,
                   self.test_cases]):
            messagebox.showwarning("Warning", "No results to export.")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"website_comprehensive_test_{timestamp}"
        
        filetypes = [
            ("Excel Report", "*.xlsx"),
            ("CSV Report", "*.csv"),
            ("JSON Report", "*.json"),
            ("HTML Report", "*.html"),
            ("Test Cases Excel", "*_testcases.xlsx"),
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
            elif filename.endswith('.csv'):
                self.export_csv(filename)
            elif filename.endswith('.json'):
                self.export_json(filename)
            elif filename.endswith('.html'):
                self.export_html(filename)
            elif filename.endswith('_testcases.xlsx'):
                self.export_test_cases_excel(filename)
            else:
                base_name = filename.rsplit('.', 1)[0]
                self.export_excel(base_name + '.xlsx')
                messagebox.showinfo("Success", f"Exported Excel report!")
            
            messagebox.showinfo("Success", f"Report exported: {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export: {str(e)}")
    
    def export_excel(self, filename):
        """Export to Excel with multiple sheets including separate sheets for Font, Responsive, and Browser."""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Sheet 1: Test Cases
            if self.test_cases:
                # Convert test cases to DataFrame
                test_cases_data = []
                for tc in self.test_cases:
                    # Create a row with only the standard columns
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
            
            # Sheet 3: Button Results
            if self.button_test_results:
                button_data = []
                for result in self.button_test_results:
                    clean_result = result.copy()
                    if 'display_text' in clean_result:
                        del clean_result['display_text']
                    if 'test_case' in clean_result:
                        del clean_result['test_case']
                    
                    button_row = {
                        'Page URL': clean_result.get('page_url', ''),
                        'Element Type': clean_result.get('element_type', ''),
                        'Button Text': clean_result.get('text', '')[:100],
                        'Button ID': clean_result.get('id', ''),
                        'Button Classes': clean_result.get('class', ''),
                        'Button Name': clean_result.get('name', ''),
                        'Button Type': clean_result.get('type', ''),
                        'Button Value': clean_result.get('value', ''),
                        'Action URL': clean_result.get('action_url', ''),
                        'HTTP Method': clean_result.get('method', ''),
                        'Test Status Code': clean_result.get('test_status_code', ''),
                        'Response Time (ms)': clean_result.get('test_response_time', 0),
                        'Final URL': clean_result.get('test_final_url', ''),
                        'Was Redirected': 'Yes' if clean_result.get('test_redirected') else 'No',
                        'Test Error': clean_result.get('test_error', ''),
                        'Test Timestamp': clean_result.get('test_timestamp', '')
                    }
                    button_data.append(button_row)
                
                button_df = pd.DataFrame(button_data)
                button_df.to_excel(writer, sheet_name='Button Results', index=False)
            
            # Sheet 4: Font Analysis (NEW SEPARATE SHEET)
            if self.font_results:
                font_data = []
                for font_test_case in self.font_results:
                    # Extract detailed font information
                    if isinstance(font_test_case, dict):
                        url = font_test_case.get('url', '')
                        analysis = font_test_case.get('analysis', [])
                        
                        # Process each analysis line
                        for line in analysis:
                            if isinstance(line, str):
                                # Categorize the line
                                category = 'General'
                                if 'FONT ANALYSIS' in line:
                                    category = 'Header'
                                elif '📊' in line or 'Font Usage:' in line:
                                    category = 'Font Usage'
                                elif '✅' in line or 'Web-Safe Font Check:' in line:
                                    category = 'Web-Safe Check'
                                elif '⚠️' in line:
                                    category = 'Warning'
                                elif '❌' in line:
                                    category = 'Error'
                                elif '-' in line or '=' in line:
                                    category = 'Separator'
                                
                                font_data.append({
                                    'Page URL': url,
                                    'Category': category,
                                    'Finding': line.strip(),
                                    'Severity': self._get_severity_from_line(line),
                                    'Recommendation': self._get_font_recommendation(line)
                                })
                
                if font_data:
                    font_df = pd.DataFrame(font_data)
                    font_df.to_excel(writer, sheet_name='Font Analysis', index=False)
            
            # Sheet 5: Responsiveness Check (NEW SEPARATE SHEET)
            if self.responsiveness_results:
                responsive_data = []
                for responsive_test_case in self.responsiveness_results:
                    if isinstance(responsive_test_case, dict):
                        url = responsive_test_case.get('url', '')
                        issues = responsive_test_case.get('issues', [])
                        
                        for line in issues:
                            if isinstance(line, str):
                                # Categorize the line
                                category = 'General'
                                if 'RESPONSIVENESS CHECK' in line:
                                    category = 'Header'
                                elif '📊' in line or 'Image Analysis:' in line:
                                    category = 'Image Analysis'
                                elif '📏' in line or 'Fixed Width Elements:' in line:
                                    category = 'Fixed Width'
                                elif '🎯' in line or 'Media Queries:' in line:
                                    category = 'Media Queries'
                                elif '📈' in line or 'RESPONSIVENESS SCORE:' in line:
                                    category = 'Score'
                                elif '✅' in line:
                                    category = 'Success'
                                elif '⚠️' in line:
                                    category = 'Warning'
                                elif '❌' in line:
                                    category = 'Error'
                                elif '-' in line or '=' in line:
                                    category = 'Separator'
                                
                                responsive_data.append({
                                    'Page URL': url,
                                    'Category': category,
                                    'Check': line.strip(),
                                    'Status': self._get_status_from_line(line),
                                    'Score Impact': self._get_score_impact(line),
                                    'Recommendation': self._get_responsive_recommendation(line)
                                })
                
                if responsive_data:
                    responsive_df = pd.DataFrame(responsive_data)
                    responsive_df.to_excel(writer, sheet_name='Responsiveness', index=False)
            
            # Sheet 6: Browser Compatibility (NEW SEPARATE SHEET)
            if self.browser_compatibility_results:
                browser_data = []
                for browser_test_case in self.browser_compatibility_results:
                    if isinstance(browser_test_case, dict):
                        url = browser_test_case.get('url', '')
                        issues = browser_test_case.get('issues', [])
                        
                        for line in issues:
                            if isinstance(line, str):
                                # Categorize the line
                                category = 'General'
                                if 'BROWSER COMPATIBILITY' in line:
                                    category = 'Header'
                                elif '🚫' in line or 'Deprecated HTML Elements:' in line:
                                    category = 'Deprecated Elements'
                                elif '🎨' in line or 'CSS3 Features Analysis:' in line:
                                    category = 'CSS3 Features'
                                elif '💻' in line or 'JavaScript Analysis:' in line:
                                    category = 'JavaScript'
                                elif '🖼️' in line or 'IFRAMES DETECTED:' in line:
                                    category = 'Iframes'
                                elif '🔧' in line or 'Browser-Specific Code:' in line:
                                    category = 'Browser Specific'
                                elif '📊' in line or 'OVERALL COMPATIBILITY ASSESSMENT:' in line:
                                    category = 'Assessment'
                                elif '💡' in line or 'RECOMMENDATIONS:' in line:
                                    category = 'Recommendations'
                                elif '✅' in line:
                                    category = 'Success'
                                elif '⚠️' in line:
                                    category = 'Warning'
                                elif '❌' in line:
                                    category = 'Error'
                                elif '-' in line or '=' in line:
                                    category = 'Separator'
                                
                                browser_data.append({
                                    'Page URL': url,
                                    'Category': category,
                                    'Issue': line.strip(),
                                    'Severity': self._get_severity_from_line(line),
                                    'Browser Affected': self._get_browser_from_line(line),
                                    'Impact Level': self._get_browser_impact_level(line),
                                    'Recommendation': self._get_browser_recommendation(line)
                                })
                
                if browser_data:
                    browser_df = pd.DataFrame(browser_data)
                    browser_df.to_excel(writer, sheet_name='Browser Compatibility', index=False)
            
            # Sheet 7: Summary
            summary_data = self.generate_export_summary()
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
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
    
    def _get_font_recommendation(self, line):
        """Get font-specific recommendations."""
        line_str = str(line).lower()
        
        if 'no font' in line_str or 'no fonts' in line_str:
            return "Add explicit font declarations in CSS for better typography control"
        elif 'non-web-safe' in line_str:
            return "Replace with web-safe fonts or add font fallbacks"
        elif 'web-safe' in line_str and 'not found' in line_str:
            return "Use web-safe fonts like Arial, Helvetica, Verdana, Georgia"
        elif 'unique fonts' in line_str and int(re.search(r'(\d+)', line_str).group(1) if re.search(r'(\d+)', line_str) else 0) > 5:
            return "Reduce number of fonts for better performance and consistency"
        elif 'font-family' in line_str and 'system' in line_str:
            return "Specify font stack with web-safe alternatives"
        elif 'inline' in line_str and 'font' in line_str:
            return "Move inline font styles to external CSS for maintainability"
        
        return "Review font usage for consistency and performance"
    
    def _get_responsive_recommendation(self, line):
        """Get responsiveness-specific recommendations."""
        line_str = str(line).lower()
        
        if 'viewport' in line_str and 'not found' in line_str:
            return "Add: <meta name='viewport' content='width=device-width, initial-scale=1'>"
        elif 'image' in line_str and 'responsive' in line_str and ('0%' in line_str or 'low' in line_str):
            return "Add CSS: img { max-width: 100%; height: auto; } to all images"
        elif 'fixed width' in line_str and ('found' in line_str or 'many' in line_str):
            return "Replace fixed pixel widths with percentage or relative units (%, vw, rem)"
        elif 'media query' in line_str and 'not found' in line_str:
            return "Add CSS media queries for different screen sizes (mobile, tablet, desktop)"
        elif 'table' in line_str and 'mobile' in line_str:
            return "Make tables responsive with CSS overflow or convert to cards on mobile"
        elif 'responsive' in line_str and 'score' in line_str and any(x in line_str for x in ['poor', 'fair', 'low']):
            return "Implement responsive design principles: fluid grids, flexible images, media queries"
        
        return "Ensure all elements adapt to different screen sizes"
    
    def _get_browser_recommendation(self, line):
        """Get browser compatibility-specific recommendations."""
        line_str = str(line).lower()
        
        if 'doctype' in line_str and 'not found' in line_str:
            return "Add <!DOCTYPE html> at the beginning of HTML document"
        elif 'deprecated' in line_str:
            return "Replace deprecated HTML elements with modern alternatives"
        elif 'vendor prefix' in line_str or 'prefix' in line_str and 'missing' in line_str:
            return "Add vendor prefixes (-webkit-, -moz-, -ms-, -o-) for CSS3 features"
        elif 'flash' in line_str:
            return "Replace Flash content with HTML5 alternatives (Canvas, WebGL, JavaScript)"
        elif 'silverlight' in line_str:
            return "Replace Silverlight with modern web technologies"
        elif 'es6' in line_str or 'javascript' in line_str and 'older browsers' in line_str:
            return "Use Babel to transpile ES6+ code for older browsers"
        elif 'iframe' in line_str and 'issues' in line_str:
            return "Test iframes in multiple browsers, handle cross-origin policies"
        elif 'browser-specific' in line_str:
            return "Use standardized code and feature detection instead of browser sniffing"
        
        return "Test in multiple browsers (Chrome, Firefox, Safari, Edge) and fix compatibility issues"
    
    def _get_score_impact(self, line):
        """Get impact on responsiveness score."""
        line_str = str(line).lower()
        
        if any(x in line_str for x in ['❌', 'not found', 'missing', 'error']):
            return 'High Negative Impact'
        elif any(x in line_str for x in ['⚠️', 'warning', 'few', 'some', 'may']):
            return 'Moderate Negative Impact'
        elif any(x in line_str for x in ['✅', 'found', 'good', 'excellent', '✓']):
            return 'Positive Impact'
        elif any(x in line_str for x in ['no', 'none', 'zero']):
            return 'Neutral'
        
        return 'Low Impact'
    
    def _get_browser_impact_level(self, line):
        """Get impact level on browser compatibility."""
        line_str = str(line).lower()
        
        if any(x in line_str for x in ['❌', 'critical', 'flash', 'silverlight', 'doctype missing']):
            return 'Critical - Will break in modern browsers'
        elif any(x in line_str for x in ['deprecated', 'vendor prefix', 'es6', 'iframe']):
            return 'High - May not work in some browsers'
        elif any(x in line_str for x in ['⚠️', 'warning', 'browser-specific']):
            return 'Medium - May have rendering differences'
        elif any(x in line_str for x in ['✅', 'compatible', 'supported', 'standard']):
            return 'Low - Well supported'
        
        return 'Unknown - Needs testing'
    
    def export_csv(self, filename):
        """Export results to CSV format with separate files for each analysis type."""
        # Export test cases
        if self.test_cases:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                # Convert test cases to list of dictionaries
                test_cases_data = []
                for tc in self.test_cases:
                    row = {col: tc.get(col, '') for col in TEST_CASE_COLUMNS}
                    test_cases_data.append(row)
                
                writer = csv.DictWriter(f, fieldnames=TEST_CASE_COLUMNS)
                writer.writeheader()
                writer.writerows(test_cases_data)
        
        # Export other results to separate CSV files
        export_configs = [
            (self.current_results, '_links.csv', [
                ('URL', 'url'),
                ('Status Code', 'status_code'),
                ('Status Text', 'status_text'),
                ('Category', 'status_category'),
                ('Response Time (ms)', 'response_time_ms'),
                ('Timestamp', 'timestamp'),
                ('Final URL', 'final_url')
            ]),
            
            (self.button_test_results, '_buttons.csv', [
                ('Page URL', 'page_url'),
                ('Element Type', 'element_type'),
                ('Button Text', 'text'),
                ('Button ID', 'id'),
                ('Button Classes', 'class'),
                ('Button Name', 'name'),
                ('Button Type', 'type'),
                ('Button Value', 'value'),
                ('Action URL', 'action_url'),
                ('HTTP Method', 'method'),
                ('Test Status Code', 'test_status_code'),
                ('Response Time (ms)', 'test_response_time'),
                ('Final URL', 'test_final_url'),
                ('Was Redirected', lambda x: 'Yes' if x.get('test_redirected') else 'No'),
                ('Test Error', 'test_error'),
                ('Test Timestamp', 'test_timestamp')
            ]),
            
            (self.font_results, '_font_analysis.csv', [
                ('Page URL', lambda x: x.get('url', '') if isinstance(x, dict) else ''),
                ('Analysis Type', 'Font Analysis'),
                ('Category', lambda x: self._categorize_font_line(x) if isinstance(x, str) else 'General'),
                ('Finding', lambda x: str(x)[:500]),
                ('Severity', lambda x: self._get_severity_from_line(str(x))),
                ('Recommendation', lambda x: self._get_font_recommendation(str(x)))
            ]),
            
            (self.responsiveness_results, '_responsiveness.csv', [
                ('Page URL', lambda x: x.get('url', '') if isinstance(x, dict) else ''),
                ('Analysis Type', 'Responsiveness Check'),
                ('Category', lambda x: self._categorize_responsive_line(x) if isinstance(x, str) else 'General'),
                ('Check', lambda x: str(x)[:500]),
                ('Status', lambda x: self._get_status_from_line(str(x))),
                ('Score Impact', lambda x: self._get_score_impact(str(x))),
                ('Recommendation', lambda x: self._get_responsive_recommendation(str(x)))
            ]),
            
            (self.browser_compatibility_results, '_browser_compatibility.csv', [
                ('Page URL', lambda x: x.get('url', '') if isinstance(x, dict) else ''),
                ('Analysis Type', 'Browser Compatibility'),
                ('Category', lambda x: self._categorize_browser_line(x) if isinstance(x, str) else 'General'),
                ('Issue', lambda x: str(x)[:500]),
                ('Severity', lambda x: self._get_severity_from_line(str(x))),
                ('Browser Affected', lambda x: self._get_browser_from_line(str(x))),
                ('Impact Level', lambda x: self._get_browser_impact_level(str(x))),
                ('Recommendation', lambda x: self._get_browser_recommendation(str(x)))
            ])
        ]
        
        for data, suffix, field_configs in export_configs:
            if data:
                export_filename = filename.replace('.csv', suffix)
                with open(export_filename, 'w', newline='', encoding='utf-8') as f:
                    headers = [header for header, _ in field_configs]
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    
                    for item in data:
                        row = {}
                        for header, extractor in field_configs:
                            if callable(extractor):
                                row[header] = extractor(item)
                            else:
                                row[header] = item.get(extractor, '') if isinstance(item, dict) else ''
                        writer.writerow(row)
    
    def _categorize_font_line(self, line):
        """Categorize font analysis lines."""
        line_str = str(line)
        if 'FONT ANALYSIS' in line_str:
            return 'Header'
        elif '📊' in line_str:
            return 'Statistics'
        elif '✅' in line_str:
            return 'Success'
        elif '⚠️' in line_str:
            return 'Warning'
        elif '❌' in line_str:
            return 'Error'
        elif '-' in line_str or '=' in line_str:
            return 'Separator'
        elif 'web-safe' in line_str.lower():
            return 'Web-Safe Check'
        elif 'font' in line_str.lower() and 'usage' in line_str.lower():
            return 'Font Usage'
        return 'General'
    
    def _categorize_responsive_line(self, line):
        """Categorize responsiveness analysis lines."""
        line_str = str(line)
        if 'RESPONSIVENESS CHECK' in line_str:
            return 'Header'
        elif '📊' in line_str:
            return 'Image Analysis'
        elif '📏' in line_str:
            return 'Fixed Width'
        elif '🎯' in line_str:
            return 'Media Queries'
        elif '📈' in line_str:
            return 'Score'
        elif '✅' in line_str:
            return 'Success'
        elif '⚠️' in line_str:
            return 'Warning'
        elif '❌' in line_str:
            return 'Error'
        elif '-' in line_str or '=' in line_str:
            return 'Separator'
        elif 'viewport' in line_str.lower():
            return 'Viewport'
        elif 'table' in line_str.lower():
            return 'Tables'
        return 'General'
    
    def _categorize_browser_line(self, line):
        """Categorize browser compatibility analysis lines."""
        line_str = str(line)
        if 'BROWSER COMPATIBILITY' in line_str:
            return 'Header'
        elif '🚫' in line_str:
            return 'Deprecated Elements'
        elif '🎨' in line_str:
            return 'CSS3 Features'
        elif '💻' in line_str:
            return 'JavaScript'
        elif '🖼️' in line_str:
            return 'Iframes'
        elif '🔧' in line_str:
            return 'Browser Specific'
        elif '📊' in line_str:
            return 'Assessment'
        elif '💡' in line_str:
            return 'Recommendations'
        elif '✅' in line_str:
            return 'Success'
        elif '⚠️' in line_str:
            return 'Warning'
        elif '❌' in line_str:
            return 'Error'
        elif '-' in line_str or '=' in line_str:
            return 'Separator'
        elif 'flash' in line_str.lower():
            return 'Flash Content'
        elif 'silverlight' in line_str.lower():
            return 'Silverlight'
        return 'General'
     
    def export_test_cases_excel(self, filename):
        """Export only test cases to Excel."""
        if not self.test_cases:
            messagebox.showwarning("Warning", "No test cases to export.")
            return
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Convert test cases to DataFrame
            test_cases_data = []
            for tc in self.test_cases:
                row = {col: tc.get(col, '') for col in TEST_CASE_COLUMNS}
                test_cases_data.append(row)
            
            test_cases_df = pd.DataFrame(test_cases_data)
            test_cases_df.to_excel(writer, sheet_name='Test Cases', index=False)
            
            # Add summary sheet
            summary_data = {
                'Metric': [
                    'Total Test Cases',
                    'Passed Test Cases',
                    'Failed Test Cases',
                    'Critical Severity',
                    'High Severity',
                    'Medium Severity',
                    'Low Severity',
                    'Info Severity',
                    'Export Timestamp'
                ],
                'Value': [
                    len(self.test_cases),
                    sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass'),
                    sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Fail'),
                    sum(1 for tc in self.test_cases if tc['Severity'] == 'Critical'),
                    sum(1 for tc in self.test_cases if tc['Severity'] == 'High'),
                    sum(1 for tc in self.test_cases if tc['Severity'] == 'Medium'),
                    sum(1 for tc in self.test_cases if tc['Severity'] == 'Low'),
                    sum(1 for tc in self.test_cases if tc['Severity'] == 'Info'),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
    
    def generate_export_summary(self):
        """Generate summary data for export."""
        summary_data = {
            'Category': [],
            'Metric': [],
            'Value': [],
            'Status': [],
            'Notes': []
        }
        
        # Test Cases Summary
        total_cases = len(self.test_cases)
        passed_cases = sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass')
        failed_cases = total_cases - passed_cases
        
        summary_data['Category'].extend(['Test Cases', 'Test Cases', 'Test Cases'])
        summary_data['Metric'].extend(['Total Test Cases', 'Passed Test Cases', 'Failed Test Cases'])
        summary_data['Value'].extend([total_cases, passed_cases, failed_cases])
        summary_data['Status'].extend([
            'Info',
            'Good' if passed_cases > 0 else 'Warning',
            'Warning' if failed_cases > 0 else 'Good'
        ])
        summary_data['Notes'].extend([
            f'Total test cases generated',
            f'{passed_cases} test cases passed',
            f'{failed_cases} test cases failed'
        ])
        
        # Link Statistics
        total_links = len(self.current_results)
        successful_links = len([r for r in self.current_results if r['status_category'] == 'Success'])
        failed_links = total_links - successful_links
        
        summary_data['Category'].extend(['Link Testing', 'Link Testing', 'Link Testing'])
        summary_data['Metric'].extend(['Total Links Tested', 'Successful Links', 'Failed Links'])
        summary_data['Value'].extend([total_links, successful_links, failed_links])
        summary_data['Status'].extend([
            'Info',
            'Good' if successful_links > 0 else 'Warning',
            'Warning' if failed_links > 0 else 'Good'
        ])
        summary_data['Notes'].extend([
            f'Total URLs checked for status',
            f'{successful_links} links returned 2xx/3xx status codes',
            f'{failed_links} links returned 4xx/5xx status codes or errors'
        ])
        
        # Button Testing
        if self.button_test_var.get():
            button_total = len(self.button_test_results)
            button_working = len([r for r in self.button_test_results if r.get('test_status_code') and 200 <= r['test_status_code'] < 400])
            button_failed = button_total - button_working
            
            summary_data['Category'].extend(['Button Testing', 'Button Testing', 'Button Testing'])
            summary_data['Metric'].extend(['Total Buttons Tested', 'Working Buttons', 'Failed Buttons'])
            summary_data['Value'].extend([button_total, button_working, button_failed])
            summary_data['Status'].extend([
                'Info',
                'Good' if button_working > 0 else 'Warning',
                'Warning' if button_failed > 0 else 'Good'
            ])
            summary_data['Notes'].extend([
                f'Total clickable elements tested',
                f'{button_working} buttons returned successful responses',
                f'{button_failed} buttons failed or returned errors'
            ])
        
        # General Info
        summary_data['Category'].extend(['General', 'General', 'General'])
        summary_data['Metric'].extend(['Scan Timestamp', 'Input Method', 'Tests Enabled'])
        summary_data['Value'].extend([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "Manual Input" if self.option_var.get() == "manual" else f"Extracted from: {self.website_entry.get()}",
            self._get_enabled_tests_string()
        ])
        summary_data['Status'].extend(['Info', 'Info', 'Info'])
        summary_data['Notes'].extend([
            'Date and time when scan was completed',
            'How URLs were provided for testing',
            'List of tests that were enabled during this scan'
        ])
        
        return summary_data
    
    def _get_enabled_tests_string(self):
        """Get string of enabled tests."""
        enabled = []
        if self.link_check_var.get(): enabled.append("Link Status")
        if self.button_test_var.get(): enabled.append("Button Testing")
        if self.spell_check_var.get(): enabled.append("Spelling Check")
        if self.font_check_var.get(): enabled.append("Font Analysis")
        if self.responsive_check_var.get(): enabled.append("Responsiveness")
        if self.browser_check_var.get(): enabled.append("Browser Compatibility")
        return ", ".join(enabled) if enabled else "None"
    
    def export_csv(self, filename):
        """Export results to CSV format."""
        # Export test cases
        if self.test_cases:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                # Convert test cases to list of dictionaries
                test_cases_data = []
                for tc in self.test_cases:
                    row = {col: tc.get(col, '') for col in TEST_CASE_COLUMNS}
                    test_cases_data.append(row)
                
                writer = csv.DictWriter(f, fieldnames=TEST_CASE_COLUMNS)
                writer.writeheader()
                writer.writerows(test_cases_data)
        
        # Export other results to separate CSV files
        export_configs = [
            (self.current_results, '_links.csv', [
                ('URL', 'url'),
                ('Status Code', 'status_code'),
                ('Status Text', 'status_text'),
                ('Category', 'status_category'),
                ('Response Time (ms)', 'response_time_ms'),
                ('Timestamp', 'timestamp'),
                ('Final URL', 'final_url')
            ]),
            
            (self.button_test_results, '_buttons.csv', [
                ('Page URL', 'page_url'),
                ('Element Type', 'element_type'),
                ('Button Text', 'text'),
                ('Button ID', 'id'),
                ('Button Classes', 'class'),
                ('Button Name', 'name'),
                ('Button Type', 'type'),
                ('Button Value', 'value'),
                ('Action URL', 'action_url'),
                ('HTTP Method', 'method'),
                ('Test Status Code', 'test_status_code'),
                ('Response Time (ms)', 'test_response_time'),
                ('Final URL', 'test_final_url'),
                ('Was Redirected', lambda x: 'Yes' if x.get('test_redirected') else 'No'),
                ('Test Error', 'test_error'),
                ('Test Timestamp', 'test_timestamp')
            ])
        ]
        
        for data, suffix, field_configs in export_configs:
            if data:
                export_filename = filename.replace('.csv', suffix)
                with open(export_filename, 'w', newline='', encoding='utf-8') as f:
                    headers = [header for header, _ in field_configs]
                    writer = csv.DictWriter(f, fieldnames=headers)
                    writer.writeheader()
                    
                    for item in data:
                        row = {}
                        for header, extractor in field_configs:
                            if callable(extractor):
                                row[header] = extractor(item)
                            else:
                                row[header] = item.get(extractor, '') if isinstance(item, dict) else ''
                        writer.writerow(row)
    
    def export_json(self, filename):
        """Export results to JSON format."""
        # Clean data by removing display_text fields
        clean_link_results = []
        for result in self.current_results:
            clean_result = result.copy()
            if 'display_text' in clean_result:
                del clean_result['display_text']
            clean_link_results.append(clean_result)
        
        clean_button_results = []
        for result in self.button_test_results:
            clean_result = result.copy()
            if 'display_text' in clean_result:
                del clean_result['display_text']
            if 'test_case' in clean_result:
                del clean_result['test_case']
            clean_button_results.append(clean_result)
        
        # Prepare test cases for export
        export_test_cases = []
        for tc in self.test_cases:
            export_tc = {col: tc.get(col, '') for col in TEST_CASE_COLUMNS}
            export_test_cases.append(export_tc)
        
        export_data = {
            'test_cases': export_test_cases,
            'link_results': clean_link_results,
            'button_results': clean_button_results,
            'spelling_results': self.spelling_results,
            'font_results': self.font_results,
            'responsiveness_results': self.responsiveness_results,
            'browser_compatibility_results': self.browser_compatibility_results,
            'summary': {
                'total_test_cases': len(self.test_cases),
                'passed_test_cases': sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Pass'),
                'failed_test_cases': sum(1 for tc in self.test_cases if tc['Case Pass/Fail'] == 'Fail'),
                'total_links': len(clean_link_results),
                'total_buttons': len(clean_button_results),
                'spelling_issues': len(self.spelling_results),
                'font_analyses': len(self.font_results),
                'responsiveness_checks': len(self.responsiveness_results),
                'browser_checks': len(self.browser_compatibility_results),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def export_html(self, filename):
        """Export results to HTML format."""
        html_content = self.generate_html_report()
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def generate_html_report(self):
        """Generate HTML report with separate sections for Font, Responsive, and Browser."""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Website Comprehensive Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .success { background-color: #d4edda; color: #155724; }
        .warning { background-color: #fff3cd; color: #856404; }
        .error { background-color: #f8d7da; color: #721c24; }
        .critical { background-color: #721c24; color: white; }
        .high { background-color: #dc3545; color: white; }
        .medium { background-color: #fd7e14; color: white; }
        .low { background-color: #ffc107; color: #212529; }
        .info { background-color: #d1ecf1; color: #0c5460; }
        .summary { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
        .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 10px 16px; transition: 0.3s; }
        .tab button:hover { background-color: #ddd; }
        .tab button.active { background-color: #ccc; }
        .tabcontent { display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }
        .test-case { margin: 10px 0; padding: 10px; border-left: 4px solid #007bff; background-color: #f8f9fa; }
        .test-case.fail { border-left-color: #dc3545; }
        .test-case.pass { border-left-color: #28a745; }
        .severity { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .analysis-section { margin: 20px 0; padding: 15px; background-color: #f8f9fa; border-radius: 5px; }
        .analysis-header { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #495057; }
    </style>
</head>
<body>
    <h1>🔍 Website Comprehensive Test Report</h1>
    {summary}
    
    <div class="tab">
        <button class="tablinks active" onclick="openTab(event, 'testcases')">Test Cases</button>
        <button class="tablinks" onclick="openTab(event, 'links')">Link Status</button>
        <button class="tablinks" onclick="openTab(event, 'buttons')">Button Tests</button>
        <button class="tablinks" onclick="openTab(event, 'fonts')">Font Analysis</button>
        <button class="tablinks" onclick="openTab(event, 'responsive')">Responsiveness</button>
        <button class="tablinks" onclick="openTab(event, 'browser')">Browser Compatibility</button>
        <button class="tablinks" onclick="openTab(event, 'summary')">Summary</button>
    </div>
    
    <div id="testcases" class="tabcontent" style="display: block;">
        <h2>📋 Test Cases ({total_test_cases})</h2>
        <div style="margin-bottom: 20px;">
            <strong>Filter:</strong>
            <button onclick="filterTestCases('all')">All</button>
            <button onclick="filterTestCases('pass')">Pass</button>
            <button onclick="filterTestCases('fail')">Fail</button>
            <button onclick="filterTestCases('critical')">Critical</button>
            <button onclick="filterTestCases('high')">High</button>
            <button onclick="filterTestCases('medium')">Medium</button>
        </div>
        {test_cases_section}
    </div>
    
    <div id="links" class="tabcontent">
        <h2>🔗 Link Status Results</h2>
        {link_section}
    </div>
    
    <div id="buttons" class="tabcontent">
        <h2>🔘 Button Test Results</h2>
        {button_section}
    </div>
    
    <div id="fonts" class="tabcontent">
        <h2>🔤 Font Analysis Results</h2>
        {font_section}
    </div>
    
    <div id="responsive" class="tabcontent">
        <h2>📱 Responsiveness Check Results</h2>
        {responsive_section}
    </div>
    
    <div id="browser" class="tabcontent">
        <h2>🌐 Browser Compatibility Results</h2>
        {browser_section}
    </div>
    
    <div id="summary" class="tabcontent">
        <h2>📊 Summary Statistics</h2>
        {summary_section}
    </div>
    
    <script>
        function openTab(evt, tabName) {
            var i, tabcontent, tablinks;
            tabcontent = document.getElementsByClassName("tabcontent");
            for (i = 0; i < tabcontent.length; i++) {
                tabcontent[i].style.display = "none";
            }
            tablinks = document.getElementsByClassName("tablinks");
            for (i = 0; i < tablinks.length; i++) {
                tablinks[i].className = tablinks[i].className.replace(" active", "");
            }
            document.getElementById(tabName).style.display = "block";
            evt.currentTarget.className += " active";
        }
        
        function filterTestCases(filter) {
            var testCases = document.getElementsByClassName('test-case');
            for (var i = 0; i < testCases.length; i++) {
                var testCase = testCases[i];
                var show = false;
                
                if (filter === 'all') {
                    show = true;
                } else if (filter === 'pass' && testCase.classList.contains('pass')) {
                    show = true;
                } else if (filter === 'fail' && testCase.classList.contains('fail')) {
                    show = true;
                } else if (filter === 'critical' && testCase.querySelector('.severity.critical')) {
                    show = true;
                } else if (filter === 'high' && testCase.querySelector('.severity.high')) {
                    show = true;
                } else if (filter === 'medium' && testCase.querySelector('.severity.medium')) {
                    show = true;
                }
                
                testCase.style.display = show ? 'block' : 'none';
            }
        }
    </script>
</body>
</html>
        """
        
        # Generate all sections
        sections = {
            'summary': self.generate_summary().replace('\n', '<br>'),
            'total_test_cases': len(self.test_cases),
            'test_cases_section': self.generate_html_test_cases_section(),
            'link_section': self.generate_html_link_section(),
            'button_section': self.generate_html_button_section(),
            'font_section': self.generate_html_font_section(),
            'responsive_section': self.generate_html_responsive_section(),
            'browser_section': self.generate_html_browser_section(),
            'summary_section': self.generate_html_summary_section()
        }
        
        return html_template.format(**sections)

    def generate_html_font_section(self):
        """Generate HTML for font analysis section."""
        if not self.font_results:
            return "<p>No font analysis was performed.</p>"
        
        font_html = []
        for font_analysis in self.font_results:
            if isinstance(font_analysis, dict):
                url = font_analysis.get('url', 'Unknown URL')
                analysis_lines = font_analysis.get('analysis', [])
                
                font_html.append(f'<div class="analysis-section">')
                font_html.append(f'<div class="analysis-header">🔤 Font Analysis for: <a href="{url}" target="_blank">{url}</a></div>')
                
                for line in analysis_lines:
                    if isinstance(line, str):
                        # Add appropriate styling based on content
                        if '✅' in line:
                            font_html.append(f'<div style="color: #28a745; margin: 5px 0;">{line}</div>')
                        elif '⚠️' in line:
                            font_html.append(f'<div style="color: #ffc107; margin: 5px 0;">{line}</div>')
                        elif '❌' in line:
                            font_html.append(f'<div style="color: #dc3545; margin: 5px 0;">{line}</div>')
                        elif '📊' in line:
                            font_html.append(f'<div style="font-weight: bold; color: #007bff; margin: 5px 0;">{line}</div>')
                        elif '=' in line or '-' in line:
                            font_html.append(f'<div style="color: #6c757d; margin: 5px 0;">{line}</div>')
                        else:
                            font_html.append(f'<div style="margin: 5px 0;">{line}</div>')
                
                font_html.append(f'</div>')
        
        return ''.join(font_html)
    
    def generate_html_responsive_section(self):
        """Generate HTML for responsiveness section."""
        if not self.responsiveness_results:
            return "<p>No responsiveness checks were performed.</p>"
        
        responsive_html = []
        for responsive_analysis in self.responsiveness_results:
            if isinstance(responsive_analysis, dict):
                url = responsive_analysis.get('url', 'Unknown URL')
                issues = responsive_analysis.get('issues', [])
                
                responsive_html.append(f'<div class="analysis-section">')
                responsive_html.append(f'<div class="analysis-header">📱 Responsiveness Check for: <a href="{url}" target="_blank">{url}</a></div>')
                
                for line in issues:
                    if isinstance(line, str):
                        # Add appropriate styling based on content
                        if '✅' in line:
                            responsive_html.append(f'<div style="color: #28a745; margin: 5px 0;">{line}</div>')
                        elif '⚠️' in line:
                            responsive_html.append(f'<div style="color: #ffc107; margin: 5px 0;">{line}</div>')
                        elif '❌' in line:
                            responsive_html.append(f'<div style="color: #dc3545; margin: 5px 0;">{line}</div>')
                        elif '📊' in line or '📏' in line or '🎯' in line or '📈' in line:
                            responsive_html.append(f'<div style="font-weight: bold; color: #007bff; margin: 5px 0;">{line}</div>')
                        elif '=' in line or '-' in line:
                            responsive_html.append(f'<div style="color: #6c757d; margin: 5px 0;">{line}</div>')
                        else:
                            responsive_html.append(f'<div style="margin: 5px 0;">{line}</div>')
                
                responsive_html.append(f'</div>')
        
        return ''.join(responsive_html)
    
    def generate_html_browser_section(self):
        """Generate HTML for browser compatibility section."""
        if not self.browser_compatibility_results:
            return "<p>No browser compatibility checks were performed.</p>"
        
        browser_html = []
        for browser_analysis in self.browser_compatibility_results:
            if isinstance(browser_analysis, dict):
                url = browser_analysis.get('url', 'Unknown URL')
                issues = browser_analysis.get('issues', [])
                
                browser_html.append(f'<div class="analysis-section">')
                browser_html.append(f'<div class="analysis-header">🌐 Browser Compatibility for: <a href="{url}" target="_blank">{url}</a></div>')
                
                for line in issues:
                    if isinstance(line, str):
                        # Add appropriate styling based on content
                        if '✅' in line:
                            browser_html.append(f'<div style="color: #28a745; margin: 5px 0;">{line}</div>')
                        elif '⚠️' in line:
                            browser_html.append(f'<div style="color: #ffc107; margin: 5px 0;">{line}</div>')
                        elif '❌' in line:
                            browser_html.append(f'<div style="color: #dc3545; margin: 5px 0;">{line}</div>')
                        elif '🚫' in line or '🎨' in line or '💻' in line or '🖼️' in line or '🔧' in line or '📊' in line or '💡' in line:
                            browser_html.append(f'<div style="font-weight: bold; color: #007bff; margin: 5px 0;">{line}</div>')
                        elif '=' in line or '-' in line:
                            browser_html.append(f'<div style="color: #6c757d; margin: 5px 0;">{line}</div>')
                        else:
                            browser_html.append(f'<div style="margin: 5px 0;">{line}</div>')
                
                browser_html.append(f'</div>')
        
        return ''.join(browser_html)
    
    def generate_html_test_cases_section(self):
        """Generate HTML for test cases section."""
        if not self.test_cases:
            return "<p>No test cases were generated.</p>"
        
        test_cases_html = []
        
        for test_case in self.test_cases:
            # Determine CSS classes
            status_class = "pass" if test_case['Case Pass/Fail'] == 'Pass' else "fail"
            severity_class = test_case['Severity'].lower()
            
            test_case_html = f"""
            <div class="test-case {status_class}">
                <h3>{test_case['Test ID']}: {test_case['Test Case Description'][:100]}</h3>
                <div>
                    <strong>Module:</strong> {test_case['Module']}<br>
                    <strong>Test Data:</strong> {test_case['Test Links/Data'][:200]}<br>
                    <strong>Status:</strong> {test_case['Status']} | 
                    <strong>Result:</strong> {test_case['Case Pass/Fail']} | 
                    <strong>Severity:</strong> <span class="severity {severity_class}">{test_case['Severity']}</span><br>
                    <strong>Expected:</strong> {test_case['Expected Result'][:200]}<br>
                    <strong>Actual:</strong> {test_case['Actual Result'][:200]}<br>
                    <strong>Comments:</strong> {test_case['Comments/Bug ID']}<br>
                    <strong>Resolutions:</strong> {test_case['Resolutions']}
                </div>
            </div>
            """
            test_cases_html.append(test_case_html)
        
        return ''.join(test_cases_html)
    
    def generate_html_link_section(self):
        """Generate HTML for link status section."""
        if not self.current_results:
            return "<p>No link tests were performed.</p>"
        
        rows = []
        for result in self.current_results:
            status_class = {
                'Success': 'success',
                'Redirect': 'warning',
                'Client Error': 'error',
                'Server Error': 'error',
                'Error': 'error'
            }.get(result['status_category'], '')
            
            status_emoji = {
                'Success': '✅', 'Redirect': '🔄', 'Client Error': '❌',
                'Server Error': '🚫', 'Error': '⚠️'
            }.get(result['status_category'], '📋')
            
            row = f"""
            <tr class="{status_class}">
                <td>{status_emoji}</td>
                <td>{result['status_code'] or 'N/A'}</td>
                <td>{result['response_time_ms']}ms</td>
                <td><a href="{result['url']}" target="_blank">{result['url']}</a></td>
                <td><a href="{result.get('final_url', result['url'])}" target="_blank">{result.get('final_url', result['url'])}</a></td>
            </tr>
            """
            rows.append(row)
        
        return f"""
        <table>
            <tr>
                <th>Status</th><th>Code</th><th>Response Time</th><th>URL</th><th>Final URL</th>
            </tr>
            {''.join(rows)}
        </table>
        <p>Total links tested: {len(self.current_results)}</p>
        """
    
    def generate_html_button_section(self):
        """Generate HTML for button test section."""
        if not self.button_test_results:
            return "<p>No button tests were performed or no buttons were found.</p>"
        
        button_html = []
        for result in self.button_test_results:
            status_emoji = "✅" if result.get('test_status_code') and 200 <= result['test_status_code'] < 400 else "❌"
            status_code = result.get('test_status_code', 'ERROR')
            button_text = result.get('text', 'N/A')[:100]
            
            html = f"""
            <div class="test-case">
                <strong>{status_emoji} Button: {button_text}</strong><br>
                <strong>Type:</strong> {result.get('element_type', 'N/A')} | 
                <strong>ID:</strong> {result.get('id', 'N/A')} | 
                <strong>Class:</strong> {result.get('class', 'N/A')}<br>
                <strong>Page:</strong> <a href="{result.get('page_url')}" target="_blank">{result.get('page_url')}</a><br>
                <strong>Action URL:</strong> <a href="{result.get('action_url')}" target="_blank">{result.get('action_url')}</a> → 
                <strong>Final URL:</strong> <a href="{result.get('test_final_url', result.get('action_url'))}" target="_blank">{result.get('test_final_url', result.get('action_url'))}</a><br>
                <strong>Status:</strong> {status_code} | 
                <strong>Response Time:</strong> {result.get('test_response_time', 0)}ms | 
                <strong>Redirected:</strong> {'Yes' if result.get('test_redirected') else 'No'}
            </div>
            """
            button_html.append(html)
        
        return f"<p>Total buttons tested: {len(self.button_test_results)}</p>{''.join(button_html)}"
    
    def generate_html_summary_section(self):
        """Generate HTML for summary section."""
        summary_data = self.generate_export_summary()
        
        rows = []
        for i in range(len(summary_data['Category'])):
            row = f"""
            <tr>
                <td>{summary_data['Category'][i]}</td>
                <td>{summary_data['Metric'][i]}</td>
                <td>{summary_data['Value'][i]}</td>
                <td>{summary_data['Status'][i]}</td>
                <td>{summary_data['Notes'][i]}</td>
            </tr>
            """
            rows.append(row)
        
        return f"""
        <table>
            <tr>
                <th>Category</th><th>Metric</th><th>Value</th><th>Status</th><th>Notes</th>
            </tr>
            {''.join(rows)}
        </table>
        """
    
    # ============================================================================
    # CLEANUP FUNCTIONS
    # ============================================================================
    
    def clear_all(self):
        """Clear all data and reset UI."""
        # Clear all text areas
        for text_widget in [self.links_preview, self.results_text, self.buttons_text, 
                           self.spelling_text, self.fonts_text, self.responsive_text, 
                           self.browser_text]:
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
        

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Install required packages
    try:
        import textblob
    except ImportError:
        print("Installing textblob...")
        subprocess.check_call(['pip', 'install', 'textblob'])
    
    try:
        import cssutils
    except ImportError:
        print("Installing cssutils...")
        subprocess.check_call(['pip', 'install', 'cssutils'])
    
    try:
        import pandas
    except ImportError:
        print("Installing pandas...")
        subprocess.check_call(['pip', 'install', 'pandas'])
    
    try:
        from openpyxl import Workbook
    except ImportError:
        print("Installing openpyxl...")
        subprocess.check_call(['pip', 'install', 'openpyxl'])
    
    # Create and run the application
    root = tk.Tk()
    app = WebsiteLinkChecker(root)
    root.mainloop()
    
    
    