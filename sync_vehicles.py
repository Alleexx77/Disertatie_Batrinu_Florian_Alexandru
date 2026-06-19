import pymysql
import pyodbc
import pandas as pd
from datetime import datetime

wp_conn = pymysql.connect(
    host='localhost',
    port=10005,
    user='root',
    password='root',
    database='local',
    charset='utf8mb4'
)

wp_query = """
SELECT
    p.ID AS wordpress_id,
    p.post_title AS vehicle_name,
    p.post_status AS status,

    MAX(CASE WHEN pm.meta_key = 'stock_number' THEN pm.meta_value END) AS stock_id,
    MAX(CASE WHEN pm.meta_key = 'vin_number' THEN pm.meta_value END) AS vin,

    MAX(CASE WHEN pm.meta_key = 'make' THEN pm.meta_value END) AS make,
    MAX(CASE WHEN pm.meta_key = 'serie' THEN pm.meta_value END) AS model,
    MAX(CASE WHEN pm.meta_key = 'condition' THEN pm.meta_value END) AS vehicle_condition,
    MAX(CASE WHEN pm.meta_key = 'price' THEN pm.meta_value END) AS price,
    MAX(CASE WHEN pm.meta_key = 'body' THEN pm.meta_value END) AS body,
    MAX(CASE WHEN pm.meta_key = 'ca-year' THEN pm.meta_value END) AS year,
    MAX(CASE WHEN pm.meta_key = 'transmission' THEN pm.meta_value END) AS transmission,
    MAX(CASE WHEN pm.meta_key = 'mileage' THEN pm.meta_value END) AS mileage,
    MAX(CASE WHEN pm.meta_key = 'engine' THEN pm.meta_value END) AS engine,
    MAX(CASE WHEN pm.meta_key = 'exterior-color' THEN pm.meta_value END) AS exterior_color,
    MAX(CASE WHEN pm.meta_key = 'interior-color' THEN pm.meta_value END) AS interior_color,
    MAX(CASE WHEN pm.meta_key = 'fuel' THEN pm.meta_value END) AS fuel_type,
    MAX(CASE WHEN pm.meta_key = 'drive' THEN pm.meta_value END) AS drive_type

FROM wp_posts p
LEFT JOIN wp_postmeta pm
    ON p.ID = pm.post_id

WHERE p.post_type = 'listings'

GROUP BY
    p.ID,
    p.post_title,
    p.post_status
"""

df = pd.read_sql(wp_query, wp_conn)
wp_conn.close()

df = df.where(pd.notnull(df), None)

for col in ['price', 'year', 'mileage']:
    df[col] = pd.to_numeric(df[col], errors='coerce')

print("Vehicles extracted from WordPress:")
print(df.head())

cas_conn = pyodbc.connect(
    'DRIVER={SQL Server};'
    'SERVER=RASIROM-DEV\\SQLEXPRESS;'
    'DATABASE=OPENSYNCDB;'
    'Trusted_Connection=yes;'
)

cursor = cas_conn.cursor()

cursor.execute("TRUNCATE TABLE dbo.crm_vehicle_staging")
cas_conn.commit()

for _, row in df.iterrows():

    values = [
        int(row['wordpress_id']),
        None if pd.isna(row['vehicle_name']) else str(row['vehicle_name']),
        None if pd.isna(row['status']) else str(row['status']),
        None if pd.isna(row['stock_id']) else str(row['stock_id']),
        None if pd.isna(row['vin']) else str(row['vin']),
        None if pd.isna(row['make']) else str(row['make']),
        None if pd.isna(row['model']) else str(row['model']),
        None if pd.isna(row['vehicle_condition']) else str(row['vehicle_condition']),
        None if pd.isna(row['price']) else float(row['price']),
        None if pd.isna(row['body']) else str(row['body']),
        None if pd.isna(row['year']) else int(row['year']),
        None if pd.isna(row['transmission']) else str(row['transmission']),
        None if pd.isna(row['mileage']) else int(row['mileage']),
        None if pd.isna(row['engine']) else str(row['engine']),
        None if pd.isna(row['exterior_color']) else str(row['exterior_color']),
        None if pd.isna(row['interior_color']) else str(row['interior_color']),
        None if pd.isna(row['fuel_type']) else str(row['fuel_type']),
        None if pd.isna(row['drive_type']) else str(row['drive_type']),
        datetime.now()
    ]

    cursor.execute("""
        INSERT INTO dbo.crm_vehicle_staging (
            wordpress_id,
            vehicle_name,
            status,
            stock_id,
            vin,
            make,
            model,
            condition,
            price,
            body,
            year,
            transmission,
            mileage,
            engine,
            exterior_color,
            interior_color,
            fuel_type,
            drive_type,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, values)

cas_conn.commit()
cursor.close()
cas_conn.close()

print("Vehicle sync completed successfully.")