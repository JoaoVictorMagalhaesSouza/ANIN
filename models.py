import tensorflow as tf
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.metrics import r2_score
import plotly.express as px
import pandas as pd
import numpy as np
from keras.models import load_model
from catboost import CatBoostRegressor

import dash
import dash_core_components as dcc
import dash_html_components as html

class MLP():
    def __init__(self, X_train, x_test, y_train, y_test):
        self.X_train = X_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        #self.model = load_model('model.h5')
        self.model = tf.keras.Sequential([
        tf.keras.layers.Dense(self.X_train.shape[1]),
        tf.keras.layers.Dense(4,activation='relu'),
        tf.keras.layers.Dense(1)
        ])
        optimizer = tf.keras.optimizers.RMSprop(0.001)
        self.model.compile(optimizer=optimizer, loss="mse", metrics=['mae',"mse"])
    
    def fit(self):
        self.model.fit(self.X_train, self.y_train, epochs=200)
    
    def predict(self):
        self.y_pred = self.model.predict(self.x_test).flatten()
        return self.y_pred
    
    def evaluate(self):
        aux = self.y_test.astype('float32').to_numpy()
        self.mse = mean_squared_error(aux, self.y_pred)
        self.mae = mean_absolute_error(aux, self.y_pred)
        self.r2 = r2_score(aux, self.y_pred)
        print(f"MSE: {self.mse}")
        print(f"MAE: {self.mae}")
        print(f'R2: {self.r2}')
    
    def plotCurve(self):
        app = dash.Dash(__name__)
        df_plot = pd.DataFrame()
        aux = list(self.y_test)
        df_plot['valor'] = self.y_test
        df_plot['predicoes'] = self.y_pred
        fig = px.line(df_plot)
        fig.show()
    
    def saveModel(self):
        self.model.save('model.h5')
        self.model.save_weights('model_weights.h5')
        

class LSTM():
    def __init__(self, X_train, x_test, y_train, y_test):
        self.X_train = np.reshape(X_train, (X_train.shape[0], 1, X_train.shape[1]))
        self.x_test = np.reshape(x_test, (x_test.shape[0], 1, x_test.shape[1]))
        self.y_train = y_train
        self.y_test = y_test
        self.model = tf.keras.Sequential([
        tf.keras.layers.LSTM(4),
        tf.keras.layers.Dense(1)
        ])
        optimizer = tf.keras.optimizers.RMSprop(0.001)
        self.model.compile(optimizer=optimizer, loss="mse", metrics=['mae',"mse"])
    
    def fit(self):
        self.model.fit(self.X_train, self.y_train, epochs=200)
    
    def predict(self):
        self.y_pred = self.model.predict(self.x_test).flatten()
        return self.y_pred
    
    def evaluate(self):
        aux = self.y_test.astype('float32').to_numpy()
        self.mse = mean_squared_error(aux, self.y_pred)
        self.mae = mean_absolute_error(aux, self.y_pred)
        self.r2 = r2_score(aux, self.y_pred)
        print(f"MSE: {self.mse}")
        print(f"MAE: {self.mae}")
        print(f'R2: {self.r2}')
    
    def plotCurve(self):
    
        df_plot = pd.DataFrame()
        df_plot['valor'] = self.y_test
        df_plot['predicoes'] = self.y_pred
        fig = px.line(df_plot)
        fig.show()

class CatBoost():
    def __init__(self, X_train, x_test, y_train, y_test):
        self.X_train = X_train
        self.x_test = x_test
        self.y_train = y_train
        self.y_test = y_test
        self.model = CatBoostRegressor(iterations=200, learning_rate=0.1, depth=2, loss_function='RMSE')

    def fit(self):
        self.model.fit(self.X_train, self.y_train)
    
    def predict(self):
        self.y_pred = self.model.predict(self.x_test)
        return self.y_pred
    
    def evaluate(self):
        aux = self.y_test.astype('float32').to_numpy()
        self.mse = mean_squared_error(aux, self.y_pred)
        self.mae = mean_absolute_error(aux, self.y_pred)
        self.r2 = r2_score(aux, self.y_pred)
        print(f"MSE: {self.mse}")
        print(f"MAE: {self.mae}")
        print(f'R2: {self.r2}')
    
    def plotCurve(self):
        app = dash.Dash(__name__)
        df_plot = pd.DataFrame()
        aux = list(self.y_test)
        valores = aux.append(list(self.y_pred))
        df_plot['valor'] = self.y_test
        df_plot['predicoes'] = self.y_pred
        fig = px.line(df_plot)
        fig.show()

class MLP_real_time():
    def __init__(self, X_train, x_test, y_train):
        self.X_train = X_train
        self.x_test = x_test
        self.y_train = y_train
        #self.model = load_model('model.h5')
        self.model = tf.keras.Sequential([
        tf.keras.layers.Dense(self.X_train.shape[1]),
        tf.keras.layers.Dense(4,activation='relu'),
        tf.keras.layers.Dense(1)
        ])
        optimizer = tf.keras.optimizers.RMSprop(0.001)
        self.model.compile(optimizer=optimizer, loss="mse", metrics=['mae',"mse"])
    
    def fit(self):
        self.model.fit(self.X_train, self.y_train, epochs=200)
    
    def predict(self):
        self.y_pred = self.model.predict(self.x_test).flatten()
        return self.y_pred
    