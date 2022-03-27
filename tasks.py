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

cia_general()
iana_root_servers()
iana_tld()
itu_baskets()
itu_indicators()
ookla_speed_index()
pch_ixp()
peeringdb_ixp()
telegeography_submarine()
worldpop_density()
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