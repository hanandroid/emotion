import boto3, json
from datetime import datetime

print('Loading function')      # Functionのロードをログに出力

def lambda_handler(event, context):
    # 文字列へ変換
    jsonstr = json.dumps(event, indent=2)
    print("Received event: " + jsonstr)

    timestamp = event['events'][0]['timestamp']
    print("timestamp: " + str(timestamp))


    return event
