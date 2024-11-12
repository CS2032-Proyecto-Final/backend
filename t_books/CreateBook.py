import boto3
import os

def lambda_handler(event, context):
    
    # Entrada desde el evento
    tenant_id = event['body']['tenant_id']
    isbn = event['body']['isbn']
    title = event['body']['title']
    author_name = event['body']['author_name']
    author_lastname = event['body']['author_lastname']
    quantity = event['body']['quantity']
    pages = event['body']['pages']
    stock = event['body']['stock']
    
    # Obtener el nombre de la tabla desde la variable de entorno
    nombre_tabla = os.environ["TABLE_NAME"]
    
    # Crear el objeto libro con índices en minúsculas
    libro = {
        'tenant_id': tenant_id,
        'isbn': isbn,
        'title': title,
        'title_index': title.lower(),  # Version minúscula para búsqueda
        'author_name': author_name,
        'author_name_index': author_name.lower(),  # Version minúscula para búsqueda
        'author_lastname': author_lastname,
        'author_lastname_index': author_lastname.lower(),  # Version minúscula para búsqueda
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
