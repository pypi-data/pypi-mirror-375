"""
Deployment Tools for production deployment of XtrapNet anomaly detection.

This module provides utilities and tools for deploying XtrapNet's anomaly
detection capabilities in production environments.
"""

from __future__ import annotations

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
import json
import yaml
import pickle
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum
import time
import threading
from concurrent.futures import ThreadPoolExecutor
import queue


class DeploymentMode(Enum):
    """Deployment modes for anomaly detection."""
    BATCH = "batch"
    STREAMING = "streaming"
    API = "api"
    EMBEDDED = "embedded"


@dataclass
class DeploymentConfig:
    """Configuration for deployment."""
    mode: DeploymentMode
    model_path: str
    config_path: str
    output_path: str
    max_batch_size: int = 100
    max_latency_ms: float = 100.0
    enable_logging: bool = True
    log_level: str = "INFO"
    enable_monitoring: bool = True
    monitoring_interval: int = 60
    enable_explanations: bool = False
    cache_size: int = 1000


class DeploymentTools:
    """
    Deployment Tools for production deployment of XtrapNet anomaly detection.
    
    This class provides utilities and tools for deploying XtrapNet's anomaly
    detection capabilities in production environments.
    """
    
    def __init__(self, config: DeploymentConfig):
        """
        Initialize Deployment Tools.
        
        Args:
            config: Deployment configuration
        """
        self.config = config
        self.logger = self._setup_logging()
        self.model = None
        self.anomaly_detector = None
        self.monitor = None
        self.cache = {}
        self.is_deployed = False
        
        # Performance tracking
        self.performance_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_latency_ms': 0.0,
            'max_latency_ms': 0.0,
            'start_time': time.time()
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for deployment."""
        logger = logging.getLogger('xtrapnet_deployment')
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def deploy(
        self,
        anomaly_detector: Any,
        model_path: Optional[str] = None
    ) -> bool:
        """
        Deploy the anomaly detection system.
        
        Args:
            anomaly_detector: Anomaly detector to deploy
            model_path: Path to saved model (optional)
            
        Returns:
            True if deployment successful
        """
        try:
            self.logger.info(f"Starting deployment in {self.config.mode.value} mode")
            
            # Load or set anomaly detector
            if model_path:
                self.anomaly_detector = self._load_model(model_path)
            else:
                self.anomaly_detector = anomaly_detector
            
            # Setup monitoring if enabled
            if self.config.enable_monitoring:
                self._setup_monitoring()
            
            # Initialize based on deployment mode
            if self.config.mode == DeploymentMode.BATCH:
                self._setup_batch_deployment()
            elif self.config.mode == DeploymentMode.STREAMING:
                self._setup_streaming_deployment()
            elif self.config.mode == DeploymentMode.API:
                self._setup_api_deployment()
            elif self.config.mode == DeploymentMode.EMBEDDED:
                self._setup_embedded_deployment()
            
            self.is_deployed = True
            self.logger.info("Deployment completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Deployment failed: {e}")
            return False
    
    def _load_model(self, model_path: str) -> Any:
        """Load model from file."""
        self.logger.info(f"Loading model from {model_path}")
        
        if model_path.endswith('.pth') or model_path.endswith('.pt'):
            return torch.load(model_path)
        elif model_path.endswith('.pkl'):
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        elif model_path.endswith('.json'):
            with open(model_path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported model format: {model_path}")
    
    def _setup_monitoring(self):
        """Setup monitoring for deployment."""
        from .real_time_monitor import RealTimeMonitor
        
        self.monitor = RealTimeMonitor(
            anomaly_detector=self.anomaly_detector,
            max_latency_ms=self.config.max_latency_ms
        )
        self.monitor.start_monitoring()
    
    def _setup_batch_deployment(self):
        """Setup batch processing deployment."""
        self.logger.info("Setting up batch processing deployment")
        # Batch processing setup
        pass
    
    def _setup_streaming_deployment(self):
        """Setup streaming deployment."""
        self.logger.info("Setting up streaming deployment")
        # Streaming setup
        pass
    
    def _setup_api_deployment(self):
        """Setup API deployment."""
        self.logger.info("Setting up API deployment")
        # API setup
        pass
    
    def _setup_embedded_deployment(self):
        """Setup embedded deployment."""
        self.logger.info("Setting up embedded deployment")
        # Embedded setup
        pass
    
    def process_batch(
        self,
        data: List[Union[np.ndarray, torch.Tensor, Dict[str, Any]]],
        batch_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Process a batch of data for anomaly detection.
        
        Args:
            data: List of data samples to process
            batch_size: Batch size for processing
            
        Returns:
            List of anomaly detection results
        """
        if not self.is_deployed:
            raise RuntimeError("System not deployed")
        
        batch_size = batch_size or self.config.max_batch_size
        results = []
        
        self.logger.info(f"Processing batch of {len(data)} samples")
        
        # Process in chunks
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            batch_results = self._process_batch_chunk(batch)
            results.extend(batch_results)
        
        self._update_performance_stats(len(data), True)
        return results
    
    def _process_batch_chunk(
        self,
        batch: List[Union[np.ndarray, torch.Tensor, Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """Process a chunk of batch data."""
        results = []
        
        for sample in batch:
            try:
                start_time = time.time()
                
                # Get anomaly score
                if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
                    if isinstance(sample, dict):
                        score = self.anomaly_detector.get_combined_anomaly_score(sample)
                    else:
                        sample_dict = {list(self.anomaly_detector.detectors.keys())[0]: sample}
                        score = self.anomaly_detector.get_combined_anomaly_score(sample_dict)
                else:
                    score = self.anomaly_detector.get_anomaly_score(sample)
                
                latency_ms = (time.time() - start_time) * 1000
                
                result = {
                    'anomaly_score': score,
                    'is_anomalous': score > 0.5,  # Default threshold
                    'latency_ms': latency_ms,
                    'timestamp': time.time()
                }
                
                # Add explanations if enabled
                if self.config.enable_explanations:
                    from .explainable_anomaly import ExplainableAnomalyDetector
                    explainer = ExplainableAnomalyDetector(self.anomaly_detector)
                    explanations = explainer.explain_anomaly(sample)
                    result['explanations'] = [
                        {
                            'type': exp.explanation_type.value,
                            'description': exp.text_description,
                            'confidence': exp.confidence
                        }
                        for exp in explanations
                    ]
                
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Error processing sample: {e}")
                results.append({
                    'error': str(e),
                    'timestamp': time.time()
                })
        
        return results
    
    def process_stream(
        self,
        data_stream: queue.Queue,
        output_queue: queue.Queue,
        max_workers: int = 4
    ):
        """
        Process streaming data for anomaly detection.
        
        Args:
            data_stream: Input data queue
            output_queue: Output results queue
            max_workers: Maximum number of worker threads
        """
        if not self.is_deployed:
            raise RuntimeError("System not deployed")
        
        self.logger.info(f"Starting stream processing with {max_workers} workers")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while True:
                try:
                    # Get data from stream
                    data_item = data_stream.get(timeout=1.0)
                    
                    # Process data
                    future = executor.submit(self._process_stream_item, data_item)
                    result = future.result(timeout=self.config.max_latency_ms / 1000.0)
                    
                    # Put result in output queue
                    output_queue.put(result)
                    
                    data_stream.task_done()
                    
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Error in stream processing: {e}")
    
    def _process_stream_item(
        self,
        data_item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process a single stream item."""
        try:
            start_time = time.time()
            data = data_item['data']
            
            # Get anomaly score
            if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
                if isinstance(data, dict):
                    score = self.anomaly_detector.get_combined_anomaly_score(data)
                else:
                    data_dict = {list(self.anomaly_detector.detectors.keys())[0]: data}
                    score = self.anomaly_detector.get_combined_anomaly_score(data_dict)
            else:
                score = self.anomaly_detector.get_anomaly_score(data)
            
            latency_ms = (time.time() - start_time) * 1000
            
            result = {
                'id': data_item.get('id', 'unknown'),
                'anomaly_score': score,
                'is_anomalous': score > 0.5,
                'latency_ms': latency_ms,
                'timestamp': time.time()
            }
            
            # Add to monitoring if available
            if self.monitor:
                self.monitor.process_data(
                    data,
                    data_item.get('data_type', 'unknown'),
                    data_item.get('metadata', {})
                )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing stream item: {e}")
            return {
                'id': data_item.get('id', 'unknown'),
                'error': str(e),
                'timestamp': time.time()
            }
    
    def create_api_endpoint(self, port: int = 8000) -> Any:
        """
        Create API endpoint for anomaly detection.
        
        Args:
            port: Port for API server
            
        Returns:
            API server instance
        """
        try:
            from flask import Flask, request, jsonify
            
            app = Flask(__name__)
            
            @app.route('/health', methods=['GET'])
            def health_check():
                return jsonify({
                    'status': 'healthy',
                    'deployed': self.is_deployed,
                    'uptime': time.time() - self.performance_stats['start_time']
                })
            
            @app.route('/predict', methods=['POST'])
            def predict():
                try:
                    data = request.json
                    
                    # Process data
                    result = self._process_api_request(data)
                    
                    return jsonify(result)
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            @app.route('/batch_predict', methods=['POST'])
            def batch_predict():
                try:
                    data_list = request.json.get('data', [])
                    
                    # Process batch
                    results = self.process_batch(data_list)
                    
                    return jsonify({'results': results})
                    
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
            
            @app.route('/stats', methods=['GET'])
            def get_stats():
                return jsonify(self.get_performance_stats())
            
            self.logger.info(f"API server created on port {port}")
            return app
            
        except ImportError:
            self.logger.error("Flask not available for API deployment")
            return None
    
    def _process_api_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single API request."""
        start_time = time.time()
        
        # Extract data from request
        input_data = data.get('data')
        if not input_data:
            raise ValueError("No data provided in request")
        
        # Get anomaly score
        if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
            if isinstance(input_data, dict):
                score = self.anomaly_detector.get_combined_anomaly_score(input_data)
            else:
                input_dict = {list(self.anomaly_detector.detectors.keys())[0]: input_data}
                score = self.anomaly_detector.get_combined_anomaly_score(input_dict)
        else:
            score = self.anomaly_detector.get_anomaly_score(input_data)
        
        latency_ms = (time.time() - start_time) * 1000
        
        result = {
            'anomaly_score': score,
            'is_anomalous': score > 0.5,
            'latency_ms': latency_ms,
            'timestamp': time.time()
        }
        
        # Add explanations if requested
        if data.get('include_explanations', False) and self.config.enable_explanations:
            from .explainable_anomaly import ExplainableAnomalyDetector
            explainer = ExplainableAnomalyDetector(self.anomaly_detector)
            explanations = explainer.explain_anomaly(input_data)
            result['explanations'] = [
                {
                    'type': exp.explanation_type.value,
                    'description': exp.text_description,
                    'confidence': exp.confidence
                }
                for exp in explanations
            ]
        
        self._update_performance_stats(1, True)
        return result
    
    def _update_performance_stats(self, count: int, success: bool):
        """Update performance statistics."""
        self.performance_stats['total_requests'] += count
        if success:
            self.performance_stats['successful_requests'] += count
        else:
            self.performance_stats['failed_requests'] += count
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        uptime = time.time() - self.performance_stats['start_time']
        
        return {
            'uptime_seconds': uptime,
            'total_requests': self.performance_stats['total_requests'],
            'successful_requests': self.performance_stats['successful_requests'],
            'failed_requests': self.performance_stats['failed_requests'],
            'success_rate': (
                self.performance_stats['successful_requests'] / 
                self.performance_stats['total_requests']
                if self.performance_stats['total_requests'] > 0 else 0
            ),
            'requests_per_second': (
                self.performance_stats['total_requests'] / uptime
                if uptime > 0 else 0
            ),
            'deployment_mode': self.config.mode.value,
            'is_deployed': self.is_deployed
        }
    
    def save_deployment_config(self, filepath: str):
        """Save deployment configuration to file."""
        config_dict = asdict(self.config)
        
        if filepath.endswith('.yaml') or filepath.endswith('.yml'):
            with open(filepath, 'w') as f:
                yaml.dump(config_dict, f, default_flow_style=False)
        else:
            with open(filepath, 'w') as f:
                json.dump(config_dict, f, indent=2)
        
        self.logger.info(f"Deployment config saved to {filepath}")
    
    def load_deployment_config(self, filepath: str) -> DeploymentConfig:
        """Load deployment configuration from file."""
        if filepath.endswith('.yaml') or filepath.endswith('.yml'):
            with open(filepath, 'r') as f:
                config_dict = yaml.safe_load(f)
        else:
            with open(filepath, 'r') as f:
                config_dict = json.load(f)
        
        # Convert mode string back to enum
        if 'mode' in config_dict:
            config_dict['mode'] = DeploymentMode(config_dict['mode'])
        
        return DeploymentConfig(**config_dict)
    
    def create_deployment_package(
        self,
        output_dir: str,
        include_model: bool = True,
        include_config: bool = True
    ):
        """Create deployment package."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save model if requested
        if include_model and self.anomaly_detector:
            model_path = output_path / "model.pth"
            torch.save(self.anomaly_detector, model_path)
            self.logger.info(f"Model saved to {model_path}")
        
        # Save config if requested
        if include_config:
            config_path = output_path / "deployment_config.yaml"
            self.save_deployment_config(str(config_path))
        
        # Create requirements file
        requirements_path = output_path / "requirements.txt"
        with open(requirements_path, 'w') as f:
            f.write("torch>=2.0.0\n")
            f.write("numpy>=1.21.0\n")
            f.write("scikit-learn>=1.0.0\n")
            f.write("flask>=2.0.0\n")
            f.write("pyyaml>=6.0\n")
        
        # Create deployment script
        script_path = output_path / "deploy.py"
        with open(script_path, 'w') as f:
            f.write("""
#!/usr/bin/env python3
import torch
from xtrapnet.anomaly.deployment_tools import DeploymentTools, DeploymentConfig, DeploymentMode

def main():
    # Load deployment config
    config = DeploymentConfig(
        mode=DeploymentMode.API,
        model_path="model.pth",
        config_path="deployment_config.yaml",
        output_path="output",
        enable_logging=True,
        enable_monitoring=True
    )
    
    # Create deployment tools
    deployment = DeploymentTools(config)
    
    # Load model and deploy
    model = torch.load("model.pth")
    deployment.deploy(model)
    
    # Create API endpoint
    app = deployment.create_api_endpoint(port=8000)
    if app:
        app.run(host='0.0.0.0', port=8000)

if __name__ == "__main__":
    main()
""")
        
        self.logger.info(f"Deployment package created in {output_dir}")
    
    def shutdown(self):
        """Shutdown deployment."""
        if self.monitor:
            self.monitor.stop_monitoring()
        
        self.is_deployed = False
        self.logger.info("Deployment shutdown completed")
