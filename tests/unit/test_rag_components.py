import pytest
from unittest.mock import patch, MagicMock


class TestBM25Retriever:

    def test_bm25_search_returns_results(self):
        from src.rag.bm25_retriever import index_documents, bm25_search

        docs = [
            {"content": "SELECT id FROM vendas", "metadata": {"type": "sql"}},
            {"content": "SELECT nome FROM clientes", "metadata": {"type": "sql"}},
            {"content": "Total de vendas por cliente", "metadata": {"type": "question"}}
        ]

        index_documents(docs)
        results = bm25_search("vendas", top_k=2)

        assert len(results) <= 2
        assert all("content" in r for r in results)

    def test_bm25_search_with_filter(self):
        from src.rag.bm25_retriever import index_documents, bm25_search

        docs = [
            {"content": "SELECT id FROM vendas", "metadata": {"type": "sql"}},
            {"content": "Total de vendas", "metadata": {"type": "question"}}
        ]

        index_documents(docs)
        results = bm25_search("vendas", top_k=10, filter_dict={"type": "sql"})

        for r in results:
            assert r.get("metadata", {}).get("type") == "sql"

    def test_bm25_search_empty_corpus(self):
        from src.rag.bm25_retriever import index_documents, bm25_search

        index_documents([])
        results = bm25_search("vendas", top_k=5)

        assert results == []

    def test_bm25_tokenize(self):
        from src.rag.bm25_retriever import tokenize

        tokens = tokenize("SELECT id FROM vendas")

        assert "select" in tokens
        assert "vendas" in tokens

    def test_bm25_results_have_source(self):
        from src.rag.bm25_retriever import index_documents, bm25_search

        docs = [{"content": "vendas totais", "metadata": {}}]
        index_documents(docs)

        results = bm25_search("vendas", top_k=5)

        for r in results:
            assert r["source"] == "bm25"


class TestReranker:

    @patch('src.rag.reranker.get_reranker')
    def test_rerank_documents(self, mock_get_reranker):
        from src.rag.reranker import rerank_documents

        mock_model = MagicMock()
        mock_model.predict.return_value = [0.9, 0.5, 0.7]
        mock_get_reranker.return_value = mock_model

        docs = [
            {"content": "SELECT id FROM vendas WHERE valor > 100"},
            {"content": "Total de vendas por cliente"},
            {"content": "Relatório de vendas mensal"}
        ]

        results = rerank_documents("vendas com valor alto", docs)

        assert len(results) == 3
        assert all("rerank_score" in r for r in results)
        assert results[0]["rerank_score"] >= results[1]["rerank_score"]

    def test_rerank_empty_list(self):
        from src.rag.reranker import rerank_documents

        results = rerank_documents("query", [])

        assert results == []

    @patch('src.rag.reranker.get_reranker')
    def test_rerank_with_top_k(self, mock_get_reranker):
        from src.rag.reranker import rerank_documents

        mock_model = MagicMock()
        mock_model.predict.return_value = [0.9, 0.5, 0.7]
        mock_get_reranker.return_value = mock_model

        docs = [
            {"content": "doc1"},
            {"content": "doc2"},
            {"content": "doc3"}
        ]

        results = rerank_documents("query", docs, top_k=2)

        assert len(results) == 2


class TestHybridRetriever:

    @patch('src.rag.hybrid_retriever.bm25_search')
    @patch('src.rag.hybrid_retriever.dense_search')
    @patch('src.rag.hybrid_retriever.rerank_documents')
    def test_hybrid_search_combines_results(self, mock_rerank, mock_dense, mock_bm25):
        from src.rag.hybrid_retriever import hybrid_search

        mock_bm25.return_value = [{"content": "doc1", "score": 0.9}]
        mock_dense.return_value = [{"content": "doc2", "score": 0.8}]
        mock_rerank.return_value = [
            {"content": "doc1", "rerank_score": 0.95},
            {"content": "doc2", "rerank_score": 0.85}
        ]

        results = hybrid_search("query", top_k=2)

        assert len(results) == 2
        mock_bm25.assert_called_once()
        mock_dense.assert_called_once()
        mock_rerank.assert_called_once()

    @patch('src.rag.hybrid_retriever.bm25_search')
    @patch('src.rag.hybrid_retriever.dense_search')
    @patch('src.rag.hybrid_retriever.rerank_documents')
    def test_hybrid_search_with_filter(self, mock_rerank, mock_dense, mock_bm25):
        from src.rag.hybrid_retriever import hybrid_search

        mock_bm25.return_value = []
        mock_dense.return_value = []
        mock_rerank.return_value = []

        results = hybrid_search("query", top_k=5, filter_dict={"db_type": "sqlite"})

        assert results == []
        mock_bm25.assert_called_once_with(query="query", top_k=10, filter_dict={"db_type": "sqlite"})
        mock_dense.assert_called_once_with(query="query", top_k=10, filter_dict={"db_type": "sqlite"})


class TestRRF:

    def test_reciprocal_rank_fusion(self):
        from src.rag.hybrid_retriever import reciprocal_rank_fusion

        results_list = [
            [{"content": "doc1"}, {"content": "doc2"}],
            [{"content": "doc2"}, {"content": "doc3"}]
        ]

        fused = reciprocal_rank_fusion(results_list)

        assert len(fused) == 3
        assert all("rrf_score" in r for r in fused)
        doc2 = next(r for r in fused if r["content"] == "doc2")
        doc1 = next(r for r in fused if r["content"] == "doc1")
        assert doc2["rrf_score"] > doc1["rrf_score"]

    def test_reciprocal_rank_fusion_empty(self):
        from src.rag.hybrid_retriever import reciprocal_rank_fusion

        fused = reciprocal_rank_fusion([[], []])

        assert fused == []