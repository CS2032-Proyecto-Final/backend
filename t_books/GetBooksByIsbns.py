import boto3
import os
import json

def lambda_handler(event, context):
    # Obtener parámetros de entrada desde query
    tenant_id = event['query']['tenant_id']
    isbns = json.loads(event['query']['isbns'])

    # Conexión a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table_name = os.environ["TABLE_NAME"]

    # Crear solicitudes para batch_get_item
    keys = [{'tenant_id': tenant_id, 'isbn': isbn} for isbn in isbns]
    response = dynamodb.batch_get_item(
        RequestItems={
            table_name: {
                'Keys': keys
            }
        }
    )

    # Retornar los libros encontrados
    books = response.get('Responses', {}).get(table_name, [])
    return {
        'statusCode': 200,
        'body': json.dumps(books)
    }
