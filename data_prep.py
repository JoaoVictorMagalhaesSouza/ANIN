import pandas as pd
import numpy as np

def limpa_dados(df: pd.DataFrame):
    pass



def normaliza_dados(x: pd.DataFrame, df_original: pd.DataFrame):
    #Med e DP
    return (x - df_original.mean()) / df_original.std()

    #Min e Max:
    # return (df - df.min()) / (df.max() - df.min())


def separa_dados(df: pd.DataFrame, percent_train: float = 1):
    percent_train = int(percent_train * df.shape[0])
    X_train = df.iloc[:percent_train,:]
    y_train = X_train.pop('price.close')

    return X_train, y_train



def aplica_pipeline(df: pd.DataFrame):
    X_train, y_train = separa_dados(df)
    df_original = df.copy()
    X_train = normaliza_dados(X_train, df_original)
    return X_train, y_train
