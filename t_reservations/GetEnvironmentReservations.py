import os
import boto3
import json
import urllib.request
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):

    query_params = event['query']

    if 'status' not in query_params:
        status = False
    else:
        status = query_params['status']

    headers = event['headers']
    token = headers['Authorization']

    MU_url = f"https://n2tqx1stl1.execute-api.us-east-1.amazonaws.com/dev/tokens/validate"

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

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["RESERVATIONS_TABLE_NAME"])

    gsi = "tenant_id-type_GSI"
    lsi = "type_LSI"

    if status:
        response = table.query(
            IndexName=gsi,
            KeyConditionExpression=Key('tenant_id#type').eq(tenant_id + "#env") & Key('email#status').eq(email + "#" + status)
        )
    else:
        response = table.query(
            IndexName=lsi,
            KeyConditionExpression=Key('tenant_id#email').eq(tenant_id + "#" + email) & Key('type').eq("env")
        )

    items = response['Items']

    return {
        "statusCode": 200,
        "body": {
            "message": "Se obtuvieron las reservas exitosamente",
            "reservations": items
        }
    }