SHOE_DATA_SOURCE = """\
```json
{{
    "content": "对酒店或举办活动场地的描述",
    "attributes": {{
        "性别": {{
            "type": "string",
            "description": "适合穿该运动鞋的人的性别"
        }},
        "颜色": {{
            "type": "string",
            "description": "运动鞋的颜色"
        }},        
        "价格": {{
            "type": "string",
            "description": "运动鞋的价格"
        }},
        "适用路面": {{
            "type": "string",
            "description": "适合使用运动鞋的路面"
        }},
        "鞋帮高度": {{
            "type": "string",
            "description": "运动鞋的鞋帮高度"
        }}
    }}
}}
```\
"""

FULL_ANSWER = """\
```json
{{
    "query": "越野鞋",
    "filter": "and(eq(\\"性别\",\\"男子\\"),eq(\\"颜色\",\\"黑色\\"),like(\\"适用路面\",\\"越野\\"),eq(\\"鞋帮高度\",\\"低帮\\"),lte(\"价格\",1000))" 
}}
}}
```\
"""

FULL_ANSWER2 = """\
```json
{{
    "query": "公路鞋",
    "filter": "and(eq(\\"性别\",\\"女子\\"),eq(\\"颜色\",\\"白色\\"),like(\\"适用路面\",\\"公路\\"),eq(\\"鞋帮高度\",\\"高帮\\"),lte(\"价格\",500))" 
}}
```\
"""

OPENSEARCH_FULL_ANSWER = """\
```json
{{
    "query": "越野鞋",
    "filter": "and(eq(\\"性别\",\\"男子\\"),eq(\\"颜色\",\\"黑色\\"),eq(\\"适用路面\",\\"越野\\"),eq(\\"鞋帮高度\",\\"低帮\\"),lte(\"价格\",1000))" 
}}
```\
"""

OPENSEARCH_FULL_ANSWER2 = """\
```json
{{
    "query": "公路鞋",
    "filter": "and(eq(\\"性别\",\\"女子\\"),eq(\\"颜色\",\\"白色\\"),eq(\\"适用路面\",\\"公路\\"),eq(\\"鞋帮高度\",\\"高帮\\"),lte(\"价格\",500))" 
```\
"""

NO_FILTER_ANSWER = """\
```json
{{
    "query": "",
    "filter": "NO_FILTER"
}}
```\
"""

SHOE_EXAMPLES = [
    {
        "i": 1,
        "data_source": SHOE_DATA_SOURCE,
        "user_query": "我想买双黑色的男款低帮越野鞋？预算1000",
        "structured_request": FULL_ANSWER,
    },
    {
        "i": 2,
        "data_source": SHOE_DATA_SOURCE,
        "user_query": "有白色的女款高帮跑步鞋？预算500",
        "structured_request": FULL_ANSWER2,
    },
    {
        "i": 3,
        "data_source": SHOE_DATA_SOURCE,
        "user_query": "那个鞋可以防水",
        "structured_request": NO_FILTER_ANSWER,
    },
]

OPENSEARCH_SHOE_EXAMPLES = [
    {
        "i": 1,
        "data_source": SHOE_DATA_SOURCE,
        "user_query": "我想买双黑色的男款低帮越野鞋？预算1000",
        "structured_request": FULL_ANSWER,
    },
    {
        "i": 2,
        "data_source": SHOE_DATA_SOURCE,
        "user_query": "有白色的女款高帮跑步鞋？预算500",
        "structured_request": FULL_ANSWER2,
    },
    {
        "i": 3,
        "data_source": SHOE_DATA_SOURCE,
        "user_query": "那个鞋可以防水？",
        "structured_request": NO_FILTER_ANSWER,
    },
]

def get_examples(database):
    if database == 'opensearch':
        return OPENSEARCH_SHOE_EXAMPLES
    else:
        return SHOE_EXAMPLES