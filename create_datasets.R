library("BatchGetSymbols")
library("data.table")

createDataSet <- function(acao){
  DI = '2015-01-01' #Data de inicio
  DF = Sys.Date() #Data de fim(hoje)
  benchmark = '^BVSP' #indice da bolsa
  DataSet = BatchGetSymbols(
    tickers = acao, #Especificando as ações
    first.date = DI,
    last.date= DF,
    bench.ticker = benchmark)
  
  
  #Pegando o segundo elemento da lista retornada, que e o que contem os dados.
  DataSet = DataSet$df.tickers
  
  write.csv(DataSet,paste0("Dados/",acao,".csv"))
  print("Escrito com sucesso !")
  
}
acoesDisponiveis <- c("ABEV3.SA" , "B3SA3.SA" , "BBAS3.SA",  "BBDC3.SA"  ,"BBDC4.SA" , "BBSE3.SA", 
                      "BEEF3.SA"  ,"BRAP4.SA"  ,"BRFS3.SA" , "BRKM5.SA"  ,"BRML3.SA"  , "CCRO3.SA" ,
                      "CIEL3.SA"  ,"CMIG4.SA"  ,"COGN3.SA" , "CPFE3.SA" , "CPLE6.SA",  "CSAN3.SA",  "CSNA3.SA", 
                      "CVCB3.SA"  ,"CYRE3.SA"  ,"ECOR3.SA"  ,"EGIE3.SA" , "ELET3.SA",  "ELET6.SA",  "EMBR3.SA", 
                      "ENBR3.SA"  ,"ENEV3.SA"  ,"ENGI11.SA" ,"EQTL3.SA" , "EZTC3.SA",  "FLRY3.SA",  "GGBR4.SA", 
                      "GOAU4.SA"  ,"GOLL4.SA"  ,"HYPE3.SA" ,  "ITSA4.SA",  "ITUB4.SA", 
                      "JBSS3.SA"  ,"JHSF3.SA"  ,"KLBN11.SA"  ,"LCAM3.SA",  "LREN3.SA",  "MGLU3.SA", 
                      "MRFG3.SA"  ,"MRVE3.SA"  ,"MULT3.SA"  ,"PCAR3.SA"  ,"PETR3.SA",  "PETR4.SA",  "PRIO3.SA", 
                      "QUAL3.SA"  ,"RADL3.SA"  ,"RAIL3.SA"  ,"RENT3.SA"  ,"SANB11.SA", "SBSP3.SA",  "SULA11.SA",
                      "SUZB3.SA"  ,"TAEE11.SA" ,"TIMS3.SA"  ,"TOTS3.SA"  ,"UGPA3.SA",  "USIM5.SA",  "VALE3.SA" ,
                      "VIVT3.SA"  ,"WEGE3.SA"  ,"YDUQ3.SA" )

for (i in acoesDisponiveis){
  createDataSet(i)
}