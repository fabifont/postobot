import logging
import requests
from os import getenv
from io import BytesIO
from datetime import datetime


API_URL = "https://easyacademy.unige.it/portalestudenti/call_ajax.php"
QR_URL = "https://easyacademy.unige.it/portalestudenti/export_pdf2.php"


async def book(lesson_id, username):
  try:
    params = {
        "mode": "salva_prenotazioni",
        "codice_fiscale": username,
        "id_entries": f"[{lesson_id}]"
    }
    res = requests.get(API_URL, params=params)
    if "presente" in res.text:
      return -1
    elif "Trying to get property 'ID' of non-object" in res.text:
      return -2
    return 0
  except Exception as e:
    logging.exception(e)


async def delete_booking(lesson_id, username):
  try:
    params = {
        "mode": "cancella_prenotazioni",
        "codice_fiscale": username,
        "id_entries": f"[{lesson_id}]"
    }
    res = requests.get(API_URL, params=params)
    if "{}" in res.text:
      return -1
    return 0
  except Exception as e:
    logging.exception(e)


async def get_qr_bytes(lecture):
  try:
    data = {
        "language": "en",
        "matricola": getenv("ID"),
        "color": "333333",
        "qr": lecture.qr,
        "sede": lecture.sede,
        "ora_inizio": lecture.ora_inizio,
        "ora_fine": lecture.ora_fine,
        "data_lezione": f"{datetime.strptime(lecture.data_lezione, '%d/%m/%Y').strftime('%A %d %B %Y')}",
        "ora_prima_lezione": lecture.ora_inizio,
        "prenotazioni[]": f"true|{lecture.nome}|{lecture.ora_inizio_lezione} - {lecture.ora_fine_lezione}|{lecture.aula}|0"
    }
    response = requests.post(QR_URL, data=data)
    return BytesIO(response.content)
  except Exception as e:
    logging.exception(e)
