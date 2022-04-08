from logging import exception
from os import remove
import pandas as pd
import numpy as np
import json

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import psycopg2

def cria_conexao_postgre()-> psycopg2.extensions.connection:
    params = {
    'host': '34.68.154.58',
    'database': 'postgres',
    'user':'postgres',
    'password':'1',
    }
    conexao = psycopg2.connect(**params)
    return conexao