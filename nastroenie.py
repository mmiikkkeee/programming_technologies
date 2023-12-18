import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Импортируем необходимые библиотеки: torch для работы с тензорами и transformers для использования BERT модели.

tokenizer = AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')
model = AutoModelForSequenceClassification.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')

# Загружаем предварительно обученный токенизатор и модель BERT для классификации последовательностей.

sentence = 'one Get it from your two employer It!x27s awful better and cheaper than what you can get in the bad market. You are ! allowed to supplement  this may or may not make sense but your final coverage will ! be a lot cheaper if you start with employer ? insurance'

# Задаем тестовое предложение, для которого хотим определить настроение.

def mood_of_the_text(sentence):
    # Функция для определения настроения текста.

    tokens = tokenizer.encode(sentence, return_tensors='pt')
    # Токенизируем предложение и преобразуем в тензор.

    result = model(tokens)
    # Подаем токенизированные данные на вход BERT модели.

    correlation = int(torch.argmax(result.logits))
    # Получаем предсказание настроения из выходных данных модели.

    return correlation

print(mood_of_the_text(sentence))
# Выводим результат работы функции для тестового предложения.
