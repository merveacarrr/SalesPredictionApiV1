import os
import joblib
import pandas as pd
from typing import List
from fastapi.requests import Request
from fastapi import FastAPI, HTTPException, Depends,Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from src.development.data_manipulation import DataManipulation
from fastapi.responses import JSONResponse
from src.model.model import Modelling
from src.utils.data_fetch import DataFetch
import src.schemas 
from src.utils.db import get_db
import src.utils.models as models
from fastapi.staticfiles import StaticFiles
from src.development.sales_summary import SalesSummary
from src.schemas import SalesSummaryResponse


app = FastAPI(title="Price Prediction API", description="Price Prediction API using the Best Model")

# CORS Ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Model yolu
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "src/model", "best_model.pkl")
FEATURES_PATH = os.path.join(BASE_DIR, "src/model", "feature_columns.pkl")


@app.get("/")
async def root():
    return {"message": "Price Prediction API is running!"}

@app.post("/predict")
async def post_predict_price(input_data: src.schemas.PredictionInput):
    try:
        # Kullanıcıdan alınan veriyi pandas dataframe'e dönüştür
        applicant_data = pd.DataFrame([input_data.dict()])
        applicant_data = DataManipulation.data_manipulation(applicant_data)

        # Feature columns'ı yükle ve eksik sütunları sıfırla
        feature_columns = joblib.load(FEATURES_PATH)
        for col in feature_columns:
            if col not in applicant_data.columns:
                applicant_data[col] = 0

        applicant_data = applicant_data[feature_columns]
        
        # En iyi model ile tahmin yap
        best_model = joblib.load(MODEL_PATH)
        y_pred = best_model.predict(applicant_data)

        return {"final_price": float(y_pred[0])}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Tahmin hatası: {str(e)}")

@app.post("/retrain")
async def post_retrain_model(
    model_name: str = Query(..., enum=["LinearRegression", "DecisionTree", "KNN"])
):
    try:
        # Model adı doğrulama
        valid_models = ["LinearRegression", "DecisionTree", "KNN"]
        if model_name not in valid_models:
            raise HTTPException(status_code=400, detail="Geçersiz model adı. Geçerli modeller: LinearRegression, DecisionTree, KNN")
        
        # Veriyi al ve işleme yap
        data_fetch_instance = DataFetch()
        df = data_fetch_instance.fetch_data()
        df = DataManipulation.data_manipulation(df)
        df = DataManipulation.feature_engineering(df)

        # Modeli eğit ve sonuçları al
        model_instance = Modelling()
        trained_model, evaluation_results = model_instance.retrain_model(model_name, df)

        # Sonuçları kaydet ve en iyi modeli seç
        X = df.drop(columns=['final_price'])
        joblib.dump(X.columns.tolist(), FEATURES_PATH)
        joblib.dump(trained_model, MODEL_PATH)

        # Sonuçları döndür
        return {"message": f"{model_name} modeli başarıyla yeniden eğitildi!", "metrics": evaluation_results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model eğitme hatası: {str(e)}")
    
@app.get("/sales_summary",response_model=SalesSummaryResponse)
def get_sales_summary(
    summary_type: str = Query("all", enum=["monthly", "product", "all"]),
    request: Request = None
):
    try:
        result = SalesSummary.generate_sales_summary()
        base_url = str(request.base_url).rstrip("/")  # http://localhost:8000

        if summary_type == "monthly":
            return {
                "monthly_sales_summary": result.monthly_sales_summary,
                "monthly_sales_image": f"{base_url}/{result.monthly_sales_image}"
            }

        elif summary_type == "product":
            return {
                "product_sales_summary": result.product_sales_summary,
                "product_sales_image": f"{base_url}/{result.product_sales_image}"
            }

        elif summary_type == "all":
            return {
                "monthly_sales_summary": result.monthly_sales_summary,
                "product_sales_summary": result.product_sales_summary,
                "monthly_sales_image": f"{base_url}/{result.monthly_sales_image}",
                "product_sales_image": f"{base_url}/{result.product_sales_image}",
            }

        else:
            return JSONResponse(status_code=400, content={"detail": "Geçersiz summary_type"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Satış özeti hatası: {str(e)}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": f"Satış özeti hatası: {str(e)}"})
@app.get("/products", response_model=List[src.schemas.Product])
async def get_products(db: Session = Depends(get_db)):
    """Ürün listesini döndürür"""
    try:
        products = db.query(models.Product).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ürünleri getirirken hata oluştu: {str(e)}")
    
@app.get("/visualizations")
async def get_visualizations(model_name: str):
    try:
        folder_path = os.path.join("visualizations", model_name)
        if not os.path.exists(folder_path):
            raise HTTPException(status_code=404, detail="Görseller bulunamadı. Model henüz eğitilmemiş olabilir.")

        files = os.listdir(folder_path)
        image_urls = [f"/visualizations/{model_name}/{file}" for file in files]
        return {"model": model_name, "visualizations": image_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görselleştirme hatası: {str(e)}")

app.mount("/visualizations", StaticFiles(directory="visualizations"), name="visualizations") # Statik görselleri sunmak için 