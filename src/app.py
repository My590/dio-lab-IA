import json
import pandas as pd
import requests
import streamlit as st

# ============== CONFIGURAÇÕES ==============
OLLAMA_URL = "http://localhost:11434/api/generate"
MODELO = "llama3.2"

# ============== CARREGAR DADOS ==============
perfil = json.load(open('data/perfil_investidor.json'))
transacoes = pd.read_csv('data/transacoes.csv')
historico = pd.read_csv('data/historico_atendimento.csv')
produtos = json.load(open('data/produtos_financeiros.json'))

# ============== MONTAR CONTEXTO ==============
contexto = f"""
CLIENTE: {perfil['nome']}, {perfil['idade']} anos, perfil {perfil['perfil_investidor']}
OBJETIVO: {perfil['objetivo_principal']}

PATRIMÔNIO: R$ {perfil['patrimonio_total']} | RESERVA: R$ {perfil['reserva_emergencia_atual']}

TRANSAÇÕES RECENTES:
{transacoes.to_string(index=False)}

ATENDIMENTOS ANTERIORES:
{historico.to_string(index=False)}

PRODUTOS DISPONÍVEIS:
{json.dumps(produtos, indent=2, ensure_ascii=False)}
"""
# ============== MONTAR CONTEXTO ==============

SYSTEM_PROMPT = """Você é um agente financeiro inteligente chamado Elo. 

OBJETIVO: Seu objetivo é analisar o cenário monetário do cliente e desenvolver relatórios simples e gráficos que permitem a organização do cliente segundo seus dados de saida e entrada.

REGRAS:
1. Sempre baseie suas respostas nos dados fornecidos.
2. Nunca invente informações financeiras.
3. Se não souber algo, admita e ofereça alternativas.
4. Nunca recomende investimentos, apenas faça considerações de risco e viabilidade de acordo com o perfil do cliente e seus dados. 
5. Sempre pergunte se os relatórios ou gráficos atenderam ao solicitado.
6. Fale de forma clara e objetiva, evitando jargões financeiros complexos.
"""

# -------- CHAMAR OLLAMA ---------


def perguntar(msg):
    prompt = f"""
{SYSTEM_PROMPT}

CONTEXTO DO CLIENTE:
{contexto}

Pergunta: {msg}
"""

    try:
        r = requests.post(
            OLLAMA_URL,
            json={
                'model': MODELO,
                'prompt': prompt,
                'stream': False
            }
        )

        # Mostra o status da requisição
        print("Status:", r.status_code)

        # Se ocorreu um erro HTTP
        if r.status_code != 200:
            print("Resposta do servidor:", r.text)
            return f"Erro ao conectar com o Ollama: {r.status_code}"

        # Converte a resposta para JSON
        dados = r.json()

        return dados.get(
            'response',
            'O Ollama respondeu, mas não enviou o campo "response".'
        )

    except requests.exceptions.JSONDecodeError:
        print("Resposta recebida:", r.text)
        return "Erro: o Ollama não retornou uma resposta válida."

    except requests.exceptions.ConnectionError:
        return "Erro: não foi possível conectar ao Ollama. Verifique se ele está rodando."

# -------- INTERFACE ---------

st.title ("Elo - Agente Financeiro Inteligente")

if pergunta := st.text_input("Digite sua pergunta:"):
    st.chat_message("user").write(pergunta)
    with st.spinner("..."):
        st.chat_message("assistant").write(perguntar(pergunta))
