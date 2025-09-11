"""
LLM Assistant for intelligent OOD handling and decision making.

This module provides the core LLM integration for XtrapNet, enabling
natural language understanding and generation for extrapolation scenarios.
"""

from __future__ import annotations

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any
import json
import re
from abc import ABC, abstractmethod
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate text from a prompt."""
        pass
    
    @abstractmethod
    def embed(self, text: str) -> np.ndarray:
        """Generate embeddings for text."""
        pass


class LocalLLMProvider(LLMProvider):
    """Local LLM provider using transformers library."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-small"):
        self.model_name = model_name
        self.tokenizer = None
        self.model = None
        self.generator = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the local model."""
        if not TRANSFORMERS_AVAILABLE:
            raise ImportError("transformers library not available. Install with: pip install transformers")
        
        try:
            # Use a small, fast model that doesn't require much memory
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            
            # Add padding token if it doesn't exist
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Set model to eval mode
            self.model.eval()
            
        except Exception as e:
            print(f"Warning: Could not load {self.model_name}: {e}")
            print("Falling back to simple rule-based responses")
            self.tokenizer = None
            self.model = None
    
    def generate(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate text from a prompt."""
        if self.model is None or self.tokenizer is None:
            return self._fallback_generate(prompt)
        
        try:
            # Truncate prompt if too long
            if len(prompt) > 500:
                prompt = prompt[:500] + "..."
            
            # Tokenize input
            inputs = self.tokenizer.encode(prompt, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + max_tokens,
                    num_return_sequences=1,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.eos_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode generated text
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Remove the original prompt from the response
            if generated_text.startswith(prompt):
                generated_text = generated_text[len(prompt):].strip()
            
            # Clean up the response
            generated_text = self._clean_response(generated_text)
            
            return generated_text if generated_text else self._fallback_generate(prompt)
            
        except Exception as e:
            print(f"Generation error: {e}")
            return self._fallback_generate(prompt)
    
    def _fallback_generate(self, prompt: str) -> str:
        """Fallback generation using simple rules."""
        prompt_lower = prompt.lower()
        
        if "ood" in prompt_lower or "out of distribution" in prompt_lower:
            return "This appears to be an out-of-distribution sample. The model is uncertain about this prediction and recommends caution."
        elif "uncertainty" in prompt_lower:
            return "The uncertainty is high due to limited training data in this region. Consider gathering more data or using a more conservative approach."
        elif "explain" in prompt_lower:
            return "The prediction is based on the model's learned patterns from training data. The model's confidence may be reduced for inputs that differ significantly from the training distribution."
        elif "recommend" in prompt_lower:
            return "I recommend using a more conservative approach, such as clipping predictions to known ranges or using ensemble methods for better reliability."
        elif "strategy" in prompt_lower:
            return "Based on the uncertainty levels and OOD detection, a conservative strategy like 'clip' or 'warn' would be appropriate to ensure safe predictions."
        else:
            return "The model has processed your request and suggests proceeding with caution given the uncertainty in the current prediction."
    
    def _clean_response(self, text: str) -> str:
        """Clean up the generated response."""
        # Remove common artifacts
        text = text.replace("<|endoftext|>", "")
        text = text.replace("<|startoftext|>", "")
        
        # Remove repeated phrases
        sentences = text.split(".")
        unique_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence not in unique_sentences:
                unique_sentences.append(sentence)
        
        # Limit length
        if len(unique_sentences) > 3:
            unique_sentences = unique_sentences[:3]
        
        return ". ".join(unique_sentences) + ("." if unique_sentences else "")
    
    def embed(self, text: str) -> np.ndarray:
        """Generate embeddings for text."""
        if self.tokenizer is None:
            # Fallback to simple hash-based embedding
            hash_val = hash(text) % (2**32)
            embedding = np.random.randn(384)
            embedding[0] = hash_val / (2**32)
            return embedding
        
        try:
            # Tokenize and get embeddings from the model
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                # Use the last hidden state and average over sequence length
                embeddings = outputs.hidden_states[-1].mean(dim=1).squeeze().numpy()
            
            return embeddings
            
        except Exception as e:
            print(f"Embedding error: {e}")
            # Fallback to simple hash-based embedding
            hash_val = hash(text) % (2**32)
            embedding = np.random.randn(384)
            embedding[0] = hash_val / (2**32)
            return embedding


class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing and development."""
    
    def __init__(self, model_name: str = "mock-llm"):
        self.model_name = model_name
    
    def generate(self, prompt: str, max_tokens: int = 100) -> str:
        """Generate mock response based on prompt content."""
        return LocalLLMProvider()._fallback_generate(prompt)
    
    def embed(self, text: str) -> np.ndarray:
        """Generate mock embeddings."""
        # Simple hash-based embedding for testing
        hash_val = hash(text) % (2**32)
        embedding = np.random.randn(384)  # Standard embedding size
        embedding[0] = hash_val / (2**32)  # Make it deterministic
        return embedding


class LLMAssistant:
    """
    LLM Assistant for intelligent OOD handling and decision making.
    
    This class provides natural language interfaces for:
    - Explaining OOD predictions
    - Making decisions about extrapolation strategies
    - Providing domain knowledge
    - Generating human-readable uncertainty reports
    """
    
    def __init__(
        self,
        provider: Optional[LLMProvider] = None,
        model_name: str = "microsoft/DialoGPT-small",
        max_tokens: int = 200,
        temperature: float = 0.7
    ):
        """
        Initialize LLM Assistant.
        
        Args:
            provider: LLM provider instance
            model_name: Name of the LLM model
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
        """
        if provider is None:
            try:
                self.provider = LocalLLMProvider(model_name)
            except ImportError:
                print("Warning: transformers not available, using mock provider")
                self.provider = MockLLMProvider(model_name)
        else:
            self.provider = provider
        
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Knowledge base for domain-specific information
        self.knowledge_base = {}
        
        # Conversation history
        self.conversation_history = []
        
        # Templates for different types of interactions
        self.templates = {
            'ood_explanation': """
            The model has encountered an out-of-distribution input with the following characteristics:
            - Input features: {features}
            - Prediction: {prediction}
            - Uncertainty: {uncertainty}
            - Confidence: {confidence}
            
            Please explain what this means and provide recommendations.
            """,
            
            'uncertainty_analysis': """
            Analyze the following uncertainty information:
            - Epistemic uncertainty: {epistemic}
            - Aleatoric uncertainty: {aleatoric}
            - Total uncertainty: {total}
            - Prediction: {prediction}
            
            What does this uncertainty tell us about the model's confidence?
            """,
            
            'decision_support': """
            The model needs to make a decision about handling an OOD input:
            - Input: {input}
            - Available strategies: {strategies}
            - Context: {context}
            
            Which strategy would you recommend and why?
            """,
            
            'domain_knowledge': """
            The model is operating in the domain: {domain}
            Input characteristics: {characteristics}
            
            What domain-specific knowledge should be considered?
            """
        }
    
    def explain_ood_prediction(
        self,
        input_features: Union[np.ndarray, torch.Tensor],
        prediction: Union[np.ndarray, torch.Tensor],
        uncertainty: Dict[str, float],
        confidence: float
    ) -> str:
        """
        Generate natural language explanation for OOD prediction.
        
        Args:
            input_features: Input features that caused OOD
            prediction: Model prediction
            uncertainty: Uncertainty components
            confidence: Confidence score
            
        Returns:
            Natural language explanation
        """
        # Convert tensors to numpy if needed
        if isinstance(input_features, torch.Tensor):
            input_features = input_features.detach().numpy()
        if isinstance(prediction, torch.Tensor):
            prediction = prediction.detach().numpy()
        
        # Format features for display
        features_str = self._format_features(input_features)
        prediction_str = self._format_prediction(prediction)
        uncertainty_str = self._format_uncertainty(uncertainty)
        
        # Create prompt
        prompt = self.templates['ood_explanation'].format(
            features=features_str,
            prediction=prediction_str,
            uncertainty=uncertainty_str,
            confidence=f"{confidence:.3f}"
        )
        
        # Generate explanation
        explanation = self.provider.generate(prompt, self.max_tokens)
        
        # Store in conversation history
        self.conversation_history.append({
            'type': 'ood_explanation',
            'input': input_features,
            'explanation': explanation
        })
        
        return explanation
    
    def analyze_uncertainty(
        self,
        epistemic_uncertainty: float,
        aleatoric_uncertainty: float,
        total_uncertainty: float,
        prediction: Union[np.ndarray, torch.Tensor]
    ) -> str:
        """
        Generate uncertainty analysis in natural language.
        
        Args:
            epistemic_uncertainty: Model uncertainty
            aleatoric_uncertainty: Data uncertainty
            total_uncertainty: Total uncertainty
            prediction: Model prediction
            
        Returns:
            Natural language uncertainty analysis
        """
        if isinstance(prediction, torch.Tensor):
            prediction = prediction.detach().numpy()
        
        prediction_str = self._format_prediction(prediction)
        
        # Create prompt
        prompt = self.templates['uncertainty_analysis'].format(
            epistemic=f"{epistemic_uncertainty:.4f}",
            aleatoric=f"{aleatoric_uncertainty:.4f}",
            total=f"{total_uncertainty:.4f}",
            prediction=prediction_str
        )
        
        # Generate analysis
        analysis = self.provider.generate(prompt, self.max_tokens)
        
        # Store in conversation history
        self.conversation_history.append({
            'type': 'uncertainty_analysis',
            'uncertainty': {
                'epistemic': epistemic_uncertainty,
                'aleatoric': aleatoric_uncertainty,
                'total': total_uncertainty
            },
            'analysis': analysis
        })
        
        return analysis
    
    def recommend_strategy(
        self,
        input_data: Union[np.ndarray, torch.Tensor],
        available_strategies: List[str],
        context: Dict[str, Any]
    ) -> Tuple[str, str]:
        """
        Recommend an extrapolation strategy using LLM reasoning.
        
        Args:
            input_data: Input that needs handling
            available_strategies: List of available strategies
            context: Additional context information
            
        Returns:
            (recommended_strategy, reasoning)
        """
        if isinstance(input_data, torch.Tensor):
            input_data = input_data.detach().numpy()
        
        input_str = self._format_features(input_data)
        strategies_str = ", ".join(available_strategies)
        context_str = json.dumps(context, indent=2)
        
        # Create prompt
        prompt = self.templates['decision_support'].format(
            input=input_str,
            strategies=strategies_str,
            context=context_str
        )
        
        # Generate recommendation
        response = self.provider.generate(prompt, self.max_tokens)
        
        # Parse response to extract strategy and reasoning
        recommended_strategy, reasoning = self._parse_recommendation(response, available_strategies)
        
        # Store in conversation history
        self.conversation_history.append({
            'type': 'strategy_recommendation',
            'input': input_data,
            'strategies': available_strategies,
            'recommended': recommended_strategy,
            'reasoning': reasoning
        })
        
        return recommended_strategy, reasoning
    
    def get_domain_knowledge(
        self,
        domain: str,
        input_characteristics: Dict[str, Any]
    ) -> str:
        """
        Get domain-specific knowledge for better decision making.
        
        Args:
            domain: Domain name (e.g., "fluid_dynamics", "finance")
            input_characteristics: Characteristics of the input
            
        Returns:
            Domain knowledge in natural language
        """
        characteristics_str = json.dumps(input_characteristics, indent=2)
        
        # Create prompt
        prompt = self.templates['domain_knowledge'].format(
            domain=domain,
            characteristics=characteristics_str
        )
        
        # Generate domain knowledge
        knowledge = self.provider.generate(prompt, self.max_tokens)
        
        # Store in conversation history
        self.conversation_history.append({
            'type': 'domain_knowledge',
            'domain': domain,
            'knowledge': knowledge
        })
        
        return knowledge
    
    def generate_uncertainty_report(
        self,
        predictions: List[Dict[str, Any]],
        uncertainty_metrics: Dict[str, float]
    ) -> str:
        """
        Generate a comprehensive uncertainty report.
        
        Args:
            predictions: List of predictions with uncertainty
            uncertainty_metrics: Overall uncertainty metrics
            
        Returns:
            Comprehensive uncertainty report
        """
        report_parts = []
        
        # Header
        report_parts.append("# Uncertainty Analysis Report")
        report_parts.append("")
        
        # Summary metrics
        report_parts.append("## Summary Metrics")
        for metric, value in uncertainty_metrics.items():
            report_parts.append(f"- **{metric}**: {value:.4f}")
        report_parts.append("")
        
        # Individual predictions
        report_parts.append("## Individual Predictions")
        for i, pred in enumerate(predictions):
            report_parts.append(f"### Prediction {i+1}")
            report_parts.append(f"- **Value**: {pred.get('value', 'N/A')}")
            report_parts.append(f"- **Uncertainty**: {pred.get('uncertainty', 'N/A')}")
            report_parts.append(f"- **Confidence**: {pred.get('confidence', 'N/A')}")
            
            if 'explanation' in pred:
                report_parts.append(f"- **Explanation**: {pred['explanation']}")
            report_parts.append("")
        
        # LLM analysis
        report_parts.append("## AI Analysis")
        analysis_prompt = f"""
        Analyze the following uncertainty report and provide insights:
        
        Summary Metrics: {uncertainty_metrics}
        Number of predictions: {len(predictions)}
        
        What are the key insights and recommendations?
        """
        
        analysis = self.provider.generate(analysis_prompt, self.max_tokens)
        report_parts.append(analysis)
        
        return "\n".join(report_parts)
    
    def _format_features(self, features: np.ndarray) -> str:
        """Format input features for display."""
        if features.ndim == 1:
            return f"[{', '.join([f'{x:.3f}' for x in features])}]"
        else:
            return f"Shape: {features.shape}, Values: {features.flatten()[:5]}..."
    
    def _format_prediction(self, prediction: np.ndarray) -> str:
        """Format prediction for display."""
        if prediction.ndim == 1:
            return f"[{', '.join([f'{x:.3f}' for x in prediction])}]"
        else:
            return f"Shape: {prediction.shape}, Values: {prediction.flatten()[:5]}..."
    
    def _format_uncertainty(self, uncertainty: Dict[str, float]) -> str:
        """Format uncertainty for display."""
        return ", ".join([f"{k}: {v:.4f}" for k, v in uncertainty.items()])
    
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
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []
    
    def add_knowledge(self, domain: str, knowledge: str):
        """Add domain knowledge to the knowledge base."""
        if domain not in self.knowledge_base:
            self.knowledge_base[domain] = []
        self.knowledge_base[domain].append(knowledge)
    
    def get_knowledge(self, domain: str) -> List[str]:
        """Get knowledge for a specific domain."""
        return self.knowledge_base.get(domain, [])
