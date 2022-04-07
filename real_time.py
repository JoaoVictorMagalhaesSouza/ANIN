#%% Load libs
import pandas as pd
#Importando funções internas:
import os
import feature_engineering as fe
from data_prep import *
from models import *
import os.path
import json
import pickle
from calcula_acertos import *



with open ('configs.json') as file:
    ativo = json.load(file)[0]


def preditaXGB(X_train,X_test,y_train):    
    model = ModelXGboost(X_train,y_train)
    model.fit()
    pickle.dump(model, open('xgb_model', "wb"))
    pred = model.predict(X_test)
    return pred[0]
    
def calcula_erro(df):
    df = pd.read_csv('df_for_error.csv', index_col='ref.date')
    df_test = df[int(len(df)*0.8):]
    X_test, y_test = df_test.drop('preco_fechamento_amanha', axis = 1), df_test['preco_fechamento_amanha']
    model = pickle.load(open('xgb_model', "rb"))
    predicao = model.predict(X_test)
    percentual_dif = 0
    real = y_test.values
    for r,p in zip(predicao,real):
        percentual_dif += (abs(r-p)/r)
    return percentual_dif
    




def main(df):

    df_fe = fe.FeatureEngineering(df).pipeline_feat_eng()
    df_ml = df.merge(df_fe, on=df.index, how='left')
    df_ml.index = df_fe.index
    df_ml['preco_fechamento_ant'] = df_ml['price.close'].shift(1)
    df_ml['preco_fechamento_amanha'] = df_ml['price.close'].shift(-1)
    df_ml = df_ml.drop(['key_0'],axis=1)
    df_ml = df_ml.fillna(0)
    df_ml.to_csv('df_for_error.csv')
    #Split in train, val and test
    df_test = df_ml.tail(1)
    df_train = df_ml.iloc[:-1]
    

    X_train, y_train = df_train.drop('preco_fechamento_amanha', axis = 1), df_train['preco_fechamento_amanha']
    X_test = df_test.drop('preco_fechamento_amanha', axis = 1)
    return preditaXGB(X_train,X_test,y_train)



#"Ative_name" vem do Shiny
nome_ativo = ativo


df = pd.read_csv(f"{nome_ativo}.csv",index_col='ref.date')

df = df.drop(columns=['Unnamed: 0','ticker','ret.adjusted.prices','ret.closing.prices'])


df = df.fillna(0)
#Pegar o ultimo valor dos dados (último dia)

predicao = round(main(df),2)
preco_fechamento = round(df.tail(1)['price.close'].values[0],2)
preco_abertura = round(df.tail(1)['price.open'].values[0],2)
preco_mais_alto = round(df.tail(1)['price.high'].values[0],2)
preco_mais_baixo = round(df.tail(1)['price.low'].values[0],2)
volume = df.tail(1)['volume'].values
preco_ajustado = round(df.tail(1)['price.adjusted'].values[0],2)
erro = round(calcula_erro(df),2)
acertos = round(calcula_acertos(ativo),2)


os.remove(f'{nome_ativo}.csv')
os.remove('configs.json')
os.remove('df_for_error.csv')


# %%
