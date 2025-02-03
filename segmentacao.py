import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO



#Configuração do layout da página
st.set_page_config(page_title="Segmentação RFM", layout="wide")


#Função de Carregamento dos dados
@st.cache_data 
def load_data(uploaded_file):
    if uploaded_file is not None:
        stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
        data = pd.read_csv(stringio, encoding="utf-8")
        
            
    else:
        data = pd.read_csv("Electronic_sales.csv")
        data = data.loc[data["Order Status"] == "Completed"]
        data.drop("Add-ons Purchased", axis=1, inplace=True)
        new_order = ["Customer ID","Purchase Date","Total Price"]
        data = data[new_order]

    return data
    

#Função Principal com o tratamento dos dados
@st.cache_resource
def process_data(data, coluna_id, coluna_data, coluna_monetario):
    data_referencia = pd.Timestamp.today()
    data.dropna(inplace=True)
    data[coluna_data] = pd.to_datetime(data[coluna_data])
    rfm = data.groupby(coluna_id).agg({
        coluna_data: lambda dates: (data_referencia - dates.max()).days,
        coluna_id: "count" if data[coluna_id].nunique()== 1  else "max",
        coluna_monetario: "sum" 
    })

    
    rfm.columns = ["Recencia_Ultima_Compra", "Num_Compras", "Valor_Gasto"]
    rfm["Recencia"] = pd.qcut(rfm["Recencia_Ultima_Compra"], q=3, labels=False, duplicates="drop")
    rfm["Recencia"] = 2 - rfm["Recencia"]
    rfm["Num_Compras"] = rfm["Num_Compras"].astype(float)
    if rfm["Num_Compras"].max()< 8.0:
        rfm["Frequencia"] = (rfm["Num_Compras"] / 4).astype(int)
    else:
        rfm["Frequencia"] = pd.qcut(rfm["Num_Compras"], q=2, labels=False, duplicates="drop")
    rfm["Monetario"] = pd.qcut(rfm["Valor_Gasto"], q=3, labels=False, duplicates="drop")
    rfm["RFM"] = rfm["Recencia"].astype(str) + rfm["Frequencia"].astype(str) + rfm["Monetario"].astype(str)
    
    #Mapeamento da segmentação
    mapeamento = {
        "000": "Hibernadores Econômicos", # Baixa frequência, recência e baixo valor
        "212": "Super Fãs", # Compram frequentemente com alto valor
        "202": "Campeões", # Compraram recentemente com alto valor mas não compram há algum tempo
        "102":"Potenciais Gastadores", # Média recência, baixa frequência e alto valor
        "112": "Fiéis", # Média recência, média frequência e alto valor
        "001": "Promissores", # Baixa recência, frequência e médio valor
        "002": "Gastadores Ocasionais", # Baixa recência e frequência mas alto valor
        "101": "Promissores Ocasionais", # Média recência, valor médio e baixa frequência
        "111": "Promissores", # Média recência, frequência e valor monetário
        "201": "Novos Entusiastas", # Compraram recentemente, com valor médio e baixa frequência
        "100": "Recentes Econômicos ", # Recência média, com baixa frequência e valor
        "200": "Novos Econômicos", # Clientes novos, valor e frequência baixos
        "211": "Engajados Promissores", # Compraram recentemente com frequência, valor médio
        "210": "Engajados Econômicos", # Compraram recentemente com frequência, valor baixo
        "012": "Ex-Campeões", # Frequência e valor altos mais baixa recência
        "110":"Economizadores"    # Média recência, alta frequência e valor baixo 
    }
    rfm["Segmentacao"] = rfm["RFM"].map(mapeamento)

    abordagens = {
    "000": "Oferecer promoções de entrada e/ou cupons de desconto progressivos para incentivar compras maiores",
    "001": "Enviar ofertas personalizadas com descontos atrativos em produtos populares.",
    "002": "Oferecer produtos premium com descontos exclusivos.",
    "012": "Reengajar com campanhas nostálgicas, lembrando bons momentos anteriores",
    "100": "Apresentar produtos de excelente custo-benefício. Oferecer facilidades de pagamento e destacar promoções atuais.",
    "101": "Enviar recomendações personalizadas com base em interesses passados. Oferecer descontos modestos para incentivar novas compras.",
    "102": "Destacar produtos de alto valor e qualidade premium.",
    "110": "Implementar programas de fidelidade para encorajá-los a aumentar a frequência de compras",
    "111": "Manter comunicação regular com novidades e ofertas especiais. Incentivar feedback para melhorar a experiência do cliente.",
    "112": "Reconhecer a lealdade com benefícios VIP. Oferecer atendimento prioritário e recompensas exclusivas.",
    "200": "Dar boas-vindas calorosas com ofertas de primeira compra. Apresentar a variedade de produtos e vantagens da marca.",
    "201": "Enviar conteúdos educacionais sobre os produtos. Oferecer amostras ou testes gratuitos para gerar interesse.",
    "202": "Oferecer recompensas por fidelidade e programas de indicação. Enviar convites para eventos exclusivos.",
    "210": "Incentivar com programas de pontos e descontos cumulativos. Destacar novos produtos que possam interessá-los.",
    "211": "Enviar ofertas baseadas em compras recentes e oferecer outros conteúdos relevantes .",
    "212": "Celebrar a parceria com experiências únicas. Oferecer previews exclusivos e personalização de produtos."
}

    rfm["Abordagem"] = rfm["RFM"].map(abordagens)

    
    
    return data, rfm


        


with st.sidebar.expander("Configurações Globais"):
    uploaded_file = st.file_uploader("Selecione o arquivo", type=["csv"])
    data = load_data(uploaded_file)
    coluna_data = st.selectbox("Selecione a coluna de Recência", data.columns, index=1 )
    coluna_id = st.selectbox("Selecione a coluna de Frequência", data.columns)
    coluna_monetario = st.selectbox("Selecione a coluna de Valor Monetário", data.columns, index=2)
    mapa_cores = st.selectbox("Selecione a palheta de cores ", ['viridis', 'plasma', 'magma', 'cividis',
                                                'turbo', 'Spectral', 'coolwarm', "coolwarm_r", 'twilight', 'cubehelix'], index=0)

    processar = st.button("Processar os dados")
if processar:
    data, rfm = process_data(data, coluna_id, coluna_data, coluna_monetario)
    
    
    tab1, tab2 = st.tabs(["Visualização Gráfica", "Abordagens e Download"])
    
    with tab1:
        col1, col2 = st.columns([0.5,0.5])
        with col1:
            fig, ax = plt.subplots()
            sns.countplot(data=rfm, x="Segmentacao", hue="Segmentacao", order=rfm["Segmentacao"].value_counts().index, ax=ax, palette=mapa_cores, legend=False)
            plt.title("Segmentação RFM")
            plt.xlabel("Segmentação dos Clientes")
            plt.ylabel("Contagem de Clientes por segmento")
            plt.xticks(rotation=45, ha="right")
            st.pyplot(fig)
            st.markdown("**Descrição:** O Gráfico acima mostra a distribuição de Clientes em cada segmento criado ")

        with col2:
            fig, ax = plt.subplots()
            corr = rfm[["Recencia", "Frequencia", "Monetario"]].corr()
            sns.heatmap(corr, annot=True, fmt=".2f",  ax=ax, linewidths=0.8, linecolor="black", cmap=mapa_cores)
            plt.title("Gráfico de Correlação RFM")
            st.pyplot(fig)
            st.markdown("**Descrição:** O Gráfico acima mostra o quanto a Recência, Frequência e Valor se influenciam")
                       

        with tab2:
            col1, col2= st.columns([0.4,0.6])
            with col1:
                st.write(rfm.drop(columns=["Recencia", "Frequencia", "Monetario"]).describe())
                st.markdown("**Descrição:** A tabela acima mostra um resumo estatístico da Recência, Frequência e Valor")

            with col2:
                st.markdown("""**Descrição:** O Dataframe abaixo contém os dados consolidados da segmentação, bem como a Segmentação e Abordagens Recomendadas - 
                             Abaixo também é possível fazer o download do arquivo como CSV  """)
                st.write(rfm)
                nome_arquivo = st.text_input("Digite o Nome do Arquivo CSV para fazer o download", value="Segmentacao.csv")
                st.download_button("Baixar Arquivo como csv", rfm.to_csv(index=False), nome_arquivo, "text/csv")
            
            

