import boto3
import os
from boto3.dynamodb.conditions import Key
import json

def lambda_handler(event, context):

    # Obtener parámetros de entrada desde query
    tenant_id = event['query']['tenant_id']
    isbn = event['query']['isbn']

    # Conexión a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    # Configurar parámetros de consulta para buscar por tenant_id y isbn
    response = table.query(
        KeyConditionExpression=Key('tenant_id').eq(tenant_id) & Key('isbn').eq(isbn)
    )

    # Retornar el resultado
    items = response.get('Items', [])
    if not items:
        return {
            'statusCode': 404,
            'body': {'message': 'Libro no encontrado'}
        }

    return {
        'statusCode': 200,
        'body': json.dumps(items[0])  # Retorna el primer (y único) resultado
    }
