import random

loses = ['Искуственный интеллект обыграл тебя.', 'Компьютер оказался сильнее.', 'Бота научили побеждать тебя.', 'Сила наполняет бота.']

wins = ['Чтож, в этот раз тебе повезло.', 'Что насчет еще одной?', 'Ты умнее чем показался боту изначально.', 'Удача на твоей стороне.']

draws = ['Может еще одну?', 'Какая жалость, бот не смог забрать твои деньги.', 'Повторим?', 'Ставку вернул, не волнуйся.']

says = ['Бот задумался о смысле жизни.', 'Что если у колобка 4 ноги?', 'Русалка села на шпагат. гы', 'Не обращай внимания.', 'Бот отвлекся от игры.']

def getsay():
    pos = random.randrange(0, len(says))
    return says[pos]

def getexplose():
    text = 'Ты проиграл! \n'
    pos = random.randrange(0, len(loses))
    return text + loses[pos]

def getexpwin():
    text = 'Ты выиграл!(х2). \n'
    pos = random.randrange(0, len(wins))
    return text + wins[pos]

def getexpdraw():
    text = 'Ничья! Ставка вернулась. \n'
    pos = random.randrange(0, len(draws))
    return text + draws[pos]