### Get Historical Market Data for any Symbol using TD Ameritrade API and Save in SQLite Database
#### Scope
This is a standalone program that obtains the data every day and is triggered by cron.
It uses
TD Ameritrade API: Specifically 'Get Price History'(pricehistory) endpoint 
Python: To work on the received data - format, maintain database connection, find new data to sink etc.
SQLite: To make use of SQL database engine. SQLite is a library that provides a relational database management system. It stores the database as a single file and eliminates the need of maintaining a database server. This immensely simplifies the database operations for a small user.


#### Implementation
The main libraries used in the code are requests, json, pandas and sqlite3.
The functions implemented are
- `get_hist_data` : Gets the historical data by sending appropriate request to the TD Ameritrade server.
- `get_db_connection` : Gets the connection to SQLite database (file)
- `create_table` : Creates the table with the specific schema. A combination of ticker symbol, date, time and interval is used as a primary key. It only creates the table if it does not exist.
- `find_new_data` : Code uses pandas `to_sql` function to write chunk of data to the database. As I understand, this `to_sql` function fails to add data if part of that data exists in the database. In other words, if you want to add 10 records to database and if one of those 10 records already exists in the database, `to_sql` function fails and it does not add rest of the 9 records. To deal with it, `find_new_data` functions gets unique keys from database and removes the data from dataframe that already exists in the database.
The for loop in the main flow iterates 12 times extracting two weeks (10 working days) worth of data at a time to get 6 month of data. This data is then formatted, extra columns are created as needed. The primary key looks like SPY_5_TIMESTAMP.

#### Database Snapshot
Once the data is in the database, this is how the database looks like. Note that the database is just a single file with name 'Historical_Data.db' on your local drive. It can be opened by database browser like 'DB Browser for SQLite'


#### Detailed Explanation
Please see this medium article for more info
