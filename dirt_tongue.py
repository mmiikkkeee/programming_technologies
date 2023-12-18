from profanity_filter import ProfanityFilter

pf = ProfanityFilter()

# Проходим по данным (предположительно в DataFrame) для анализа комментариев
for i in range(len(data)):
    for j in range(5):
        # Разбиваем текст комментария на слова
        word_counter = data['comments'][i][j]['text'].split(' ')

        # Проходим по каждому слову в комментарии
        for k in range(len(word_counter)):
            current_word = word_counter[k]

            # Проверяем, является ли текущее слово нецензурным
            if not(pf.is_clean(current_word)):
                data['comments'][i][j]['score'] = 0  # Если слово нецензурное, устанавливаем оценку комментария в 0
                print(data['comments'][i][j]['score'])

def dirt_tongue(sentence):
    word_counter = sentence.split()
    for k in range(len(word_counter)):
        current_word = word_counter[k]

        # Проверяем, является ли текущее слово нецензурным
        if not (pf.is_clean(current_word)):
            dirt_score = 0  # Если слово нецензурное, устанавливаем оценку в 0
        else:
            dirt_score = 1  # В противном случае, оценка равна 1
    
    return dirt_score
