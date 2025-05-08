# 🤖 Sistema Inteligente NL2SQL

Este projeto é um sistema interativo de análise de dados via linguagem natural, que transforma perguntas em linguagem humana em consultas SQL, executa essas consultas e apresenta os resultados de forma compreensível e visual.

---

## 🔍 Visão Geral

O sistema **NL2SQL** oferece uma interface intuitiva desenvolvida com **Streamlit**, onde usuários podem carregar arquivos de dados (CSV, Excel ou SQLite), fazer perguntas em linguagem natural e receber respostas precisas, visualizações automáticas e análises descritivas. Ele utiliza **LangGraph**, **LangChain** e modelos da **OpenAI** para orquestrar agentes inteligentes em um fluxo estruturado de compreensão, geração de SQL, execução e resposta.

---

## 🧩 Problema e Solução

### ❗ Problema

Profissionais sem conhecimento técnico em SQL ou análise de dados estruturada frequentemente enfrentam dificuldades ao tentar extrair insights de suas bases de dados.

### ✅ Solução

Este projeto resolve esse desafio com um sistema **NL2SQL multimodal**, permitindo que usuários interajam diretamente com seus dados em linguagem natural. O sistema:

- Identifica a intenção da pergunta (consulta, visualização, acompanhamento, pergunta geral).
- Converte a pergunta em SQL considerando o esquema do banco.
- Executa a consulta sobre os dados carregados.
- Gera uma resposta textual explicativa.
- Apresenta gráficos automáticos quando aplicável.
- Lida com perguntas de acompanhamento em contexto.

---

## ⚙️ Processo

O sistema é baseado em uma arquitetura de agentes coordenados por um grafo de estados, com os seguintes módulos principais:

### 1. **Classificador de Intenção**
- Identifica o tipo da pergunta: `nl2sql`, `visual`, `followup` ou `geral`.

### 2. **Gerador de SQL (NL2SQL)**
- Traduz perguntas em linguagem natural em comandos SQL, com base no esquema do dataset carregado.

### 3. **Executor SQL**
- Executa as queries SQL em arquivos CSV, Excel ou SQLite usando `pandasql` ou `sqlite3`.

### 4. **Gerador de Resposta Natural**
- Transforma os resultados da consulta em uma resposta textual explicativa e acessível.

### 5. **Gerador de Visualizações**
- Cria automaticamente gráficos relevantes com `matplotlib`, retornando uma imagem em base64.

### 6. **Resposta Geral**
- Responde perguntas que não envolvem dados, como explicações de conceitos.

### 7. **Manipulador de Acompanhamento**
- Recontextualiza perguntas subsequentes considerando o histórico de conversa.

### 🛠️ Tecnologias e Bibliotecas

- `Streamlit` para a interface interativa
- `LangGraph` e `LangChain` para a orquestração dos agentes
- `OpenAI GPT-3.5 Turbo` como modelo de linguagem
- `Pandas`, `pandasql`, `matplotlib` para manipulação e visualização de dados
- `sqlite3`, `base64`, `tempfile` para integração com dados locais

---

## 📈 Resultados

- ✅ Conversão eficaz de linguagem natural em SQL em diferentes formatos de dados.
- ✅ Geração automática de gráficos intuitivos para facilitar a visualização.
- ✅ Respostas explicativas e contextuais para perguntas sobre os dados.
- ✅ Manutenção de histórico de conversação com perguntas de acompanhamento contextualizadas.
- ✅ Interface amigável, sem necessidade de conhecimento técnico prévio.

---

## 🧠 Conclusões

Este sistema NL2SQL representa um passo importante na democratização do acesso à análise de dados. A combinação de interfaces naturais, agentes inteligentes e execução automatizada permite que qualquer pessoa explore dados com perguntas simples, transformando a complexidade da análise em uma experiência conversacional fluida.

---

## ▶️ Como Usar

1. Clone o repositório e instale as dependências:

```bash
pip install -r requirements.txt
