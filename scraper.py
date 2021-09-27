from selenium.webdriver.common.keys import Keys
import os
from os import getenv
import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from controller import insert_lecture
from utils import wait_until_present, js_click, get_json, parse_json


EA_LOGIN_URL = "https://easyacademy.unige.it/portalestudenti/index.php?view=login&include=login&from=prenotalezione&from_include=prenotalezione_home&_lang=it"
BOOKING_URL = "https://easyacademy.unige.it/portalestudenti/index.php?view=prenotalezione&include=prenotalezione"


def ea_login(driver):
    try:
        driver.get(EA_LOGIN_URL)
        login_button = wait_until_present(driver, el_id="oauth_btn")
        switches = driver.find_elements_by_class_name("switch")
        for switch in switches:
            js_click(driver, switch)
        js_click(driver, login_button)
        return driver.get_cookies()[0]["value"]
    except Exception as e:
        logging.exception(e)


def ug_login(driver, username, password):
    try:
        wait_until_present(driver, el_id="username").send_keys(username)
        driver.find_element_by_id("password").send_keys(password)
        driver.execute_script("document.getElementsByName('f')[0].submit()")
    except Exception as e:
        logging.exception(e)


def update_lectures():
    binary = FirefoxBinary(os.environ.get('FIREFOX_BIN'))
    options = webdriver.firefox.options.Options()
    options.headless = True
    driver = webdriver.Firefox(
        firefox_binary=binary,
        executable_path=os.environ.get('GECKODRIVER_PATH'),
        options=options)
    try:
        phpsessid = ea_login(driver)
        ug_login(driver, getenv("MATRICOLA"), getenv("PASSWORD"))
        sleep(2)
        reservable_seats = parse_json(
            get_json(phpsessid, BOOKING_URL, "var lezioni_prenotabili = JSON.parse('"))
        reserved_seats = parse_json(get_json(
            phpsessid, f"{BOOKING_URL}_gestisci", "var lezioni_prenotate = JSON.parse('"))
        for lecture in (reservable_seats + reserved_seats):
            insert_lecture(lecture)
    except Exception as e:
        logging.exception(e)
    driver.quit()


def update_lectures_loop(thread=False):
    while True:
        try:
            update_lectures()
        except Exception as e:
            logging.exception(e)
        sleep(60 * 30)
