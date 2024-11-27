import boto3
import os
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Entrada desde el evento
    tenant_id = event['query']['tenant_id']
    env_type = event['query']['type']

    # Validación de parámetros
    if not tenant_id or not env_type:
        return {
            "statusCode": 400,
            "body": {
                "message": "tenant_id and type are required"
            }
        }

    # Configuración DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    
    # Consulta en DynamoDB
    response = table.query(
        KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('type#name#hour').begins_with(env_type)
    )

    environments = [
        {
            "name": item["name"],
            "hour": item["hour"],
            "status": item["status"],
            "capacity": item["capacity"]
        }
        for item in response.get("Items", [])
    ]

    # Respuesta
    return {
        "statusCode": 200,
        "body": {
            environments
        }
    }
