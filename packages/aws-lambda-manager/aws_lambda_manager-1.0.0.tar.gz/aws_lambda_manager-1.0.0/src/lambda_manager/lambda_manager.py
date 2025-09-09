"""
AWS Lambda EventBridge Manager - Herramienta simple para administrar AWS Lambda y EventBridge.

Funcionalidades:
- Habilitar reglas de EventBridge
- Deshabilitar reglas de EventBridge  
- Invocar funciones Lambda
"""

import boto3
import json
import logging
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError, NoCredentialsError


class AWSLambdaEventBridgeError(Exception):
    """Excepción base para errores del AWS Lambda EventBridge Manager."""
    pass


class AWSAuthenticationError(AWSLambdaEventBridgeError):
    """Error de autenticación AWS."""
    pass


class AWSLambdaEventBridgeManager:
    """
    Administrador simple de AWS Lambda y EventBridge.
    
    Proporciona solo las 3 funcionalidades esenciales:
    - Habilitar reglas de EventBridge
    - Deshabilitar reglas de EventBridge
    - Invocar funciones Lambda
    """
    
    def __init__(self, region: str = "us-east-1", 
                 aws_access_key_id: Optional[str] = None,
                 aws_secret_access_key: Optional[str] = None,
                 aws_session_token: Optional[str] = None):
        """
        Inicializa el manager con configuración AWS.
        
        Args:
            region: Región de AWS (default: us-east-1)
            aws_access_key_id: Access Key ID (opcional, usa credenciales por defecto si no se proporciona)
            aws_secret_access_key: Secret Access Key (opcional)
            aws_session_token: Session Token (opcional)
        """
        self.region = region
        self.logger = logging.getLogger(__name__)
        
        # Configurar clientes AWS
        self._setup_aws_clients(aws_access_key_id, aws_secret_access_key, aws_session_token)
        
        # Verificar autenticación
        self._verify_authentication()
    
    def _setup_aws_clients(self, aws_access_key_id: Optional[str], 
                          aws_secret_access_key: Optional[str], 
                          aws_session_token: Optional[str]):
        """Configura los clientes de AWS."""
        try:
            session_kwargs = {
                'region_name': self.region
            }
            
            # Agregar credenciales si están disponibles
            if aws_access_key_id and aws_secret_access_key:
                session_kwargs.update({
                    'aws_access_key_id': aws_access_key_id,
                    'aws_secret_access_key': aws_secret_access_key
                })
                
                if aws_session_token:
                    session_kwargs['aws_session_token'] = aws_session_token
            
            session = boto3.Session(**session_kwargs)
            
            self.lambda_client = session.client('lambda')
            self.events_client = session.client('events')
            self.sts_client = session.client('sts')
            
        except Exception as e:
            raise AWSAuthenticationError(f"Error configurando clientes AWS: {str(e)}")
    
    def _verify_authentication(self):
        """Verifica que las credenciales AWS sean válidas."""
        try:
            self.sts_client.get_caller_identity()
            self.logger.info("Autenticación AWS exitosa")
        except NoCredentialsError:
            raise AWSAuthenticationError("No se encontraron credenciales AWS válidas")
        except ClientError as e:
            raise AWSAuthenticationError(f"Error de autenticación AWS: {str(e)}")
    
    def enable_rule(self, rule_name: str) -> Dict[str, Any]:
        """
        Habilita una regla de EventBridge.
        
        Args:
            rule_name: Nombre de la regla a habilitar
            
        Returns:
            Diccionario con información de la operación
            
        Raises:
            AWSLambdaEventBridgeError: Si hay error en la operación
        """
        try:
            self.logger.info(f"Habilitando regla EventBridge: {rule_name}")
            
            # Habilitar la regla
            self.events_client.enable_rule(Name=rule_name)
            
            # Obtener información de la regla
            rule_info = self.events_client.describe_rule(Name=rule_name)
            
            result = {
                'success': True,
                'rule_name': rule_name,
                'state': rule_info['State'],
                'message': f'Regla {rule_name} habilitada exitosamente'
            }
            
            self.logger.info(f"Regla {rule_name} habilitada exitosamente")
            return result
            
        except ClientError as e:
            error_msg = f"Error habilitando regla {rule_name}: {str(e)}"
            self.logger.error(error_msg)
            raise AWSLambdaEventBridgeError(error_msg)
    
    def disable_rule(self, rule_name: str) -> Dict[str, Any]:
        """
        Deshabilita una regla de EventBridge.
        
        Args:
            rule_name: Nombre de la regla a deshabilitar
            
        Returns:
            Diccionario con información de la operación
            
        Raises:
            AWSLambdaEventBridgeError: Si hay error en la operación
        """
        try:
            self.logger.info(f"Deshabilitando regla EventBridge: {rule_name}")
            
            # Deshabilitar la regla
            self.events_client.disable_rule(Name=rule_name)
            
            # Obtener información de la regla
            rule_info = self.events_client.describe_rule(Name=rule_name)
            
            result = {
                'success': True,
                'rule_name': rule_name,
                'state': rule_info['State'],
                'message': f'Regla {rule_name} deshabilitada exitosamente'
            }
            
            self.logger.info(f"Regla {rule_name} deshabilitada exitosamente")
            return result
            
        except ClientError as e:
            error_msg = f"Error deshabilitando regla {rule_name}: {str(e)}"
            self.logger.error(error_msg)
            raise AWSLambdaEventBridgeError(error_msg)
    
    def invoke_lambda(self, function_name: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Invoca una función Lambda.
        
        Args:
            function_name: Nombre de la función Lambda a invocar
            payload: Datos a enviar a la función (opcional)
            
        Returns:
            Diccionario con la respuesta de la función
            
        Raises:
            AWSLambdaEventBridgeError: Si hay error en la operación
        """
        try:
            self.logger.info(f"Invocando función Lambda: {function_name}")
            
            # Preparar payload
            if payload is None:
                payload = {}
            
            # Invocar la función
            response = self.lambda_client.invoke(
                FunctionName=function_name,
                InvocationType='RequestResponse',
                Payload=json.dumps(payload)
            )
            
            # Procesar respuesta
            result = {
                'success': True,
                'function_name': function_name,
                'status_code': response['StatusCode'],
                'payload': payload
            }
            
            # Incluir la respuesta de la función
            if 'Payload' in response:
                try:
                    payload_response = json.loads(response['Payload'].read())
                    result['response'] = payload_response
                except (json.JSONDecodeError, AttributeError):
                    result['response'] = response['Payload'].read().decode('utf-8')
            
            self.logger.info(f"Función {function_name} invocada exitosamente")
            return result
            
        except ClientError as e:
            error_msg = f"Error invocando función {function_name}: {str(e)}"
            self.logger.error(error_msg)
            raise AWSLambdaEventBridgeError(error_msg)
    
    def list_lambda_functions(self) -> list:
        """
        Lista todas las funciones Lambda disponibles.
        
        Returns:
            Lista de diccionarios con información de las funciones Lambda
            
        Raises:
            AWSLambdaEventBridgeError: Si hay error en la operación
        """
        try:
            self.logger.info("Listando funciones Lambda disponibles")
            
            # Listar funciones Lambda
            response = self.lambda_client.list_functions()
            functions = response.get('Functions', [])
            
            # Formatear la respuesta para que sea consistente con los ejemplos
            formatted_functions = []
            for func in functions:
                formatted_func = {
                    'function_name': func['FunctionName'],
                    'runtime': func.get('Runtime', 'N/A'),
                    'state': func.get('State', 'N/A'),
                    'last_modified': func.get('LastModified', 'N/A'),
                    'code_size': func.get('CodeSize', 0),
                    'timeout': func.get('Timeout', 0),
                    'memory_size': func.get('MemorySize', 0),
                    'description': func.get('Description', ''),
                    'arn': func.get('FunctionArn', '')
                }
                formatted_functions.append(formatted_func)
            
            self.logger.info(f"Encontradas {len(formatted_functions)} funciones Lambda")
            return formatted_functions
            
        except ClientError as e:
            error_msg = f"Error listando funciones Lambda: {str(e)}"
            self.logger.error(error_msg)
            raise AWSLambdaEventBridgeError(error_msg)
    
    def list_eventbridge_rules(self) -> list:
        """
        Lista todas las reglas de EventBridge disponibles.
        
        Returns:
            Lista de diccionarios con información de las reglas de EventBridge
            
        Raises:
            AWSLambdaEventBridgeError: Si hay error en la operación
        """
        try:
            self.logger.info("Listando reglas de EventBridge disponibles")
            
            # Listar reglas de EventBridge
            response = self.events_client.list_rules()
            rules = response.get('Rules', [])
            
            # Formatear la respuesta para que sea consistente
            formatted_rules = []
            for rule in rules:
                formatted_rule = {
                    'name': rule['Name'],
                    'state': rule.get('State', 'N/A'),
                    'description': rule.get('Description', ''),
                    'last_modified': rule.get('LastModified', 'N/A'),
                    'arn': rule.get('Arn', ''),
                    'schedule_expression': rule.get('ScheduleExpression', 'N/A')
                }
                formatted_rules.append(formatted_rule)
            
            self.logger.info(f"Encontradas {len(formatted_rules)} reglas de EventBridge")
            return formatted_rules
            
        except ClientError as e:
            error_msg = f"Error listando reglas de EventBridge: {str(e)}"
            self.logger.error(error_msg)
            raise AWSLambdaEventBridgeError(error_msg)
    
