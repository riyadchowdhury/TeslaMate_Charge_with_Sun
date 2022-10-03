import local_envoy_reader
import solar_surplus_to_tesla
import tesla_api
import asyncio
import json
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

solar_surplus_to_tesla.mainfunction()

sched = BackgroundScheduler(daemon=True)
sched.add_job(solar_surplus_to_tesla.mainfunction,'interval',seconds=60)
sched.start()

app = Flask(__name__)

@app.route("/home")
def home():
    """ Function for test purposes. """
    return "Hello World" # TODO print stats on webpage

if __name__ == "__main__":
    app.run(use_reloader=False)
