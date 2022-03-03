from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_compress import Compress
import logging
from logging.handlers import SMTPHandler
from threading import Thread
from flask_apscheduler import APScheduler


app = Flask(__name__)
Compress(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from flask_mail import Mail
mail = Mail(app) 


from app.sources.cia_general import cia_general
from app.sources.iana_root_servers import iana_root_servers
from app.sources.iana_tld import iana_tld
from app.sources.itu_baskets import itu_baskets
from app.sources.itu_indicators import itu_indicators
from app.sources.ookla_speed_index import ookla_speed_index
from app.sources.pch_ixp import pch_ixp
from app.sources.peeringdb_ixp import peeringdb_ixp
from app.sources.telegeography_submarine import telegeography_submarine
from app.sources.worldpop_density import worldpop_density

from app.modules.maps import create_map
from app.modules.graph_infr import graph_infr
from app.modules.graph_adop import graph_adop
from app.modules.graph_use import graph_use
from app.modules.landing_image import create_land_image
from app.modules.submarine_image import create_sub_image
from app.modules.ixp_image import create_ixp_image
from app.modules.root_image import create_root_image
from app.modules.density_image import create_density_image
from app.modules.facility_image import create_fac_image

scheduler = APScheduler()
def scheduleTask():
    print('Started')
    # print(cia_general())
    # print(iana_root_servers())
    # print(iana_tld())
    print(itu_baskets())
    # print(itu_indicators())
    # print(ookla_speed_index())
    # print(pch_ixp())
    # print(peeringdb_ixp())
    # print(telegeography_submarine())
    # print(worldpop_density())
    
    create_map()
    graph_infr()
    graph_adop()
    graph_use()
    create_land_image()
    create_sub_image()
    create_ixp_image()
    create_root_image()
    create_density_image()
    create_fac_image()

    print('Finished')




# from app.email import scheduler
# scheduler.start()

# import traceback
# @app.errorhandler(Exception)
# def handle_error(e):
#     response = dict()
#     error_message = traceback.format_exc()
#     response['errorMessage'] = error_message
#     return None


if not app.debug:
# if app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            # fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            fromaddr=app.config['SENDER'],
            toaddrs=app.config['ADMINS'], subject='Warnings',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)



scheduler.add_job(
    id = 'Scheduled Task1', 
    # func = Thread(target=scheduleTask()).start, 
    func=scheduleTask,
    trigger='cron', 
    # day = 2,
    hour = 8, # + 4
    minute = 58,
    second = 0,
    timezone = 'UTC',
    )
scheduler.start()



from app import routes, models