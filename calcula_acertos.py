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

def calcula_acertos(ativo: str):
    connect = cria_conexão_banco()
    query = f'SELECT TOP 7 [TS],[{ativo}] FROM tendencia ORDER BY TS DESC'
    df = pd.read_sql(query, connect)
    acertos = df[df[ativo]=='Acertou'].count()[0]
    erros = df[df[ativo]=='Errou'].count()[0]
    return (acertos/(acertos+erros))*100