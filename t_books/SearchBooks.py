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
    title = event['query'].get('title')
    author_name = event['query'].get('author_name')
    author_lastname = event['query'].get('author_lastname')
    isbn = event['query'].get('isbn')

    # Conexión a DynamoDB para la tabla de libros
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    # Inicializar favoritos
    favorite_isbns = set()
    favorites_present = False

    # Intentar obtener los favoritos
    try:
        api_url = f"https://wb5hznomeh.execute-api.us-east-1.amazonaws.com/dev/favorite/my/actual?tenant_id={tenant_id}&email={email}"
        with urllib.request.urlopen(api_url) as response:
            favorites_data = json.load(response)
            favorite_items = favorites_data.get("body", [])
            favorite_isbns = {item['isbn'] for item in favorite_items if item['isFavorite']}
            favorites_present = bool(favorite_items)
    except Exception as e:
        print(f"Error al obtener favoritos: {e}")
        favorites_present = False  # Indicar que no hay favoritos disponibles en caso de error

    # Configurar parámetros de consulta para libros
    query_params = {
        'Limit': limit,
    }

    # Determinar el índice y la expresión de condición según el parámetro de búsqueda
    if isbn:
        # Búsqueda por ISBN específico
        query_params.update({
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('isbn').eq(isbn)
        })
    elif title:
        # Búsqueda por título usando el índice `title-index`
        query_params.update({
            'IndexName': 'title-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('title').begins_with(title)
        })
    elif author_name:
        # Búsqueda por nombre del autor usando `author_name-index`
        query_params.update({
            'IndexName': 'author_name-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('author_name').begins_with(author_name)
        })
    elif author_lastname:
        # Búsqueda por apellido del autor usando `author_lastname-index`
        query_params.update({
            'IndexName': 'author_lastname-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('author_lastname').begins_with(author_lastname)
        })
    else:
        # Búsqueda general para todos los libros bajo el `tenant_id`
        query_params.update({
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id)
        })

    # Avanzar a la página solicitada usando la paginación de DynamoDB
    exclusive_start_key = None
    for _ in range(page - 1):
        response = table.query(**query_params)
        exclusive_start_key = response.get('LastEvaluatedKey', None)
        
        # Si no hay más datos, retornar una lista vacía
        if not exclusive_start_key:
            return {
                "statusCode": 200,
                "body": {
                    "favorites": favorites_present,
                    "books": []
                }
            }

        # Actualizar la clave de inicio exclusiva para la siguiente iteración
        query_params['ExclusiveStartKey'] = exclusive_start_key

    # Obtener los elementos de la página actual
    response = table.query(**query_params)
    items = response.get('Items', [])

    # Agregar el estado `isFavorite` a cada libro
    for item in items:
        item['isFavorite'] = item.get('isbn') in favorite_isbns

    return {
        "statusCode": 200,
        "body": {
            "favorites": favorites_present,
            "books": items
        }
    }