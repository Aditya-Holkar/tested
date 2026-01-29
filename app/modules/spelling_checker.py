# modules/spelling_checker.py - Spelling and grammar checking
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import re

class SpellingChecker:
    """Check spelling and grammar on web pages"""
    
    def __init__(self, test_case_manager=None):
        self.test_case_manager = test_case_manager
    
    def check_spelling_on_page(self, url):
        """Check spelling on a web page"""
        test_cases = []
        
        try:
            response = requests.get(url, timeout=10, verify=False)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean and split text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            lines = [line for line in lines if len(line.split()) > 3]  # Skip short lines
            
            if not lines:
                test_cases.append(self._create_spelling_test_case(
                    url=url,
                    module="Spelling Check",
                    description="Check page for spelling errors",
                    test_steps="1. Extract text content\n2. Analyze spelling\n3. Identify errors",
                    expected_result="Page should have readable text content",
                    actual_result="No substantial text content found",
                    status="Info",
                    severity="Low"
                ))
                return test_cases
            
            # Check spelling in chunks
            all_errors = []
            for i, line in enumerate(lines[:20]):  # Check first 20 lines
                line_errors = self._check_line_spelling(line, i+1)
                if line_errors:
                    all_errors.extend(line_errors)
            
            if not all_errors:
                test_cases.append(self._create_spelling_test_case(
                    url=url,
                    module="Spelling Check",
                    description="Check page for spelling errors",
                    test_steps="1. Extract text content\n2. Analyze spelling\n3. Identify errors",
                    expected_result="No spelling errors should be present",
                    actual_result="No spelling errors detected",
                    status="Pass",
                    severity="Low"
                ))
            else:
                # Group errors
                error_count = len(all_errors)
                sample_errors = all_errors[:5]  # Show first 5 errors
                
                test_cases.append(self._create_spelling_test_case(
                    url=url,
                    module="Spelling Check",
                    description="Check page for spelling errors",
                    test_steps="1. Extract text content\n2. Analyze spelling\n3. Identify errors",
                    expected_result="No spelling errors should be present",
                    actual_result=f"Found {error_count} potential spelling issues. Examples: {', '.join(sample_errors)}",
                    status="Warning",
                    severity="Low",
                    resolutions="Review and correct spelling errors on the page"
                ))
            
            # Check readability (basic)
            readability_score = self._check_readability(text[:1000])  # Check first 1000 chars
            if readability_score < 50:
                test_cases.append(self._create_spelling_test_case(
                    url=url,
                    module="Readability",
                    description="Check text readability",
                    test_steps="1. Analyze text complexity\n2. Calculate readability score\n3. Evaluate results",
                    expected_result="Text should be readable",
                    actual_result=f"Readability score: {readability_score:.1f}% (Low)",
                    status="Warning",
                    severity="Low",
                    resolutions="Simplify language and improve readability"
                ))
            
            return test_cases
            
        except Exception as e:
            test_cases.append(self._create_spelling_test_case(
                url=url,
                module="Spelling Check",
                description="Check page for spelling errors",
                test_steps="1. Extract text content\n2. Analyze spelling\n3. Identify errors",
                expected_result="Spelling check completed successfully",
                actual_result=f"Error during spelling check: {str(e)[:100]}",
                status="Fail",
                severity="Medium"
            ))
            return test_cases
    
    def _check_line_spelling(self, line, line_number):
        """Check spelling in a single line"""
        errors = []
        
        try:
            # Clean line (remove URLs, email addresses, etc.)
            clean_line = re.sub(r'http\S+|www\.\S+|\S+@\S+', '', line)
            clean_line = re.sub(r'[^\w\s]', ' ', clean_line)
            
            # Skip very short lines
            if len(clean_line.split()) < 3:
                return errors
            
            # Use TextBlob for spelling correction
            blob = TextBlob(clean_line)
            
            # Get corrected version
            corrected = blob.correct()
            
            # Compare original and corrected
            original_words = str(blob).split()
            corrected_words = str(corrected).split()
            
            for orig, corr in zip(original_words, corrected_words):
                if orig.lower() != corr.lower() and len(orig) > 2:  # Skip short words
                    # Check if it's actually a misspelling (not just different word)
                    if self._is_likely_misspelling(orig, corr):
                        errors.append(f"Line {line_number}: '{orig}' → '{corr}'")
            
            return errors
            
        except:
            return errors
    
    def _is_likely_misspelling(self, original, corrected):
        """Determine if a word is likely misspelled"""
        # Skip common abbreviations, acronyms, and proper nouns
        common_abbrevs = {'usa', 'uk', 'api', 'css', 'html', 'js', 'json', 'xml', 'http', 'https'}
        
        if original.lower() in common_abbrevs:
            return False
        
        # Check if words are similar (edit distance)
        if len(original) <= 3 or len(corrected) <= 3:
            return False
        
        # Simple similarity check
        if original.lower() == corrected.lower():
            return False
        
        # Check if it's a capitalization issue
        if original.lower() == corrected.lower():
            return False
        
        return True
    
    def _check_readability(self, text):
        """Calculate basic readability score"""
        try:
            # Simple readability calculation
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            if not sentences:
                return 0
            
            words = text.split()
            word_count = len(words)
            sentence_count = len(sentences)
            
            if word_count == 0 or sentence_count == 0:
                return 0
            
            # Average words per sentence
            avg_words_per_sentence = word_count / sentence_count
            
            # Calculate readability score (simplified)
            if avg_words_per_sentence < 15:
                return 80
            elif avg_words_per_sentence < 20:
                return 70
            elif avg_words_per_sentence < 25:
                return 60
            else:
                return 40
                
        except:
            return 50
    
    def _create_spelling_test_case(self, **kwargs):
        """Helper method to create spelling test cases"""
        if self.test_case_manager:
            return self.test_case_manager.create_test_case(
                test_type="Spelling Check",
                module=kwargs.get('module', 'Spelling Check'),
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