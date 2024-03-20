import pandas as pd
from sqlalchemy import create_engine

# create dataframes from csv files
df = pd.read_csv("../csv_files/nepalstock_2024-03-03.csv")
pd.set_option("display.max_columns", None)
cols = df.columns.drop(['Date', 'Symbol '])
df[cols] = df[cols].astype(str).apply(lambda x:x.str.replace('"',''))
print(df.head())
df.to_csv('stock_data.csv', sep=',', index=False)
'''

#split LTP column into LTP and Pt. Change columns
# print(df.columns)
df.insert(11, 'Pt. Change ', 0)
df[["LTP ", "Pt. Change "]] = df['LTP '].str.split('(', n= 1, expand=True)
# print(df.head())
# df["Pt. Change "] = df["Pt. Change "].map(lambda x: x.rstrip(')'))
df['Pt. Change '] = df['Pt. Change '].str.split(')').str.get(0)
print(df.head())

#convert datatypes from text to numeric
cols = df.columns.drop(['Date', 'Symbol '])
print(cols)
# df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
df[cols] = df[cols].astype('float')
print(df.dtypes)

#convert datatypes to string and date
# df['Date'] = pd.to_datetime(df['Date'])
# print(df.dtypes)

conn_url = "postgresql://postgres:1234@localhost:5432/postgres"
engine = create_engine(conn_url)
df.to_sql(name="nepal_stock_data", con=engine, if_exists='replace', index=False)
print("Inserted to postgres database successfully.")
'''
