import boto3
import hashlib
from datetime import datetime


# Hashear contraseña
def hash_password(password):
    # Retorna la contraseña hasheada
    return hashlib.sha256(password.encode()).hexdigest()

# Función que maneja el registro de user y validación del password
def lambda_handler(event, context):
    try:
        # Obtener el email ,password, tenant_id e email
        password = event.get('password')
        tenant_id = event.get('tenant_id')
        email = event.get('email')
        
        # Verificar que el email y el password existen
        if email and password:
            # Hashea la contraseña antes de almacenarla
            hashed_password = hash_password(password)
            # Conectar DynamoDB
            dynamodb = boto3.resource('dynamodb')
            t_usuario = dynamodb.Table('t_usuario')

            item = t_usuario.get_item(
                Key={
                    'tenant_id': tenant_id,
                    'email': email 
                }
            )
            if 'Item' in item:
                mensaje = {
                    'message': f'Email ya existe en la base de datos del tenant_id: {tenant_id}',
                    'tenant_id': tenant_id
                }
                return {
                    'statusCode': 400,
                    'body': json.dumps(mensaje)
                }
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Almacena los datos del user en la tabla de usuario en DynamoDB
            t_usuario.put_item(
                Item={
                    'tenant_id' : tenant_id,
                    'email': email,
                    'password': hashed_password,
                    'name' : name,
                    'fecha_creacion' : now
                }
            )
            # Retornar un código de estado HTTP 200 (OK) y un mensaje de éxito
            mensaje = {
                'message': 'User registered successfully',
                'email': email
            }
            return {
                'statusCode': 200,
                'body': mensaje
            }
        else:
            mensaje = {
                'error': 'Invalid request body: missing email or password'
            }
            return {
                'statusCode': 400,
                'body': mensaje
            }

    except Exception as e:
        # Excepción y retornar un código de error HTTP 500
        print("Exception:", str(e))
        mensaje = {
            'error': str(e)
        }        
        return {
            'statusCode': 500,
            'body': mensaje
        }