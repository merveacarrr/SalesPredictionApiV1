from pydantic import BaseModel, Field
from typing import List,Dict

class Product(BaseModel):
    product_id: int
    product_name: str

    class Config:
        orm_mode = True

class PredictionInput(BaseModel):
    customer_id: int = Field(..., description="Müşteri kimlik numarası")
    category_id: int = Field(..., example=1, description="Ürünün ait olduğu kategori ID’si")
    contact_title: str = Field(..., example="Sales Representative", description="Müşteri yetkili unvanı")
    country: str = Field(..., example="USA", description="Müşterinin bulunduğu ülke")
    order_date: str = Field(..., example="2023-01-01", description="Sipariş tarihi (YYYY-MM-DD formatında)")
    product_id: int = Field(..., example=12, description="Ürün ID’si")
    quantity: int = Field(..., example=20, description="Sipariş edilen miktar")
    discount: float = Field(..., example=0.05, description="İndirimin oranı (0 ile 1 arasında)")

    class Config:
        schema_extra = {
            "example": {
                "customer_id":3,
                "category_id": 1,
                "contact_title": "Sales Representative",
                "country": "USA",
                "order_date": "2023-01-01",
                "product_id": 12,
                "unit_price": 18.99,
                "quantity": 20,
                "discount": 0.05
            }
        }
class MonthlySalesSummary(BaseModel):
    """Aylık satış özetini temsil eden model."""
    year_month: str
    total_sales: float

class ProductSalesSummary(BaseModel):
    """Ürün bazlı satış özetini temsil eden model."""
    product_id: int
    product_name: str
    final_price: float
    category_id: int

class SalesSummaryResponse(BaseModel):
    monthly_sales_summary: List[MonthlySalesSummary] = []
    product_sales_summary: List[ProductSalesSummary] = []
    monthly_sales_image: str = ""
    product_sales_image: str = ""