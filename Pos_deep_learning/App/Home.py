import streamlit as st

st.set_page_config(
    page_title="TCC — FinBank Dataset",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏦 Fine-tuning de LLM para Atendimento Bancário")
st.subheader("Pós-Graduação em Deep Learning — UFPE")

st.markdown("""
**Aluna:** Larissa Akemi Iuki  
**Orientador:** Prof. Cleber Zanchettin  
**Técnicas:** QLoRA + DPO | **Modelo base:** Qwen2-7B-Instruct
""")

st.divider()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total de linhas", "9.011")
with col2:
    st.metric("Sessões únicas", "6.136")
with col3:
    st.metric("Colunas", "23")
with col4:
    st.metric("Fluxos temáticos", "20")

st.divider()

st.markdown("## Navegação")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.info("""
    **📋 Documentação**  
    Pipeline completo das 9 etapas de construção do dataset, decisões tomadas e justificativas acadêmicas.
    """)

with col2:
    st.info("""
    **📊 Análise Exploratória**  
    Distribuições de produtos, categorias, agentes, sessões, ticket rate e sazonalidade horária.
    """)

with col3:
    st.info("""
    **💬 Visualizador de Sessões**  
    Explore sessões completas de conversa com todos os turnos em ordem cronológica.
    """)

with col4:
    st.info("""
    **⚖️ Comparador de Respostas**  
    Side-by-side entre resposta original, chosen (GPT-4o) e resposta do modelo treinado.  
    *(disponível após fine-tuning)*
    """)

st.divider()
st.markdown("## Pipeline do Projeto")

st.markdown("""
```
Base Sintética (9.011 linhas)          
question + answer + metadados          
        │                              
        ▼                              
  GPT-4o reescreve                     
        │                              
        ▼                              
  Base DPO (triplas)                   
  question + chosen + rejected         
        │                              
        ├──────────────┐               
        ▼              ▼               
   70% treino     15% validação + 15% teste
        │                              
        ├─────────────────────┐        
        ▼                     ▼        
  Estágio 1: SFT        Estágio 2: DPO 
  QLoRA Qwen2-7B        QLoRA + ref_model
        │                     │        
        ▼                     ▼        
  Modelo baseline       Modelo final   
        │                     │        
        └──────────┬───────────┘        
                   ▼                   
            Avaliação                  
     ROUGE-L | BERTScore | LLM-as-judge
```
""")
