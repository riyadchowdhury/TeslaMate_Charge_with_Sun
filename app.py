import db_init
import db_functions
import solar_surplus_to_tesla
import globals
import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, redirect, url_for, request

globals.init()
db_init.initialize_db()
LOGLEVEL = os.environ.get('LOGGING_LEVEL', 'WARNING').upper()
logging.basicConfig(level=LOGLEVEL)
logging.getLogger('root').setLevel(logging.INFO)
logger = logging.getLogger(__name__)

config = db_functions.get_config_from_db()

envoy_data = db_functions.write_envoy_data_to_db()
solar_surplus_to_tesla.mainfunction(envoy_data)

sched = BackgroundScheduler(daemon=True)
sched.add_job(db_functions.write_envoy_data_to_db, 'interval', seconds=60)
sched.add_job(solar_surplus_to_tesla.mainfunction, 'interval', seconds=300)
sched.start()

app = Flask(__name__)


@app.route("/home")
def home():
    out = db_functions.read_envoy_data_from_db()
    return out  # TODO print stats on webpage


@app.route('/')
def root():
    if config['charge_mode'] == 'solar':
        solar_selected = ' selected'
        grid_selected = ''
    else:
        solar_selected = ''
        grid_selected = ' selected'
    return render_template('index.html', solar_selected=solar_selected, grid_selected=grid_selected)


@app.route('/settings')
def settings():
    return render_template('settings.html')


@app.route('/selectchargemode', methods=['POST'])
def handle_data():
    config['charge_mode'] = request.form['charge']
    db_functions.save_config_to_db(config)
    logger.info(f"Charge mode is now {request.form['charge']}")
    return redirect(url_for('root'))


if __name__ == "__main__":
    app.run(use_reloader=False)
