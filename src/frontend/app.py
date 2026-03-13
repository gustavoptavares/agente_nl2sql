import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Optional, Dict, Any
import uuid
import os
import tempfile

API_URL = "http://localhost:8000/api/v1"
UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "nl2sql_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.set_page_config(
    page_title="NL2SQL Assistant",
    page_icon="🔍",
    layout="wide"
)

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "connection_string" not in st.session_state:
    st.session_state.connection_string = None
if "data_source" not in st.session_state:
    st.session_state.data_source = "sqlite"
if "db_schema" not in st.session_state:
    st.session_state.db_schema = None

st.title("🔍 NL2SQL Assistant")
st.markdown("Faça perguntas em linguagem natural sobre seus dados")

with st.sidebar:
    st.header("⚙️ Configurações")
    
    data_source = st.selectbox(
        "Fonte de Dados",
        ["sqlite", "postgresql", "mysql", "csv", "excel"],
        index=["sqlite", "postgresql", "mysql", "csv", "excel"].index(st.session_state.data_source)
    )
    st.session_state.data_source = data_source
    
    st.divider()
    st.subheader("📁 Conexão")
    
    if data_source == "sqlite":
        upload_option = st.radio(
            "Opção de conexão",
            ["Upload de arquivo .db", "String de conexão manual"]
        )
        
        if upload_option == "Upload de arquivo .db":
            uploaded_db = st.file_uploader(
                "Upload do banco SQLite (.db)",
                type=["db", "sqlite", "sqlite3"],
                key="sqlite_upload"
            )
            
            if uploaded_db:
                file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{uploaded_db.name}")
                with open(file_path, "wb") as f:
                    f.write(uploaded_db.getvalue())
                st.session_state.connection_string = f"sqlite:///{file_path}"
                st.success(f"✅ Banco '{uploaded_db.name}' carregado!")
                
                try:
                    from sqlalchemy import create_engine, inspect
                    engine = create_engine(st.session_state.connection_string)
                    inspector = inspect(engine)
                    tables = inspector.get_table_names()
                    st.session_state.db_schema = tables
                    
                    with st.expander("📋 Tabelas disponíveis"):
                        for table in tables:
                            cols = inspector.get_columns(table)
                            col_names = [c["name"] for c in cols]
                            st.markdown(f"**{table}**: {', '.join(col_names)}")
                except Exception as e:
                    st.error(f"Erro ao ler schema: {e}")
        else:
            connection_string = st.text_input(
                "String de Conexão SQLite",
                value=st.session_state.connection_string or "sqlite:///./data/northwind.db",
                placeholder="sqlite:///./caminho/para/banco.db"
            )
            st.session_state.connection_string = connection_string
            
            if st.button("🔗 Conectar"):
                try:
                    from sqlalchemy import create_engine, inspect
                    engine = create_engine(connection_string)
                    inspector = inspect(engine)
                    tables = inspector.get_table_names()
                    st.session_state.db_schema = tables
                    st.success(f"✅ Conectado! {len(tables)} tabelas encontradas.")
                    
                    with st.expander("📋 Tabelas disponíveis"):
                        for table in tables:
                            cols = inspector.get_columns(table)
                            col_names = [c["name"] for c in cols]
                            st.markdown(f"**{table}**: {', '.join(col_names)}")
                except Exception as e:
                    st.error(f"Erro de conexão: {e}")
    
    elif data_source in ["postgresql", "mysql"]:
        st.text_input("Host", value="localhost", key="db_host")
        st.text_input("Porta", value="5432" if data_source == "postgresql" else "3306", key="db_port")
        st.text_input("Banco de Dados", key="db_name")
        st.text_input("Usuário", key="db_user")
        st.text_input("Senha", type="password", key="db_password")
        
        if st.button("🔗 Conectar"):
            if data_source == "postgresql":
                conn_str = f"postgresql://{st.session_state.db_user}:{st.session_state.db_password}@{st.session_state.db_host}:{st.session_state.db_port}/{st.session_state.db_name}"
            else:
                conn_str = f"mysql+pymysql://{st.session_state.db_user}:{st.session_state.db_password}@{st.session_state.db_host}:{st.session_state.db_port}/{st.session_state.db_name}"
            
            st.session_state.connection_string = conn_str
            st.success("✅ String de conexão configurada!")
    
    elif data_source == "csv":
        uploaded_csv = st.file_uploader(
            "Upload do arquivo CSV",
            type=["csv"],
            key="csv_upload"
        )
        
        if uploaded_csv:
            file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{uploaded_csv.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_csv.getvalue())
            st.session_state.connection_string = file_path
            st.success(f"✅ Arquivo '{uploaded_csv.name}' carregado!")
            
            try:
                df = pd.read_csv(file_path)
                with st.expander("📋 Preview dos dados"):
                    st.dataframe(df.head(10))
                    st.markdown(f"**Colunas**: {', '.join(df.columns.tolist())}")
                    st.markdown(f"**Linhas**: {len(df)}")
            except Exception as e:
                st.error(f"Erro ao ler CSV: {e}")
    
    elif data_source == "excel":
        uploaded_excel = st.file_uploader(
            "Upload do arquivo Excel",
            type=["xlsx", "xls"],
            key="excel_upload"
        )
        
        if uploaded_excel:
            file_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}_{uploaded_excel.name}")
            with open(file_path, "wb") as f:
                f.write(uploaded_excel.getvalue())
            st.session_state.connection_string = file_path
            st.success(f"✅ Arquivo '{uploaded_excel.name}' carregado!")
            
            try:
                xl = pd.ExcelFile(file_path)
                with st.expander("📋 Planilhas disponíveis"):
                    for sheet in xl.sheet_names:
                        df = pd.read_excel(file_path, sheet_name=sheet)
                        st.markdown(f"**{sheet}**: {', '.join(df.columns.tolist())} ({len(df)} linhas)")
            except Exception as e:
                st.error(f"Erro ao ler Excel: {e}")
    
    st.divider()
    
    if st.session_state.connection_string:
        st.success("🟢 Fonte de dados configurada")
    else:
        st.warning("🟡 Configure uma fonte de dados")
    
    st.divider()
    
    if st.button("🗑️ Limpar Conversa"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    if st.button("🔄 Resetar Conexão"):
        st.session_state.connection_string = None
        st.session_state.db_schema = None
        st.rerun()

def create_chart(viz_config: Dict[str, Any]) -> Optional[go.Figure]:
    if not viz_config or "data" not in viz_config:
        return None
    
    df = pd.DataFrame(viz_config["data"])
    if df.empty:
        return None
    
    chart_type = viz_config.get("chart_type", "bar")
    x_col = viz_config.get("x_column")
    y_col = viz_config.get("y_column")
    title = viz_config.get("title", "Resultado")
    
    if not x_col or x_col not in df.columns:
        x_col = df.columns[0]
    if not y_col or y_col not in df.columns:
        y_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]
    
    if chart_type == "bar":
        fig = px.bar(df, x=x_col, y=y_col, title=title)
    elif chart_type == "line":
        fig = px.line(df, x=x_col, y=y_col, title=title)
    elif chart_type == "pie":
        fig = px.pie(df, names=x_col, values=y_col, title=title)
    elif chart_type == "scatter":
        fig = px.scatter(df, x=x_col, y=y_col, title=title)
    else:
        fig = px.bar(df, x=x_col, y=y_col, title=title)
    
    return fig

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sql" in message and message["sql"]:
            with st.expander("📝 SQL Gerado"):
                st.code(message["sql"], language="sql")
        if "data" in message and message["data"]:
            with st.expander("📊 Dados"):
                st.dataframe(pd.DataFrame(message["data"]))
        if "chart" in message and message["chart"]:
            fig = create_chart(message["chart"])
            if fig:
                st.plotly_chart(fig, use_container_width=True)

if not st.session_state.connection_string:
    st.info("👈 Configure uma fonte de dados na barra lateral para começar.")
else:
    if prompt := st.chat_input("Digite sua pergunta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Processando..."):
                try:
                    payload = {
                        "question": prompt,
                        "data_source": st.session_state.data_source,
                        "connection_string": st.session_state.connection_string,
                        "session_id": st.session_state.session_id
                    }
                    
                    response = requests.post(f"{API_URL}/query", json=payload, timeout=120)
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        st.markdown(result["answer"])
                        
                        if result.get("sql"):
                            with st.expander("📝 SQL Gerado"):
                                st.code(result["sql"], language="sql")
                        
                        if result.get("data"):
                            with st.expander("📊 Dados"):
                                st.dataframe(pd.DataFrame(result["data"]))
                        
                        if result.get("chart"):
                            fig = create_chart(result["chart"])
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result["answer"],
                            "sql": result.get("sql"),
                            "data": result.get("data"),
                            "chart": result.get("chart")
                        })
                    else:
                        error_msg = f"Erro: {response.text}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
                        
                except requests.exceptions.ConnectionError:
                    error_msg = "❌ Erro: API não está rodando. Execute: `uvicorn src.api.main:app --reload --port 8000`"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                except Exception as e:
                    error_msg = f"Erro: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })