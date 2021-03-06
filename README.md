<h1 align="center"> Raspagem de dados e dashboards no mercado financeiro </h1>

![foto-de-capa](https://user-images.githubusercontent.com/87511811/158238792-c221f46f-80bf-4ac2-8170-6d107c7105a5.png)

##
![Licença](https://img.shields.io/github/license/lucasfrasca/web_scraping_fin_training?style=flat-square)
![Languages](https://img.shields.io/github/languages/top/lucasfrasca/web_scraping_fin_training?style=flat-square)
![LangCount](https://img.shields.io/github/languages/count/lucasfrasca/web_scraping_fin_training?style=flat-square)

> Status do projeto: Concluído :ballot_box_with_check:

## Tópicos

:small_blue_diamond: [Descrição do projeto](#descrição-do-projeto) <br/>
:small_blue_diamond: [Organização: pastas e arquivos](#organização-pastas-e-arquivos) <br/>
:small_blue_diamond: [Funcionalidades da aplicação](#funcionalidades-da-aplicação) <br/>
:small_blue_diamond: [Acesso ao projeto e utilização](#acesso-ao-projeto-e-utilização) <br/> 
:small_blue_diamond: [Planos futuros](#planos-futuros) <br/>
:small_blue_diamond: [Referências](#referências) <br/>
:small_blue_diamond: [Autores](#autores) <br/>
:small_blue_diamond: [Licença](#licença) <br/>

## Descrição do projeto

O projeto consiste em uma ferramenta para visualização do histórico de cotação de ações e fundos de investimento imobiliários (FIIs) e os seus principais indicadores. A coleta dos dados é feita no momento da pesquisa a partir da raspagem de diversos sites, esses dados são pré-processados e utilizados para montar um dashboard interativo.

### Objetivo:

O objetivo do projeto foi concentrar a visualização dos dados em um único lugar, retirando a necessidade da abertura de vários sites para a pesquisa das informações referentes a um determinado ativo.
  
### Ferramentas utilizadas:

A principal ferramenta utilizada foi a linguagem de programação **Python**, versão 3.8, tanto para a extração dos dados, quanto para a apresentação das informações. Mas é importante destacar as bibliotecas essenciais para o desenvolvimento e utilização, são elas:

* Streamlit
* Plotly
* Selenium
* Requests
* Beautifulsoup
* time
* Numpy
* Pandas

O código do projeto utiliza webdriver do Google Chrome para interagir com as páginas, portanto duas ferramentas fundamentais são: o navegador Google Chrome e o driver com a versão coincidente à versão do navegador, por exemplo:

* Google [Chrome](https://www.google.com/intl/pt-BR/chrome/): Versão 99.0.4844.74 
* Google [ChromeDriver](https://chromedriver.chromium.org/downloads): Versão 99.0.4844.51 

### Sites utilizados:

* [Yahoo](https://br.financas.yahoo.com): foi utilizado para a obtenção dos históricos das cotações das ações e dos fundos imobiliários;
* [Status Invest](https://statusinvest.com.br): foi utilizado para a obtenção do indicadores fundamentalistas das ações;
* [Funds Explorer](https://www.fundsexplorer.com.br): foi utilizado para a obtenção dos indicadores referentes aos FIIs;
* [Infomoney](https://www.infomoney.com.br): foi utilizado para a obtenção das ações e dos FIIs listados na B3.

## Organização: pastas e arquivos

As pastas do projeto estão divididas conforme o esquema a seguir:

![pasta_e_arquivos](https://user-images.githubusercontent.com/87511811/158664315-6a167140-65de-4250-9e88-6d404837edee.png)

A pasta **browser** contém o driver do Google Chrome utilizado pelo Selenium para interagir com as páginas web. Na pasta **data** se encontram os arquivos que são lidos durante a execução do aplicativo, dados estáticos para a decoração e elaboração das listas de pesquisa. O arquivo **app.py** contém todo o código destinado à elaboração do dashboard utilizando o Streamlit. O arquivo de Jupyter Notebook **Web_scraping_financial_data.ipynb** contém um resumo dos objetivos do projeto, todos os testes de raspagem que foram realizados e todas as análises.

## Funcionalidades da aplicação

Com o aplicativo é possível:
* Analisar ações e fundos imobiliários selecionando pelos filtros de dados;
* Visualizar o histórico das cotações de um determinado ativo em gráfico de vela;
* Filtrar o intervalo de tempo desejado para realizar a análise;
* Ver a cotação do dia e comparar em percentual com a cotação da última data selecionada;
* Visualizar os principais indicadores fundamentalistas do ativo.

Na imagem a seguir é possível observar no retângulo vermelho com número 1 os três filtros laterais, os quais são utilizados para selecionar os ativos a serem pesquisados e restringir a lista de ativos para um determinado tipo e setor. No retângulo de número 2 encontra-se o objeto que faz a seleção do intervalo de tempo em que a cotação do ativo será mostrada. O intervalo de tempo desse gráfico será de no máximo 5 anos, terminando no dia da pesquisa, esse período foi escolhido em virtude do tempo de raspagem.

![app_visao_geral_1](https://user-images.githubusercontent.com/87511811/158503864-666f7f3f-9a7f-43d8-bbff-74eb1fd1a810.png)

A barra lateral possui três filtros: o filtro mais inferior apresentará o símbolo dos ativos selecionando por *default* o primeiro ativo da lista em ordem alfabética; então, na primeira posição, segue um filtro de tipo de ativo, em que o usuário pode afunilar a busca escolhendo entre ação ou FII; em seguida é possível escolher o setor de atuação da empresa ou do fundo, porém este filtro só estará disponível se um tipo de ativo for selecionado. A sequência de imagens abaixo mostra o funcionamento desses filtros de dados:   

![side_bar](https://user-images.githubusercontent.com/87511811/158503896-9e0e8725-3200-4ef0-bb16-bf954e961f63.png)

O dashboard possui como elementos de análise um gráfico de vela delimitado pelo retângulo 1, sendo totalmente interativo, com deslocado nos eixos, *zoom* e etiqueta nos dados. No retângulo de número 2 é possível ver a cotação do dia e logo abaixo a variação percentual em relação ao preço do primeiro dia da janela temporal. O terceiro retângulo mostra alguns indicadores fundamentalistas para auxiliar na análise. 

![app_visao_geral_2](https://user-images.githubusercontent.com/87511811/158503871-bec046eb-3377-4902-b807-48619c9c3c56.png)

![acoes_gif](https://user-images.githubusercontent.com/87511811/158651217-9d6762b4-ab53-42b6-836f-9e433132114f.gif)

## Acesso ao projeto e utilização

É bem simples obter as pastas do projeto e utilizá-lo, porém é importante se atentar aos requisitos.

Para acessar o projeto basta clonar o repositório a partir do seu computador.
* No bash escreva: **git clone https://github.com/lucasfrasca/web_scraping_fin_training.git**

Para usar a aplicação abra o prompt e execute o comando **streamlit run app.py** de dentro do diretório do arquivo **app.py**, se for preciso use o comando **cd** acompanhado do caminho do arquivo para mudar de diretório, a imagem abaixo ilustra o procedimento.

![prompt](https://user-images.githubusercontent.com/87511811/158658881-983a3b1c-efb3-4e1e-9503-2af7591d6b72.PNG)

### Requisitos

Possuir as bibliotecas citadas instaladas no computador. Para isso pode-se utilizar o gerenciador de pacotes do Python (**pip**), digitando no prompt o comando **pip install** acrescido do nome da biblioteca, por exemplo: **pip install numpy**. 

É indispensável ter instalado no computardor o navegador Google Chrome e ter baixado o webdriver refente à versão do navegador. 

## Planos futuros

Como plano de melhoria e aprendizado pretende-se:
* Integrar os meios de raspagem com um banco de dados;
* Criar processo para a atualização diária dos dados;
* Disponibilizar o dashboard em produção, para que o usuário não precise ter contato com o código.

## Referências

Estes são os sites de referência:
* [Pandas](https://pandas.pydata.org/docs/)
* [Streamlit](https://docs.streamlit.io/)
* [Wigets](https://ipywidgets.readthedocs.io/en/latest/)
* [Beautifulsoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
* [Requests](https://docs.python-requests.org/en/latest/)
* [Flaticon](https://www.flaticon.com/authors/smashicons)

## Autores 

| [<img src="https://avatars.githubusercontent.com/u/87511811?v=4" width=115><br><sub> Lucas Frascarelli </sub>](https://github.com/lucasfrasca) | [<img src="https://avatars.githubusercontent.com/u/97852830?v=4" width=115><br><sub> Mateus V. Garcia </sub>](https://github.com/Mateus-V-Garcia) |
| :---: | :---: |

## Licença

[MIT License](LICENSE) (MIT)

Copyright :copyright: 2022 - web_scraping_fin_training
