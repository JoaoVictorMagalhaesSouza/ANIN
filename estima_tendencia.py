#%%
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
FIRST_EXECUTION = False
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
#%% Realizando predicoes
amanha = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')
valores = [amanha]
today = datetime.today().strftime('%Y-%m-%d')
predicao = [today]
for acao in acoesDisponiveis:
    if FIRST_EXECUTION:
        df = web.DataReader(acao, 'yahoo', start='2022-04-02')
        resultado = df['Close'][0] * 100
        valores.append(resultado)

    else:
        df = web.DataReader(acao, 'yahoo', start='2015-01-01')
        df.columns = ['price.high', 'price.low', 'price.open', 'price.close', 'volume', 'adjusted.close']
        df_fe = fe.FeatureEngineering(df).pipeline_feat_eng()
        
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
        resultado = model.predict(X_test)[0]
        valores.append(float(resultado)*100)


#%%
connect = cria_conexao_postgre()
query = "SELECT * FROM dados_predicao WHERE 'TS'=(SELECT MAX('TS') FROM dados_predicao)"
ultima_predicao = pd.read_sql(query, con=connect)
#Mudar aqui todo dia para a data de ontem (ou ultimo dia util)
start = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
end = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
valores_reais = pd.DataFrame()
valores_reais['TS'] = [start,end]
valores_tendencia = [end]
for acao in acoesDisponiveis:
    linha = web.DataReader(acao, 'yahoo', start=start, end=end)
    valores_reais[acao] = (linha.loc[:,['Close']]*100).values
    #Calculando a tendência
    if ((valores_reais[acao][0] - valores_reais[acao][1]) > 0) and ((valores_reais[acao][0] - ultima_predicao[acao][0]) > 0):
        valores_tendencia.append("Acertou")
    elif ((valores_reais[acao][0] - valores_reais[acao][1]) < 0) and ((valores_reais[acao][0] - ultima_predicao[acao][0]) < 0):
        valores_tendencia.append('Acertou')
    else:
        valores_tendencia.append("Errou")

connection = cria_conexao_postgre()
valores_tendencia = str(valores_tendencia).replace('[', '').replace(']', '').replace(' ', '')
query = f'INSERT INTO tendencia VALUES ({valores_tendencia})'
cursor = connection.cursor()
cursor.execute(query)
connection.commit()
cursor.close()



#%% Save predict
conexao = cria_conexao_postgre()
valores = str(valores).replace('[', '').replace(']', '').replace(' ', '')
query_insert = f'INSERT INTO dados_predicao VALUES ({valores})'
cursor = conexao.cursor()
cursor.execute(query_insert)
conexao.commit()
cursor.close()

# %%
