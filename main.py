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

    schedule = {
        4: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        5: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        6: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        7: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        8: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        9: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}},
        10: {'main': {'name': '', 'prep': '', 'cab': ''}, 'add': {'name': '', 'prep': '', 'cab': ''}}
    }

    cells = {}
    limit = 0

    for j in rows:
        if limit <= 10:
            limit += 1
            cells[limit] = j.find_all('td', class_='ur')

    for i in cells:
        if i not in schedule:
            continue

        isMain = True
        if len(cells[i]) > 1:
            for cell in cells[i]:
                if isMain:
                    if cell.find('a', class_='z1') is not None:
                        schedule[i]['main']['name'] = cell.find('a', class_='z1').text
                    # else:
                    #     schedule[i]['main']['name'] = 'У этой подгруппы нет пары'
                    #     print('no')

                    if cell.find('a', class_='z3') is not None:
                        schedule[i]['main']['prep'] = cell.find('a', class_='z3').text
                    if cell.find('a', class_='z2') is not None:
                        schedule[i]['main']['cab'] = cell.find('a', class_='z2').text
                else:
                    if cell.find('a', class_='z1') is not None:
                        schedule[i]['add']['name'] = cell.find('a', class_='z1').text
                    # else:
                    #     schedule[i]['add']['name'] = 'У этой подгруппы нет пары'
                    #     print('no')

                    if cell.find('a', class_='z3') is not None:
                        schedule[i]['add']['prep'] = cell.find('a', class_='z3').text
                    if cell.find('a', class_='z2') is not None:
                        schedule[i]['add']['cab'] = cell.find('a', class_='z2').text
                isMain = False
        else:
            for cell in cells[i]:
                if cell.find('a', class_='z1') is not None:
                    schedule[i]['main']['name'] = cell.find('a', class_='z1').text
                if cell.find('a', class_='z3') is not None:
                    schedule[i]['main']['prep'] = cell.find('a', class_='z3').text
                if cell.find('a', class_='z2') is not None:
                    schedule[i]['main']['cab'] = cell.find('a', class_='z2').text

    return schedule

def GetScheduleText(schedule_dict):
    output_text = ""
    
    for day, subjects in schedule_dict.items():
        output_text += f"<b>📅 Пара {day - 3}:</b>\n"
        
        for key in ['main', 'add']:
            subject = subjects[key]
            subject_info = []
            
            # Составляем информацию о предмете, пропуская пустые поля
            if subject['name']:
                subject_info.append(f"\n\t\t\t\t\t\t\t\t{subject['name']}")
            if subject['prep']:
                subject_info.append(f"\t\t\t\t\t\t\t\t{subject['prep']}")
            if subject['cab']:
                subject_info.append(f"\t\t\t\t\t\t\t\t{subject['cab']}")
            
            if subject_info:
                output_text += "<b>"
                output_text += "\n".join(subject_info)
                output_text += "</b>\n"
            # else:
            #     output_text += "<b>—</b>\n"
        
        output_text += "\n"  # Добавляем пустую строку между днями
    
    return output_text.strip()

url = ''
user_id = ''

bot = Bot('7565630801:AAEJS3zZtetuZL2AW3Pit-QYz4ijVb9obuk')
dp = Dispatcher(bot)

# Создаем клавиатуру
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("Текущая ссылка"))
keyboard.add(KeyboardButton("Получить текущее расписание форсированно"))

@dp.message_handler(commands='start')
async def start(message: types.Message):
    global user_id
    user_id = message.from_user.id
    await message.answer(
        "Привет! Я - Бот расписания СКСиПТ\nЯ отправляю нужное вам расписание в 17:30 каждый день\nНо для начала, введите ссылку НЕДЕЛЬНОГО расписания вашей группы\nОна будет в будущем использоваться для взятия расписания и отправки вам, без передачи ссылки расписание приходить не БУДЕТ.\nУчтите, что ссылки меняются каждый семестр!\nПример: http://schedule.ckstr.ru/cg142.htm\n\n<pre>Бот находится в beta-test версии и прекращает работу 20.02.25</pre>",
        reply_markup=keyboard, parse_mode='html'
    )

@dp.message_handler(lambda message: message.text.startswith('http://schedule.ckstr.ru/cg'))
async def capture_url(message: types.Message):
    global user_id
    user_id = message.from_user.id
    global url
    url = message.text
    await message.reply("Ссылка сохранена! Теперь я буду отправлять вам расписание в 17:30 каждый день\nЕсли захотите поменять ее, то просто отправьте в чат новую и я автоматически сменю целевую ссылку", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text == "Текущая ссылка")
async def show_current_url(message: types.Message):
    await message.answer("Обрабатываю запрос... Подождите 5 секунд.")
    await asyncio.sleep(5)  # Задержка 5 секунд
    if url:
        await message.answer(f"Текущая ссылка: {url}")
    else:
        await message.answer("Ссылка не установлена!")

@dp.message_handler(lambda message: message.text == "Получить текущее расписание форсированно")
async def force_get_schedule(message: types.Message):
    await message.answer("Обрабатываю запрос... Подождите 5 секунд.")
    await asyncio.sleep(5)  # Задержка 5 секунд
    if url:
        temp = GetScheduleDict(url)
        res = GetScheduleText(temp)
        await message.answer(text=res, parse_mode='html')
    else:
        await message.answer("Ссылка не установлена!")

async def on_startup(dp):
    asyncio.create_task(send_message_at_time())

async def send_message_at_time():
    ekaterinburg_tz = pytz.timezone('Asia/Yekaterinburg')

    while True:
        now = datetime.now(ekaterinburg_tz)
        target_time = now.replace(hour=6, minute=0, second=0, microsecond=0)
        
        if now > target_time:
            target_time += timedelta(days=1)
        
        wait_time = (target_time - now).total_seconds()
        await asyncio.sleep(wait_time)
        
        if target_time.weekday() < 6:  # 0-4 — понедельник-пятница
            if user_id:
                temp = GetScheduleDict(url)
                res = GetScheduleText(temp)
                await bot.send_message(user_id, text=res, parse_mode='html', reply_markup=keyboard)
            else:
                print("user_id не установлен, сообщение не отправлено")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
