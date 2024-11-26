import os
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):

    #body = event['body']

    # por ahora se pasa el tenant y email por params, en realidad se conoce por el token

    query_params = event['query']

    tenant_id = query_params['tenant_id']
    email = query_params['email']

    if 'status' not in query_params:
        status = False
    else:
        status = query_params['status']

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ["RESERVATIONS_TABLE_NAME"])

    gsi = "tenant_id-type_GSI"
    lsi = "type_LSI"

    if status:
        response = table.query(
            IndexName=gsi,
            KeyConditionExpression=Key('tenant_id#type').eq(tenant_id + "#book") & Key('email#status').eq(email + "#" + status)
        )
    else:
        response = table.query(
            IndexName=lsi,
            KeyConditionExpression=Key('tenant_id#email').eq(tenant_id + "#" + email) & Key('type').eq("book")
        )

    items = response['Items']

    return {
        "statusCode": 200,
        "body": {
            "message": "Se obtuvieron las reservas exitosamente",
            "reservations": items
        }
    }