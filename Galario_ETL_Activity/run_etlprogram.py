# etl/run_etlprogram.py
from extract import run_extract
from transform import transform_and_clean
from load import build_big_table

def run_etl():
    print("STARTING ETL…")
    
    print("Stage 1: Extracting…")
    run_extract()
    
    print("Stage 2: Transforming…")
    transform_and_clean()
    
    print("Stage 3: Loading…")
    build_big_table()
    
    print("ETL COMPLETE")

if __name__ == "__main__":
    run_etl()
