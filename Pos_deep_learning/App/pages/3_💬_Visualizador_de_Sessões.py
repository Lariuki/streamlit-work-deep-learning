import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(page_title="Visualizador de Sessões", page_icon="💬", layout="wide")
st.title("💬 Visualizador de Sessões")
st.caption("Explore conversas completas com todos os turnos em ordem cronológica")

@st.cache_data
def load_data():
    base = Path(__file__).parent.parent.parent / "Dados" / "base_sintetica_tcc_10234_anonimizada.csv"
    df = pd.read_csv(base, encoding='utf-8-sig')
    def parse_label(val):
        try:
            items = json.loads(val)
            if isinstance(items, list) and items:
                return items[0].get('product', ''), items[0].get('category', '')
        except:
            pass
        return '', ''
    df[['product', 'category']] = df['label_classified'].apply(lambda x: pd.Series(parse_label(x)))
    df['interection_ocurred_at'] = pd.to_datetime(df['interection_ocurred_at'], utc=True, errors='coerce')
    df['llm_model'] = df['llm_model'].replace('null', None)
    return df

df = load_data()

# ── Filtros ───────────────────────────────────────────────────────────────────
st.sidebar.header("Filtros")

# Filtro por tamanho de sessão
min_turns = st.sidebar.slider("Mínimo de turnos na sessão", 1, 9, 2)

# Filtro por produto
produtos = ['Todos'] + sorted(df['product'].dropna().unique().tolist())
produto_sel = st.sidebar.selectbox("Filtrar por produto", produtos)

# Filtro por agente
agentes = ['Todos'] + sorted(df['agent'].dropna().unique().tolist())
agente_sel = st.sidebar.selectbox("Filtrar por agente", agentes)

# Aplica filtros
sess_size = df.groupby('session_id').size()
sess_validas = sess_size[sess_size >= min_turns].index

df_filtrado = df[df['session_id'].isin(sess_validas)]
if produto_sel != 'Todos':
    sess_prod = df_filtrado[df_filtrado['product'] == produto_sel]['session_id'].unique()
    df_filtrado = df_filtrado[df_filtrado['session_id'].isin(sess_prod)]
if agente_sel != 'Todos':
    sess_ag = df_filtrado[df_filtrado['agent'] == agente_sel]['session_id'].unique()
    df_filtrado = df_filtrado[df_filtrado['session_id'].isin(sess_ag)]

sessoes_disponiveis = df_filtrado['session_id'].unique()
st.sidebar.markdown(f"**{len(sessoes_disponiveis)} sessões** com os filtros aplicados")

# ── Seleção de sessão ─────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 1])
with col1:
    session_sel = st.selectbox(
        "Selecione uma sessão",
        options=sessoes_disponiveis[:200],
        format_func=lambda s: f"{s[:8]}... ({sess_size.get(s, 0)} turnos)"
    )
with col2:
    if st.button("🎲 Sessão aleatória"):
        import random
        session_sel = random.choice(sessoes_disponiveis.tolist())

st.divider()

# ── Conversa ─────────────────────────────────────────────────────────────────
if session_sel:
    conversa = df[df['session_id'] == session_sel].copy()
    conversa = conversa.sort_values('interection_ocurred_at').reset_index(drop=True)

    # Header da sessão
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Session ID",   session_sel[:16] + "...")
    col2.metric("Consumer",     conversa['consumer_id'].iloc[0])
    col3.metric("Turnos",       len(conversa))
    col4.metric("Ticket",       "✅ Sim" if (conversa['was_support_ticket_created'].astype(str).str.lower() == 'true').any() else "❌ Não")

    st.divider()

    # Renderiza turnos
    for i, row in conversa.iterrows():
        turno_num = i + 1
        ts = row['interection_ocurred_at']
        ts_str = ts.strftime('%d/%m/%Y %H:%M') if pd.notna(ts) else '—'
        prod    = row['product'] or '—'
        cat     = row['category'] or '—'
        agent   = row['agent'] or '—'
        llm     = row['llm_model'] if pd.notna(row['llm_model']) and row['llm_model'] != 'null' else 'rule-based'
        ticket  = str(row['was_support_ticket_created']).lower() == 'true'
        human   = str(row['was_offered_human_support']).lower() == 'true'

        with st.container():
            st.markdown(f"#### Turno {turno_num} — {ts_str}")

            # Mensagem do cliente
            st.markdown(
                f"""<div style="background:#1e3a5f;padding:12px 16px;border-radius:12px;
                border-left:4px solid #4da6ff;margin-bottom:8px;">
                <b style="color:#4da6ff">👤 Cliente</b><br>
                <span style="color:#f0f0f0">{row['question']}</span>
                </div>""",
                unsafe_allow_html=True
            )

            # Resposta do agente
            st.markdown(
                f"""<div style="background:#1a3a2a;padding:12px 16px;border-radius:12px;
                border-left:4px solid #00cc96;margin-bottom:8px;">
                <b style="color:#00cc96">🤖 Agente</b><br>
                <span style="color:#f0f0f0">{row['answer']}</span>
                </div>""",
                unsafe_allow_html=True
            )

            # Metadados do turno
            meta_cols = st.columns(6)
            meta_cols[0].caption(f"**Produto:** {prod}")
            meta_cols[1].caption(f"**Categoria:** {cat}")
            meta_cols[2].caption(f"**Agente:** {agent}")
            meta_cols[3].caption(f"**LLM:** {llm}")
            meta_cols[4].caption(f"**Ticket:** {'✅' if ticket else '❌'}")
            meta_cols[5].caption(f"**Humano:** {'✅' if human else '❌'}")

            st.markdown("---")

# ── Estatísticas gerais ───────────────────────────────────────────────────────
st.subheader("Estatísticas das Sessões Filtradas")
col1, col2, col3 = st.columns(3)
with col1:
    sizes = df_filtrado.groupby('session_id').size()
    st.metric("Média msgs/sessão",  f"{sizes.mean():.2f}")
    st.metric("Máx msgs/sessão",    int(sizes.max()))
with col2:
    st.metric("Sessões com ticket", f"{(df_filtrado.groupby('session_id')['was_support_ticket_created'].apply(lambda x: (x.astype(str).str.lower()=='true').any()).sum()):,}")
    st.metric("Sessões com handoff",f"{(df_filtrado.groupby('session_id')['was_offered_human_support'].apply(lambda x: (x.astype(str).str.lower()=='true').any()).sum()):,}")
with col3:
    st.metric("Consumers recorrentes",
              f"{(df_filtrado.groupby('consumer_id')['session_id'].nunique() > 1).sum():,}")
