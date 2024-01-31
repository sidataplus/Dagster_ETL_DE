from dagster import  asset 
from etl.resources.db_conn import get_sql_conn , get_postgres_conn
#import needed libraries
import pandas as pd
import logging

@asset(group_name="churn_modelling", compute_kind="pandas" , io_manager_key="file_io")
def read_csv_solid(context)  -> pd.DataFrame:
    # Replace '/path/to/input.csv' with your actual file path
    file_path = r'./etl/sfo_q2_weather_sample.csv'
    df = pd.read_csv(file_path)
    context.log.info(f'Read {len(df)} rows from {file_path}')
    return df

#load data
@asset( group_name="churn_modelling", compute_kind="pandas", io_manager_key="db_io")
def sfo_q2_weather(context, read_csv_solid: pd.DataFrame) -> pd.DataFrame:
    """Transform and Stage Data into Postgres."""
    try:
        context.log.info(read_csv_solid.head())
        df = read_csv_solid
        #df = df.rename(columns={'surname': 'lastname'})
        return df
    except Exception as e:
        context.log.info(str(e))


#extract data from postgresql
@asset(group_name="churn_modelling", compute_kind="pandas" , io_manager_key="file_io")
def extract_sfo_q2_weather(context) -> pd.DataFrame:
    """Extract Data from Postgresql."""
    conn = get_postgres_conn()
    cursor = conn.cursor()
    query =  "select * FROM public.sfo_q2_weather"
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
        
        # Convert the fetched rows to a DataFrame
    df = pd.DataFrame(rows, columns=[desc[0] for desc in cursor.description])
    context.log.info(df.head())
    return df

#load data
@asset( group_name="churn_modelling", compute_kind="pandas", io_manager_key="db_io")
def dim_sfo_q2_weather(context, extract_sfo_q2_weather: pd.DataFrame) -> pd.DataFrame:
    """Transform and Stage Data into Postgres."""
    try:
        context.log.info(extract_sfo_q2_weather.head())
        df = extract_sfo_q2_weather
        df = df.rename(columns={'station': 'station_weather'})
        return df
    except Exception as e:
        context.log.info(str(e))