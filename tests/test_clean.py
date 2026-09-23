import sys
import os

# Add src to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from clean import split_sentences, clean_text

def test_sentence_splitter():
    # 1. Treats । and . both as sentence boundaries
    text1 = "यह पहला वाक्य है। यह दूसरा वाक्य है. यह तीसरा है?"
    sents1 = split_sentences(text1)
    assert len(sents1) == 3
    assert sents1[0] == "यह पहला वाक्य है।"
    assert sents1[1] == "यह दूसरा वाक्य है."
    assert sents1[2] == "यह तीसरा है?"
    
    # 2. Does not break on numbers-with-periods (e.g. 1.5)
    text2 = "उन्होंने 1.5 करोड़ लोगों को प्रेरित किया। यह सच है।"
    sents2 = split_sentences(text2)
    assert len(sents2) == 2
    assert sents2[0] == "उन्होंने 1.5 करोड़ लोगों को प्रेरित किया।"
    assert sents2[1] == "यह सच है।"
    
    # 3. Does not break on abbreviations
    text3 = "ए.पी.जे. अब्दुल कलाम भारत के ग्यारहवें राष्ट्रपति थे। डॉ. कलाम महान थे।"
    sents3 = split_sentences(text3)
    assert len(sents3) == 2
    assert sents3[0] == "ए.पी.जे. अब्दुल कलाम भारत के ग्यारहवें राष्ट्रपति थे।"
    assert sents3[1] == "डॉ. कलाम महान थे।"
    
    print("test_sentence_splitter passed!")

def test_clean_text():
    # Test stripping extraction artifacts
    raw = "मेगामाइंड्स एआई सॉल्यूूशंस · नमूना RAG दस्तावेज़\nकुछ पाठ\nनमूना RAG दस्तावेज़\nऔर कुछ पाठ"
    cleaned = clean_text(raw)
    assert "मेगामाइंड्स" not in cleaned
    assert "नमूना RAG" not in cleaned
    assert "कुछ पाठ और कुछ पाठ" in cleaned
    
    print("test_clean_text passed!")

if __name__ == "__main__":
    test_sentence_splitter()
    test_clean_text()
