import boto3
import os
from datetime import datetime
import json

def lambda_handler(event):
    body = event['body']
    token = body['token']
    tenant_id = body['tenant_id']
    email = body['email']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TOKENS_TABLE_NAME'])
    
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'email': email
        }
    )
    
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Token no válido'})
        }
    
    bd_token = response['Item']['token']
    expires = response['Item']['exp_date']

    if token != bd_token:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Token no válido'})
        }

    if datetime.now().isoformat() > expires:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Token no válido'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Token válido'})
    }
