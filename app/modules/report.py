from app import db
from sqlalchemy import inspect, MetaData

def generate_report():

    # Query criteria
    cols = [
        'ctry',
        'year',
        'date',
        'ctry_',
        'name',
        'org_name',
        'country',
        'pop_yr',
    ]

    # Get Table Names
    insp = inspect(db.engine)
    table_names = insp.get_table_names()
    
    # Remove column
    table_names.remove('alembic_version')

    # print(table_names)			# List of table names as strings in database 'db'

    # Retrieve table's metadata to get column data
    meta_data = db.MetaData(bind=db.engine)
    db.MetaData.reflect(meta_data)

    for j in range(len(table_names)):
        # Converts a table string to an sqlalchemy object
        u = meta_data.tables[table_names[j]]	# First table name string

        for col in u.columns:
            
            # If column in tables is in the query criteria (cols) ...
            if str(col).split('.')[-1] in cols:
            
                # Returns a list of tuples for all values in column 0
                p = db.session.query(u).with_entities(col).all()
                
                # Unpack tuples in a list.
                p = [value for value, in p]

                # Remove duplicates from list.
                p = list(dict.fromkeys(p))
                
                # Insert a query selection of 'all'
                p.insert(0, 'all')

                # Links the sqlalchemy object (table column) to its contents in 'p'.
                dict_col = {col: p}
                     