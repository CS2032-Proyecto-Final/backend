import boto3
import os
import json
from boto3.dynamodb.conditions import Key
import urllib.request
import json

def lambda_handler(event, context):

    body = event['body']
    tenant_id = body['tenant_id']

    # Configuración DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    
    # Consulta y actualización en batch en DynamoDB
    response = table.query(
        KeyConditionExpression=Key('tenant_id').eq(tenant_id)
    )

    with table.batch_writer() as batch:
        for item in response.get("Items", []):
            if item['status'] != 'available':
                batch.put_item(
                    Item={
                        "tenant_id": item["tenant_id"],
                        "type#name#hour": item["type#name#hour"],
                        "status": "available",
                        "name": item["name"],
                        "hour": item["hour"],
                        "capacity": item["capacity"]
                    }
                )

    # Respuesta
    return {
        "statusCode": 200,
        "body": {"message": "Environments status reset to available"}
    }
