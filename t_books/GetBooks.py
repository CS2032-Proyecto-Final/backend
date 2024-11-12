import boto3
import os
import json
import urllib.request
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Obtener parámetros de entrada
    tenant_id = event['query']['tenant_id']
    email = event['query']['email']
    page = int(event['query']['page'])
    limit = int(event['query']['limit'])

    # Conexión a DynamoDB para la tabla de libros
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    # Conexión a la API de favoritos para obtener el estado de `isFavorite`
    api_url = f"https://wb5hznomeh.execute-api.us-east-1.amazonaws.com/dev/favorite/my/actual?tenant_id={tenant_id}&email={email}"
    with urllib.request.urlopen(api_url) as response:
        favorites_data = json.load(response)
        favorite_isbns = {item['isbn'] for item in favorites_data if item['isFavorite']}

    # Configurar parámetros de consulta para libros
    query_params = {
        'KeyConditionExpression': Key('tenant_id').eq(tenant_id),
        'Limit': limit,
    }

    # Avanzar a la página solicitada usando la paginación de DynamoDB
    exclusive_start_key = None
    for _ in range(page - 1):
        response = table.query(**query_params)
        exclusive_start_key = response.get('LastEvaluatedKey', None)
        
        # Si no hay más datos, retornar una lista vacía
        if not exclusive_start_key:
            return []

        # Actualizar la clave de inicio exclusiva para la siguiente iteración
        query_params['ExclusiveStartKey'] = exclusive_start_key

    # Obtener los elementos de la página actual
    response = table.query(**query_params)
    items = response.get('Items', [])

    # Agregar el estado `isFavorite` a cada libro
    for item in items:
        item['isFavorite'] = item.get('isbn') in favorite_isbns

    return items
