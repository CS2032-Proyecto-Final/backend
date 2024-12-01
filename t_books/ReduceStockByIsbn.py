import boto3
import os
import urllib.request
import json

def lambda_handler(event, context):
    # Obtener parámetros de entrada
    isbn = event['body']['isbn']

    # Validar token
    token = event['headers']['Authorization']

    data = json.dumps({"token": token}).encode('utf-8')

    req = urllib.request.Request(f"{os.environ['USERS_URL']}/tokens/validate", data=data, method="POST", headers={"Content-Type": "application/json"})

    user_response = json.loads(urllib.request.urlopen(req).read())
    
    if user_response.get('statusCode') == 403:
        return {"statusCode": 403, "body": {"message": "Token no válido"}}
    
    tenant_id = user_response['body']['tenant_id']
    email = user_response['body']['email']

    # Conexión a DynamoDB
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["TABLE_NAME"])

    # Obtener el libro por tenant_id e isbn
    response = table.get_item(
        Key={
            "tenant_id": tenant_id,
            "isbn": isbn
        }
    )

    # Verificar si el libro existe
    if "Item" not in response:
        return {
            "statusCode": 404,
            "body": {"message": "Book not found"}
        }

    book = response["Item"]

    # Verificar si hay stock disponible
    if book.get("quantity", 0) <= 0:
        return {
            "statusCode": 406,
            "body": {"message": "No stock"}
        }

    # Disminuir la cantidad en 1
    new_quantity = book["quantity"] - 1
    table.update_item(
        Key={
            "tenant_id": tenant_id,
            "isbn": isbn
        },
        UpdateExpression="SET quantity = :new_quantity",
        ExpressionAttributeValues={
            ":new_quantity": new_quantity
        }
    )

    # Respuesta de éxito
    return {
        "statusCode": 200,
        "body": {"message": "Stock updated successfully", "new_quantity": new_quantity}
    }
