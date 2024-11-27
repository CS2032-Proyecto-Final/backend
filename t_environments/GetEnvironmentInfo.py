import boto3
import os
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Entrada desde el evento
    tenant_id = event['query']['tenant_id']
    env_type = event['query']['type']
    env_name = event['query']['env_name']
    hour = event['query']['hour']

    # Configuración DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    
    # Consulta en DynamoDB
    response = table.get_item(
        Key={
            "tenant_id": tenant_id,
            "type#name#hour": f"{env_type}#{env_name}#{hour}"
        }
    )

    # Respuesta
    if "Item" in response:
        return {
            "statusCode": 200,
            "body": response['Item'] 
        }
    else:
        return {
            "statusCode": 404,
            "body": {
                "message": "Env not found"
            }
        }
