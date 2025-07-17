from typing import List
from pydantic import BaseModel, Field

class Stock(BaseModel):
    name: str = Field(..., description='Name of the stock')
    symbol: str = Field(..., description='Stock symbol')
    fair_value: float = Field(..., description='Fair value of the stock')
    price_fair_ratio: float = Field(..., description='Price/Fair value')
    capitalizaton: str = Field(..., description='Market Capitalization')
    uncertainity_rating: str = Field(..., description='Uncertainly rating')
    economic_moat: str = Field(..., description='Economic moat')
    summary: str = Field(..., description='Summary of the stock')
    exchange: str = Field(..., description='Stock exchange')

class StockList(BaseModel):
    title: str = Field(..., description='Title of the article')
    as_of_date: str = Field(..., description='As of date')
    companies: List[Stock]