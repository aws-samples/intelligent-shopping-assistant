import os
import sys
import json
from model import *
from prompt import *

response = {
    "statusCode": 200,
    "headers": {
        "Access-Control-Allow-Origin": '*'
    },
    "isBase64Encoded": False
}

def call_tools(query:str, model_id:str):
    messages = []
    input_msg = {"role": "user", "content": [{"text": query}]}
    messages.append(input_msg)
    output_msg, stop_reason = generate_response_with_tools(messages,model_id)
    print('output_msg:',output_msg)
    print('stop_reason:',stop_reason)
    
    tool_use_args_list = []
    answer = ""
    if stop_reason == "tool_use":
        tool_use_args_list = get_tool_use_args(output_msg)
        tool_answer_list = []
        for tool_use_args in tool_use_args_list:
            print('tool_use_args:',tool_use_args)
            tool_answer = execute_tool(tool_use_args)
            print('tool answer:',tool_answer)
            tool_answer_list.append(tool_answer)
        answer = '|'.join(tool_answer_list)
    else:
        answer = output_msg['content'][0]['text']
        
    return answer,tool_use_args_list


def lambda_handler(event, context):
    
    evt_body = event['queryStringParameters']
    
    query = "hello"
    if "query" in evt_body.keys():
        query = evt_body['query'].strip()
    print('query:',query)
    
    model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
    if "model_id" in evt_body.keys():
        model_id = evt_body['model_id'].strip()
    print('model_id:',model_id)

    history = ""
    if "history" in evt_body.keys():
        history = evt_body['history'].strip()
    print('history:',history)
    
    user_id = ""
    if "user_id" in evt_body.keys():
        user_id = evt_body['user_id'].strip()
    print('user_id:',user_id)
    
    products_info = ""
    if "products_info" in evt_body.keys():
        products_info = evt_body['products_info'].strip()
    print('products_info:',products_info)

    intention_system_prompt = get_intention_prompt(history)
    intention = invoke_model(query,intention_system_prompt,model_id)
    print('intention:',intention)
    
    tool_use_args = []
    answer = ''

    if intention == 'search': 
        #image search
        if query.find('image') >=0 or query.find('picture') >=0:
            prompt = keyword_for_image_search_prompt(query)
            answer = invoke_model(query,prompt,model_id)
            print('keyword for image search:',answer)

        #text search
        else:
            conversation_prompt = get_search_conversation_prompt(history)
            print('conversation_prompt:',conversation_prompt)
            answer = invoke_model(query,conversation_prompt,model_id)
            print('answer:',answer)
            if answer.find('Hold on') >=0:
                rewrite_prompt = get_query_rewrite_prompt(history)
                answer = invoke_model(query,rewrite_prompt,model_id)
                answer = 'keywords:' + answer
                print('keywords:',answer)


    elif intention == 'adding shopping cart':
        shopping_cart_info = query
        if len(user_id) > 0:
            shopping_cart_info += (',user_id:' + user_id) 
        if len(products_info) > 0:
            shopping_cart_info += (',products information:' + products_info) 
        answer,tool_use_args = call_tools(shopping_cart_info,model_id)
        print('tool answer:',answer)
        
    elif intention== 'check order':
        conversation_prompt = get_order_check_conversation_prompt(query,history)
        answer = invoke_model(query,conversation_prompt,model_id)
        print('answer:',answer)
        
        if answer.find('Hold on') >=0:
            order_info = 'conversation history:' + history + ' ,user_id:' + user_id
            answer,tool_use_args = call_tools(order_info,model_id)
            print('tool answer:',answer)
    else:
        answer = "I don't know the answer, please ask other question!"

    print('tool_use_args:',tool_use_args)
    response['body'] = json.dumps(
                    {
                        'answer':answer,
                        'tool_use_args':tool_use_args,
                        'intention':intention
                    })      
    
    return response
    
