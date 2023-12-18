import pandas as pd
import re
import difflib
import spacy
import yake
import nltk
import torch
import json
from nltk.tokenize import word_tokenize
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from better_profanity import profanity
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor

# Функция очистки данных от ненужных символов
def clearning(data):
    for comments in data['comments']:
        for comment in comments:
            comment['text'] = re.sub(r"[^a-zA-Z0-9 !?]", "", comment['text'])
    return data

# Функция лемматизации текста
def lemmatization(sentence):
    nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])
    doc = nlp(sentence)
    sentence = " ".join([token.lemma_ for token in doc])
    return sentence

# Функция вычисления коэффициента схожести двух текстов
def similarity(s1, s2):
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()

# Функция извлечения ключевых слов из текста
def key_words(sentence):
    key_tuples = extractor.extract_keywords(sentence)
    key_words = []

    for tuple in key_tuples:
        key_words.append(tuple[0])

    return key_words

# Функция определения частей речи в предложении
def tagging_words_from_sentence(sentence):
    adjectives_count, adverbs_count, nouns_count, verbs_count, numerals_count = 0, 0, 0, 0, 0

    words_in_sentence = word_tokenize(sentence)
    tags_of_words = nltk.pos_tag(words_in_sentence)

    for word in tags_of_words:
        if word[1] == 'JJ':
            adjectives_count += 1
        if word[1] == 'RB':
            adverbs_count += 1
        if word[1] == 'NN':
            nouns_count += 1
        if word[1] == 'VB':
            verbs_count += 1
        if word[1] == 'CD':
            numerals_count += 1

    return {'adjectives_count': adjectives_count, 'adverbs_count': adverbs_count, 'nouns_count': nouns_count, 'verbs_count': verbs_count, 'numerals_count': numerals_count}

# Функция подсчета знаков пунктуации в предложении
def counting_punctuation_marks(sentence):
    words = sentence.split()
    question_marks_count, exclamation_marks_count = 0, 0

    for word in words:
        for symb in word:
            if symb == '!':
                question_marks_count += 1
            if symb == '?':
                exclamation_marks_count += 1

    return {'question_marks_count': question_marks_count, 'exclamation_marks_count': exclamation_marks_count}

# Функция определения настроения текста с использованием BERT
def mood_of_the_text(sentence):
    tokens = tokenizer.encode(sentence, return_tensors='pt')
    result = model(tokens)
    correlation = int(torch.argmax(result.logits))
    return correlation

# Функция определения наличия нецензурной лексики в тексте
def dirt_tongue(sentence):
    word_counter = sentence.split()
    dirt_score = 0
    for k in range(len(word_counter)):
        current_word = word_counter[k]

        if (profanity.censor(current_word)[0] == '*'):
            dirt_score = 1
        else:
            dirt_score = 0

    return dirt_score

# Функция преобразования результатов в оценки
def scores_result(a):
    a_copy = a.copy()
    a.sort()
    a.reverse()
    scores_result = []
    for i in range(5):
        for j in range(5):
            if a_copy[i] == a[j]:
                scores_result.append(j)
    return scores_result

# Загрузка данных из JSON-файла
data = pd.read_json('/Users/konstantin/Downloads/CL_Cup_IT_Data_Scince_секция_кейс_VK_датасет/ranking_train.jsonl', lines=True)
pd.options.mode.chained_assignment = None

# Выбор первых 5 записей для тестирования
data = data.iloc[:5]

# Инициализация YAKE для извлечения ключевых слов
extractor = yake.KeywordExtractor(lan="en", n=1, dedupLim=0.3, top=10)

# Инициализация BERT для определения настроения текста
tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

# Инициализация списков для хранения результатов анализа
all_count_of_key_words, all_count_of_adjectives, all_count_of_adverbs, all_count_of_nouns = [], [], [], []
all_count_of_verbs, all_count_of_numerals, all_count_of_question_marks, all_count_of_exclamation_marks = [], [], [], []
all_pohozhest, all_dirt_words = [], []

# Анализ каждого поста
for i in tqdm(range(0, len(data))):
    post = data.iloc[i]
    key_wrds = key_words(post['text'])  # ключевые слова
    texts_to_compare = []

    for dct in post['comments']:
        texts_to_compare.append(dct['text'])  # комменты без скора

    scores, count_of_key_words, count_of_adjectives, count_of_adverbs, count_of_nouns, count_of_verbs, count_of_numerals = [], [], [], [], [], [], []
    count_of_question_marks, count_of_exclamation_marks, dirt_words = [], [], []

    # Анализ каждого комментария
    for text in texts_to_compare:
        scores.append(similarity(post['text'], text))  # похожесть коммента на текст поста

        count_key_words = 0

        for word in text:  # проверка на ключевые слова
            for key_word in key_wrds:
                if similarity(word, key_word) > 0.3:  # параметр схожести (поиграться)
                    count_key_words = 1
        count_of_key_words.append(count_key_words)

        parts_of_speech = tagging_words_from_sentence(text)  # количество различных частей речи в тексте
        count_of_adjectives.append(parts_of_speech['adjectives_count'])
        count_of_adverbs.append(parts_of_speech['adverbs_count'])
        count_of_nouns.append(parts_of_speech['nouns_count'])
        count_of_verbs.append(parts_of_speech['verbs_count'])
        count_of_numerals.append(parts_of_speech['numerals_count'])

        punctuation_marks = counting_punctuation_marks(text)
        count_of_question_marks.append(punctuation_marks['question_marks_count'])
        count_of_exclamation_marks.append(punctuation_marks['exclamation_marks_count'])

        dirt_words.append(dirt_tongue(text))

    all_pohozhest.append(scores)
    all_count_of_key_words.append(count_of_key_words)
    all_count_of_adjectives.append(count_of_adjectives)
    all_count_of_adverbs.append(count_of_adverbs)
    all_count_of_nouns.append(count_of_nouns)
    all_count_of_verbs.append(count_of_verbs)
    all_count_of_numerals.append(count_of_numerals)
    all_count_of_question_marks.append(count_of_question_marks)
    all_count_of_exclamation_marks.append(count_of_exclamation_marks)
    all_dirt_words.append(dirt_words)

# Добавление результатов анализа в DataFrame
data['pohozhest'] = all_pohozhest
data['key_words'] = all_count_of_key_words
data['adjectives'] = all_count_of_adjectives
data['adverbs'] = all_count_of_adverbs
data['nouns'] = all_count_of_nouns
data['verbs'] = all_count_of_verbs
data['numerals'] = all_count_of_numerals
data['question_marks'] = all_count_of_question_marks
data['exclamation_marks'] = all_count_of_exclamation_marks
data['dirt_words'] = all_dirt_words

# Создание списка с оценками для каждого комментария в каждом посте
all_targets = []
for x in range(len(data['comments'])):
    targets = []
    for y in range(5):
        targets.append(data['comments'][x][y]['score'])
    all_targets.append(targets)

data['targets'] = all_targets

# Подготовка данных для обучения модели
Xtrain = data.drop('text', axis=1)
Xtrain = Xtrain.drop('comments', axis=1)
ytrain = data['targets']

# Создание DataFrame для хранения признаков и меток
df = pd.DataFrame()

# Преобразование данных для обучения
for i in range(0, len(Xtrain)):
    for j in range(5):
        a = {}
        line = Xtrain.iloc[i]
        a['pohozhest'] = line['pohozhest'][j]
        a['key_words'] = line['key_words'][j]
        a['adjectives'] = line['adjectives'][j]
        a['adverbs'] = line['adverbs'][j]
        a['nouns'] = line['nouns'][j]
        a['verbs'] = line['verbs'][j]
        a['numerals'] = line['numerals'][j]
        a['question_marks'] = line['question_marks'][j]
        a['exclamation_marks'] = line['exclamation_marks'][j]
        a['dirt_words'] = line['dirt_words'][j]
        a['targets'] = line['targets'][j]
        df = df.append(a, ignore_index=True)

# Вывод преобразованных данных
print(df)

# Подготовка данных для тестирования
ytrain = df['targets']
Xtrain = df.drop('targets', axis=1)

# Загрузка данных для тестирования
datatest = pd.read_json('/Users/konstantin/Downloads/CL_Cup_IT_Data_Scince_секция_кейс_VK_датасет/ranking_train.jsonl', lines=True)

# Выбор первых 10 записей для тестирования
datatest = data.iloc[:10]

# Инициализация YAKE для извлечения ключевых слов
extractor = yake.KeywordExtractor(lan="en", n=1, dedupLim=0.3, top=10)

# Инициализация BERT для определения настроения текста
tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

# Инициализация списков для хранения результатов анализа
all_count_of_key_words, all_count_of_adjectives, all_count_of_adverbs, all_count_of_nouns = [], [], [], []
all_count_of_verbs, all_count_of_numerals, all_count_of_question_marks, all_count_of_exclamation_marks = [], [], [], []
all_pohozhest, all_dirt_words = [], []

# Анализ каждого поста для тестирования
for i in tqdm(range(0, len(data))):
    post = data.iloc[i]
    key_wrds = key_words(post['text'])  # ключевые слова
    texts_to_compare = []

    for dct in post['comments']:
        texts_to_compare.append(dct['text'])  # комменты без скора

    scores, count_of_key_words, count_of_adjectives, count_of_adverbs, count_of_nouns, count_of_verbs, count_of_numerals = [], [], [], [], [], [], []
    count_of_question_marks, count_of_exclamation_marks, dirt_words = [], [], []

    # Анализ каждого комментария для тестирования
    for text in texts_to_compare:
        scores.append(similarity(post['text'], text))  # похожесть коммента на текст поста

        count_key_words = 0

        for word in text:  # проверка на ключевые слова
            for key_word in key_wrds:
                if similarity(word, key_word) > 0.3:  # параметр схожести (поиграться)
                    count_key_words = 1
        count_of_key_words.append(count_key_words)

        parts_of_speech = tagging_words_from_sentence(text)  # количество различных частей речи в тексте
        count_of_adjectives.append(parts_of_speech['adjectives_count'])
        count_of_adverbs.append(parts_of_speech['adverbs_count'])
        count_of_nouns.append(parts_of_speech['nouns_count'])
        count_of_verbs.append(parts_of_speech['verbs_count'])
        count_of_numerals.append(parts_of_speech['numerals_count'])

        punctuation_marks = counting_punctuation_marks(text)
        count_of_question_marks.append(punctuation_marks['question_marks_count'])
        count_of_exclamation_marks.append(punctuation_marks['exclamation_marks_count'])

        dirt_words.append(dirt_tongue(text))

    all_pohozhest.append(scores)
    all_count_of_key_words.append(count_of_key_words)
    all_count_of_adjectives.append(count_of_adjectives)
    all_count_of_adverbs.append(count_of_adverbs)
    all_count_of_nouns.append(count_of_nouns)
    all_count_of_verbs.append(count_of_verbs)
    all_count_of_numerals.append(count_of_numerals)
    all_count_of_question_marks.append(count_of_question_marks)
    all_count_of_exclamation_marks.append(count_of_exclamation_marks)
    all_dirt_words.append(dirt_words)

# Добавление результатов анализа в DataFrame для тестирования
datatest['pohozhest'] = all_pohozhest
datatest['key_words'] = all_count_of_key_words
datatest['adjectives'] = all_count_of_adjectives
datatest['adverbs'] = all_count_of_adverbs
datatest['nouns'] = all_count_of_nouns
datatest['verbs'] = all_count_of_verbs
datatest['numerals'] = all_count_of_numerals
datatest['question_marks'] = all_count_of_question_marks
datatest['exclamation_marks'] = all_count_of_exclamation_marks
datatest['dirt_words'] = all_dirt_words

# Создание списка с оценками для каждого комментария в каждом посте для тестирования
all_targets = []
for x in range(len(datatest['comments'])):
    targets = []
    for y in range(5):
        targets.append(datatest['comments'][x][y]['score'])
    all_targets.append(targets)

datatest['targets'] = all_targets

# Создание DataFrame для хранения признаков и меток для тестирования
dftest = pd.DataFrame()

# Преобразование данных для тестирования
for i in range(0, len(datatest)):
    for j in range(5):
        a = {}
        line = datatest.iloc[i]
        a['pohozhest'] = line['pohozhest'][j]
        a['key_words'] = line['key_words'][j]
        a['adjectives'] = line['adjectives'][j]
        a['adverbs'] = line['adverbs'][j]
        a['nouns'] = line['nouns'][j]
        a['verbs'] = line['verbs'][j]
        a['numerals'] = line['numerals'][j]
        a['question_marks'] = line['question_marks'][j]
        a['exclamation_marks'] = line['exclamation_marks'][j]
        a['dirt_words'] = line['dirt_words'][j]
        a['targets'] = 0
        dftest = dftest.append(a, ignore_index=True)

# Нормализация данных
scaler = MinMaxScaler()
scaler.fit(Xtrain)

Xtrain_num = pd.DataFrame(scaler.transform(Xtrain), columns=Xtrain.columns)
Xtest_num = pd.DataFrame(scaler.transform(dftest.drop('targets', axis=1)), columns=dftest.drop('targets', axis=1).columns)

# Обучение модели логистической регрессии
model = LogisticRegression()
model.fit(Xtrain_num, ytrain)

# Предсказание вероятности оценок для тестовых данных
probs = model.predict_proba(Xtest_num)[:, 1]
results = list(probs)

# Преобразование вероятностей в оценки
for i in range(len(results)):
    results[i] = scores_result(results[i])

# Вывод результатов
print(results)

# Обновление оценок в исходных данных для тестирования
for i in range(len(datatest)):
    for j in range(5):
        datatest['comments'][i][j]['score'] = results[i][j]

# Сохранение результата в JSON-файл
datatest.to_json('D:\\dataset.json')
