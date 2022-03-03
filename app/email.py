from flask_mail import Message
from app import app, mail
import traceback
from threading import Thread
from flask_apscheduler import APScheduler

# from app.sources.cia_general import cia_general
# from app.sources.iana_root_servers import iana_root_servers
# from app.sources.iana_tld import iana_tld
# from app.sources.itu_baskets import itu_baskets
# from app.sources.itu_indicators import itu_indicators
# from app.sources.ookla_speed_index import ookla_speed_index
# from app.sources.pch_ixp import pch_ixp
# from app.sources.peeringdb_ixp import peeringdb_ixp
# from app.sources.telegeography_submarine import telegeography_submarine
# from app.sources.worldpop_density import worldpop_density


# from app.modules.maps import create_map
# from app.modules.graph_infr import graph_infr
# from app.modules.graph_adop import graph_adop
# from app.modules.graph_use import graph_use
# from app.modules.landing_image import create_land_image
# from app.modules.submarine_image import create_sub_image
# from app.modules.ixp_image import create_ixp_image
# from app.modules.root_image import create_root_image
# from app.modules.density_image import create_density_image
# from app.modules.facility_image import create_fac_image



def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# scheduler = APScheduler()
# def scheduleTask():
#     iana_tld()
#     cia_general()
#     # print('run run run')

# scheduler.add_job(
#     id = 'Scheduled Task', 
#     func = Thread(target=scheduleTask()).start(), 
#     trigger='cron', 
#     # day = 2,
#     hour = 10, # + 4
#     minute = 40,
#     second = 0,
#     timezone = 'UTC',
#     )
# scheduler.start()



def send_email(subject, body, sender, recipients):
    msg = Message(
        subject, 
        body=body, 
        sender=sender, 
        recipients=recipients)
    # mail.send(msg)
    Thread(target=send_async_email, args=(app, msg)).start()

def email_exception(e, source, subject):
    traceback_msg = traceback.format_exc()
    error = "Source: " + source + "\n\nError: " + str(e) + "\n\nTraceback: " + traceback_msg
    send_email(subject, error, app.config['SENDER'], app.config['ADMINS'])