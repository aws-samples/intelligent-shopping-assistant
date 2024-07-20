import os
import shutil
from langchain.prompts.prompt import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.llms import AmazonAPIGateway
import json

import boto3
import json
import os

from model import *
from session import *

def get_history(session_id,table_name,context_rounds):
    history = []
    session_info = ""
    if len(session_id) > 0 and len(table_name) > 0 and context_rounds > 0:
        session_info = get_session_info(table_name,session_id)
        if len(session_info) > 0:
            session_info = session_info[-context_rounds:]
            if len(session_info) > 0:
                for item in session_info:
                    print("session info:",item[0]," ; ",item[1]," ; ",item[2])
                    if item[2] == "chat":
                        history.append((string_processor(item[0]),string_processor(item[1])))
    return history


class ShoppingGuideChatBot:
    
    def init_cfg(self,
                 region,
                 llm_endpoint_name: str = 'pytorch-inference-llm-v1',
                 temperature: float = 0.01,
                 model_type:str = "normal",
                 api_url:str = "",
                 model_name:str="anthropic.claude-v2",
                 api_key:str = "",
                 secret_key:str = "",
                 max_tokens:int=512,
                ):
                    
        if model_type == "llama2":
            self.llm = init_model_llama2(llm_endpoint_name,region,temperature)
        elif model_type == "bedrock_api":
            self.llm = AmazonAPIGateway(api_url=bedrock_api_url)
            parameters={
                "modelId":bedrock_model_id,
                "max_tokens":bedrock_max_tokens,
                "temperature":temperature
            }
            self.llm.model_kwargs = parameters
        elif model_type == "bedrock":
            self.llm = init_model_bedrock(model_name)
            parameters={
                "temperature":temperature,
                "max_tokens":max_tokens
            }
            self.llm.model_kwargs = parameters
        elif model_type == 'llm_api':
            if model_name.find('Baichuan2') >= 0:
                self.llm = AmazonAPIGateway(api_url=api_url)
                parameters={
                    "modelId":model_name,
                    "api_key":api_key,
                    "secret_key":secret_key,
                }
                self.llm.model_kwargs = parameters
            elif model_name.find('chatglm') >= 0:
                self.llm = AmazonAPIGateway(api_url='')
                parameters={
                    "modelId":model_name,
                    "api_key":api_key,
                }
                self.llm.model_kwargs = parameters
        else:
            self.llm = init_model(llm_endpoint_name,region,temperature)
    
    def get_llm(self):
        return self.llm
            
    def get_chat(self,query,
                      prompt_template: str='',
                      session_id: str='',
                      table_name: str='',
                      context_rounds: int=3,
                ):
                    
    
        prompt = PromptTemplate(
            input_variables=["question"], 
            template=prompt_template
        )
        history = get_history(session_id,table_name,context_rounds)
        his_query = ''
        if len(history) > 0:
            for (question,answer) in history:
                if question != query:
                    his_query += (question+',') 
        print('history query:',his_query)
        query = string_processor(query)
        if len(his_query) > 0:
            query = his_query + query  

        print('combine query:',query)
        
        chat_chain = LLMChain(
            llm=self.llm,
            prompt=prompt, 
            # verbose=True, 
            # memory=memory,
        )
            
        output = chat_chain.predict(question=query)
        
        if len(session_id) > 0 and len(query) > 0:
            chat_result = output
            if output.find('@') > 0:
                chat_result = output.split('@')[1].replace('</answer>','').strip()
            update_session_info(table_name, session_id, query, chat_result, "chat")
        
        return output


    def get_item_ads(self,query,
                          prompt_template: str='',
                          items_info: str=''
                    ):
                    
        prompt = PromptTemplate(
            input_variables=["items_info","question"], 
            template=prompt_template
        )
        print('prompt:',prompt)
 
        print('query:',query)
        
        chat_chain = LLMChain(
            llm=self.llm,
            prompt=prompt, 
            # verbose=True, 
            # memory=memory,
        )
            
        output = chat_chain.predict(question=query,items_info=items_info)
        
        return output


    def get_chat_llama2(self,query,
                        task: str='chat',
                        sys_prompt_template: str='',
                        chat_prompt_template: str='',
                        session_id: str='',
                        table_name: str=''
                       ):
    
        history = get_history(session_id,table_name)
        
        if task == 'chat':
            query = string_processor(query)
        else:
            his_query = ''
            if len(history) > 0:
                for (question,answer) in history:
                    his_query += (question+',')
            query = his_query + string_processor(query)
            
            print('chat_prompt_template 1:',chat_prompt_template)
            print('query 0:',query)
            query = chat_prompt_template.format(query)
            print('query 1:',query)
            history = []
            
        prompt={
            'system_content':string_processor(sys_prompt_template),
            'query':string_processor(query),
            'history':history
        }
    
        prompt_str = json.dumps(prompt)
        response = self.llm.predict(prompt_str)
        
        if len(session_id) > 0 and task == 'chat':
            update_session_info(table_name, session_id, query, response, "chat")
        
        return response
        
    def get_item_ads_llama2(self,
                           query,
                           items_info,
                           user_base_info,
                           history_item_info,
                           system_content
                          ):
        system_content += (user_base_info + history_item_info)
        query += items_info
        prompt={
            'system_content':string_processor(system_content),
            'query':string_processor(query)
        }
        prompt_str = json.dumps(prompt)
        response = self.llm.predict(prompt_str)
        return response