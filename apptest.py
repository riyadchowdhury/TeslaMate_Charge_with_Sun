# import db_init
# import db_functions
# import enphase_api
# import os
# import datetime

# if __name__ == "__main__":
#     # print('testing db')
#     # out = db_functions.get_config_from_db()
#     db_init.initialize_db()
#     # print(out)
#     # out['charge_mode'] = 'grid'
#     # out['voltage'] = 120
#     # db_functions.save_config_to_db(out)
#     # enphase = enphase_api.Enhase()
#     # envoy_data = enphase.get_envoy_data()
#     # print(envoy_data)
#     print('writing to db')
#     # db_functions.write_envoy_data_to_db()
#     print('reafind from to db')
#     out = db_functions.read_envoy_data_from_db()
#     # fiveminsago = datetime.datetime.utcnow() - datetime.timedelta(minutes=5)
#     print(out)
