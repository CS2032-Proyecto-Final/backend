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

    env_type = body['type']
    name = body['name']
    hour = body['hour']
    formatted_hour = str(hour).zfill(2)

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["RESERVATIONS_TABLE_NAME"])

    headers_data = {
        "Authorization": token
    }

    ME_url = f"{os.environ["ENVIRONMENTS_URL"]}/environment/info?&type={env_type}&env_name={name}&hour={formatted_hour}"
    ML_url = f"{os.environ["LIBRARIES_URL"]}/libraries/info"

    ME_request = urllib.request.Request(ME_url, headers=headers_data)

    ML_request = urllib.request.Request(ML_url, headers=headers_data)

    with urllib.request.urlopen(ML_request) as response:
        tenant_info = json.loads(response.read())

    with urllib.request.urlopen(ME_request) as response:
        env_info = json.loads(response.read())

    if env_info['statusCode'] == 404:
        return {
        "statusCode": 404,
        "body": {
            "message": "El ambiente a reservar no existe"
        }
    }

    if env_info['body']['status'] != "available":
        return {
            "statusCode": 406,
            "body": {
                "message": "El ambiente a reservar no está disponible a la hora especificada"
            }
        }
    
    type = "env"
    res_id = str(uuid.uuid4())
    status = "pending"
    date = datetime.now().strftime('%d-%m-%Y')
    capacity = env_info['body']['capacity']

    # Cambiar el estado del env a unavailable

    ME_url = f"{os.environ["ENVIRONMENTS_URL"]}/environment/status"

    data = {
        "type": env_type,
        "name": name,
        "hour": formatted_hour,
        "status": "unavailable"
    }

    data_json = json.dumps(json.dumps(data)).encode('utf-8')

    request = urllib.request.Request(ME_url, data=data_json, headers=headers_data, method="PATCH")

    request.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(request) as response:
        update_response = json.loads(response.read())
        print(update_response)


    reservation = {
        "tenant_id#email": tenant_id + "#" + email,
        "type": type,
        "res_id": res_id,
        "status": status,
        "tenant_id#type": tenant_id + "#" + type,
        "email#status": email + "#" + status,

        "env_name": name,
        "date": date,
        "hour": hour,
        "capacity": capacity
    }

    response = table.put_item(Item=reservation)

    return {
        "statusCode": 200,
        "body": {
            "message": "Se reservó el ambiente existosamente",
            "reservation": reservation
        }
    }