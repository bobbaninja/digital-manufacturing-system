import pandas as pd
import sqlite3
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import MES_CSV, ERP_CSV, SPECS_CSV, DB_PATH

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_data():
    try:
        mes = pd.read_csv(MES_CSV)
        erp = pd.read_csv(ERP_CSV)
        specs = pd.read_csv(SPECS_CSV)
        logging.info("Data loaded successfully.")
        return mes, erp, specs
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        raise

def transform_data(mes, erp, specs):
    df = mes.merge(erp, how="left", on="serial_number").merge(specs, how="left", on=["part_number", "process_step"])
    df["out_of_spec"] = (
        (df["measured_value"] < df["lower_limit"]) |
        (df["measured_value"] > df["upper_limit"])
    )
    df = df.sort_values(["serial_number", "event_time"])
    df["consecutive_failures"] = (
        df.groupby("serial_number")["out_of_spec"]
          .transform(lambda x: x.astype(int).groupby(x.eq(False).cumsum()).cumsum())
    )
    logging.info("Data transformed.")
    return df

def load_to_db(df):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql("validated_data", conn, if_exists="replace", index=False)
    conn.close()
    logging.info("Data loaded to database.")

if __name__ == "__main__":
    mes, erp, specs = load_data()
    df = transform_data(mes, erp, specs)
    load_to_db(df)
    logging.info("ETL pipeline completed.")