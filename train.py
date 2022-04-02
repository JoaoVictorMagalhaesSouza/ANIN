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

with open ('configs.json') as file:
    ativo = json.load(file)[0]

def make_fig(y_true,y_pred,index):
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    fig.add_trace(
    go.Scatter(
    x=index,
    y=y_true,
    name='Valor Real',
    mode='markers+lines',
    marker_color='#000000',
    ), secondary_y=False)

    
    fig.add_trace(
        go.Scatter(
        x=index,
        y=y_pred,
        name='Valor Previsto',
        mode='markers+lines',
        marker_color='#fd5800',#'#ccff33',
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
    fig.show()


def preditaXGB(X_train,X_test,y_train,y_test,dates):    
    model = ModelXGboost(X_train,y_train)
    model.fit()
    pred = model.predict(X_test)
    mae = mean_absolute_error(y_test,pred)
    print("MAE: ", mae)
    percentual_dif = 0
    for r,p in zip(list(pred),list(y_test.values)):
        #print(f'Real: {r} Pred: {p}')
        percentual_dif += (abs(r-p)/r)
    print('Percentual de erro do XGboost: +-', round(percentual_dif,2),"%")
    make_fig(y_test,pred,dates)

def preditaMLP(X_train,X_test,y_train,y_test,dates):
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

    model = ModelMLP(X_train,y_train)
    model.compile()
    model.fit()
    pred = model.predict(X_test).flatten()
    pred = output_scaler.inverse_transform(pred.reshape(-1,1))
    #y_test = output_scaler.inverse_transform(y_test)
    pred = pred.flatten()
    mae = mean_absolute_error(y_test,pred)
    print("MAE: ", mae)
    percentual_dif = 0
    for r,p in zip(list(pred),list(y_test.values)):
        #print(f'Real: {r} Pred: {p}')
        percentual_dif += (abs(r-p)/r)
    print('Percentual de erro do MLP: +-', round(percentual_dif,2),"%")
    make_fig(y_test,pred,dates)



def lstm_data_transform(x_data, y_data, num_steps=3):
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

    X_train,y_train = lstm_data_transform(X_train, y_train)
    X_test,y_test = lstm_data_transform(X_test, y_test)
    


    model = ModelLSTM(X_train,y_train)
    model.compile()
    model.fit()
    pred = model.predict(X_test).flatten()
    pred = output_scaler.inverse_transform(pred.reshape(-1,1))
    
    pred = pred.flatten()
    mae = mean_absolute_error(y_test,pred)
    print("MAE: ", mae)
    percentual_dif = 0
    for r,p in zip(pred,y_test):
        
        percentual_dif += (abs(r-p)/r)
    print('Percentual de erro do LSTM: +-', round(percentual_dif,2),"%")
    make_fig(y_test,pred,[x for x in range(len(y_test))])

#%% Teste
def main(df):

    df_fe = FeatureEngineering(df).pipeline_feat_eng()
    df_ml = df.merge(df_fe, on=df.index, how='left')
    df_ml.index = df_fe.index
    df_ml['preco_fechamento_ant'] = df_ml['price.close'].shift(1)
    df_ml['preco_fechamento_amanha'] = df_ml['price.close'].shift(-1)
    df_ml = df_ml.drop(['key_0'],axis=1)
    df_ml = df_ml.fillna(0)
    #Split in train, val and test
    df_test = df_ml.iloc[(int(len(df_ml)*0.9)):]
    df_train = df_ml.iloc[:(int(len(df_ml)*0.9))]
    df_val = df_train.iloc[(int(len(df_train)*0.9)):]

    X_train, y_train = df_train.drop('preco_fechamento_amanha', axis = 1), df_train['preco_fechamento_amanha']
    X_val, y_val = df_val.drop('preco_fechamento_amanha', axis = 1), df_val['preco_fechamento_amanha']
    X_test, y_test = df_test.drop('preco_fechamento_amanha', axis = 1), df_test['preco_fechamento_amanha']
    datas_val = df_val.index
    datas_test = df_test.index
    conjuntos = ['Validação','Teste']
    algoritmos = ['XGB','MLP', 'LSTM']

    for alg in algoritmos:
        print('\n',alg)
        if alg == 'XGB':
            for conj in conjuntos:
                if (conj == 'Validação'):
                    print("Dados de Validação:")
                    preditaXGB(X_train,X_val,y_train,y_val,datas_val)
                else:
                    print("Dados de Teste:")
                    preditaXGB(X_train,X_test,y_train,y_test,datas_test)

        elif alg == 'MLP':
            for conj in conjuntos:
                if (conj == 'Validação'):
                    print("Dados de Validação:")
                    preditaMLP(X_train,X_val,y_train,y_val,datas_val)
                else:
                    print("Dados de Teste:")
                    preditaMLP(X_train,X_test,y_train,y_test,datas_test)

        else:
            for conj in conjuntos:
                if (conj == 'Validação'):
                    print("Dados de Validação:")
                    preditaLSTM(X_train,X_val,y_train,y_val,datas_val)
                else:
                    print("Dados de Teste:")
                    preditaLSTM(X_train,X_test,y_train,y_test,datas_test)
            
    



#"Ative_name" vem do Shiny
nome_ativo = ativo
nome_ativo = 'ABEV3.SA'
df = pd.read_csv(f"{nome_ativo}.csv",index_col='ref.date')

df = df.drop(columns=['ticker','ret.adjusted.prices'])


df = df.fillna(0)
#Pegar o ultimo valor dos dados (último dia)




df.to_csv(f'{nome_ativo}.csv')

os.remove(f'{nome_ativo}.csv')
os.remove('configs.json')
exit()

