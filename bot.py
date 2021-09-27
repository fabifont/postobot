import asyncio
import logging
import threading
from os import getenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from scraper import update_lectures
from utils import gen_markup, parse_lecture
from api import book, delete_booking, get_qr_bytes
from controller import get_lecture, get_reserved_seats, get_reservable_seats

PROFILE_URL = "https://easyacademy.unige.it/portalestudenti/index.php?view=prenotalezione&include=prenotalezione_profilo"

WELCOME_STR = """
Questo bot permette di prenotare i posti a lezione per i corsi di UniGe.\n
/prenota prenota una lezione tra quelle disponibili.
/prenotate ottieni il QR di una lezione tra quelle prenotate.
/cancella cancella una lezione tra quelle prenotate.
/annulla annulla la procedura corrente.
"""


bot = Bot(getenv("BOT_TOKEN"))
dispatcher = Dispatcher(bot, storage=MemoryStorage())


class NewRequest(StatesGroup):
    label = State()


class QrRequest(StatesGroup):
    label = State()


class DeleteRequest(StatesGroup):
    label = State()


async def update_and_send_qr(entry_id, chat_id):
    try:
        update_lectures()
        lecture = get_lecture(entry_id)
        qr_bytes = await get_qr_bytes(lecture)
        bot2 = Bot(getenv("BOT_TOKEN"))
        qr_file = types.InputFile(qr_bytes, f"qr_{lecture.entry_id}.pdf")
        await bot2.send_document(chat_id, qr_file)
        await bot2.close()
    except Exception as e:
        logging.exception(e)


def aux_uasr(entry_id, chat_id):
    asyncio.run(update_and_send_qr(entry_id, chat_id))


if getenv("CHAT_ID") is not None:
    @dispatcher.message_handler(lambda message: message.from_user.id != int(getenv("CHAT_ID")), content_types=["any"])
    async def handle_unwanted_users(message: types.Message):
        try:
            await message.reply("Non sei autorizzato ad eseguire comandi.")
        except Exception as e:
            logging.exception(e)


@dispatcher.message_handler(commands="start")
async def start(message: types.Message):
    try:
        await message.reply(WELCOME_STR)
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(commands="prenota")
async def reservable_seats(message: types.Message):
    try:
        reservable_seats = get_reservable_seats()
        if len(reservable_seats) < 1:
            await message.reply("Non ci sono lezioni prenotabili.")
        else:
            await NewRequest.label.set()
            markup = await gen_markup(reservable_seats, 1)
            await message.reply("Scegli la lezione da prenotare.", reply_markup=markup)
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(state="*", commands="annulla")
async def cancel_handler(message: types.Message, state: FSMContext):
    try:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply("Annullato.", reply_markup=types.ReplyKeyboardRemove())
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(lambda message: parse_lecture(message.text) is None, state=NewRequest.label)
async def process_invalid_new_label(message: types.Message):
    try:
        await message.reply("Scelta errata!\nRiprova.")
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(state=NewRequest.label)
async def process_new_label(message: types.Message, state: FSMContext):
    try:
        entry_id = parse_lecture(message.text)
        result = await book(entry_id, getenv("MATRICOLA"))
        if result == -1:
            await bot.send_message(message.chat.id, "Ti sei già prenotato per questa lezione.")
        elif result == -2:
            await bot.send_message(message.chat.id, f"La matricola non esiste oppure non hai ancora impostato un profilo, fallo [qui]({PROFILE_URL})", parse_mode=types.ParseMode.MARKDOWN)
        else:
            await bot.send_message(message.chat.id, "Prenotazione effettuata, riceverai il QR code a breve.", reply_markup=types.ReplyKeyboardRemove())
            threading.Thread(target=aux_uasr, args=(
                entry_id, message.chat.id)).start()
        await state.finish()
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(commands="prenotate")
async def reserved_seats_qr(message: types.Message):
    try:
        reserved_seats = get_reserved_seats()
        if len(reserved_seats) < 1:
            await message.reply("Non ci sono lezioni prenotate.")
        else:
            await QrRequest.label.set()
            markup = await gen_markup(reserved_seats, 1)
            await message.reply("Scegli una lezione per ottenere il QR.", reply_markup=markup)
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(lambda message: parse_lecture(message.text) is None, state=QrRequest.label)
async def process_invalid_qr_label(message: types.Message):
    try:
        await message.reply("Scelta errata!\nRiprova.")
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(state=QrRequest.label)
async def process_qr_label(message: types.Message, state: FSMContext):
    try:
        entry_id = parse_lecture(message.text)
        threading.Thread(target=aux_uasr, args=(
            entry_id, message.chat.id)).start()
        await bot.send_message(message.chat.id, "Riceverai il QR a breve.", reply_markup=types.ReplyKeyboardRemove())
        await state.finish()
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(commands="cancella")
async def reserved_seats_delete(message: types.Message):
    try:
        reserved_seats = get_reserved_seats()
        if len(reserved_seats) < 1:
            await message.reply("Non ci sono lezioni prenotate.")
        else:
            await DeleteRequest.label.set()
            markup = await gen_markup(reserved_seats, 1)
            await message.reply("Scegli la lezione da cancellare.", reply_markup=markup)
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(lambda message: parse_lecture(message.text) is None, state=DeleteRequest.label)
async def process_invalid_delete_label(message: types.Message):
    try:
        await message.reply("Scelta errata!\nRiprova.")
    except Exception as e:
        logging.exception(e)


@dispatcher.message_handler(state=DeleteRequest.label)
async def process_delete_label(message: types.Message, state: FSMContext):
    try:
        entry_id = parse_lecture(message.text)
        result = await delete_booking(entry_id, getenv("MATRICOLA"))
        if result == -1:
            await bot.send_message(message.chat.id, "Hai già cancellato questa prenotazione.")
        else:
            await bot.send_message(message.chat.id, "Cancellazione effettuata.", reply_markup=types.ReplyKeyboardRemove())
            threading.Thread(target=update_lectures).start()
        await state.finish()
    except Exception as e:
        logging.exception(e)


def run():
    executor.start_polling(dispatcher)
