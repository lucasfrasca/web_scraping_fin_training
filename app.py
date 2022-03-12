# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 17:06:42 2022

@author: User
"""
import streamlit as st
import numpy as np
import pandas as pd
import csv
import plotly.graph_objects as go
from PIL import Image

## Extraindo dados da web
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service



@st.cache(allow_output_mutation=True, show_spinner=False)
def get_stock_data(ticker):
    # Ajuste do url
    ticker = ".".join([ticker,'SA'])
    
    # selecionado a data do horizonte de busca de 5 anos 
    date2 = np.timedelta64(np.datetime64('today') - np.datetime64('1969-12-31'), 's').astype(int)
    date1 = date2 - 86400 * 365 * 5
    
    url = "https://br.financas.yahoo.com/quote/{}/history?period1={}&period2={}&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
    
    # formatando o url da página que será acessada
    url = url.format(ticker, date1, date2)
    
    # instância do navegador
    opt = webdriver.ChromeOptions()
    opt.headless = True #não mostrar a ação em andamento 
    ser = Service(r'browser\chromedriver.exe')
    driver = webdriver.Chrome(service=ser, options=opt)
    
    driver.get(url)
    
    time.sleep(4)
    
    html = driver.find_element(By.TAG_NAME, 'html')
    
    # posição do inicial do scroll
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while (True):
        # posiciona o scroll no final da página
        html.send_keys(Keys.END)
        
        # pausa para carregar a página
        time.sleep(1)
    
        # atualiza a posição do scroll 
        new_height = driver.execute_script(
            "return document.documentElement.scrollHeight"
        )
        
        # verifica se houve movimento da página 
        if (new_height == last_height):
            # termina o loop
            break
        else:
            # atualiza o último valor da posição do scroll 
            last_height = new_height         
    
    element = driver.find_element(By.TAG_NAME, 'table')
    html_content = element.get_attribute('outerHTML')
    
    driver.quit()
    
    # Código HTML da tabela
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Tratando o HTML para gerar a tabela de hostórico do preço da ação
    # lista para armazenar o dados que não sejam relacionados com o preço da ação (dividendo e desdobramento)
    list_not_related = [] #lista com conteúdo não relacionado com o preço das ações
    tuplas_eventos = [] #tuplas data, valor, ocorrencia (dividendo e desdobramento)
    for element in soup.find_all('td',"Ta(start) Py(10px)"):
        list_not_related.append(element)
        tuplas_eventos.append((element.previous_element, element.find('strong').string, element.find('span').string))
    
    linhas_tab = [] #lista para armazenar os dados das linhas da tebela
    # retira os strings que acompanham as classes selecionadas e filtra os casos não requeridos
    for element in soup.find_all(['td', 'th']):
        if element in list_not_related:
            del(linhas_tab[-1]) #deleta o elemento anterior
        else:
            linhas_tab.append(element.string)
            
    new_lista = list(filter(None, linhas_tab)) #retira os Nones se existirem
    stock_data = list(zip(*[iter(new_lista)]*7)) #empacota em listas de 7 elementos 
    
    df_data_stocks = pd.DataFrame(stock_data[1:], columns=stock_data[0][0:7]) 
    
    # df_not_related = pd.DataFrame(tuplas_eventos, columns=['Data', 'Valor', 'Tipo'])
    
    # Tratando o DataFrame de preços de ações 
    # converte a última coluna para inteiro substituindo o ponto
    df_data_stocks["Volume"] = df_data_stocks['Volume'].apply(lambda x: int(x.replace(".","")) if x != "-" else x)
    
    # laço para substituir os pontos por vírgulas 
    for coluna in df_data_stocks.columns[1:6]:
        df_data_stocks[coluna] = df_data_stocks[coluna].apply(lambda x: float(x.replace(".","").replace(",",".")) if x != '-' else np.nan)
    
    df_data_stocks.dropna(axis=0, how='any', inplace=True)
    
    # dicionário para auxiliar na correção das datas
    dicio = {"jan.": "01",
             "fev.": "02",
             "mar.": "03",
             "abr.": "04",
             "mai.": "05",
             "jun.": "06",
             "jul.": "07",
             "ago.": "08",
             "set.": "09",
             "out.": "10",
             "nov.": "11",
             "dez.": "12"}
    
    # ordenando cada data por Ano-mês-dia, substituindo o nome do mês pelo número correspondente e convertendo para datetime64
    df_data_stocks["Data_Time"] = pd.to_datetime(df_data_stocks["Data"].apply(lambda x: x.split(' ')[0:6:2][::-1]).\
                                                 apply(lambda x: "".join([x[0], dicio[x[1]], x[2]])), 
                                                 format='%Y-%m-%d')
    
    # rearanjando as colunas do dataframe
    cols = df_data_stocks.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df_data_stocks = df_data_stocks[cols]
    df_data_stocks.index = df_data_stocks['Data_Time'] #faz o índice virar a coluna data_time
    df_data_stocks.drop(labels='Data_Time', axis=1, inplace=True)
    
    return df_data_stocks

@st.cache(allow_output_mutation=True, show_spinner=False)
def get_parameter(ticker, flag):
    """
    O ticker será inserido na pesquisa do ativo e a flag indicará o tipo de ativo 
    """
    headers = {'User-Agent':'Mozilla/5.0'}
    params = {}
    if not flag: #ação
        # Aquisição do HTML
        url_stock = 'https://statusinvest.com.br/acoes/{}'
        url_stock = url_stock.format(ticker)
        
        url_requests = requests.get(url_stock, headers = headers)
        soup = BeautifulSoup(url_requests.text, 'html.parser')
        
        # Localização dos dados alvo
        lista_recebe_alvos = []
        for i in soup.find_all('div', 'info special w-100 w-md-33 w-lg-20'):
            lista_recebe_alvos.append((i.find('h3').string, i.find('strong').string))
                
        for i in soup.find_all('div',{'title':'Valorização no preço do ativo com base nos últimos 12 meses'}):
            lista_recebe_alvos.append((i.find('h3').string, i.find('strong').string))
        
        for i in soup.find_all('div',["w-50 w-sm-33 w-md-25 w-lg-50 mb-2 mt-2 item",'w-50 w-sm-33 w-md-25 w-lg-16_6 mb-2 mt-2 item']):
            lista_recebe_alvos.append((i.find('h3').string,i.find('strong').string))
        
        df_param = pd.DataFrame(lista_recebe_alvos, columns = ['Indicador','Valor'])
        
        # Separando os indicadores desejados 
        params['Acao'] = ticker
        params['ROE'] = df_param.loc[df_param['Indicador'].isin(['ROE']), "Valor"].item()
        params['ROIC'] = df_param.loc[df_param['Indicador'].isin(['ROIC']), "Valor"].item()
        params['Liq. corrente'] = df_param.loc[df_param['Indicador'].isin(['Liq. corrente']), "Valor"].item()
        params['M. Líquida'] = df_param.loc[df_param['Indicador'].isin(['M. Líquida']), "Valor"].item()
        params['CAGR Receitas 5 anos'] = df_param.loc[df_param['Indicador'].isin(['CAGR Receitas 5 anos']), "Valor"].item()
        params['P/L'] = df_param.loc[df_param['Indicador'].isin(['P/L']), "Valor"].item()
    else: #fundo
        url_FII = 'https://www.fundsexplorer.com.br/ranking'
        lendo_url = requests.get(url_FII, headers = headers)
        
        soup = BeautifulSoup(lendo_url.content,'html.parser')
        
        rows = []
        for i in soup.find_all('td'):
            rows.append(i.string)
        
        indice = 0
        rows_separate = []
        while indice < len(rows):
            lista_provisoria = []
            for i in range(indice, indice + 25):
                lista_provisoria.append(rows[i])
            rows_separate.append(lista_provisoria)
            indice += 26
        
        # Criando o dataframe
        df_param = pd.DataFrame(
            rows_separate,
            columns = ['Código do fundo', 
                       'Setor', 'Preço atual',
                       'Liquidez','Dividendo',
                       'Dividend Yield','DY 3M',
                       'DY 6M','DY 12M',
                       'DY 3M media',
                       'DY 6M media',
                       'DY 12M media',
                       'DY ANO',
                       'Variação Preço',
                       'Rentab. Período',
                       'Retab. Acum.',
                       'Patrimônio Líq.',
                       'VPA','P/VPA',
                       'DY PATR.',
                       'Varia. Patri.',
                       'Rentab. Patr.', 
                       'Vacância Física',
                       'Vacância Financeira',
                       'Quantidade de ativos'
            ]
        )   
        
        df_param.index = df_param["Código do fundo"]
        df_param.drop(labels='Código do fundo', axis=1, inplace=True)
        
        # Separando os indicadores desejados 
        params['FII'] = ticker
        params['Preço'] = df_param['Preço atual'][ticker]
        params['DY 12 M'] = df_param['DY 12M'][ticker]
        params['Vacância Financeira'] = df_param['Vacância Financeira'][ticker]
        params['P/VPA'] = df_param['P/VPA'][ticker] 
        params['Dividendo'] = df_param['Dividendo'][ticker]
        den = float(df_param['Dividendo'][ticker].replace('R$ ','').replace(',','.'))
        num = float(df_param['Preço atual'][ticker].replace('R$ ','').replace(',','.'))
        params['Magic Number'] = str(round(num/den, 2)).replace('.',',') if den != 0.0 else 'N/A'
    
    return params

@st.cache(allow_output_mutation=True, show_spinner=False)
def read_csv_file(file_path):
    output_list = []
    
    with open(file_path, mode='r', newline='\n') as csv_file:
        # Cria o ponteiro para a escrita do arquivo
        reader = csv.reader(csv_file)
        
        # Transfere as linhas para a lista
        for line in reader:
            output_list.append(line)
    
    return output_list

@st.cache(allow_output_mutation=(True), show_spinner=False)
def get_asset_field(ticker, flag, df_fiis, df_stocks): 
    # Verificando o tipo de ativo
    if flag:
        return df_fiis[df_fiis['Sigla'] == ticker]['Setor'].item()
    else:
        return df_stocks[df_stocks['Sigla'] == ticker]['Setor'].item()

@st.cache(allow_output_mutation=(True), show_spinner=False)
def get_list_asset_field(type_filter, df_fiis, df_stocks): 
    # Verifica o tipo de ativo selecionado
    if type_filter == "FIIs":
        aux = pd.unique(df_fiis['Setor'].sort_values()).tolist()
        return aux
    elif type_filter == "Ações":
        aux = pd.unique(df_stocks['Setor'].sort_values()).tolist()
        return aux 
    else:
        return ["Todos"]

@st.cache(allow_output_mutation=(True), show_spinner=False)
def define_options(asset_type, asset_field, df_fiis, df_stocks):
    # Inicializando variáveis 
    list_stocks = []
    list_fiis = []
    
    # verificando se é ação ou fundo
    if asset_type == "FIIs":
        if asset_field != "Todos":
            # caso seja um setor específico
            df_temp = df_fiis.groupby(by='Setor')['Sigla'].get_group(asset_field)
        else:
            # caso sejam desejados todos os grupos
            df_temp = df_fiis['Sigla']
        list_fiis = df_temp.values.tolist()
    elif asset_type == "Ações":
        # verificando o setor da ação
        if asset_field != "Todos":
            # caso seja um grupo específico
            df_temp = df_stocks.groupby(by='Setor')[['Empresa','Sigla']].get_group(asset_field)
        else:
            # caso sejam desejados todos os grupos
            df_temp = df_stocks[['Empresa', 'Sigla']]
        list_stocks = df_temp.values.tolist()
    else:
        list_fiis = df_fiis['Sigla'].values.tolist()
        list_stocks = df_stocks[['Empresa','Sigla']].values.tolist()
    
    # Ajustando as opções para a saída 
    # inserindo lista de ações caso ela não seja nula
    options = [e[1] + " (" + e[0] + ")" for e in list_stocks] if bool(list_stocks) else [] 
    # concatenando a lista de fiis se ela não for nula
    options = options + list_fiis if bool(list_fiis) else options 
    options.sort() #ordenando alfabeticamente
    
    return options

# Iniciando o Dash com layout longo
st.set_page_config(layout="wide")

# Fazendo a leitura dos tickers das ações 
columns = ['Empresa', 'Sigla', 'Setor']
df_stocks = pd.DataFrame(
    read_csv_file("data\\csvs\\empresas_listadas.csv"),
    columns=columns
) 

# Fazendo a leitura dos tickers dos fundos imobiliários 
columns = ['Sigla', 'Setor']
df_fiis = pd.DataFrame(
    read_csv_file("data\\csvs\\fundos_listados.csv"), 
    columns=columns
) 

# Ajustando as listas com os nomes das empresas e fundos
list_stocks = df_stocks[['Empresa','Sigla']].values.tolist()
list_fiis = df_fiis['Sigla'].values.tolist()

# Dividindo a parte superior em 3 colunas
col1, col2, col3 = st.columns([0.2,1,3])
col1.metric(" ", "", "") #apenas para ocupar espaço
image = Image.open("data\\imgs\\stock-market.png")
col2.image(image, width=128) #inserindo logo
col3.title('Dashboard Financeiro') #título

# Mudando a CSS da barra lateral e dos labels dos objetos selectbox
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 300px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 300px;
        margin-left: -300px;
    }
    [class="css-16huue1 effi0qh0"] {
        font-size:18px !important;
    }
    [class="css-3snfz0 effi0qh0"] {
        font-size:18px !important;
    }
    [class="block-container css-18e3th9 egzxvld2"] {
        padding-top:40px !important;
    }
    [class="css-sygy1k e1fqkh3o1"] {
        padding-top:25px !important;
    }
    [class="css-e370rw e19lei0e0"] {
        visibility: hidden !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header('Filtragem de dados')

########################### Filtro de tipo de ativo ###########################
st.sidebar.selectbox("Selecione o tipo de ativo:",
                     options=('Todos',"Ações", "FIIs"),
                     key='type_filter',
                     index=0,
                     disabled=False)

########################## Filtro de setor de ativo ###########################
is_type_filter_off = True if st.session_state.type_filter =='Todos' else False
options = ['Todos'] + get_list_asset_field(st.session_state.type_filter,
                                           df_fiis,
                                           df_stocks)

st.sidebar.selectbox('Selecione o setor do ativo:',
                      options=options,
                      key='field_filter',
                      index=0,
                      disabled=is_type_filter_off)

########################## Filtro de seleção de ativo #########################
options = define_options(st.session_state.type_filter,
                         st.session_state.field_filter,
                         df_fiis,
                         df_stocks)

st.sidebar.selectbox("Selecione o símbolo do ativo:",
                     options=options, 
                     key='ticker_filter')

# Corrigindo o string retornado pelo filtro de seleção 
ticker = st.session_state.ticker_filter.split(" ")[0]

# Flag para verificar se foi selecionada um fundo ou uma ação 
if_fund = ticker in list_fiis 

st.header(ticker + ' - Setor ' + get_asset_field(ticker, if_fund, df_fiis, df_stocks))

# Pegando dados históricos do site do Yahoo
try:
    with st.spinner('Carregando dados. Aguarde, por favor!'):
        dataframe = get_stock_data(ticker)
except Exception:
    print("Erro na raspagem do Yahoo")

# Escrevendo o range de datas para o slider
try:
    # pega o índice do dataframe e transforma em uma lista para opções
    options = [e.strftime(' %d/%m/%Y ') for e in dataframe.index.to_list()[::-1]]
    sldr_enabl = False
    # caso o dataframe venha com apenas uma linha
    if options[0] == options[-1]: 
        # cria um dataframe com um ano de datas e transforma em umaa lista
        options = pd.date_range(end = np.datetime64('today'), periods = 365)
        options = list(map(lambda x: x.strftime(' %d/%m/%Y '), options))
        sldr_enabl = True
except Exception:
    # cria um dataframe com um ano de datas e transforma em umaa lista
    options = pd.date_range(end = np.datetime64('today'), periods = 365)
    options = list(map(lambda x: x.strftime(' %d/%m/%Y '), options))
    sldr_enabl = True
    
# Inserindo slider de tempo
date_init, date_fin = st.select_slider('Selecione a data de pesquisa',
                                        options=options,
                                        value=(options[0],
                                               options[-1]),
                                        disabled=sldr_enabl)

# Insere o gráfico na página e o indicador de preço 
try:
    # divide uma coluna para o gráfico e outra para o indicador
    col1, col2 = st.columns([3,1])
    
    # datas selecionadas, convertidas de string (%d/%m/%Y) para datetime64 (%Y-%m-%d)
    date_init = np.datetime64("-".join(date_init.replace('/','-').strip().split('-')[::-1])) 
    date_fin = np.datetime64("-".join(date_fin.replace('/','-').strip().split('-')[::-1]))
    
    # selecionando o dataframe
    dataframe_aux = dataframe[(dataframe.index >= date_init) &
                              (dataframe.index <= date_fin)].copy()
    
    fig = go.Figure(
        data=[go.Candlestick(
            x=dataframe_aux.index,
            open=dataframe_aux['Abrir'], high=dataframe_aux['Alto'],
            low=dataframe_aux['Baixo'], close=dataframe_aux['Fechamento*']
        )],
        layout_yaxis_range=[0, dataframe_aux['Alto'].max()]
    )
    
    fig.update_layout(xaxis_rangeslider_visible=False) #retira a tabela abaixo
    
    # desenha o gráfico na página
    col1.plotly_chart(fig, use_container_width=True) 
    
    stock_price = "R$ " + str(dataframe_aux['Fechamento ajustado**'][0]).replace('.', ',')
    delta_price = str(
        round(
            100 * ((dataframe_aux['Fechamento ajustado**'][0]     \
                    - dataframe_aux['Fechamento ajustado**'][-1]) \
                    / dataframe_aux['Fechamento ajustado**'][-1]),
            2
        )
    ).replace('.', ',') + "%" 
    
    col2.metric(" ", "", "") #espaço
    col2.metric("", "", "")  #espaço
    col2.metric(" ", "", "") #espaço
    col2.metric("", "", "")  #espaço
    col2.metric("Preço:", stock_price, delta_price)
except Exception:
    st.write("Não foi possível exibir o gráfico do ativo")

try:
    param = get_parameter(ticker, if_fund)
except Exception:
    param = {}

try:
    if not if_fund: 
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("ROE:", param["ROE"], "")
        col2.metric("ROIC:", param["ROIC"], "")    
        # col3.metric("Liquidez:", param["Liq. corrente"], "")
        col3.metric("M. Líquida:", param["M. Líquida"], "")
        col4.metric("CAGR:", param["CAGR Receitas 5 anos"], "")
        col5.metric("P/L:", param["P/L"], "")
    else:
        print(param["DY 12 M"])
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("DY 12 M:", param["DY 12 M"], "")    
        col2.metric("Liquidez:", param["Vacância Financeira"], "")
        col3.metric("P/VPA:", param["P/VPA"], "")
        col4.metric("Dividendo:", param["Dividendo"], "")
        col5.metric("Magic Number:", param["Magic Number"], "")
except Exception:
    print('Problema na exibição dos indicadores')
    pass



