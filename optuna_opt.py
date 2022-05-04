#%%Imports
import pandas as pd
import os
import feature_engineering as fe
from data_prep import *
from models import *
import os.path
import json
import pickle
import pandas_datareader as web
from database import *
from datetime import datetime, timedelta
#Train test split
from sklearn.model_selection import train_test_split
import optuna
from xgboost import XGBRegressor as xgb
#Mape
from sklearn.metrics import mean_absolute_error
import random
#%%
acoesDisponiveis = ["ABEV3.SA" , "B3SA3.SA" , "BBAS3.SA",  "BBDC3.SA"  ,"BBDC4.SA" , "BBSE3.SA", 
                      "BEEF3.SA"  ,"BRAP4.SA"  ,"BRFS3.SA" , "BRKM5.SA"  ,"BRML3.SA"  , "CCRO3.SA" ,
                      "CIEL3.SA"  ,"CMIG4.SA"  ,"COGN3.SA" , "CPFE3.SA" , "CPLE6.SA",  "CSAN3.SA",  "CSNA3.SA", 
                      "CVCB3.SA"  ,"CYRE3.SA"  ,"ECOR3.SA"  ,"EGIE3.SA" , "ELET3.SA",  "ELET6.SA",  "EMBR3.SA", 
                      "ENBR3.SA"  ,"ENEV3.SA"  ,"ENGI11.SA" ,"EQTL3.SA" , "EZTC3.SA",  "FLRY3.SA",  "GGBR4.SA", 
                      "GOAU4.SA"  ,"GOLL4.SA"  ,"HYPE3.SA" ,  "ITSA4.SA",  "ITUB4.SA", 
                      "JBSS3.SA"  ,"JHSF3.SA"  ,"KLBN11.SA" ,"LCAM3.SA",  "LREN3.SA",  "MGLU3.SA", 
                      "MRFG3.SA"  ,"MRVE3.SA"  ,"MULT3.SA"  ,"PCAR3.SA"  ,"PETR3.SA",  "PETR4.SA",  "PRIO3.SA", 
                      "QUAL3.SA"  ,"RADL3.SA"  ,"RAIL3.SA"  ,"RENT3.SA"  ,"SANB11.SA", "SBSP3.SA",  "SULA11.SA",
                      "SUZB3.SA"  ,"TAEE11.SA" ,"TIMS3.SA"  ,"TOTS3.SA"  ,"UGPA3.SA",  "USIM5.SA",  "VALE3.SA" ,
                      "VIVT3.SA"  ,"WEGE3.SA"  ,"YDUQ3.SA" ]

#%%
def objective(trial):
    param = {
        #Define params for XGBoost
        'max_depth': trial.suggest_int('max_depth', 1, 10),
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000),
        'eval_metric': trial.suggest_categorical('eval_metric', ['mae', 'rmse']),
        'learning_rate': trial.suggest_loguniform('learning_rate', 1e-5, 1e-1),
        'gamma': trial.suggest_loguniform('gamma', 1e-8, 1e-2),
        'reg_lambda': trial.suggest_loguniform('reg_lambda', 1e-8, 1e-2),
        'reg_alpha': trial.suggest_loguniform('reg_alpha', 1e-8, 1e-2),
        'subsample': trial.suggest_uniform('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_uniform('colsample_bytree', 0.5, 1.0),
    }
    regressor = xgb(**param)
    regressor.fit(X_train, y_train)
    y_pred = regressor.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    return mae

#%%
for acao in acoesDisponiveis:
    print(f"Acao: {acao}")
    df = web.DataReader(acao, 'yahoo', start='2015-01-01')
    df.columns = ['price.high', 'price.low', 'price.open', 'price.close', 'volume', 'adjusted.close']
    df_fe = fe.FeatureEngineering(df).pipeline_feat_eng()

    df_ml = df.join(df_fe)
    df_ml['preco_fechamento_ant'] = df_ml['price.close'].shift(1)
    df_ml['preco_fechamento_amanha'] = df_ml['price.close'].shift(-1)
    df_ml = df_ml.fillna(0)
    #Split in train, val and test
    df_train = df_ml.iloc[:int(len(df_ml)*0.7)]
    df_val = df_ml.iloc[int(len(df_ml)*0.7):int(len(df_ml)*0.85)]
    df_test = df_ml.iloc[int(len(df_ml)*0.85):]

#%%
    