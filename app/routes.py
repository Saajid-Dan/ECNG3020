from flask import render_template, url_for, send_from_directory, request, render_template_string
from app import app, db
from app.forms import Feedback, form_validate

import geopandas as gpd
import ast
from bs4 import BeautifulSoup
import requests
import pdfkit

from app.models import Tld
from app.models import Land
from app.models import Ixp_dir, Ixp_sub, Ixp_mem
from app.models import Root_srv
from app.models import Gen_pop, Pop_dens
from app.models import Fixed_br, Mob_br
from app.models import GNI, PPP, USD
from app.models import indicators

from app.sources.General_Population import population
from app.sources.ICT_Baskets import baskets
from app.sources.ICT_Indicators import ict_indicators
from app.sources.Internet_Exchange_Points import ixp
from app.sources.Population_Density import density
from app.sources.Root_Servers import root
from app.sources.Speed_Index import speedindex
from app.sources.Submarine_Cables import submarine
from app.sources.Top_Level_Domains import tld
from app.sources.peeringdb_ixp import peer_ixp

from app.modules.maps import create_map
from app.modules.graph_infr import graph_infr
from app.modules.graph_adop import graph_adop
from app.modules.graph_use import graph_use
from app.modules.landing_image import create_land_image
from app.modules.submarine_image import create_sub_image
from app.modules.ixp_image import create_ixp_image
from app.modules.root_image import create_root_image
from app.modules.density_image import create_density_image
from app.modules.report import generate_report

# from app.modules.test import create_indic_graph_test


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    
    url = url_for('index')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)
        
    return render_template('index.html', title='Home', form=form, url=url)


@app.route('/tld/<country>', methods=['GET', 'POST'])
def tld_page(country):
    tld_ctry = Tld.query.filter_by(ctry_=country).first_or_404()

    url = url_for('tld_page', country=country)
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('tld_page.html', title=country, tld=tld_ctry, form=form, url=url)

@app.route('/landing/<country>', methods=['GET', 'POST'])
def land_page(country):
    land_uni = Land.query.order_by(Land.lon).filter_by(ctry=country).all()
    # x = ast.literal_eval(x[0])
    lst_cab = []
    for j in land_uni:
        x = ast.literal_eval(j.cab)
        lst_cab.append(x)
    
    url = url_for('land_page', country=country)
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('land_page.html', title=country, land=land_uni, cables=lst_cab, form=form, url=url)

@app.route('/landing', methods=['GET', 'POST'])
def land_list():
    ctry_lst = []
    ctry = Land.query.order_by(Land.ctry).filter_by(car='Yes').with_entities(Land.ctry)
    for j in ctry:
        ctry_lst.append(j[0])

    ctry_lst_uni = []
    for items in ctry_lst:
        if items not in ctry_lst_uni:
            ctry_lst_uni.append(items)
    
    url = url_for('land_list')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('land_list.html', title= 'Landing Point Listing', land_all=ctry_lst_uni, form=form, url=url)

@app.route('/submarine/<cable>', methods=['GET', 'POST'])
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

    url = url_for('sub_page', cable=cable)
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('sub_page.html', title=cable, sub=sub, land_car=car_lst, land_int=int_lst, form=form, url=url)

@app.route('/submarine', methods=['GET', 'POST'])
def sub_list():
    cable_lst = []
    file_sub = open('./app/static/json/submarine.json', 'r')
    gdf_sub = gpd.read_file(file_sub)
    for j in range(len(gdf_sub)):
        cable_lst.append(gdf_sub.iloc[j]['name'])

    url = url_for('sub_list')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)
        
    return render_template('sub_list.html', title= 'Submarine Cable Listing', sub_all=cable_lst, form=form, url=url)

@app.route('/ixp/<country>', methods=['GET', 'POST'])
def ixp_page(country):
    ixp_dir = Ixp_dir.query.filter_by(ctry=country).all()
    ixp_sub = Ixp_sub.query.filter_by(ctry=country).all()
    ixp_mem = Ixp_mem.query.filter_by(ctry=country).all()

    url = url_for('ixp_page', country=country)
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('ixp_page.html', title=country, ixp_dir=ixp_dir, ixp_sub=ixp_sub, ixp_mem=ixp_mem, form=form, url=url)

@app.route('/ixp', methods=['GET', 'POST'])
def ixp_list():
    ctry_lst = []
    ctry = Ixp_dir.query.order_by(Ixp_dir.ctry).with_entities(Ixp_dir.ctry)
    for j in ctry:
        ctry_lst.append(j[0])
    ctry_lst = list(dict.fromkeys(ctry_lst))

    url = url_for('ixp_list')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('ixp_list.html', title= 'IXP Listing', ixp_all=ctry_lst, form=form, url=url)

@app.route('/tld', methods=['GET', 'POST'])
def tld_list():
    ctry_lst = []
    ctry = Tld.query.order_by(Tld.ctry_).with_entities(Tld.ctry_)
    for j in ctry:
        ctry_lst.append(j[0])
    
    url = url_for('tld_list')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('tld_list.html', title= 'TLD Listing', tld_all = ctry_lst, form=form, url=url)

@app.route('/root/<country>', methods=['GET', 'POST'])
def root_page(country):
    root = Root_srv.query.filter_by(ctry=country).all()

    url = url_for('root_page', country=country)
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('root_page.html', title=country, root=root, form=form, url=url)

@app.route('/root', methods=['GET', 'POST'])
def root_list():
    ctry_lst = []
    ctry = Root_srv.query.order_by(Root_srv.ctry).with_entities(Root_srv.ctry)
    for j in ctry:
        ctry_lst.append(j[0])
    ctry_lst = list(dict.fromkeys(ctry_lst))

    url = url_for('root_list')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('root_list.html', title= 'Root Server Listing', root_all = ctry_lst, form=form, url=url)

@app.route('/gen/<country>', methods=['GET', 'POST'])
def gen_page(country):
    gen = Gen_pop.query.filter_by(ctry_=country).first()
    dens = Pop_dens.query.filter_by(ctry=country).first()

    url = url_for('gen_page', country=country)
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('gen_page.html', title=country, gen=gen, dens=dens, form=form, url=url)

@app.route('/gen', methods=['GET', 'POST'])
def gen_list():
    ctry_lst = []
    ctry = Gen_pop.query.order_by(Gen_pop.ctry_).with_entities(Gen_pop.ctry_)
    for j in ctry:
        ctry_lst.append(j[0])
    
    url = url_for('gen_list')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('gen_list.html', title= 'General Population Information Listing', gen_all = ctry_lst, form=form, url=url)

@app.route('/speed/<country>', methods=['GET', 'POST'])
def speed_page(country):
    fix = Fixed_br.query.filter_by(ctry=country).all()
    mob = Mob_br.query.filter_by(ctry=country).all()

    url = url_for('speed_page', country=country)
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('speed_page.html', title=country, fix=fix, mob=mob, form=form, url=url)

@app.route('/speed', methods=['GET', 'POST'])
def speed_list():
    ctry_lst = []
    ctry = Fixed_br.query.order_by(Fixed_br.ctry).with_entities(Fixed_br.ctry)
    for j in ctry:
        ctry_lst.append(j[0])
    ctry_lst = list(dict.fromkeys(ctry_lst))

    url = url_for('speed_list')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('speed_list.html', title= 'Speed Index Listing', speed_all = ctry_lst, form=form, url=url)

@app.route('/basket/<country>', methods=['GET', 'POST'])
def basket_page(country):
    gni = GNI.query.filter_by(ctry=country).all()
    ppp = PPP.query.filter_by(ctry=country).all()
    usd = USD.query.filter_by(ctry=country).all()

    url = url_for('basket_page', country=country)
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('basket_page.html', title=country, gni=gni, ppp=ppp, usd=usd, form=form, url=url)

@app.route('/basket', methods=['GET', 'POST'])
def basket_list():
    ctry_lst = []
    ctry = GNI.query.order_by(GNI.ctry).with_entities(GNI.ctry)
    for j in ctry:
        ctry_lst.append(j[0])
    ctry_lst = list(dict.fromkeys(ctry_lst))

    url = url_for('basket_list')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('basket_list.html', title= 'ICT Price Basket Listing', bask_all = ctry_lst, form=form, url=url)

@app.route('/indicator/<country>', methods=['GET', 'POST'])
def indicator_page(country):
    fix = indicators.query.filter_by(ctry=country).all()
    mob = indicators.query.filter_by(ctry=country).all()
    per = indicators.query.filter_by(ctry=country).all()
    bw = indicators.query.filter_by(ctry=country).all()

    year =  indicators.query.order_by(indicators.year).all()
    year = list(dict.fromkeys(year))

    url = url_for('indicator_page', country=country)
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('indicator_page.html', title=country, year=year, fix=fix, mob=mob, per=per, bw=bw, form=form, url=url)

@app.route('/indicator', methods=['GET', 'POST'])
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

    url = url_for('indicator_list')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('indicator_list.html', title= 'ICT Indicators Listing', indic_all = ctry_lst, form=form, url=url)


@app.route('/child/<root>/<sub>')
def child(root, sub):

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

    head = request.headers['Host']

    if sub == 'none':
        sub = url_for(root)
    elif sub in ctry_lst:
        sub = url_for(root, country=sub)
    else:
        sub = url_for(root, cable=sub)

    source = requests.get('http://' + head + sub).text
    soup = BeautifulSoup(source, 'lxml')

    a = str(soup).find('<!-- -------------------------- Insert Code Here --------------------------- -->')
    b = str(soup).find('<!-- -------------------------- Insert Code Here --------------------------- -->', a + 1)
    
    html = str(soup)[a:b]
    html = html.replace('h5', 'h2')

    a = html.find('<audio')
    b = html.find('</audio>')

    if (a != -1 and b != -1):
        html = html.replace(html[a:b+8], 'NA')

    html_head = '''
    <!doctype html>
    <head>
        <meta charset="UTF-8">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
        <style>
        body { 
            font: normal Helvetica, Arial, sans-serif; 
            letter-spacing: 1.5px;
            }
        </style>
    </head>
    <body>
    '''

    html_foot = '''
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>
    </body>
    '''

    return render_template_string(html_head + html + html_foot)

from PyPDF2 import PdfFileMerger, PdfFileReader
from pathlib import Path

@app.route('/create_pdf')
def create_pdf():
    path_wkhtmltopdf = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)


    def merge_pdf(config, cat, query):
        head = request.headers['Host']
        merger = PdfFileMerger()

        sub = url_for('child', root=cat + '_list', sub='none')
        pdfkit.from_url('http://' + head + sub, "./app/temp/listing.pdf", configuration=config)
        pdf = "./app/temp/listing.pdf"
        merger.append(pdf, import_bookmarks=False)

        for item in query:
            sub = url_for('child', root=cat + '_page', sub=item)
            pdfkit.from_url('http://' + head + sub, "./app/temp/" + item + ".pdf", configuration=config)
            pdf = "./app/temp/" + item + ".pdf"
            merger.append(pdf, import_bookmarks=False)
        merger.write("./app/static/pdf/" + cat + ".pdf")
        merger.close()

        # https://stackoverflow.com/questions/185936/how-to-delete-the-contents-of-a-folder
        [f.unlink() for f in Path("./app/temp").glob("*") if f.is_file()] 


    tld = Tld.query.order_by(Tld.ctry_).with_entities(Tld.ctry_).all()
    tld = sorted(set([v[0] for v in tld]))
    merge_pdf(config, 'tld', tld)

    land = Land.query.order_by(Land.ctry).filter_by(car='Yes').with_entities(Land.ctry).all()
    land = sorted(set([v[0] for v in land]))
    merge_pdf(config, 'land', land)

    cable_lst = []
    file_sub = open('./app/static/json/submarine.json', 'r')
    gdf_sub = gpd.read_file(file_sub)
    for j in range(len(gdf_sub)):
        cable_lst.append(gdf_sub.iloc[j]['name'])
    merge_pdf(config, 'sub', cable_lst)

    ixp = Ixp_dir.query.order_by(Ixp_dir.ctry).with_entities(Ixp_dir.ctry).all()
    ixp = sorted(set([v[0] for v in ixp]))
    merge_pdf(config, 'ixp', ixp)

    root = Root_srv.query.order_by(Root_srv.ctry).with_entities(Root_srv.ctry).all()
    root = sorted(set([v[0] for v in root]))
    merge_pdf(config, 'root', root)

    gen = Gen_pop.query.order_by(Gen_pop.ctry_).with_entities(Gen_pop.ctry_).all()
    gen = sorted(set([v[0] for v in gen]))
    merge_pdf(config, 'gen', gen)

    speed = Fixed_br.query.order_by(Fixed_br.ctry).with_entities(Fixed_br.ctry).all()
    speed = sorted(set([v[0] for v in speed]))
    merge_pdf(config, 'speed', speed)

    basket = GNI.query.order_by(GNI.ctry).with_entities(GNI.ctry).all()
    basket = sorted(set([v[0] for v in basket]))
    merge_pdf(config, 'basket', basket)

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
    merge_pdf(config, 'indicator', ctry_lst)

    # print("PDF Test Completed")
    return render_template('test.html')


@app.route('/reports', methods=['GET', 'POST'])
def reports():
    url = url_for('reports')
    form = Feedback()
    if form.validate_on_submit():
        form_validate(url, form)

    return render_template('reports.html', title='Download Reports', form=form, url=url)

@app.route('/pdf/<path:filename>', methods=['GET', 'POST'])
def pdf(filename):
    from pathlib import Path
    root = Path('.')
    folder_path = root / 'static/pdf'

    return send_from_directory(folder_path, filename, as_attachment=True)

@app.route('/csv/<path:filename>', methods=['GET', 'POST'])
def csv(filename):
    from pathlib import Path
    root = Path('.')
    folder_path = root / 'static/csv'

    return send_from_directory(folder_path, filename, as_attachment=True)

@app.route('/json/<path:filename>', methods=['GET', 'POST'])
def json(filename):
    from pathlib import Path
    root = Path('.')
    folder_path = root / 'static/json'

    return send_from_directory(folder_path, filename, as_attachment=True)


from flask import jsonify, redirect, Response
from sqlalchemy import inspect, MetaData
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import ValidationError
import pandas as pd
from dicttoxml import dicttoxml
from json import loads
import xmltodict
import csv

class Form(FlaskForm):
    tables = SelectField('tables', choices=[])
    columns = SelectField('columns', choices=[])
    values = SelectField('values', choices=[])
    formats = SelectField('formats', choices=[('CSV', 'CSV'), ('JSON', 'JSON'), ('XML', 'XML')])
    submit = SubmitField(label=('Populate Tables'))
    query = SubmitField(label=('Submit Query'))

@app.route('/report', methods=['GET', 'POST'])
def report():
    
    form = Form()

    # Query criteria
    cols = ['ctry', 'year', 'date', 'ctry_', 'name', 'org_name', 'country', 'pop_yr']

    # Get Table Names
    insp = inspect(db.engine)
    table_names = insp.get_table_names()
    table_names.insert(0, 'Select a Table')
    # Remove table
    table_names.remove('alembic_version')
    
    if form.is_submitted():
        if form.submit.data:
            print('success')
            form.tables.choices = [ (table, table) for table in table_names ]
            form.tables.default = 'Select a Table'
            form.process()

        if form.query.data:
            w = form.tables.data
            x = form.columns.data
            y = form.values.data
            z = form.formats.data

            if x == None or y == None:
                return redirect(url_for('report'))

            # Retrieve table's metadata to get column data
            meta_data = db.MetaData(bind=db.engine)
            db.MetaData.reflect(meta_data)
            
            # Converts a table string to an sqlalchemy object
            u = meta_data.tables[w]	# First table name string

            col = getattr(u.columns, x)
            p = db.session.query(u).filter(col == y).all()
            
            data = [dict(r) for r in p]
            dict_data = data
            response = jsonify(dict_data)

            if z == 'CSV':
                df = pd.json_normalize(loads(response.data))
                csv = df.to_csv(encoding='utf-8', index=False)
                return Response(csv, mimetype='application/csv', headers={'Content-Disposition':'attachment;filename={}.csv'.format(w)})

            if z == 'JSON':
                json = response.data
                return Response(json, mimetype='text/json', headers={'Content-Disposition':'attachment;filename={}.json'.format(w)})
            
            if z == 'XML':
                xml = dicttoxml(loads(response.data), attr_type=False)
                return Response(xml, mimetype='text/xml', headers={'Content-Disposition':'attachment;filename={}.xml'.format(w)})

            return redirect(url_for('report'))

    return render_template('report.html', form=form)


@app.route('/report/<table>')
def columns(table):

    # Query criteria
    query_cols = ['ctry', 'year', 'date', 'ctry_', 'name', 'org_name', 'country', 'pop_yr']

    # Retrieve table's metadata to get column data
    meta_data = db.MetaData(bind=db.engine)
    db.MetaData.reflect(meta_data)

    lst_cols = []

    if table == 'Select a Table':
        return jsonify({'columns' : lst_cols})
        
    # Converts a table string to an sqlalchemy object
    u = meta_data.tables[table]	# First table name string

    for col in u.columns:
        str_col = str(col).split('.')[-1]
        if str_col in query_cols:
            col_obj = {}
            col_obj['id'] = str_col
            col_obj['name'] = str_col
            lst_cols.append(col_obj)

    return jsonify({'columns' : lst_cols})

@app.route('/report/<table>/<column>')
def values(table, column):
    
    # Retrieve table's metadata to get column data
    meta_data = db.MetaData(bind=db.engine)
    db.MetaData.reflect(meta_data)

    lst_vals = []
    
    if table == 'Select a Table':
        return jsonify({'values' : lst_vals})

    # Converts a table string to an sqlalchemy object
    u = meta_data.tables[table]	# First table name string

    for col in u.columns:
        str_col = str(col).split('.')[-1]
        if str_col == column:

            # Returns a list of tuples for all values in column 0
            p = db.session.query(u).with_entities(col).all()
            
            # Unpack tuples in a list.
            p = [value for value, in p]

            # Remove duplicates from list.
            p = list(dict.fromkeys(p))

            for j in p:
                val_obj = {}
                val_obj['id'] = j 
                val_obj['name'] = j
                lst_vals.append(val_obj)

    return jsonify({'values' : lst_vals})

@app.route('/test')
def test():
    # print(population())
    # print(baskets())
    # print(ict_indicators())
    # print(ixp())
    print(peer_ixp())
    # print(density())
    # print(root())
    # print(speedindex())
    # print(submarine())
    # print(tld())
    # print("successful")
    # create_map()
    # print("successful")
    # graph_infr()
    # print("successful")
    # graph_adop()
    # print("successful")
    # graph_use()
    # print("successful")
    # create_land_image()
    # print("successful")
    # create_sub_image()
    # print("successful")
    # create_ixp_image()
    # print("successful")
    # create_root_image()
    # print("successful")
    # create_density_image()
    # generate_report()
    print("Test Completed")
    return render_template('test.html')