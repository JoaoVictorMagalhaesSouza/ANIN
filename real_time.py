#%% Load libs
import pandas as pd
#Importando funções internas:
import os
import feature_engineering as fe
from data_prep import *
from models import *
import os.path
import json



with open ('configs.json') as file:
    ativo = json.load(file)[0]


def preditaXGB(X_train,X_test,y_train):    
    model = ModelXGboost(X_train,y_train)
    model.fit()
    pred = model.predict(X_test)
    return pred[0]
    





#%% Teste
def main(df):

    df_fe = fe.FeatureEngineering(df).pipeline_feat_eng()
    df_ml = df.merge(df_fe, on=df.index, how='left')
    df_ml.index = df_fe.index
    df_ml['preco_fechamento_ant'] = df_ml['price.close'].shift(1)
    df_ml['preco_fechamento_amanha'] = df_ml['price.close'].shift(-1)
    df_ml = df_ml.drop(['key_0'],axis=1)
    df_ml = df_ml.fillna(0)
    #Split in train, val and test
    df_test = df_ml.tail(1)
    df_train = df_ml.iloc[:-1]
    

    X_train, y_train = df_train.drop('preco_fechamento_amanha', axis = 1), df_train['preco_fechamento_amanha']
    X_test = df_test.drop('preco_fechamento_amanha', axis = 1)
    return preditaXGB(X_train,X_test,y_train)



#"Ative_name" vem do Shiny
nome_ativo = ativo
df = pd.read_csv(f"{nome_ativo}.csv",index_col='ref.date')

df = df.drop(columns=['ticker','ret.adjusted.prices'])


df = df.fillna(0)
#Pegar o ultimo valor dos dados (último dia)

predicao = round(main(df),2)
preco_abertura = round(df.tail(1)['price.open'].values[0],2)
preco_mais_alto = round(df.tail(1)['price.high'].values[0],2)
preco_mais_baixo = round(df.tail(1)['price.low'].values[0],2)
volume = df.tail(1)['volume'].values
preco_ajustado = round(df.tail(1)['price.adjusted'].values[0],2)


os.remove(f'{nome_ativo}.csv')
os.remove('configs.json')

