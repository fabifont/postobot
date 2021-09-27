import math
import json
import logging
import requests
from time import sleep
from bs4 import BeautifulSoup
from aiogram.types import ReplyKeyboardMarkup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from models import Lecture
from controller import exists, cleanup


def wait_until_present(driver, xpath=None, class_name=None, el_id=None, name=None, duration=5, frequency=0.01):
    if xpath:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.XPATH, xpath)))
    elif class_name:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
    elif el_id:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.ID, el_id)))
    elif name:
        return WebDriverWait(driver, duration, frequency).until(EC.presence_of_element_located((By.NAME, name)))


def js_click(driver, element):
    driver.execute_script("arguments[0].click()", element)


def get_json(phpsessid, url, var_identifier):
    cookies = {"PHPSESSID": f"{phpsessid}"}
    r = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(r.text, "html.parser")
    lessons = str(soup).split(var_identifier)[1].split("') ;")[0]
    return json.loads(lessons)


def parse_json(json):
    bookings = []
    for booking_group in json:
        qr = booking_group["qr"]
        sede = booking_group["sede"]
        ora_inizio = booking_group["ora_inizio"]
        ora_fine = booking_group["ora_fine"]
        data_lezione = booking_group["data"]
        for booking in booking_group["prenotazioni"]:
            ora_inizio_lezione = booking["ora_inizio"]
            ora_fine_lezione = booking["ora_fine"]
            aula = booking["aula"]
            entry_id = booking["entry_id"]
            nome = booking["nome"]
            lecture = Lecture(entry_id=entry_id, sede=sede, aula=aula, data_lezione=data_lezione, ora_inizio=ora_inizio,
                              ora_fine=ora_fine, qr=qr, nome=nome, ora_inizio_lezione=ora_inizio_lezione, ora_fine_lezione=ora_fine_lezione)
            bookings.append(lecture)
    return bookings


def parse_lecture(label, qr=False):
    try:
        data = label.split("\n")
        entry_id = data[0].split(" ")[0]
        if not entry_id.isnumeric() or len(entry_id) != 7:
            return None
        if exists(entry_id, qr):
            return entry_id
        return None
    except Exception as e:
        logging.exception(e)


async def get_labels(lectures):
    return [str(lecture) for lecture in lectures]


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


async def gen_markup(data, step):
    labels = await get_labels(data)
    pool = split(labels, math.ceil(len(labels) / step))
    markup = ReplyKeyboardMarkup()
    markup.add("/annulla")
    for elems in pool:
        markup.add(*elems)
    return markup


def db_cleanup():
    while True:
        cleanup()
        sleep(60 * 30)
