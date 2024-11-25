import boto3
import os
from boto3.dynamodb.conditions import Key
import json

def lambda_handler(event, context):
    # Obtener parámetros de entrada desde query
    tenant_id = event['query']['tenant_id']
    isbns = event['query']['isbns']
    isbns = json.loads(isbns)

    # Conexión a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    # Consultar DynamoDB para cada ISBN
    books = []
    for isbn in isbns:
        response = table.query(
            KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('isbn').eq(isbn)
        )
        items = response.get('Items', [])
        if items:
            books.append(items[0])

    # Retornar los libros encontrados
    return {
        'statusCode': 200,
        'body': json.dumps(books)  # Retornar la lista de libros
    }
