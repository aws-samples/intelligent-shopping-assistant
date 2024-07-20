HOTEL_DATA_SOURCE = """\
```json
{{
    "content": "对酒店或举办活动场地的描述",
    "attributes": {{
        "城市": {{
            "type": "string",
            "description": "酒店所在的城市"
        }},
        "地区": {{
            "type": "string",
            "description": "酒店所在的城市区域"
        }},        
        "酒店名": {{
            "type": "string",
            "description": "酒店的名称"
        }},
        "星级": {{
            "type": "string",
            "description": "酒店的星级"
        }},
        "地铁站": {{
            "type": "string",
            "description": "酒店所在地附近的地铁站"
        }},
        "最大容纳人数": {{
            "type": "integer",
            "description": "酒店中举办活动的会场可以容纳的最大人数"
        }},
        "会场全天价格": {{
            "type": "integer",
            "description": "酒店中举办活动的会场的全天价格"
        }},
        "会场半天价格": {{
            "type": "string",
            "description": "酒店中举办各类活动的会场的半天价格"
        }}
    }}
}}
```\
"""

FULL_ANSWER = """\
```json
{{
    "query": "培训",
    "filter": "and(eq(\\"城市\",\\"广州\\"),eq(\\"地区\\",\\"琶洲\\"),gte(\\"最大容纳人数\\",100),lte(\"会场全天价格\",10000))" 
}}
```\
"""

FULL_ANSWER2 = """\
```json
{{
    "query": "讲座",
    "filter": "and(eq(\\"城市\",\\"广州\\"),eq(\\"地区\\",\\"东山口\\"),gte(\\"最大容纳人数\\",200),lte(\"会场全天价格\",5000))" 
}}
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

HOTEL_EXAMPLES = [
    {
        "i": 1,
        "data_source": HOTEL_DATA_SOURCE,
        "user_query": "广州琶洲有哪个酒店可以举办100人培训？预算1万",
        "structured_request": FULL_ANSWER,
    },
    {
        "i": 2,
        "data_source": HOTEL_DATA_SOURCE,
        "user_query": "广州东山口举办200人讲座？2天时间，预算1万",
        "structured_request": FULL_ANSWER2,
    },
    {
        "i": 3,
        "data_source": HOTEL_DATA_SOURCE,
        "user_query": "那个酒店有100个房间？",
        "structured_request": NO_FILTER_ANSWER,
    },
]
