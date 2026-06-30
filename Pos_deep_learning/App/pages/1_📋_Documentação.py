import streamlit as st

st.set_page_config(page_title="Documentação — Dataset", page_icon="📋", layout="wide")
st.title("📋 Documentação do Dataset")
st.caption("Pipeline completo de construção da base sintética de atendimento bancário")

st.divider()

# ── Motivação ─────────────────────────────────────────────────────────────────
st.header("1. Motivação")
st.markdown("""
O treinamento de modelos de linguagem para atendimento bancário em português exige uma base de dados
que reflita o comportamento real de interações entre clientes e agentes automatizados.

Como o uso de dados reais de produção é inviável por **restrições de privacidade e LGPD**, optou-se
pela construção de uma base sintética estruturada a partir de um schema real de sistema de atendimento,
com anonimização completa de identidades e marcas.
""")

st.divider()

# ── Schema ────────────────────────────────────────────────────────────────────
st.header("2. Schema Real — 23 Colunas")

import pandas as pd

schema = pd.DataFrame([
    ("iara_log_id",                "ID único do registro de log"),
    ("iara_trace_id",              "ID de rastreamento da requisição"),
    ("consumer_id",                "ID do usuário (anonimizado: prefixo USR)"),
    ("session_id",                 "ID da sessão de conversa (agrupa múltiplos turnos)"),
    ("question",                   "Mensagem enviada pelo cliente"),
    ("answer",                     "Resposta gerada pelo agente"),
    ("origin",                     "Canal de origem: customer_service ou dm"),
    ("llm_model",                  "Modelo LLM utilizado (gpt-4o, gpt-4-turbo, null)"),
    ("reason_failure",             "Motivo de falha, quando houver"),
    ("deeplink_id_array",          "IDs de deeplinks acionados (JSON array)"),
    ("rule_activated_id_array",    "IDs de regras ativadas (JSON array)"),
    ("related_article_id_array",   "IDs de artigos de conhecimento utilizados (JSON array)"),
    ("message_id",                 "ID único da mensagem"),
    ("version_prompt",             "Versão do prompt utilizado"),
    ("user_segmentation",          "Segmentação do usuário"),
    ("label_classified",           "JSON com produto, categoria e probabilidade de classificação"),
    ("connector",                  "Tipo de conector: orchestrator ou dm"),
    ("flags",                      "Flags de configuração A/B e features (JSON)"),
    ("agent",                      "Agente que processou a mensagem"),
    ("debug",                      "JSON com contexto de integrações acionadas"),
    ("was_support_ticket_created", "Se um ticket de suporte foi criado (true/false)"),
    ("was_offered_human_support",  "Se suporte humano foi oferecido (true/false)"),
    ("interection_ocurred_at",     "Timestamp da interação (ISO 8601, UTC)"),
], columns=["Coluna", "Descrição"])

st.dataframe(schema, use_container_width=True, hide_index=True)

st.divider()

# ── Etapas ────────────────────────────────────────────────────────────────────
st.header("3. Etapas de Construção")

etapas = [
    {
        "num": "Etapa 1",
        "titulo": "Geração inicial em formato didático — descartada",
        "feito": "Geração de 10 conversas em JSON com campos `categoria`, `tom_cliente`, `problema_assistente`, turnos alternados com resposta ruim vs ideal.",
        "problema": "Formato adequado para análise qualitativa, mas incompatível com pipelines de treinamento. Muito distante de logs reais.",
        "decisao": "Descartar e migrar para schema real.",
        "cor": "🔴"
    },
    {
        "num": "Etapa 2",
        "titulo": "Migração para CSV com schema real",
        "feito": "Reestruturação para 23 colunas cobrindo IDs, mensagens, agentes, metadados de classificação e sinais operacionais.",
        "problema": "Separador inicial era `;`, causando incompatibilidade com pandas e Excel.",
        "decisao": "Corrigido para `,` com encoding UTF-8 BOM.",
        "cor": "🟡"
    },
    {
        "num": "Etapa 3",
        "titulo": "Escala para 10.000 conversas — F1 = 1.0 identificado",
        "feito": "Geração de 10.000 conversas (~22.767 linhas) com distribuição por categoria, subcategoria, sentimento e tipo de falha.",
        "problema": "**F1-macro = 1.0000** — base perfeitamente separável. Vocabulário exclusivo por categoria, frases template sem variação, zero sobreposição.",
        "decisao": "Reformular completamente a geração de conteúdo.",
        "cor": "🔴"
    },
    {
        "num": "Etapa 4",
        "titulo": "Introdução de ruído, ambiguidade e sobreposição",
        "feito": 'Mensagens curtas ambíguas ("Valor", "Cancelar", "Tá"), ruído tipográfico real ("fis um ceguro célula cem queré"), sobreposição de intenções, label_classified com erro simulado.',
        "problema": "Sem problemas críticos. F1 esperado entre 0.75–0.88.",
        "decisao": "Manter e escalar.",
        "cor": "🟢"
    },
    {
        "num": "Etapa 5",
        "titulo": "Escala para 10.234 linhas + anonimização completa",
        "feito": "PicPay → FinBank em todos os textos. Agentes renomeados. Substituição em debug, flags e label_classified.",
        "problema": "consumer_id ainda seguia padrão `138xxxxxxx` do sistema real.",
        "decisao": "Corrigir IDs na etapa seguinte.",
        "cor": "🟡"
    },
    {
        "num": "Etapa 6",
        "titulo": "Correção dos IDs de usuário",
        "feito": "Migração de `138xxxxxxxxxxxxxxx` para `USRxxxxxxxxxxxxxxx` (15 dígitos aleatórios sem padrão real).",
        "problema": "Nenhum após correção.",
        "decisao": "Validado: 0 colisões com IDs reais, 0 referências ao padrão original.",
        "cor": "🟢"
    },
    {
        "num": "Etapa 7",
        "titulo": "Correção da estrutura de sessões",
        "feito": "Cada linha tinha session_id único. Reestruturado para que múltiplos turnos compartilhem session_id, com distribuição replicando o dado real (64% = 1 msg, 17% = 2, 10% = 3...).",
        "problema": "Sessões de 1 msg = 100% — irreal.",
        "decisao": "Distribuição ajustada para 70.6% / 13.9% / 13.4% / 2.0%.",
        "cor": "🟢"
    },
    {
        "num": "Etapa 8",
        "titulo": "Redução de mensagens de baixo valor",
        "feito": "Remoção de 1.223 mensagens de saudação pura com 153 ocorrências cada (reflexo do ciclo do gerador).",
        "problema": "15% das mensagens eram 'Oi', 'Bom dia', 'Tá', 'Sim' — sem valor de treinamento.",
        "decisao": "Reduzido para 3.4% — proporção realista mantendo algumas saudações.",
        "cor": "🟢"
    },
    {
        "num": "Etapa 9",
        "titulo": "Reconstrução com 20 fluxos temáticos coerentes",
        "feito": "Criação de fluxos com sequência lógica de turnos. Cada sessão multi-turno segue um tema do início ao fim.",
        "problema": 'Sessões com temas misturados: "Quero parcelar a fatura" → "Nao ta funcionando o app" → "Limite bloqueado".',
        "decisao": "20 fluxos temáticos cobrindo os principais casos de atendimento bancário.",
        "cor": "🟢"
    },
]

for e in etapas:
    with st.expander(f"{e['cor']} **{e['num']} — {e['titulo']}**"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**O que foi feito**")
            st.markdown(e['feito'])
        with col2:
            st.markdown("**Problema identificado**")
            st.markdown(e['problema'])
        with col3:
            st.markdown("**Decisão**")
            st.markdown(e['decisao'])

st.divider()

# ── Agentes ───────────────────────────────────────────────────────────────────
st.header("4. Mapa de Anonimização de Agentes")

agentes = pd.DataFrame([
    ("AI_CHAT_ENGINE",                        "NLU_CHAT_ENGINE"),
    ("RULE_AGENT",                            "FLOW_AGENT"),
    ("PICPAY_CARD_INTEGRATION",               "DIGITAL_CARD_INTEGRATION"),
    ("PIX_DEVOLUTION_INTEGRATION",            "TRANSFER_DEVOLUTION_INTEGRATION"),
    ("PICPAY_CARD_REPLACEMENT_INTEGRATION",   "CARD_REPLACEMENT_INTEGRATION"),
    ("CARD_CONTESTATION_NOT_RECOGNISE_PURCHASE", "TRANSACTION_DISPUTE_INTEGRATION"),
    ("PIX_MED_BLOCKING_INTEGRATION",          "TRANSFER_BLOCK_INTEGRATION"),
    ("LOAN_RENEGOTIATION_INTEGRATION",        "CREDIT_RENEGOTIATION_INTEGRATION"),
    ("GUARANTEED_LIMIT_INTEGRATION",          "CREDIT_LIMIT_INTEGRATION"),
    ("USER_CARD_INFO_INTEGRATION",            "CARD_INFO_INTEGRATION"),
], columns=["Nome Original", "Nome Fictício (FinBank)"])

st.dataframe(agentes, use_container_width=True, hide_index=True)

st.divider()

# ── Ruídos intencionais ───────────────────────────────────────────────────────
st.header("5. Ruídos Intencionais e Justificativas Acadêmicas")

st.warning("""
**`label_classified` desalinhado com `question`**  
O label é gerado ciclicamente, sem considerar o conteúdo da mensagem — replicando o comportamento 
de classificadores automáticos de intenção em produção, que cometem erros de produto e categoria.  

*Justificativa:* "A base reflete o comportamento real de sistemas de atendimento automatizado. 
Essa característica é uma das principais motivações para o uso de DPO — o modelo aprende a 
preferir respostas de qualidade independente da classificação automática de intenção."
""")

st.warning("""
**`agent` × `debug_integrations_context_selected` parcialmente desalinhados (~5%)**  
O debug é um snapshot de contexto do sistema, não necessariamente consistente com o agente acionado.  
**Impacto no treinamento: nenhum.** As colunas `debug` e `label_classified` não são features do fine-tuning.
""")

st.info("""
**`llm_model` como string `"null"`**  
Agentes rule-based possuem `llm_model = "null"` como string. Consistente com o formato do log real.  
**Impacto no treinamento: nenhum.**
""")

st.divider()

# ── Estado final ──────────────────────────────────────────────────────────────
st.header("6. Estado Final do Dataset")

final = pd.DataFrame([
    ("Total de linhas", "9.011"),
    ("Colunas", "23"),
    ("Schema", "Idêntico ao log real do sistema"),
    ("Sessões únicas", "6.136"),
    ("Msgs/sessão média", "1.47"),
    ("Msgs/sessão máximo", "9"),
    ("Consumers recorrentes", "~2.164"),
    ("Mensagens de baixo valor", "3.4%"),
    ("Referências à marca real", "0"),
    ("Colisões com IDs reais", "0"),
    ("Encoding", "UTF-8 BOM"),
    ("Separador", ","),
], columns=["Característica", "Valor"])

st.dataframe(final, use_container_width=True, hide_index=True)

st.divider()

# ── Limitações ────────────────────────────────────────────────────────────────
st.header("7. Limitações Declaradas")

st.markdown("""
1. **Base sintética:** resultados do fine-tuning podem não generalizar diretamente para distribuições de linguagem de clientes reais, que apresentam maior variação e ambiguidade.
2. **Vocabulário limitado:** os 20 fluxos temáticos cobrem os casos mais comuns, mas não esgotam a diversidade de intenções real.
3. **Ausência de contexto multi-sessão:** o modelo não recebe histórico de sessões anteriores do mesmo consumer.
4. **Chosen/rejected via GPT-4o:** a qualidade dos pares de preferência depende da qualidade do prompt e das limitações do GPT-4o como juiz.
""")

st.divider()

# ── Próximos passos ───────────────────────────────────────────────────────────
st.header("8. Próximos Passos")

proximos = pd.DataFrame([
    ("Geração de pares chosen/rejected", "Chamar GPT-4o API para cada (question, answer)", "Python + OpenAI API", "⏳ Pendente"),
    ("Divisão treino/validação/teste",   "Split 70/15/15 por session_id",                  "pandas",             "⏳ Pendente"),
    ("SFT + QLoRA",                      "Treinar Qwen2-7B nos pares (question, chosen)",   "HuggingFace TRL",    "⏳ Pendente"),
    ("DPO + QLoRA",                      "Treinar nos triplos usando modelo SFT como ref",  "HuggingFace TRL",    "⏳ Pendente"),
    ("Avaliação",                        "ROUGE-L, BERTScore e LLM-as-judge no test set",   "evaluate + OpenAI",  "⏳ Pendente"),
], columns=["Etapa", "Descrição", "Ferramenta", "Status"])

st.dataframe(proximos, use_container_width=True, hide_index=True)
