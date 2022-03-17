'''
    Módulo destinado à feature engineering dos dados.
'''
from json.encoder import py_encode_basestring
from typing import List
import pandas as pd
import numpy as np
from abc import ABC, abstractmethod

class FeatureEngineeringBase(ABC):

    @abstractmethod
    def transform(self, cols: List[str], **kwargs):
        pass

class FeatureEngineeringFactory(FeatureEngineeringBase):

    def __init__(self, dataframe: pd.DataFrame()):
        self.data = dataframe

    
    def cria_feature_engineering(self, features: str, cols: List[str], **kwargs):
        df_feature_engineering = pd.DataFrame()
        for i,feature in enumerate(features):
            if feature.lower() == 'derivada':
                dados, nome_colunas = Derivada(self.data).transform(cols[i]) 
            elif feature.lower() == 'momentos_estatisticos':
                dados, nome_colunas = MomentosEstatisticos(self.data).transform(cols[i], **kwargs)
            elif feature.lower() == 'integral':
                dados, nome_colunas = Integral(self.data).transform(cols[i], **kwargs)
            else:
                raise Exception("Feature engineering não encontrada")

            df_feature_engineering[nome_colunas] = dados
        
        return df_feature_engineering, df_feature_engineering.columns
                
        

    def transform(self, cols: List[str]):
        pass

class Derivada(FeatureEngineeringFactory):

    def transform(self, cols: List[str], **kwargs):
        df_feature_engineering = pd.DataFrame()
        for coluna in cols:
            df_feature_engineering[f'derivada_{coluna}'] = np.diff(self.data[coluna])
        
        return df_feature_engineering, df_feature_engineering.columns

class MomentosEstatisticos(FeatureEngineeringFactory):

    def transform(self, cols: List[str], **kwargs):
        df_feature_engineering = pd.DataFrame()
        for coluna in cols:
            df_feature_engineering[f'{coluna}_med_mov_{kwargs["janela_momentos"]}'] = self.data[coluna].rolling(kwargs['janela_momentos']).mean()
            df_feature_engineering[f'{coluna}_std_mov_{kwargs["janela_momentos"]}'] = self.data[coluna].rolling(kwargs['janela_momentos']).std()
            df_feature_engineering[f'{coluna}_max_mov_{kwargs["janela_momentos"]}'] = self.data[coluna].rolling(kwargs['janela_momentos']).max()
            df_feature_engineering[f'{coluna}_min_mov_{kwargs["janela_momentos"]}'] = self.data[coluna].rolling(kwargs['janela_momentos']).min()
            df_feature_engineering[f'{coluna}_var_mov_{kwargs["janela_momentos"]}'] = self.data[coluna].rolling(kwargs['janela_momentos']).var()

        return df_feature_engineering, df_feature_engineering.columns

class Integral(FeatureEngineeringFactory):
    def transform(self, cols: List[str], **kwargs):
        df_feature_engineering = pd.DataFrame()
        for coluna in cols:
            df_feature_engineering[f'{coluna}_integral_{kwargs["janela_integral"]}'] = self.data[coluna].rolling(kwargs['janela_integral']).sum()
        
        return df_feature_engineering, df_feature_engineering.columns
        
        