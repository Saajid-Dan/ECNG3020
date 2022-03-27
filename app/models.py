from app import db

# ---------------------------- General-Country Information  ---------------------------- #

# CIA World Factbook data source - general country information
class Cia_general(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, index=True)
    general = db.Column(db.String, index=True)
    currency = db.Column(db.String, index=True)
    area = db.Column(db.String, index=True)
    land_use = db.Column(db.String, index=True)
    language = db.Column(db.String, index=True)
    tot_pop = db.Column(db.String, index=True)
    urbanize = db.Column(db.String, index=True)
    elec_acc = db.Column(db.String, index=True)
    lab_frc = db.Column(db.String, index=True)
    lab_occ = db.Column(db.String, index=True)
    unem_rt = db.Column(db.String, index=True)
    poverty = db.Column(db.String, index=True)
    literacy = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# WorldPop.org data source - population density
class Wpop_density(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, index=True)
    url_tif = db.Column(db.String, index=True)
    avg_dens = db.Column(db.String, index=True)
    max_dens = db.Column(db.String, index=True)
    min_dens = db.Column(db.String, index=True)
    max_lat = db.Column(db.Float, index=True)
    max_lon = db.Column(db.Float, index=True)
    min_lat = db.Column(db.Float, index=True)
    min_lon = db.Column(db.Float, index=True)
    date = db.Column(db.Integer, index=True)
    source = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# -------------------------------- Internet Adoption ------------------------------- #

# ITU Price baskets - GNI
class Itu_basket_gni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, index=True)
    date = db.Column(db.Integer, index=True)
    fix = db.Column(db.Float, index=True)
    mob = db.Column(db.Float, index=True)
    low = db.Column(db.Float, index=True)
    high = db.Column(db.Float, index=True)
    source = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# ITU Price baskets - PPP
class Itu_basket_ppp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, index=True)
    date = db.Column(db.Integer, index=True)
    fix = db.Column(db.Float, index=True)
    mob = db.Column(db.Float, index=True)
    low = db.Column(db.Float, index=True)
    high = db.Column(db.Float, index=True)
    source = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# ITU Price baskets - USD
class Itu_basket_usd(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, index=True)
    date = db.Column(db.Integer, index=True)
    fix = db.Column(db.Float, index=True)
    mob = db.Column(db.Float, index=True)
    low = db.Column(db.Float, index=True)
    high = db.Column(db.Float, index=True)
    source = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# ------------------------------ ICT-Use ------------------------------ #

# ITU's ICT Indicators
class Itu_indicator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, index=True)
    date = db.Column(db.Integer, index=True)
    fix = db.Column(db.Float, index=True)
    mob = db.Column(db.Float, index=True)
    per = db.Column(db.Float, index=True)
    bw = db.Column(db.Float, index=True)
    source = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# ------------------------- Internet Infrastructure ------------------------ #

# Packet Clearing House data source - IXP
class Pch_ixp_dir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_ref = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    city = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    url_home = db.Column(db.String, index=True)
    status = db.Column(db.String, index=True)
    date = db.Column(db.String, index=True)
    num_prfs = db.Column(db.String, index=True)
    lat = db.Column(db.String, index=True)
    lon = db.Column(db.String, index=True)
    num_prts = db.Column(db.String, index=True)
    ipv4_avg = db.Column(db.String, index=True)
    ipv4_pk = db.Column(db.String, index=True)
    ipv6_avg = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)
    
# Packet Clearing House data source - IXP subnet details
class Pch_ixp_sub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_ref = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    status = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    name_long = db.Column(db.String, index=True)
    version = db.Column(db.String, index=True)
    num_sub = db.Column(db.String, index=True)
    mlpa = db.Column(db.String, index=True)
    avg_traf = db.Column(db.String, index=True)
    num_prts = db.Column(db.String, index=True)
    url_traf = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# Packet Clearing House data source - IXP subnet members
class Pch_ixp_mem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, index=True)
    ip_adr = db.Column(db.String, index=True)
    fqdn = db.Column(db.String, index=True)
    ping = db.Column(db.String, index=True)
    asn = db.Column(db.String, index=True)
    org_name = db.Column(db.String, index=True)
    peer_pol = db.Column(db.String, index=True)
    num_prfs = db.Column(db.String, index=True)
    version = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# PeeringDB data source - IXP
class Pdb_ixp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ix_id = db.Column(db.String, index=True)
    fac_id = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    org_name = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    name_long = db.Column(db.String, index=True)
    city = db.Column(db.String, index=True)
    media = db.Column(db.String, index=True)
    prot_unicast = db.Column(db.String, index=True)
    prot_multicast = db.Column(db.String, index=True)
    prot_ipv6 = db.Column(db.String, index=True)
    url_home = db.Column(db.String, index=True)
    url_stats = db.Column(db.String, index=True)
    tech_email = db.Column(db.String, index=True)
    tech_phone = db.Column(db.String, index=True)
    policy_email = db.Column(db.String, index=True)
    policy_phone = db.Column(db.String, index=True)
    sale_phone = db.Column(db.String, index=True)
    sale_email = db.Column(db.String, index=True)
    svc_lvl = db.Column(db.String, index=True)
    terms = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    status = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# PeeringDB data source - Network facilities
class Pdb_facility(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fac_id = db.Column(db.String, index=True)
    net_id = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    org_name = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    name_long = db.Column(db.String, index=True)
    url_home = db.Column(db.String, index=True)
    sale_email = db.Column(db.String, index=True)
    sale_phone = db.Column(db.String, index=True)
    tech_email = db.Column(db.String, index=True)
    tech_phone = db.Column(db.String, index=True)
    status = db.Column(db.String, index=True)
    address1 = db.Column(db.String, index=True)
    address2 = db.Column(db.String, index=True)
    city = db.Column(db.String, index=True)
    state = db.Column(db.String, index=True)
    zipcode = db.Column(db.String, index=True)
    lat = db.Column(db.String, index=True)
    lon = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# PeeringDB data source - Networks
class Pdb_network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    net_id = db.Column(db.String, index=True)
    org_name = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    name_long = db.Column(db.String, index=True)
    url_home = db.Column(db.String, index=True)
    asn = db.Column(db.String, index=True)
    look_glass = db.Column(db.String, index=True)
    route_srv = db.Column(db.String, index=True)
    irr_as_set = db.Column(db.String, index=True)
    info_type = db.Column(db.String, index=True)
    ipv4_prfs = db.Column(db.String, index=True)
    ipv6_prfs = db.Column(db.String, index=True)
    traf_lvl = db.Column(db.String, index=True)
    traf_ratio = db.Column(db.String, index=True)
    geo_scope = db.Column(db.String, index=True)
    prot_unicast = db.Column(db.String, index=True)
    prot_multicast = db.Column(db.String, index=True)
    prot_ipv6 = db.Column(db.String, index=True)
    prot_nvr_by_rt_srv = db.Column(db.String, index=True)
    policy_url = db.Column(db.String, index=True)
    policy_general = db.Column(db.String, index=True)
    policy_locations = db.Column(db.String, index=True)
    policy_contracts = db.Column(db.String, index=True)
    status = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# IANA root name servers
class Iana_root_server(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    url_home = db.Column(db.String, index=True)
    location = db.Column(db.String, index=True)
    srv_operator = db.Column(db.String, index=True)
    srv_type = db.Column(db.String, index=True)
    asn = db.Column(db.String, index=True)
    ipv4 = db.Column(db.String, index=True)
    ipv6 = db.Column(db.String, index=True)
    num_inst = db.Column(db.String, index=True)
    rssac = db.Column(db.String, index=True)
    srv_contact = db.Column(db.String, index=True)
    peer_pol = db.Column(db.String, index=True)
    id_root = db.Column(db.String, index=True)
    id_nc = db.Column(db.String, index=True)
    lat = db.Column(db.Float, index=True)
    lon = db.Column(db.Float, index=True)
    updated = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# IANA top level domains
class Iana_tld(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String, index=True)
    country_code = db.Column(db.String, index=True)
    tld_type = db.Column(db.String, index=True)
    cctld = db.Column(db.String, index=True)
    admin_contact = db.Column(db.String, index=True)
    tech_contact = db.Column(db.String, index=True)
    name_srv = db.Column(db.String, index=True)
    info_registry = db.Column(db.String, index=True)
    date = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# OOKLA global speed index - mobile broadband 
class Ookla_mobile_bband(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    dl_spd = db.Column(db.Float, index=True)
    up_spd = db.Column(db.Float, index=True)
    ltcy = db.Column(db.Float, index=True)
    jitt = db.Column(db.Float, index=True)
    stamp = db.Column(db.String, index=True)

# OOKLA global speed index - fixed broadband
class Ookla_fixed_bband(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    dl_spd = db.Column(db.Float, index=True)
    up_spd = db.Column(db.Float, index=True)
    ltcy = db.Column(db.Float, index=True)
    jitt = db.Column(db.Float, index=True)
    stamp = db.Column(db.String, index=True)

# Telegeography submarine cable map - landing points
class Telegeography_landing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_ref = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    lat = db.Column(db.Float, index=True)
    lon = db.Column(db.Float, index=True)
    in_caribbean = db.Column(db.String, index=True)
    cables = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

# Telegeography submarine cable map - submarine cables
class Telegeography_submarine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, index=True)
    status = db.Column(db.String, index=True)
    land_pts = db.Column(db.String, index=True)
    length = db.Column(db.String, index=True)
    rfs = db.Column(db.String, index=True)
    suppliers = db.Column(db.String, index=True)
    owners = db.Column(db.String, index=True)
    url_home = db.Column(db.String, index=True)
    geometry = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    source = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)