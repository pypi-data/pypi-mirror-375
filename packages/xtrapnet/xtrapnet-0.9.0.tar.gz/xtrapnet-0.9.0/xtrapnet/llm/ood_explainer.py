"""
OOD Explainer for natural language explanations of out-of-distribution scenarios.

This module provides intelligent explanations for why inputs are considered
out-of-distribution and what this means for predictions.
"""

from __future__ import annotations

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import json
from .llm_assistant import LLMAssistant


class OODExplainer:
    """
    OOD Explainer for natural language explanations of out-of-distribution scenarios.
    
    This class provides intelligent explanations for:
    - Why inputs are considered OOD
    - What this means for predictions
    - How to interpret uncertainty in OOD scenarios
    - Recommendations for handling OOD inputs
    """
    
    def __init__(self, llm_assistant: LLMAssistant):
        """
        Initialize OOD Explainer.
        
        Args:
            llm_assistant: LLM assistant for natural language generation
        """
        self.llm_assistant = llm_assistant
        
        # OOD detection methods and their explanations
        self.ood_methods = {
            'mahalanobis': 'Mahalanobis distance from training data distribution',
            'knn': 'Distance to k-nearest neighbors in training data',
            'isolation_forest': 'Isolation Forest anomaly detection',
            'one_class_svm': 'One-class SVM boundary detection',
            'autoencoder': 'Reconstruction error from autoencoder',
            'uncertainty': 'High predictive uncertainty from Bayesian model'
        }
        
        # Common OOD scenarios and explanations
        self.ood_scenarios = {
            'extrapolation': 'Input is outside the range of training data',
            'interpolation_gap': 'Input is in a region with sparse training data',
            'domain_shift': 'Input comes from a different domain than training',
            'adversarial': 'Input appears to be adversarially crafted',
            'corrupted': 'Input appears to be corrupted or noisy',
            'novel_class': 'Input represents a novel class not seen in training'
        }
    
    def explain_ood_detection(
        self,
        input_data: Union[np.ndarray, torch.Tensor],
        ood_score: float,
        detection_method: str,
        threshold: float,
        training_stats: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Explain why an input was detected as out-of-distribution.
        
        Args:
            input_data: Input that was detected as OOD
            ood_score: OOD detection score
            detection_method: Method used for OOD detection
            threshold: Threshold used for OOD detection
            training_stats: Statistics about training data
            
        Returns:
            Natural language explanation
        """
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().numpy()
        
        # Get method description
        method_description = self.ood_methods.get(detection_method, detection_method)
        
        # Create explanation prompt
        prompt = f"""
        An input has been detected as out-of-distribution using {detection_method}.
        
        Detection Details:
        - Method: {method_description}
        - OOD Score: {ood_score:.4f}
        - Threshold: {threshold:.4f}
        - Input: {self._format_input(input_data)}
        
        Training Data Statistics:
        {self._format_training_stats(training_stats)}
        
        Please explain:
        1. What this OOD detection means
        2. Why the input was flagged as OOD
        3. What this implies for the model's prediction
        4. What the user should consider
        """
        
        explanation = self.llm_assistant.provider.generate(prompt, max_tokens=300)
        
        return explanation
    
    def explain_ood_impact(
        self,
        input_data: Union[np.ndarray, torch.Tensor],
        prediction: Union[np.ndarray, torch.Tensor],
        uncertainty: Dict[str, float],
        ood_type: str,
        confidence: float
    ) -> str:
        """
        Explain the impact of OOD detection on predictions.
        
        Args:
            input_data: OOD input
            prediction: Model prediction
            uncertainty: Uncertainty components
            ood_type: Type of OOD scenario
            confidence: Confidence in the prediction
            
        Returns:
            Natural language explanation of impact
        """
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().numpy()
        if isinstance(prediction, torch.Tensor):
            prediction = prediction.detach().numpy()
        
        # Get OOD scenario description
        scenario_description = self.ood_scenarios.get(ood_type, ood_type)
        
        # Create impact explanation prompt
        prompt = f"""
        An out-of-distribution input has been processed with the following results:
        
        Input: {self._format_input(input_data)}
        Prediction: {self._format_prediction(prediction)}
        Uncertainty: {self._format_uncertainty(uncertainty)}
        OOD Type: {scenario_description}
        Confidence: {confidence:.3f}
        
        Please explain:
        1. How the OOD nature affects the prediction reliability
        2. What the uncertainty values mean in this context
        3. How confident we can be in this prediction
        4. What risks or limitations should be considered
        """
        
        explanation = self.llm_assistant.provider.generate(prompt, max_tokens=300)
        
        return explanation
    
    def explain_uncertainty_in_ood(
        self,
        epistemic_uncertainty: float,
        aleatoric_uncertainty: float,
        total_uncertainty: float,
        ood_score: float,
        context: Dict[str, Any]
    ) -> str:
        """
        Explain uncertainty components in the context of OOD detection.
        
        Args:
            epistemic_uncertainty: Model uncertainty
            aleatoric_uncertainty: Data uncertainty
            total_uncertainty: Total uncertainty
            ood_score: OOD detection score
            context: Additional context
            
        Returns:
            Natural language explanation of uncertainty in OOD context
        """
        # Create uncertainty explanation prompt
        prompt = f"""
        Analyze the uncertainty components for an out-of-distribution input:
        
        Uncertainty Breakdown:
        - Epistemic (Model) Uncertainty: {epistemic_uncertainty:.4f}
        - Aleatoric (Data) Uncertainty: {aleatoric_uncertainty:.4f}
        - Total Uncertainty: {total_uncertainty:.4f}
        - OOD Score: {ood_score:.4f}
        
        Context: {json.dumps(context, indent=2)}
        
        Please explain:
        1. What each uncertainty component means in OOD context
        2. How the OOD score relates to the uncertainty
        3. Whether the uncertainty is primarily from model or data
        4. What this tells us about prediction reliability
        5. How to interpret these values for decision making
        """
        
        explanation = self.llm_assistant.provider.generate(prompt, max_tokens=300)
        
        return explanation
    
    def recommend_ood_handling(
        self,
        input_data: Union[np.ndarray, torch.Tensor],
        ood_score: float,
        uncertainty: Dict[str, float],
        available_strategies: List[str],
        domain: str = "general"
    ) -> Tuple[str, str]:
        """
        Recommend how to handle an OOD input.
        
        Args:
            input_data: OOD input
            ood_score: OOD detection score
            uncertainty: Uncertainty components
            available_strategies: Available handling strategies
            domain: Domain context
            
        Returns:
            (recommended_strategy, reasoning)
        """
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().numpy()
        
        # Create recommendation prompt
        prompt = f"""
        Recommend how to handle an out-of-distribution input:
        
        Input: {self._format_input(input_data)}
        OOD Score: {ood_score:.4f}
        Uncertainty: {self._format_uncertainty(uncertainty)}
        Domain: {domain}
        Available Strategies: {', '.join(available_strategies)}
        
        Please recommend the best strategy and explain why, considering:
        1. The severity of the OOD detection
        2. The uncertainty levels
        3. The domain context
        4. The available options
        """
        
        response = self.llm_assistant.provider.generate(prompt, max_tokens=300)
        
        # Parse recommendation
        recommended_strategy, reasoning = self._parse_recommendation(response, available_strategies)
        
        return recommended_strategy, reasoning
    
    def generate_ood_report(
        self,
        ood_detections: List[Dict[str, Any]],
        summary_stats: Dict[str, float]
    ) -> str:
        """
        Generate a comprehensive OOD analysis report.
        
        Args:
            ood_detections: List of OOD detection results
            summary_stats: Summary statistics
            
        Returns:
            Comprehensive OOD report
        """
        report_parts = []
        
        # Header
        report_parts.append("# Out-of-Distribution Analysis Report")
        report_parts.append("")
        
        # Summary
        report_parts.append("## Summary")
        report_parts.append(f"- Total inputs analyzed: {summary_stats.get('total_inputs', 'N/A')}")
        report_parts.append(f"- OOD inputs detected: {summary_stats.get('ood_count', 'N/A')}")
        report_parts.append(f"- OOD rate: {summary_stats.get('ood_rate', 'N/A'):.2%}")
        report_parts.append(f"- Average OOD score: {summary_stats.get('avg_ood_score', 'N/A'):.4f}")
        report_parts.append("")
        
        # Individual detections
        report_parts.append("## Individual OOD Detections")
        for i, detection in enumerate(ood_detections):
            report_parts.append(f"### Detection {i+1}")
            report_parts.append(f"- **Input**: {detection.get('input', 'N/A')}")
            report_parts.append(f"- **OOD Score**: {detection.get('ood_score', 'N/A'):.4f}")
            report_parts.append(f"- **Method**: {detection.get('method', 'N/A')}")
            report_parts.append(f"- **Uncertainty**: {detection.get('uncertainty', 'N/A')}")
            
            if 'explanation' in detection:
                report_parts.append(f"- **Explanation**: {detection['explanation']}")
            
            if 'recommendation' in detection:
                report_parts.append(f"- **Recommendation**: {detection['recommendation']}")
            
            report_parts.append("")
        
        # AI Analysis
        report_parts.append("## AI Analysis")
        analysis_prompt = f"""
        Analyze the following OOD detection report:
        
        Summary: {summary_stats}
        Number of OOD detections: {len(ood_detections)}
        
        Provide insights about:
        1. Overall OOD patterns
        2. Common characteristics of OOD inputs
        3. Recommendations for improving the system
        4. Potential risks or concerns
        """
        
        analysis = self.llm_assistant.provider.generate(analysis_prompt, max_tokens=400)
        report_parts.append(analysis)
        
        return "\n".join(report_parts)
    
    def _format_input(self, input_data: np.ndarray) -> str:
        """Format input data for display."""
        if input_data.ndim == 1:
            return f"[{', '.join([f'{x:.3f}' for x in input_data])}]"
        else:
            return f"Shape: {input_data.shape}, Values: {input_data.flatten()[:5]}..."
    
    def _format_prediction(self, prediction: np.ndarray) -> str:
        """Format prediction for display."""
        if prediction.ndim == 1:
            return f"[{', '.join([f'{x:.3f}' for x in prediction])}]"
        else:
            return f"Shape: {prediction.shape}, Values: {prediction.flatten()[:5]}..."
    
    def _format_uncertainty(self, uncertainty: Dict[str, float]) -> str:
        """Format uncertainty for display."""
        return ", ".join([f"{k}: {v:.4f}" for k, v in uncertainty.items()])
    
    def _format_training_stats(self, stats: Optional[Dict[str, Any]]) -> str:
        """Format training statistics for display."""
        if stats is None:
            return "Not available"
        
        formatted = []
        for key, value in stats.items():
            if isinstance(value, (int, float)):
                formatted.append(f"- {key}: {value:.4f}")
            else:
                formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted)
    
    def _parse_recommendation(
        self,
        response: str,
        available_strategies: List[str]
    ) -> Tuple[str, str]:
        """Parse LLM response to extract strategy and reasoning."""
        # Simple parsing - look for strategy names in the response
        response_lower = response.lower()
        
        # Find which strategy is mentioned
        recommended_strategy = available_strategies[0]  # Default
        for strategy in available_strategies:
            if strategy.lower() in response_lower:
                recommended_strategy = strategy
                break
        
        # Extract reasoning (everything after the strategy)
        reasoning = response
        
        return recommended_strategy, reasoning
