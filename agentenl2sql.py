import os
import sqlite3
import base64
import pandas as pd
import tempfile
import streamlit as st
from typing import Dict, TypedDict, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
import matplotlib.pyplot as plt
from io import BytesIO
from pandasql import sqldf
import atexit

# Configuração do ambiente
os.environ["OPENAI_API_KEY"] = "Insira a Sua Chave de API"  # Substitua pela sua chave real

# Inicialização do modelo de linguagem
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# Definição de tipos
class AgentState(TypedDict):
    user_input: str
    intent: Optional[str]
    sql_query: Optional[str]
    query_result: Optional[pd.DataFrame]
    natural_response: Optional[str]
    chart: Optional[str]  # imagem codificada em base64
    conversation_history: List[dict]

# Configuração do Streamlit
st.set_page_config(page_title="Sistema NL2SQL", layout="wide")
st.title("📊 Sistema Inteligente de Consulta a Dados")
st.write("Faça perguntas em linguagem natural para analisar seus dados")

# Upload do arquivo de dados
uploaded_file = st.file_uploader(
    "📤 Carregue seu arquivo de dados (CSV, Excel, SQLite)", 
    type=["csv", "xlsx", "db", "sqlite"]
)

# Inicialização do estado da sessão
if "conversation" not in st.session_state:
    st.session_state.conversation = []

if "data_source" not in st.session_state:
    st.session_state.data_source = None

if "df" not in st.session_state:
    st.session_state.df = None

if "conn" not in st.session_state:
    st.session_state.conn = None

# Processamento do arquivo carregado
if uploaded_file is not None:
    if uploaded_file.name.endswith('.csv'):
        try:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.session_state.data_source = "csv"
            st.success("✅ Arquivo CSV carregado com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao ler CSV: {str(e)}")
            
    elif uploaded_file.name.endswith('.xlsx'):
        try:
            st.session_state.df = pd.read_excel(uploaded_file)
            st.session_state.data_source = "excel"
            st.success("✅ Arquivo Excel carregado com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro ao ler Excel: {str(e)}")
            
    elif uploaded_file.name.endswith('.db') or uploaded_file.name.endswith('.sqlite'):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            conn = sqlite3.connect(tmp_file_path)
            st.session_state.data_source = "sqlite"
            st.session_state.conn = conn
            st.session_state.temp_db_path = tmp_file_path
            st.success("✅ Banco de dados SQLite conectado com sucesso!")
            
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if tables:
                st.sidebar.subheader("📋 Tabelas disponíveis:")
                for table in tables:
                    st.sidebar.write(f"- {table[0]}")
            else:
                st.warning("⚠️ O banco de dados não contém tabelas.")
                
        except Exception as e:
            st.error(f"❌ Erro ao conectar ao SQLite: {str(e)}")
            if 'conn' in st.session_state and st.session_state.conn:
                st.session_state.conn.close()

# Função para obter o esquema do banco de dados
def get_schema():
    if st.session_state.data_source == "sqlite" and st.session_state.conn:
        try:
            cursor = st.session_state.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            schema = ""
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                schema += f"📌 Tabela {table_name}:\n"
                for col in columns:
                    schema += f"  ├─ {col[1]}: {col[2]}\n"
                schema += "\n"
            return schema
        except Exception as e:
            st.error(f"❌ Erro ao obter esquema: {str(e)}")
            return "Erro ao obter esquema do banco de dados"
    elif st.session_state.data_source in ["csv", "excel"] and st.session_state.df is not None:
        schema = "📌 Colunas de dados:\n"
        for col in st.session_state.df.columns:
            dtype = str(st.session_state.df[col].dtype)
            schema += f"  ├─ {col}: {dtype}\n"
        return schema
    return "Nenhum esquema disponível"

# Agente 1: Classificador de Intenção
def classify_intent(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Classifique a intenção do usuário com base em sua entrada. Escolha uma destas opções:
        - "nl2sql": Pergunta que requer consulta a dados
        - "visual": Solicitação de visualização gráfica
        - "followup": Pergunta de acompanhamento
        - "geral": Pergunta não relacionada a dados
        
        Exemplos:
        - "Quais foram as vendas em janeiro?" → "nl2sql"
        - "Mostre um gráfico de vendas por região" → "visual"
        - "Explique o que é JOIN em SQL" → "geral"
        - "E no trimestre anterior?" → "followup"
        """),
        ("human", "Pergunta: {user_input}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"user_input": state["user_input"]})
    
    intent = response.content.lower()
    if "nl2sql" in intent:
        return {"intent": "nl2sql"}
    elif "visual" in intent:
        return {"intent": "visual"}
    elif "followup" in intent:
        return {"intent": "followup"}
    else:
        return {"intent": "geral"}

# Agente 2: Gerador NL2SQL
def generate_sql(state: AgentState):
    schema = get_schema()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Você é um especialista em SQL. Dado o esquema abaixo:
        {schema}
        
        Gere uma consulta SQL para responder à pergunta:
        - Use funções de data quando relevante
        - Retorne APENAS o SQL, sem explicações
        - Formate de forma legível
        """),
        ("human", "Pergunta: {user_input}\n\nSQL:")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"user_input": state["user_input"], "schema": schema})
    
    sql_query = response.content.strip()
    for prefix in ["```sql", "```"]:
        if sql_query.startswith(prefix):
            sql_query = sql_query[len(prefix):-3].strip()
    
    return {"sql_query": sql_query}

# Agente 3: Executor SQL
def execute_sql(state: AgentState):
    if not state.get("sql_query"):
        return {"query_result": None}
    
    try:
        if st.session_state.data_source == "sqlite":
            cursor = st.session_state.conn.cursor()
            cursor.execute(state["sql_query"])
            columns = [description[0] for description in cursor.description]
            data = cursor.fetchall()
            result = pd.DataFrame(data, columns=columns)
        elif st.session_state.data_source in ["csv", "excel"]:
            result = sqldf(state["sql_query"], {"df": st.session_state.df})
        else:
            result = None
    except Exception as e:
        st.error(f"❌ Erro na consulta SQL: {str(e)}")
        result = None
    
    return {"query_result": result}

# Agente 4: Gerador de Resposta Natural
def generate_natural_response(state: AgentState):
    if state.get("query_result") is None:
        return {"natural_response": "Não foi possível obter resultados para sua consulta."}
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Você é um analista de dados. Explique os resultados de forma clara:
        - Seja conciso mas informativo
        - Destaque insights relevantes
        - Formate números e datas adequadamente
        - Não mencione SQL ou consultas técnicas
        """),
        ("human", """
        Pergunta original: {user_input}
        
        Resultados (amostra):
        {query_result}
        
        Resposta:
        """)
    ])
    
    sample_data = state["query_result"].head().to_string()
    
    chain = prompt | llm
    response = chain.invoke({
        "user_input": state["user_input"],
        "query_result": sample_data
    })
    
    return {"natural_response": response.content}

# Agente 5: Gerador de Visualização
def generate_visualization(state: AgentState):
    if state.get("query_result") is None or state["query_result"].empty:
        return {"chart": None}
    
    df = state["query_result"]
    
    try:
        plt.figure(figsize=(10, 5))
        
        numeric_cols = df.select_dtypes(include=['number']).columns
        cat_cols = df.select_dtypes(include=['object', 'category']).columns
        
        if len(numeric_cols) >= 2:
            plt.scatter(df[numeric_cols[0]], df[numeric_cols[1]])
            plt.xlabel(numeric_cols[0])
            plt.ylabel(numeric_cols[1])
            plt.title(f"{numeric_cols[0]} vs {numeric_cols[1]}")
        elif len(numeric_cols) >= 1 and len(cat_cols) >= 1:
            df.groupby(cat_cols[0])[numeric_cols[0]].sum().plot(kind='bar')
            plt.title(f"{numeric_cols[0]} por {cat_cols[0]}")
        elif len(numeric_cols) >= 1:
            df[numeric_cols[0]].plot(kind='hist', bins=10)
            plt.title(f"Distribuição de {numeric_cols[0]}")
        else:
            return {"chart": None}
        
        plt.tight_layout()
        
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()
        
        return {"chart": img_base64}
    except Exception as e:
        st.error(f"❌ Erro ao gerar visualização: {str(e)}")
        return {"chart": None}

# Agente 6: Gerador de Resposta Geral
def generate_general_response(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é um assistente inteligente. Responda à pergunta geral do usuário de forma clara e educada."),
        ("human", "{user_input}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({"user_input": state["user_input"]})
    
    return {"natural_response": response.content}

# Agente 7: Manipulador de Acompanhamento
def handle_followup(state: AgentState):
    if not st.session_state.conversation:
        return {"intent": "nl2sql"}
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        Você está em uma conversa sobre análise de dados. 
        A última pergunta foi: {last_question}
        Com resposta: {last_response}
        
        Reformule a nova pergunta como uma pergunta completa independente.
        """),
        ("human", "Pergunta de acompanhamento: {user_input}\n\nReformulação:")
    ])
    
    last_interaction = [m for m in st.session_state.conversation[-2:] if m["role"] in ["user", "assistant"]]
    last_question = next((m["content"] for m in reversed(last_interaction) if m["role"] == "user"), "")
    last_response = next((m["content"] for m in reversed(last_interaction) if m["role"] == "assistant"), "")
    
    chain = prompt | llm
    response = chain.invoke({
        "user_input": state["user_input"],
        "last_question": last_question,
        "last_response": last_response
    })
    
    return {"user_input": response.content, "intent": "nl2sql"}

# Construção do fluxo de trabalho
workflow = StateGraph(AgentState)

# Adicionar nós
workflow.add_node("intent_classifier", classify_intent)
workflow.add_node("generate_sql", generate_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("generate_response", generate_natural_response)
workflow.add_node("generate_visual", generate_visualization)
workflow.add_node("general_response", generate_general_response)
workflow.add_node("followup_handler", handle_followup)

# Configurar fluxo
workflow.set_entry_point("intent_classifier")

# Rotas condicionais
workflow.add_conditional_edges(
    "intent_classifier",
    lambda state: state["intent"],
    {
        "nl2sql": "generate_sql",
        "visual": "generate_sql",
        "geral": "general_response",
        "followup": "followup_handler"
    }
)

# Fluxo principal
workflow.add_edge("generate_sql", "execute_sql")
workflow.add_edge("execute_sql", "generate_response")

# Rotas após resposta
workflow.add_conditional_edges(
    "generate_response",
    lambda state: "visual" if state["intent"] == "visual" else "end",
    {
        "visual": "generate_visual",
        "end": END
    }
)

# Finalizações
workflow.add_edge("generate_visual", END)
workflow.add_edge("general_response", END)
workflow.add_edge("followup_handler", "generate_sql")

# Compilar o workflow (SOLUÇÃO PARA O ERRO)
app = workflow.compile()

# Função para limpeza
def cleanup():
    if 'temp_db_path' in st.session_state:
        try:
            os.unlink(st.session_state.temp_db_path)
        except:
            pass
    if 'conn' in st.session_state and st.session_state.conn:
        st.session_state.conn.close()

atexit.register(cleanup)

# Interface Streamlit
user_input = st.chat_input("💬 Digite sua pergunta sobre os dados...")

if user_input:
    if st.session_state.data_source is None:
        st.error("⚠️ Por favor, carregue um arquivo de dados primeiro")
        st.stop()
    
    st.session_state.conversation.append({"role": "user", "content": user_input})
    
    with st.spinner("🔍 Processando sua pergunta..."):
        try:
            result = app.invoke({
                "user_input": user_input,
                "conversation_history": st.session_state.conversation
            })
            
            if result.get("natural_response"):
                st.session_state.conversation.append({"role": "assistant", "content": result["natural_response"]})
                with st.chat_message("assistant"):
                    st.write(result["natural_response"])
            
            if result.get("chart"):
                try:
                    st.image(base64.b64decode(result["chart"]))
                    st.session_state.conversation.append({"role": "assistant", "content": "[Gráfico exibido]"})
                except Exception as e:
                    st.error(f"❌ Erro ao exibir gráfico: {str(e)}")
            
            if result.get("sql_query"):
                with st.expander("🔍 Ver SQL gerado"):
                    st.code(result["sql_query"])
            
            if result.get("query_result") is not None:
                with st.expander("📊 Ver resultados completos"):
                    st.dataframe(result["query_result"])
        
        except Exception as e:
            st.error(f"❌ Ocorreu um erro: {str(e)}")

# Sidebar
with st.sidebar:
    st.subheader("🗂 Histórico da Conversa")
    for msg in st.session_state.conversation[-10:]:  # Mostrar apenas últimos 10
        if msg["role"] == "user":
            st.markdown(f"**Você**: {msg['content']}")
        else:
            st.markdown(f"**Assistente**: {msg['content'][:100]}...")
    
    if st.session_state.data_source:
        with st.expander("📝 Esquema de Dados"):
            schema = get_schema()
            if schema:
                st.text(schema)
            else:
                st.warning("Nenhum esquema disponível")
    
    if st.button("🧹 Limpar Conversa"):
        st.session_state.conversation = []
        st.experimental_rerun()