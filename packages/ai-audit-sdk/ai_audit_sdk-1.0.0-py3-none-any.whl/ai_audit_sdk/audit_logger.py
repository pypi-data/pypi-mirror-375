import requests
import threading
import time
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin


class AuditLogger:
    """
    AI Audit Trail SDK for Python
    
    Logs AI/ML decisions to the audit backend for compliance tracking.
    All requests are sent asynchronously to avoid blocking your application.
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the AuditLogger.
        
        Args:
            api_key: Your AI Audit Trail API key (use sandbox API key for development/testing)
        """
        self.api_key = api_key
        # Production URL - cannot be overridden for security and revenue protection
        # For development/testing, use your sandbox tenant API key
        self.base_url = "https://explainableai.azurewebsites.net"
        
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'User-Agent': 'ai-audit-sdk-python/1.0.0'
        })

    def log_decision(self, 
                    input_text: str, 
                    output_text: str, 
                    model_name: str = "unknown",
                    metadata: Optional[Dict[str, Any]] = None,
                    confidence: Optional[float] = None,
                    response_time: Optional[int] = None,
                    provider: Optional[str] = None,
                    model_version: Optional[str] = None,
                    risk_level: Optional[str] = None,
                    prompt_tokens: Optional[int] = None,
                    completion_tokens: Optional[int] = None,
                    total_tokens: Optional[int] = None,
                    cost_micros: Optional[int] = None,
                    external_ref: Optional[str] = None,
                    data_subject_id: Optional[str] = None,
                    lawful_basis: Optional[str] = None,
                    automated_decision: Optional[bool] = None,
                    redact_pii: Optional[bool] = None,
                    priority: Optional[str] = None) -> None:
        """
        Log an AI decision asynchronously.
        
        Args:
            input_text: The input prompt or data sent to the AI model
            output_text: The output/response from the AI model
            model_name: Name/identifier of the AI model used
            metadata: Additional metadata (user_id, session_id, etc.)
            confidence: Model confidence score (0.0 to 1.0)
            response_time: Response time in milliseconds
            provider: AI provider (openai, anthropic, etc.)
            model_version: Version of the model
            risk_level: Risk level assessment (low, medium, high)
            prompt_tokens: Number of tokens in the prompt
            completion_tokens: Number of tokens in the completion
            total_tokens: Total number of tokens
            cost_micros: Cost in micros (millionths of currency unit)
            external_ref: External reference ID
            data_subject_id: ID of the data subject (for GDPR compliance)
            lawful_basis: Legal basis for processing (GDPR)
            automated_decision: Whether this is an automated decision
            redact_pii: Whether to redact PII from the data
            priority: Priority for processing (low, normal, high)
        """
        payload = {
            "input": input_text,
            "output": output_text,
            "modelName": model_name,
            "metadata": metadata or {},
            "confidence": confidence,
            "responseTime": response_time,
            "provider": provider,
            "modelVersion": model_version,
            "riskLevel": risk_level,
            "promptTokens": prompt_tokens,
            "completionTokens": completion_tokens,
            "totalTokens": total_tokens,
            "costMicros": cost_micros,
            "externalRef": external_ref,
            "dataSubjectId": data_subject_id,
            "lawfulBasis": lawful_basis,
            "automatedDecision": automated_decision,
            "redactPII": redact_pii,
            "priority": priority
        }
        
        # Remove None values to keep payload clean
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # Send asynchronously to avoid blocking the main application
        thread = threading.Thread(target=self._send_async, args=(payload,))
        thread.daemon = True  # Don't prevent program shutdown
        thread.start()

    def log_decision_sync(self, 
                         input_text: str, 
                         output_text: str, 
                         model_name: str = "unknown",
                         metadata: Optional[Dict[str, Any]] = None,
                         confidence: Optional[float] = None,
                         response_time: Optional[int] = None,
                         provider: Optional[str] = None,
                         model_version: Optional[str] = None,
                         risk_level: Optional[str] = None,
                         prompt_tokens: Optional[int] = None,
                         completion_tokens: Optional[int] = None,
                         total_tokens: Optional[int] = None,
                         cost_micros: Optional[int] = None,
                         external_ref: Optional[str] = None,
                         data_subject_id: Optional[str] = None,
                         lawful_basis: Optional[str] = None,
                         automated_decision: Optional[bool] = None,
                         redact_pii: Optional[bool] = None,
                         priority: Optional[str] = None) -> bool:
        """
        Log an AI decision synchronously (blocking).
        
        Returns:
            bool: True if successful, False otherwise
        """
        payload = {
            "input": input_text,
            "output": output_text,
            "modelName": model_name,
            "metadata": metadata or {},
            "confidence": confidence,
            "responseTime": response_time,
            "provider": provider,
            "modelVersion": model_version,
            "riskLevel": risk_level,
            "promptTokens": prompt_tokens,
            "completionTokens": completion_tokens,
            "totalTokens": total_tokens,
            "costMicros": cost_micros,
            "externalRef": external_ref,
            "dataSubjectId": data_subject_id,
            "lawfulBasis": lawful_basis,
            "automatedDecision": automated_decision,
            "redactPII": redact_pii,
            "priority": priority
        }
        
        # Remove None values to keep payload clean
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return self._send_sync(payload)

    def _send_async(self, payload: Dict[str, Any]) -> None:
        """Send audit log asynchronously."""
        try:
            self._send_sync(payload)
        except Exception as e:
            # For MVP, just log errors (production: add retries/backoff)
            print(f"AI Audit log failed: {e}")

    def _send_sync(self, payload: Dict[str, Any]) -> bool:
        """Send audit log synchronously."""
        try:
            url = urljoin(self.base_url, '/api/v2/log-decision')
            response = self.session.post(url, json=payload, timeout=5)
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            print(f"AI Audit log failed: {e}")
            return False
        except Exception as e:
            print(f"AI Audit log unexpected error: {e}")
            return False

    def close(self) -> None:
        """Close the session and cleanup resources."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience function for simple usage
def log_ai_decision(api_key: str, 
                   input_text: str, 
                   output_text: str, 
                   model_name: str = "unknown",
                   metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Simple function to log a single AI decision.
    
    For applications that need to log many decisions, 
    use the AuditLogger class instead for better performance.
    """
    logger = AuditLogger(api_key)
    logger.log_decision(input_text, output_text, model_name, metadata)
    logger.close()