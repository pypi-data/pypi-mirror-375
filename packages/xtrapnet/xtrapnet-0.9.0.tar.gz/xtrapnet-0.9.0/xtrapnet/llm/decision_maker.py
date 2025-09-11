"""
LLM Decision Maker for intelligent extrapolation strategy selection.

This module provides LLM-powered decision making for choosing appropriate
extrapolation strategies based on context, uncertainty, and domain knowledge.
"""

from __future__ import annotations

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import json
from .llm_assistant import LLMAssistant


class LLMDecisionMaker:
    """
    LLM Decision Maker for intelligent extrapolation strategy selection.
    
    This class provides intelligent decision making for:
    - Choosing appropriate extrapolation strategies
    - Balancing risk vs. performance
    - Incorporating domain knowledge
    - Making context-aware decisions
    """
    
    def __init__(self, llm_assistant: LLMAssistant):
        """
        Initialize LLM Decision Maker.
        
        Args:
            llm_assistant: LLM assistant for natural language reasoning
        """
        self.llm_assistant = llm_assistant
        
        # Available extrapolation strategies
        self.strategies = {
            'clip': 'Clip predictions to known value ranges',
            'zero': 'Return zero for OOD inputs',
            'nearest_data': 'Use closest training point prediction',
            'symmetry': 'Use symmetry-based assumptions',
            'warn': 'Print warning but still predict',
            'error': 'Raise error for OOD inputs',
            'highest_confidence': 'Select lowest-variance prediction',
            'backup': 'Use secondary model',
            'deep_ensemble': 'Average multiple model predictions',
            'llm_assist': 'Use LLM for fallback prediction',
            'physics_guided': 'Use physics constraints for guidance',
            'uncertainty_weighted': 'Weight predictions by uncertainty'
        }
        
        # Decision factors and their importance
        self.decision_factors = {
            'uncertainty_level': 'How uncertain the model is',
            'ood_severity': 'How far out-of-distribution the input is',
            'domain_context': 'Domain-specific requirements',
            'risk_tolerance': 'Acceptable level of risk',
            'performance_requirements': 'Required prediction accuracy',
            'computational_cost': 'Available computational resources',
            'interpretability': 'Need for explainable predictions'
        }
    
    def make_decision(
        self,
        input_data: Union[np.ndarray, torch.Tensor],
        prediction: Union[np.ndarray, torch.Tensor],
        uncertainty: Dict[str, float],
        ood_score: float,
        context: Dict[str, Any],
        available_strategies: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Make an intelligent decision about extrapolation strategy.
        
        Args:
            input_data: Input that needs handling
            prediction: Model prediction
            uncertainty: Uncertainty components
            ood_score: OOD detection score
            context: Additional context information
            available_strategies: Available strategies (None for all)
            
        Returns:
            Decision dictionary with strategy, reasoning, and confidence
        """
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().numpy()
        if isinstance(prediction, torch.Tensor):
            prediction = prediction.detach().numpy()
        
        # Use all strategies if none specified
        if available_strategies is None:
            available_strategies = list(self.strategies.keys())
        
        # Analyze the situation
        situation_analysis = self._analyze_situation(
            input_data, prediction, uncertainty, ood_score, context
        )
        
        # Make decision using LLM reasoning
        decision = self._llm_decision_making(
            situation_analysis, available_strategies, context
        )
        
        # Validate decision
        validated_decision = self._validate_decision(decision, context)
        
        return validated_decision
    
    def _analyze_situation(
        self,
        input_data: np.ndarray,
        prediction: np.ndarray,
        uncertainty: Dict[str, float],
        ood_score: float,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze the current situation for decision making."""
        
        # Calculate uncertainty level
        total_uncertainty = uncertainty.get('total_std', 0.0)
        epistemic_uncertainty = uncertainty.get('epistemic_std', 0.0)
        aleatoric_uncertainty = uncertainty.get('aleatoric_std', 0.0)
        
        # Determine uncertainty level
        if total_uncertainty < 0.1:
            uncertainty_level = 'low'
        elif total_uncertainty < 0.5:
            uncertainty_level = 'medium'
        else:
            uncertainty_level = 'high'
        
        # Determine OOD severity
        if ood_score < 0.3:
            ood_severity = 'mild'
        elif ood_score < 0.7:
            ood_severity = 'moderate'
        else:
            ood_severity = 'severe'
        
        # Analyze prediction characteristics
        prediction_magnitude = np.mean(np.abs(prediction))
        prediction_variance = np.var(prediction)
        
        # Determine domain context
        domain = context.get('domain', 'general')
        risk_tolerance = context.get('risk_tolerance', 'medium')
        performance_requirements = context.get('performance_requirements', 'medium')
        
        return {
            'uncertainty_level': uncertainty_level,
            'ood_severity': ood_severity,
            'total_uncertainty': total_uncertainty,
            'epistemic_uncertainty': epistemic_uncertainty,
            'aleatoric_uncertainty': aleatoric_uncertainty,
            'prediction_magnitude': prediction_magnitude,
            'prediction_variance': prediction_variance,
            'domain': domain,
            'risk_tolerance': risk_tolerance,
            'performance_requirements': performance_requirements,
            'ood_score': ood_score
        }
    
    def _llm_decision_making(
        self,
        situation: Dict[str, Any],
        available_strategies: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use LLM for decision making."""
        
        # Create decision prompt
        prompt = f"""
        You are an AI decision maker for extrapolation strategies. Analyze the following situation and recommend the best strategy.
        
        Situation Analysis:
        - Uncertainty Level: {situation['uncertainty_level']} (total: {situation['total_uncertainty']:.4f})
        - OOD Severity: {situation['ood_severity']} (score: {situation['ood_score']:.4f})
        - Domain: {situation['domain']}
        - Risk Tolerance: {situation['risk_tolerance']}
        - Performance Requirements: {situation['performance_requirements']}
        - Prediction Magnitude: {situation['prediction_magnitude']:.4f}
        - Epistemic Uncertainty: {situation['epistemic_uncertainty']:.4f}
        - Aleatoric Uncertainty: {situation['aleatoric_uncertainty']:.4f}
        
        Available Strategies:
        {self._format_strategies(available_strategies)}
        
        Context: {json.dumps(context, indent=2)}
        
        Please recommend the best strategy and provide:
        1. The recommended strategy
        2. Detailed reasoning
        3. Confidence level (0-1)
        4. Alternative strategies to consider
        5. Potential risks and benefits
        """
        
        response = self.llm_assistant.provider.generate(prompt, max_tokens=500)
        
        # Parse response
        decision = self._parse_decision_response(response, available_strategies)
        
        return decision
    
    def _parse_decision_response(
        self,
        response: str,
        available_strategies: List[str]
    ) -> Dict[str, Any]:
        """Parse LLM response to extract decision information."""
        
        # Simple parsing - look for strategy names
        response_lower = response.lower()
        
        # Find recommended strategy
        recommended_strategy = available_strategies[0]  # Default
        for strategy in available_strategies:
            if strategy.lower() in response_lower:
                recommended_strategy = strategy
                break
        
        # Extract confidence (look for numbers between 0 and 1)
        import re
        confidence_matches = re.findall(r'confidence[:\s]*([0-9]*\.?[0-9]+)', response_lower)
        confidence = 0.7  # Default
        if confidence_matches:
            try:
                confidence = float(confidence_matches[0])
                confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
            except ValueError:
                pass
        
        # Extract alternative strategies
        alternatives = []
        for strategy in available_strategies:
            if strategy != recommended_strategy and strategy.lower() in response_lower:
                alternatives.append(strategy)
        
        return {
            'strategy': recommended_strategy,
            'reasoning': response,
            'confidence': confidence,
            'alternatives': alternatives,
            'raw_response': response
        }
    
    def _validate_decision(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and potentially adjust the decision."""
        
        strategy = decision['strategy']
        confidence = decision['confidence']
        
        # Check if strategy is appropriate for the context
        validation_checks = []
        
        # Check risk tolerance
        risk_tolerance = context.get('risk_tolerance', 'medium')
        if risk_tolerance == 'low' and strategy in ['warn', 'error']:
            validation_checks.append("Strategy may be too risky for low risk tolerance")
        
        # Check performance requirements
        performance_requirements = context.get('performance_requirements', 'medium')
        if performance_requirements == 'high' and strategy in ['zero', 'error']:
            validation_checks.append("Strategy may not meet high performance requirements")
        
        # Check computational constraints
        computational_cost = context.get('computational_cost', 'medium')
        if computational_cost == 'low' and strategy in ['deep_ensemble', 'llm_assist']:
            validation_checks.append("Strategy may be too computationally expensive")
        
        # Adjust confidence based on validation
        if validation_checks:
            confidence *= 0.8  # Reduce confidence if there are concerns
        
        decision['validation_checks'] = validation_checks
        decision['confidence'] = confidence
        decision['validated'] = len(validation_checks) == 0
        
        return decision
    
    def _format_strategies(self, strategies: List[str]) -> str:
        """Format available strategies for display."""
        formatted = []
        for strategy in strategies:
            description = self.strategies.get(strategy, strategy)
            formatted.append(f"- {strategy}: {description}")
        return "\n".join(formatted)
    
    def batch_decision_making(
        self,
        inputs: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Make decisions for multiple inputs efficiently.
        
        Args:
            inputs: List of input dictionaries with data, predictions, etc.
            context: Shared context for all decisions
            
        Returns:
            List of decision dictionaries
        """
        decisions = []
        
        for i, input_dict in enumerate(inputs):
            # Make individual decision
            decision = self.make_decision(
                input_dict['input_data'],
                input_dict['prediction'],
                input_dict['uncertainty'],
                input_dict['ood_score'],
                context,
                input_dict.get('available_strategies')
            )
            
            # Add input index
            decision['input_index'] = i
            decisions.append(decision)
        
        return decisions
    
    def explain_decision(
        self,
        decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """
        Generate a detailed explanation of a decision.
        
        Args:
            decision: Decision dictionary
            context: Context used for decision
            
        Returns:
            Detailed explanation
        """
        prompt = f"""
        Explain the following decision in detail:
        
        Decision: {decision['strategy']}
        Confidence: {decision['confidence']:.3f}
        Reasoning: {decision['reasoning']}
        
        Context: {json.dumps(context, indent=2)}
        
        Please provide:
        1. Why this strategy was chosen
        2. How the context influenced the decision
        3. What the confidence level means
        4. What to expect from this strategy
        5. When to reconsider this decision
        """
        
        explanation = self.llm_assistant.provider.generate(prompt, max_tokens=400)
        return explanation
    
    def get_decision_statistics(
        self,
        decisions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about a set of decisions.
        
        Args:
            decisions: List of decision dictionaries
            
        Returns:
            Statistics dictionary
        """
        if not decisions:
            return {}
        
        # Count strategies
        strategy_counts = {}
        confidences = []
        validated_count = 0
        
        for decision in decisions:
            strategy = decision['strategy']
            strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1
            confidences.append(decision['confidence'])
            if decision.get('validated', False):
                validated_count += 1
        
        return {
            'total_decisions': len(decisions),
            'strategy_distribution': strategy_counts,
            'average_confidence': np.mean(confidences),
            'confidence_std': np.std(confidences),
            'min_confidence': np.min(confidences),
            'max_confidence': np.max(confidences),
            'validated_decisions': validated_count,
            'validation_rate': validated_count / len(decisions)
        }
