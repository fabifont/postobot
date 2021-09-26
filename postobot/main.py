import threading

import bot
import scraper
from utils import db_cleanup

if __name__ == "__main__":
  scraper.update_lectures()
  threading.Thread(target=scraper.update_lectures_loop).start()
  threading.Thread(target=db_cleanup).start()
  bot.run()
