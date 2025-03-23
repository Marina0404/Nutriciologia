

#АКТУАЛЬНЫЙ 
import logging
import asyncio
import nest_asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from math import ceil, floor

TOKEN = "6816802285:AAHJZYNriP32u-RXFgIEa-i6KnFnlWdECgE"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    gender = State()
    weight = State()
    height = State()
    age = State()

def round_to_5(value, method):
    return ceil(value / 5) * 5 if method == "ceil" else floor(value / 5) * 5

def calculate_maintenance(gender, weight, height, age):
    if gender.lower() == "мужчина":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
        method = "ceil"
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161
        method = "floor"

    bmr -= 200 if bmr < 1800 else 300

    maintenance = round_to_5(bmr / 13, method)
    loss = round_to_5(maintenance * 0.9, method)
    gain = round_to_5(maintenance * 1.15, method)

    return loss, maintenance, gain

@dp.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.set_state(Form.gender)
    await message.answer("Привет! Укажи свой пол (Мужчина/Женщина):")

@dp.message(Form.gender)
async def get_gender(message: Message, state: FSMContext):
    gender = message.text.lower()
    if gender not in ["мужчина", "женщина"]:
        await message.answer("Пожалуйста, введи 'Мужчина' или 'Женщина'")
        return
    await state.update_data(gender=gender)
    await state.set_state(Form.weight)
    await message.answer("Теперь укажи свой вес (кг):")

@dp.message(Form.weight)
async def get_weight(message: Message, state: FSMContext):
    try:
        weight = float(message.text)
        await state.update_data(weight=weight)
        await state.set_state(Form.height)
        await message.answer("Теперь укажи свой рост (см):")
    except ValueError:
        await message.answer("Пожалуйста, введи числовое значение веса.")

@dp.message(Form.height)
async def get_height(message: Message, state: FSMContext):
    try:
        height = float(message.text)
        await state.update_data(height=height)
        await state.set_state(Form.age)
        await message.answer("Теперь укажи свой возраст (лет):")
    except ValueError:
        await message.answer("Пожалуйста, введи числовое значение роста.")

@dp.message(Form.age)
async def get_age(message: Message, state: FSMContext):
    try:
        age = int(message.text)
        user_data = await state.get_data()
        loss, maintenance, gain = calculate_maintenance(user_data['gender'], user_data['weight'], user_data['height'], age)

        response = (
            f" Результаты расчета Диеты 2+1:\n"
            f"✅ Ваш коэффициент для похудения: {loss} гр\n"
            f" ⚖ Коэффициент для поддержания веса: {maintenance} гр\n"
            f"📈 Ваш коэффициент для набора веса: {gain} гр\n\n"
            f"Спасибо за использование бота!"
        )

        await message.answer(response)
        await state.clear()  # Очищаем состояние пользователя
    except ValueError:
        await message.answer("Пожалуйста, введи числовое значение возраста.")

nest_asyncio.apply()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
