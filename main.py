TOKEN = 'YOUR_BOT_TOKEN_HERE'
from homeworks import Homeworks, Time, Cabinet

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.error import Conflict
from datetime import datetime
from colorama import Fore, Style, init
import json, requests, httpx
import nest_asyncio
import asyncio
import logging
import psutil
import sys
import os

nest_asyncio.apply()
init(autoreset=True)

keyboard = [
        [InlineKeyboardButton(" Обратно в Меню ", callback_data='menu_again')],
    ]

class ColoredFormatter(logging.Formatter):
    """Класс для форматирования логов с цветами."""
    def format(self, record):
        if record.levelname == "INFO":
            record.msg = f"{Fore.CYAN}{record.msg}{Style.RESET_ALL}"
        return super().format(record)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = ColoredFormatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARNING)
logger.setLevel(logging.ERROR)
logger.setLevel(logging.CRITICAL)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext").setLevel(logging.WARNING)

def kill_python_processes():
    current_pid = os.getpid()  # Получаем PID текущего процесса
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] == 'python.exe' and proc.info['pid'] != current_pid:
                proc.kill()  # Завершаем процесс
                print(f'\r{Fore.WHITE}[{time_now()}] {Fore.GREEN}I: Процесс {proc.info["pid"]} завершен.{Fore.RESET}')
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def logs(TG_USER_NICK, TG_USER_ID,  COMMAND):
    print(f"\r{Fore.WHITE}[{time_now()}] {Fore.GREEN}I:{Fore.LIGHTYELLOW_EX} @{TG_USER_NICK}[{TG_USER_ID}]{Fore.LIGHTWHITE_EX} использовал команду{Fore.LIGHTCYAN_EX} {COMMAND} {Fore.RESET}")
    with open(f'logs.log', 'a', encoding='utf-8') as file:
        file.write(f"\r[{time_now()}] @{TG_USER_NICK}[{TG_USER_ID}] использовал команду {COMMAND}.")
def time_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global message
    user = update.effective_user
    logs(user.username, user.id, '/start')
    await update.message.reply_text('Привет! Я бот для работы с электронным журналом.')
    await menu(update, context)

########################################################################################################################
async def lessons_study(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global keyboard, message
    user = update.effective_user
    logs(user.username, user.id, '/lessons_study')
    text = ''
    for i in range(len(Homeworks.keys())):
        text += f'{list(Homeworks.keys())[i]} - {list(Homeworks.values())[i]}' + '\n'
    context.user_data['message'] = message.message_id
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await context.bot.edit_message_text(chat_id=user.id, message_id=message.message_id, text=text, reply_markup=reply_markup)
    context.user_data['message'] = message.message_id

async def time_study(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global keyboard, message
    user = update.effective_user
    logs(user.username, user.id, '/times_study')
    text = ''
    for i in range(len(Time.keys())):
        text += f'{list(Time.keys())[i]} - {list(Time.values())[i]}' + '\n'
    context.user_data['message'] = message.message_id
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await context.bot.edit_message_text(chat_id=user.id, message_id=message.message_id, text=text, reply_markup=reply_markup)

async def cabinet_study(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global keyboard, message
    user = update.effective_user
    logs(user.username, user.id, '/cabinet_study')
    text = ''
    for i in range(len(Cabinet.keys())):
        text += f'{list(Cabinet.keys())[i]} - {list(Cabinet.values())[i]}' + '\n'
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = await context.bot.edit_message_text(chat_id=user.id, message_id=message.message_id, text=text, reply_markup=reply_markup)
    context.user_data['message'] = message.message_id
########################################################################################################################

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'time_study':
        await time_study(update, context)
    elif query.data == 'cabinet_study':
        await cabinet_study(update, context)
    elif query.data == 'lessons_study':
        await lessons_study(update, context)
    elif query.data == 'menu_again':
        await menu_again(update, context)

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global message
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton(" Домашние задания ", callback_data='lessons_study')],
        [InlineKeyboardButton(" Время Занятий ", callback_data='time_study')],
        [InlineKeyboardButton(" Кабинет ", callback_data='cabinet_study')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    new_text = 'Выберите нужную опцию:'

    # Проверяем, было ли сообщение отправлено ранее
    if 'message' in context.user_data:
        message_id = context.user_data['message']
        try:
            message = await context.bot.send_message(chat_id=user.id, text=new_text, reply_markup=reply_markup)
            message_id = context.user_data['message']
        except Exception as e:
            print(f"Ошибка при редактировании сообщения: {e}")

    else:
        message = await context.bot.send_message(chat_id=user.id, text=new_text, reply_markup=reply_markup)
        context.user_data['message'] = message.message_id

async def menu_again(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global message
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton(" Домашние задания ", callback_data='lessons_study')],
        [InlineKeyboardButton(" Время Занятий ", callback_data='time_study')],
        [InlineKeyboardButton(" Кабинет ", callback_data='cabinet_study')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    new_text = 'Выберите нужную опцию:'
    message_id = context.user_data['message']
    message = await context.bot.edit_message_text(chat_id=user.id, message_id=message_id, text=new_text, reply_markup=reply_markup)
    message_id = context.user_data['message']




async def main():
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe").json()
        print(f"\r{Fore.WHITE}[{time_now()}] {Fore.GREEN}I: {Fore.BLUE}Телеграмм бот{Fore.LIGHTYELLOW_EX} @{response['result']['username']}{Fore.BLUE} запущен")
        with open(f'logs.log', 'a') as file:
            file.write(f"\r[{time_now()}] Телеграмм бот @{response['result']['username']} запущен")

        app = ApplicationBuilder().token(TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("time_study", time_study))
        app.add_handler(CommandHandler("cabinet_study", cabinet_study))
        app.add_handler(CommandHandler("lessons_study", lessons_study))
        app.add_handler(CommandHandler("menu", menu))
        app.add_handler(CallbackQueryHandler(button))
        await app.run_polling()

    except Conflict:
        print(f"{Fore.LIGHTRED_EX}E: Неожиданная ошибка! Убедитесь, что только один экземпляр бота запущен.")
        time.sleep(2)
    except httpx.ReadError as e:
        print(f"{Fore.LIGHTRED_EX}E: Ошибка чтения ответа от сервера: {e}")
    except Exception as e:
        logger.exception(f"{Fore.LIGHTRED_EX}E: Ошибка: %s", e)
    except BadRequest as e:
        print(f"Ошибка редактирования сообщения: {e}")
    except:
        print(f"{Fore.LIGHTRED_EX}E: Неожиданная ошибка!")

if __name__ == '__main__':
    #_ = input('Terminate other PYTHON processes? Y/n: ')
    #if _.lower() == 'y' or _.lower() == 'yes':
    #    kill_python_processes() #REMEMBER TO DO NORMAAAAAAAAAAAAAAAAAAAAAAAAAL!!!!
    asyncio.run(main())