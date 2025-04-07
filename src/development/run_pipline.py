import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.utils.data_fetch import DataFetch
from development.data_manipulation import DataManipulation

def main():
    # Veriyi çek
    fetcher = DataFetch()
    df = fetcher.fetch_data()

    # EDA (opsiyonel)
    DataManipulation.data_eda(df)

    # Veriyi işle
    processed_df = DataManipulation.data_manipulation(df)

    # İşlenmiş veriyi kaydet
    processed_df.to_csv("processed_data.csv", index=False)
    print("Veri işlendi ve 'processed_data.csv' olarak kaydedildi.")

if __name__ == "__main__":
    main()
