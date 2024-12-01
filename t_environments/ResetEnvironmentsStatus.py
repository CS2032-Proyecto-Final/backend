import boto3
import os
import json
from boto3.dynamodb.conditions import Key
import urllib.request
import json

def lambda_handler(event, context):

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
