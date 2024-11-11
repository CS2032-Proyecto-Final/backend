import boto3
import os
import hashlib
from datetime import datetime

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):

    body = event['body']
    email = body['email']
    password = body['password']
    firstname = body['firstname']
    lastname = body['lastname']
    tenant_id = body['tenant_id']

    # Esto se debería verificar (todavia no esta implementado creo asi que no puedo verificarlo)

    # if tenant_id es una universidad:
    #    if tenant_id != email.split('@')[1].split('.')[0]:
    #        return {
    #            'statusCode': 403,
    #            'body': {'error': 'Usuario no válido'}
    #        }

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
