import streamlit as st
import pandas as pd  
import plotly.express as px
from prophet import Prophet


st.markdown(
    """
    <style>
    .reportview-container{
    background-color: #f0f2f6;
    padding: 10px;
    }

    h1{
    color:#2E4053;
    font-family: 'Arial Black', sans-serif;
    }

    .stPlotlyChart{
    margin: 20px 0;
    padding: 10 px;
    border-radius: 10px;
    background-color: #fffff;
    box-shadow: 0px 4px 12px rgba(0,0,0, 0.1);
    }
    .css-1lcbmhc.e1fqkh3o1{
    display:flex;
    justufy-content: center;
    margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    """
    <div style="background-color: #2E4053; padding: 10px;">
    <h1 style="color:white; text-aling: center;"> Dashboard de Vendas E-commerce</h1>
    </div>

    """, unsafe_allow_html=True

)

df = pd.read_csv('data.csv', encoding='ISO-8859-1')


df['total'] = df["Quantity"] * df['UnitPrice']
vendas_por_pais = df.groupby('Country')['total'].sum().reset_index()

fig = px.bar(vendas_por_pais, x='Country', y='total', title = 'Vendas Totais por País')

#exibir o gráfico]
st.plotly_chart(fig)

paises = df['Country'].unique()
pais_selecionado = st.selectbox('Selecione um país', paises)

#filtrar dados 
df_filtrado = df[df['Country']== pais_selecionado]

#exibir vendas 
vendas_por_pais_selecionado = df_filtrado.groupby('Country')['total'].sum().reset_index()
st.write(f"Vendas Totais no {pais_selecionado}:")
st.write(vendas_por_pais_selecionado)

# Converter a coluna para o formato de data
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Criar uma nova coluna com o mês/ano da transação (e converter para string)
df['YearMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)

# Calcular vendas por mês
vendas_mensais = df.groupby('YearMonth')['total'].sum().reset_index()

# Gráfico de vendas por mês
fig_mensal = px.line(vendas_mensais, x='YearMonth', y='total', title='Vendas por Mês')

st.plotly_chart(fig_mensal)

#agrupar as vendas por cliente
vendas_por_cliente = df.groupby('CustomerID')[ 'total'].sum().reset_index()

#exibir o top 10 clientes
top_clientes = vendas_por_cliente.sort_values(by='total', ascending=False).head(10)

#grafico 
fig_clientes = px.bar(top_clientes, x='CustomerID', y='total', title='Top 10 Clientes Mais Lucrativos')

st.plotly_chart(fig_clientes)

#calculo de metricas e mostrar os valores do dashboard
total_vendas = df ['total'].sum()
num_transacoes = df['InvoiceNo'].nunique()
ticket_medio = total_vendas / num_transacoes

st.metric(label="Total de Vendas", value = f"R${total_vendas:,.2f}")
st.metric(label="Número de Transações", value=num_transacoes)
st.metric(label="Ticket Médio", value=f"R${ticket_medio:,.2f}")

#grafico dos produtos mais vendidos

produtos_mais_vendidos = df.groupby('StockCode')['Quantity'].sum().reset_index()
top_produtos = produtos_mais_vendidos.sort_values(by='Quantity',ascending=False).head(10)
fig_produtos = px.bar(top_produtos, x='StockCode', y='Quantity' , title="Top 10 Produtos Mais Vendidos")

st.plotly_chart(fig_produtos)

#Filtros para ajudar a interatividade da pagina 

data_inicial=st.date_input('Data Inicial', df['InvoiceDate'].min().date())
data_final=st.date_input('Data Final', df['InvoiceDate'].max().date())

df_filtrado_data = df[(df['InvoiceDate'] >= pd.to_datetime(data_inicial)) & (df['InvoiceDate']<= pd.to_datetime(data_final))]

vendas_filtradas = df_filtrado_data.groupby('YearMonth')['total'].sum().reset_index()

fig_vendas_filtradas = px.line(vendas_filtradas, x='YearMonth', y='total', title='Vendas por Mês (Filtrado)')

#renomeando as colunas 

vendas_mensais.rename(columns={'YearMonth': 'ds', 'total': 'y'}, inplace=True)

modelo=Prophet()
modelo.fit(vendas_mensais)

futuro = modelo.make_future_dataframe(periods=12, freq='M')

#fazer previsão

previsao = modelo.predict(futuro)
fig_previsao = modelo.plot(previsao)
st.write("Previsão de Vendas para os Próximos 12 Meses")
st.plotly_chart(fig_previsao)
