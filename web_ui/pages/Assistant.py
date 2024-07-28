import requests
import streamlit as st
import streamlit.components.v1 as components
import json
from datetime import datetime
import pandas as pd
from PIL import Image
from io import BytesIO
import base64
import boto3
from botocore.exceptions import ClientError
import time
import os
import ast


index = 'shopping_demo_test'
language = 'english' #english or chinese
account=''
region=''

assistant_invoke_url = ''
ads_invoke_url = ''
product_search_invoke_url = ''

product_search_sagemaker_endpoint = ""
reranker_sagemaker_endpoint = ''

#Optional
image_search_invoke_url = ''
image_search_sagemaker_endpoint = ''


conversation_rounds = 6
model_name = "anthropic.claude-3-sonnet-20240229-v1:0"

ads_prompt = """
You are an e-commerce customer service staff. Please generate a shopping guide for the products based on the user's questions and products information.

<products information>
{items_info}
</products information>

customer's question:{question}

No preface, just go straight to the product guide.
"""

product_prompt = """

You are an e-commerce customer service staff, please answer the user's questions based on the user's questions and product information.

<product information>
{items_info}
</product information>

customer's question:{question}

No preface, just go straight to the product guide.
"""

def get_user_id():
    return '123456'

def get_history(messages,k:int=3):
    if len(messages) < 2*k + 1:
        messages = messages[1:]
    else:
        messages = messages[-2*k:]

    history = ''
    for message in messages:
        print('message:',message)
        if message['role'] == 'user':
            history += ('user:'+ str(message['content']) + '\n')
        elif message['role'] == 'assistant':
            history += ('AI：'+ str(message['content']) + '\n')
    return history


def product_search(query,
                invoke_url,
                index,
                modelName: str = '',
                endpointName: str = '',
                rerankerEndpoint: str = '',
                searchType: str = 'text',
                textSearchNumber: int = 3,
                vectorSearchNumber: int = 0,
                textScoreThresholds: float = 0,
                vectorScoreThresholds: float = 0,
                language: str = '',
                productId: str = '',
                productName: str = '',
                description: str= '',
                keywords: str='',
                filter_item_id: list=[]
                ):
    url = invoke_url + '/product_search?'
    url += ('&query='+query)
    url += ('&searchType='+searchType)
    url += ('&index='+index)
    if len(modelName) > 0:
        url += ('&modelName='+modelName)
    if len(endpointName) > 0:
        url += ('&embeddingEndpoint='+endpointName)
    if len(rerankerEndpoint) > 0:
        url += ('&rerankerEndpoint='+rerankerEndpoint)
    if textSearchNumber > 0:
        url += ('&textSearchNumber='+str(textSearchNumber))
    if vectorSearchNumber > 0:
        url += ('&vectorSearchNumber='+str(vectorSearchNumber))
    if textScoreThresholds > 0:
        url += ('&textScoreThresholds='+str(textScoreThresholds))
    if vectorScoreThresholds > 0:
        url += ('&vectorScoreThresholds='+str(vectorScoreThresholds))
    if len(language) > 0:
        url += ('&language='+language)
    if len(productId) > 0:
        url += ('&productId='+productId)
    if len(productName) > 0:
        url += ('&productName='+productName)
    if len(description) > 0:
        url += ('&description='+description)
    if len(keywords) > 0:
        url += ('&keywords='+keywords)
    if len(filter_item_id) > 0:
        url += ('&itemFilterId='+','.join(filter_item_id))

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print("result:",result)
    products = result['products']

    return products


def get_item_ads(query,items_info,prompt,model_name:str=""):
    url = ads_invoke_url + '/get_item_ads?query='
    url += query
    url += ('&itemInfo='+items_info)
    url += ('&prompt='+prompt)
    if len(model_name) > 0:
        url += ('&modelName='+model_name)
    url += ('&modelType=bedrock')
    url += ('&language=chinese')

    print('get_user_info url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    item_ads = result['item_ads']

    print('item ads:',item_ads)
    return item_ads


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        return False
    return True

def get_image_coordinate(image_name,product,bucket_name,invoke_url,bucket:str='',prompt:str=''):
    url = invoke_url + '/image_search?'
    new_image_name = image_name.split('.')[0] + '-' + str(time.time()) + '.' + image_name.split('.')[-1]
    upload_file(image_name,bucket_name,new_image_name)
    url += ('&imageName='+new_image_name)
    if len(product) > 0:
        url += ('&product='+product)
    if len(bucket) > 0:
        url += ('&bucket='+bucket)
    if len(prompt) > 0:
        url += ('&prompt='+prompt)

    url += ('&task=image-coordinate')

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print("result:",result)
    coordinate = result['coordinate']
    if coordinate.find('\n\n') > 0:
        coordinate = coordinate.split('\n\n')[1].strip()
    coordinate = json.loads(coordinate)
    print('coordinate:',coordinate)

    return coordinate

def image_search(image_url,index,invoke_url,endpoint_name,vectorSearchNumber):
    url = invoke_url + '/image_search?'
    if len(image_url) > 0:
        url += ('&url='+image_url)
    url += ('&index='+index)
    url += ('&task=image-search')
    url += ('&embeddingEndpoint='+endpoint_name)
    url += ('&vectorSearchNumber='+str(vectorSearchNumber))

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print("result:",result)
    products = result['products']
    return products


def image_search_localfile(image_name,index,invoke_url,bucket_name,endpoint_name,vectorSearchNumber):
    url = invoke_url + '/image_search?'
    new_image_name = image_name.split('.')[0] + '-' + str(time.time()) + '.' + image_name.split('.')[-1]
    upload_file(image_name,bucket_name,new_image_name)
    url += ('&imageName='+new_image_name)
    url += ('&index='+index)
    url += ('&task=image-search')
    url += ('&embeddingEndpoint='+endpoint_name)
    url += ('&vectorSearchNumber='+str(vectorSearchNumber))

    print('url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)
    print("result:",result)
    products = result['products']

    return products


def assistant(query,user_id,history,products_info):
    url = assistant_invoke_url + '/assistant?query='
    url += query
    if len(user_id) > 0:
        url += ('&user_id='+str(user_id))
    if len(history) > 0:
        url += ('&history='+history)
    if len(products_info) > 0:
        url += ('&products_info='+products_info)
    print('get_user_info url:',url)
    response = requests.get(url)
    result = response.text
    result = json.loads(result)

    print('assistant result:',result)
    return result

# App title
st.set_page_config(page_title="aws intelligent shopping assistant solution")


with st.sidebar:
    st.title('AWS Intelligent Shopping Assistant Solution Guide')

    search_type = 'mix'
    textSearchNumber = 3
    textScoreThresholds = 0
    vectorSearchNumber = 3
    vectorScoreThresholds = 0
    top_k = 3

    image_coloum_name = st.text_input(label="Image coloum name", value="ImageURL")
    item_id_coloum_name = st.text_input(label="Product id coloum name", value="ProductId")
    item_name_coloum_name = st.text_input(label="Product name coloum name", value="ProductTitle")
    Keywords_coloum_name = st.text_input(label="Keywords coloum name", value="")
    Description_coloum_name = st.text_input(label="Description coloum name", value="")


st.session_state.uploaded_file = st.file_uploader("Upload Image",type=['png', 'jpg','jpeg'])
if st.session_state.uploaded_file:
    #st.image(st.session_state.uploaded_file)
    image = Image.open(st.session_state.uploaded_file)
    image.save(st.session_state.uploaded_file.name)
    size = 500
    if image.size[0] > size:
        image = image.resize((size,int(image.size[1]*size / image.size[0])))
    st.image(image)


# Store LLM generated responses
if "messages" not in st.session_state.keys():
    # st.session_state.messages = [{"role": "assistant", "content": "Hello,How may I assist you today?"}]
    if language == 'english':
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    elif language == 'chinese':
        st.session_state.messages = [{"role": "assistant", "content": "您好，请问有什么可以帮助您吗?"}]
    elif language == 'chinese-tc':
        st.session_state.messages = [{"role": "assistant", "content": "您好，請問有什麽可以幫助您嗎?"}]

    now = datetime.now()
    timestamp = datetime.timestamp(now)
    st.session_state.sessionId = 'qa'+str(timestamp)
    st.session_state.uploaded_file = ''
    st.session_state.item_info = ''
    st.session_state.item_ids = []


# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    if language == 'english':
        st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]
    elif language == 'chinese':
        st.session_state.messages = [{"role": "assistant", "content": "您好，请问有什么可以帮助您吗?"}]
    elif language == 'chinese-tc':
        st.session_state.messages = [{"role": "assistant", "content": "您好，請問有什麽可以幫助您嗎?"}]

    st.session_state.uploaded_file = ''
    st.session_state.item_info = ''
    st.session_state.item_ids = []

    now = datetime.now()
    timestamp = datetime.timestamp(now)
    st.session_state.sessionId = 'shopping'+str(timestamp)


# User-provided prompt
if query := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.write(query)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            bucket_name = "intelligent-image-search-data" + "-" + account + "-" + region
            placeholder = st.empty()
            #try:
            if True:
                
                history = get_history(st.session_state.messages,conversation_rounds)
                user_id = get_user_id()
        
                result = assistant(query,user_id,history,st.session_state.item_info)
                intention = result['intention']
                if intention == 'search':
                    products = []
                    if st.session_state.uploaded_file is not None:
                        keyword = result['answer']
                        coordinate = get_image_coordinate(st.session_state.uploaded_file.name,keyword,bucket_name,image_search_invoke_url)
                        if len(coordinate) > 0:
                            image = Image.open(st.session_state.uploaded_file.name)
                            print('image size:',image.size)
                            if image.size[0] > 500:
                                image = image.resize((500,int(image.size[1]*500 / image.size[0])))
                            print('resize image size:',image.size)
                            cropped_iamge = image.crop((coordinate['x'],coordinate['y'],coordinate['x1'],coordinate['y1']))
                            cropped_iamge.save('cropped_'+st.session_state.uploaded_file.name)
                            products = image_search_localfile('cropped_'+st.session_state.uploaded_file.name,index,image_search_invoke_url,bucket_name,image_search_sagemaker_endpoint,vectorSearchNumber)
                            os.remove('cropped_'+st.session_state.uploaded_file.name)
                        os.remove(st.session_state.uploaded_file.name)
                    
                    else:
                        answer = result['answer']
                        if answer.find('keywords:') >=0:
                            query = answer.split('keywords:')[-1]
                            products = product_search(query,
                                  product_search_invoke_url,
                                  model_name,
                                  index,
                                  product_search_sagemaker_endpoint,
                                  reranker_sagemaker_endpoint,
                                  search_type,
                                  textSearchNumber,
                                  vectorSearchNumber,
                                  textScoreThresholds,
                                  vectorScoreThresholds,
                                  productId=item_id_coloum_name,
                                  productName=item_name_coloum_name,
                                  description=Description_coloum_name,
                                  keywords=Keywords_coloum_name,
                                  filter_item_id=st.session_state.item_ids
                                 )
                        else:
                            response = answer
                            st.write(response)
                            
                    if len(products) > 0:
                        products = products[:top_k]
                        items_num = len(products)
                        col1, col2, col3 = st.columns(3)
                        image_list = []
                        scores_list = []
                        source_list = []

                        for product in products:
                            score = product['score']
                            scores_list.append(str(score))
                            source = product['product_info']
                            source_list.append(source)

                            if image_coloum_name in source.keys():
                                image_list.append(source[image_coloum_name])

                        st.session_state.item_info = str(source_list)

                        for item in source_list:
                            print('item:',item)
                            st.session_state.item_ids.append(item[item_id_coloum_name])

                        products_ad = get_item_ads(query,str(source_list),ads_prompt,model_name)
                        st.write(products_ad)
                        response = products_ad
                        
                        with col1:
                            for i in range(items_num):
                                col = i % 3
                                if col == 0:
                                    st.image(image_list[i])
                                    with st.expander("Product details"):
                                        score = scores_list[i]
                                        score_str = f"<p style='font-size:12px;'>score:{score}</p>"
                                        st.markdown(score_str,unsafe_allow_html=True)
                                        
                                        source = source_list[i]
                                        for key in source.keys():
                                            value = source[key]
                                            info_str = f"<p style='font-size:12px;'>{key}:{value}</p>"
                                            st.markdown(info_str,unsafe_allow_html=True)

                        with col2:
                            for i in range(items_num):
                                col = i % 3
                                if col == 1:
                                    st.image(image_list[i])
                                    with st.expander("Product details"):
                                        score = scores_list[i]
                                        score_str = f"<p style='font-size:12px;'>score:{score}</p>"
                                        st.markdown(score_str,unsafe_allow_html=True)
                                        
                                        source = source_list[i]
                                        for key in source.keys():
                                            value = source[key]
                                            info_str = f"<p style='font-size:12px;'>{key}:{value}</p>"
                                            st.markdown(info_str,unsafe_allow_html=True)
                                        
                        with col3:
                            for i in range(items_num):
                                col = i % 3
                                if col == 2:
                                    st.image(image_list[i])
                                    with st.expander("Product details"):
                                        score = scores_list[i]
                                        score_str = f"<p style='font-size:12px;'>score:{score}</p>"
                                        st.markdown(score_str,unsafe_allow_html=True)
                                        
                                        source = source_list[i]
                                        for key in source.keys():
                                            value = source[key]
                                            info_str = f"<p style='font-size:12px;'>{key}:{value}</p>"
                                            st.markdown(info_str,unsafe_allow_html=True)

                elif intention == 'product issues':
                    response = get_item_ads(query,st.session_state.item_info,product_prompt)
                    st.write(response)

                else:
                    response = result['answer']
                    tool_use_args = result['tool_use_args']
                    if len(tool_use_args) > 0:
                        answers = response.split('|')
                        for i in range(len(answers)):
                            answer = answers[i]
                            tool_name = tool_use_args[i]['name']
                            tool_input = tool_use_args[i]['input']
                            st.write(answer)
                            st.write('tool input:' + str(tool_input))
                    else:
                        st.write(response)

            #except:
            #    placeholder.markdown("您好，麻烦您重新提问!")
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)