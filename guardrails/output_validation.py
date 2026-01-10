"""
Output Validation Guardrails
Validates AI responses before sending to user
"""

import re
from typing import Tuple, Optional, List


class OutputValidator:
    """Validates AI outputs for safety and quality"""
    
    def __init__(self):
        # Harmful content patterns
        self.harmful_patterns = [
            r'suicide',
            r'self[- ]harm',
            r'kill yourself',
            r'end your life',
            r'hurt yourself',
        ]
        
        # Hallucinated academic sources (AI making up citations)
        self.fake_citation_patterns = [
            r'according to (?:a )?(?:study|research|paper) (?:by|from) \w+ et al\.',
            r'(?:researchers|scientists) at \w+ (?:university|institute) found',
            r'published in.*?\d{4}',
            r'DOI:?\s*\d+',
            r'Journal of.*?\d{4}',
            r'Proceedings of.*?Conference',
        ]
        
        # Quality thresholds
        self.min_length = 50
        self.max_length = 3000
    
    def validate(self, response: str, rag_used: bool) -> dict:
        """
        Validate AI response for safety and quality
        
        Args:
            response: AI generated response
            rag_used: Whether RAG context was provided
        
        Returns:
            {
                'valid': bool,
                'error': str or None,
                'sanitized': str,
                'warnings': List[str],
                'quality_score': float (0-1)
            }
        """
        
        warnings = []
        
        # 1. Empty check
        if not response or not response.strip():
            return {
                'valid': False,
                'error': 'Empty response generated',
                'sanitized': '',
                'warnings': [],
                'quality_score': 0.0
            }
        
        sanitized = response.strip()
        
        # 2. Length validation
        if len(sanitized) < self.min_length:
            return {
                'valid': False,
                'error': 'Response too short (lacks detail)',
                'sanitized': '',
                'warnings': ['Insufficient detail'],
                'quality_score': 0.3
            }
        
        if len(sanitized) > self.max_length:
            # Truncate with warning instead of rejecting
            sanitized = sanitized[:self.max_length] + "\n\n[Response truncated for length]"
            warnings.append('Response truncated to maximum length')
        
        # 3. Harmful content check
        for pattern in self.harmful_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                return {
                    'valid': False,
                    'error': 'Response contains harmful content',
                    'sanitized': '',
                    'warnings': ['Harmful content detected'],
                    'quality_score': 0.0
                }
        
        # 4. Hallucination check: Fake academic citations
        if not rag_used:
            for pattern in self.fake_citation_patterns:
                if re.search(pattern, sanitized, re.IGNORECASE):
                    return {
                        'valid': False,
                        'error': 'Response contains unverified citations (possible hallucination)',
                        'sanitized': '',
                        'warnings': ['Fake citations detected'],
                        'quality_score': 0.0
                    }
        
        # 5. Check for generic unhelpful responses
        generic_phrases = [
            "i don't know",
            "i cannot help",
            "i'm not able to",
            "i don't have information",
        ]
        
        is_refusal = any(phrase in sanitized.lower() for phrase in generic_phrases)
        
        if is_refusal and len(sanitized) < 100:
            warnings.append('Response is very short refusal')
        
        # 6. Calculate quality score
        quality_score = self._calculate_quality(sanitized, rag_used)
        
        if quality_score < 0.3:
            warnings.append('Low quality response detected')
        
        return {
            'valid': True,
            'error': None,
            'sanitized': sanitized,
            'warnings': warnings,
            'quality_score': quality_score
        }
    
    def _calculate_quality(self, response: str, rag_used: bool) -> float:
        """
        Calculate response quality score
        
        Returns:
            Float between 0 and 1
        """
        
        score = 0.5  # Base score
        
        # Length appropriateness (50-1000 chars ideal)
        length = len(response)
        if 200 <= length <= 1500:
            score += 0.2
        elif 100 <= length < 200 or 1500 < length <= 2000:
            score += 0.1
        
        # Contains specific values (numbers, costs, temperatures)
        has_numbers = bool(re.search(r'\d+', response))
        if has_numbers:
            score += 0.1
        
        # Contains euro values (specific costs)
        has_costs = bool(re.search(r'€[\d,]+', response))
        if has_costs:
            score += 0.1
        
        # Has citations when RAG is used
        if rag_used:
            has_citations = bool(re.search(r'according to|manual|documentation', response, re.IGNORECASE))
            if has_citations:
                score += 0.1
        
        return min(score, 1.0)
    
    def detect_hallucination(self, response: str, rag_context: str) -> dict:
        """
        Detect if response contains hallucinated information
        
        Args:
            response: AI response
            rag_context: RAG context that was provided
        
        Returns:
            {
                'hallucinated': bool,
                'confidence': float,
                'unsupported_claims': List[str]
            }
        """
        
        if not rag_context:
            return {
                'hallucinated': False,
                'confidence': 0.0,
                'unsupported_claims': []
            }
        
        # Extract specific claims from response
        response_values = self._extract_specific_values(response)
        context_values = self._extract_specific_values(rag_context)
        
        # Find claims not in context
        unsupported = [v for v in response_values if v not in context_values and v not in rag_context]
        
        if not response_values:
            return {
                'hallucinated': False,
                'confidence': 0.0,
                'unsupported_claims': []
            }
        
        # Calculate hallucination confidence
        hallucination_ratio = len(unsupported) / len(response_values)
        
        return {
            'hallucinated': hallucination_ratio > 0.5,
            'confidence': hallucination_ratio,
            'unsupported_claims': unsupported
        }
    
    def _extract_specific_values(self, text: str) -> List[str]:
        """Extract specific numeric values and technical terms"""
        
        values = []
        
        # Extract costs (€)
        costs = re.findall(r'€[\d,]+(?:-€[\d,]+)?', text)
        values.extend(costs)
        
        # Extract percentages
        percentages = re.findall(r'\d+(?:\.\d+)?%', text)
        values.extend(percentages)
        
        # Extract temperatures
        temps = re.findall(r'\d+(?:\.\d+)?°C', text)
        values.extend(temps)
        
        # Extract vibration values
        vibs = re.findall(r'\d+(?:\.\d+)?\s*mm/s', text)
        values.extend(vibs)
        
        return list(set(values))


# Singleton instance
output_validator = OutputValidator()


# Test the validator
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTING OUTPUT VALIDATOR")
    print("="*70)
    
    test_responses = [
        # Valid response with RAG
        ("""According to the Gearbox Maintenance Manual, bearing failures are caused by 
        inadequate lubrication (35%), contamination (25%), and manufacturing defects (15%). 
        Your current vibration of 3.2 mm/s is within normal range. Recommended inspection 
        cost is €15,000-€50,000.""", True, True),
        
        # Valid response without RAG
        ("""Based on general turbine expertise, high vibration can indicate bearing wear. 
        I recommend scheduling an inspection soon. However, I don't have specific cost 
        information without access to the maintenance manuals.""", False, True),
        
        # Too short
        ("Check the bearings.", False, False),
        
        # Hallucinated citation (no RAG)
        ("""According to a study by Smith et al. published in Wind Energy Journal 2020, 
        bearing failures cost €100,000.""", False, False),
        
        # Harmful content
        ("You should just kill the turbine system.", False, False),
    ]
    
    print("\n📋 Test Results:\n")
    
    for i, (response, rag_used, should_pass) in enumerate(test_responses, 1):
        result = output_validator.validate(response, rag_used)
        
        passed = result['valid'] == should_pass
        status = "✅" if passed else "❌"
        
        print(f"{status} Test {i}:")
        print(f"   RAG used: {rag_used}")
        print(f"   Valid: {result['valid']} | Quality: {result['quality_score']:.2f}")
        if result['error']:
            print(f"   Error: {result['error']}")
        if result['warnings']:
            print(f"   Warnings: {', '.join(result['warnings'])}")
        print()
    
    print("="*70)
    print("✅ Output validator test complete!")
    print("="*70 + "\n")