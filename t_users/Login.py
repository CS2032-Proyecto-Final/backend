import boto3
import os
import hashlib
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
        "exp": (datetime.now() + timedelta(hours=24)).timestamp()
    }

    token = jwt.encode(payload=payload, key=JWT_SECRET, algorithm="HS256", headers=header)

    return token

def lambda_handler(event, context):
    body = event['body']
    email = body['email']
    password = body['password']
    tenant_id = body['tenant_id']

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

    libraries_url = os.environ.get("LIBRARIES_URL")
    if not libraries_url:
        raise Exception("LIBRARIES_URL environment variable not set")

    api_url = f"{libraries_url}/libraries/info"

    api_request = urllib.request.Request(api_url, headers={"Authorization": token})

    with urllib.request.urlopen(api_request) as response:
        tenant_info = json.load(response)
    
    return {
        'statusCode': 200,
        'body': {
            'message': 'Login exitoso',
            'token': token,
            'tenant_info': tenant_info
        }
    }
