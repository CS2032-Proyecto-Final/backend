import boto3
import os
import hashlib
import uuid
import urllib.request
import json
import jwt
from datetime import datetime, timedelta

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(email, tenant_id):
    JWT_SECRET = os.environ["JWT_SECRET"]

    header = {"alg": "HS256", "typ": "JWT"}

    payload = {
        "tenant_id": tenant_id,
        "email": email,
        "creation_date": datetime.now().isoformat(),
        "exp": (datetime.now() + timedelta(hours=24)).isoformat()
    }

    token = jwt.encode(payload=payload, key=JWT_SECRET, algorithm="HS256", headers=header)

    return token

def lambda_handler(event, context):
    body = event['body']
    email = body['email']
    password = body['password']
    tenant_id = body['tenant_id']

    api_url = f"https://hsoml2f154.execute-api.us-east-1.amazonaws.com/dev/libraries/info?tenant_id={tenant_id}"

    with urllib.request.urlopen(api_url) as response:
        tenant_info = json.load(response)
    
    hashed_password = hash_password(password)
    
    dynamodb = boto3.resource('dynamodb')
    users_table = dynamodb.Table(os.environ['USERS_TABLE_NAME'])
    
    response = users_table.get_item(
        Key={
            'tenant_id': tenant_id,
            'email': email
        }
    )
    
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': {'error': 'Usuario y/o contraseña incorrectos'}
        }
    
    stored_hashed_password = response['Item']['password']
    if hashed_password != stored_hashed_password:
        return {
            'statusCode': 403,
            'body': {'error': 'Usuario y/o contraseña incorrectos'}
        }

    token = generate_token(email, tenant_id)
    
    return {
        'statusCode': 200,
        'body': {
            'message': 'Login exitoso',
            'token': token,
            'tenant_info': tenant_info
        }
    }
