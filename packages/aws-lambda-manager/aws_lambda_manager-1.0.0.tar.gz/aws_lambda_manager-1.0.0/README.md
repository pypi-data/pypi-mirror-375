# AWS Lambda EventBridge Manager

Una herramienta simple para administrar AWS Lambda y EventBridge desde Python.

## 🚀 Instalación

```bash
pip install aws-lambda-manager
```

## ⚡ Uso Básico

```python
from lambda_manager import AWSLambdaEventBridgeManager, AWSAuthenticationError, AWSLambdaEventBridgeError

try:
    # Inicializar
    manager = AWSLambdaEventBridgeManager(region="us-east-1")
    
    # Habilitar regla de EventBridge
    result = manager.enable_rule("mi-regla-eventbridge")
    print(f"✅ Regla habilitada: {result['message']}")
    
    # Deshabilitar regla
    result = manager.disable_rule("mi-regla-eventbridge")
    print(f"✅ Regla deshabilitada: {result['message']}")
    
    # Invocar función Lambda con payload
    payload = {"mensaje": "Hola", "datos": [1, 2, 3]}
    result = manager.invoke_lambda("mi-funcion-lambda", payload)
    print(f"🚀 Invocación exitosa: {result['status_code']}")
    
    # Invocar función Lambda sin payload
    result = manager.invoke_lambda("mi-funcion-lambda")
    print(f"🚀 Invocación sin payload: {result['status_code']}")
    
    # Listar recursos
    rules = manager.list_eventbridge_rules()
    functions = manager.list_lambda_functions()
    print(f"📋 Reglas: {len(rules)}, Funciones: {len(functions)}")
    
except AWSAuthenticationError as e:
    print(f"🔐 Error de autenticación: {e}")
except AWSLambdaEventBridgeError as e:
    print(f"❌ Error de operación: {e}")
```


## 🔧 Funcionalidades

| Método | Descripción |
|--------|-------------|
| `enable_rule(rule_name)` | Habilita una regla de EventBridge |
| `disable_rule(rule_name)` | Deshabilita una regla de EventBridge |
| `invoke_lambda(function_name, payload)` | Invoca una función Lambda |
| `list_eventbridge_rules()` | Lista todas las reglas de EventBridge |
| `list_lambda_functions()` | Lista todas las funciones Lambda |

## 🔐 Configuración de Credenciales

**⚠️ IMPORTANTE:** Este paquete requiere que tengas configuradas las credenciales AWS en tu máquina.

### Configurar Variables de Entorno

```bash
# Editar archivo de configuración
nano ~/.bashrc

# Agregar las siguientes líneas al final del archivo:
export AWS_ACCESS_KEY_ID=tu_access_key
export AWS_SECRET_ACCESS_KEY=tu_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Aplicar los cambios
source ~/.bashrc
```

**Nota:** Reemplaza `tu_access_key` y `tu_secret_key` con tus credenciales reales de AWS.

## 🛡️ Permisos AWS Necesarios

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "lambda:InvokeFunction",
                "lambda:ListFunctions"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "events:EnableRule",
                "events:DisableRule",
                "events:DescribeRule",
                "events:ListRules",
                "events:ListTargetsByRule"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sts:GetCallerIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```


## 🧪 Testing

```bash
# Ejecutar test completo
python test_complete.py
```

**Requisito:** Asegúrate de tener configuradas las credenciales AWS (ver sección de configuración).

El test ejecuta la secuencia completa: habilitar regla → listar recursos → invocar Lambda → deshabilitar regla.

## 📋 API Reference

### Constructor
```python
AWSLambdaEventBridgeManager(
    region: str = "us-east-1",
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None
)
```


### Excepciones

- `AWSLambdaEventBridgeError`: Error base para operaciones
- `AWSAuthenticationError`: Error de autenticación AWS

## 📄 Licencia

MIT License - Ver archivo `LICENSE` para más detalles.

---

**Desarrollado para simplificar la administración de AWS Lambda y EventBridge** 🚀