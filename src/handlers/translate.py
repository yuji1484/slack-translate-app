import base64
import boto3
from http import HTTPStatus
import json
import logging
import os
import time
from urllib.parse import parse_qs
import urllib.request

translate_client = boto3.client('translate')
SLACK_VERIFICATION_TOKEN = os.environ['SLACK_VERIFICATION_TOKEN']
 
def handler(event, context):
    body = parse_qs(event['body'])
    params = json.loads(body['payload'][0])

    token = params['token']
    if token != SLACK_VERIFICATION_TOKEN
        return "Not Authed"

    input_text = params['message']['text']
    target_language = params['callback_id']
    response_url = params['response_url']

    res = translate_client.translate_text(
        Text=input_text,
        SourceLanguageCode='auto',
        TargetLanguageCode=target_language
    )
  
    translated_text = res["TranslatedText"]
    data = {
        'text':translated_text
    }

    res = urllib.request.Request(response_url, data=json.dumps(data).encode())
    urllib.request.urlopen(res)


    return {
        'statusCode': HTTPStatus.OK,
        'headers': {
            'Content-Type': 'application/json'
        }
    }
