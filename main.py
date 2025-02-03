import requests
from bs4 import BeautifulSoup
from aiogram import types, Bot, Dispatcher, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import asyncio
from datetime import datetime, timedelta
import pytz

def GetScheduleDict(scheduleUrl):

    res = requests.get(scheduleUrl)
    soup = BeautifulSoup(res.content, 'lxml')
    tbody = soup.find('table', class_='inf')
    rows = tbody.find_all('tr')

    schedule = {4:{'main':{'name':'', 'prep':'', 'cab':''}, 'add':{'name':'', 'prep':'', 'cab':''}},
            5:{'main':{'name':'', 'prep':'', 'cab':''}, 'add':{'name':'', 'prep':'', 'cab':''}},
            6:{'main':{'name':'', 'prep':'', 'cab':''}, 'add':{'name':'', 'prep':'', 'cab':''}},
            7:{'main':{'name':'', 'prep':'', 'cab':''}, 'add':{'name':'', 'prep':'', 'cab':''}},
            8:{'main':{'name':'', 'prep':'', 'cab':''}, 'add':{'name':'', 'prep':'', 'cab':''}},
            9:{'main':{'name':'', 'prep':'', 'cab':''}, 'add':{'name':'', 'prep':'', 'cab':''}},
            10:{'main':{'name':'', 'prep':'', 'cab':''}, 'add':{'name':'', 'prep':'', 'cab':''}}}


    cells = {}
    limit = 0

    for j in rows:
        if (limit <= 10):
            limit = limit + 1
            cells[limit] = j.find_all('td', class_='ur') #возможно понадобится изменение индекса чтобы первая пара совпадала с цифр 1

    for i in cells: #в каждом результсете
        isMain = True
        if (len(cells[i]) > 1):
            for cell in cells[i]: #в результсете перебираем теги
                if (isMain):
                    schedule[i]['main']['name'] = cell.find('a', class_='z1').text
                    schedule[i]['main']['prep'] = cell.find('a', class_='z3').text
                    schedule[i]['main']['cab'] = cell.find('a', class_='z2').text
                if (not isMain):
                    schedule[i]['add']['name'] = cell.find('a', class_='z1').text
                    schedule[i]['add']['prep'] = cell.find('a', class_='z3').text
                if (cell.find('a', class_='z2') != None):
                    schedule[i]['add']['cab'] = cell.find('a', class_='z2').text
                isMain = False

        if (len(cells[i]) == 1):
            for cell in cells[i]: #в результсете перебираем теги
                    schedule[i]['main']['name'] = cell.find('a', class_='z1').text
                    schedule[i]['main']['prep'] = cell.find('a', class_='z3').text
                    if (cell.find('a', class_='z2') != None):
                        schedule[i]['add']['cab'] = cell.find('a', class_='z2').text

    return schedule

def GetScheduleText(schedule_dict):
    output_text = ""

    for day, subjects in schedule_dict.items():
        output_text += f"<b> Пара {day - 3}: </b>\n"
        
        for key in ['main', 'add']:
            subject = subjects[key]
            subject_info = []
            
            # Составляем информацию о предмете, пропуская пустые поля
            if subject['name']:
                subject_info.append(f"Предмет: {subject['name']}")
            if subject['prep']:
                subject_info.append(f"Преподаватель: {subject['prep']}")
            if subject['cab']:
                subject_info.append(f"Каб.: {subject['cab']}")
            
            if subject_info:
                output_text += f"  ------------------------------\n"  # Заменяем "main" и "add" на строку
                output_text += '\n'.join(['    ' + info for info in subject_info]) + '\n'
                output_text += f"  ------------------------------\n"
            else:
                output_text += f"  ------------------------------\n"  # Заменяем "Нет." на "-"

    output_text = output_text.strip()
    return output_text

url = ''
user_id = ''

bot = Bot('7565630801:AAEJS3zZtetuZL2AW3Pit-QYz4ijVb9obuk')
dp = Dispatcher(bot)


@dp.message_handler(commands='start')
async def start(message: types.Message):
    global user_id
    user_id = message.from_user.id  # Сохраняем ID в глобальной переменной
    await message.answer("Привет! Я - Бот расписания СКСиПТ\nЯ отправляю нужное вам расписание в 17:00 каждый день\nНо для начала, введите ссылку НЕДЕЛЬНОГО расписания вашей группы\nОна будет в будущем использоваться для взятия расписания и отправки вам, без передачи ссылки расписание приходить не БУДЕТ.\nУчтите, что ссылки меняются каждый семестр!\nПример: http://schedule.ckstr.ru/cg142.htm\n")
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    button_input = KeyboardButton("Ввести ссылку")
    button_get = KeyboardButton("Проверить ссылку")
    keyboard.add(button_input, button_get)




@dp.message_handler(lambda message: message.text == "Ввести ссылку")
async def ask_for_url(message: types.Message):
    await message.reply("Введите ссылку НЕДЕЛЬНОГО расписания вашей группы\nПример: http://schedule.ckstr.ru/cg142.htm")




@dp.message_handler(lambda message: message.text == "Проверить ссылку")
async def get_url(message: types.Message):
    if url:  # Проверяем, установлен ли URL
        await message.answer(text=url)  
    else:
        await message.answer(text="Ссылка еще не была сохранена.")


@dp.message_handler(lambda message: message.text.startswith('http'))  # Захватываем только URL
async def capture_url(message: types.Message):
    global url
    url = message.text  # Сохраняем URL в глобальной переменной
    await message.reply("Ссылка сохранена! Теперь я буду отправлять вам расписание в 17:00 каждый день\nЕсли захотите поменять ее, то просто отправьте в чат новую и я автоматически сменю целевую ссылку")


async def send_message_at_time():

    # Установите часовой пояс Екатеринбурга
    ekaterinburg_tz = pytz.timezone('Asia/Yekaterinburg')

    while True:

        # Получите текущее время в Екатеринбурге
        now = datetime.now(ekaterinburg_tz)
        # Установите время, когда хотите отправить сообщение (например, каждый день в 10:00)
        target_time = now.replace(hour=17, minute=0, second=0, microsecond=0)
        
        # Если текущее время больше целевого, установите целевое время на следующий день
        if now > target_time:
            target_time += timedelta(days=1)
        
        # Вычисляем время ожидания
        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)  # Ждем до целевого времени
        
        # Отправляем сообщение
        await bot.send_message(user_id, text=url)        


# @dp.message_handler(commands='getschedule')
# async def get_url(message: types.Message):
#     temp = GetScheduleDict(url)
#     res = GetScheduleText(temp)
#     await message.answer(text=res, parse_mode='html')


if __name__ == '__main__':
    try:
        asyncio.run(executor.start_polling(dp, skip_updates=True))  # Запускаем бота
        asyncio.run(send_message_at_time())  # Запускаем отправку сообщений
    except Exception as e:
        print(f"Ошибка: {e}")

