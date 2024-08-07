from pydantic import BaseModel

class PineconeCreds(BaseModel):
    api_key: str
    index_name: str

class QueryModel(BaseModel):
    api_key: str
    index_name: str
    query_sentence: str