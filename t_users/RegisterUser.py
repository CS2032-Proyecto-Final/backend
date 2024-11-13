import boto3
import os
import hashlib
import urllib.request
from datetime import datetime
import json

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

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
       firstname = email.split('@')[0].split('.')[0]
       lastname = email.split('@')[0].split('.')[1]
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
    creation_date = datetime.now().isoformat()

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

    return {
        'statusCode': 200,
        'body': {'message': 'El usuario se registró existosamente'}
    }
