from pydantic import BaseModel, Field


class Author(BaseModel):
    first_name: str = Field(
        ..., min_length=1, max_length=100, description="The author's first name"
    )
    last_name: str = Field(
        ..., min_length=1, max_length=100, description="The author's last name"
    )
