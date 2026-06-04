import sqlite3
import pandas as pd
import re
import math

#Establish connection to database 
conn = sqlite3.connect('world_heritage.db')

#create cursor for SQL commands
cur = conn.cursor()


# Load Excel sheet into a DataFrame
file_path = "whc-sites-2024.xls"
data = pd.read_excel(file_path, sheet_name=0)

#Criterias - just need to add once

descriptions = ['to represent a masterpiece of human creative genius',
'to exhibit an important interchange of human values, over a span of time or within a cultural area of the world, on developments in architecture or technology, monumental arts, town-planning or landscape design',
'to bear a unique or at least exceptional testimony to a cultural tradition or to a civilization which is living or which has disappeared',
'to be an outstanding example of a type of building, architectural or technological ensemble or landscape which illustrates (a) significant stage(s) in human history',
'to be an outstanding example of a traditional human settlement, land-use, or sea-use which is representative of a culture (or cultures), or human interaction with the environment especially when it has become vulnerable under the impact of irreversible change',
'to be directly or tangibly associated with events or living traditions, with ideas, or with beliefs, with artistic and literary works of outstanding universal significance. (The Committee considers that this criterion should preferably be used in conjunction with other criteria)',
'to contain superlative natural phenomena or areas of exceptional natural beauty and aesthetic importance',
'to be outstanding examples representing major stages of earths history, including the record of life, significant on-going geological processes in the development of landforms, or significant geomorphic or physiographic features',
'to be outstanding examples representing significant on-going ecological and biological processes in the evolution and development of terrestrial, fresh water, coastal and marine ecosystems and communities of plants and animals',
'to contain the most important and significant natural habitats for in-situ conservation of biological diversity, including those containing threatened species of outstanding universal value from the point of view of science or conservation'
]

b = 1
for description in descriptions:
    cur.execute('''INSERT INTO Criterias(sigla, description)
                 VALUES ( ?, ? )''',( f"C{b}", description) )
    b += 1
conn.commit()



#iterate over each row and extract information to add to database
for index, row in data.iterrows():

    #Regions
    if row['region_en'].find(',') == -1:
        cursor = cur.execute('SELECT 1 FROM Regions WHERE name = ?', (row['region_en'],))
        if cursor.fetchone() is None:  # No record found
            cur.execute('''
                INSERT INTO Regions (name)
                VALUES (?)
            ''', (row['region_en'],))
        conn.commit()

    

    #Sites
    cur.execute('''
            INSERT INTO Sites (siteID, rev_bis, name, description,danger, longitude, latitude, area_hectares, transboundary)
            VALUES (?,?,?,?,?,?,?,?,?) ''',(row['unique_number'], row['rev_bis'], row['name_en'],
                                            row['short_description_en'], row['danger'], row['longitude'], 
                                            row['latitude'], row['area_hectares'], row['transboundary'],))
    conn.commit()


    #Risks
    results = []
    danger_list = row['danger_list']  # Get the value from the row
    if danger_list is not None and not isinstance(danger_list, float):
        matches = re.findall(r'(Y \d{4}|P \d{4}-\d{4})', str(danger_list))
        # Process matches as needed
    else:
        # Handle cases where danger_list is not a valid string
        matches = []

    for match in matches:
        if match.startswith('Y'):
            # Extract type and year
            _, year = match.split()
            results.append({
                'type': 'Y',
                'year': int(year),
                'period_start': None,
                'period_end': None,
                'date_end': None
            })
        elif match.startswith('P'):
            # Extract type, period_start, and period_end
            _, period = match.split()
            period_start, period_end = map(int, period.split('-'))
            if period_end == row['date_end']:
                results.append({
                    'type': 'P',
                    'year': None,
                    'period_start': period_start,
                    'period_end': period_end,
                    'date_end': period_end
                })
            else:
                results.append({
                    'type': 'P',
                    'year': None,
                    'period_start': period_start,
                    'period_end': period_end,
                    'date_end': None
                })


    for entry in results:
        cur.execute(''' INSERT INTO Risks (type, date_end, year, period_start, period_end)
        VALUES (?,?,?,?,?)
        ''',
        (entry['type'], entry['date_end'], entry['year'], entry['period_start'], entry['period_end'],)
        )
    conn.commit()


    #Dates
    # Check if 'secondary_dates' is not None and convert to string if necessary
    secondary_dates = row['secondary_dates']

    if isinstance(secondary_dates,str):
        if isinstance(secondary_dates, str):
            years_to_add = secondary_dates.split(',')  # Split the string
        elif secondary_dates:  # If it's a float, convert to a string
            years_to_add = str(secondary_dates).split(',')  # Handle float conversion
    else:
        years_to_add = []  # No valid dates

    # Insert each year into the database
    for year in years_to_add:
        cursor = cur.execute('''SELECT 1 FROM Dates WHERE year = ?''', (year,))
        if cursor.fetchone() is None:
            cur.execute(''' INSERT INTO Dates (year)
                            VALUES (?)
                ''', (year.strip(),))  # Ensure stripping of extra spaces
    conn.commit()



    #Selections
    cur.execute('''INSERT INTO Selections (selectionID, siteID, justification,year_inscribed, category_short, category, criteria_txt)
                    VALUES(?,?,?,?,?,?,?)
    ''', (row['id_no'], row['unique_number'], row['justification_en'], row['date_inscribed'], row['category_short'], row['category'], row['criteria_txt'],))
    conn.commit()



for index, row in data.iterrows():

    #States
    if row['region_en'].find(',') == -1:  # We just want to add the countries where the region is well defined
        # Fetch the region ID from the database
        cur.execute('''SELECT regionID FROM Regions WHERE name = ? ''', (row['region_en'],))
        result = cur.fetchone()
        region_id = result[0]

        # Split states into a list
        states = row['states_name_en'].split(',')

        # Initialize iso_codes and udnp_codes
        iso_codes = [None] * len(states) if isinstance(row['iso_code'], float) else row['iso_code'].split(',')
        
        udnp_codes = [None] * len(states) if isinstance(row['udnp_code'], float) else row['udnp_code'].split(',')

        # Iterate over states
        for x in range(len(states)):
            # Check if the state already exists in the database
            cur.execute('''SELECT 1 FROM States WHERE name = ? AND regionID = ?''', (states[x], region_id))
            if cur.fetchone() is None:  # State does not exist, so insert it
                cur.execute(
                    '''INSERT INTO States (regionID, name, iso_code, udnp_code)
                    VALUES (?,?,?,?)''',
                    (region_id, 
                    states[x], 
                    iso_codes[x] if x < len(iso_codes) else None, 
                    udnp_codes[x] if x < len(udnp_codes) else None)
                )
                conn.commit()

    #Info_Risks
    import re

    results = []
    danger_list = row['danger_list'] 
    if danger_list is not None and not isinstance(danger_list, float):
        matches = re.findall(r'(Y \d{4}|P \d{4}-\d{4})', str(danger_list))
    else:
        matches = []

    for match in matches:
        if match.startswith('Y'):
            # Extract type and year
            _, year = match.split()
            entry = {
                'type': 'Y',
                'year': int(year),
                'period_start': None,
                'period_end': None,
                'date_end': None
            }
        elif match.startswith('P'):
            # Extract type, period_start, and period_end
            _, period = match.split()
            period_start, period_end = map(int, period.split('-'))
            entry = {
                'type': 'P',
                'year': None,
                'period_start': period_start,
                'period_end': period_end,
                'date_end': None
            }
            # If date_end matches period_end in row, include it
            if period_end == row.get('date_end'):
                entry['date_end'] = period_end
        else:
            continue

        # Add entry to results
        results.append(entry)

    # Function to check if a Risk entry exists
    def get_existing_risk_id(cur, entry):
        cur.execute('''
            SELECT riskID FROM Risks
            WHERE type = ?
            AND (date_end = ? OR date_end IS NULL AND ? IS NULL)
            AND (year = ? OR year IS NULL AND ? IS NULL)
            AND (period_start = ? OR period_start IS NULL AND ? IS NULL)
            AND (period_end = ? OR period_end IS NULL AND ? IS NULL)
        ''', (
            entry['type'], entry['date_end'], entry['date_end'],
            entry['year'], entry['year'],
            entry['period_start'], entry['period_start'],
            entry['period_end'], entry['period_end']
        ))
        result = cur.fetchone()
        return result[0] if result else None

    # Process and insert into the database
    for entry in results:
        risk_id = get_existing_risk_id(cur, entry)
        if risk_id:
            cur.execute('''INSERT INTO Info_Risks (riskID, siteID)
                        VALUES (?,?)''',
                        (risk_id, row['unique_number']))
            
    #All_Criterias
    for i in range(1,11):
        if (i<7):
            code = f"C{i}"
        else: 
            code = f"N{i}"
        if row[code] == 1: 
            cur.execute('''INSERT INTO All_Criterias (selectionID, sigla)
                        VALUES (?,?)''', 
                        (row['id_no'], code))


    #Date_COMBINATIONS
    if isinstance(row['secondary_dates'], str): 
        dates = row['secondary_dates'].split(',')
        for date in dates: 
            cur.execute('''SELECT dateID FROM Dates where year = ? ''', 
                        (date,))
            res = cur.fetchone()
            date_id = res[0]
            cur.execute('''INSERT INTO Date_Combinations ( selectionID, dateID)
                        VALUES ( ?,?)''',
                        (row['id_no'], date_id))
        conn.commit()
        


for index, row in data.iterrows():

    #Sites_Combinations
    # Split states into a list
    states = row['states_name_en'].split(',')

    # Initialize iso_codes and udnp_codes
    for x in range(len(states)): 
        cur.execute('''SELECT stateID FROM States where name = ?''', (states[x],))
        result = cur.fetchone()
        state_id = result[0]
        cur.execute('''INSERT INTO Sites_Combinations(siteID, stateID)
                    VALUES (?,?)''',
                    (row['unique_number'], state_id))
    conn.commit()


    #Dates_Combinations


 