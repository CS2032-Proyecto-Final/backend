import boto3
import os
import json
from boto3.dynamodb.conditions import Key
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    # Obtén los parámetros de la solicitud
    tenant_id = event['query']['tenant_id']
    page = int(event['query'].get('page', 1))
    limit = 10  # Límite de resultados por página

    # Clave de inicio para paginación, si se proporciona
    start_key = None
    if 'lastEvaluatedKey' in event['query']:
        start_key = json.loads(event['query']['lastEvaluatedKey'])

    # Parámetros de consulta en DynamoDB
    query_params = {
        'KeyConditionExpression': Key('tenant_id').eq(tenant_id),
        'Limit': limit
    }
    
    # Solo añadir 'ExclusiveStartKey' si existe
    if start_key:
        query_params['ExclusiveStartKey'] = start_key
    
    # Ejecuta la consulta
    response = table.query(**query_params)

    # Convierte los resultados de Decimal a float o int según corresponda
    books = json.loads(json.dumps(response.get('Items', []), default=convert_decimal))
    last_evaluated_key = response.get('LastEvaluatedKey', None)

    # Devuelve los libros y la clave de paginación directamente en el cuerpo de respuesta
    return {
        'statusCode': 200,
        'body': {
            'books': books,
            'lastEvaluatedKey': last_evaluated_key
        }
    }

def convert_decimal(value):
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    raise TypeError
