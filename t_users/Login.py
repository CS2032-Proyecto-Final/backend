import boto3
import os
import hashlib
import uuid
import urllib.request
from datetime import datetime, timedelta
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    body = event['body']
    email = body['email']
    password = body['password']

    api_url = f"https://api-endpoint/libraries/info?email={email}"

    with urllib.request.urlopen(api_url) as response:
        tenant_info_response = response.read().decode()
        tenant_info_outer = json.loads(tenant_info_response)
        tenant_info = json.loads(tenant_info_outer["body"])

    tenant_id = tenant_info.get('tenant_id')

    if not tenant_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Tenant ID no encontrado en la respuesta'})
        }
    
    hashed_password = hash_password(password)
    
    dynamodb = boto3.resource('dynamodb')
    users_table = dynamodb.Table(os.environ['USERS_TABLE_NAME'])
    tokens_table = dynamodb.Table(os.environ['TOKENS_TABLE_NAME'])
    
    response = users_table.get_item(
        Key={
            'tenant_id': tenant_id,
            'email': email
        }
    )
    
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Usuario y/o contraseña incorrectos'})
        }
    
    stored_hashed_password = response['Item']['password']
    if hashed_password != stored_hashed_password:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Usuario y/o contraseña incorrectos'})
        }

    token = str(uuid.uuid4())
    expiration_date = (datetime.now() + timedelta(minutes=60)).isoformat()
    
    token_item = {
        'tenant_id': tenant_id,
        'email': email,
        'token': token,
        'exp_date': expiration_date
    }
    
    tokens_table.put_item(Item=token_item)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Login exitoso',
            'token': token,
            'tenant_info': tenant_info
        })
    }
