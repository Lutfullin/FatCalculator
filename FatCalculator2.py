import telebot
import re
import config

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

bot = telebot.TeleBot(config.token, parse_mode=None)

#подключаем БД
cred = credentials.Certificate(config.base_cred)

firebase_admin.initialize_app(cred, {
    'databaseURL': config.databaseURL
})

ref = db.reference('Fat_Calculator')

import datetime
now = datetime.datetime.now()


def add_food(id, name, protein, fat, carboh):
    data = {
        name:
        {
            "protein": protein,
            "fat": fat,
            "cabroh": carboh,
            "callories": ((4 * carboh) + (4 * protein) + (9 * fat))	
        }
    }
    ref.child(str(id)+"/My_products/").update(data)


def I_have_eatten(id, name, protein, fat, carboh, callories,mass):
    
    coeff = float(mass)/100
    
    dict = ref.child(str(id) + "/Eatten/" + str(now.day) + "_" + str(now.month) + "_"+str(now.year)).get()

    
    if (dict is None):
        item = 1
    else:
        item = len(dict)

    data = {
        str(item):
        {
            "name":name,
            "protein": protein*coeff,
            "fat": fat*coeff,
            "cabroh": carboh*coeff,
            "mass": mass,
            "callories": callories*coeff
        }
    }

    ref.child(str(id) + "/Eatten/" + str(now.day) + "_" + str(now.month) + "_" + str(now.year)).update(data)


#команда добавляющая новый продукт в реестр продуктов
@bot.message_handler(commands = ['add'])
def send_welcome(message):

    bot.send_message(message.chat.id,
        'Че хочешь добавить? Образец: "Яблоко 0.4 0.4 9.8" - это типа белки жиры углеводы в граммах')
    
    #переключаем - чтобы чат ждал
    ref.child(str(message.chat.id)).update({"state":"adding"})



#функция для старта
@bot.message_handler(commands = ['start'])
def send_welcome(message):
    #сощадем в БД раздел для нового пользователя и делаем его статус start
    ref.child(str(message.chat.id)).update({"state":"start"})
    bot.send_message(message.chat.id,
                     "/eatten - сколько ты сегодня съел\n"
                     "/add - добавить новый продутк в мои продукты\n"
                     "/my_products - мои продукты\n"
                     "/delete_my_product - удалить проудкт из моих продутов"
                     "/delete - удалить, что съел\n"
                     "/day - показать что я съел в тот день"
                     'Если съел напиши: "проудкт 234" 234 - это масса съеденного в граммах')


#выводи список продуктов в реестре
@bot.message_handler(commands = ['my_products'])
def my_products(message):
    dict = ref.child(str(message.chat.id) + "/My_products").get()
    
    if (dict is None):
        bot.send_message(message.chat.id, "Список Мои продукты пустой,чтобы добавить жмякни на /add")
    else:
        bot.send_message(message.chat.id, "В твоем списке продуктов есть:")
        
        #счетчик типа
        index = 1
        for item in dict:
            bot.send_message(message.chat.id, str(index)+". "+item)
            index += 1
            

#Команда для удаления продукта из моих проуктков
@bot.message_handler(commands=['delete_my_product'])
def delete_my_product(message):
    try:
        dict = ref.child(str(message.chat.id) + "/My_products").get()
        if (dict is None):
            bot.send_message(message.chat.id, "Список Мои продукты пустой,чтобы добавить жмякни на /add")
        else:
            bot.send_message(message.chat.id, "В твоем списке продуктов есть:")
            #клавдия
            keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
            index = 1
            for item in dict:
                bot.send_message(message.chat.id, str(index)+". "+item)
                keyboard.add(str(index))
                index += 1
            
            bot.send_message(message.chat.id, "Что хочешь удалить? Напиши номер", reply_markup=keyboard)
            ref.child(str(message.chat.id)).update({"state":"delete_my_product"})
    except Exception:
        print("функция delete_my_product уронила все")
        bot.send_message(message.chat.id, "Че-то пошло не так!")

#эта команда будет вовзращать сегодняшний рацион
@bot.message_handler(commands=['eatten'])
def eatten(message):
    dict = ref.child(str(message.chat.id) + "/Eatten/" + str(now.day) + "_" + str(now.month) + "_"+str(now.year)).get()

    if (dict is not None):
        total_cclal = 0
        index = 1
        #Бежим по листу сегодняшено рациона и выкатываем в чат каждый съеденный продукт
        for item in dict[1:]:
            
            answer = str (i) + ". " + item['name'] + ": " + str(item['callories']) + " ккал"
            bot.send_message(message.chat.id, answer)
            total_cclal += item['callories']
            index+= 1

        bot.send_message(message.chat.id, "Всего ты сегодян съел: " + str(total_cclal) + " ккал")
    else:
        bot.send_message(message.chat.id, "Ты ж ничего еще не съел")    


    
#Команда для удаления продукта из сегодняшнего рациона
@bot.message_handler(commands=['ratdel'])
def ratdel(message):
    dict = ref.child(str(message.chat.id) + "/Eatten/" + str(now.day) + "_" + str(now.month) + "_"+str(now.year)).get()

    if (dict is not None):
        
        keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)

        total_cclal = 0
        i = 1
        #Бежим по листу сегодняшено рациона и выкатываем в чат каждый съеденный продукт
        for item in dict[1:]:
            answer = str (i) + ". " + item['name'] + ": " + str(item['callories']) + " ккал"
            bot.send_message(message.chat.id, answer)
            total_cclal += item['callories']
            keyboard1.add(str(i))
            i += 1
                

        bot.send_message(message.chat.id, "Всего ты сегодян съел: " + str(total_cclal) + " ккал")
        bot.send_message(message.chat.id, "Что хочешь удалить? Напиши номер", reply_markup=keyboard1)
        
        

        ref.child(str(message.chat.id)).update({"state":"ratdeling"})


    else:
        bot.send_message(message.chat.id, "Ты ж ничего еще не съел")     


#выводи список продуктов в реестре
@bot.message_handler(commands = ['day'])
def day(message):
    bot.send_message(message.chat.id, "Введи дату, которую хочешь посмотреть")
    ref.child(str(message.chat.id)).update({"state":"waiting_gay"})


#обработка текстовых сообщений
@bot.message_handler(content_types=['text'])
def got_text(message):
    #проверяем переключатель. ждет ли чат нового продукта в реестр
    if (ref.child(str(message.chat.id)+"/state").get() == "adding"):
        try:
            #делаем все маленькими буквами
            product = message.text.lower() 

            #разделяем по пробелам
            result = re.split(r' ', product)
            # "хлеб 34 23 75" → "хлеб", "34", "23", "75"
            #34 - белки, 23 - жиры, 75 - углеводы


            #добавляем в реестр продуктов новый объект - продукт
            add_food(message.chat.id,result[0],float(result[1]),float(result[2]),float(result[3]))

            bot.send_message(message.chat.id, "Дело сделано!")


        #ну мало ли пойдет не так
        except Exception:
            bot.send_message(message.chat.id,"слышь, шутник иди в баню, напиши норм продукт, мы тута работаем вообще т")

        finally:
            #обратно переключим, чтобы чат больше не ждал продукт
            ref.child(str(message.chat.id)).update({"state":"start"})     
    
    #если чат не ждет нового продукта, то пусть пока будет так. что пациент что-то съел
    elif(ref.child(str(message.chat.id)+"/state").get() == "start"):
        
        # делаем все маленькими буквами
        text_of_message = message.text.lower() 
        #по пробелу разделяем название продукта и его массу
        result = re.split(r' ', text_of_message)
            #яблоко 250 → "яблоко" "250"
            #250 - это масса съеденного в граммах

        prod_info = ref.child("Comon_products/"+result[0]).get()

        
        if (prod_info is None):
            prod_info = ref.child(str(message.chat.id)+"/My_products/"+result[0]).get()
            
            if (prod_info is None):
                bot.send_message(message.chat.id, "Такой продукт не найден. Если хотите добавить, жмякните на /add ")
                
            else:
                I_have_eatten(message.chat.id, result[0], prod_info["protein"], prod_info["fat"], prod_info["cabroh"], prod_info["callories"], result[1])
                bot.send_message(message.chat.id, "добавлено!")                
        else:
            I_have_eatten(message.chat.id, result[0], prod_info["protein"], prod_info["fat"], prod_info["cabroh"], prod_info["callories"], result[1])
            bot.send_message(message.chat.id, "добавлено!")
    
    elif(ref.child(str(message.chat.id)+"/state").get() == "delete_my_product"):
        try:
            list_of_products = ref.child(str(message.chat.id) + "/My_products").get()
            new_dict = {}
            print(type(list_of_products))
            #Счетчик нового массива
            i = 1
            #Счетчик исходного массива
            n = 1
            
            #Бежим по словарю продуктов
            for item in list_of_products:
                
        
                if (int(message.text) != n):
                    new_item = ref.child(str(message.chat.id) + "/My_products/" + item).get()

                    new_dict.update({item:new_item})
                    i += 1
                n+=1

            ref.child(str(message.chat.id) + "/My_products").set(new_dict)
            bot.send_message(message.chat.id, "дело сделано!")
        except Exception:
            print("блок удаляющий продукт из моего реестра уронил все")
            bot.send_message(message.chat.id, "что-то пошло не так!")
            
        finally:
            ref.child(str(message.chat.id)).update({"state":"start"})

    elif(ref.child(str(message.chat.id)+"/state").get() == "waiting_gay"):
        #заменим точки на подчеркивания
        required_data = re.sub(".", "_", message.text)

bot.polling()
