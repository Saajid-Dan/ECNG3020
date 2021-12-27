'''
Name: Saajid Dan
Course: ECNG 3020
Project Title:
'''

# ---------------------------------------------------------------------------- #
#                                    Imports                                   #
# ---------------------------------------------------------------------------- #

import pandas as pd
from bokeh.plotting import figure, show, output_file, save
from bokeh.models import ColumnDataSource, FactorRange, HoverTool, Panel, Tabs
from math import pi
from app import db
from app.models import Mob_br, Fixed_br


# ---------------------------------------------------------------------------- #
#                                 Create Graphs                                #
# ---------------------------------------------------------------------------- #

# List of three letter Caribbean country codes used in plot titles
ctry_ = [
    'Haiti',
    'Jamaica',
    'Suriname',
    'Trinidad and Tobago'
]

cc = [ 
        'HTI', 
        'JAM',  
        'SUR', 
        'TTO'
    ]

# 'dict1' is a dictionary that relates numerical month (key) to three letter abbreviated month (value)
dict1 = {'01':'Jan',
         '02':'Feb',
         '03':'Mar',
         '04':'Apr',
         '05':'May',
         '06':'Jun',
         '07':'Jul',
         '08':'Aug',
         '09':'Sep',
         '10':'Oct',
         '11':'Nov',
         '12':'Dec'}


def create_speed_graph():
    '''
    Retrieves Mobile and Fixed broadband speed index data from the database and plots them into bokeh graphs.
    '''
    
    # -------------------------- Mobile Broadband Graphs ------------------------- #

    # Loop over countries in 'ctry_' to add 4 figures per 4 graphs.
    for index, j in enumerate(ctry_):
        # 'dates' = Extract dates from database query as list with tuples.
        # 'dls' = Extract download speeds from database query as list with tuples.
        # 'ups' = Extract upload speeds from database query as list with tuples.
        # 'ltcy' = Extract latencies from database query as list with tuples.
        # 'jitt' = Extract jitters from database query as list with tuples.
        dates = db.session.query(Mob_br.mnth).filter_by(ctry=j).all()
        dls = db.session.query(Mob_br.dls).filter_by(ctry=j).all()
        ups = db.session.query(Mob_br.ups).filter_by(ctry=j)
        ltcy = db.session.query(Mob_br.ltcy).filter_by(ctry=j)
        jitt = db.session.query(Mob_br.jitt).filter_by(ctry=j)
        
        # Unpack tuples in list.
        dates = [value for value, in dates]
        dls = [value for value, in dls]
        ups = [value for value, in ups]
        ltcy = [value for value, in ltcy]
        jitt = [value for value, in jitt]
        
        # 'y' = y coordinates to plot.
        # 4 lists of coordinates for 4 figures.
        y = [dls, ups, ltcy, jitt]
        
        # 'x' = x coordinates to plot.
        x = []
        
        # Split 'dates' into years (yr) and months (mnth).
        # Appends 'yr' and 'mnth' to 'x' as a tuple.
        # 'x' contains categorical grouped data to be plotted.
        for k in dates:
            yr = k.split('-')[0]
            mnth = dict1.get(k.split('-')[1])
            x.append((yr, mnth + ' 1'))

        # List of figure titles.
        title = [
            'Mobile Broadband - Download',
            'Mobile Broadband - Upload',
            'Mobile Broadband - Latency',
            'Mobile Broadband - Jitter',
        ]

        # list of y-axis label.
        y_label = [
            'Download Speed (Mbps)', 
            'Upload Speed (Mbps)', 
            'Latency (ms)', 
            'Jitter (ms)'
        ]

        # 'tabs' = list to append 4 figures.
        tabs = []
        
        for k in range(4):
            # 'source' = used to reference 'x' and 'y' values.
            source = ColumnDataSource(data={'x':x,'y':y[k]})

            # 'p' = bokeh figure.
            p = figure(
                x_range=FactorRange(*x), 
                width=250, 
                title=title[k].split('-')[0] + '- ' + cc[index],
                x_axis_label = 'Date',
                y_axis_label = y_label[k]
            )
            
            # Orient x-axis by 90 degrees.
            p.xaxis.major_label_orientation = pi/2

            # Custom Bokeh HoverTool
            hover = HoverTool(
                tooltips=[
                    (y_label[k], '@y'),
                    ('Date', '@x')
                ]
            )

            # Add 'hover' to figures.
            p.add_tools(hover)

            # Plot vertical bar chart.
            p.vbar(
                x='x', 
                top='y', 
                width=0.5, 
                source=source,
                color='#0d6efd'
            )
            
            # Makes figures responsive.
            p.sizing_mode = 'stretch_both'

            # Add figure to a Bokeh panel.
            # Append panel to 'tabs' list.
            tabs.append(Panel( child=p, title=title[k].split(' - ')[-1] ))
        
        # 'tabs' = Bokeh tabs object.
        # Combines the figures in 'tabs' list to one graph.
        tabs = Tabs(tabs = tabs)

        # Saves graph in 'tabs' to output directory.
        output_file('./app/static/html/mobile' + str(index) + ".html")
        save(tabs)
    
    
    # -------------------------- Fixed Broadband Graphs -------------------------- #

    # Loop over countries in 'ctry_' to add 4 figures per 4 graphs.
    for index, j in enumerate(ctry_):
        # 'dates' = Extract dates from database query as list with tuples.
        # 'dls' = Extract download speeds from database query as list with tuples.
        # 'ups' = Extract upload speeds from database query as list with tuples.
        # 'ltcy' = Extract latencies from database query as list with tuples.
        # 'jitt' = Extract jitters from database query as list with tuples.
        dates = db.session.query(Fixed_br.mnth).filter_by(ctry=j).all()
        dls = db.session.query(Fixed_br.dls).filter_by(ctry=j).all()
        ups = db.session.query(Fixed_br.ups).filter_by(ctry=j)
        ltcy = db.session.query(Fixed_br.ltcy).filter_by(ctry=j)
        jitt = db.session.query(Fixed_br.jitt).filter_by(ctry=j)

        # Unpack tuples in list.
        dates = [value for value, in dates]
        dls = [value for value, in dls]
        ups = [value for value, in ups]
        ltcy = [value for value, in ltcy]
        jitt = [value for value, in jitt]
        
        # 'y' = y coordinates to plot.
        # 4 lists of coordinates for 4 figures.
        y = [dls, ups, ltcy, jitt]
        
        # 'x' = x coordinates to plot.
        x = []
        
        # Split 'dates' into years (yr) and months (mnth).
        # Appends 'yr' and 'mnth' to 'x' as a tuple.
        # 'x' contains categorical grouped data to be plotted.
        for k in dates:
            yr = k.split('-')[0]
            mnth = dict1.get(k.split('-')[1])
            x.append((yr, mnth + ' 1'))

        # List of figure titles.
        title = [
            'Fixed Broadband - Download',
            'Fixed Broadband - Upload',
            'Fixed Broadband - Latency',
            'Fixed Broadband - Jitter',
        ]

        # list of y-axis label.
        y_label = [
            'Download Speed (Mbps)', 
            'Upload Speed (Mbps)', 
            'Latency (ms)', 
            'Jitter (ms)'
        ]

        # 'tabs' = list to append 4 figures.
        tabs = []
        
        for k in range(4):
            # 'source' = used to reference 'x' and 'y' values.
            source = ColumnDataSource(data={'x':x,'y':y[k]})

            # 'p' = bokeh figure.
            p = figure(
                x_range=FactorRange(*x), 
                width=250, 
                title=title[k].split('-')[0]  + '- ' + cc[index],
                x_axis_label = 'Date',
                y_axis_label = y_label[k])
            
            # Orient x-axis by 90 degrees.
            p.xaxis.major_label_orientation = pi/2

            # Custom Bokeh HoverTool
            hover = HoverTool(
                tooltips=[
                    (y_label[k], '@y'),
                    ('Date', '@x')
                ]
            )

            # Add 'hover' to figures.
            p.add_tools(hover)

            # Plot vertical bar chart.
            p.vbar(
                x='x', 
                top='y', 
                width=0.5, 
                source=source,
                color='#0d6efd'
                )
            
            # Makes figures responsive.
            p.sizing_mode = 'stretch_both'

            # Add figure to a Bokeh panel.
            # Append panel to 'tabs' list.
            tabs.append(Panel( child=p, title=title[k].split(' - ')[-1] ))
        
        # 'tabs' = Bokeh tabs object.
        # Combines the figures in 'tabs' list to one graph.
        tabs = Tabs(tabs = tabs)

        # Saves graph in 'tabs' to output directory.
        output_file('./app/static/html/fixed' + str(index) + ".html")
        save(tabs)
