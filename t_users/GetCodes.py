import boto3
import os
from datetime import datetime

def lambda_handler(event):
    tenant_id = event['query']['tenant_id']
    table_name = os.environ["CODES_TABLE_NAME"]

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    response = table.query(
        KeyConditionExpression=boto3.dynamodb.conditions.Key('tenant_id').eq(tenant_id)
    )

    now = datetime.now().isoformat()
    valid_codes = [item for item in response['Items'] if item['expiration_date'] > now]

    return {
        'statusCode': 200,
        'body': {
            'codes': valid_codes
        }
    }
