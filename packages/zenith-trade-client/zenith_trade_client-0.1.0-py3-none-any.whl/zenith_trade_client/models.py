from pydantic import BaseModel

class DataRequest(BaseModel):
    exchange: str
    symbol: str
    data_type: str
    from_date: str
    to_date: str
    
class ExchangeInfoRequest(BaseModel):
    exchange: str
    datasource: str = None
