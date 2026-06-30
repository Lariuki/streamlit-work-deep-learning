import streamlit as st

st.set_page_config(page_title="Comparador de Respostas", page_icon="⚖️", layout="wide")
st.title("⚖️ Comparador de Respostas")
st.caption("Side-by-side: resposta original × chosen (GPT-4o) × modelo treinado")

st.info("""
**Esta página estará disponível após a conclusão do fine-tuning.**

O comparador mostrará lado a lado:
- **Rejected** — resposta original da base (pode ser ruim)
- **Chosen** — resposta reescrita pelo GPT-4o (ideal)
- **Modelo treinado** — resposta gerada pelo Qwen2-7B após QLoRA + DPO

Com métricas automáticas por linha: ROUGE-L, BERTScore e avaliação do LLM-as-judge.
""")

st.divider()
st.subheader("Prévia do formato")

exemplos = [
    {
        "question": "fis um ceguro célula cem queré tá cobrado de mim todo mes",
        "rejected": "Para informações sobre seguros, acesse a central de ajuda.",
        "chosen":   "Entendo. O Seguro Celular tem cobrança mensal automática. Se você não deseja continuar, posso te ajudar a cancelar agora mesmo pelo app em Seguros > Seguro Celular > Cancelar.",
        "modelo":   "⏳ Disponível após fine-tuning"
    },
    {
        "question": "cai num golpe do pix ontem e vcs nao fazem nada??? perdi 800 conto",
        "rejected": "Transferências via Pix são de responsabilidade do usuário.",
        "chosen":   "Sinto muito por isso. Não apague as conversas com o golpista. Abra o comprovante do Pix de R$800 no extrato e toque em Relatar problema > Fui vítima de golpe. Recomendamos também registrar um boletim de ocorrência.",
        "modelo":   "⏳ Disponível após fine-tuning"
    },
]

for ex in exemplos:
    with st.expander(f"📩 **Cliente:** _{ex['question']}_"):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### ❌ Rejected")
            st.markdown(
                f"""<div style="background:#3a1a1a;padding:12px;border-radius:8px;
                border-left:4px solid #ef553b;">
                <span style="color:#f0f0f0">{ex['rejected']}</span>
                </div>""",
                unsafe_allow_html=True
            )

        with col2:
            st.markdown("#### ✅ Chosen (GPT-4o)")
            st.markdown(
                f"""<div style="background:#1a3a2a;padding:12px;border-radius:8px;
                border-left:4px solid #00cc96;">
                <span style="color:#f0f0f0">{ex['chosen']}</span>
                </div>""",
                unsafe_allow_html=True
            )

        with col3:
            st.markdown("#### 🤖 Modelo Treinado")
            st.markdown(
                f"""<div style="background:#1e2a3a;padding:12px;border-radius:8px;
                border-left:4px solid #636efa;">
                <span style="color:#aaaaaa">{ex['modelo']}</span>
                </div>""",
                unsafe_allow_html=True
            )

        st.caption("ROUGE-L: — | BERTScore: — | LLM-judge: —")

st.divider()
st.subheader("Próximos passos para ativar esta página")

st.markdown("""
1. Gerar `chosen` e `rejected` via GPT-4o API para cada linha da base
2. Treinar o modelo com SFT + QLoRA
3. Treinar o modelo com DPO + QLoRA  
4. Exportar o modelo final
5. Carregar aqui e habilitar a geração de respostas em tempo real
""")
