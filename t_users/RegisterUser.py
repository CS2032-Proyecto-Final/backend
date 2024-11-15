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
        # Convert the email payload to JSON
        data = json.dumps(email_payload).encode('utf-8')

        # Create a request object
        req = urllib.request.Request(email_endpoint, data=data, method="POST")
        req.add_header('Content-Type', 'application/json')

        # Send the request
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

    api_url = f"https://95tbi6q50h.execute-api.us-east-1.amazonaws.com/dev/libraries/info?tenant_id={tenant_id}"

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

    # Prepare the payload for the notification email
    email_payload = {
        "email": email,
        "firstname": firstname,
        "lastname": lastname,
        "creationDate": creation_date,
        "full_name" : tenant_info["body"]["full_name"],
        "color" : tenant_info["body"]["color"]["sidebar"]
    }

    # Email endpoint
    email_endpoint = "https://epa4o89cfl.execute-api.us-east-1.amazonaws.com/dev/emails/signUp"

    # Asynchronously send the email
    with ThreadPoolExecutor() as executor:
        executor.submit(send_email_async, email_payload, email_endpoint)

    return {
        'statusCode': 200,
        'body': {'message': 'El usuario se registró exitosamente'}
    }
