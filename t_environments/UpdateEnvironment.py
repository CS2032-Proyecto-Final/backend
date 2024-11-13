import boto3
import os
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Entrada desde el evento
    body = json.loads(event['body'])
    tenant_id = event['query'].get('tenant_id')
    env_type = body.get("type")
    name = body.get("name")
    hour = body.get("hour")
    new_status = body.get("status")

    # Validación de parámetros
    if not tenant_id or not env_type or not name or not hour or not new_status:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "All parameters are required"})
        }

    # Configuración DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['DYNAMODB_TABLE'])
    
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
            "body": json.dumps({"message": "Environment status changed"})
        }
    else:
        return {
            "statusCode": 406,
            "body": json.dumps({"message": "Environment hour status: occupied"})
        }
