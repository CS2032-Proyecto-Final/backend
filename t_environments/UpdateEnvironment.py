import boto3
import os
import json
from boto3.dynamodb.conditions import Key
import urllib.request

def lambda_handler(event, context):
    # Entrada desde el evento
    body = json.loads(event['body'])
    tenant_id = event['query'].get('tenant_id')
    env_type = body.get("type")
    name = body.get("name")
    hour = body.get("hour")
    new_status = body.get("status")

    # Validación de parámetros
    if not env_type or not name or not hour or not new_status:
        return {
            "statusCode": 400,
            "body": {"message": "All parameters are required"}
        }
    
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
    
    # Consulta y actualización en DynamoDB
    response = table.get_item(
        Key={
            "tenant_id": tenant_id,
            "type#name#hour": f"{env_type}#{name}#{hour}"
        }
    )

    item = response.get('Item')
    if item and item['status'] == 'available':
        table.update_item(
            Key={
                "tenant_id": tenant_id,
                "type#name#hour": f"{env_type}#{name}#{hour}"
            },
            UpdateExpression="SET #status = :new_status",
            ExpressionAttributeNames={'#status': 'status'},
            ExpressionAttributeValues={':new_status': new_status}
        )
        return {
            "statusCode": 202,
            "body": {"message": "Environment status changed"}
        }
    else:
        return {
            "statusCode": 406,
            "body": {"message": "Environment hour status: occupied"}
        }
