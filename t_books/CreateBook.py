import boto3
import os
import urllib.request
import json

def lambda_handler(event, context):
    
    # Entrada desde el evento
    isbn = event['body']['isbn']
    title = event['body']['title']
    author_name = event['body']['author_name']
    author_lastname = event['body']['author_lastname']
    quantity = event['body']['quantity']
    pages = event['body']['pages']
    stock = event['body']['stock']

    # Validar token
    token = event['headers']['Authorization']

    data = json.dumps({"token": token}).encode('utf-8')

    req = urllib.request.Request(f"{os.environ['USERS_URL']}/tokens/validate", data=data, method="POST", headers={"Content-Type": "application/json"})

    user_response = json.loads(urllib.request.urlopen(req).read())
    
    if user_response.get('statusCode') == 403:
        return {"statusCode": 403, "body": {"message": "Token no válido"}}
    
    tenant_id = user_response['body']['tenant_id']
    email = user_response['body']['email']
    
    # Obtener el nombre de la tabla desde la variable de entorno
    nombre_tabla = os.environ["TABLE_NAME"]
    
    # Crear el objeto libro con índices en minúsculas
    libro = {
        'tenant_id': tenant_id,
        'isbn': isbn,
        'title': title,
        'title_index': title.lower(),
        'author_name': author_name,
        'author_name_index': author_name.lower(),
        'author_lastname': author_lastname,
        'author_lastname_index': author_lastname.lower(),
        'quantity': quantity,
        'pages': pages,
        'stock': stock
    }
    
    # Guardar el libro en DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(nombre_tabla)
    response = table.put_item(Item=libro)
    
    # Retornar respuesta
    return {
        'statusCode': 200,
        'body': {
            'message': 'Book created successfully',
            'book': libro
        }
    }
