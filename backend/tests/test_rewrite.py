from app.doc_processor.rewrite import rewrite_text


def test_rewrite_text_academic_replacement():
    result = rewrite_text("本文说明这个方法可以提高结果。")
    assert "本研究" in result
    assert "表明" in result
    assert "技术路径" in result
