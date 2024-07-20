from langchain.chains.query_constructor.schema import VirtualColumnName
from langchain.chains.query_constructor.base import AttributeInfo

def map_chinese_metadata(name,database='opensearch'):
    if database == 'myscale':
        return VirtualColumnName(name=name, column=f"metadata.`{name}`")
    else:
        return name

def get_metadata_field_info(database):
    metadata_field_info = [
        AttributeInfo(
            name=map_chinese_metadata("性别",database),
            description="适合穿该运动鞋的人的性别",
            type="string",
        ),
        AttributeInfo(
            name=map_chinese_metadata("颜色",database),
            description="运动鞋的颜色",
            type="string",
        ),
        AttributeInfo(
            name=map_chinese_metadata("价格",database),
            description="运动鞋的价格",
            type="string",
        ),
        AttributeInfo(
            name=map_chinese_metadata("适用路面",database),
            description="适合使用运动鞋的路面",
            type="string",
        ),
        AttributeInfo(
            name=map_chinese_metadata("鞋帮高度",database),
            description="运动鞋的鞋帮高度",
            type="string",
        )
    ]
    return metadata_field_info
    
def get_document_content_description():
    document_content_description = "对运动鞋的描述"
    return document_content_description