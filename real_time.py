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
from database import *
from datetime import datetime
from sklearn.metrics import mean_absolute_percentage_error as mape



with open ('configs.json') as file:
    ativo = json.load(file)[0]


def preditaXGB(X_train,X_test,y_train):    
    model = ModelXGboost(X_train,y_train)
    model.fit()
    pickle.dump(model, open('xgb_model', "wb"))
    pred = model.predict(X_test)
    return pred[0]
    
def calcula_erro(nome_ativo):
    conexao = cria_conexao_postgre()
    query = f'SELECT "TS","{nome_ativo}" FROM dados_predicao ORDER BY "TS" DESC LIMIT 10'
    dados_predicao = pd.read_sql(query, con=conexao)
    max_ts = dados_predicao[dados_predicao.index==0]
    today = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    ts_predicao = dados_predicao['TS']
    ts_predicao.pop(0)
    dados_predicao[nome_ativo] = (dados_predicao[nome_ativo]/100).values
    if (int(today[11:13]) < 17) or (max_ts['TS'][0] != today[0:10]):
        lastElementIndex = 0
        dados_predicao = dados_predicao[dados_predicao.index != lastElementIndex]

    data_inicial = min(ts_predicao).strftime("%Y-%m-%d")
    data_final = max(ts_predicao).strftime("%Y-%m-%d")
    dados_reais = web.DataReader(nome_ativo, 'yahoo', start=data_inicial,end=data_final)
    #dados_reais = dados_reais[dados_reais.index.isin(ts_predicao)]
    dados_reais['TS'] = dados_reais.index
    dados_reais['TS'] = dados_reais['TS'].astype(str)
    dados_predicao['TS'] = dados_predicao['TS'].astype(str) 
    df_final = dados_predicao.merge(dados_reais,on='TS')

    dados_predicao = df_final.pop(nome_ativo).values
    dados_reais = df_final.pop('Close').values
        

    erro_percentual = 0
    for i in range (len(dados_predicao)):
        erro_percentual += abs((dados_predicao[i]-dados_reais[i])/dados_reais[i])
    erro_percentual = erro_percentual/len(dados_predicao)

    # df = pd.read_csv('df_for_error.csv', index_col='ref.date')
    # df_train = df[:int(len(df)-10)]
    # df_test = df[:int(len(df)-10):]
    # X_train, y_train = df_train.drop('preco_fechamento_amanha', axis = 1), df_train['preco_fechamento_amanha']
    # X_test, y_test = df_test.drop('preco_fechamento_amanha', axis = 1), df_test['preco_fechamento_amanha']
    # preditaXGB(X_train,X_test,y_train)
    # model = pickle.load(open('xgb_model', "rb"))
    # predicao = model.predict(X_test)
    # percentual_dif = 0
    # real = y_test.values
    # for r,p in zip(predicao,real):
    #     percentual_dif += (abs(r-p)/r)
    return erro_percentual*100

    




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
erro = round(calcula_erro(nome_ativo),2)
acertos = round(calcula_acertos(ativo),2)


os.remove(f'{nome_ativo}.csv')
os.remove('configs.json')
os.remove('df_for_error.csv')



# %%
