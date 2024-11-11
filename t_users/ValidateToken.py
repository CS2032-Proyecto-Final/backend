import boto3
import os
from datetime import datetime

def lambda_handler(event, context):
    body = event['body']
    token = body['token']
    tenant_id = body['tenant_id']
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TOKENS_TABLE_NAME'])
    
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'token': token
        }
    )
    
    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': {'error': 'Token no válido'}
        }
    
    email = response['Item']['email']
    expires = response['Item']['exp_date']

    if datetime.now().isoformat() > expires:
        return {
            'statusCode': 403,
            'body': {'error': 'Token no válido'}
        }
    
    return {
        'statusCode': 200,
        'body': {
            'message': 'Token válido',
            'email': email
        }
    }
