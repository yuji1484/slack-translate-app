import base64
import boto3
import os
from slack import WebClient
from http import HTTPStatus
import json
import logging

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USER_TOKENS_TABLE'])
kms_client = boto3.client('kms')
logger = logging.getLogger()

def handler(event, context):
    
    client = WebClient()
    client_id = os.environ['SLACK_CLIENT_ID']
    client_secret = os.environ['SLACK_CLIENT_SECRET']
    code = event['queryStringParameters']['code']
    
    response = client.oauth_v2_access(
        client_id=client_id,
        client_secret=client_secret,
        code=code
    )
    
    token = response.data['authed_user']['access_token']
    kms_res = kms_client.encrypt(
        KeyId=os.environ['KMS_KEY_ID'],
        Plaintext=token.encode()
    )
 
    encrypted_token = base64.b64encode(kms_res['CiphertextBlob'] ).decode('utf-8')

    user_id = response.data['authed_user']['id']
    table.put_item(Item={
        'token': encrypted_token,
        'user_id': user_id
    })
 
    return {
            'statusCode': HTTPStatus.OK,
            'body': json.dumps({'text':'/translate command is successfully installed!!'}),
            'headers': {
                'Content-Type': 'application/json'
            }
    }
