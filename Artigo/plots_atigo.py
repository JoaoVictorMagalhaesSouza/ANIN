import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pandas_datareader as web
import seaborn as sns
sns.set(rc={'figure.figsize':(8,5)})
import random
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
#%% Plot 1 - Distribuições
#Get 15 random stocks from list
random_stocks = random.sample(acoesDisponiveis, 15)
columns = ["Open", "High", "Low", "Close", "Volume", 'Adj Close']
dados_plot = pd.DataFrame()

for stock in random_stocks:
    aux = web.DataReader(stock, data_source='yahoo', start='2010-01-01', end='2019-12-31').loc[:, columns]
    aux['Ativo'] = stock
    dados_plot = dados_plot.append(aux)

dados_plot = dados_plot.reset_index()
#Increase size of plot

for col in columns:
    
    fig = sns.displot(dados_plot,x=col, hue="Ativo", kind='kde', fill=True, height=7)
    #Save fig
    fig.savefig(f'Plots_Dist/{col}.png')
#%% Plot 2 - Correlation
corr = dados_plot.corr()
fig = plt.figure(figsize=(8,8))
fig = sns.heatmap(corr, annot=True, cmap='coolwarm')
fig.savefig(f'{"correlation"}.png')
# %%
