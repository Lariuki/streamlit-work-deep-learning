import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Análise Exploratória", page_icon="📊", layout="wide")
st.title("📊 Análise Exploratória do Dataset")

# ── Carrega dados ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = Path(__file__).parent.parent.parent / "Dados" / "base_sintetica_tcc_10234_anonimizada.csv"
    df = pd.read_csv(base, encoding='utf-8-sig')

    # Parse label_classified
    def parse_label(val):
        try:
            items = json.loads(val)
            if isinstance(items, list) and items:
                return items[0].get('product', None), items[0].get('category', None), items[0].get('probability', None)
        except:
            pass
        return None, None, None

    df[['product', 'category', 'probability']] = df['label_classified'].apply(
        lambda x: pd.Series(parse_label(x))
    )

    # Timestamp
    df['interection_ocurred_at'] = pd.to_datetime(df['interection_ocurred_at'], utc=True, errors='coerce')
    df['hour'] = df['interection_ocurred_at'].dt.hour
    df['month'] = df['interection_ocurred_at'].dt.month

    # llm_model null string → NaN
    df['llm_model'] = df['llm_model'].replace('null', pd.NA)

    # booleans
    df['ticket'] = df['was_support_ticket_created'].astype(str).str.lower() == 'true'
    df['human']  = df['was_offered_human_support'].astype(str).str.lower() == 'true'

    return df

df = load_data()

# ── Métricas ──────────────────────────────────────────────────────────────────
st.subheader("Visão Geral")
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("Total linhas",      f"{len(df):,}")
c2.metric("Sessões únicas",    f"{df['session_id'].nunique():,}")
c3.metric("Consumers únicos",  f"{df['consumer_id'].nunique():,}")
c4.metric("Produtos únicos",   f"{df['product'].nunique()}")
c5.metric("Ticket rate",       f"{df['ticket'].mean()*100:.1f}%")
c6.metric("Handoff rate",      f"{df['human'].mean()*100:.1f}%")

st.divider()

# ── Row 1: Produto e Categoria ────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição por Produto")
    prod_count = df['product'].value_counts().reset_index()
    prod_count.columns = ['Produto', 'Count']
    fig = px.bar(prod_count, x='Count', y='Produto', orientation='h',
                 color='Count', color_continuous_scale='Blues',
                 text='Count')
    fig.update_layout(showlegend=False, coloraxis_showscale=False,
                      yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top 15 Categorias")
    cat_count = df['category'].value_counts().head(15).reset_index()
    cat_count.columns = ['Categoria', 'Count']
    fig = px.bar(cat_count, x='Count', y='Categoria', orientation='h',
                 color='Count', color_continuous_scale='Teal',
                 text='Count')
    fig.update_layout(showlegend=False, coloraxis_showscale=False,
                      yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Row 2: Agentes e LLM ─────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição por Agente")
    agent_count = df['agent'].value_counts().reset_index()
    agent_count.columns = ['Agente', 'Count']
    fig = px.pie(agent_count, names='Agente', values='Count',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Modelo LLM Utilizado")
    llm_count = df['llm_model'].fillna('rule-based (null)').value_counts().reset_index()
    llm_count.columns = ['LLM', 'Count']
    fig = px.pie(llm_count, names='LLM', values='Count',
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Row 3: Sessões ────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribuição de Msgs por Sessão")
    sess_size = df.groupby('session_id').size().value_counts().sort_index().reset_index()
    sess_size.columns = ['Msgs/Sessão', 'Qtde Sessões']
    sess_size['Msgs/Sessão'] = sess_size['Msgs/Sessão'].astype(str).apply(
        lambda x: x if int(x) < 6 else '6+'
    )
    sess_size = sess_size.groupby('Msgs/Sessão')['Qtde Sessões'].sum().reset_index()
    fig = px.bar(sess_size, x='Msgs/Sessão', y='Qtde Sessões',
                 color='Qtde Sessões', color_continuous_scale='Purples',
                 text='Qtde Sessões')
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Ticket e Handoff por Produto")
    ticket_prod = df.groupby('product').agg(
        ticket_rate=('ticket', 'mean'),
        human_rate=('human', 'mean'),
        total=('ticket', 'count')
    ).reset_index()
    ticket_prod['ticket_pct'] = (ticket_prod['ticket_rate'] * 100).round(1)
    ticket_prod['human_pct']  = (ticket_prod['human_rate'] * 100).round(1)

    fig = go.Figure()
    fig.add_bar(name='Ticket Criado (%)', x=ticket_prod['product'],
                y=ticket_prod['ticket_pct'], marker_color='#ef553b')
    fig.add_bar(name='Suporte Humano (%)', x=ticket_prod['product'],
                y=ticket_prod['human_pct'], marker_color='#636efa')
    fig.update_layout(barmode='group', xaxis_tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Row 4: Sazonalidade e Probabilidade ──────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Volume por Hora do Dia")
    hour_count = df.groupby('hour').size().reset_index(name='Count')
    fig = px.area(hour_count, x='hour', y='Count',
                  color_discrete_sequence=['#00cc96'],
                  labels={'hour': 'Hora', 'Count': 'Interações'})
    fig.update_layout(xaxis=dict(tickmode='linear', dtick=2))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Distribuição de Probabilidade do Classificador")
    fig = px.histogram(df.dropna(subset=['probability']),
                       x='probability', nbins=30,
                       color_discrete_sequence=['#ab63fa'],
                       labels={'probability': 'Probabilidade', 'count': 'Frequência'})
    fig.add_vline(x=df['probability'].mean(), line_dash='dash',
                  annotation_text=f"Média: {df['probability'].mean():.2f}")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Tabela amostral ───────────────────────────────────────────────────────────
st.subheader("Amostra do Dataset")
cols_show = ['consumer_id', 'session_id', 'question', 'answer', 'product',
             'category', 'agent', 'llm_model', 'was_support_ticket_created']
st.dataframe(
    df[cols_show].sample(20, random_state=42).reset_index(drop=True),
    use_container_width=True
)
