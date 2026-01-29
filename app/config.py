# config.py - Configuration and constants

# Test Case Columns
TEST_CASE_COLUMNS = [
    'Test ID', 'Module', 'Test Links/Data', 'Test Case Description',
    'Pre-Conditions', 'Test Steps', 'Expected Result', 'Actual Result',
    'Status', 'Severity', 'Case Pass/Fail', 'Comments/Bug ID', 'Resolutions'
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

# Flask Configuration
class Config:
    SECRET_KEY = 'your-secret-key-here'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    TEMPLATES_AUTO_RELOAD = True