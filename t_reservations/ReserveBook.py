import os
import boto3
import uuid
import urllib.request
import json
from datetime import datetime, timedelta

def lambda_handler(event, context):

    body = event['body']

    # por ahora se pasa el tenant y email por el body, en realidad se conoce por el token

    headers = event['headers']
    token = headers['Authorization']

    MU_url = f"https://n2tqx1stl1.execute-api.us-east-1.amazonaws.com/dev/tokens/validate"

    data = {
        "token": token
    }

    data_json = json.dumps(data).encode('utf-8')

    request = urllib.request.Request(MU_url, data=data_json, method="POST")

    with urllib.request.urlopen(request) as response:
        user_response = json.loads(response.read())

    if(user_response['statusCode'] == 403):
        return {
            "statusCode": 403,
            "body": {
                "message": "Token no válido"
            }
        }

    tenant_id = user_response['body']['tenant_id']
    email = user_response['body']['email']

    isbn = body['isbn']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["RESERVATIONS_TABLE_NAME"])

    MB_url = f"https://fenlnd1g0c.execute-api.us-east-1.amazonaws.com/dev/books/search?tenant_id={tenant_id}&email={email}&page=1&limit=1&isbn={isbn}"
    ML_url = f"https://95tbi6q50h.execute-api.us-east-1.amazonaws.com/dev/libraries/info?tenant_id={tenant_id}"

    with urllib.request.urlopen(ML_url) as response:
        tenant_info = json.loads(response.read())

    with urllib.request.urlopen(MB_url) as response:
        book_info = json.loads(response.read())

    type = "book"
    res_id = str(uuid.uuid4())
    status = "pending"

    if not book_info['body']['books']:
        return {
        "statusCode": 404,
        "body": {
            "message": "El libro a reservar no existe"
        }
    }
    
    author_name = book_info['body']['books'][0]['author_name']
    author_lastname = book_info['body']['books'][0]['author_lastname']
    title = book_info['body']['books'][0]['title']
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
        "author_name": author_name,
        "author_lastname": author_lastname,
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