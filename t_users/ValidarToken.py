import boto3
import os
from datetime import datetime
import json

def lambda_handler(event):
    token = event['query']['token']
    tenant_id = event['query']['tenant_id']
    
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
            'body': json.dumps({'error': 'Token no existe'})
        }
    
    expires = response['Item']['exp_date']
    if datetime.now().isoformat() > expires:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Token expirado'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Token válido'})
    }
