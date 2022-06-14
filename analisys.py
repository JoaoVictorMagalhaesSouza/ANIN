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
with open ('configs.json') as file:
    ativo = json.load(file)[0]

def make_fig(y_true,y_pred_xgb, y_pred_lstm,index,conj):
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(
    go.Scatter(
    x=index,
    y=y_true,
    name='Valor Real',
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
        title_text="Preço",
        
            secondary_y=False, 
            gridcolor='#d3d3d3', 
            zerolinecolor='black')

    fig.update_xaxes(
        title_text="Data",
            gridcolor='#d3d3d3', 
            zerolinecolor='black')

    fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=100, r=0, b=50, t=50),
            height=350,
            title={'text': 'Real x Predito', 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'},
            )
    #fig.show()
    #save fig
    fig.write_image("Artigo/fig_"+acao+"_"+conj+".png")


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
    #dados_erro_percent[acao] = [percentual_dif]
    print('Percentual de erro do XGboost: +-', round(percentual_dif,2),"%")
    #R2
    r2 = r2_score(y_test,pred)
    #dados_r2[acao] = [r2]
    print("R2: ", r2)
    print(f"Correlação entre as curvas: {round(np.corrcoef(y_test,pred)[0][1],2)}")
    return pred, mae, mse, percentual_dif, r2
    #make_fig(y_test,pred,dates)



def lstm_data_transform(x_data, y_data, num_steps=5):
    """ Changes data to the format for LSTM training 
for sliding window approach """
    # Prepare the list for the transformed data
    X, y = list(), list()
    # Loop of the entire data set
    for i in range(x_data.shape[0]):
        # compute a new (sliding window) index
        end_ix = i + num_steps
        # if index is larger than the size of the dataset, we stop
        if end_ix >= x_data.shape[0]:
            break
        # Get a sequence of data for x
        seq_X = x_data[i:end_ix]
        # Get only the last element of the sequency for y
        seq_y = y_data[end_ix]
        # Append the list with sequencies
        X.append(seq_X)
        y.append(seq_y)
    # Make final arrays
    x_array = np.array(X)
    y_array = np.array(y)
    return x_array, y_array

def preditaLSTM(X_train,X_test,y_train,y_test,dates):
    
    # Different scaler for input and output
    scaler_x = MinMaxScaler(feature_range = (0,1))
    scaler_y = MinMaxScaler(feature_range = (0,1))
    # Fit the scaler using available training data
    input_scaler = scaler_x.fit(X_train)
    output_scaler = scaler_y.fit(y_train.values.reshape(-1,1))
    # Apply the scaler to training data
    train_y_norm = output_scaler.transform(y_train.values.reshape(-1,1))
    train_x_norm = input_scaler.transform(X_train)
    # Apply the scaler to test data
    #test_y_norm = output_scaler.transform(y_test.values.reshape(-1,1))
    test_x_norm = input_scaler.transform(X_test)
    X_train = train_x_norm
    y_train = train_y_norm
    X_test = test_x_norm
    #y_test = test_y_norm
    # Reshaping data

    #timesteps = 5, input_dim = num_features geradas, 

    #X_train,y_train = lstm_data_transform(X_train, y_train)
    #X_test,y_test = lstm_data_transform(X_test, y_test)
    #3d input
    X_train = X_train.reshape(X_train.shape[0], X_train.shape[1], 1)
    X_test = X_test.reshape(X_test.shape[0], X_test.shape[1], 1)



    model = ModelLSTM(X_train,X_test,y_train, y_test)
    #model.compile()
    #model.fit()
    #model.save_model()
    model.carrega_modelo()
    pred = model.predict().flatten()
    pred = output_scaler.inverse_transform(pred.reshape(-1,1))
    
    pred = pred.flatten()
    mae = mean_absolute_error(y_test,pred)
    #dados_mae[acao] = [mae]
    print("MAE: ", mae)
    mse = mean_squared_error(y_test,pred)
    #dados_mse[acao] = [mse]
    print("MSE: ", mse)
    percentual_dif = 0
    for r,p in zip(pred,y_test):
        
        percentual_dif += (abs(r-p)/r)
    print('Percentual de erro do LSTM: +-', round(percentual_dif,2),"%")
    #dados_erro_percent[acao] = [percentual_dif]
    r2 = r2_score(y_test,pred)
    #dados_r2[acao] = [r2]
    print("R2: ", r2)
    print(f"Correlação entre as curvas: {round(np.corrcoef(y_test,pred)[0][1],2)}")
    return pred, mae, mse, percentual_dif, r2
    #make_fig(y_test,pred,[x for x in range(len(y_test))])

#%% Teste
def main(df):

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
    #conjuntos = ['Validação','Teste']
    conjuntos = ['Teste']
    algoritmos = ['XGB', 'LSTM']

    for conj in conjuntos:
        if (conj == 'Validação'):
            print("Dados de Validação:")
            x = preditaXGB(X_train,X_val,y_train,y_val,datas_val)
            l = preditaLSTM(X_train,X_val,y_train,y_val,datas_val)
            make_fig(y_val,x,l,datas_val,conj)
        else:
            print("Dados de Teste:")
            pred_xgb, mae_xgb, mse_xgb, percentual_dif_xgb, r2_xgb = preditaXGB(X_train,X_test,y_train,y_test,datas_test)
            pred_lstm, mae_lstm, mse_lstm, percentual_dif_lstm, r2_lstm = preditaLSTM(X_train,X_test,y_train,y_test,datas_test)
            mae = [mae_xgb, mae_lstm]
            mse = [mse_xgb, mse_lstm]
            percentual_dif = [percentual_dif_xgb, percentual_dif_lstm]
            r2 = [r2_xgb, r2_lstm]
            dados_mae[acao] = mae
            dados_mse[acao] = mse
            dados_erro_percent[acao] = percentual_dif
            dados_r2[acao] = r2
            #make_fig(y_test,x,l,datas_test,conj)


        # else:
        #     for conj in conjuntos:
        #         if (conj == 'Validação'):
        #             print("Dados de Validação:")
        #             preditaLSTM(X_train,X_val,y_train,y_val,datas_val)
        #         else:
        #             print("Dados de Teste:")
        #             preditaLSTM(X_train,X_test,y_train,y_test,datas_test)
            
    



#"Ative_name" vem do Shiny
#nome_ativo = ativo
#nome_ativo = 'BBAS3.SA'
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
dados_mae = pd.DataFrame()
dados_mse = pd.DataFrame()
dados_erro_percent = pd.DataFrame()
dados_r2 = pd.DataFrame()
for acao in acoesDisponiveis:
    df = pd.read_csv(f"Dados/{acao}.csv",index_col='ref.date')
    #df = web.DataReader(acao, 'yahoo', start='2022-04-02')
    #Renaming the columns
    df = df.drop(columns=['ticker','ret.adjusted.prices'])


    df = df.fillna(0)
    #Pegar o ultimo valor dos dados (último dia)
    main(df)



# df.to_csv(f'{nome_ativo}.csv')

# os.remove(f'{nome_ativo}.csv')
# os.remove('configs.json')
# exit()

#%% Save to csv
dados_mae.index = ['XGBoost','LSTM']
dados_mse.index = ['XGBoost','LSTM']
dados_erro_percent.index = ['XGBoost','LSTM']
dados_r2.index = ['XGBoost','LSTM']
dados_mae.to_csv('dados_mae.csv')
dados_mse.to_csv('dados_mse.csv')
dados_erro_percent.to_csv('dados_erro_percent.csv')
dados_r2.to_csv('dados_r2.csv')
# %% Load data
dados_mae = pd.read_csv('dados_mae.csv')
dados_mse = pd.read_csv('dados_mse.csv')
dados_erro_percent = pd.read_csv('dados_erro_percent.csv')
dados_r2 = pd.read_csv('dados_r2.csv')


# %% Analise do MAE
xgboost = 0
lstm = 0
for col in dados_mae.columns:
    if (dados_mae[col][0] < dados_mae[col][1]):
        xgboost += 1
    else:
        lstm += 1

print(f'Ativos que o MAE do XGBoost é menor que o do LSTM: {xgboost} - {xgboost/len(dados_mae.columns)*100}%')
print(f'Ativos que o MAE do LSTM é menor que o do XGBoost: {lstm} - {lstm/len(dados_mae.columns)*100}%')

# %% Analise do MSE
xgboost = 0
lstm = 0
for col in dados_mse.columns:
    if (dados_mse[col][0] < dados_mse[col][1]):
        xgboost += 1
    else:
        lstm += 1

print(f"Ativos que o MSE do XGBoost é menor que o do LSTM: {xgboost} - {xgboost/len(dados_mse.columns)*100}%")
print(f"Ativos que o MSE do LSTM é menor que o do XGBoost: {lstm} - {lstm/len(dados_mse.columns)*100}%")
#%% Analise do Erro Percentual
xgboost = 0
lstm = 0
for col in dados_erro_percent.columns:
    if (dados_erro_percent[col][0] < dados_erro_percent[col][1]):
        xgboost += 1
    else:
        lstm += 1

print(f'Ativos que o Erro Percentual do XGBoost é menor que o do LSTM: {xgboost} - {xgboost/len(dados_erro_percent.columns)*100}%')
print(f'Ativos que o Erro Percentual do LSTM é menor que o do XGBoost: {lstm} - {lstm/len(dados_erro_percent.columns)*100}%')

# %% Analise do R2
xgboost = 0
lstm = 0
for col in dados_r2.columns:
    if (dados_r2[col][0] > dados_r2[col][1]):
        xgboost += 1
    else:
        lstm += 1

print(f"Ativos que o R2 do XGBoost é maior que o do LSTM: {xgboost} - {xgboost/len(dados_r2.columns)*100}%")
print(f"Ativos que o R2 do LSTM é maior que o do XGBoost: {lstm} - {lstm/len(dados_r2.columns)*100}%")


# %%
