# 🤖 Agente NL2SQL com LangGraph + RAG Avançado

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema de agentes de IA para conversão de linguagem natural em SQL (NL2SQL), utilizando arquitetura RAG avançada com múltiplos agentes orquestrados via LangGraph.

---

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Tecnologias](#-tecnologias)
- [Instalação](#-instalação)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Agentes](#-agentes)
- [Pipeline RAG](#-pipeline-rag)
- [Observabilidade](#-observabilidade)
- [Contribuição](#-contribuição)

---

## 🎯 Sobre o Projeto

Este projeto é uma **Prova de Conceito (POC)** que demonstra a capacidade de agentes de IA em interpretar perguntas em linguagem natural e gerar consultas SQL automaticamente. O sistema suporta múltiplas fontes de dados e utiliza uma arquitetura avançada de RAG (Retrieval-Augmented Generation) para melhorar a precisão das consultas geradas.

### Principais Capacidades

- 📝 Interpretação de perguntas em português e inglês
- 🔄 Geração automática de SQL para múltiplas fontes de dados
- 💬 Suporte a perguntas de acompanhamento (follow-ups)
- 📊 Geração automática de visualizações (gráficos)
- 🔍 Recuperação semântica avançada com BM25 + Dense Retrieval
- 🛡️ Validação e segurança nas consultas SQL
- 📈 Observabilidade completa via LangSmith

---

## ✨ Funcionalidades

| Funcionalidade | Descrição |
|----------------|-----------|
| **NL2SQL** | Converte perguntas naturais em consultas SQL precisas |
| **Multi-Fonte** | Suporta PostgreSQL, MySQL, SQLite, CSV e Excel |
| **RAG Avançado** | Pipeline com BM25, Dense Retrieval, RRF e Flash Reranker |
| **Follow-ups** | Mantém contexto para perguntas sequenciais |
| **Visualização** | Gera gráficos automáticos (barras, linhas, pizza) |
| **Validação** | Guardrails para segurança e qualidade do SQL |
| **Observabilidade** | Rastreamento completo via LangSmith |

---

## 🏗️ Arquitetura

┌─────────────────────────────────────────────────────────────┐ │ STREAMLIT (UI) │ │ Porta: 8501 │ └──────────────────────┬──────────────────────────────────────┘ │ ▼ ┌─────────────────────────────────────────────────────────────┐ │ FASTAPI (Backend) │ │ Porta: 8000 │ └──────────────────────┬──────────────────────────────────────┘ │ ▼ ┌─────────────────────────────────────────────────────────────┐ │ LANGGRAPH (Agentes) │ │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │ │ │ Router │ │ Schema │ │ RAG │ │ NL2SQL │ │ │ │ Agent │ │ Agent │ │ Agent │ │ Agent │ │ │ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ │ │ └───────────┴───────────┴───────────┘ │ │ │ │ │ ▼ │ │ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ │ │ │ SQL │ │ SQL │ │ Exp │ │ Viz │ │ │ │Validator│ │Executor │ │ Agent │ │ Agent │ │ │ └─────────┘ └─────────┘ └─────────┘ └─────────┘ │ └──────────────────────┬──────────────────────────────────────┘ │ ┌──────────────┼──────────────┐ ▼ ▼ ▼ ┌─────────┐ ┌─────────┐ ┌─────────────┐ │ Qdrant │ │ Banco │ │ LangSmith │ │ (RAG) │ │ Dados │ │(Observabil.)│ │ Porta: │ │ │ │ │ │ 6333 │ │ │ │ │ └─────────┘ └─────────┘ └─────────────┘

---

## 🛠️ Tecnologias

### Core
- **LangGraph** - Orquestração de agentes
- **LangChain** - Framework LLM
- **FastAPI** - Backend API
- **Streamlit** - Interface do usuário

### RAG & Vector Store
- **Qdrant** - Banco de dados vetorial
- **Sentence-Transformers** - Embeddings locais
- **BM25** - Busca lexical
- **Rank-BM25** - Fusão de rankings

### Banco de Dados
- **SQLAlchemy** - ORM e conexões SQL
- **Pandas** - Manipulação de dados
- **DuckDB** - Execução SQL em arquivos
- **OpenPyXL** - Leitura de Excel

### Visualização & Observabilidade
- **Plotly** - Gráficos interativos
- **LangSmith** - Rastreamento e monitoramento

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.9+
- Docker e Docker Compose
- Chave de API OpenAI
- Chave de API LangSmith (opcional, para observabilidade)

Exemplos de Perguntas

"Qual o total de vendas por mês em 2024?"
"Mostre os top 10 clientes com maior faturamento"
"E se eu filtrar apenas por São Paulo?"
"Gere um gráfico de linha das vendas ao longo do tempo"