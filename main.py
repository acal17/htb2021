import threading
from display import Display
import os
from dotenv import load_dotenv

from twitch import TwitchBot
from db import DatabaseInterface

def main():
  load_dotenv()

  connection_data = ("localhost", 3307, "root", "")
  db = DatabaseInterface(connection_data, "test", "GBP")
  twitch_data = list(map(lambda x : os.environ[x], ["TMI_TOKEN", "CLIENT_ID", "BOT_NICK", "BOT_PREFIX", "CHANNEL"]))
  twitch_data[4] = [twitch_data[4]]
  twitch_data = tuple(twitch_data)

  tb = TwitchBot(twitch_data, db)
  tb.display = Display()
  x = threading.Thread(target=tb.display.run)
  x.start()
  tb.run()

if __name__ == "__main__":
  main()