"""
Content Filtering
Combines input and output validation with helpful user guidance
"""

from typing import Dict, Any
from .input_validation import input_validator
from .output_validation import output_validator


class ContentFilter:
    """Main guardrail coordinator"""
    
    def __init__(self):
        self.input_validator = input_validator
        self.output_validator = output_validator
    
    def filter_input(self, question: str) -> Dict[str, Any]:
        """
        Comprehensive input filtering
        
        Returns:
            {
                'valid': bool,
                'error': str or None,
                'sanitized_question': str,
                'on_topic': bool,
                'topic_confidence': float,
                'warnings': List[str],
                'suggestions': List[str] (if off-topic)
            }
        """
        
        # Step 1: Safety validation
        safety_check = self.input_validator.validate(question)
        
        if not safety_check['valid']:
            return {
                'valid': False,
                'error': safety_check['error'],
                'sanitized_question': '',
                'on_topic': False,
                'topic_confidence': 0.0,
                'warnings': safety_check['warnings'],
                'suggestions': []
            }
        
        # Step 2: Topic relevance
        topic_check = self.input_validator.check_topic_relevance(safety_check['sanitized'])
        
        # Step 3: Generate suggestions if off-topic
        suggestions = []
        if not topic_check['on_topic']:
            suggestions = self.input_validator.get_suggestions(safety_check['sanitized'])
        
        return {
            'valid': True,
            'error': None,
            'sanitized_question': safety_check['sanitized'],
            'on_topic': topic_check['on_topic'],
            'topic_confidence': topic_check['confidence'],
            'warnings': safety_check['warnings'],
            'suggestions': suggestions,
            'topic_reason': topic_check['reason']
        }
    
    def filter_output(self, response: str, rag_used: bool, rag_context: str = "") -> Dict[str, Any]:
        """
        Comprehensive output filtering
        
        Returns:
            {
                'valid': bool,
                'error': str or None,
                'sanitized_response': str,
                'quality_score': float,
                'warnings': List[str],
                'hallucination_detected': bool,
                'hallucination_confidence': float
            }
        """
        
        # Step 1: Safety and quality validation
        safety_check = self.output_validator.validate(response, rag_used)
        
        if not safety_check['valid']:
            return {
                'valid': False,
                'error': safety_check['error'],
                'sanitized_response': '',
                'quality_score': 0.0,
                'warnings': safety_check['warnings'],
                'hallucination_detected': False,
                'hallucination_confidence': 0.0
            }
        
        # Step 2: Hallucination detection
        hallucination_check = self.output_validator.detect_hallucination(
            safety_check['sanitized'], 
            rag_context
        )
        
        return {
            'valid': True,
            'error': None,
            'sanitized_response': safety_check['sanitized'],
            'quality_score': safety_check['quality_score'],
            'warnings': safety_check['warnings'],
            'hallucination_detected': hallucination_check['hallucinated'],
            'hallucination_confidence': hallucination_check['confidence'],
            'unsupported_claims': hallucination_check.get('unsupported_claims', [])
        }
    
    def generate_off_topic_response(self, question: str, confidence: float, suggestions: list) -> str:
        """Generate helpful response for off-topic questions"""
        
        response = f"""**I'm TurboBot, specialized in wind turbine maintenance and operations.**

Your question appears to be outside my area of expertise (confidence: {confidence:.0%}).

**I can help you with:**
- 🔧 Turbine diagnostics and troubleshooting
- 📋 Maintenance procedures and schedules
- ⚠️ Component failures and repairs
- 💰 Cost estimates for maintenance
- 📊 Vibration and temperature analysis
- ⚡ Performance optimization
- 🛡️ Safety protocols
- 📈 Real-time turbine monitoring

**Current turbine capabilities:**
I can analyze your turbine's real-time data including power output, temperature, vibration, and wind speed to provide actionable recommendations.

**Try asking questions like:**"""
        
        for suggestion in suggestions[:5]:
            response += f"\n• {suggestion}"
        
        return response
    
    def get_stats(self) -> Dict[str, Any]:
        """Get guardrail statistics"""
        
        return {
            'input_validator': {
                'max_length': self.input_validator.max_length,
                'min_length': self.input_validator.min_length,
                'blocked_patterns': len(self.input_validator.blocked_patterns),
                'on_topic_keywords': len(self.input_validator.on_topic_keywords)
            },
            'output_validator': {
                'min_length': self.output_validator.min_length,
                'max_length': self.output_validator.max_length,
                'harmful_patterns': len(self.output_validator.harmful_patterns),
                'fake_citation_patterns': len(self.output_validator.fake_citation_patterns)
            }
        }


# Singleton instance
content_filter = ContentFilter()