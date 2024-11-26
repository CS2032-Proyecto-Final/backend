import os
import boto3
import uuid
import urllib.request
import json
from datetime import datetime, timedelta

def lambda_handler(event, context):

    body = event['body']

    # por ahora se pasa el tenant y email por el body, en realidad se conoce por el token

    tenant_id = body['tenant_id']
    email = body['email']
    isbn = body['isbn']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["RESERVATIONS_TABLE_NAME"])

    MB_url = f"https://fenlnd1g0c.execute-api.us-east-1.amazonaws.com/dev/books/get?tenant_id={tenant_id}&isbn={isbn}"
    ML_url = f"https://95tbi6q50h.execute-api.us-east-1.amazonaws.com/dev/libraries/info?tenant_id={tenant_id}"

    with urllib.request.urlopen(ML_url) as response:
        tenant_info = json.loads(response.read())

    with urllib.request.urlopen(MB_url) as response:
        book_info = json.loads(response.read())

    type = "book"
    res_id = str(uuid.uuid4())
    status = "pending"
    
    author = book_info['body']['author']
    title = book_info['body']['title']
    pickup_date = datetime.now().strftime('%d-%m-%Y')
    max_return_date = (datetime.now() + timedelta(days=tenant_info['body']['reserv_book_time'])).strftime('%d-%m-%Y')

    reservation = {
        "tenant_id#email": tenant_id + "#" + email,
        "type": type,
        "res_id": res_id,
        "status": status,
        "tenant_id#type": tenant_id + "#" + type,
        "email#status": email + "#" + status,
        "max_return_date#status": max_return_date + "#" + status,

        "isbn": isbn,
        "author": author,
        "title": title,
        "pickup_date": pickup_date,
        "max_return_date": max_return_date
    }

    response = table.put_item(Item=reservation)

    return {
        "statusCode": 200,
        "body": {
            "message": "Se reservó el libro existosamente",
            "reservation": reservation
        }
    }