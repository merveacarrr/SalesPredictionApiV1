import pandas as pd
import matplotlib.pyplot as plt
from src.utils.data_fetch import DataFetch  # DataFetch sınıfını içe aktar
from schemas import MonthlySalesSummary, ProductSalesSummary, SalesSummaryResponse

class SalesSummary:
    """Satış özetlerini oluşturan ana sınıf."""

    @staticmethod
    def generate_sales_summary() -> SalesSummaryResponse:
        """
        Veritabanından veriyi çeker, satış özetlerini oluşturur ve JSON döndürür.
        """
        print("Veriler çekiliyor...")
        data_fetcher = DataFetch()
        df = data_fetcher.fetch_data()

        # Tarih Formatı Dönüştürme
        df["order_date"] = pd.to_datetime(df["order_date"])
        df["year_month"] = df["order_date"].dt.to_period("M")  # Yıl-Ay formatına çevir

        # Aylık Satış Özetini Hesaplama
        print("Aylık satış özeti hesaplanıyor...")
        monthly_sales_summary = df.groupby("year_month")["final_price"].sum().reset_index()
        monthly_sales_summary.to_csv("monthly_sales_summary.csv", index=False)

 # Aylık satışları görselleştir
        monthly_sales_img_path = "visualizations/monthly_sales_summary.png"
        plt.figure(figsize=(10, 6))
        plt.plot(monthly_sales_summary["year_month"].astype(str), monthly_sales_summary["final_price"], marker="o",
                 color="blue")
        plt.title("Aylık Satış Özeti")
        plt.xlabel("Ay")
        plt.ylabel("Toplam Satış")
        plt.xticks(rotation=45)
        plt.grid()
        plt.tight_layout()
        plt.savefig(monthly_sales_img_path)
        plt.close()

        # Ürün Bazlı Satış Özetini Hesaplama
        print("Ürün bazlı satış özeti hesaplanıyor...")
        product_sales_summary = df.groupby("product_id")["final_price"].sum().reset_index()
        product_sales_summary = product_sales_summary.merge(df[["product_id", "category_id", "product_name"]].drop_duplicates(),
                                                            on="product_id")
        product_sales_summary.to_csv("product_sales_summary.csv", index=False)
        # Ürün bazlı satışları görselleştir
        product_sales_img_path = "visualizations/product_sales_summary.png"
        top_products = product_sales_summary.nlargest(10, "final_price")
        plt.figure(figsize=(10, 6))
        plt.barh(top_products["product_name"], top_products["final_price"], color="skyblue")  # Ürün adını kullan
        plt.title("En Çok Satan 10 Ürün")
        plt.xlabel("Toplam Satış")
        plt.ylabel("Ürün Adı")  # Ürün adı gösterilecek
        plt.gca().invert_yaxis()
        plt.grid(axis="x")
        plt.tight_layout()
        plt.savefig(product_sales_img_path)
        plt.close()

        # Satış özeti tamamlandı
        return SalesSummaryResponse(
            monthly_sales_summary=[
                MonthlySalesSummary(year_month=str(row["year_month"]), total_sales=row["final_price"])
                for _, row in monthly_sales_summary.iterrows()
            ],
            product_sales_summary=[
                ProductSalesSummary(
                    product_id=row["product_id"],
                    product_name=row["product_name"],
                    final_price=row["final_price"],
                    category_id=row["category_id"]
                )
                for _, row in product_sales_summary.iterrows()
            ],
            monthly_sales_image=monthly_sales_img_path,  # Görsel yolu
            product_sales_image=product_sales_img_path 
        )