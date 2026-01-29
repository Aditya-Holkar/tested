# modules/constants.py - Shared constants

# Required packages for installation
REQUIRED_PACKAGES = [
    ('textblob', 'textblob'),
    ('cssutils', 'cssutils'),
    ('pandas', 'pandas'),
    ('openpyxl', 'openpyxl'),
    ('psutil', 'psutil'),
    ('beautifulsoup4', 'beautifulsoup4'),
    ('requests', 'requests'),
    ('lxml', 'lxml'),
]

# Valid ARIA roles from WAI-ARIA specification
VALID_ARIA_ROLES = {
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
}

# CSS Frameworks for detection
CSS_FRAMEWORKS = {
    'Bootstrap': ['bootstrap'],
    'Foundation': ['foundation'],
    'Bulma': ['bulma'],
    'Tailwind': ['tailwind'],
    'Materialize': ['materialize']
}

# JavaScript Frameworks for detection
JS_FRAMEWORKS = {
    'jQuery': ['jquery', '$.', 'jQuery.'],
    'React': ['react', 'ReactDOM'],
    'Vue': ['vue', 'Vue.'],
    'Angular': ['angular', 'ng-']
}
# WCAG 2.1 Success Criteria
WCAG_CRITERIA = {
    # Perceivable
    '1.1.1': 'Non-text Content',
    '1.2.1': 'Audio-only and Video-only (Prerecorded)',
    '1.2.2': 'Captions (Prerecorded)',
    '1.3.1': 'Info and Relationships',
    '1.3.2': 'Meaningful Sequence',
    '1.4.1': 'Use of Color',
    '1.4.2': 'Audio Control',
    '1.4.3': 'Contrast (Minimum)',
    '1.4.4': 'Resize text',
    '1.4.5': 'Images of Text',
    '1.4.10': 'Reflow',
    '1.4.11': 'Non-text Contrast',
    '1.4.12': 'Text Spacing',
    '1.4.13': 'Content on Hover or Focus',
    
    # Operable
    '2.1.1': 'Keyboard',
    '2.1.2': 'No Keyboard Trap',
    '2.1.4': 'Character Key Shortcuts',
    '2.2.1': 'Timing Adjustable',
    '2.2.2': 'Pause, Stop, Hide',
    '2.3.1': 'Three Flashes or Below Threshold',
    '2.4.1': 'Bypass Blocks',
    '2.4.2': 'Page Titled',
    '2.4.3': 'Focus Order',
    '2.4.4': 'Link Purpose (In Context)',
    '2.4.5': 'Multiple Ways',
    '2.4.6': 'Headings and Labels',
    '2.4.7': 'Focus Visible',
    '2.5.1': 'Pointer Gestures',
    '2.5.2': 'Pointer Cancellation',
    '2.5.3': 'Label in Name',
    '2.5.4': 'Motion Actuation',
    
    # Understandable
    '3.1.1': 'Language of Page',
    '3.1.2': 'Language of Parts',
    '3.2.1': 'On Focus',
    '3.2.2': 'On Input',
    '3.2.3': 'Consistent Navigation',
    '3.2.4': 'Consistent Identification',
    '3.3.1': 'Error Identification',
    '3.3.2': 'Labels or Instructions',
    '3.3.3': 'Error Suggestion',
    '3.3.4': 'Error Prevention (Legal, Financial, Data)',
    
    # Robust
    '4.1.1': 'Parsing',
    '4.1.2': 'Name, Role, Value',
    '4.1.3': 'Status Messages'
}

# Test ID generator
class TestIDGenerator:
    """Generate unique test IDs"""
    
    def __init__(self, prefix="TC"):
        self.prefix = prefix
        self.counter = 1
    
    def generate(self):
        """Generate next test ID"""
        test_id = f"{self.prefix}{self.counter:04d}"
        self.counter += 1
        return test_id
    
    def reset(self):
        """Reset counter"""
        self.counter = 1
# CDN domains
CDN_DOMAINS = ['cloudflare', 'akamai', 'fastly', 'cloudfront', 'azureedge', 'googleusercontent']