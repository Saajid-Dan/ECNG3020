from flask import render_template, flash, redirect, url_for
from app import app, mail, db
from flask_mail import Message
from app.forms import Feedback

import geopandas as gpd
import ast

from app.models import Tld
from app.models import Land
from app.models import Ixp_dir, Ixp_sub, Ixp_mem
from app.models import Root_srv
from app.models import Gen_pop, Pop_dens
from app.models import Fixed_br, Mob_br
from app.models import GNI, PPP, USD
from app.models import ICT_fix, ICT_mob, ICT_per, ICT_bw

from app.sources.General_Population import population
from app.sources.ICT_Baskets import baskets
from app.sources.ICT_Indicators import indicators
from app.sources.Internet_Exchange_Points import ixp
from app.sources.Population_Density import density
from app.sources.Root_Servers import root
from app.sources.Speed_Index import speedindex
from app.sources.Submarine_Cables import submarine
from app.sources.Top_Level_Domains import tld

from app.modules.maps import create_map
from app.modules.speed_index_graph import create_speed_graph
from app.modules.baskets_graph import create_baskets_graph
from app.modules.indicators_graph import create_indic_graph
from app.modules.landing_image import create_land_image
from app.modules.submarine_image import create_sub_image
from app.modules.ixp_image import create_ixp_image
from app.modules.root_image import create_root_image
from app.modules.density_image import create_density_image


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = Feedback()
    if form.validate_on_submit():
        flash('Feedback Sent Successfully.')
            
        title = form.option.data
        body = form.comment.data

        msg = Message(title, body=body, sender='SDan.Testing@gmail.com', recipients=['SDan.Testing@gmail.com'])
        mail.send(msg)

        return redirect(url_for('index') + "#anchor")
        
    return render_template('index.html', title='Home', form=form)

# url_for('index') - #3
@app.route('/tld/<country>')
def tld_page(country):
    tld_ctry = Tld.query.filter_by(ctry_=country).first_or_404()
    return render_template('tld_page.html', title=country, tld=tld_ctry)

@app.route('/landing/<country>')
def land_page(country):
    land_uni = Land.query.order_by(Land.lon).filter_by(ctry=country).all()
    # x = ast.literal_eval(x[0])
    lst_cab = []
    for j in land_uni:
        x = ast.literal_eval(j.cab)
        lst_cab.append(x)
    return render_template('land_page.html', title=country, land=land_uni, cables=lst_cab)

@app.route('/landing')
def land_list():
    ctry_lst = []
    ctry = Land.query.order_by(Land.ctry).filter_by(car='Yes').with_entities(Land.ctry)
    for j in ctry:
        ctry_lst.append(j[0])

    ctry_lst_uni = []
    for items in ctry_lst:
        if items not in ctry_lst_uni:
            ctry_lst_uni.append(items)
    # print(ctry_lst_uni)
    # land_all = Land.query.all()
    # print(sub_all[1].ctry)
    return render_template('land_list.html', title= 'Landing Point Listing', land_all=ctry_lst_uni)

@app.route('/submarine/<cable>')
def sub_page(cable):
    file_sub = open('./app/static/json/submarine.json', 'r')
    gdf_sub = gpd.read_file(file_sub)
    sub = gdf_sub.loc[gdf_sub['name']==cable]

    x = sub.iloc[0]['lnd']
    land = ast.literal_eval(x)
    
    car_lst = []
    int_lst = []
    for j in land:
        # Return None if item does not exist in database.
        car_ = Land.query.filter_by(uni=j['id'], car='Yes').first()
        pos = db.session.query(Land.lon, Land.name).filter_by(uni=j['id']).first()
        
        if car_ == None:
            int_lst.append(pos)
        else:
            car_lst.append(pos)

    int_lst.sort(key = lambda x: x[0])
    int_lst = dict(int_lst).values()

    car_lst.sort(key = lambda x: x[0])
    car_lst = dict(car_lst).values()

    return render_template('sub_page.html', title=cable, sub=sub, land_car=car_lst, land_int=int_lst)

@app.route('/submarine')
def sub_list():
    cable_lst = []
    file_sub = open('./app/static/json/submarine.json', 'r')
    gdf_sub = gpd.read_file(file_sub)
    for j in range(len(gdf_sub)):
        cable_lst.append(gdf_sub.iloc[j]['name'])
    return render_template('sub_list.html', title= 'Submarine Cable Listing', sub_all=cable_lst)

@app.route('/ixp/<country>')
def ixp_page(country):
    ixp_dir = Ixp_dir.query.filter_by(ctry=country).all()
    ixp_sub = Ixp_sub.query.filter_by(ctry=country).all()
    ixp_mem = Ixp_mem.query.filter_by(ctry=country).all()
    return render_template('ixp_page.html', title=country, ixp_dir=ixp_dir, ixp_sub=ixp_sub, ixp_mem=ixp_mem)

@app.route('/ixp')
def ixp_list():
    ctry_lst = []
    ctry = Ixp_dir.query.order_by(Ixp_dir.ctry).with_entities(Ixp_dir.ctry)
    for j in ctry:
        ctry_lst.append(j[0])
    ctry_lst = list(dict.fromkeys(ctry_lst))
    return render_template('ixp_list.html', title= 'IXP Listing', ixp_all=ctry_lst)

@app.route('/tld')
def tld_list():
    ctry_lst = []
    ctry = Tld.query.order_by(Tld.ctry_).with_entities(Tld.ctry_)
    for j in ctry:
        ctry_lst.append(j[0])
    # ctry_lst = list(dict.fromkeys(ctry_lst))
    return render_template('tld_list.html', title= 'TLD Listing', tld_all = ctry_lst)

@app.route('/root/<country>')
def root_page(country):
    root = Root_srv.query.filter_by(ctry=country).all()
    return render_template('root_page.html', title=country, root=root)

@app.route('/root')
def root_list():
    ctry_lst = []
    ctry = Root_srv.query.order_by(Root_srv.ctry).with_entities(Root_srv.ctry)
    for j in ctry:
        ctry_lst.append(j[0])
    ctry_lst = list(dict.fromkeys(ctry_lst))
    return render_template('root_list.html', title= 'Root Server Listing', root_all = ctry_lst)

@app.route('/gen/<country>')
def gen_page(country):
    gen = Gen_pop.query.filter_by(ctry_=country).first()
    dens = Pop_dens.query.filter_by(ctry=country).first()
    return render_template('gen_page.html', title=country, gen=gen, dens=dens)

@app.route('/gen')
def gen_list():
    ctry_lst = []
    ctry = Gen_pop.query.order_by(Gen_pop.ctry_).with_entities(Gen_pop.ctry_)
    for j in ctry:
        ctry_lst.append(j[0])
    # ctry_lst = list(dict.fromkeys(ctry_lst))
    return render_template('gen_list.html', title= 'General Population Information Listing', gen_all = ctry_lst)

@app.route('/speed/<country>')
def speed_page(country):
    fix = Fixed_br.query.filter_by(ctry=country).all()
    mob = Mob_br.query.filter_by(ctry=country).all()
    return render_template('speed_page.html', title=country, fix=fix, mob=mob)

@app.route('/speed')
def speed_list():
    ctry_lst = []
    ctry = Fixed_br.query.order_by(Fixed_br.ctry).with_entities(Fixed_br.ctry)
    for j in ctry:
        ctry_lst.append(j[0])
    ctry_lst = list(dict.fromkeys(ctry_lst))
    return render_template('speed_list.html', title= 'Speed Index Listing', speed_all = ctry_lst)

@app.route('/basket/<country>')
def basket_page(country):
    gni = GNI.query.filter_by(ctry=country).all()
    ppp = PPP.query.filter_by(ctry=country).all()
    usd = USD.query.filter_by(ctry=country).all()
    return render_template('basket_page.html', title=country, gni=gni, ppp=ppp, usd=usd)

@app.route('/basket')
def basket_list():
    ctry_lst = []
    ctry = GNI.query.order_by(GNI.ctry).with_entities(GNI.ctry)
    for j in ctry:
        ctry_lst.append(j[0])
    ctry_lst = list(dict.fromkeys(ctry_lst))
    return render_template('basket_list.html', title= 'ICT Price Basket Listing', bask_all = ctry_lst)

@app.route('/indicator/<country>')
def indicator_page(country):

    dict_ctry = {
        'Anguilla':[ ICT_fix.ai, ICT_mob.ai, ICT_per.ai, ICT_bw.ai ],
        'Antigua and Barbuda':[ ICT_fix.ag, ICT_mob.ag, ICT_per.ag, ICT_bw.ag ],
        'Bahamas':[ ICT_fix.bs, ICT_mob.bs, ICT_per.bs, ICT_bw.bs ],
        'Barbados':[ ICT_fix.bb, ICT_mob.bb, ICT_per.bb, ICT_bw.bb ],
        'Belize':[ ICT_fix.bz, ICT_mob.bz, ICT_per.bz, ICT_bw.bz ],
        'Bermuda':[ ICT_fix.bm, ICT_mob.bm, ICT_per.bm, ICT_bw.bm ],
        'Virgin Islands U K ':[ ICT_fix.vg, ICT_mob.vg, ICT_per.vg, ICT_bw.vg ],
        'Cayman Islands':[ ICT_fix.ky, ICT_mob.ky, ICT_per.ky, ICT_bw.ky ],
        'Dominica':[ ICT_fix.dm, ICT_mob.dm, ICT_per.dm, ICT_bw.dm ],
        'Grenada':[ ICT_fix.gd, ICT_mob.gd, ICT_per.gd, ICT_bw.gd ],
        'Guyana':[ ICT_fix.gy, ICT_mob.gy, ICT_per.gy, ICT_bw.gy ],
        'Haiti':[ ICT_fix.ht, ICT_mob.ht, ICT_per.ht, ICT_bw.ht ],
        'Jamaica':[ ICT_fix.jm, ICT_mob.jm, ICT_per.jm, ICT_bw.jm ],
        'Montserrat':[ ICT_fix.ms, ICT_mob.ms, ICT_per.ms, ICT_bw.ms ],
        'Saint Kitts and Nevis':[ ICT_fix.kn, ICT_mob.kn, ICT_per.kn, ICT_bw.kn ],
        'Saint Lucia':[ ICT_fix.lc, ICT_mob.lc, ICT_per.lc, ICT_bw.lc ],
        'Saint Vincent and The Grenadines':[ ICT_fix.vc, ICT_mob.vc, ICT_per.vc, ICT_bw.vc ],
        'Suriname':[ ICT_fix.sr, ICT_mob.sr, ICT_per.sr, ICT_bw.sr ],
        'Trinidad and Tobago':[ ICT_fix.tt, ICT_mob.tt, ICT_per.tt, ICT_bw.tt ],
        'Turks and Caicos Islands':[ ICT_fix.tc, ICT_mob.tc, ICT_per.tc, ICT_bw.tc ]
    }
    
    cat = dict_ctry[country]
    
    fix_yr =  ICT_fix.query.order_by(ICT_fix.yrs).all()
    mob_yr =  ICT_mob.query.order_by(ICT_mob.yrs).all()
    per_yr =  ICT_per.query.order_by(ICT_per.yrs).all()
    bw_yr =  ICT_bw.query.order_by(ICT_bw.yrs).all()

    fix = ICT_fix.query.order_by(ICT_fix.yrs).with_entities(cat[0])
    mob = ICT_mob.query.order_by(ICT_mob.yrs).with_entities(cat[1])
    per = ICT_per.query.order_by(ICT_per.yrs).with_entities(cat[2])
    bw = ICT_bw.query.order_by(ICT_bw.yrs).with_entities(cat[3])

    return render_template(
        'indicator_page.html', 
        title=country, 
        fix_yr=fix_yr, 
        mob_yr=mob_yr, 
        per_yr=per_yr, 
        bw_yr=bw_yr, 
        fix=fix, 
        mob=mob, 
        per=per, 
        bw=bw
        )

@app.route('/indicator')
def indicator_list():
    ctry_lst = [
        'Anguilla',
        'Antigua and Barbuda',
        'Bahamas',
        'Barbados',
        'Belize',
        'Bermuda',
        'British Virgin Islands',
        'Cayman Islands',
        'Dominica',
        'Grenada',
        'Guyana',
        'Haiti',
        'Jamaica',
        'Montserrat',
        'Saint Kitts and Nevis',
        'Saint Lucia',
        'Saint Vincent and the Grenadines',
        'Suriname',
        'Trinidad and Tobago',
        'Turks & Caicos Is.'
    ]
    return render_template('indicator_list.html', title= 'ICT Indicators Listing', indic_all = ctry_lst)

@app.route('/test')
def test():
    # print(population())
    # print(baskets())
    # print(indicators())
    # print(ixp())
    print(density())
    # print(root())
    # print(speedindex())
    # print(submarine())
    # print(tld())
    # create_map()
    # create_speed_graph()
    # create_baskets_graph()
    # create_indic_graph()
    # print("successful")
    # create_land_image()
    # create_sub_image()
    # create_ixp_image()
    # create_root_image()
    create_density_image()            # Failed
    print("Test Completed")
    return render_template('test.html')