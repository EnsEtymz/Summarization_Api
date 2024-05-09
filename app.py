from flask import Flask, render_template,jsonify, request
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.lang.tr.stop_words import STOP_WORDS as TR_STOP_WORDS
from spacy.lang.fr.stop_words import STOP_WORDS as FR_STOP_WORDS
from string import punctuation
from heapq import nlargest
import nltk
from flask_cors import CORS
nltk.download('punkt')

# python -m spacy download en_core_web_sm # web bilgileriyle eğitilmiş İngilizce spacy modeli
# pip install https://huggingface.co/turkish-nlp-suite/tr_core_news_trf/resolve/main/tr_core_news_trf-any-py3-none-any.whl

app = Flask(__name__)
CORS(app)
DETAY = False

# https://www.activestate.com/blog/how-to-do-text-summarization-with-python/
def summarize_text(text, percent, lang='en'):
# spacy modelini yükle 
    if lang=='tr':
        nlp = spacy.load("tr_core_news_trf")
    if lang =='en':
        nlp = spacy.load('en_core_web_sm')
    if lang =='fr':
        nlp = spacy.load('fr_core_news_sm')
        
  
        
# metni spacy modeline göre tokenlarına ayır
    doc = nlp(text)
    if DETAY:
        print(); print (50*'-')
        print("TOKENLAR")
        n=0
        for token in doc:
            n += 1
            if n > 10: break
            # token text ve part-of-speech tag
            print (token.text, "-->", token.pos_)
    # tokenları metin parçalarına dönüştür
    tokens=[token.text for token in doc]
    if DETAY:
        print(); print (50*'-')
    print("TOKEN.TEXT LİSTESİ")
    print (tokens[:10])
    # sözcük frekanslarını bul
    word_frequencies={}    
    if lang == 'tr':
        WORDS = TR_STOP_WORDS
    if lang == 'en':
        WORDS = STOP_WORDS
    if lang == 'fr':
        WORDS = FR_STOP_WORDS
    for word in doc:
        if word.text.lower() not in list (WORDS):
            if word.text.lower() not in punctuation:
                if word.text not in word_frequencies.keys():
                    word_frequencies[word.text] = 1
                else:
                    word_frequencies[word.text] += 1
    # Bulunan en yüksek frekans
    max_frequency=max(word_frequencies.values())
    if DETAY:
        print(); print (50*'-')
        print("max_frequency= ", max_frequency)
    # frekans değerlerini normalize et
    for word in word_frequencies.keys():
        word_frequencies[word]=word_frequencies[word]/max_frequency
        
    if DETAY:
        print(); print (50*'-')
        print("NORMALİZE EDİLMİŞ FREKANSLAR")
        n=0
        for w, f in word_frequencies.items():
            n += 1
            if n>10: break
            print (w, f)
        
    # cümle tokenlarını oluştur
    sentence_tokens= [sent for sent in doc.sents]
    if DETAY:
        print(); print (50*'-')
        print("CÜMLE TOKENLARI")
        print (sentence_tokens[:10])
    # cümle skorlarını hesaplat
    sentence_scores = {}
    for sent in sentence_tokens:
        for word in sent:
            if word.text.lower() in word_frequencies.keys():
                if sent not in sentence_scores.keys():
                    sentence_scores[sent]=word_frequencies[word.text.lower()]
                else:
                    sentence_scores[sent]+=word_frequencies[word.text.lower()]
                    
    if DETAY:
        print(); print (50*'-')
        print("CÜMLE SKORLARI")
        n=0
        for w, f in sentence_scores.items():
            n += 1 
            if n>10: break
            print (w, f)
    # en yüksek skora sahip cümlelerin percent oranını ayır
    select_length=int (len(sentence_tokens)*percent)
    summary=nlargest (select_length, sentence_scores, key=sentence_scores.get)
    # en yüksek skora sahip cümleleri bir araya getir
    final_summary=[word.text for word in summary]
    summary=''.join(final_summary)
    return summary





@app.route('/')
def index():
    return 'enes'



@app.route('/summary', methods=['POST'])
def metin_summary_sonuc():
    json_data = request.get_json()
    lang = json_data.get('lang','tr')
    text = json_data.get('text', '')
    percent = json_data.get('percent', 0.4)  # Default değer 0.4
    # Metin özetleme işlemini gerçekleştir
    rtext = summarize_text(text, percent, lang)
  

    # Sonucu JSON formatında döndür
    return jsonify({'summary': rtext, 'oran': f'%{percent*100}'})




if __name__ == "__main__":
    app.run(debug=False)