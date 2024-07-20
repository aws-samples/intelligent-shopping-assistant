from langchain.prompts.prompt import PromptTemplate


#chinese
CHINESE_CHAT = """你是一个助手，请根据多个维度，回复用户的问题。

    用户提问: {question}
    用户需求:""" 

CHINESE_SUMMARIZE = """请根据用户的问题，从各个维度总结客户的需求。
    
    用户提问: {question}
    用户需求:"""
    
CHINESE_ADS = """请根据用户的需求，生成商品信息的广告词。
    
    商品信息: {items_info}
    用户需求:{question}"""
    

#chinese_tc
CHINESE_TC_CHAT = """你是一個助手，請根據多個維度，回復用戶的問題。

    用戶提問: {question}
    用戶需求:""" 

CHINESE_TC_SUMMARIZE = """请根据用户的问题，从各个维度总结客户的需求。

    用戶提問: {question}
    用戶需求:"""
    
CHINESE_TC_ADS = """請根據用戶的需求，生成商品信息的廣告詞。
    
    商品信息: {items_info}
    用戶需求:{question}"""


#claude chinese    
CLAUDE_CHINESE_CHAT = '\n\nHuman:'+CHINESE_CHAT+'\n\nAssistant:'
CLAUDE_CHINESE_SUMMARIZE = '\n\nHuman:'+CHINESE_SUMMARIZE+'\n\nAssistant:'
CLAUDE_CHINESE_ADS = '\n\nHuman:'+CHINESE_ADS+'\n\nAssistant:'

#claude chinese tc
CLAUDE_CHINESE_TC_SUMMARIZE = '\n\nHuman:'+CHINESE_TC_SUMMARIZE+'\n\nAssistant:'


CLAUDE_CHINESE_TC_CHAT = """

Human:你是房產中介公司的一個客服工作人員，任務是幫助梳理客戶的租房或買房需求，請判断用戶的問題中是否已包含區域、價格和面積這3個維度的信息，請將判斷結果輸出到<answer></answer>標識後面 如果已包含3個維度的信息，請輸出『是#』，如果不包括，請輸出『否#』，並输回復用戶，讓用戶提供缺失的信息。房子的面積使用尺或呎來計算，立即回答問題，不要前言，一定用使用繁體中文回答。

    用戶提問: {question}
    
Assistant:判断是否包含3个维度信息，用繁體中文回答问题<answer>    
""" 

CLAUDE_CHINESE_TC_ADS = """

Human:你是房產中介公司的一個客服工作人員，任務是從給出的房屋信息中，向用戶推薦符合用戶需求的房子，並給出推薦理由。 立即回答問題，不要前言，一定用使用繁體中文回答。

房屋信息如下：
<apartments>
{items_info}
</apartments>

用戶需求爲：{question}

輸出符合要求的房子信息，房子信息需要包括2部分的內容：
1、輸出符合用戶需求的房子的推薦理由，推薦理由需要結合用戶需求和房子的標簽信息編寫，突出房子的配套完善和交通便利性。
2、輸出符合用戶需求的房子的標簽信息
按照以下例子输出：

<example>
##1、推薦理由
這套沙田第一城1期09座的低層A室,實用面積為451平方呎,配套設施完善,交通便利,距離石門地鐵站僅5分鐘步行路程,非常適合您的需求。
##2、房子标签
編號:=M300553295
區域:=新界沙田第一城 / 石門
樓盤名稱:=沙田第一城  
屋苑:=1期09座
座向:=西北
樓層:=低層
實用面積(呎):=451
房間數:=3
物業設施:=有泳池,兒童設施,運動設施,娛樂設施,餐飲設施,基座商場
校網:=91
租售情况:=可出租,可出售
每月租金:=20000
售價:=7000000
附近地鐵站:=石門站
圖片:=https://wm-cdn.midland.com.hk/img_wm_revamp.php?wm=mr&src=https%3A%2F%2Finternal-res-thumbnail-midland.s3.amazonaws.com%2Fvr_thumbnails%2FM300553295%2Fmatterport%2F1d3a70522a1ace4b813f35fcf05957d4f21928e9.jpg
網頁:=https://www.midland.com.hk/zh-hk/property/%E6%96%B0%E7%95%8C-%E7%AC%AC%E4%B8%80%E5%9F%8E-%E7%9F%B3%E9%96%80-%E6%B2%99%
</example>
     
如果找不到符合要求的房子信息，请输出：“對不起，暫時沒有滿足您需求的房子，請試試找下其他房子吧”

Assistant:   
""" 

#LLAMA2 english
LLAMA2_CHAT_SYSTEM_CONTENT = "You are an assistant for an e-commerce website, and your task is to collect users' shopping needs. Given the conversation between the following customers and the e-commerce website assistant and their subsequent input, ask the user questions based on their current needs. You can ask questions about the brand, functionality, or price of the product.Do not directly recommend products to users,Just ask users for their shopping needs."

LLAMA2_SUMMARIZE_SYSTEM_CONTENT = "You are an assistant for an e-commerce website, after the user puts forward the shopping demand, please simply summariz the user's shopping intention from the product name, material, color, function, price, etc.,do not directly recommend products to users, only simply output information about the user's shopping intention"

LLAMA2_SUMMARIZE_CHAT_TEMPLATE = "user's shopping demand are:{}, what is user's shopping intention? only simply output information about the user's shopping intention"

LLAMA2_ADS_SYSTEM_CONTENT = "If you are a shopping guide of an e-commerce website, please generate product marketing advertising messages within 50 words for the user according to the user's information and shopping history, as well as the basic information of the product."

LLAMA2_ADS_CHAT_TEMPLATE="Based on the user's shopping history,Please create advertising messages for each of the following 3 products, each product advertising message is within 200 words."  


#english
ENGLISH_CHAT = """You are an assistant for an e-commerce website, and your task is to collect users' shopping needs. Given the conversation between the following customers and the e-commerce website assistant and their subsequent input, ask the user questions based on their current needs. You can ask questions about the brand, functionality, or price of the product.Do not directly recommend products to users,Just ask users for their shopping needs.
          
            user's question: {question}
            Answer:""" 

ENGLISH_SUMMARIZE = """According to the user's problem, summarize the customer's needs from various dimensions.
       
            user's question: {question}
            Answer:""" 


ENGLISH_ADS = """Please generate advertising words for product information based on the needs of users.
       
    Product information: {items_info}
    User needs:{question}"""
    
    
#claude english
CLAUDE_ENGLISH_CHAT = '\n\nHuman:'+ENGLISH_CHAT+'\n\nAssistant:'
CLAUDE_ENGLISH_SUMMARIZE = '\n\nHuman:'+ENGLISH_SUMMARIZE+'\n\nAssistant:'
CLAUDE_ENGLISH_ADS = '\n\nHuman:'+ENGLISH_ADS+'\n\nAssistant:'
            


def get_prompt_template(language,modelType,task):
    prompt_template = CHINESE_CHAT
    if language == "chinese":
        if modelType == 'mornal':
            if task == 'chat':
                prompt_template = CHINESE_CHAT
            elif task == 'summarize':
                prompt_template = CHINESE_SUMMARIZE
            elif task == 'ads':
                prompt_template = CHINESE_ADS
        elif modelType.find('bedrock') >=0:
            if task == 'chat':
                prompt_template = CLAUDE_CHINESE_CHAT
            elif task == 'summarize':
                prompt_template = CLAUDE_CHINESE_SUMMARIZE
            elif task == 'ads':
                prompt_template = CLAUDE_CHINESE_ADS
    elif language == "chinese-tc":
        if modelType == 'mornal':
            if task == 'chat':
                prompt_template = CHINESE_TC_CHAT
            elif task == 'summarize':
                prompt_template = CHINESE_TC_SUMMARIZE
            elif task == 'ads':
                prompt_template = CHINESE_TC_ADS
        elif modelType.find('bedrock') >=0:
            if task == 'chat':
                prompt_template = CLAUDE_CHINESE_TC_CHAT
            elif task == 'summarize':
                prompt_template = CLAUDE_CHINESE_TC_SUMMARIZE
            elif task == 'ads':
                prompt_template = CLAUDE_CHINESE_TC_ADS
        
    elif language == "english":
        # prompt_template = ENGLISH_CHAT_PROMPT_TEMPLATE
        if modelType == 'llama2':
            if task == 'chat':
                prompt_template = LLAMA2_CHAT_SYSTEM_CONTENT
            elif task == 'summarize-sys':
                prompt_template = LLAMA2_SUMMARIZE_SYSTEM_CONTENT
            elif task == 'summarize-chat':
                prompt_template = LLAMA2_SUMMARIZE_CHAT_TEMPLATE
            elif task == 'ads-sys':
                prompt_template = LLAMA2_ADS_SYSTEM_CONTENT
            elif task == 'ads-chat':
                prompt_template = LLAMA2_ADS_CHAT_TEMPLATE                
                
        elif modelType == 'mornal':
            if task == 'chat':
                prompt_template = ENGLISH_CHAT
            elif task == 'summarize':
                prompt_template = ENGLISH_SUMMARIZE
            elif task == 'ads':
                prompt_template = ENGLISH_ADS
                
        elif modelType.find('bedrock') >=0:
            if task == 'chat':
                prompt_template = CLAUDE_ENGLISH_CHAT
            elif task == 'summarize':
                prompt_template = CLAUDE_ENGLISH_SUMMARIZE
            elif task == 'ads':
                prompt_template = CLAUDE_ENGLISH_ADS
    return prompt_template