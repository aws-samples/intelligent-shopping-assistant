import boto3
import json
from typing import Dict,Any
from tools.tools_func import ToolsList

bedrock_client = boto3.client(service_name='bedrock-runtime')

def invoke_model(query:str,system_prompt:str, model_id:str):
    
    messages = []
    input_msg = {"role": "user", "content": [{"text": query}]}
    messages.append(input_msg)
    
    temperature = 0.5
    top_k = 200
    
    system_prompts = [{"text": system_prompt}]
    inference_config = {"temperature": temperature}
    additional_model_fields = {"top_k": top_k}

    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields
    )
    return response["output"]["message"]['content'][0]['text']
        

def generate_response_with_tools(messages,model_id):
    system_prompt = "You are an AI assistant. You have access to tools, but only use them when necessary. If a tool is not required, respond as normal."
    temperature = 0.5
    top_k = 200
    tool_config = {
        "tools": [],
        "toolChoice": {
            "auto": {},
        },
    }
    with open("./tools/tools_definition.json", "r") as file:
        tool_config["tools"] = json.load(file)
    
    system_prompts = [{"text": system_prompt}]
    inference_config = {"temperature": temperature}
    additional_model_fields = {"top_k": top_k}

    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=additional_model_fields,
        toolConfig=tool_config,
    )
    return response["output"]["message"], response["stopReason"]
    
    
def get_tool_use_args(response_msg):
    # sometimes response_msg["content"] include text
    return [c["toolUse"] for c in response_msg["content"] if "toolUse" in c]



def run_tool(tool_name, tool_args):
    return getattr(ToolsList(), tool_name)(**tool_args)


def execute_tool(tool_use_args):
    tool_name = tool_use_args["name"]
    tool_args = tool_use_args["input"] or {}
    print(f"Running ({tool_name}) tool...")
    tool_response = run_tool(tool_name, tool_args)
    return tool_response