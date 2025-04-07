import pandas as pd
from sqlalchemy import create_engine
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from development.data_manipulation import DataManipulation

class DataFetch:
    def __init__(self):
        self.engine = create_engine("postgresql://postgres:meri3516@localhost:5432/postgres")
    
    def fetch_data(self):
        df_orders = pd.read_sql("SELECT * FROM orders", self.engine)
        df_order_details = pd.read_sql("SELECT * FROM order_details", self.engine)
        df_customers = pd.read_sql("SELECT * FROM customers", self.engine)
        df_products = pd.read_sql("SELECT * FROM products", self.engine)
        df_categories = pd.read_sql("SELECT * FROM categories", self.engine)

        # Merge data
        df_order_details['final_price'] = df_order_details['unit_price'] * df_order_details['quantity'] * (1 - df_order_details['discount'])
        df_merged = pd.merge(df_order_details, df_orders, on='order_id', how='inner')
        df_merged = pd.merge(df_merged, df_customers, on='customer_id', how='inner')
        df_merged = pd.merge(df_merged, df_products, on='product_id', how='inner')
        df_merged = pd.merge(df_merged, df_categories, on='category_id', how='inner')

        # Select columns
        df_merged = df_merged[["category_id", "contact_title", "country", "order_date", "product_id","product_name", "unit_price_x", "quantity", "discount", "final_price"]]
        return df_merged


    def fetch_products(self):
        df_products = pd.read_sql("SELECT * FROM products", self.engine)
        return df_products