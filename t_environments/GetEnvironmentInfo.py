import boto3
import os
from boto3.dynamodb.conditions import Key
import urllib.request
import json

def lambda_handler(event, context):
    # Entrada desde el evento
    env_type = event['query']['type']
    env_name = event['query']['env_name']
    hour = event['query']['hour']

    # Obtener token
    headers = event['headers']
    token = headers['Authorization']

    # Validar token
    MU_url = f"{os.environ["USERS_URL"]}/tokens/validate"

    data = {
        "token": token
    }

    data_json = json.dumps(data).encode('utf-8')

    MU_request = urllib.request.Request(MU_url, data=data_json, method="POST")

    MU_request.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(MU_request) as response:
        user_response = json.loads(response.read())

    if(user_response['statusCode'] == 403):
        return {
            "statusCode": 403,
            "body": {
                "message": "Token no válido"
            }
        }
    
    tenant_id = user_response['body']['tenant_id']
    email = user_response['body']['email']

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
