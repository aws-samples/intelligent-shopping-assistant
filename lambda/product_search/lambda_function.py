import os
import json
import traceback
import urllib.parse
import boto3
from datetime import datetime
import time
from model import init_embeddings,init_vector_store
from chat_bot import *
from search_prompt import get_examples
from search_metadata import *
from langchain.vectorstores import MyScale,MyScaleSettings
from langchain.retrievers.self_query.base import SelfQueryRetriever

from opensearch_search import get_opensearch_client
from embeddings import get_embedding_sagemaker,get_reranker_scores,get_embedding_bedrock

EMBEDDING_ENDPOINT_NAME = os.environ.get('embedding_endpoint_name')
LLM_ENDPOINT_NAME = os.environ.get('llm_embedding_name')
region = os.environ.get('AWS_REGION')
INDEX =  os.environ.get('index')
host =  os.environ.get('host')
LANGUAGE =  os.environ.get('language')
port = 443

def get_retriever(database,vector_store,region,
                 sagemakerEndpoint: str = 'pytorch-inference-llm-v1',
                 temperature: float = 0.01,
                 modelType:str = "normal",
                 apiUrl:str = "",
                 modelName:str="anthropic.claude-v2",
                 apiKey:str = "",
                 secretKey:str = "",
                 maxTokens:int=512,
                 ):
                        
    metadata_field_info = get_metadata_field_info(database)
    document_content_description = get_document_content_description()
    
    chain_kwargs = {}
    chain_kwargs["examples"]=get_examples(database)
    chat_bot = ShoppingGuideChatBot()
    chat_bot.init_cfg(
                     region,
                     sagemakerEndpoint,
                     temperature,
                     modelType,
                     apiUrl,
                     modelName,
                     apiKey,
                     secretKey,
                     maxTokens
                     )
    
    retriever = SelfQueryRetriever.from_llm(
        chat_bot.get_llm(), vector_store, document_content_description, metadata_field_info,
        chain_kwargs=chain_kwargs,
        verbose=True
    )
    return retriever


def text_search(index: str, search_term: str, name:str='', keywords:str='', description:str='', size: int = 10):
    client = get_opensearch_client()
    offset = 0
    collapse_size = int(max(size / 15, 15))
    
    body ={
            "from": offset,
            "size": size,
            "query": {
                "dis_max" : {
                    "queries" : [
                    ],
                    "tie_breaker" : 0.7
                }
            },
            "fields":[
                "_id"
            ]
        }
    
    if len(name) > 0:
        name_query = { "match_bool_prefix" : { "metadata."+name : { "query": search_term, "boost": 1.2 }}}
        body['query']['dis_max']['queries'].append(name_query)
        
    if len(keywords) > 0:
        keyword_query = { "match_bool_prefix" : { "metadata."+keywords : { "query": search_term, "boost": 1 }}}
        body['query']['dis_max']['queries'].append(keyword_query)
    
    if len(description) > 0:
        description_query = { "match_bool_prefix" : { "metadata."+description : { "query": search_term, "boost": 1 }}}
        body['query']['dis_max']['queries'].append(description_query)

    results = client.search(index = index, body=body)

    return results['hits']['hits']

def vector_search(index: str, query_vector: List[float], size: int = 10,vector_field: str = "vector_field"):
    client = get_opensearch_client()
    offset = 0
    collapse_size = int(max(size / 15, 15))

    results = client.search(index = index, body={
                "size": size,
                "query": {"knn": {vector_field: {"vector": query_vector, "k": size}}},
            }
        )

    return results['hits']['hits']


def lambda_handler(event, context):
    
    print("event:",event)
    print('host',host)
    
    evt_body = event['queryStringParameters']
    
    query = "hello"
    if "query" in evt_body.keys():
        query = evt_body['query'].strip()
    print('query:',query)
    
    vectorDatabase = 'opensearch'
    if "vectorDatabase" in evt_body.keys():
        vectorDatabase = evt_body['vectorDatabase']
    print('vectorDatabase:',vectorDatabase)
    
    if vectorDatabase == 'opensearch':
        index = INDEX
        if "index" in evt_body.keys():
            index = evt_body['index']
        print('index:',index)
        
        searchType = 'vector'
        if "searchType" in evt_body.keys():
            searchType = evt_body['searchType']
        print('searchType:',searchType)
        
    elif vectorDatabase == 'myscale':
        myscaleHost = ''
        if "myscaleHost" in evt_body.keys():
            myscaleHost = evt_body['myscaleHost']
        print('myscaleHost:',myscaleHost)
        
        myscalePort = ''
        if "myscalePort" in evt_body.keys():
            myscalePort = evt_body['myscalePort']
        print('myscalePort:',myscalePort)
        
        myscaleUsername = ''
        if "myscaleUsername" in evt_body.keys():
            myscaleUsername = evt_body['myscaleUsername']
        print('myscaleUsername:',myscaleUsername)
        
        myscalePassword = ''
        if "myscalePassword" in evt_body.keys():
            myscalePassword = evt_body['myscalePassword']
        print('myscalePassword:',myscalePassword)
    
    embeddingType = 'sagemaker'
    if "embeddingType" in evt_body.keys():
        embeddingType = evt_body['embeddingType']
    
    embeddingEndpoint = EMBEDDING_ENDPOINT_NAME
    if "embeddingEndpoint" in evt_body.keys():
        embeddingEndpoint = evt_body['embeddingEndpoint']
    
    itemFilterId = ''
    if "itemFilterId" in evt_body.keys():
        itemFilterId = evt_body['itemFilterId']
    print('itemFilterId:',itemFilterId)
    
    textSearchNumber = 0
    if "textSearchNumber" in evt_body.keys() and evt_body['textSearchNumber'] is not None:
        textSearchNumber = int(evt_body['textSearchNumber'])
    print('textSearchNumber:', textSearchNumber)
    
    vectorSearchNumber = 0
    if "vectorSearchNumber" in evt_body.keys() and evt_body['vectorSearchNumber'] is not None:
        vectorSearchNumber = int(evt_body['vectorSearchNumber'])
    print('vectorSearchNumber:', vectorSearchNumber)

    vectorScoreThresholds = 0
    if "vectorScoreThresholds" in evt_body.keys() and evt_body['vectorScoreThresholds'] is not None:
        vectorScoreThresholds = float(evt_body['vectorScoreThresholds'])
    print('vectorScoreThresholds:', vectorScoreThresholds)

    textScoreThresholds = 0
    if "textScoreThresholds" in evt_body.keys() and evt_body['textScoreThresholds'] is not None:
        textScoreThresholds = float(evt_body['textScoreThresholds'])
    print('textScoreThresholds:', textScoreThresholds)

    vectorField = "vector_field"
    if "vectorField" in evt_body.keys():
        vectorField = evt_body['vectorField']
    print('vectorField:', vectorField)
    
    modelType = 'bedrock'
    if "modelType" in evt_body.keys():
        modelType = evt_body['modelType']
  
    apiUrl = ''
    if "apiUrl" in evt_body.keys():
        apiUrl = evt_body['apiUrl']
  
    apiKey = ''
    if "apiKey" in evt_body.keys():
        apiKey = evt_body['apiKey']

    secretKey = ''
    if "secretKey" in evt_body.keys():
        secretKey = evt_body['secretKey']

    modelName = 'anthropic.claude-v2'
    if "modelName" in evt_body.keys():
        modelName = evt_body['modelName']

    maxTokens = 512
    if "maxTokens" in evt_body.keys():
        maxTokens = int(evt_body['maxTokens'])
        
    sagemakerEndpoint = LLM_ENDPOINT_NAME
    if "sagemakerEndpoint" in evt_body.keys():
        sagemakerEndpoint = evt_body['sagemakerEndpoint']
        
    textEmbeddingModelId = ""
    if "textEmbeddingModelId" in evt_body.keys():
        textEmbeddingModelId = evt_body['textEmbeddingModelId']
    print("textEmbeddingModelId:",textEmbeddingModelId) 
    
    temperature = 0.01
    if "temperature" in evt_body.keys():
        temperature = float(evt_body['temperature'])
    
    language=LANGUAGE
    if "language" in evt_body.keys():
        language = evt_body['language']
        
    productId = ""
    if "productId" in evt_body.keys():
        productId = evt_body['productId']
    print('productId:', productId)
    
    productName = ""
    if "productName" in evt_body.keys():
        productName = evt_body['productName']
    print('productName:', productName)
    
    rerankerEndpoint = ""
    if "rerankerEndpoint" in evt_body.keys():
        rerankerEndpoint = evt_body['rerankerEndpoint']
        
    keywords = ""
    if "keywords" in evt_body.keys():
        keywords = evt_body['keywords']
    print('keywords:', keywords)
    
    description = ""
    if "description" in evt_body.keys():
        description = evt_body['description']
    print('description:', description)
    
    task = 'search'
    if "task" in evt_body.keys():
        task = evt_body['task']
    print('task:',task)
        
    if task == 'search':
        if vectorDatabase == 'opensearch' and searchType != 'selfQuery':
            products = []
            product_id_set = set()
            if (searchType == 'text' or searchType == 'mix') and len(index) > 0 and len(query) > 0:
                results = text_search(index,query,productName,keywords,description,size=textSearchNumber)
                for result in results:
                    score = result['_score']
                    metadata = result['_source']['metadata']
                    if score is not None and float(score) >= textScoreThresholds:
                        if len(productId) > 0:
                            product_id = metadata[productId]
                            if product_id not in product_id_set:
                                products.append({'score':score,'product_info':metadata})
                                product_id_set.add(product_id)
                        else:
                            products.append({'score':score,'product_info':metadata})
                print('products in text search:',products)               
            if (searchType == 'vector' or searchType == 'mix') and len(index) > 0 and len(query) > 0:
                
                if len(textEmbeddingModelId) > 0:
                    embedding = get_embedding_bedrock(query,textEmbeddingModelId)
                elif len(embeddingEndpoint) > 0:
                    embedding = get_embedding_sagemaker(embeddingEndpoint,query,language=language,is_query=True)
                
                results = vector_search(index,embedding,size=vectorSearchNumber,vector_field=vectorField)
                for result in results:
                    score = result['_score']
                    print('vertor score:',score)
                    metadata = result['_source']['metadata']
                    if score is not None and float(score) >= vectorScoreThresholds:
                        if len(productId) > 0:
                            product_id = metadata[productId]
                            if product_id not in product_id_set:
                                products.append({'score':score,'product_info':metadata})
                                product_id_set.add(product_id)
                        else:
                            products.append({'score':score,'product_info':metadata})
                print('products in vector search:',products)            
            if searchType == 'mix' and len(rerankerEndpoint) > 0:
                pairs = []
                for product in products:
                    product_name = product['product_info'][productName]
                    if len(keywords) > 0:
                        product_name += (',' + product['product_info'][keywords])
                    pair = [query,product_name]
                    pairs.append(pair)
        
                rerank_scores = get_reranker_scores(pairs,rerankerEndpoint)
                rerank_scores = rerank_scores['rerank_scores']
                new_products=[]
                for i in range(len(products)):
                    new_product = products[i].copy()
                    new_product['rerank_score'] = rerank_scores[i]
                    new_products.append(new_product)
                products = sorted(new_products,key=lambda new_products:new_products['rerank_score'],reverse=True)
        
            print('products:',products)
            scores = []
            item_metadatas = []
            for product in products:
                if 'rerank_score' in product.keys():
                    scores.append(product['rerank_score'])
                else:
                    scores.append(product['score'])
                item_metadatas.append(product['product_info'])
                
            
            
        elif searchType == 'selfQuery':
            
            if embeddingType == 'sagemaker':
                embeddings_func = init_embeddings(embeddingEndpoint,region,language= LANGUAGE)
            elif embeddingType == 'bedrock':
                embeddings_func = init_embeddings_bedrock(model_id='amazon.titan-embed-text-v1')
            
            if vectorDatabase == 'opensearch':
                #1.get item info
                sm_client = boto3.client('secretsmanager')
                master_user = sm_client.get_secret_value(SecretId='opensearch-master-user')['SecretString']
                data= json.loads(master_user)
                username = data.get('username')
                password = data.get('password')
                vector_store=init_vector_store(embeddings_func,index,host,port,username,password)
                retriever = get_retriever(vectorDatabase,vector_store,
                                             region,
                                             sagemakerEndpoint,
                                             temperature,
                                             modelType,
                                             apiUrl,
                                             modelName,
                                             apiKey,
                                             secretKey,
                                             maxTokens
                                         )
                docs = retriever.get_relevant_documents(query,k=topK)
                print('docs:',docs)
                item_metadatas = [doc[0].metadata for doc in docs]
                print('item_metadatas:',item_metadatas)
                scores = [doc[1] for doc in docs]
                print('scores:',scores)
                    
            elif vectorDatabase == 'myscale':
                scaleSettings = MyScaleSettings(host=myscaleHost,port=myscalePort,username=myscaleUsername,password=myscalePassword)
                vector_store = MyScale(embeddings_func,config=scaleSettings)
                retriever = get_retriever(vectorDatabase,vector_store,
                                             region,
                                             sagemakerEndpoint,
                                             temperature,
                                             modelType,
                                             apiUrl,
                                             modelName,
                                             apiKey,
                                             secretKey,
                                             maxTokens
                                          )
                docs = retriever.get_relevant_documents(query,k=topK)
                print('docs:',docs)
                item_metadatas = [doc[0].metadata for doc in docs]
                print('item_metadatas:',item_metadatas)
                scores = [doc[1] for doc in docs]
                print('scores:',scores)
    
        item_id_list = []
        for metadata in item_metadatas:
            item_id_list.append(metadata[productId])

        item_info_dict = item_metadatas
        if len(itemFilterId) > 0:
            item_filter_id_list = itemFilterId.split(',')
            if len(list(set(item_id_list)-set(item_filter_id_list))) == 0:
                item_id_list = []
                item_info_dict = {}
                scores = []
            else:
                item_id_list, item_info_dict, scores = zip(*((item_id, item_info, score) for item_id, item_info, score in zip(item_id_list, item_metadatas,scores) if item_id not in item_filter_id_list))

        products = []
        for item,score in zip(item_info_dict,scores):
            if score != 'None':
                products.append({'score':score,'product_info':item})

        response = {
                "statusCode": 200,
                "headers": {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
                },
                "isBase64Encoded": False
            }

        response['body'] = json.dumps(
        {
            'products': products
        })
                                    
    elif task == 'opensearch_index':
        index_list = []
        try:
            #get indices list from opensearch
            client = get_opensearch_client()
    
            result = list(client.indices.get_alias().keys())
            
            for indice in result:
                if not indice.startswith("."):
                    index_list.append(indice)
            #         index_list.append({"name": indice, "s3_prefix": "", "aos_indice": indice})
            print(index_list)
            response = {
                "statusCode": 200,
                "headers": {
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'OPTIONS,GET'
                },
                "isBase64Encoded": False
            }
            
            response['body'] = json.dumps(index_list)
            
        except Exception as e:
            print(e)
            response = {
                'statusCode': 500,
                'body': json.dumps('Internal Server Error')
            }
    elif task == 'sagemaker_endpoint':
        sagemaker = boto3.client('sagemaker')
        endpoints = sagemaker.list_endpoints()
        # 从响应中提取处于"InService"状态的所有端点的名称
        endpoint_names = [
            endpoint['EndpointName'] for endpoint in endpoints['Endpoints']
            if endpoint['EndpointStatus'] == 'InService'
        ]
        response = {
            "statusCode": 200,
            "headers": {
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'OPTIONS,GET'
            },
            "isBase64Encoded": False
        }
        response['body'] = json.dumps(endpoint_names)
        
    else:
        response = {
                'statusCode': 500,
        }
        response['body'] = json.dumps(
            {
                'result':"Paremeters Server Error"
            }
        )
    return response
