import logging
from aiogram import Bot, Dispatcher, types
from aiogram import executor
import openai
from function import check_complexity, process_simple_query
import datetime
import os
from environs import Env

env = Env()
env.read_env()

# Ваш токен Telegram бота
API_TOKEN=""
OPENAI_API_KEY =""


# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

logging.basicConfig(level=logging.INFO)

openai.api_key = OPENAI_API_KEY

# Функция для обработки сложных запросов через ChatGPT
def handle_complex_query(query):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message["content"]


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Помни, что \n"
                    "• Я не запоминаю предыдущие запросы, поэтому постарайся уместить все в одном сообщении \n"
                    "• К сожалению я реагирую только на текст, поэтому не присылай мне картинки/аудио \n"
                    "• Если я долго не отвечаю, значит я генерирую ответ, спасибо за терпение \n"
                    "• Я знаком только с событиями происходившими до 2021-го года ")


# Обработчик текстовых сообщений
@dp.message_handler(content_types=types.ContentType.TEXT)
async def handle_text_message(message: types.Message):
    user_query = message.text
    user_id = message.from_user.id
    username = message.from_user.username

    current_datetime = datetime.datetime.now()
    formatted_date = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    add_data = open("data.txt", "a")
    add_data.write(f'Время запроса: {formatted_date} | Имя пользователя: {username} | ID пользователя: {user_id} | Запрос пользователя: {user_query} \n')

    # Проверьте, является ли запрос сложным
    is_complex_query = check_complexity(user_query)

    if is_complex_query:
        # Если запрос сложный, обработайте его с помощью ChatGPT
        response_text = handle_complex_query(user_query)
    else:
        # Если запрос простой, обработайте его стандартным образом
        response_text = process_simple_query(user_query)

    await message.answer(response_text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
