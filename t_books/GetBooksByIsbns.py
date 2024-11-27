import boto3
import os
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Obtener parámetros de entrada
    tenant_id = event['query']['tenant_id']
    isbns = event['query']['isbns']

    if not tenant_id or not isbns:
        return {
            "statusCode": 400,
            "body": {"error": "tenant_id and isbns are required"}
        }

    # Convertir isbns de string a lista de forma segura
    try:
        isbns = json.loads(isbns)
    except Exception as e:
        return {
            "statusCode": 400,
            "body": {"error": "Invalid isbns format"}
        }

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
