from pydantic import BaseModel, Field


class ArticleSchema(BaseModel):
    title: str
    content: str
    author: str
    date: str
    important_quotes: list[str] = Field(description="Important quotes from the article. Format in all caps.")