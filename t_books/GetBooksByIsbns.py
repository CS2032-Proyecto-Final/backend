import boto3
import os
import json
from boto3.dynamodb.conditions import Key
import urllib.request

def lambda_handler(event, context):
    # Obtener parámetros de entrada
    isbns = event['query']['isbns']

    if not isbns:
        return {
            "statusCode": 400,
            "body": {"error": "isbns are required"}
        }

    # Convertir isbns de string a lista de forma segura
    try:
        isbns = json.loads(isbns)
    except Exception as e:
        return {
            "statusCode": 400,
            "body": {"error": "Invalid isbns format"}
        }
    
    # Validar token
    token = event['headers']['Authorization']

    data = json.dumps({"token": token}).encode('utf-8')

    req = urllib.request.Request(f"{os.environ['USERS_URL']}/tokens/validate", data=data, method="POST", headers={"Content-Type": "application/json"})

    user_response = json.loads(urllib.request.urlopen(req).read())
    
    if user_response.get('statusCode') == 403:
        return {"statusCode": 403, "body": {"message": "Token no válido"}}
    
    tenant_id = user_response['body']['tenant_id']
    email = user_response['body']['email']

    # Conexión a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    # Obtener los detalles de los libros
    books_details = []
    for isbn in isbns:
        response = table.query(
            KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('isbn').eq(isbn)
        )
        items = response.get('Items', [])
        if items:
            books_details.append(items[0])

    return {
        "statusCode": 200,
        "body": books_details
    }
