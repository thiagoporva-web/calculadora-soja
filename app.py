import streamlit as st
import datetime

# --- CONFIGURAÇÃO DA PÁGINA E LOGO ---
st.set_page_config(page_title="Formação de Preço", page_icon="🌾")

# Tenta carregar o logo (ajuste "logo.png" para o nome exato do arquivo que você subiu)
try:
    st.image("logo.png", width=250)
except:
    pass # Se a imagem não for encontrada, ele simplesmente segue o código

st.title("Formação de Preço")


# --- 1. DADOS DO ADMINISTRADOR (Menu Lateral) ---
st.sidebar.header("⚙️ Parâmetros Admin")
st.sidebar.caption("Pode inserir em % (ex: digite 5 para 5%)")

# Note que adicionei o "/ 100" no final das variáveis de porcentagem
curva_dolar = st.sidebar.number_input("Curva Dólar (%)", value=8.10, format="%.2f") / 100
custo_fin_aa = st.sidebar.number_input("Custo Financeiro a.a. (%)", value=7.20, format="%.2f") / 100
custo_fin_am = st.sidebar.number_input("Custo Financeiro a.m. (%)", value=1.24451, format="%.2f") / 100
quebra = st.sidebar.number_input("Quebra (%)", value=0.25, format="%.2f") / 100

# Estes continuam normais pois são valores financeiros/dias, e não porcentagens
impostos = st.sidebar.number_input("Impostos ($ ou R$)", value=1.70, format="%.2f")
custo_porto = st.sidebar.number_input("Custo Porto", value=8.50, format="%.2f")
margem = st.sidebar.number_input("Margem", value=5.00, format="%.2f")
dias_a_partir = st.sidebar.number_input("Número de dias a partir", value=30, step=1)



# --- 2. DADOS DO COMPRADOR (Tela Principal) ---
st.header("Preencha os Dados")

col1, col2 = st.columns(2) # Cria duas colunas para o layout ficar mais bonito
with col1:
    cambio = st.number_input("Câmbio", value=5.00, format="%.4f")
    cotacao_cbot = st.number_input("Cotação Cbot", value=1200.00, format="%.2f")
    premio = st.number_input("Prêmio", value=10.00, format="%.2f")
    frete = st.number_input("Frete", value=50.00, format="%.2f")

with col2:
    hoje = datetime.date.today()
    # Adicionamos o format="DD/MM/YYYY" para ficar no padrão brasileiro
    data_final_entrega = st.date_input("Data Final Entrega", hoje, format="DD/MM/YYYY")
    data_pagamento = st.date_input("Data Pagamento", hoje, format="DD/MM/YYYY")



# --- 3. ÁREA DE CÁLCULOS (O "Cérebro") ---
# Diferença de dias
dias_hoje_pagamento = (data_pagamento - hoje).days
dias_entrega_pagamento = (data_pagamento - data_final_entrega).days

# Fórmulas sequenciais
usd_pagamento = ((1 + curva_dolar) ** (dias_hoje_pagamento / 360)) * cambio
flat_pgua = ((cotacao_cbot + premio) * 0.367454) - custo_porto - margem
liquido_pgua = (usd_pagamento * 0.06) * flat_pgua
preco_bruto_sem_fin = (liquido_pgua * (1 - quebra)) - (frete * 0.06) - impostos

# A lógica do "SE" do Excel transformada em Python
if dias_entrega_pagamento >= dias_a_partir:
    # Cenário Verdadeiro
    preco_bruto = ((custo_fin_aa / 360) * (dias_entrega_pagamento - dias_a_partir) + 1) * preco_bruto_sem_fin
else:
    # Cenário Falso
    preco_bruto = preco_bruto_sem_fin * (1 - (custo_fin_am / 30) * (30 - dias_entrega_pagamento))


# --- 4. RESULTADO FINAL NA TELA ---
st.markdown("---")
st.header("Resultado Final")

# Formatar o número para o padrão de moeda (trocando pontos e vírgulas)
preco_bruto_formatado = f"{preco_bruto:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Mostra o preço com destaque já em R$
st.metric(label="Preço Bruto", value=f"R$ {preco_bruto_formatado}")

# --- BOTÃO DE COPIAR PARA WHATSAPP ---
st.write("📄 **Resumo para copiar:**")
texto_para_copiar = f"""Data de Entrega: {data_final_entrega.strftime('%d/%m/%Y')}
Data de Pagamento: {data_pagamento.strftime('%d/%m/%Y')}
Preço Bruto: R$ {preco_bruto_formatado}"""

st.code(texto_para_copiar, language="text")

# --- DETALHES INTERMEDIÁRIOS ---
with st.expander("Ver detalhes dos cálculos intermediários"):
    st.write(f"**Número de dias hoje/pagamento:** {dias_hoje_pagamento}")
    st.write(f"**Número de dias entrega/pagamento:** {dias_entrega_pagamento}")
    st.write(f"**USD Pagamento:** {usd_pagamento:,.4f}")
    st.write(f"**Flat Pgua:** {flat_pgua:,.4f}")
    st.write(f"**Líquido Pgua:** {liquido_pgua:,.4f}")
    st.write(f"**Preço Bruto sem Financeiro:** {preco_bruto_sem_fin:,.4f}")
