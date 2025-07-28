from typing import List
from pydantic import BaseModel, Field

# Model class for an article. This model will be used for saving articles
class Article(BaseModel):
    key: str
    url: str
    title: str
    pub_date: str

# Represent a list of Articles
class ArticleList(BaseModel):
    articles: List[Article]

# Model class for a stock; used in capturing the response from the LLM
class Stock(BaseModel):
    name: str = Field(..., description='Name of the stock')
    symbol: str = Field(..., description='Stock symbol')
    fair_value: float = Field(..., description='Failr value of the stock')
    industry: str = Field(..., description='Industry the stock belongs to')
    uncertainity_rating: str = Field(..., description='Uncertainly rating')
    star_rating: str = Field(..., description='Star rating')
    summary: str = Field(..., description='Summary of the stock')

# List of stocks
class StockList(BaseModel):
    stocks: List[Stock]

    