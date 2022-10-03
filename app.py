import local_envoy_reader
import db_functions
import solar_surplus_to_tesla
import tesla_api
import asyncio
import json
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask

# solar_surplus_to_tesla.mainfunction()
#
# sched = BackgroundScheduler(daemon=True)
# sched.add_job(solar_surplus_to_tesla.mainfunction,'interval',seconds=60)
# sched.start()

envoy_data = db_functions.write_envoy_data_to_db()
solar_surplus_to_tesla.mainfunction(envoy_data)

sched = BackgroundScheduler(daemon=True)
sched.add_job(db_functions.write_envoy_data_to_db,'interval',seconds=60)
sched.add_job(solar_surplus_to_tesla.mainfunction,'interval',seconds=300)

sched.start()

app = Flask(__name__)

@app.route("/home")
def home():
    """ Function for test purposes. """
    out = db_functions.read_envoy_data_from_db()
    return out # TODO print stats on webpage

if __name__ == "__main__":
    app.run(use_reloader=False)
