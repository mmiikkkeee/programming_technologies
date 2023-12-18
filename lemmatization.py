import spacy

sentence = 'one Get it from your two employer It!x27s better and cheaper than what you can get in the market. You are ! allowed to supplement  this may or may not make sense but your final coverage will ! be a lot cheaper if you start with employer ? insurance'

def lemmatization(sentence):
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner']) # Загружаем английскую модель языка Spacy с отключенными компонентами 'parser' и 'ner', так как они не нужны для лемматизации
    doc = nlp(sentence)
    sentence = " ".join([token.lemma_ for token in doc]) # Проходим по каждому токену в предложении, извлекаем его лемму и объединяем в строку
    return sentence

print(lemmatization(sentence))
