"""
AWS Lambda EventBridge Manager - Herramienta simple para administrar AWS Lambda y EventBridge.

Funcionalidades:
- Habilitar reglas de EventBridge
- Deshabilitar reglas de EventBridge
- Invocar funciones Lambda
"""

from .lambda_manager import AWSLambdaEventBridgeManager, AWSLambdaEventBridgeError, AWSAuthenticationError

__version__ = "1.0.0"
__author__ = "Edwin"
__all__ = ["AWSLambdaEventBridgeManager", "AWSLambdaEventBridgeError", "AWSAuthenticationError"]
