import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class DataManipulation:
    def __init__(self):
        pass

    @staticmethod
    def data_eda(df):
        """Veri seti hakkında genel bilgileri ekrana yazdırır."""
        print("##################### Genel Bilgiler #######################")
        print(df.info())
        print("\n##################### Eksik Değerler ######################")
        print(df.isnull().sum())
        print("\n##################### İstatistikler ######################")
        print(df.describe())

    @staticmethod    
    def data_manipulation(df):
        df = df.copy()

        # Tarih işlemleri
        if "order_date" in df.columns:
            df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
            df['order_days'] = (df['order_date'] - df['order_date'].min()).dt.days

        if "purchase_date" in df.columns:
            df['purchase_date'] = pd.to_datetime(df['purchase_date'], errors='coerce')
            df['purchase_days'] = (df['purchase_date'] - df['purchase_date'].min()).dt.days

        df = DataManipulation.feature_engineering(df)

        # Eksik değerleri temizle
        df = DataManipulation.handle_missing_values(df)

        # Aykırı değerleri düzelt
        outlier_cols = [col for col in ["final_price", "quantity", "unit_price_x"] if col in df.columns]
        df = DataManipulation.remove_outliers(df, columns=outlier_cols, method="replace")

        # Kullanılmayan sütunları sil
        df.drop(columns=["order_date", "purchase_date"], errors="ignore", inplace=True)

        return df

    @staticmethod
    def feature_engineering(df):
        df = df.copy()

        df = DataManipulation.encode_object_features(df)
        df = DataManipulation.add_new_features(df)

        # Hedef değişken adı burada da açıkça verilmeli
        df = DataManipulation.scale_features(df, target_column="final_price")

        print("##################### Özellik Mühendisliği Tamamlandı #######################")
        return df

    @staticmethod
    def encode_object_features(df):
        """Kategorik değişkenleri one-hot encoding ile dönüştürür."""
        df = df.copy()
        categorical_cols = df.select_dtypes(include=['object']).columns
        if categorical_cols.any():
            df = pd.get_dummies(df, columns=categorical_cols, drop_first=False)  # drop_first=False ile bilgi kaybını önledik
        return df

    @staticmethod
    def add_new_features(df):
        """Yeni özellikler ekler."""
        df = df.copy()

        if {"unit_price_x", "quantity"}.issubset(df.columns):
            df["total_cost"] = df["unit_price_x"] * df["quantity"]

        return df

    @staticmethod
    def handle_missing_values(df):
        """Eksik değerleri yönetir (ortalama veya medyan ile doldurma)."""
        df = df.copy()
        for col in df.columns:
            if df[col].isnull().sum() > 0:
                if df[col].dtype in ['float64', 'int64']:
                    df[col].fillna(df[col].median(), inplace=True)  # Sayısal değerler için medyan ile doldurma
                else:
                    df[col].fillna(df[col].mode()[0], inplace=True)  # Kategorik değerler için en sık görülen değeri kullan
        return df

    @staticmethod
    def scale_features(df, target_column="final_price"):
        """Özellikleri ölçeklendirir, ancak hedef değişkeni dışarıda bırakır."""
        df = df.copy()
        numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns

        # Hedef değişkeni dışarda bırak
        numerical_cols = [col for col in numerical_cols if col != target_column]

        scaler = StandardScaler()
        df[numerical_cols] = scaler.fit_transform(df[numerical_cols])

        return df

    @staticmethod
    def remove_outliers(df, columns, method="replace"):
        """Aykırı değerleri temizler veya düzeltir."""
        df = df.copy()
        for col in columns:
            if col not in df.columns:
                print(f"Uyarı: {col} sütunu veri çerçevesinde yok, aykırı değer temizleme atlandı.")
                continue

            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            if method == "drop":
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
            elif method == "replace":
                df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
                df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])

        return df


