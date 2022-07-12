#%%Imports
from pyexpat.errors import XML_ERROR_NOT_STANDALONE
from re import X
import numpy as np
import pandas as pd
import tensorflow as tf
#Importando funções internas:
import os, sys
from feature_engineering import FeatureEngineering
from data_prep import *
from models import *
import os.path
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler
#import mae
from sklearn.metrics import r2_score
from sklearn.metrics import mean_absolute_error, mean_squared_error
import pandas_datareader as web
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
                      "VIVT3.SA"  ,"WEGE3.SA" ]

acoesDisponiveis = ["B3SA3.SA",'VALE3.SA',"BBAS3.SA"]

for acao in acoesDisponiveis:
    df = web.DataReader(acao, 'yahoo', start='2015-01-01')
    df.columns = ['price.high', 'price.low', 'price.open', 'price.close', 'volume', 'adjusted.close']

    df_fe = FeatureEngineering(df).pipeline_feat_eng()
    df_ml = df.join(df_fe)
    
    df_ml['preco_fechamento_ant'] = df_ml['price.close'].shift(1)
    df_ml['preco_fechamento_amanha'] = df_ml['price.close'].shift(-1)
    df_ml = df_ml.fillna(0)
    df_test = df_ml.tail(1)
    df_train = df_ml.iloc[:-1]   

    X_train, y_train = df_train.drop('preco_fechamento_amanha', axis = 1), df_train['preco_fechamento_amanha']
    X_test = df_test.drop('preco_fechamento_amanha', axis = 1)
    model = ModelXGboost(X_train, y_train)
    model.fit()
    feature_important = model.get_booster().get_score(importance_type='weight')
    keys = list(feature_important.keys())
    values = list(feature_important.values())

    data = pd.DataFrame(data=values, index=keys, columns=["score"]).sort_values(by = "score", ascending=False)
    fig = px.bar(data, x="score", y=data.index, orientation='h', title='Importância das Features',
    labels={'score': 'Importância','index':'Feature'}, color='score')
    
    fig.update_layout(
        # paper_bgcolor='rgba(0,0,0,0)',
        # plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=100, r=0, b=50, t=50),
        height=800,
        width=800
    )    
    
    fig.write_image("Artigo/feat_importance"+acao+".png")
#%%