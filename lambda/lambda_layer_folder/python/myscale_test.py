import os

os.environ["OPENAI_API_BASE"] = 'https://one-api.myscale.cloud/v1'
os.environ["OPENAI_API_KEY"] = 'sk-STqI5pwWFo2LbbiK13Aa9bF6E4Bc43E7873dE2945285F5Cc'
os.environ["MYSCALE_HOST"] = 'msc-c6c1595b.us-east-1.aws.myscale.com'
os.environ["MYSCALE_PORT"] = '443'
os.environ["MYSCALE_USERNAME"] = 'myscale_default'
os.environ["MYSCALE_PASSWORD"] = 'passwd_FIwWZ2NRguOGE8'



from langchain.schema import Document
from langchain.vectorstores import MyScale
# from python.langchain.embeddings import SentenceTransformerEmbeddings
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.chains.query_constructor.base import AttributeInfo
from langchain.llms import OpenAI
from langchain.chains.query_constructor.schema import VirtualColumnName
from langchain.retrievers.self_query.myscale import MyScaleTranslator
from langchain.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from typing import Dict, List, Optional,Any
from langchain.embeddings import SagemakerEndpointEmbeddings
import json
from langchain.llms import AmazonAPIGateway
from model import *
from query_prompt import HOTEL_EXAMPLES

# def init_embeddings(endpoint_name,region_name,language: str = "chinese"):
    
#     class ContentHandler(EmbeddingsContentHandler):
#         content_type = "application/json"
#         accepts = "application/json"

#         def transform_input(self, inputs: List[str], model_kwargs: Dict) -> bytes:
#             input_str = json.dumps({"inputs": inputs, **model_kwargs})
#             return input_str.encode('utf-8')

#         def transform_output(self, output: bytes) -> List[List[float]]:
#             response_json = json.loads(output.read().decode("utf-8"))
#             return response_json

#     content_handler = ContentHandler()

#     embeddings = SagemakerEndpointEmbeddings(
#         endpoint_name=endpoint_name, 
#         region_name=region_name, 
#         content_handler=content_handler
#     )
#     return embeddings





embedding_endpoint_name = 'huggingface-inference-eb-zh'
region = 'us-west-2'
LANGUAGE = 'chinese'
embeddings = init_embeddings(embedding_endpoint_name,region,language= LANGUAGE)


class MyScaleDebug(MyScale):
    def similarity_search_by_vector(self, embedding, k: int = 4, where_str = None, **kwargs):
        """
        This is for debug purpose, you can deplace this with langchain.vectorstores.MyScale
        """
        q_str = self._build_qstr(embedding, k, where_str)
        # Print our sql
        print(q_str)
        try:
            return [
                Document(
                    page_content=r[self.config.column_map["text"]],
                    metadata=r[self.config.column_map["metadata"]],
                )
                for r in self.client.query(q_str).named_results()
            ]
        except Exception as e:
            print(f"\033[91m\033[1m{type(e)}\033[0m \033[95m{str(e)}\033[0m")
            return []

vectorstore = MyScaleDebug(embeddings)

def map_chinese_metadata(name):
    return VirtualColumnName(name=name, column=f"metadata.`{name}`")

metadata_field_info = [
    AttributeInfo(
        name=map_chinese_metadata("城市"),
        description="酒店所在的城市",
        type="string",
    ),
    AttributeInfo(
        name=map_chinese_metadata("地区"),
        description="酒店所在的城市区域",
        type="string",
    ),
    AttributeInfo(
        name=map_chinese_metadata("酒店名"),
        description="酒店的名称",
        type="string",
    ),
    AttributeInfo(
        name=map_chinese_metadata("星级"),
        description="酒店的星级",
        type="string",
    ),
    AttributeInfo(
        name=map_chinese_metadata("地铁站"),
        description="酒店所在地附近的地铁站",
        type="string",
    ),    
    AttributeInfo(
        name=map_chinese_metadata("最大容纳人数"),
        description="酒店中举办活动的会场可以容纳的最大人数",
        type="float",
    ),    
    AttributeInfo(
        name=map_chinese_metadata("会场全天价格"),
        description="酒店中举办活动的会场的全天价格",
        type="float",
    ),     
    AttributeInfo(
        name=map_chinese_metadata("会场半天价格"),
        description="酒店中举办各类活动的会场的半天价格",
        type="float",
    )
]
document_content_description = "对酒店或举办活动场地的描述"


# llm = OpenAI(temperature=0)

#zhipu
llm = AmazonAPIGateway(api_url='')
model_name='chatglm_turbo'
api_key='64682bb1ba579e2cebf8a4a5522aef59.VtMAJxawMcUamrdH'

parameters={
    "modelId":model_name,
    "api_key":api_key,
}
llm.model_kwargs = parameters

# model_name = 'anthropic.claude-v2'
# llm = init_model_bedrock(model_name)
# parameters={
#     "max_tokens_to_sample":512,
#     "temperature":0.01
# }
# llm.model_kwargs = parameters

chain_kwargs = {}
chain_kwargs["examples"]=HOTEL_EXAMPLES
retriever = SelfQueryRetriever.from_llm(
    llm, vectorstore, document_content_description, metadata_field_info, 
    structured_query_translator=MyScaleTranslator(),
    chain_kwargs=chain_kwargs,
    verbose=True
)

query = '我想找一个广州体育中心举办200人发布会的酒店，2天时间，预算2万'
# query = '我想找1个广州的酒店'
response = retriever.get_relevant_documents(query,k=5)

print('hotel len:',len(response))
for item in response:
    print(item.page_content)