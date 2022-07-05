#%% Load libs
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

def make_fig(y_true,y_pred_xgb, y_pred_lstm,index,conj):
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(
    go.Scatter(
    x=index,
    y=y_true,
    name='Real Price',
    mode='lines',
    marker_color='#000000',
    ), secondary_y=False)

    
    fig.add_trace(
        go.Scatter(
        x=index,
        y=y_pred_xgb,
        name='XGBoost',
        mode='lines',
        marker_color='#fd5800',#'#ccff33',
    ), secondary_y=False)

    fig.add_trace(
        go.Scatter(
        x=index,
        y=y_pred_lstm,
        name='LSTM',
        mode='lines',
        marker_color='#4133ff',
    ), secondary_y=False)

   

    fig.update_yaxes(
        title_text="Price (R$)",
        
            secondary_y=False, 
            gridcolor='#d3d3d3', 
            zerolinecolor='black')

    fig.update_xaxes(
        title_text="Date",
            gridcolor='#d3d3d3', 
            zerolinecolor='black')

    fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=100, r=0, b=50, t=50),
            height=350,
            title={'text': 'Graph of true values vs predicted values', 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
            )
    #fig.show()
    #save fig
    fig.write_image("Artigo/fig_"+acao+"_"+conj+".png")

#%%

def preditaXGB(X_train,X_test,y_train,y_test,dates):    
    model = ModelXGboost(X_train,y_train)
    model.fit()
    pred = model.predict(X_test)
    mae = mean_absolute_error(y_test,pred)
    #dados_mae[acao] = [mae]
    print("MAE: ", mae)
    mse = mean_squared_error(y_test,pred)
    #dados_mse[acao] = [mse]
    print("MSE: ", mse)
    percentual_dif = 0
    for r,p in zip(list(pred),list(y_test.values)):
        #print(f'Real: {r} Pred: {p}')
        percentual_dif += (abs(r-p)/r)
    percentual_dif = percentual_dif/len(pred)
    #dados_erro_percent[acao] = [percentual_dif]
    print('Percentual de erro do XGboost: +-', percentual_dif*100,"%")
    #R2
    r2 = r2_score(y_test,pred)
    #dados_r2[acao] = [r2]
    print("R2: ", r2)
    print(f"Correlação entre as curvas: {round(np.corrcoef(y_test,pred)[0][1],2)}")
    #make_fig(y_test,pred,dates)
    return pred, mae, mse, percentual_dif, r2
    
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
mae_sem_fe = []
mae_com_fe = []

mse_sem_fe = []
mse_com_fe = []

mape_sem_fe = []
mape_com_fe = []

r2_sem_fe = []
r2_com_fe = []


for acao in acoesDisponiveis:
    df = pd.read_csv(f"Dados/{acao}.csv",index_col='ref.date')
    #df = web.DataReader(acao, 'yahoo', start='2022-04-02')
    #Renaming the columns
    df = df.drop(columns=['ticker','ret.adjusted.prices'])


    df = df.fillna(0)
    #Pegar o ultimo valor dos dados (último dia)
    df_fe = FeatureEngineering(df).pipeline_feat_eng()
    df_ml = df.merge(df_fe, on=df.index, how='left')
    df_ml.index = df_fe.index
    df_ml['preco_fechamento_ant'] = df_ml['price.close'].shift(1)
    df_ml['preco_fechamento_amanha'] = df_ml['price.close'].shift(-1)
    df_ml = df_ml.drop(['key_0'],axis=1)
    df_ml = df_ml.fillna(0)
    #Remove last row
    df_ml = df_ml.drop(df_ml.index[-1])
    #Split in train and test
    df_train = df_ml.iloc[:int(len(df_ml)*0.9)]
    df_test = df_ml.iloc[int(len(df_ml)*0.9):]

    X_train, y_train = df_train.drop('preco_fechamento_amanha', axis = 1), df_train['preco_fechamento_amanha']
    X_test, y_test = df_test.drop('preco_fechamento_amanha', axis = 1), df_test['preco_fechamento_amanha']
    datas_test = df_test.index
    pred_xgb_fe, mae_xgb_fe, mse_xgb_fe, percentual_dif_xgb_fe, r2_xgb_fe = preditaXGB(X_train,X_test,y_train,y_test,datas_test)
    mae_com_fe.append(mae_xgb_fe)
    mse_com_fe.append(mse_xgb_fe)
    mape_com_fe.append(percentual_dif_xgb_fe)
    r2_com_fe.append(r2_xgb_fe)

    #SEM FE
    df = pd.read_csv(f"Dados/{acao}.csv",index_col='ref.date')
    #df = web.DataReader(acao, 'yahoo', start='2022-04-02')
    #Renaming the columns
    df = df.drop(columns=['ticker','ret.adjusted.prices'])


    df = df.fillna(0)
    #Pegar o ultimo valor dos dados (último dia)
    #df_fe = FeatureEngineering(df).pipeline_feat_eng()
    #df_ml = df.merge(df_fe, on=df.index, how='left')
    #df_ml.index = df_fe.index
    df_ml['preco_fechamento_ant'] = df_ml['price.close'].shift(1)
    df_ml['preco_fechamento_amanha'] = df_ml['price.close'].shift(-1)
    #df_ml = df_ml.drop(['key_0'],axis=1)
    df_ml = df_ml.fillna(0)
    #Remove last row
    df_ml = df_ml.drop(df_ml.index[-1])
    #Split in train and test
    df_train = df_ml.iloc[:int(len(df_ml)*0.9)]
    df_test = df_ml.iloc[int(len(df_ml)*0.9):]

    X_train, y_train = df_train.drop('preco_fechamento_amanha', axis = 1), df_train['preco_fechamento_amanha']
    X_test, y_test = df_test.drop('preco_fechamento_amanha', axis = 1), df_test['preco_fechamento_amanha']
    datas_test = df_test.index
    pred_xgb, mae_xgb, mse_xgb, percentual_dif_xgb, r2_xgb = preditaXGB(X_train,X_test,y_train,y_test,datas_test)
    mae_sem_fe.append(mae_xgb)
    mse_sem_fe.append(mse_xgb)
    mape_sem_fe.append(percentual_dif_xgb)
    r2_sem_fe.append(r2_xgb)
#%%
mae = 0
mse = 0
mape = 0
r2 = 0
for i in range (len(mae_sem_fe)):
    if (mae_com_fe[i] < mae_sem_fe[i]):
        mae += 1
    if (mse_com_fe[i] < mse_sem_fe[i]):
        mse += 1
    if (mape_com_fe[i] < mape_sem_fe[i]):
        mape += 1
    if (r2_com_fe[i] > r2_sem_fe[i]):
        r2 += 1

print(f"Percentual de ativos em que o MAE da FE foi menor que MAE sem FE: {(mae/67)*100}")
print(f"Percentual de ativos em que o MSE da FE foi menor que MSE sem FE: {(mse/67)*100}")
print(f"Percentual de ativos em que o MAPE da FE foi menor que MAPE sem FE: {(mape/67)*100}")
print(f"Percentual de ativos em que o R2 da FE foi maior que R2 sem FE: {(r2/67)*100}")
# %%
