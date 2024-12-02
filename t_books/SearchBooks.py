import boto3
import os
import json
import urllib.request
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # Obtener parámetros de entrada
    page = int(event['query']['page'])
    limit = int(event['query']['limit'])
    title = event['query'].get('title', '').lower()
    author_name = event['query'].get('author_name', '').lower()
    author_lastname = event['query'].get('author_lastname', '').lower()
    isbn = event['query'].get('isbn')

    # Validar token
    token = event['headers']['Authorization']

    data = json.dumps({"token": token}).encode('utf-8')

    req = urllib.request.Request(f"{os.environ['USERS_URL']}/tokens/validate", data=data, method="POST", headers={"Content-Type": "application/json"})

    user_response = json.loads(urllib.request.urlopen(req).read())
    
    if user_response.get('statusCode') == 403:
        return {"statusCode": 403, "body": {"message": "Token no válido"}}
    
    tenant_id = user_response['body']['tenant_id']
    email = user_response['body']['email']

    # Conexión a DynamoDB para la tabla de libros
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    # Inicializar favoritos
    favorite_isbns = set()
    favorites_present = False

    favorites_url = os.environ.get("FAVORITES_URL")
    if not favorites_url:
        raise Exception("FAVORITES_URL environment variable not set")

    # Intentar obtener los favoritos
    try:
        api_url = f"{favorites_url}/favorite/my/actual"
        api_request = urllib.request.Request(api_url, headers={"Authorization": token})
        with urllib.request.urlopen(api_request) as response:
            favorites_data = json.load(response)
            # Asegúrate de acceder a la estructura correcta
            if "body" in favorites_data and isinstance(favorites_data["body"], list):
                favorite_items = favorites_data["body"]
                favorite_isbns = {item['isbn'] for item in favorite_items if item['isFavorite']}
                favorites_present = bool(favorite_items)
    except Exception as e:
        print(f"Error al obtener favoritos: {e}")
        favorites_present = False  # Indicar que no hay favoritos disponibles en caso de error

    # Configurar parámetros de consulta para libros
    query_params = {
        'Limit': limit,
    }

    # Determinar el índice y la expresión de condición según los parámetros de búsqueda
    if isbn:
        # Búsqueda por ISBN específico
        query_params.update({
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('isbn').eq(isbn)
        })
    elif title and author_name and author_lastname:
        # Búsqueda por combinación de título, nombre y apellido del autor
        query_params.update({
            'IndexName': 'title-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('title_index').begins_with(title),
            'FilterExpression': Key('author_name_index').begins_with(author_name) & Key('author_lastname_index').begins_with(author_lastname)
        })
    elif title and author_name:
        # Búsqueda por título y nombre del autor
        query_params.update({
            'IndexName': 'title-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('title_index').begins_with(title),
            'FilterExpression': Key('author_name_index').begins_with(author_name)
        })
    elif title and author_lastname:
        # Búsqueda por título y apellido del autor
        query_params.update({
            'IndexName': 'title-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('title_index').begins_with(title),
            'FilterExpression': Key('author_lastname_index').begins_with(author_lastname)
        })
    elif author_name and author_lastname:
        # Búsqueda por nombre y apellido del autor
        query_params.update({
            'IndexName': 'author_name-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('author_name_index').begins_with(author_name),
            'FilterExpression': Key('author_lastname_index').begins_with(author_lastname)
        })
    elif title:
        # Búsqueda solo por título
        query_params.update({
            'IndexName': 'title-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('title_index').begins_with(title)
        })
    elif author_name:
        # Búsqueda solo por nombre del autor
        query_params.update({
            'IndexName': 'author_name-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('author_name_index').begins_with(author_name)
        })
    elif author_lastname:
        # Búsqueda solo por apellido del autor
        query_params.update({
            'IndexName': 'author_lastname-index',
            'KeyConditionExpression': Key('tenant_id').eq(tenant_id) & Key('author_lastname_index').begins_with(author_lastname)
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
