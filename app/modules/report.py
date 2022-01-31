from app import db
from sqlalchemy import inspect, MetaData

def generate_report():

    
    cols = [
        'ctry',
        'year',
        'date',
        'ctry_',
        'name',
        'org_name',
        'country',
        'pop_yr',
        'yrs'
    ]

    # Get Table Names
    insp = inspect(db.engine)
    table_names = insp.get_table_names()
    
    table_names.remove('alembic_version')

    print(table_names)			# List of table names as strings in database 'db'

    meta_data = db.MetaData(bind=db.engine)
    db.MetaData.reflect(meta_data)

    for j in range(len(table_names)):
        # Converts a table string to an sqlalchemy object
        u = meta_data.tables[table_names[j]]	# First table name string
        # print(u)

        for col in u.columns:
            # print(str(col).split('.')[-1] in cols)
            # print(str(col).split('.')[-1])
            # print(type(col))
            if str(col).split('.')[-1] in cols:
                # print(col)
            
                # Returns a list of tuples for all values in column 0
                p = db.session.query(u).with_entities(col).all()
                
                # Unpack tuples in a list.
                p = [value for value, in p]

                p = list(dict.fromkeys(p))
                
                p.insert(0, 'all')

                dict_col = {col: p}
                print(dict_col)
                # print()

        print()      