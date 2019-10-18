import sqlite3

conn = sqlite3.connect('contracts.db',
                       detect_types=PARSE_DECLTYPES)
c = conn.cursor()
c.execute('''CREATE TABLE contracts
                        (id integer primary key, 
                        date date, 
                        expiry date,
                        strike text, 
                        contract_type text, 
                        option_type text,
                        volume integer, 
                        vwap real)''')
conn.close()
