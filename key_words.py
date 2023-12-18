import yake

extractor = yake.KeywordExtractor(lan="en",     # Задаем язык (английский)
                                  n=3,           # Максимальное количество слов в ключевой фразе
                                  dedupLim=0.3,   # Порог похожести слов
                                  top=10)         # Количество ключевых слов для извлечения

sentence = 'one Get it from your two employer It!x27s better and cheaper than what you can get in the market. You are ! allowed to supplement  this may or may not make sense but your final coverage will ! be a lot cheaper if you start with employer ? insurance'

def key_words(sentence):
    key_tuples = extractor.extract_keywords(sentence)  # Извлекаем ключевые фразы из предложения
    key_words = []

    for key_tuple in key_tuples:
        key_words.append(key_tuple[0])

    return key_words

print(key_words(sentence))
