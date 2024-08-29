from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
import asyncio

api = ''
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()

def create_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
    buttons = [
        types.KeyboardButton("Рассчитать"),
        types.KeyboardButton("Информация")
    ]
    kb.add(*buttons)
    return kb

def create_inline_keyboard():
    kb = InlineKeyboardMarkup()
    buttons = [
        InlineKeyboardButton("Рассчитать норму калорий", callback_data='calories'),
        InlineKeyboardButton("Формулы расчёта", callback_data='formulas')
    ]
    kb.add(*buttons)
    return kb

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Привет! Я бот помогающий твоему здоровью. Нажми "Рассчитать", чтобы начать.',
                         reply_markup=create_keyboard())

@dp.message_handler(lambda message: message.text == "Рассчитать")
async def main_menu(message: types.Message):
    await message.answer('Выберите опцию:', reply_markup=create_inline_keyboard())

@dp.callback_query_handler(lambda call: call.data == 'formulas')
async def get_formulas(call: types.CallbackQuery):
    await call.message.answer("Формула Миффлина-Сан Жеора:\n"
                              "Для мужчин: BMR = 10 * вес + 6.25 * рост - 5 * возраст + 5\n"
                              "Для женщин: BMR = 10 * вес + 6.25 * рост - 5 * возраст - 161")
    await call.answer()

@dp.callback_query_handler(lambda call: call.data == 'calories')
async def set_age(call: types.CallbackQuery):
    await call.message.answer('Введите свой возраст:')
    await UserState.age.set()

@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (0 < int(message.text) < 120):
        await message.answer('Пожалуйста, введите корректный возраст (число от 1 до 120).')
        return
    await state.update_data(age=message.text)
    await message.answer('Введите свой рост в см:')
    await UserState.growth.set()

@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (50 < int(message.text) < 300):
        await message.answer('Пожалуйста, введите корректный рост (число от 50 до 300 сантиметров).')
        return
    await state.update_data(growth=message.text)
    await message.answer('Введите свой вес в кг:')
    await UserState.weight.set()

@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    if not message.text.isdigit() or not (20 < int(message.text) < 300):
        await message.answer('Пожалуйста, введите корректный вес (число от 20 до 300 кг).')
        return
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])
    calories = 10 * weight + 6.25 * growth - 5 * age + 5
    await message.answer(f'Ваша норма калорий: {calories} ккал в день.')
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)