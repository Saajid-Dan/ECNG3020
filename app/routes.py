from flask import render_template, url_for, send_from_directory, request, render_template_string, jsonify, Response, redirect
from app import app, db
from app.forms import Feedback, form_validate, Machine_format, Report

import geopandas as gpd
import ast
from bs4 import BeautifulSoup
import requests
import pdfkit

from sqlalchemy import inspect, MetaData
import pandas as pd
from dicttoxml import dicttoxml
from json import loads

from app.models import *

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

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    
    url = url_for('index')
    form = Feedback()
    form_validate(url, form)
        
    return render_template('index.html', title='Home', form=form, url=url)


# ------------------------------- Baskets Route ------------------------------ #

@app.route('/basket/<path>', methods=['GET', 'POST'])
def basket_page(path):
    gni = Itu_basket_gni.query.filter_by(country=path).all()
    ppp = Itu_basket_ppp.query.filter_by(country=path).all()
    usd = Itu_basket_usd.query.filter_by(country=path).all()

    url = url_for('basket_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='basket_page', path2=path))

    return render_template('basket_page.html', title=path, gni=gni, ppp=ppp, usd=usd, form=form, form_pdf=form_pdf, url=url)

@app.route('/basket', methods=['GET', 'POST'])
def basket_list():
    ctry = Itu_basket_gni.query.order_by(Itu_basket_gni.country).with_entities(Itu_basket_gni.country)
    ctry_lst = list(dict.fromkeys([c for c, in ctry]))

    url = url_for('basket_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('basket_list.html', title= 'ICT Price Basket Listing', bask = ctry_lst, form=form, url=url)


# ------------------------------ Facility Route ------------------------------ #

@app.route('/facility/<path>', methods=['GET', 'POST'])
def facility_page(path):
    fac = Pdb_facility.query.order_by(Pdb_facility.lon).filter_by(country=path).all()

    nets = []
    for j in fac:
        for k in range(j.net_id.count(', ')):
            net_id = j.net_id.split(', ')[k]
            net_name =  db.session.query(Pdb_network.name).filter(Pdb_network.net_id==net_id).first()
            nets.append(net_name[0])

    url = url_for('facility_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='facility_page', path2=path))

    return render_template('facility_page.html', title=path, fac=fac, nets=nets, form=form, form_pdf=form_pdf, url=url)

@app.route('/facility', methods=['GET', 'POST'])
def facility_list():
    fac = Pdb_facility.query.order_by(Pdb_facility.country).with_entities(Pdb_facility.country)
    fac_lst = list(dict.fromkeys([f for f, in fac]))
    
    url = url_for('facility_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('facility_list.html', title= 'Facility Listing', fac = fac_lst, form=form, url=url)


# ------------------------- General Population Route ------------------------- #

@app.route('/gen/<path>', methods=['GET', 'POST'])
def gen_page(path):
    gen = Cia_general.query.filter_by(country=path).first_or_404()
    dens = Wpop_density.query.filter_by(country=path).first_or_404()

    url = url_for('gen_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='gen_page', path2=path))

    return render_template('gen_page.html', title=path, gen=gen, dens=dens, form=form, form_pdf=form_pdf, url=url)

@app.route('/gen', methods=['GET', 'POST'])
def gen_list():
    ctry = Cia_general.query.order_by(Cia_general.country).with_entities(Cia_general.country)
    ctry_lst = [c for c, in ctry]

    url = url_for('gen_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('gen_list.html', title= 'General Population Information Listing', gen = ctry_lst, form=form, url=url)


# ----------------------------- Indicators Route ----------------------------- #

@app.route('/indicator/<path>', methods=['GET', 'POST'])
def indicator_page(path):

    indic = Itu_indicator.query.filter_by(country=path).order_by(Itu_indicator.date).all()

    url = url_for('indicator_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='indicator_page', path2=path))

    return render_template('indicator_page.html', title=path, indic=indic, form=form, form_pdf=form_pdf, url=url)

@app.route('/indicator', methods=['GET', 'POST'])
def indicator_list():
    indic = Itu_indicator.query.order_by(Itu_indicator.country).with_entities(Itu_indicator.country)
    ctry_lst = list(dict.fromkeys([c for c, in indic]))

    url = url_for('indicator_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('indicator_list.html', title= 'ICT Indicators Listing', indic = ctry_lst, form=form, url=url)


# --------------------------------- IXP Route -------------------------------- #

@app.route('/ixp/pch/<path>', methods=['GET', 'POST'])
def ixp_page_pch(path):
    ixp_dir = Pch_ixp_dir.query.filter_by(country=path).all()
    ixp_sub = Pch_ixp_sub.query.filter_by(country=path).all()
    ixp_mem = Pch_ixp_mem.query.filter_by(country=path).all()

    url = url_for('ixp_page_pch', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='ixp_page_pch', path2=path))

    return render_template('ixp_page_pch.html', title=path, ixp_dir=ixp_dir, ixp_sub=ixp_sub, ixp_mem=ixp_mem, form=form, form_pdf=form_pdf, url=url)

@app.route('/ixp/pdb/<path>', methods=['GET', 'POST'])
def ixp_page_pdb(path):
    ixp = Pdb_ixp.query.filter_by(country=path).all()

    facs = []
    for j in ixp:
        for k in range(j.fac_id.count(', ')):
            fac_id = j.fac_id.split(', ')[k]
            fac_name =  db.session.query(Pdb_facility.name).filter(Pdb_facility.fac_id==fac_id).first()
            facs.append(fac_name[0])

    url = url_for('ixp_page_pdb', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='ixp_page_pdb', path2=path))

    return render_template('ixp_page_pdb.html', title=path, ixp=ixp, fac=facs, form=form, form_pdf=form_pdf, url=url)

@app.route('/ixp', methods=['GET', 'POST'])
def ixp_list():
    ctry = Pch_ixp_dir.query.order_by(Pch_ixp_dir.country).with_entities(Pch_ixp_dir.country)
    ctry_pch = list(dict.fromkeys([c for c, in ctry]))

    ctry = Pdb_ixp.query.order_by(Pdb_ixp.country).with_entities(Pdb_ixp.country)
    ctry_pdb = list(dict.fromkeys([c for c, in ctry]))

    url = url_for('ixp_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('ixp_list.html', title= 'IXP Listing', ixp1=ctry_pch, ixp2=ctry_pdb, form=form, url=url)


# --------------------------- Landing Point Routes --------------------------- #

@app.route('/landing/<path>', methods=['GET', 'POST'])
def land_page(path):
    lan = Telegeography_landing
    land_uni = lan.query.order_by(lan.lon).filter_by(country=path).all()
    lst_cab = [ast.literal_eval(j.cables) for j in land_uni]
    
    url = url_for('land_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='land_page', path2=path))

    return render_template('land_page.html', title=path, land=land_uni, cables=lst_cab, form=form, form_pdf=form_pdf, url=url)

@app.route('/landing', methods=['GET', 'POST'])
def land_list():
    lan = Telegeography_landing
    ctry = lan.query.order_by(lan.country).filter_by(in_caribbean='Yes').with_entities(lan.country)
    ctry_lst = list(dict.fromkeys([c for c, in ctry]))
    
    url = url_for('land_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('land_list.html', title= 'Landing Point Listing', land=ctry_lst, form=form, url=url)


# ------------------------------- Network Route ------------------------------ #

@app.route('/network/<path>', methods=['GET', 'POST'])
def network_page(path):
    net = Pdb_network.query.filter_by(name=path).first_or_404()

    url = url_for('network_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='network_page', path2=path))

    return render_template('network_page.html', title=path, net=net, form=form, form_pdf=form_pdf, url=url)

@app.route('/network', methods=['GET', 'POST'])
def network_list():
    net = Pdb_network.query.order_by(Pdb_network.name).with_entities(Pdb_network.name)
    net_lst = list(dict.fromkeys([n for n, in net]))
    
    url = url_for('network_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('network_list.html', title= 'Network Listing', net=net_lst, form=form, url=url)


# ----------------------------- Root Server Route ---------------------------- #

@app.route('/root/<path>', methods=['GET', 'POST'])
def root_page(path):
    root = Iana_root_server.query.filter_by(country=path).all()

    url = url_for('root_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='root_page', path2=path))

    return render_template('root_page.html', title=path, root=root, form=form, form_pdf=form_pdf, url=url)

@app.route('/root', methods=['GET', 'POST'])
def root_list():
    ctry = Iana_root_server.query.order_by(Iana_root_server.country).with_entities(Iana_root_server.country)
    ctry_lst = list(dict.fromkeys([c for c, in ctry]))

    url = url_for('root_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('root_list.html', title= 'Root Server Listing', root = ctry_lst, form=form, url=url)


# ------------------------------ Speedtest Route ----------------------------- #

@app.route('/speed/<path>', methods=['GET', 'POST'])
def speed_page(path):
    fix = Ookla_fixed_bband.query.filter_by(country=path).all()
    mob = Ookla_mobile_bband.query.filter_by(country=path).all()

    url = url_for('speed_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='speed_page', path2=path))

    return render_template('speed_page.html', title=path, fix=fix, mob=mob, form=form, form_pdf=form_pdf, url=url)

@app.route('/speed', methods=['GET', 'POST'])
def speed_list():
    ctry = Ookla_fixed_bband.query.order_by(Ookla_fixed_bband.country).with_entities(Ookla_fixed_bband.country)
    ctry_lst = list(dict.fromkeys([c for c, in ctry]))

    url = url_for('speed_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('speed_list.html', title= 'Speed Index Listing', speed = ctry_lst, form=form, url=url)


# --------------------------- Submarine Cable Route -------------------------- #

@app.route('/submarine/<path>', methods=['GET', 'POST'])
def sub_page(path):
    cab = Telegeography_submarine
    lan = Telegeography_landing
    cable = cab.query.filter_by(name=path).first_or_404()
    land_pts = cable.land_pts
    land_pts = ast.literal_eval(land_pts)
    
    car_lst = []
    int_lst = []

    for j in land_pts:
        print(j['id'])
        in_caribbean = lan.query.filter_by(id_ref=j['id'], in_caribbean='Yes').first()
        coords = db.session.query(lan.lon, lan.name).filter_by(id_ref=j['id']).first()
        
        int_lst.append(coords) if in_caribbean == None else car_lst.append(coords)
    
    int_lst.sort(key = lambda x: x[0])
    print(int_lst)
    int_lst = dict(int_lst).values()
    print(int_lst)

    car_lst.sort(key = lambda x: x[0])
    car_lst = dict(car_lst).values()

    url = url_for('sub_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='sub_page', path2=path))

    return render_template('sub_page.html', title=path, sub=cable, car=car_lst, int=int_lst, form=form, form_pdf=form_pdf, url=url)

@app.route('/submarine', methods=['GET', 'POST'])
def sub_list():
    cable = Telegeography_submarine.query.order_by(Telegeography_submarine.name).with_entities(Telegeography_submarine.name)
    cable_lst = [c for c, in cable]

    url = url_for('sub_list')
    form = Feedback()
    form_validate(url, form)
        
    return render_template('sub_list.html', title= 'Submarine Cable Listing', sub=cable_lst, form=form, url=url)


# --------------------------------- TLD Route -------------------------------- #

@app.route('/tld/<path>', methods=['GET', 'POST'])
def tld_page(path):
    tld = Iana_tld.query.filter_by(country=path).first_or_404()

    url = url_for('tld_page', path=path)
    form = Feedback()
    form_validate(url, form)

    form_pdf = Report()
    if form_pdf.save.data:
        return redirect(url_for('pdf', path1='tld_page', path2=path))

    return render_template('tld_page.html', title=path, tld=tld, form=form, form_pdf=form_pdf, url=url)

@app.route('/tld', methods=['GET', 'POST'])
def tld_list():
    ctry = Iana_tld.query.order_by(Iana_tld.country).with_entities(Iana_tld.country)
    ctry_lst = [c for c, in ctry]
    
    url = url_for('tld_list')
    form = Feedback()
    form_validate(url, form)

    return render_template('tld_list.html', title= 'TLD Listing', tld = ctry_lst, form=form, url=url)


# ------------------------------- Report Routes ------------------------------ #

@app.route('/pdf/<path1>/<path2>')
def pdf(path1, path2):
    path_wkhtmltopdf = r'C:\Users\User\Documents\Python Scripts\ECNG3020\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    
    head = request.headers['Host']
    url = url_for('strip_base', path1=path1, path2=path2)
    
    options = {
        'page-size': 'Letter',
        'margin-top': '1in',
        'margin-right': '1in',
        'margin-bottom': '1in',
        'margin-left': '1in',
    }

    report = pdfkit.from_url('http://' + head + url, options=options, configuration=config)
    
    return Response(report, mimetype='application/pdf', headers={'Content-Disposition':'attachment;filename={}.pdf'.format('report')})

@app.route('/strip_base/<path1>/<path2>')
def strip_base(path1, path2):
    head = request.headers['Host']
    sub = url_for(path1, path=path2)
    source = requests.get('http://' + head + sub).text
    soup = BeautifulSoup(source, 'lxml')

    a = str(soup).find('<!-- boundary -->')
    b = str(soup).find('<!-- boundary -->', a + 1)
    
    html = str(soup)[a:b]
    html = html.replace('h5', 'h2')
    html = f'''
    <!doctype html>
    <head>
        <meta charset="UTF-8">
        <style>
        body {{ 
            font: normal Helvetica, Arial, sans-serif; 
            letter-spacing: 1.5px;
        }}
        th, td {{
            text-align: center;
            border: 1px solid whitesmoke;
        }}
        table {{
            width: 100%;
            border-spacing: 0px;
            border: 1px solid whitesmoke;
        }}
        </style>
    </head>
    <body>
    {html}
    </body>
    '''
    return html


# --------------------------- Machine Format Routes -------------------------- #

@app.route('/machine', methods=['GET', 'POST'])
def machine():
    # Instantiate query form for machine format generation
    form1 = Machine_format()

    '''
    Generate machine formats for JSON, CSV and XML.
    '''
    # The databases are designed having as much common names.
    # Not all database columns are needed to produce an effective query.
    # Only meaningful criteria is chosen.
    cols = ['country', 'date', 'name', 'org_name']

    # Get a list database tables as strings
    insp = inspect(db.engine)
    table_names = insp.get_table_names()
    table_names.insert(0, 'Select a Table')

    # Remove database version table so it does not pop up on table dropdown
    # It does not contain the dashboard's data
    table_names.remove('alembic_version')
    
    # If a submit response is sent
    if form1.is_submitted():
        # If submit via submit button
        # Then add options to table dropdown which is initially empty
        if form1.populate.data:
            # Generates table options for table dropdown
            form1.tables.choices = [ (table, table) for table in table_names ]
            form1.tables.default = 'Select a Table'
            form1.process()
            
        # If submit via query button
        # Then generate machine formats
        if form1.query.data:
            
            form1.previous.data = 'Table: {}; Column: {}; Value: {}; Format: {}'.format(w, x, y, z)

        if form1.generate.data:
            z = form1.formats.data   # Selected formats from dropdown

            if z == 'CSV':
                form_data = form1.comment.data
                return Response(form_data, mimetype='application/csv', headers={'Content-Disposition':'attachment;filename={}.csv'.format('csv_format')})

            if z == 'JSON':
                form_data = form1.comment.data
                return Response(form_data, mimetype='text/json', headers={'Content-Disposition':'attachment;filename={}.json'.format('json_format')})

            if z == 'XML':
                form_data = form1.comment.data
                return Response(form_data, mimetype='text/xml', headers={'Content-Disposition':'attachment;filename={}.xml'.format('xml_format')})

            # Redirect to fresh page if any selections were not valid
            # return redirect(url_for('machine'))
    
    url = url_for('machine')
    form = Feedback()
    form_validate(url, form)

    return render_template('machine.html', title= 'Get Datasets', form1=form1, form=form, url=url)


@app.route('/machine/<table>/<column>/<value>/<formats>')
def preview(table, column, value, formats):
    w = table    # Selected table from dropdown
    x = column   # Selected column from dropdown
    y = value    # Selected values from dropdown
    z = formats   # Selected formats from dropdown

    print(w,x,y,z)
    # If column and values selection are empty, then don't generate anything
    # Instead redirect to a fresh page
    if x == None or y == None:
        return redirect(url_for('machine'))

    # Retrieve table's metadata to get column data
    meta_data = db.MetaData(bind=db.engine)
    db.MetaData.reflect(meta_data)
    
    # Converts a table string to an sqlalchemy object
    # A table object is needed for database queries
    u = meta_data.tables[w]

    if y == 'All':
        p = db.session.query(u).all()
    else:
        # Convert a string column to an sql object
        # String column can't be used effectively for queries 
        col = getattr(u.columns, x)
        # Query database table 'u' and filter by column in y
        p = db.session.query(u).filter(col == y).all()

    # Loop over query and store into a list each row as a dictionary.
    # This mimics a basic JSON
    data = [dict(r) for r in p]
    # Convert dictionary to a JSON response object
    response = jsonify(data)

    # If a CSV was selected
    if z == 'CSV':
        # Get JSON string from JSON response object using response.data
        df = pd.json_normalize(loads(response.data))
        # Read JSON into a pandas dataframe
        # df = pd.json_normalize(data)
        # Pandas can convert dataframes to CSV
        csv = df.to_csv(encoding='utf-8', index=False)
        # Return CSV to the user
        
        data = csv

        # return Response(csv, mimetype='application/csv', headers={'Content-Disposition':'attachment;filename={}.csv'.format(w)})

    # If a JSON was selected
    if z == 'JSON':
        # Convert dictionary to a JSON response object
        response = jsonify(data)
        # Fetch JSON from response to deliver to a user
        json = response.data
        # Deliver JSON to the user
        # print(json)

        # print(type(json))
        data = json.decode()

        # return Response(json, mimetype='text/json', headers={'Content-Disposition':'attachment;filename={}.json'.format(w)})

    # If an XML was selected
    if z == 'XML':
        xml = dicttoxml(loads(response.data), attr_type=False)
        # Convert dictionary to an XML
        # xml = dicttoxml(data, attr_type=False)
        # Return XML to the user
        # print(xml)

        xml_string = xml.decode().replace('><', '>\n<')
        data = xml_string

        # return Response(xml, mimetype='text/xml', headers={'Content-Disposition':'attachment;filename={}.xml'.format(w)})

    return data


@app.route('/machine/<table>/<column>')
def values(table, column):
    '''
    Returns a JSON response that dynamically swaps dropdown options depending on the table and column selection.
    The table and column are inputs.
    '''
    # The databases are designed having as much common names.
    # Not all database columns are needed to produce an effective query.
    # Only meaningful criteria is chosen.
    query_cols = ['country', 'date', 'name', 'org_name']

    # Retrieve table's metadata to get column data
    meta_data = db.MetaData(bind=db.engine)
    db.MetaData.reflect(meta_data)

    lst = []   # Stores a list of dictionaries
    
    # If no valid database table was selected, then return an empty JSON.
    # An empty JSON means that the column and value dropdowns are blank.
    if table == 'Select a Table':
        return jsonify({'data' : lst})

    # Converts a table string to an sqlalchemy object
    # A table object is needed for database queries
    u = meta_data.tables[table]

    # Iterate over columns in the table object
    for col in u.columns:
        # 'col' is formatted as <table>.<column>
        # The column is separated from the table and stored as a string
        # String needed to compare with string column input
        str_col = str(col).split('.')[-1]

        # Checks if the column meets the criteria.
        # Also, checks if column is valid i.e != None.
        # An invalid column means that a JSON will be created with all columns for the input table
        if str_col in query_cols and column == 'None':
            # Stores columns to a dictionary
            # This mimics the innermost part of a JSON
            col_obj = {}
            col_obj['id'] = str_col
            col_obj['name'] = str_col
            lst.append(col_obj)
        
        # A valid column means that a JSON will be created with all value for the input table and column
        elif str_col == column:
            # Fetches unique values for the input column and store into a list
            p = db.session.query(u).with_entities(col).all()
            p = [value for value, in p]
            p = list(dict.fromkeys(p))

            # Iterate over the list to add the values to a dictionary
            # This mimics the innermost part of a JSON
            for j in p:
                val_obj = {}
                val_obj['id'] = j 
                val_obj['name'] = j
                lst.append(val_obj)
    
    # If column in valid i.e. != 'None' ...
    # Then add an entry called 'All' to the list of unique values.
    if column != 'None':
        val_obj = {}
        val_obj['id'] = 'All'
        val_obj['name'] = 'All'
        lst.insert(0, val_obj)

    # Add the innermost dictionary to another dictionary
    # This dictionary mimics the outermost part of a JSON
    # jsonify converts and returns the dictionary as a JSON response
    return jsonify({'data' : lst})



@app.route('/test')
def test():
    # print(cia_general())
    # print("successful")
    # print(iana_root_servers())
    # print("successful")
    # print(iana_tld())
    # print("successful")
    # print(itu_baskets())
    # print("successful")
    # print(itu_indicators())
    # print("successful")
    # print(ookla_speed_index())
    # print("successful")
    # print(pch_ixp())
    # print("successful")
    # print(peeringdb_ixp())
    # print("successful")
    # print(telegeography_submarine())
    # print("successful")
    # print(worldpop_density())
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
    # print("successful")
    # create_fac_image()
    # print("Test Completed")
    return render_template('test.html')