import boto3
import os
import json
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Obtener parámetros de entrada desde query
    tenant_id = event['query']['tenant_id']
    isbns = json.loads(event['query']['isbns'])

    # Conexión a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    # Inicializar lista de libros encontrados
    books = []

    # Procesar cada ISBN
    for isbn in isbns:
        response = table.query(
            KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('isbn').eq(isbn)
        )
        items = response.get('Items', [])
        books.extend(items)

    # Retornar los libros encontrados
    return {
        'statusCode': 200,
        'body': json.dumps(books)
    }
