import db_init
import db_functions

if __name__ == "__main__":
    print('testing db')
    out = db_functions.get_config_from_db()
    # db_init.initialize_db()
    print(out)
    out['charge_mode'] = 'grid'
    out['voltage'] = 120
    db_functions.save_config_to_db(out)
