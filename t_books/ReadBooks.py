import boto3
import os
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Obtener parámetros de entrada
    tenant_id = event['query']['tenant_id']
    page = int(event['query']['page'])
    limit = 6

    # Conexión a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    # Configurar parámetros de consulta
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
    return response.get('Items', [])
