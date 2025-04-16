from pydantic import BaseModel

class ProductResponse(BaseModel):
    id: int
    name: str 
    description: str
    price: float
    quantity: int
    category_id: int
    category_name: str
    image_url: str