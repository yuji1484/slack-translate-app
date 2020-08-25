import base64
import boto3
from http import HTTPStatus
import json
import logging
import os
import re
from slack.web.client import WebClient
from slack.errors import SlackApiError
import time
from urllib.parse import parse_qs

dynamodb = boto3.resource('dynamodb')
kms_client = boto3.client('kms')
token_table = dynamodb.Table(os.environ['USER_TOKENS_TABLE'])
translate = boto3.client('translate')
logger = logging.getLogger()

def handler(event, context):
    body = event['body']
    params = parse_qs(body)
    channel_id = params['channel_id'][0]
    user_id = params['user_id'][0]
    
    if 'text' not in params:
        return cmd_help()
    
    res = token_table.get_item(Key={'user_id': user_id})
    if 'Item' not in res:
        return please_install()

    encrypt_token = res['Item']['token']
    blob_token = base64.b64decode(encrypt_token)
    kms_res = kms_client.decrypt(CiphertextBlob=blob_token)
    decrypted_token = kms_res['Plaintext'].decode('utf-8')
    
    input_text = params['text'][0].split()
    TargetLanguageCode = input_text[0]
    main_text = input_text[1]
    response = translate.translate_text(
        Text=main_text,
        SourceLanguageCode='auto',
        TargetLanguageCode=TargetLanguageCode
    )
    
    client = WebClient(token=decrypted_token)
    client.chat_postMessage(channel=channel_id, text=response['TranslatedText'])
    return {
        'statusCode': HTTPStatus.OK,
        'body': json.dumps({'text': 'Input: ' + input_text[1] }),
        'headers': {
            'Content-Type': 'application/json'
        }
    }
    
def cmd_help(title='help'):
    text = """
`/translate` ... show help
`/translate [lang_code] [text]` ... translate [text] and post current channel as you
ex) `/transalte en こんにちは` => you can post "Hello" to current channel

*lang_code*
- `ja` ... Japanese
- `en` ... English 
- `ko` ... Korean
- `de` ... German
- `vi` ... Vietnamese 
- `hi` ... Hindi
- show more lang_code(https://docs.aws.amazon.com/translate/latest/dg/what-is.html#what-is-languages)
"""
    return {
        'statusCode': HTTPStatus.OK,
        'body': json.dumps({
            'text': title,
            'response_type': 'ephemeral',
            'attachments': [{
                'color': '#36a64f',
                'pretext': 'how to use /translate command ↓',
                'text': text
            }]
        }),
        'headers': {
                'Content-Type': 'application/json'
        }
    }  

def please_install():
    return {
            'statusCode': HTTPStatus.OK,
            'body': json.dumps({
              'text': '*Plese install !!*',
              'response_type': 'ephemeral',
              'attachments': [{
                  'text': 'ここ(URL)からインストールしてください'
                }]
            }),
          'headers': {
                    'Content-Type': 'application/json'
            }               
        }
