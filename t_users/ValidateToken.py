import boto3
import os
from datetime import datetime
import jwt

def validate_jwt(token):
    try:
        JWT_SECRET = os.environ["JWT_SECRET"]
        payload = jwt.decode(jwt=token, key=JWT_SECRET, algorithms=["HS256"])

        return payload
    except:
        return False

def lambda_handler(event, context):
    body = event['body']
    token = body['token']
    
    payload = validate_jwt(token)
    
    if not payload:
        return {
            'statusCode': 403,
            'body': {'error': 'Token no válido'}
        }
    
    tenant_id = payload["tenant_id"]
    email = payload["email"]
    
    return {
        'statusCode': 200,
        'body': {
            'message': 'Token válido',
            'tenant_id': tenant_id,
            'email': email
        }
    }
