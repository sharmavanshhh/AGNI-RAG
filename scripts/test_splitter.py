import re

def split_sentences(text):
    boundaries = re.finditer(r'([।?!]|\.)', text)
    sentences = []
    start = 0
    for b in boundaries:
        char = b.group(1)
        idx = b.start()
        
        if char == '.':
            # Check number
            if idx > 0 and idx + 1 < len(text) and text[idx-1].isdigit() and text[idx+1].isdigit():
                continue
                
            # Check abbreviation
            last_delim = idx - 1
            while last_delim >= 0 and not (text[last_delim].isspace() or text[last_delim] == '.'):
                last_delim -= 1
            word = text[last_delim+1:idx]
            
            # Clean punctuation from word start
            word = re.sub(r'^[^\w\u0900-\u097F]+', '', word)
            
            abbrevs = {'डॉ', 'प्रो', 'श्री', 'मि', 'मिसेज', 'पं', 'प्रोफ'}
            verbs = {'था', 'थी', 'थे', 'हो', 'है', 'हैं', 'दी', 'दीं', 'ली', 'लीं', 'की', 'कीं', 'लूंगा'}
            
            if word in abbrevs:
                continue
                
            if word not in verbs:
                base_chars = [c for c in word if ('\u0904' <= c <= '\u0939') or ('\u0958' <= c <= '\u095F') or ('a' <= c.lower() <= 'z') or ('A' <= c <= 'Z')]
                if len(base_chars) <= 1:
                    continue
                    
        end = b.end()
        sentences.append(text[start:end].strip())
        start = end
        
    if start < len(text):
        remainder = text[start:].strip()
        if remainder:
            sentences.append(remainder)
            
    return sentences

def test_split():
    texts = [
        "ए.पी.जे. अब्दुल कलाम भारत के राष्ट्रपति थे। उन्होंने 1.5 करोड़ लोगों को प्रेरित किया।",
        "डॉ. कलाम एक महान वैज्ञानिक थे. यह एक सच है।",
        "रामेश्वरम में उनका जन्म हुआ! क्या आपको पता है?",
        "मैं खुश था. वह दुखी थी."
    ]
    for t in texts:
        print(f"Original: {t}")
        sents = split_sentences(t)
        for i, s in enumerate(sents):
            print(f"  {i+1}: {s}")

if __name__ == '__main__':
    test_split()
