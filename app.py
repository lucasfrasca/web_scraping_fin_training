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
    # date1 = 0
    
    url = "https://br.financas.yahoo.com/quote/{}/history?period1={}&period2={}&interval=1d&filter=history&frequency=1d&includeAdjustedClose=true"
    
    # formatando o url da página que será acessada
    url = url.format(ticker, date1, date2)
    
    # Instância do navegador
    opt = webdriver.ChromeOptions()
    opt.headless = True #não mostrar a ação em andamento 
    ser = Service(r'C:\Program Files (x86)\Google\Chrome\Application\97.0.4692.99\chromedriver.exe')
    driver = webdriver.Chrome(service=ser, options=opt)
    
    driver.get(url)
    
    time.sleep(5)
    
    html = driver.find_element(By.TAG_NAME, 'html')
    
    # posição do inicial do scroll
    last_height = driver.execute_script("return document.body.scrollHeight")
    print("last_height: {}".format(last_height))
    
    while (True):
        # posiciona o scroll no final da página
        html.send_keys(Keys.END)
        
        # pausa para carregar a página
        time.sleep(1)
    
        # atualiza a posição do scroll 
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        print("new_height: {}".format(new_height))
        
        # verifica se houve movimento da página 
        if (new_height == last_height):
            # termina o loop
            break
        else:
            # atualiza o último valor 
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
    
    df_not_related = pd.DataFrame(tuplas_eventos, columns=['Data', 'Valor', 'Tipo'])
    
    # Tratando o DataFrame de preços de ações 
    # converte a última coluna para inteiro substituindo o ponto
    df_data_stocks["Volume"] = df_data_stocks['Volume'].apply(lambda x: int(x.replace(".","")) if x != "-" else x)
    
    # laço para substituir os pontos por vírgulas 
    for coluna in df_data_stocks.columns[1:6]:
        df_data_stocks[coluna] = df_data_stocks[coluna].apply(lambda x: float(x.replace(",",".")) if x != '-' else x)
    
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
        df_param = pd.DataFrame(rows_separate, columns = ['Código do fundo', 
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
                                                          'Quantidade de ativos'])
        
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

# Iniciando o Dash
st.set_page_config(layout="wide")

# Fazendo a leitura dos tickers das ações 
columns = ['Empresa', 'Sigla','Setor']
df_stocks = pd.DataFrame(read_csv_file("empresas_listadas.csv"), columns=columns) 

# Fazendo a leitura dos tickers dos fundos imobiliários 
columns = ['Sigla','Setor']
df_fiis = pd.DataFrame(read_csv_file("fundos_listados.csv"), columns=columns) 

# Ajustando as listas com os nomes das empresas e fundos
list_stocks = df_stocks[['Empresa','Sigla']].values.tolist()
list_fiis = df_fiis['Sigla'].values.tolist()

# Ajustando as opções para o selectbox
options = [e[1] + " (" + e[0] + ")" for e in list_stocks] #inserindo lista de ações
options = options + list_fiis #inserindo a lista de fiis
options.sort()

st.title('Dashboard Financeiro')

st.sidebar.selectbox("Selecione o símbolo da empresa ou fundo:", options, key='name')

# st.sidebar.subheader('Selecione a filtragem de ativo')

st.sidebar.selectbox("Selecione a filtragem de ativo:", options=("Ações", "FIIs", None), index=2)

st.sidebar.selectbox("Selecione a filtragem por setor:", disabled=True, options=('Setor'))


ticker = st.session_state.name.split(" ")[0]

# Flag para verificar se está é um fundo ou uma ação selecionada
if_fund = ticker in list_fiis 

st.header(ticker + ' - Setor ' + get_asset_field(ticker, if_fund, df_fiis, df_stocks))

# Pegando dados históricos do site do Yahoo
try:
    with st.spinner('Carregando dados. Aguarde, por favor!'):
        dataframe = get_stock_data(ticker)
except Exception:
    print("Erro na raspagem do Yahoo")

# Tentando escrever o range de datas para o slider
try:
    # Pega o índice do dataframe e transforma em uma lista para opções
    options = [e.strftime(' %d/%m/%Y ') for e in dataframe.index.to_list()[::-1]]
    sldr_enabl = False
except Exception:
    # Cria um dataframe com um ano de datas e transforma em umaa lista
    options = pd.date_range(end = np.datetime64('today'), periods = 365)
    options = list(map(lambda x: x.strftime(' %d/%m/%Y '), options))
    sldr_enabl = True
    
# Inserindo slider de tempo
date_init, date_fin = st.select_slider('Selecione a data de pesquisa',
                                        options=options,
                                        value=(options[0],
                                               options[-1]),
                                        disabled=sldr_enabl)
# Insere o gráfico na página 
try:
    col1, col2 = st.columns([3,1])
    # Nome da empresa selecionada pelo ticker
    
    # Datas selecionadas, convertidas de string (%d/%m/%Y) para datetime64 (%Y-%m-%d)
    date_init = np.datetime64("-".join(date_init.replace('/','-').strip().split('-')[::-1])) 
    date_fin = np.datetime64("-".join(date_fin.replace('/','-').strip().split('-')[::-1]))
    
    # Selecionando o dataframe
    dataframe_aux = dataframe[(dataframe.index >= date_init) &
                              (dataframe.index <= date_fin)].copy()
    
    # Monta a figura
    fig = go.Figure(data=[go.Candlestick(x=dataframe_aux.index,
                    open=dataframe_aux['Abrir'], high=dataframe_aux['Alto'],
                    low=dataframe_aux['Baixo'], close=dataframe_aux['Fechamento*'])])
    
    fig.update_layout(xaxis_rangeslider_visible=False) #retira a tabela abaixo
    # fig.update_layout(width=1000, height=500) 
    col1.plotly_chart(fig, use_container_width=True) #desenha o gráfico na página
    
    stock_price = "R$ " + str(dataframe_aux['Fechamento ajustado**'][0]).replace('.', ',')
    delta_price = str(round(100 * ((dataframe_aux['Fechamento ajustado**'][0] - dataframe_aux['Fechamento ajustado**'][-1]) \
                             / dataframe_aux['Fechamento ajustado**'][-1]), 2)).replace('.', ',') + "%" 
    
    col2.metric(" ", "", "") #espaço
    col2.metric("", "", "")  #espaço
    col2.metric(" ", "", "") #espaço
    col2.metric("", "", "")  #espaço
    col2.metric("Preço:", stock_price, delta_price)
    # col2.metric(" ", "", "") #espaço
    # col2.metric("", "", "")  #espaço
    # col2.metric("Teste:", "R$ 20,00", "-2%")
except Exception:
    st.write("Não foi possível localizar o ativo")

try:
    param = get_parameter(ticker, if_fund)
except Exception:
    param = {}

# st.markdown("""
# <style>
# .big-font {
#     font-size:30px !important;
# }
# </style>
# """, unsafe_allow_html=True)

# st.markdown('<p class="big-font">Hello World !!</p>', unsafe_allow_html=True)

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
        col5.metric("Magic N.:", param["Magic Number"], "")
except Exception:
    print('Problema na exibição dos indicadores')
    pass

# dataframe[dataframe['Código do fundo'] == 'sbroule']["valor"]
# dataframe.loc[dataframe["Código do produto"] == "sbrouble", 'valor']



