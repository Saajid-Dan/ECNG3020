from app import db

# ---------------------------- General-Population ---------------------------- #

class Gen_pop(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ctry_ = db.Column(db.String, index=True)
    gen = db.Column(db.String, index=True)
    cur = db.Column(db.String, index=True)
    area = db.Column(db.String, index=True)
    land = db.Column(db.String, index=True)
    lang = db.Column(db.String, index=True)
    pop = db.Column(db.String, index=True)
    urb = db.Column(db.String, index=True)
    elec = db.Column(db.String, index=True)
    lab = db.Column(db.String, index=True)
    occ = db.Column(db.String, index=True)
    unem = db.Column(db.String, index=True)
    pov = db.Column(db.String, index=True)
    lit = db.Column(db.String, index=True)
    updt = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# -------------------------------- ICT-Baskets ------------------------------- #

class GNI(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ctry = db.Column(db.String, index=True)
    year = db.Column(db.Integer, index=True)
    uni = db.Column(db.String, index=True)
    fix = db.Column(db.Float, index=True)
    mob = db.Column(db.Float, index=True)
    low = db.Column(db.Float, index=True)
    high = db.Column(db.Float, index=True)
    updt = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

class PPP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ctry = db.Column(db.String, index=True)
    year = db.Column(db.Integer, index=True)
    uni = db.Column(db.String, index=True)
    fix = db.Column(db.Float, index=True)
    mob = db.Column(db.Float, index=True)
    low = db.Column(db.Float, index=True)
    high = db.Column(db.Float, index=True)
    updt = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

class USD(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ctry = db.Column(db.String, index=True)
    year = db.Column(db.Integer, index=True)
    uni = db.Column(db.String, index=True)
    fix = db.Column(db.Float, index=True)
    mob = db.Column(db.Float, index=True)
    low = db.Column(db.Float, index=True)
    high = db.Column(db.Float, index=True)
    updt = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# ------------------------------ ICT-Indicators ------------------------------ #

class indicators(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, index=True)
    ctry = db.Column(db.String, index=True)
    fix = db.Column(db.Float, index=True)
    mob = db.Column(db.Float, index=True)
    per = db.Column(db.Float, index=True)
    bw = db.Column(db.Float, index=True)
    updt = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# ------------------------- Internet Exchange Points: ------------------------ #

# Packet Clearing House
class Ixp_dir(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uni = db.Column(db.String, index=True)
    ctry = db.Column(db.String, index=True)
    city = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    url = db.Column(db.String, index=True)
    stat = db.Column(db.String, index=True)
    date = db.Column(db.String, index=True)
    prfs = db.Column(db.String, index=True)
    lat = db.Column(db.String, index=True)
    lon = db.Column(db.String, index=True)
    prts = db.Column(db.String, index=True)
    ipv4_avg = db.Column(db.String, index=True)
    ipv4_pk = db.Column(db.String, index=True)
    ipv6_avg = db.Column(db.String, index=True)
    updt = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)
    
class Ixp_sub(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uni = db.Column(db.String, index=True)
    ctry = db.Column(db.String, index=True)
    stat = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    name_lng = db.Column(db.String, index=True)
    ver = db.Column(db.String, index=True)
    sub = db.Column(db.String, index=True)
    mlpa = db.Column(db.String, index=True)
    traf = db.Column(db.String, index=True)
    prts = db.Column(db.String, index=True)
    est = db.Column(db.String, index=True)
    url_traf = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

class Ixp_mem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uni = db.Column(db.String, index=True)
    ctry = db.Column(db.String, index=True)
    ip = db.Column(db.String, index=True)
    fqdn = db.Column(db.String, index=True)
    ping = db.Column(db.String, index=True)
    asn = db.Column(db.String, index=True)
    org = db.Column(db.String, index=True)
    peer = db.Column(db.String, index=True)
    prfs = db.Column(db.String, index=True)
    ipv4 = db.Column(db.String, index=True)
    ipv6 = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# PeeringDB
class Peer_ix(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ix_id = db.Column(db.String, index=True)
    fac_id = db.Column(db.String, index=True)
    org_name = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    name_long = db.Column(db.String, index=True)
    city = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    media = db.Column(db.String, index=True)
    proto_unicast = db.Column(db.String, index=True)
    proto_multicast = db.Column(db.String, index=True)
    proto_ipv6 = db.Column(db.String, index=True)
    website = db.Column(db.String, index=True)
    url_stats = db.Column(db.String, index=True)
    tech_email = db.Column(db.String, index=True)
    tech_phone = db.Column(db.String, index=True)
    policy_email = db.Column(db.String, index=True)
    policy_phone = db.Column(db.String, index=True)
    sales_phone = db.Column(db.String, index=True)
    sales_email = db.Column(db.String, index=True)
    service_level = db.Column(db.String, index=True)
    terms = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    status = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

class Peer_fac(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fac_id = db.Column(db.String, index=True)
    net_id = db.Column(db.String, index=True)
    org_name = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    name_long = db.Column(db.String, index=True)
    website = db.Column(db.String, index=True)
    sales_email = db.Column(db.String, index=True)
    sales_phone = db.Column(db.String, index=True)
    tech_email = db.Column(db.String, index=True)
    tech_phone = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    status = db.Column(db.String, index=True)
    address1 = db.Column(db.String, index=True)
    address2 = db.Column(db.String, index=True)
    city = db.Column(db.String, index=True)
    country = db.Column(db.String, index=True)
    state = db.Column(db.String, index=True)
    zipcode = db.Column(db.String, index=True)
    latitude = db.Column(db.String, index=True)
    longitude = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)

class Peer_net(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    net_id = db.Column(db.String, index=True)
    org_name = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    name_long = db.Column(db.String, index=True)
    website = db.Column(db.String, index=True)
    asn = db.Column(db.String, index=True)
    looking_glass = db.Column(db.String, index=True)
    route_server = db.Column(db.String, index=True)
    irr_as_set = db.Column(db.String, index=True)
    info_type = db.Column(db.String, index=True)
    info_prefixes4 = db.Column(db.String, index=True)
    info_prefixes6 = db.Column(db.String, index=True)
    info_traffic = db.Column(db.String, index=True)
    info_ratio = db.Column(db.String, index=True)
    info_scope = db.Column(db.String, index=True)
    info_unicast = db.Column(db.String, index=True)
    info_multicast = db.Column(db.String, index=True)
    info_ipv6 = db.Column(db.String, index=True)
    info_never_via_route_servers = db.Column(db.String, index=True)
    policy_url = db.Column(db.String, index=True)
    policy_general = db.Column(db.String, index=True)
    policy_locations = db.Column(db.String, index=True)
    policy_contracts = db.Column(db.String, index=True)
    updated = db.Column(db.String, index=True)
    status = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# ---------------------------- Population-Density ---------------------------- #

class Pop_dens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    updt = db.Column(db.String, index=True)
    ctry = db.Column(db.String, index=True)
    url = db.Column(db.String, index=True)
    dens = db.Column(db.String, index=True)
    max_ = db.Column(db.String, index=True)
    min_ = db.Column(db.String, index=True)
    pop_yr = db.Column(db.Integer, index=True)
    stamp = db.Column(db.String, index=True)


# ------------------------------- Root-Servers ------------------------------- #

class Root_srv(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uni = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    url = db.Column(db.String, index=True)
    ctry = db.Column(db.String, index=True)
    loc = db.Column(db.String, index=True)
    oper = db.Column(db.String, index=True)
    type_ = db.Column(db.String, index=True)
    asn = db.Column(db.String, index=True)
    ipv4 = db.Column(db.String, index=True)
    ipv6 = db.Column(db.String, index=True)
    inst = db.Column(db.String, index=True)
    rssac = db.Column(db.String, index=True)
    con = db.Column(db.String, index=True)
    peer = db.Column(db.String, index=True)
    id_root = db.Column(db.String, index=True)
    id_nc = db.Column(db.String, index=True)
    lat = db.Column(db.Float, index=True)
    lon = db.Column(db.Float, index=True)
    updt = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# -------------------------------- Speed-Index ------------------------------- #

class Mob_br(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uni = db.Column(db.String, index=True)
    date = db.Column(db.String, index=True)
    ctry = db.Column(db.String, index=True)
    dls = db.Column(db.Float, index=True)
    ups = db.Column(db.Float, index=True)
    ltcy = db.Column(db.Float, index=True)
    jitt = db.Column(db.Float, index=True)
    stamp = db.Column(db.String, index=True)

class Fixed_br(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uni = db.Column(db.String, index=True)
    date = db.Column(db.String, index=True)
    ctry = db.Column(db.String, index=True)
    dls = db.Column(db.Float, index=True)
    ups = db.Column(db.Float, index=True)
    ltcy = db.Column(db.Float, index=True)
    jitt = db.Column(db.Float, index=True)
    stamp = db.Column(db.String, index=True)


# ----------------------------- Submarine-Cables ----------------------------- #

class Land(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uni = db.Column(db.String, index=True)
    name = db.Column(db.String, index=True)
    lat = db.Column(db.Float, index=True)
    lon = db.Column(db.Float, index=True)
    ctry = db.Column(db.String, index=True)
    car = db.Column(db.String, index=True)
    cab = db.Column(db.String, index=True)
    updt = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)


# ----------------------------- Top-Level-Domains ---------------------------- #

class Tld(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ctry_ = db.Column(db.String, index=True)
    cc = db.Column(db.String, index=True)
    type_ = db.Column(db.String, index=True)
    cctld = db.Column(db.String, index=True)
    ad_con = db.Column(db.String, index=True)
    tch_con = db.Column(db.String, index=True)
    nm_svr = db.Column(db.String, index=True)
    reg = db.Column(db.String, index=True)
    dates = db.Column(db.String, index=True)
    stamp = db.Column(db.String, index=True)
