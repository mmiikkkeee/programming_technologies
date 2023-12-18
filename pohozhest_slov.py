import pandas as pd
import re
import difflib
from tqdm import tqdm

# Импорт необходимых библиотек: pandas для работы с данными, re для работы с регулярными выражениями,
# difflib для вычисления схожести текстов, tqdm для отображения прогресса в цикле.

def similarity(s1, s2):
    # Функция для вычисления схожести двух строк.
    normalized1 = s1.lower()
    normalized2 = s2.lower()
    matcher = difflib.SequenceMatcher(None, normalized1, normalized2)
    return matcher.ratio()

pd.options.mode.chained_assignment = None
# Отключаем предупреждения pandas о присвоении значений новым объектам.

data = pd.read_json('data_frame.json', lines=True)
# Загружаем данные из JSON-файла в pandas DataFrame.

for comments in data['comments']:
    for comment in comments:
        comment['text'] = re.sub(r"[^a-zA-Z0-9 ]", "", comment['text'])
        # Очищаем текст комментария от спецсимволов и приводим к нижнему регистру.

for i in tqdm(range(0, len(data))):
    # Итерируемся по всем записям в DataFrame с отображением прогресса.
    post = data.iloc[i]
    texts_to_compare = []
    for dct in post['comments']:
        texts_to_compare.append(dct['text'])
        # Собираем тексты комментариев для сравнения.

    scores = []
    for text in texts_to_compare:
        scores.append(similarity(post['text'], text))
        # Вычисляем схожесть между текстом поста и каждым из комментариев.

    for i in range(5):
        post['comments'][i]['score'] = scores[i]
        # Присваиваем каждому комментарию оценку схожести с соответствующим текстом поста.

    scores = sorted(scores, reverse=True)

    for i in range(5):
        post['comments'][i]['score'] = scores.index(post['comments'][i]['score'])
        # Присваиваем каждому комментарию ранг схожести.

print(data)
# Выводим обновленные данные.
