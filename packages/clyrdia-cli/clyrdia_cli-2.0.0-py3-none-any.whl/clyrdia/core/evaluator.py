"""
Simplified quality evaluator for Clyrdia CLI MVP - handles response quality assessment.
"""

import re
from typing import Dict, Any, Optional
from .console import console

class QualityEvaluator:
    """Simplified quality evaluator for MVP"""
    
    def __init__(self):
        self.evaluation_methods = {
            "length": self._evaluate_length,
            "coherence": self._evaluate_coherence,
            "relevance": self._evaluate_relevance,
            "completeness": self._evaluate_completeness
        }
    
    def evaluate_response(self, prompt: str, response: str, expected_output: Optional[str] = None) -> Dict[str, float]:
        """Evaluate response quality using multiple criteria"""
        scores = {}
        
        try:
            for method_name, method_func in self.evaluation_methods.items():
                try:
                    score = method_func(prompt, response, expected_output)
                    scores[method_name] = max(0.0, min(1.0, score))  # Clamp between 0 and 1
                except Exception as e:
                    console.print(f"[yellow]⚠️  Evaluation error for {method_name}: {str(e)}[/yellow]")
                    scores[method_name] = 0.0
            
            # Calculate overall score as average of individual scores
            if scores:
                scores["overall"] = sum(scores.values()) / len(scores)
            else:
                scores["overall"] = 0.0
                
        except Exception as e:
            console.print(f"[yellow]⚠️  Quality evaluation error: {str(e)}[/yellow]")
            scores = {"overall": 0.0}
        
        return scores
    
    def _evaluate_length(self, prompt: str, response: str, expected_output: Optional[str] = None) -> float:
        """Evaluate response length appropriateness"""
        if not response or len(response.strip()) == 0:
            return 0.0
        
        # Basic length scoring - responses should be substantial but not excessive
        response_length = len(response.strip())
        
        if response_length < 10:
            return 0.2  # Too short
        elif response_length < 50:
            return 0.5  # Short but acceptable
        elif response_length < 500:
            return 0.8  # Good length
        elif response_length < 2000:
            return 1.0  # Excellent length
        else:
            return 0.7  # Long but acceptable
    
    def _evaluate_coherence(self, prompt: str, response: str, expected_output: Optional[str] = None) -> float:
        """Evaluate response coherence and readability"""
        if not response or len(response.strip()) == 0:
            return 0.0
        
        score = 0.5  # Base score
        
        # Check for proper sentence structure
        sentences = re.split(r'[.!?]+', response)
        if len(sentences) > 1:
            score += 0.2
        
        # Check for paragraph structure
        paragraphs = response.split('\n\n')
        if len(paragraphs) > 1:
            score += 0.1
        
        # Check for common coherence indicators
        coherence_indicators = ['however', 'therefore', 'furthermore', 'moreover', 'additionally', 'in addition']
        if any(indicator in response.lower() for indicator in coherence_indicators):
            score += 0.2
        
        return min(1.0, score)
    
    def _evaluate_relevance(self, prompt: str, response: str, expected_output: Optional[str] = None) -> float:
        """Evaluate response relevance to the prompt"""
        if not response or len(response.strip()) == 0:
            return 0.0
        
        # Simple keyword overlap scoring
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        
        if not prompt_words:
            return 0.5  # Neutral if no prompt words
        
        overlap = len(prompt_words.intersection(response_words))
        relevance_score = overlap / len(prompt_words)
        
        # Boost score if response contains prompt-related terms
        if any(word in response.lower() for word in prompt_words):
            relevance_score = min(1.0, relevance_score + 0.3)
        
        return relevance_score
    
    def _evaluate_completeness(self, prompt: str, response: str, expected_output: Optional[str] = None) -> float:
        """Evaluate response completeness"""
        if not response or len(response.strip()) == 0:
            return 0.0
        
        score = 0.5  # Base score
        
        # Check if response addresses the prompt
        if '?' in prompt and '?' in response:
            score += 0.2  # Response includes questions
        
        # Check for structured response
        if any(marker in response for marker in ['1.', '2.', '3.', '•', '-', '*']):
            score += 0.2  # Structured response
        
        # Check for conclusion or summary
        conclusion_words = ['conclusion', 'summary', 'in summary', 'to summarize', 'overall']
        if any(word in response.lower() for word in conclusion_words):
            score += 0.1
        
        return min(1.0, score)
    
    def get_evaluation_summary(self, scores: Dict[str, float]) -> str:
        """Get a human-readable summary of evaluation scores"""
        if not scores:
            return "No evaluation data available"
        
        summary_parts = []
        for metric, score in scores.items():
            if metric == "overall":
                continue
            
            if score >= 0.8:
                status = "Excellent"
            elif score >= 0.6:
                status = "Good"
            elif score >= 0.4:
                status = "Fair"
            else:
                status = "Poor"
            
            summary_parts.append(f"{metric.title()}: {status} ({score:.2f})")
        
        if "overall" in scores:
            overall_score = scores["overall"]
            if overall_score >= 0.8:
                overall_status = "Excellent"
            elif overall_score >= 0.6:
                overall_status = "Good"
            elif overall_score >= 0.4:
                overall_status = "Fair"
            else:
                overall_status = "Poor"
            
            summary_parts.insert(0, f"Overall: {overall_status} ({overall_score:.2f})")
        
        return " | ".join(summary_parts)
