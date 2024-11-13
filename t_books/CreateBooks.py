import boto3
import os

def lambda_handler(event, context):
    # Obtener el nombre de la tabla desde la variable de entorno
    nombre_tabla = os.environ["TABLE_NAME"]

    # Conectar a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(nombre_tabla)

    # Lista de libros para insertar
    libros = event['body']

    # Procesar e insertar cada libro en la tabla
    for libro in libros:
        # Generar índices en minúsculas para búsqueda insensible a mayúsculas/minúsculas
        libro['title_index'] = libro['title'].lower()
        libro['author_name_index'] = libro['author_name'].lower()
        libro['author_lastname_index'] = libro['author_lastname'].lower()

        # Insertar el libro en la tabla de DynamoDB
        table.put_item(Item=libro)

    # Retornar una respuesta de éxito
    return {
        'statusCode': 200,
        'body': {
            'message': 'Books created successfully',
            'books': libros
        }
    }
