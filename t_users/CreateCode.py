import boto3
import os
import uuid
from datetime import datetime, timedelta

def lambda_handler(event, context):
    tenant_id = event['queryStringParameters']['tenant_id']
    table_name = os.environ["CODES_TABLE_NAME"]

    token = str(uuid.uuid4())
    expiration_date = (datetime.now() + timedelta(hours=24)).isoformat()

    code_item = {
        'tenant_id': tenant_id,
        'code': token,
        'expiration_date': expiration_date
    }
    
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    table.put_item(Item=code_item)
    
    return {
        'statusCode': 200,
        'body': {
            'message': 'Code created successfully',
            'code': token,
            'expiration_date': expiration_date
        }
    }
