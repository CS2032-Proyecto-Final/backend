import boto3
import os
import hashlib
import urllib.request
from urllib.error import URLError, HTTPError
from datetime import datetime
import json
from concurrent.futures import ThreadPoolExecutor

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_email_async(email_payload, email_endpoint):
    try:
        data = json.dumps(email_payload).encode('utf-8')

        req = urllib.request.Request(email_endpoint, data=data, method="POST")
        req.add_header('Content-Type', 'application/json')

        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(f"Error sending email: {response.read().decode('utf-8')}")
    except HTTPError as e:
        print(f"HTTPError: {e.code} - {e.reason}")
    except URLError as e:
        print(f"URLError: {e.reason}")
    except Exception as e:
        print(f"Exception occurred while sending email: {e}")

def lambda_handler(event, context):

    body = event['body']
    email = body['email']
    password = body['password']
    tenant_id = body['tenant_id']

    libraries_url = os.environ.get("LIBRARIES_URL")
    if not libraries_url:
        raise Exception("LIBRARIES_URL environment variable not set")

    api_url = f"{libraries_url}/libraries/customization?tenant_id={tenant_id}"

    with urllib.request.urlopen(api_url) as response:
        tenant_info = json.loads(response.read())

    firstname = ""
    lastname = ""

    if tenant_info["body"]["email_suffix"] != "*":
        if tenant_info["body"]["email_suffix"] != email.split('@')[1]:
            return {
                'statusCode': 403,
                'body': {'error': 'Usuario no válido'}
            }
        firstname = email.split('@')[0].split('.')[0].capitalize()
        lastname = email.split('@')[0].split('.')[1].capitalize()
    else:
        firstname = body['firstname']
        lastname = body['lastname']

    dynamodb = boto3.resource('dynamodb')
    users_table = dynamodb.Table(os.environ['USERS_TABLE_NAME'])

    user_item = users_table.get_item(
        Key={
            'tenant_id': tenant_id,
            'email': email
        }
    )

    if 'Item' in user_item:
        return {
            'statusCode': 409,
            'body': {'error': 'El usuario ya existe'}
        }

    hashed_password = hash_password(password)
    creation_date = datetime.now().strftime('%d-%m-%Y')

    users_table.put_item(
        Item={
            'tenant_id': tenant_id,
            'email': email,
            'password': hashed_password,
            'firstname': firstname,
            'lastname': lastname,
            'creation_date': creation_date
        }
    )

    email_payload = {
        "email": email,
        "firstname": firstname,
        "lastname": lastname,
        "creationDate": creation_date,
        "full_name" : tenant_info["body"]["full_name"],
        "color" : tenant_info["body"]["color"]["sidebar"],
        "tenant_id" : tenant_id
    }

    notifications_url = os.environ.get("NOTIFICATIONS_URL")
    if not notifications_url:
        raise Exception("NOTIFICATIONS_URL environment variable not set")

    # Email endpoint
    email_endpoint = f"{notifications_url}/emails/signUp"

    with ThreadPoolExecutor() as executor:
        executor.submit(send_email_async, email_payload, email_endpoint)

    return {
        'statusCode': 200,
        'body': {'message': 'El usuario se registró exitosamente'}
    }
