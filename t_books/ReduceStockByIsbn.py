import boto3
import os

def lambda_handler(event, context):
    # Obtener parámetros de entrada
    tenant_id = event['query']['tenant_id']
    isbn = event['body']['isbn']

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
