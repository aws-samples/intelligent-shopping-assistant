import os
import json
from session import get_table_info
TABLE_NAME = os.environ.get('dynamodb_table_name')


def lambda_handler(event, context):
    
    print("event:",event)
    evt_body = event['queryStringParameters']
    
    user_table_name = ''
    if "userTableName" in evt_body.keys():
        user_table_name = evt_body['userTableName'].strip()
    print('user_table_name:',user_table_name)    
    
    userId = 1
    if "userId" in event.keys():
        userId = event['userId']
    elif "queryStringParameters" in event.keys():
        if "userId" in evt_body.keys():
            userId = evt_body['userId'].strip()
        
    userInfo = get_table_info(user_table_name, userId, 'user')
    print('userInfo:',userInfo)
    userBase = userInfo['user_base']
    userHistory = userInfo['user_history']
    
    print('user_base:',userBase)
    print('user_history:',userHistory)
    response = {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": '*'
        },
        "isBase64Encoded": False
    }
    
    response['body'] = json.dumps(
    {
        'user_base':userBase,
        'user_history':userHistory
    })
    return response