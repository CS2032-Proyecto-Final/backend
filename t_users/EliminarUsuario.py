import boto3

def lambda_handler(event, context):
    # Inicio - Proteger el Lambda
    token = event['headers']['Authorization']
    lambda_client = boto3.client('lambda')    
    payload_string = '{ "token": "' + token +  '" }'
    invoke_response = lambda_client.invoke(FunctionName="ValidarTokenAcceso",
                                           InvocationType='RequestResponse',
                                           Payload=payload_string)
    response = json.loads(invoke_response['Payload'].read())
    print(response)
    if response['statusCode'] == 403:
        return {
            'statusCode': 403,
            'status': 'Forbidden - Acceso No Autorizado'
        }
    # Fin - Proteger el Lambda        

    # Proceso
    tenant_id = event['tenant_id']
    email = event['email']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_usuario')
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'email': email
        }
    )
    
    # Entrada (json)
    tenant_id = event['tenant_id']
    email = event['email']
    # Proceso
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('t_alumnos')
    response = table.delete_item(
        Key={
            'tenant_id': tenant_id,
            'email': email
        }
    )
    # Salida (json)
    return {
        'statusCode': 200,
        'response': response
    }