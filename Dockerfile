FROM rocker/shiny-verse:latest
FROM python:3.9

WORKDIR /usr/local/bin

RUN apt-get update && apt-get install -y \
    sudo \
    pandoc \
    pandoc-citeproc \
    libcurl4-gnutls-dev \
    libcairo2-dev \
    libxt-dev \
    libssl-dev \
    libssh2-1-dev 

RUN apt-get update && \
    apt-get upgrade -y

RUN sudo apt-get install software-properties-common -y
RUN sudo apt install dirmngr gnupg apt-transport-https ca-certificates software-properties-common -y
RUN sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9
RUN sudo add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/' -y
RUN sudo apt install r-base -y

RUN sudo apt install default-jre -y
RUN sudo apt install default-jdk -y

RUN R -e "install.packages('shinydashboard', repos='http://cran.rstudio.com/')"
RUN sudo apt-get install r-cran-raster -y
RUN sudo apt-get install r-cran-devtools -y
RUN sudo apt-get install r-cran-magrittr -y
RUN R -e "install.packages(pkgs=c('shiny' ,'shinyjs' ,'shinyBS' ,'plotly' ,'shinythemes' ,'shinycssloaders' ,'RColorBrewer' ,'data.table' ,'tidyverse' ,'readr' ,'stringr' ,'plyr' ,'reshape2' ,'rsconnect' ,'pracma' ,'ggthemes' ,'lubridate' ,'GGally' ,'ggplot2' ,'viridis' ,'fPortfolio' ,'timeSeries' ,'dplyr' ,'dygraphs' ,'xts' ,'caret' ,'rpart.plot' ,'reticulate' ,'rjson','leaflet' ,'GetDFPData','shinydashboardPlus'), repos='https://cran.rstudio.com/')"
RUN R -e "devtools::install_github('msperlin/BatchGetSymbols')"
RUN sudo apt-get install r-cran-rjava -y
RUN sudo apt-get install r-cran-plotrix -y
RUN sudo apt-get install r-cran-fportfolio -y


COPY . .
# # install FreeTDS and dependencies
# RUN apt-get update \
#  && apt-get install unixodbc -y \
#  && apt-get install unixodbc-dev -y \
#  && apt-get install freetds-dev -y \
#  && apt-get install freetds-bin -y \
#  && apt-get install tdsodbc -y \
#  && apt-get install --reinstall build-essential -y

# # populate "ocbcinst.ini"
# RUN echo "[FreeTDS]\n\
# Description = FreeTDS unixODBC Driver\n\
# Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
# Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
# RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list
# RUN apt-get update
# RUN ACCEPT_EULA=Y apt-get -y install msodbcsql17
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt


EXPOSE 3838
CMD ["R", "-e", "shiny::runApp('/usr/local/bin', host = '0.0.0.0', port = 3838)"]
