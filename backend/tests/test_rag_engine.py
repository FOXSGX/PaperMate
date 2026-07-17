from app.core.rag_engine import RagEngine


def test_rag_engine_indexes_and_retrieves(tmp_path):
    engine = RagEngine(str(tmp_path))
    count = engine.index_document("doc_demo", "Transformer 模型用于医学图像分割。RAG 用于文档问答。", "demo.txt")

    assert count >= 1

    answer, citations = engine.answer("doc_demo", "医学图像分割用什么模型？")
    assert "医学图像分割" in answer
    assert citations
