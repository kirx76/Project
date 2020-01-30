import random
import time

import Expressions
import connect
import telebot
from telebot import types

print('BOT STARTED')
connection = connect.getConnection()
print('BOT GET CONNECTION')
tele_token = 'TOKEN'
bot = telebot.TeleBot(tele_token)
print('BOT WORKS')
deck = [6, 7, 8, 9, 10, 2, 3, 4, 11] * 4
value = {6: '5', 7: '6', 8: '7', 9: '8', 10: '9', 2: '1', 3: '2', 4: '3', 11: '4'}

# TODO MARKUPS

# После ввода /start
markupstart = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markupstart.add('/start', 'Правила')
# Главное меню
markupg = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markupg.add('Играть', 'Личный кабинет', '', 'Пополнить')
# Отмена
markupback = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markupback.add('Отмена')
# Пополнение баланса
markupbal = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markupbal.add('Я пополнил баланс', 'Отмена')
# Личный кабинет
markuplk = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markuplk.add('Назад', 'Последняя игра', 'Мой ID', 'Изм. изображение карт', '', '', 'Изм. спам бота', '', '')
# Назад
markupcan = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markupcan.add('Назад')
# Да Нет
markupans = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
markupans.add('Да', 'Нет')


@bot.message_handler(commands=['bu'])
def balanceup(message):
    if int(isadmin(message)) >= 10:
        line = message.text.split(' ')
        who = line[1]
        count = line[2]
        conn = Conn()
        conn.execute('update users set user_balance = user_balance + %s where id = %s', (int(count), int(who)))
        connection.commit()
        bot.send_message(message.chat.id, 'Баланс пользователя ' + str(who) + ' изменен.')
        bot.send_message(int(who), 'Ваш баланс пополнен администратором')


@bot.message_handler(commands=['bd'])
def balanceup(message):
    if int(isadmin(message)) >= 10:
        line = message.text.split(' ')
        who = line[1]
        count = line[2]
        conn = Conn()
        conn.execute('update users set user_balance = user_balance - %s where id = %s', (int(count), int(who)))
        connection.commit()
        bot.send_message(message.chat.id, 'Баланс пользователя ' + str(who) + ' изменен.')
        bot.send_message(int(who), 'Ваш баланс уменьшен администратором')


@bot.message_handler(func=lambda message: message.text in ['Мой ID'])
def getid(message):
    bot.send_message(message.chat.id, message.chat.id)


@bot.message_handler(func=lambda message: message.forward_from is not None)
def getreplyinfo(message):
    bot.send_message(message.chat.id, message.forward_from)


def isadmin(message):
    conn = Conn()
    res = conn.execute('select * from admin where id = %s', message.chat.id)
    con = conn.fetchone()
    if res > 0:
        return con['admlvl']
    else:
        return False


# TODO BOT LOGIC

@bot.message_handler(func=lambda message: message.text in ['Последняя игра'])
def check_last_game(message):
    conn = Conn()
    conn.execute('select * from users where id = %s', message.chat.id)
    res = conn.fetchone()
    vc = int(res['view_card'])
    checc(message, vc)
    abotchec(message, 1, vc)
    my(message)


@bot.message_handler(func=lambda message: message.text in ['Правила'])
def rules(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('/start', 'Правила')
    bot.send_message(message.chat.id,
                     '<b>Правила бота:</b> \n<b>1.</b>Перед игрой надо пополнить баланс.\n<b>2.</b>За поддержкой обращаться к @\n<b>3.</b>Выиграть не сложно, главное знать как.\n<b>4.</b>При условии начала использования бота (без принятия правил), правила со стороны пользователя принимаются автоматически\n<b>n</b>.Создатель бота имеет право хранить и обрабатывать ваши данные.',
                     parse_mode='HTML', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in ['Назад'])
def mun(message):
    bot.send_message(message.chat.id, 'Поиграем?', reply_markup=markupg)


@bot.message_handler(func=lambda message: message.text in ['Изм. изображение карт'])
def change_card_view(message):
    conn = Conn()
    conn.execute('select * from users where id = %s', message.chat.id)
    res = conn.fetchone()
    if int(res['view_card']) == 1:
        conn.execute('update users set view_card = 0 where id =%s', message.chat.id)
        connection.commit()
        bot.send_message(message.chat.id, 'Бот не будет присылать картинки карт', reply_markup=markuplk)
    else:
        conn.execute('update users set view_card = 1 where id =%s', message.chat.id)
        connection.commit()
        bot.send_message(message.chat.id, 'Бот будет присылать картинки карт', reply_markup=markuplk)


def cicada(message):
    id = int(message.chat.id)
    text = message.text

    if str(bin(id))[2:] == text:
        return True
    else:
        return False


def cicad(message):
    info = getinfo(message)
    if info['cicad'] == 1:
        return True
    else:
        return False


@bot.message_handler(func=lambda message: True and cicada(message) == True and cicad(message) == False)
def second_step(message):
    sent = bot.send_message(message.chat.id, 'Молодец, готов к следующему этапу?', reply_markup=markupans)
    bot.register_next_step_handler(sent, third_step)
    pot_token = 'TOKEN'
    pot = telebot.TeleBot(pot_token)
    pot.send_message(216607409, 'Пользователь: ' + str(message.chat.id) + ' прошел во 2 этап.')


def third_step(message):
    if message.text == 'Да':
        sent = bot.send_message(message.chat.id,
                                'Сыграем в игру?\nПервый вопрос - первый ответ.\nОтвет принимается на русском языке.\nЧто нельзя увидеть, потрогать, почувствовать, но оно существует?\n\nПодсказка:\nСумма единиц бинарного кода ответа меньше 10. Цифру, которую стоит ввести указывайте перед ответом слитно. Прим.(17Кедр).')
        bot.register_next_step_handler(sent, final_line)
    else:
        bot.send_message(message.chat.id, 'Хорошо, ждем, когда ты решишься', reply_markup=markupg)


def final_line(message):
    if message.text == '6Да':
        bot.send_message(message.chat.id,
                         'Поздравляю, ты разгадал загадку. На твой счет начисленно 1к. Воспользуйся кнопкой в ЛК.',
                         reply_markup=markupg)
        conn = Conn()
        conn.execute('update users set user_balance = user_balance + 1000 where id = %s', message.chat.id)
        connection.commit()
        conni = Conn()
        conni.execute('update users set cicad = 1 where id = %s', message.chat.id)
        connection.commit()
        connection.close()
    else:
        bot.send_message(message.chat.id, 'Увы, твой ответ неверный, пройди весь путь заново.', reply_markup=markupg)


@bot.message_handler(func=lambda message: message.text in ['Изм. спам бота'])
def change_spam_bot(message):
    conn = Conn()
    conn.execute('select * from users where id = %s', message.chat.id)
    res = conn.fetchone()
    if int(res['spam_bot']) == 1:
        conn.execute('update users set spam_bot = 0 where id =%s', message.chat.id)
        connection.commit()
        bot.send_message(message.chat.id, 'Бот не будет писать лишние сообщения', reply_markup=markuplk)
    else:
        conn.execute('update users set spam_bot = 1 where id =%s', message.chat.id)
        connection.commit()
        bot.send_message(message.chat.id, 'Бот будет сообщать обо всех своих действиях', reply_markup=markuplk)


@bot.message_handler(func=lambda message: message.text in ['отмена', 'Отмена'])
def cancelbalanceup(message):
    connection.connect()
    cursor = connection.cursor()
    sqlone = "select * from users where id=%(user_id)s"
    dataone = {'user_id': message.chat.id}
    cursor.execute(sqlone, dataone)
    myresult = cursor.fetchone()
    user_time = int(myresult['user_time'])
    user_sum = int(myresult['user_sum'])
    if user_time > int(time.time()):
        bot.send_message(message.chat.id,
                         "Подождите окончание таймера!\nОсталось: *" + str(user_time - int(time.time())) + "* c.",
                         parse_mode='Markdown', reply_markup=markupbal)
    elif user_sum > 0:
        sql = "update users set user_random=0, user_sum=0, user_time=%(user_time)s where id=%(user_id)s"
        data = {'user_time': int(time.time()), 'user_id': message.chat.id}
        cursor.execute(sql, data)
        connection.commit()
        bot.send_message(message.chat.id, "Ваш запрос на пополнение баланса *отменен*", reply_markup=markupg,
                         parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, "У вас нет запросов на пополнение баланса!", reply_markup=markupg)


@bot.message_handler(func=lambda message: message.text in ['Отмена', 'отмена'])
def cancel(message):
    bot.send_message(message.chat.id, 'Главное меню', reply_markup=markupg)


@bot.message_handler(commands=['real'])
def wantreal(message):
    info = getinfo(message)
    if int(info['user_balance']) >= 1000 and int(info['user_real']) == 0:
        bot.send_message(message.chat.id, 'Твоя заявка оформлена, жди приглашения от админа.', reply_markup=markupg)
        bot.send_message(216607409, 'Пользователь с ID: ' + str(message.chat.id) + ' хочет играть реал.')
        conn = Conn()
        conn.execute('update users set user_real = 1 where id = %s', message.chat.id)
        connection.commit()
    connection.close()


@bot.message_handler(commands=['inf'])
def inf(message):
    if int(message.chat.id) == 216607409:
        conn = Conn()
        res = conn.execute('select * from users')
        conni = Conn()
        resi = conni.execute('select * from users where play_count > 0')
        bot.send_message(message.chat.id,
                         'Всего пользователей: ' + str(res) + '\nПользователей, что сыграли хоть 1 игру: ' + str(resi))
        connection.close()


@bot.message_handler(commands=['check'])
def checkreal(message):
    if int(message.chat.id) == 216607409:
        task = ''
        conn = Conn()
        conn.execute('select * from users')
        res = conn.fetchone()
        while res is not None:
            if int(res['user_real']) > 0:
                task += str(res['id']) + '\n'
            res = conn.fetchone()
        bot.send_message(message.chat.id, 'Пользователи, которые хотят большего: \n' + task)
        connection.close()


@bot.message_handler(func=lambda message: message.text in ['Личный кабинет', 'личный кабинет'])
def my(message):
    info = getinfo(message)
    if (info['user_balance']) >= 1000 and int(info['user_real']) == 0:
        bot.send_message(message.chat.id, 'Хочешь играть по крупному?\nПиши /real')
    if info['play_count'] >= 1:
        persent = round((int(info['play_wins']) / int(info['play_count']) * 100), 1)
        bot.send_message(message.chat.id, '<b>Ваша информация</b>\nВсего игр: ' + str(
            info['play_count']) + '\nВаш баланс: ' + str(info['user_balance']) + '\nПроцент побед: ' + str(
            persent) + ' <b>%</b>',
                         reply_markup=markuplk, parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, '<b>Ваша информация</b>\nВсего игр: ' + str(
            info['play_count']) + '\nВаш баланс: ' + str(info['user_balance']) + '\nВы не сыграли ни одной игры',
                         reply_markup=markuplk, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, '1000 баланса -> новая кнопка в ЛК')
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    bot.send_message(message.chat.id,
                     'Бот не несет ответственности за оставленные в нем нервы.\nПравила игры: 21 очко на 36 карт.',
                     parse_mode='HTML')
    markup.add('Да', 'Нет', 'Правила')
    sent = bot.send_message(message.chat.id,
                            "Чтобы пользоваться ботом, нужно принять правила пользования.\nВы принимаете правила использования?",
                            reply_markup=markup, parse_mode='HTML')
    bot.register_next_step_handler(sent, register)


@bot.message_handler(
    func=lambda message: message.text in ['Пополнить', 'пополнить', '/pol', u'\U00002714' ' Пополнить'])
def newpol(message):
    conn = Conn()
    conn.execute('select * from users where id = %s', message.chat.id)
    res = conn.fetchone()
    if int(res['user_balance']) < 50:
        if int(res['user_lu']) > int(time.time()):
            bot.send_message(message.chat.id, 'Нельзя так часто пополнять баланс, дождитесь конца таймера: <b>' + str(
                int(res['user_lu']) - int(time.time())) + ' c.</b>', reply_markup=markupg, parse_mode='HTML')
            connection.close()
        else:
            conni = Conn()
            conni.execute('update users set user_balance = 50 where id = %s', message.chat.id)
            connection.commit()
            conny = Conn()
            tome = int(time.time()) + 600
            conny.execute('update users set user_lu = %s where id = %s', (tome, message.chat.id))
            connection.commit()
            bot.send_message(message.chat.id, 'Ваш баланс теперь равен 50', reply_markup=markupg)
    else:
        bot.send_message(message.chat.id, 'Ваш баланс и так больше 50', reply_markup=markupg)
        connection.close()


@bot.message_handler(commands=['send'])
def sendMess(message):
    count = 0
    connection.connect()
    cursor = connection.cursor()
    if int(message.chat.id) == 216607409:
        sql = "select * from users"
        cont = cursor.execute(sql)
        myresult = cursor.fetchone()
        while myresult is not None:
            user_id = int(myresult['id'])
            text = message.text[6:]
            try:
                bot.send_message(user_id, text, parse_mode='Markdown')
                count += 1
            except Exception:
                pass
            myresult = cursor.fetchone()
        bot.send_message(message.chat.id,
                         "Рассылка окончена\nВсего пользователей: " + str(cont) + '\nОтправленно ' + str(
                             count) + ' пользователям.\nНе отправлено ' + str(int(cont) - int(count)) + '.')
    else:
        bot.send_message(message.chat.id, "Вы не являетесь администратором")
    connection.close()


def getinfo(message):
    conn = Conn()
    conn.execute('select * from users where id = %s', message.chat.id)
    res = conn.fetchone()
    return res


def isRegistered(id):
    try:
        connection.connect()
        cursor = connection.cursor()
        sql = "select id from users"
        cursor.execute(sql)
        for row in cursor:
            if row["id"] == id:
                return True
        return False
    finally:
        pass


def register(message):
    if message.text == 'Да':
        if not isRegistered(int(message.chat.id)):
            connection.connect()
            cursor = connection.cursor()
            sql = 'insert into users values(%(id)s,0,0,0,0,0,0,0,0,0,0,0,0,0,0)'
            data = {'id': message.chat.id}
            cursor.execute(sql, data)
            connection.commit()
            bot.send_message(message.chat.id, "Вы успешно добавлены в базу", reply_markup=markupg)
        else:
            bot.send_message(message.chat.id, 'Вы уже зарегестрированны и приняли правила', reply_markup=markupg)
    elif message.text == 'Правила':
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('/start', 'Правила')
        bot.send_message(message.chat.id,
                         '<b>Правила бота:</b> \n<b>1.</b>Перед игрой надо пополнить баланс.\n<b>2.</b>За поддержкой обращаться к @\n<b>3.</b>Выиграть не сложно, главное знать как.\n<b>4.</b>При условии начала использования бота (без принятия правил), правила со стороны пользователя принимаются автоматически\n<b>n</b>.Создатель бота имеет право хранить и обрабатывать ваши данные.',
                         parse_mode='HTML', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Вы не приняли правила, использование бота без принятия правил невозможно!",
                         reply_markup=markupstart)


def Conn():
    connection.connect()
    cursor = connection.cursor()
    return cursor


def shuf():
    numm = random.randrange(1, 9)
    return numm


def checc(message, view_card):
    ace = 0
    media = []
    out = '<b>В вашей руке: \n</b>'
    allval = 0
    sql = 'select * from comp join cards using(card_id) join suit using(suit) where user_id = %(id)s'
    data = {'id': message.chat.id}
    conn = Conn()
    conn.execute(sql, data)
    res = conn.fetchone()
    while res is not None:
        if int(res['value']) == 11:
            ace += 1
        out += str(res['name']) + ' ' + str(res['name_suit']) + '\n'
        allval += int(res['value'])
        file = open('cards/1x/' + str(res['value']) + ' ' + str(res['suit']) + '.png', 'rb')
        media.append(types.InputMediaPhoto(file, (str(res['name']) + ' ' + str(res['name_suit']))))
        res = conn.fetchone()
    if allval > 21 and ace > 0:
        allval -= ace * 11 - ace
    bot.send_message(message.chat.id, out + '\nОбщая ценность карт: ' + str(allval), parse_mode='HTML')
    if view_card == 1 and res is not None:
        try:
            bot.send_media_group(message.chat.id, media=media)
        except Exception as e:
            pass


def chec(message):
    media = []
    out = '<b>В вашей руке: \n</b>'
    allval = 0
    sql = 'select * from comp join cards using(card_id) join suit using(suit) where user_id = %(id)s'
    data = {'id': message.chat.id}
    conn = Conn()
    conn.execute(sql, data)
    res = conn.fetchone()
    while res is not None:
        out += str(res['name']) + ' ' + str(res['name_suit']) + '\n'
        allval += int(res['value'])
        file = open('cards/1x/' + str(res['value']) + ' ' + str(res['suit']) + '.png', 'rb')
        media.append(types.InputMediaPhoto(file, (str(res['name']) + ' ' + str(res['name_suit']))))
        res = conn.fetchone()
    bot.send_message(message.chat.id, out + '\nОбщая ценность карт: ' + str(allval), parse_mode='HTML')
    bot.send_media_group(message.chat.id, media=media)


def botchec(message):
    ace = 0
    conni = Conn()
    conni.execute('select * from users where id = %s', message.chat.id)
    res = conni.fetchone()
    vc = int(res['view_card'])
    media = []
    out = '<b>В руке Бота: \n</b>'
    allval = 0
    sql = 'select * from bothand join cards using(card_id) join suit using(suit) where user_id = %(id)s'
    data = {'id': message.chat.id}
    conn = Conn()
    conn.execute(sql, data)
    res = conn.fetchone()
    out += 'Карта бота скрыта\n'
    allval += int(res['value'])
    media.append(types.InputMediaPhoto(open('cards/1x/0.png', 'rb'), 'Карта скрыта'))
    res = conn.fetchone()
    while res is not None:
        if res['value'] == 11:
            ace += 1
        file = open('cards/1x/' + str(res['value']) + ' ' + str(res['suit']) + '.png', 'rb')
        media.append(types.InputMediaPhoto(file, (str(res['name']) + ' ' + str(res['name_suit']))))
        out += str(res['name']) + ' ' + str(res['name_suit']) + '\n'
        allval += int(res['value'])
        res = conn.fetchone()
    if allval == 22 and ace == 2:
        allval = 21
        return allval
    if allval > 21 and ace > 0:
        allval -= ace * 11 - ace
    bot.send_message(message.chat.id, out + '\nОбщая ценность карт: ' + str(allval), parse_mode='HTML')
    if vc == 1:
        bot.send_media_group(message.chat.id, media=media)
    return allval


def abotchec(message, spam_bot, view_card):
    ace = 0
    media = []
    out = '<b>В руке Бота: \n</b>'
    allval = 0
    sql = 'select * from bothand join cards using(card_id) join suit using(suit) where user_id = %(id)s'
    data = {'id': message.chat.id}
    conn = Conn()
    conn.execute(sql, data)
    res = conn.fetchone()
    while res is not None:
        if int(res['value']) == 11:
            ace += 1
        file = open('cards/1x/' + str(res['value']) + ' ' + str(res['suit']) + '.png', 'rb')
        media.append(types.InputMediaPhoto(file, (str(res['name']) + ' ' + str(res['name_suit']))))
        out += str(res['name']) + ' ' + str(res['name_suit']) + '\n'
        allval += int(res['value'])
        res = conn.fetchone()
    if allval == 22 and ace == 2:
        allval = 21
        bot.send_message(message.chat.id, out + '\nОбщая ценность карт: ' + str(allval), parse_mode='HTML')
        return allval
    if allval > 21 and ace > 0:
        allval -= ace * 11 - ace
    if spam_bot == 1:
        bot.send_message(message.chat.id, out + '\nОбщая ценность карт: ' + str(allval), parse_mode='HTML')
        if view_card == 1:
            try:
                bot.send_media_group(message.chat.id, media=media)
            except Exception:
                pass
    return allval


def takesuit():
    id = random.randrange(1, 5)
    return id


def distr(who):
    numm = shuf()
    conn = Conn()
    sql = 'insert into comp values(0, %(who)s, %(num)s, %(suit)s)'
    data = {'who': who, 'num': numm, 'suit': takesuit()}
    conn.execute(sql, data)
    connection.commit()
    connection.close()


def botdis(who):
    numm = shuf()
    conn = Conn()
    sql = 'insert into bothand values(%(who)s, %(num)s, %(suit)s)'
    data = {'who': who, 'num': numm, 'suit': takesuit()}
    conn.execute(sql, data)
    connection.commit()
    connection.close()


def botadd(who, numm):
    conn = Conn()
    sql = 'insert into bothand values(%(who)s, %(num)s, %(suit)s)'
    numn = value[numm]
    data = {'who': who, 'num': numn, 'suit': takesuit()}
    conn.execute(sql, data)
    connection.commit()
    connection.close()


def player(message):
    conn = Conn()
    sql = 'select * from comp join cards using(card_id) join suit using(suit) where user_id = %(id)s'
    data = {'id': message.chat.id}
    numbercards = conn.execute(sql, data)
    if numbercards == 0:
        distr(message.chat.id)
    distr(message.chat.id)
    conn = Conn()
    conn.execute('select * from users where id = %s', message.chat.id)
    res = conn.fetchone()
    vc = int(res['view_card'])
    checc(message, vc)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('Да', 'Нет')
    sent = bot.send_message(message.chat.id, 'Будете брать карту?', reply_markup=markup)
    bot.register_next_step_handler(sent, anothercard)


def anothercard(message):
    ace = 0
    val = 0
    conn = Conn()
    sql = 'select * from comp join cards using(card_id) join suit using(suit) where user_id = %(id)s'
    data = {'id': message.chat.id}
    conn.execute(sql, data)
    res = conn.fetchone()
    while res is not None:
        if int(res['value']) == 11:
            ace += 1
            val += int(res['value'])
        else:
            val += int(res['value'])
        res = conn.fetchone()
    if val > 21 and ace > 0:
        val -= ace * 11 - ace
    if message.text == 'Да' and val <= 21:
        bot.send_message(message.chat.id, 'Берем карту')
        player(message)
    elif message.text == 'Да' and val > 21:
        bot.send_message(message.chat.id, 'В вашей руке больше 21 очка, переходим к игре бота!')
        botp(message)
    elif message.text == 'Нет':
        botp(message)
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Да', 'Нет')
        sent = bot.send_message(message.chat.id, 'Будете брать карту?', reply_markup=markup)
        bot.register_next_step_handler(sent, anothercard)


def bots(message):
    conn = Conn()
    sql = 'select * from bothand join cards using(card_id) join suit using(suit) where user_id = %(id)s'
    data = {'id': message.chat.id}
    numbercards = conn.execute(sql, data)
    if numbercards == 0:
        botdis(message.chat.id)
    botdis(message.chat.id)
    botchec(message)


def getvalue():
    vall = {}
    conn = Conn()
    sql = 'select * from cards'
    conn.execute(sql)
    res = conn.fetchone()
    vall += res['']
    while res is not None:
        pass


def botp(message):
    ace = 0
    allval = 0
    connu = Conn()
    connu.execute('select * from users where id = %s', message.chat.id)
    res = connu.fetchone()
    user_play_count = int(res['play_count'])
    user_wins = int(res['play_wins'])
    view_card = int(res['view_card'])
    spam_bot = int(res['spam_bot'])
    user_rate = int(res['user_bet'])
    conni = Conn()
    conni.execute('select * from comp join cards using(card_id) join suit using(suit) where user_id = %s',
                  message.chat.id)
    res = conni.fetchone()
    while res is not None:
        if int(res['value']) == 11:
            ace += 1
        allval += int(res['value'])
        res = conni.fetchone()
    if allval == 22 and ace == 2:
        allval = 21
    if allval > 21 and ace > 0:
        allval -= ace * 11 - ace

    if user_play_count >= 1:
        persent = round(((user_wins / user_play_count) * 100), 1)
    else:
        persent = 0
    if persent > 70:
        alwayswin = True
    else:
        alwayswin = False
    if user_rate > 120:
        alwayswin = True
    ended = False
    bot.send_message(message.chat.id, 'Бот начал свою игру')
    while True:
        botval = abotchec(message, spam_bot, view_card)
        time.sleep(1)
        if botval < 21 and ended == False:
            if 2 <= allval < 18 and 18 <= botval <= 21:
                if spam_bot == 1:
                    bot.send_message(message.chat.id, Expressions.getsay())
                ended = True
            else:
                if allval > 21 and botval >= 12:
                    if spam_bot == 1:
                        bot.send_message(message.chat.id, Expressions.getsay())
                    ended = True
                else:
                    if alwayswin:
                        bj = 21
                        bj -= botval
                        if bj in value:
                            if spam_bot == 1:
                                bot.send_message(message.chat.id, 'Бот решил взять карту')
                            botadd(message.chat.id, bj)
                        else:
                            if bj == 1:
                                ended = True
                                if spam_bot == 1:
                                    bot.send_message(message.chat.id, str(Expressions.getsay()))
                            else:
                                if spam_bot == 1:
                                    bot.send_message(message.chat.id, 'Бот решил взять карту')
                                added = random.randrange(2, 9)
                                while added == 5:
                                    added = random.randrange(2, 9)
                                botadd(message.chat.id, added)
                    else:
                        if botval == 20:
                            ended = True
                            if spam_bot == 1:
                                bot.send_message(message.chat.id, str(Expressions.getsay()))
                        elif botval <= 16:
                            if spam_bot == 1:
                                bot.send_message(message.chat.id, 'Бот решил взять карту')
                            botdis(message.chat.id)
                        elif botval > 16:
                            percent = random.randrange(0, 2)
                            if percent == 0:
                                if spam_bot == 1:
                                    bot.send_message(message.chat.id, 'Бот решил взять карту')
                                botdis(message.chat.id)
                                ended = True
                            else:
                                if spam_bot == 1:
                                    bot.send_message(message.chat.id, 'Бот решил не брать карту')
                                ended = True
        else:
            if spam_bot == 1:
                bot.send_message(message.chat.id, 'Бот решил не брать карту и завершить свою игру')
            abotchec(message, spam_bot, view_card)
            break

    en(message, spam_bot)


def en(message, spam_bot):
    aceu = 0
    aceb = 0
    if spam_bot == 0:
        abotchec(message, 0, 1)
    userval = 0
    botvali = 0
    conn = Conn()
    conni = Conn()
    sqlu = 'select * from comp join cards using(card_id) join suit using(suit) where user_id = %(id)s'
    datau = {'id': message.chat.id}
    conn.execute(sqlu, datau)
    resu = conn.fetchone()
    while resu is not None:
        if int(resu['value']) == 11:
            aceu += 1
        userval += int(resu['value'])
        resu = conn.fetchone()
    if userval == 22 and aceu == 2:
        userval = 21
    if userval > 21 and aceu > 0:
        userval -= aceu * 11 - aceu
    sqlb = 'select * from bothand join cards using(card_id) join suit using(suit) where user_id = %(id)s'
    datab = {'id': message.chat.id}
    conni.execute(sqlb, datab)
    resb = conni.fetchone()
    while resb is not None:
        if int(resb['value']) == 11:
            aceb += 1
        botvali += int(resb['value'])
        resb = conni.fetchone()
    if botvali == 22 and aceb == 2:
        botvali = 21
        aceb = 0
    if botvali > 21 and aceb > 0:
        botvali -= aceb * 11 - aceb
    bot.send_message(message.chat.id, 'Ваши очки: ' + str(userval) + '\nОчки бота: ' + str(botvali))
    connu = Conn()
    connu.execute('select * from users where id = %s', message.chat.id)
    res = connu.fetchone()
    user_balance = int(res['user_balance'])
    user_bet = int(res['user_bet'])
    user_play_count = int(res['play_count'])
    user_wins = int(res['play_wins'])
    time.sleep(1)
    if userval == botvali:
        conn1 = Conn()
        newb = user_balance + user_bet
        conn1.execute('update users set user_balance = %s where id = %s', (newb, message.chat.id))
        connection.commit()
        conn2 = Conn()
        conn2.execute('update users set user_bet = 0 where id = %s', message.chat.id)
        connection.commit()
        bot.send_message(message.chat.id, str(Expressions.getexpdraw()), reply_markup=markupg)

    elif 21 >= userval > botvali:
        conn1 = Conn()
        newb = user_balance + (user_bet * 2)
        conn1.execute('update users set user_balance = %s where id = %s', (newb, message.chat.id))
        connection.commit()
        conn2 = Conn()
        conn2.execute('update users set user_bet = 0 where id = %s', message.chat.id)
        connection.commit()
        conn3 = Conn()
        conn3.execute('update users set play_count = %s where id = %s', (user_play_count + 1, message.chat.id))
        connection.commit()
        conn4 = Conn()
        conn4.execute('update users set play_wins = %s where id = %s', (user_wins + 1, message.chat.id))
        connection.commit()
        bot.send_message(message.chat.id, str(Expressions.getexpwin()), reply_markup=markupg)

    elif 21 >= botvali > userval:
        conn1 = Conn()
        conn1.execute('update users set user_bet = 0 where id = %s', message.chat.id)
        connection.commit()
        conn3 = Conn()
        conn3.execute('update users set play_count = %s where id = %s', (user_play_count + 1, message.chat.id))
        connection.commit()
        bot.send_message(message.chat.id, str(Expressions.getexplose()), reply_markup=markupg)

    elif 21 >= userval and botvali > 21:
        conn1 = Conn()
        newb = user_balance + (user_bet * 2)
        conn1.execute('update users set user_balance = %s where id = %s', (newb, message.chat.id))
        connection.commit()
        conn2 = Conn()
        conn2.execute('update users set user_bet = 0 where id = %s', message.chat.id)
        connection.commit()
        conn3 = Conn()
        conn3.execute('update users set play_count = %s where id = %s', (user_play_count + 1, message.chat.id))
        connection.commit()
        conn4 = Conn()
        conn4.execute('update users set play_wins = %s where id = %s', (user_wins + 1, message.chat.id))
        connection.commit()
        bot.send_message(message.chat.id, str(Expressions.getexpwin()), reply_markup=markupg)

    elif 21 >= botvali and userval > 21:
        conn1 = Conn()
        conn1.execute('update users set user_bet = 0 where id = %s', message.chat.id)
        connection.commit()
        conn3 = Conn()
        conn3.execute('update users set play_count = %s where id = %s', (user_play_count + 1, message.chat.id))
        connection.commit()
        bot.send_message(message.chat.id, str(Expressions.getexplose()), reply_markup=markupg)

    elif botvali > 21 and userval > 21:
        conn1 = Conn()
        newb = user_balance + user_bet
        conn1.execute('update users set user_balance = %s where id = %s', (newb, message.chat.id))
        connection.commit()
        conn2 = Conn()
        conn2.execute('update users set user_bet = 0 where id = %s', message.chat.id)
        connection.commit()
        bot.send_message(message.chat.id, str(Expressions.getexpdraw()), reply_markup=markupg)


@bot.message_handler(func=lambda message: message.text in ['Играть', 'играть'])
def bet(message):
    sent = bot.send_message(message.chat.id, 'Сколько вы хотите поставить?', reply_markup=markupcan)
    bot.register_next_step_handler(sent, startplaybj)


def startplaybj(message):
    bet = message.text
    if bet.isdigit() and int(bet) >= 15:
        conn = Conn()
        sqlb = 'delete from bothand where user_id = %(id)s'
        sqlu = 'delete from comp where user_id = %(id)s'
        data = {'id': message.chat.id}
        conn.execute(sqlb, data)
        conn.execute(sqlu, data)
        connection.commit()
        connu = Conn()
        connu.execute('select * from users where id = %s', message.chat.id)
        res = connu.fetchone()
        user_balance = int(res['user_balance'])
        if user_balance >= int(bet):
            conni = Conn()
            sqlbet = 'update users set user_bet = %(bet)s where id = %(id)s'
            databet = {'bet': bet, 'id': message.chat.id}
            conni.execute(sqlbet, databet)
            connection.commit()
            newbalance = user_balance - int(bet)
            connuu = Conn()
            connuu.execute('update users set user_balance = %s where id = %s', (newbalance, message.chat.id))
            connection.commit()
            bots(message)
            player(message)
        else:
            sent = bot.send_message(message.chat.id, 'Ваша ставка больше вашего баланса.\nВведите число снова')
            bot.register_next_step_handler(sent, startplaybj)
    elif message.text in ['Назад']:
        bot.send_message(message.chat.id, 'Поиграем?', reply_markup=markupg)
    else:
        sent = bot.send_message(message.chat.id,
                                'Вводите только числа от 15 и не больше вашего баланса.\nВведите число снова')
        bot.register_next_step_handler(sent, startplaybj)


bot.polling(none_stop=True)
