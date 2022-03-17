#%% Load libs
from pyexpat.errors import XML_ERROR_NOT_STANDALONE
from re import X
import numpy as np
import pandas as pd
import tensorflow as tf
#Importando funções internas:
import os, sys
from feature_engineering import *
from data_prep import *
from models import *
import os.path
import json

with open ('configs.json') as file:
    ativo = json.load(file)[0]

def predita(x_test, df):    
    #  Separing train and test
    X_train, y_train = aplica_pipeline(df)
    X_train = X_train.drop(['price.close'], axis=1)
    print(x_test)
    model = MLP_real_time(X_train,x_test,y_train)
    model.fit()
    return model.predict()
# 

#%% Teste
def main(df,preco_open, preco_high, preco_low, volume, price_adjusted, ret_closing_prices, preco_fechamento_ant):


    x_test = np.array([preco_open,preco_high,preco_low,volume, price_adjusted, ret_closing_prices, preco_fechamento_ant]).reshape(1,-1)
    x_test = pd.DataFrame(x_test, columns=['price.open','price.high','price.low','volume', 'price.adjusted', 'ret.closing.prices', 'preco_fechamento_ant'])
    x_test = normaliza_dados(x_test, df)
    x_test = x_test.drop(['price.close'],axis=1)


    return predita(x_test, df)[0]   



#"Ative_name" vem do Shiny
nome_ativo = ativo

df = pd.read_csv(f"{nome_ativo}.csv")
df['preco_fechamento_ant'] = df['price.close'].shift(1)
df = df.drop(columns=['ref.date','ticker','Unnamed: 0','ret.adjusted.prices'])
df = df.fillna(0)
#Pegar o ultimo valor dos dados (último dia)
preco_abertura = df['price.open'].iloc[-1]
preco_mais_alto = df['price.high'].iloc[-1]
preco_mais_baixo = df['price.low'].iloc[-1]
volume = df['volume'].iloc[-1]
preco_ajustado = df['price.adjusted'].iloc[-1]
ret_closing_prices = df['ret.closing.prices'].iloc[-1]
preco_fechamento_ant = df['preco_fechamento_ant'].iloc[-1]
#Drop the last row (last day)
df = df.drop(df.index[-1])

predicao = main(df,preco_abertura, preco_mais_alto, preco_mais_baixo, volume, preco_ajustado, ret_closing_prices, preco_fechamento_ant)

df.to_csv(f'{nome_ativo}.csv')

os.remove(f'{nome_ativo}.csv')
os.remove('configs.json')
    

