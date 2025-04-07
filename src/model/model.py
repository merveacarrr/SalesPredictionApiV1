import pandas as pd
import os
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib

class Modelling:
    def __init__(self, filepath="processed_data.csv"):
        self.filepath = filepath
        self.model_params = {
            "LinearRegression": (LinearRegression(), {}),
            "DecisionTree": (DecisionTreeRegressor(random_state=42), {
                'max_depth': [3, 5, 10, None],
                'min_samples_split': [2, 5, 10]
            }),
            "KNN": (KNeighborsRegressor(), {
                'n_neighbors': [3, 5, 7, 9]
            })
        }

    def load_data(self):
        return pd.read_csv(self.filepath)

    def train_best_model(self, X_train, y_train, model_name):
        base_model, params = self.model_params.get(model_name, (None, None))
        if base_model is None:
            raise ValueError(f"Geçersiz model adı: {model_name}")
        
        if params:
            grid_search = GridSearchCV(base_model, params, cv=3, scoring='r2', n_jobs=-1)
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            print(f"{model_name} için en iyi parametreler: {grid_search.best_params_}")
        else:
            best_model = base_model
            best_model.fit(X_train, y_train)

        return best_model

    def evaluate_model(self, model, X_test, y_test):
        predictions = model.predict(X_test)
        mse = mean_squared_error(y_test, predictions)
        r2 = r2_score(y_test, predictions)
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mape = np.mean(np.abs((y_test - predictions) / y_test)) * 100

        return {
            "MSE": mse,
            "R2": r2,
            "MAE": mae,
            "RMSE": rmse,
            "MAPE": mape
        }

    def save_model(self, model, model_name, filename="src/model/{model_name}.pkl"):
        filename = filename.format(model_name=model_name)
        joblib.dump(model, filename)
        print(f"{model_name} modeli '{filename}' olarak kaydedildi.")

    def save_results(self, results, filename="src/model/model_results.txt"):
        try:
            with open(filename, "w") as f:
                for model_name, metrics in results.items():
                    f.write(f"Model: {model_name}\n")
                    for metric_name, value in metrics.items():
                        f.write(f"  {metric_name}: {value:.4f}\n")
                    f.write("\n")
            print(f"Model karşılaştırma sonuçları '{filename}' olarak kaydedildi.")
        except Exception as e:
            print(f"Sonuçlar kaydedilirken hata oluştu: {str(e)}")

    def retrain_model(self, model_name, df=None):
        if df is None:
            df = self.load_data()

        X = df.drop(columns=["final_price"])
        y = df["final_price"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = self.train_best_model(X_train, y_train, model_name)
        evaluation_results = self.evaluate_model(model, X_test, y_test)
        self.save_model(model, model_name)
        self.generate_visualizations(model, X_test, y_test, model_name)

        return model,evaluation_results

    
    def compare_and_save_best_model(self, df=None):
        if df is None:
            df = self.load_data()

        X = df.drop(columns=["final_price"])
        y = df["final_price"]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        trained_models = {}
        results = {}

        for model_name in self.model_params:
            try:
                print(f"{model_name} en iyi parametrelerle eğitiliyor...")
                model = self.train_best_model(X_train, y_train, model_name)
                evaluation = self.evaluate_model(model, X_test, y_test)
                results[model_name] = evaluation
                trained_models[model_name] = model
                self.save_model(model, model_name)
                self.generate_visualizations(model, X_test, y_test, model_name)
            except Exception as e:
                print(f"{model_name} eğitilirken hata oluştu: {e}")

        if not trained_models:
            raise Exception("Hiçbir model başarıyla eğitilemedi.")

        self.save_results(results)

        best_model_name = max(results, key=lambda x: results[x]["R2"])
        best_model = trained_models[best_model_name]

        try:
            self.save_model(best_model, "best_model")
            self.generate_visualizations(best_model, X_test, y_test, best_model_name)
            print(f"En iyi model: {best_model_name} seçildi ve kaydedildi.")
        except Exception as e:
            print(f"En iyi model kaydedilirken hata oluştu: {e}")

        return best_model, results

    def generate_visualizations(self, model, X_test, y_test, model_name):
        predictions = model.predict(X_test)

        os.makedirs(f"visualizations/{model_name}", exist_ok=True)

        plt.figure(figsize=(8, 6))
        plt.scatter(y_test, predictions, alpha=0.6, color='royalblue')
        plt.xlabel("Gerçek Fiyat")
        plt.ylabel("Tahmin Edilen Fiyat")
        plt.title(f"{model_name} - Gerçek vs Tahmin")
        plt.grid(True)
        plt.savefig(f"visualizations/{model_name}/actual_vs_predicted.png")
        plt.close()

        errors = y_test - predictions
        plt.figure(figsize=(8, 6))
        plt.hist(errors, bins=30, color="tomato", edgecolor="black")
        plt.title(f"{model_name} - Hata Dağılımı")
        plt.xlabel("Hata")
        plt.ylabel("Frekans")
        plt.grid(True)
        plt.savefig(f"visualizations/{model_name}/error_distribution.png")
        plt.close()
