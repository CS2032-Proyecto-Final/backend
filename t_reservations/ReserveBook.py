import os
import boto3
import uuid
import urllib.request
import json
from datetime import datetime, timedelta

def lambda_handler(event, context):

    body = event['body']
    
    headers = event['headers']
    token = headers['Authorization']

    MU_url = f"{os.environ["USERS_URL"]}/tokens/validate"

    data = {
        "token": token
    }

    data_json = json.dumps(data).encode('utf-8')

    request = urllib.request.Request(MU_url, data=data_json, method="POST")

    request.add_header("Content-Type", "application/json")

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

    headers_data = {
        "Authorization": token
    }

    MB_url = f"{os.environ["BOOKS_URL"]}/books/search?page=1&limit=1&isbn={isbn}"

    ML_url = f"{os.environ["LIBRARIES_URL"]}/libraries/info?tenant_id={tenant_id}"

    MB_request = urllib.request.Request(MB_url, headers=headers_data)

    ML_request = urllib.request.Request(ML_url, headers=headers_data)

    with urllib.request.urlopen(ML_request) as response:
        tenant_info = json.loads(response.read())

    with urllib.request.urlopen(MB_request) as response:
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