import boto3
import os
import json

def lambda_handler(event, context):
    # Entrada desde el evento
    tenant_id = event['query'].get('tenant_id')
    env_type = event['query'].get('type')
    env_name = event['query'].get('env_name')
    hour = event['query'].get('hour')

    # Validación de parámetros
    if not tenant_id or not env_type or not env_name or not hour:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "All parameters are required"})
        }

    # Configuración DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
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
            "body": json.dumps(response['Item'])
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Env not found"})
        }
