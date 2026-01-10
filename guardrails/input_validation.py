"""
Input Validation Guardrails
Validates and sanitizes user inputs before processing
"""

import re
from typing import Tuple, Optional, List


class InputValidator:
    """Validates user inputs for safety and appropriateness"""
    
    def __init__(self):
        # Security: Blocked injection patterns
        self.blocked_patterns = [
            # XSS attempts
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'onerror\s*=',
            r'onclick\s*=',
            r'<iframe',
            
            # SQL injection
            r';\s*DROP\s+TABLE',
            r'UNION\s+SELECT',
            r'--\s*$',
            r'/\*.*?\*/',
            
            # Command injection
            r';\s*rm\s+-rf',
            r'\$\(.*?\)',
            r'`.*?`',
            r'&&\s*rm',
            
            # Path traversal
            r'\.\./\.\.',
            r'\.\.\\\.\.\\',
        ]
        
        # Inappropriate content
        self.inappropriate_keywords = [
            # Adult content
            'porn', 'xxx', 'sex', 'nude', 'nsfw',
            # Drugs
            'drugs', 'cocaine', 'heroin', 'meth',
            # Violence
            'bomb', 'weapon', 'gun', 'explosive',
            # Hate speech
            'kill', 'murder', 'suicide', 'hate',
        ]
        
        # Topic relevance: Wind turbine keywords
        self.on_topic_keywords = [
            # Core components
            'turbine', 'wind', 'rotor', 'blade', 'nacelle', 'tower',
            'gearbox', 'generator', 'bearing', 'shaft', 'hub',
            'pitch', 'yaw', 'brake',
            
            # Operations
            'power', 'output', 'generation', 'performance', 'capacity',
            'rpm', 'rotation', 'speed', 'production', 'efficiency',
            
            # Maintenance
            'maintenance', 'repair', 'inspection', 'service', 'failure',
            'diagnostic', 'troubleshoot', 'replace', 'fix', 'check',
            'lubrication', 'oil', 'grease',
            
            # Measurements
            'temperature', 'vibration', 'pressure', 'voltage', 'current',
            'sensor', 'reading', 'measurement', 'monitor', 'data',
            
            # Issues
            'alarm', 'fault', 'error', 'warning', 'problem', 'issue',
            'noise', 'leak', 'damage', 'wear', 'crack', 'corrosion',
            
            # Costs & planning
            'cost', 'price', 'expense', 'budget', 'downtime', 'schedule',
            
            # Status
            'status', 'health', 'condition', 'state', 'operating',
            'shutdown', 'startup', 'running', 'stopped',
        ]
        
        # Off-topic indicators
        self.off_topic_keywords = [
            # Weather (unless asking about turbine impact)
            'weather', 'forecast', 'rain', 'snow',
            # Unrelated topics
            'recipe', 'cooking', 'movie', 'game', 'sport',
            'politics', 'news', 'stock', 'bitcoin', 'crypto',
            # Other machinery
            'car', 'airplane', 'ship', 'train', 'boat',
        ]
        
        # Length limits
        self.max_length = 500
        self.min_length = 3
    
    def validate(self, question: str) -> dict:
        """
        Comprehensive input validation
        
        Args:
            question: User's question
        
        Returns:
            {
                'valid': bool,
                'error': str or None,
                'sanitized': str,
                'warnings': List[str]
            }
        """
        
        warnings = []
        
        # 1. Empty check
        if not question or not question.strip():
            return {
                'valid': False,
                'error': 'Question cannot be empty',
                'sanitized': '',
                'warnings': []
            }
        
        # 2. Sanitize
        sanitized = question.strip()
        
        # 3. Length validation
        if len(sanitized) < self.min_length:
            return {
                'valid': False,
                'error': f'Question too short (minimum {self.min_length} characters)',
                'sanitized': '',
                'warnings': []
            }
        
        if len(sanitized) > self.max_length:
            return {
                'valid': False,
                'error': f'Question too long (maximum {self.max_length} characters)',
                'sanitized': '',
                'warnings': []
            }
        
        # 4. Security: Check for injection attempts
        for pattern in self.blocked_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                return {
                    'valid': False,
                    'error': 'Invalid input detected - potential security risk',
                    'sanitized': '',
                    'warnings': ['Security violation detected']
                }
        
        # 5. Check for inappropriate content
        lower_question = sanitized.lower()
        for keyword in self.inappropriate_keywords:
            if keyword in lower_question:
                return {
                    'valid': False,
                    'error': 'Question contains inappropriate content',
                    'sanitized': '',
                    'warnings': ['Inappropriate content']
                }
        
        # 6. Spam detection: Excessive special characters
        if len(sanitized) > 0:
            special_char_ratio = sum(1 for c in sanitized if not c.isalnum() and not c.isspace()) / len(sanitized)
            if special_char_ratio > 0.3:
                return {
                    'valid': False,
                    'error': 'Question contains too many special characters',
                    'sanitized': '',
                    'warnings': ['Possible spam']
                }
        
        # 7. Repeated characters (spam)
        if re.search(r'(.)\1{10,}', sanitized):
            return {
                'valid': False,
                'error': 'Invalid input format detected',
                'sanitized': '',
                'warnings': ['Spam pattern detected']
            }
        
        # 8. Excessive capitalization
        if len(sanitized) > 10:
            caps_ratio = sum(1 for c in sanitized if c.isupper()) / len(sanitized)
            if caps_ratio > 0.7:
                warnings.append('Excessive capitalization detected')
        
        return {
            'valid': True,
            'error': None,
            'sanitized': sanitized,
            'warnings': warnings
        }
    
    def check_topic_relevance(self, question: str) -> dict:
        """
        Check if question is related to wind turbines
        
        Returns:
            {
                'on_topic': bool,
                'confidence': float (0-1),
                'reason': str
            }
        """
        
        question_lower = question.lower()
        
        # Count topic matches
        on_topic_matches = sum(1 for kw in self.on_topic_keywords if kw in question_lower)
        off_topic_matches = sum(1 for kw in self.off_topic_keywords if kw in question_lower)
        
        # Strong off-topic indicators
        if off_topic_matches > 0 and on_topic_matches == 0:
            return {
                'on_topic': False,
                'confidence': 0.9,
                'reason': f'Question appears to be about {self.off_topic_keywords[0]} rather than wind turbines'
            }
        
        # Calculate confidence
        if on_topic_matches == 0:
            # Check for general questions (acceptable)
            general_phrases = [
                'what can you', 'help me', 'tell me about', 'explain',
                'how does', 'what is', 'show me', 'analyze', 'status',
                'current', 'now', 'today', 'check', 'look at',
            ]
            
            has_general = any(phrase in question_lower for phrase in general_phrases)
            
            if has_general:
                return {
                    'on_topic': True,
                    'confidence': 0.5,
                    'reason': 'General question accepted (may relate to turbine data)'
                }
            
            return {
                'on_topic': False,
                'confidence': 0.7,
                'reason': 'No wind turbine-related keywords found'
            }
        
        # Calculate confidence based on matches
        confidence = min(on_topic_matches * 0.25, 1.0)
        
        return {
            'on_topic': True,
            'confidence': confidence,
            'reason': f'Found {on_topic_matches} turbine-related keywords'
        }
    
    def get_suggestions(self, question: str) -> List[str]:
        """
        Generate helpful suggestions for off-topic questions
        
        Returns:
            List of suggested questions
        """
        
        return [
            "What causes high vibration in wind turbines?",
            "Analyze my current turbine performance",
            "What are the symptoms of bearing failure?",
            "How much does gearbox maintenance cost?",
            "What's the current turbine status?",
            "Explain temperature monitoring best practices",
            "What maintenance is due this month?",
            "Troubleshoot power output issues",
        ]


# Singleton instance
input_validator = InputValidator()


# Test the validator
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTING INPUT VALIDATOR")
    print("="*70)
    
    test_cases = [
        # Valid inputs
        ("What causes bearing failure?", True, True),
        ("Is vibration of 4.2 mm/s too high?", True, True),
        ("Analyze current turbine performance", True, True),
        
        # Off-topic but valid format
        ("What's the weather today?", True, False),
        ("Tell me a joke", True, False),
        
        # Invalid inputs
        ("", False, False),
        ("ab", False, False),
        ("<script>alert('xss')</script>", False, False),
        ("x" * 600, False, False),
        
        # Inappropriate
        ("Show me porn", False, False),
        ("How to make a bomb", False, False),
    ]
    
    print("\n📋 Test Results:\n")
    
    for i, (question, should_be_valid, should_be_on_topic) in enumerate(test_cases, 1):
        result = input_validator.validate(question)
        topic = input_validator.check_topic_relevance(question)
        
        valid_ok = result['valid'] == should_be_valid
        topic_ok = not should_be_valid or topic['on_topic'] == should_be_on_topic
        
        status = "✅" if (valid_ok and topic_ok) else "❌"
        
        print(f"{status} Test {i}: {question[:50]}")
        print(f"   Valid: {result['valid']} | On-topic: {topic['on_topic']} (confidence: {topic['confidence']:.2f})")
        if result['error']:
            print(f"   Error: {result['error']}")
        if result['warnings']:
            print(f"   Warnings: {', '.join(result['warnings'])}")
        print()
    
    print("="*70)
    print("✅ Input validator test complete!")
    print("="*70 + "\n")