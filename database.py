from logging import exception
from os import remove
import pandas as pd
import numpy as np
import json
from pyodbc import connect
import pyodbc
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import psycopg2

def cria_conexão_banco()-> pyodbc.Connection:

    #Criando a conexão com o Banco de Dados
    host = '35.232.77.137'
    database = 'acompanhamento_lucro'
    user = 'sqlserver'
    password = '1'

    conexao = connect(
            driver='{ODBC Driver 17 for SQL Server}',
            host=host,
            database=database,
            user=user,
            password=password
    )
    return conexao

def cria_conexao_postgre()-> psycopg2.extensions.connection:
    params = {
    'host': '34.68.154.58',
    'database': 'postgres',
    'user':'postgres',
    'password':'1',
    }
    conexao = psycopg2.connect(**params)
    return conexao