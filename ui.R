#
# This is the user-interface definition of a Shiny web application. You can
# run the application by clicking 'Run App' above.
#
# Find out more about building applications with Shiny here:
#
#    http://shiny.rstudio.com/
#

# Define UI for application

shinyUI(shinydashboardPlus::dashboardPage(md=T, skin = 'blue-light',
  
  dashboardHeader(title = "Análise da Bolsa de Valores de São Paulo",titleWidth = '500px'),
  

  sidebar <- dashboardSidebar(
    sidebarMenu(
      menuItem(h4("Apresentação"), tabName = "presentation"),
      menuItem(h4("Ativos"), tabName = "actives", 
               menuItem(h5("Série Temporal"), tabName = "time_series"),
               menuItem(h5("Comparação com a B3"), tabName = 'b3_comparation'),
               menuItem(h5("Boxplot"), tabName = 'boxplot')
               ),
      
      menuItem(h4("Setorial"),tabName = 'sectorial'),
      menuItem(h4("Candlesticks"),tabName = 'candles'),
      menuItem(h4("Fronteira de Markowitz"),tabName = 'markowitz',
               menuItem(h5("O que é"), tabName = "whats_markowitz"),
               menuItem(h5("Simular Portfólio"), tabName = "simulation_markowitz")
               
               ),
      
      menuItem(h4("Predição de Valores"),tabName = 'prediction',
               menuItem(h5("O que é"), tabName = "how_prediction"),
               menuItem(h5("Realizar predição"), tabName = "todo_prediction")
             
      ),
      menuItem(h4("Desenvolvedores"),tabName = 'developers')
      
      
               
    ), width = '250px'
    
  ),
 body <-  dashboardBody(
   tabItems(
     tabItem(tabName = "presentation",
             h3(style = "font-weight: bold","Projeto: Análise dos Ativos da B",tags$sup("3")),
             p(style = "text-align: justify;", style = "font-size:25px;","Propomos com este trabalho, 
            uma maneira prática e objetiva para visualizar de forma interativa 
            e comparativa a evolução dos preço de ativos da Bolsa de Valores de 
            São Paulo. Esta", em("dashboard"), "foi produzida como resultado do 
            trabalho de Iniciação Científica voluntária do aluno de graduação", 
               strong("João Victor M. Souza"), "orientado pelo professor", 
               strong("Fernando de Souza Bastos"), "(vide aba 'Desenvolvedores')."
              ),
             br(),
             p(style = "text-align: justify;", style = "font-size:25px;",strong("Observação Importante:"), 
               "Este trabalho não tem o objetivo de sugerir a compra de nenhum ativo da bolsa. "),
             
             
            
     ),
     
     tabItem(tabName = "time_series",
             h3(style = "font-weight: bold","Visualização temporal do comportamento dos ativos"),
             fluidRow(column(3,
                             selectizeInput("inAtivosSerie",
                                         strong("Escolha um ou mais ativos:"),
                                         multiple = TRUE,
                                         choices=c(acoesDisponiveis))),
                      column(9,
                             dygraphOutput("outPlotAtivos", height = 500))
                      
                      
             )),
     
     tabItem(tabName = "b3_comparation",
             h3(style = "font-weight: bold","Comparação de um ativo com a B3:"),
             fluidRow(column(3,
                             selectizeInput("inAtivoCompB3",
                                         strong("Escolha um ou mais ativos:"),
                                         multiple = TRUE,
                                         choices=noB3)),
                      column(9,
                             dygraphOutput("outAtivoCompB3", height = 500))
      )),
     
     tabItem(tabName = 'boxplot',
             h3(style = "font-weight: bold","Boxplot dos valores de um ativo nos últimos anos"),
             fluidRow(column(3, 
                             selectizeInput("inBoxAnualAtivo", 
                                         strong("Escolha um ativo:"), 
                                         choices=c(acoesDisponiveis))
                             
                             
             ),
             
             
             column(9,
                    plotlyOutput("outBoxplotAtivo", height = 600))
             
             )),
     
     tabItem(tabName = 'sectorial',
             h3(style = "font-weight: bold","Análise setorial dos ativos"),
             fluidRow(column(9,
                             selectizeInput("inSetorFilt",
                                         strong("Escolha o setor que deseja monitorar: "),
                                         choices = listaSetores,
                                         selected = NULL,
                                         multiple = FALSE
                             )
             ),
             
             
             column(9,
                    uiOutput("outSetorFilt"))
             )),
     
     
     tabItem(tabName = 'candles',
             h3(style = "font-weight: bold","Candlesticks dos ativos"),
             fluidRow(column(3,
                             selectizeInput("inCandles",
                                            strong("Escolha os ativos que deseja monitorar: "),
                                            choices = c(acoesDisponiveis),
                                            selected = "B3SA3.SA",
                                            multiple = FALSE
                                            
                             )
             ),
             
             br(),
             column(9,
                    plotlyOutput("outCandles",height = 500))
             )),
     
     tabItem(tabName = 'whats_markowitz',
             h3(style = "font-weight: bold","O que é a Teoria de Markowitz"),
             h4(style = "text-align: justify;","A Teoria Moderna do Portfólio, também conhecida como Fronteira Eficience de Markowitz ou Portfólio Eficiente de Markowitz,
                                       consiste em uma teoria desenvolvida por um economista chamado",strong("Harry Markowitz"),"na qual objetiva-se otimizar a carteira de investimentos de um investidor analisando dois fatores: risco e retorno.
                                       Grosseiramente, é possível analisar combinações de proporções de risco e retorno dos ativos da carteira de maneira a escolher combinações de investimento que sejam
                                       mais rentáveis e menos arriscadas.
                                 "),
             br(),
             h4(style = "text-align: justify;","Essa análise permite que guiar o investidor de forma que, correndo o mesmo risco para diferente distribuições de recursos de investimento,
                                         ele possa escolher a que lhe trará o maior retorno. Paralelamente, a teoria traz, interessantemente, o fato de que a carteira deve ser montada com ações de diferentes setores,
                                         de modo que apresentem uma correlação forte e negativa (inversamente proporcionais), visando sempre otimizar mas, ao mesmo tempo, minimizar as possíveis perdas.
                                         Logo, é possível observar que a Fronteira Eficiente consiste em todos os pontos onde o retorno é máximo e estes pontos, por sua vez, variam de acordo com o risco que o investidor
                                         está disposto a correr."),
             br(),
             h4("O que é o ",strong("risco")," ?"),
             br(),
             h4(style = "text-align: justify;","O cálculo do risco, seguindo a Teoria do Portfólio de Markowitz, é calculada utilizando a variância de todos os ativos presentes na carteira acrescida do cálculo
                                         da covariância entre os pares de ativos da carteira. Logo, se tivermos uma carteira com apenas dois ativos A e B, termos o risco dado por: "),
             br(),
             h4(style = "text-align: center;",strong("Risco(A,B) = var(A) + var(B) + 2*cov(A,B)")),
             br(),
             h4(style = "text-align: justify;","Generalizando, o risco para uma carteira com N ativos é expresso da seguinte forma:"),
             br(),
             h4(style = "text-align: center; color: red;",strong("Risco(A,B,C,...,N) = var(A) + var(B) + var(C) + ... + var(N) + 2*cov(A,B) + 2*cov(A,C) + ... + 2*cov(A,N) + ... + 2*cov(N-1,N)")),
             br(),
             h4(style = "text-align: justify;","Estatisticamente, a covariância pode ser escrita também em função da correlação entre os ativos. Dessa forma, se os ativos apresentarem uma correlação forte e negativa,
                                         isso significa que quando um ativo for desvalorizado, o outro não-necessariamente será desvalorizado também, minimizando o risco do investimento."),
             br(),
             h4("O que é o ",strong("retorno esperado")," ?"),
             br(),
             h4(style = "text-align: justify;","O retorno esperado é medido a partir do cálculo da soma dos valores esperados dos ativos da carteira, considerando seu comportamento temporalmente, ou seja, levando em conta seu desempenho ao longo do tempo.
                                         Sendo assim, se tivermos uma carteira com dois ativos X e Y, nosso retorno esperado será: "),
             br(),
             h4(style = "text-align: center;",strong("Retorno esperado(A,B) = E(A) + E(B)")),
             br(),
             h4(style = "text-align: justify;","De modo geral, o retorno esperado pode ser escrito, para uma carteira com N ativos, como: "),
             br(),
             h4(style = "text-align: center; color: red;",strong("Retorno esperado(A,B,...,N) = E(A) + E(B) + ... + E(N)")),
             br(),
             h4(style = "text-align: justify;","Dessa forma, podemos entender que se um investimento tem 50% de chances de valorizar 20% e 50% de chances de desvalorizar 10%, o retorno esperado é de ",strong("5%")," pois: (20% x 50% + 10% x 50% = 5%)."),
             br()
             
             
             ),
     
     tabItem(tabName = 'simulation_markowitz',
             h3(style = "font-weight: bold","Simular uma carteira de investimentos"),
             sidebarLayout(
               column(9,
                      selectizeInput("inAtivosMark",
                                  strong("Escolha os ativos do portfólio (mín. 2):"),
                                  choices=c(acoesDisponiveis),
                                  multiple = TRUE
                      ),
                      actionButton(inputId="buttonOk", label="Gerar", icon("paper-plane"), 
                                   style="color: #fff; background-color: #337ab7; border-color: #2e6da4")
                      
                      
               ),
               mainPanel(
                 
                 fluidRow(column(offset = 5,width = 12,plotlyOutput("outCartMark"))),
                 br(),
                 br(),
                 br(),
                 
                 div(
                   splitLayout(style = "border 1px solid silver",cellWidths = c("50%","25%","50%"),plotlyOutput("outMark1"),NULL,plotlyOutput("outMark2")),
                   style = "position:relative; left:150px"
                 ),
                 br(),
                 br(),
                 br(),
                 
                 br(),
                 div(
                   splitLayout(style = "botder 1px solid silver",cellWidths = c("50%","25%","50%"),strong(h3("Carteira de Melhor Índice Sharpe")),NULL,strong(h3("Carteira de Menor Risco"))), 
                   splitLayout(style = "botder 1px solid silver",cellWidths = c("50%","25%","50%"),tableOutput("outTabelaMark"),NULL,tableOutput("outTabelaMark2")),
                   style = "position:relative; left:150px"
                 ),
                 br(),
                 br(),
                 br(),
                 plotOutput("outMark3"),
                 br(),
                 br(),
                 br(),
                 plotlyOutput("outMark4")
                 
               )
               
             )),
     tabItem(tabName = 'how_prediction',
             h3(style = "font-weight: bold","Como funciona a predição de um valor"),
             #Fazer depois
             ),
     tabItem(tabName = 'todo_prediction',
             h3(style = "font-weight: bold","Realizar uma predição"),
             fluidRow(column(3,
                             selectizeInput("inAtivoPredict",
                                         strong("Escolha um ativo:"),
                                         multiple = FALSE,
                                         choices=c(acoesDisponiveis)),
                             
                             actionButton(inputId="buttonPredict", label="Realizar", icon("paper-plane"), 
                                          style="color: #fff; background-color: #337ab7; border-color: #2e6da4")
                             
                             
                             )
                      
                      
                      
                      
             ),
             valueBoxOutput("outPredicao"),
             valueBoxOutput('outTendencia'),
             valueBoxOutput("outErroPredicao"),
             valueBoxOutput("outPriceOpen"),
             valueBoxOutput('outCloseAnt'),
             valueBoxOutput("outPriceAdjusted"),
             valueBoxOutput("outPriceHigh"),
             valueBoxOutput("outPriceLow"),
             valueBoxOutput("outVolume"),
             
             #("outRetClosingPrices"),
             
             ),
     
     tabItem(tabName = 'developers',
             h3(style = "font-weight: bold","Sobre os desenvolvedores"),
             sidebarLayout(
               
               sidebarPanel(
                 fluidRow(
                   column(6, 
                          #h4(strong("Desenvolvedor:")),
                          img(src = "joao.png", height = 150, width = 150, align = "center",style = "border-radius:50%"),
                          br(),
                          em(strong("João Victor M. Souza")),
                          br(),
                          p(style = "text-align: justify;","Graduando em Ciência da Computação."),
                          p(style = "text-align: justify;","Universidade
                                Federal de Viçosa - Campus UFV - Florestal."),
                          br(),
                          icon("at"),
                          #em("   JoaoVictorMagalhaesSouza@gmail.com"),
                          a(href = "JoaoVictorMagalhaesSouza@gmail.com",em("E-mail")),
                          br(),
                          icon("instagram"),
                          a(href = "https://www.instagram.com/joaovictormagalhaessouza/",em("Instagram")),
                          br(),
                          icon("github"),
                          a(href = "https://github.com/JoaoVictorMagalhaesSouza",em("GitHub")),
                          br(),
                          icon("briefcase"),
                          a(href="https://joaovictormagalhaessouza.github.io/", em("Página Pessoal"))
                   ),
                   column(6, 
                          img(src = "Fernando.jpg", height = 150, width = 150, align = "center",style = "border-radius:50%"),
                          br(),
                          em(strong("Fernando de Souza Bastos")),
                          br(),
                          p(style = "text-align: justify;","Doutor em Estatística."),
                          p(style = "text-align: justify;","Professor da Universidade
                                Federal de Viçosa - Campus UFV - Florestal."),
                          br(),
                          icon("at"),
                          a(href = "fernando.bastos@ufv.br",em("E-mail")),
                          br(),
                          icon("instagram"),
                          a(href = "https://www.instagram.com/fsbmat/",em("Instagram")),
                          br(),
                          icon("github"),
                          a(href = "https://github.com/fsbmat-ufv",em("GitHub")),
                          br(),
                          icon("briefcase"),
                          a(href="https://fsbmat-ufv.github.io/", em("Página Pessoal"))
                   )
                 ),
                 
                 
                 width = 12),
               
               mainPanel()
             )
             
             
             )
     
     
     )
    
  )
)
)


