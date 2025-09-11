"""
Real-Time Monitor for low-latency anomaly detection in production environments.

This module provides optimized algorithms and monitoring capabilities for
real-time anomaly detection with minimal latency.
"""

from __future__ import annotations

import torch
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
import time
import threading
import queue
from collections import deque
from dataclasses import dataclass
from enum import Enum


class AlertLevel(Enum):
    """Alert levels for anomaly detection."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class AnomalyAlert:
    """Anomaly alert data structure."""
    timestamp: float
    anomaly_score: float
    alert_level: AlertLevel
    data_type: str
    description: str
    metadata: Dict[str, Any]


class RealTimeMonitor:
    """
    Real-Time Monitor for low-latency anomaly detection.
    
    This class provides optimized monitoring capabilities for real-time
    anomaly detection in production environments.
    """
    
    def __init__(
        self,
        anomaly_detector: Any,
        alert_thresholds: Optional[Dict[AlertLevel, float]] = None,
        max_latency_ms: float = 100.0,
        buffer_size: int = 1000,
        enable_streaming: bool = True
    ):
        """
        Initialize Real-Time Monitor.
        
        Args:
            anomaly_detector: Anomaly detector instance
            alert_thresholds: Thresholds for different alert levels
            max_latency_ms: Maximum allowed latency in milliseconds
            buffer_size: Size of data buffer
            enable_streaming: Whether to enable streaming mode
        """
        self.anomaly_detector = anomaly_detector
        self.max_latency_ms = max_latency_ms
        self.buffer_size = buffer_size
        self.enable_streaming = enable_streaming
        
        # Alert thresholds
        self.alert_thresholds = alert_thresholds or {
            AlertLevel.LOW: 0.3,
            AlertLevel.MEDIUM: 0.5,
            AlertLevel.HIGH: 0.7,
            AlertLevel.CRITICAL: 0.9
        }
        
        # Data buffers
        self.data_buffer = deque(maxlen=buffer_size)
        self.alert_buffer = deque(maxlen=buffer_size)
        
        # Performance tracking
        self.latency_history = deque(maxlen=100)
        self.throughput_history = deque(maxlen=100)
        self.alert_history = deque(maxlen=1000)
        
        # Streaming components
        self.data_queue = queue.Queue(maxsize=buffer_size)
        self.processing_thread = None
        self.is_running = False
        
        # Statistics
        self.total_processed = 0
        self.total_alerts = 0
        self.start_time = time.time()
    
    def start_monitoring(self):
        """Start real-time monitoring."""
        if self.enable_streaming:
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._streaming_processor)
            self.processing_thread.daemon = True
            self.processing_thread.start()
    
    def stop_monitoring(self):
        """Stop real-time monitoring."""
        self.is_running = False
        if self.processing_thread:
            self.processing_thread.join()
    
    def process_data(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]],
        data_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> AnomalyAlert:
        """
        Process data for real-time anomaly detection.
        
        Args:
            data: Input data to analyze
            data_type: Type of data
            metadata: Additional metadata
            
        Returns:
            Anomaly alert if anomaly detected
        """
        start_time = time.time()
        
        # Get anomaly score
        if hasattr(self.anomaly_detector, 'get_combined_anomaly_score'):
            # Multi-modal detector
            if isinstance(data, dict):
                anomaly_score = self.anomaly_detector.get_combined_anomaly_score(data)
            else:
                # Convert single data to dict format
                data_dict = {list(self.anomaly_detector.detectors.keys())[0]: data}
                anomaly_score = self.anomaly_detector.get_combined_anomaly_score(data_dict)
        else:
            # Single-modal detector
            anomaly_score = self.anomaly_detector.get_anomaly_score(data)
        
        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        self.latency_history.append(latency_ms)
        
        # Update statistics
        self.total_processed += 1
        
        # Determine alert level
        alert_level = self._determine_alert_level(anomaly_score)
        
        # Create alert if threshold exceeded
        alert = None
        if alert_level != AlertLevel.LOW or anomaly_score > self.alert_thresholds[AlertLevel.LOW]:
            alert = AnomalyAlert(
                timestamp=time.time(),
                anomaly_score=anomaly_score,
                alert_level=alert_level,
                data_type=data_type,
                description=self._generate_alert_description(anomaly_score, alert_level),
                metadata=metadata or {}
            )
            
            self.alert_buffer.append(alert)
            self.alert_history.append(alert)
            self.total_alerts += 1
        
        # Add to data buffer
        self.data_buffer.append({
            'timestamp': time.time(),
            'data': data,
            'anomaly_score': anomaly_score,
            'alert_level': alert_level,
            'latency_ms': latency_ms
        })
        
        return alert
    
    def process_stream(
        self,
        data: Union[np.ndarray, torch.Tensor, Dict[str, Any]],
        data_type: str = "unknown",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add data to streaming processing queue.
        
        Args:
            data: Input data to analyze
            data_type: Type of data
            metadata: Additional metadata
            
        Returns:
            True if data was queued successfully
        """
        if not self.enable_streaming:
            raise ValueError("Streaming mode is not enabled")
        
        try:
            self.data_queue.put_nowait({
                'data': data,
                'data_type': data_type,
                'metadata': metadata,
                'timestamp': time.time()
            })
            return True
        except queue.Full:
            return False
    
    def _streaming_processor(self):
        """Process data from streaming queue."""
        while self.is_running:
            try:
                # Get data from queue with timeout
                item = self.data_queue.get(timeout=1.0)
                
                # Process data
                alert = self.process_data(
                    item['data'],
                    item['data_type'],
                    item['metadata']
                )
                
                # Handle alert if generated
                if alert:
                    self._handle_alert(alert)
                
                self.data_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error in streaming processor: {e}")
    
    def _determine_alert_level(self, anomaly_score: float) -> AlertLevel:
        """Determine alert level based on anomaly score."""
        if anomaly_score >= self.alert_thresholds[AlertLevel.CRITICAL]:
            return AlertLevel.CRITICAL
        elif anomaly_score >= self.alert_thresholds[AlertLevel.HIGH]:
            return AlertLevel.HIGH
        elif anomaly_score >= self.alert_thresholds[AlertLevel.MEDIUM]:
            return AlertLevel.MEDIUM
        else:
            return AlertLevel.LOW
    
    def _generate_alert_description(
        self,
        anomaly_score: float,
        alert_level: AlertLevel
    ) -> str:
        """Generate description for alert."""
        descriptions = {
            AlertLevel.LOW: f"Low-level anomaly detected (score: {anomaly_score:.3f})",
            AlertLevel.MEDIUM: f"Medium-level anomaly detected (score: {anomaly_score:.3f})",
            AlertLevel.HIGH: f"High-level anomaly detected (score: {anomaly_score:.3f})",
            AlertLevel.CRITICAL: f"CRITICAL anomaly detected (score: {anomaly_score:.3f})"
        }
        return descriptions[alert_level]
    
    def _handle_alert(self, alert: AnomalyAlert):
        """Handle generated alert."""
        # Default alert handling - can be overridden
        print(f"ALERT [{alert.alert_level.value.upper()}]: {alert.description}")
        
        # In production, this would trigger notifications, logging, etc.
        if alert.alert_level in [AlertLevel.HIGH, AlertLevel.CRITICAL]:
            self._trigger_emergency_protocols(alert)
    
    def _trigger_emergency_protocols(self, alert: AnomalyAlert):
        """Trigger emergency protocols for critical alerts."""
        # Placeholder for emergency protocols
        print(f"EMERGENCY PROTOCOL TRIGGERED: {alert.description}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get real-time performance metrics."""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Calculate throughput
        throughput = self.total_processed / uptime if uptime > 0 else 0
        
        # Calculate average latency
        avg_latency = np.mean(self.latency_history) if self.latency_history else 0
        
        # Calculate alert rate
        alert_rate = self.total_alerts / self.total_processed if self.total_processed > 0 else 0
        
        # Check if latency requirements are met
        latency_compliance = avg_latency <= self.max_latency_ms
        
        return {
            'uptime_seconds': uptime,
            'total_processed': self.total_processed,
            'total_alerts': self.total_alerts,
            'throughput_per_second': throughput,
            'average_latency_ms': avg_latency,
            'max_latency_ms': max(self.latency_history) if self.latency_history else 0,
            'alert_rate': alert_rate,
            'latency_compliance': latency_compliance,
            'buffer_utilization': len(self.data_buffer) / self.buffer_size,
            'queue_size': self.data_queue.qsize() if self.enable_streaming else 0
        }
    
    def get_alert_summary(self, time_window_minutes: int = 60) -> Dict[str, Any]:
        """Get summary of alerts in the specified time window."""
        current_time = time.time()
        window_start = current_time - (time_window_minutes * 60)
        
        # Filter alerts within time window
        recent_alerts = [
            alert for alert in self.alert_history
            if alert.timestamp >= window_start
        ]
        
        # Count alerts by level
        alert_counts = {level: 0 for level in AlertLevel}
        for alert in recent_alerts:
            alert_counts[alert.alert_level] += 1
        
        # Calculate average anomaly score
        avg_score = np.mean([alert.anomaly_score for alert in recent_alerts]) if recent_alerts else 0
        
        return {
            'time_window_minutes': time_window_minutes,
            'total_alerts': len(recent_alerts),
            'alert_counts': {level.value: count for level, count in alert_counts.items()},
            'average_anomaly_score': avg_score,
            'most_common_data_type': self._get_most_common_data_type(recent_alerts)
        }
    
    def _get_most_common_data_type(self, alerts: List[AnomalyAlert]) -> str:
        """Get the most common data type in alerts."""
        if not alerts:
            return "none"
        
        data_types = [alert.data_type for alert in alerts]
        return max(set(data_types), key=data_types.count)
    
    def set_alert_thresholds(self, thresholds: Dict[AlertLevel, float]):
        """Update alert thresholds."""
        self.alert_thresholds.update(thresholds)
    
    def get_recent_alerts(self, n: int = 10) -> List[AnomalyAlert]:
        """Get the most recent alerts."""
        return list(self.alert_history)[-n:]
    
    def clear_buffers(self):
        """Clear all buffers."""
        self.data_buffer.clear()
        self.alert_buffer.clear()
        self.latency_history.clear()
        self.throughput_history.clear()
        self.alert_history.clear()
        
        # Clear queue
        while not self.data_queue.empty():
            try:
                self.data_queue.get_nowait()
            except queue.Empty:
                break
    
    def export_monitoring_data(self, filepath: str):
        """Export monitoring data to file."""
        data = {
            'performance_metrics': self.get_performance_metrics(),
            'alert_summary': self.get_alert_summary(),
            'recent_alerts': [
                {
                    'timestamp': alert.timestamp,
                    'anomaly_score': alert.anomaly_score,
                    'alert_level': alert.alert_level.value,
                    'data_type': alert.data_type,
                    'description': alert.description,
                    'metadata': alert.metadata
                }
                for alert in self.get_recent_alerts(100)
            ],
            'alert_thresholds': {level.value: threshold for level, threshold in self.alert_thresholds.items()}
        }
        
        torch.save(data, filepath)
    
    def load_monitoring_data(self, filepath: str):
        """Load monitoring data from file."""
        data = torch.load(filepath)
        
        # Restore alert thresholds
        self.alert_thresholds = {
            AlertLevel(level): threshold
            for level, threshold in data['alert_thresholds'].items()
        }
        
        return data
