"""
Imports `CropCompass.xlsx` into `cropcompass.db` if the DB file is missing.
This helps when running the app locally: put CropCompass.xlsx in the project root.
"""

import os
from pathlib import Path
import pandas as pd
from models import db


def import_excel_if_needed(app):
    """Import Excel sheets into SQLite if the DB file does not exist."""
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    # Only proceed if using SQLite
    if not db_url.startswith('sqlite:///'):
        return

    db_file = db_url.replace('sqlite:///', '')

    if Path(db_file).exists():
        # DB already exists — nothing to import
        return

    xlsx = Path('CropCompass.xlsx')
    if not xlsx.exists():
        print("[WARN] CropCompass.xlsx not found; skipping import.")
        return

    print("[INFO] Importing Excel data into", db_file)
    xls = pd.ExcelFile(str(xlsx))

    # Initialize DB before use
    with app.app_context():
        engine = db.engine  # ✅ the proper way to get engine inside app context
        conn = engine.raw_connection()
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            df.columns = [str(c).strip().replace(' ', '_') for c in df.columns]
            df.to_sql(sheet.lower(), conn, if_exists='replace', index=False)
        conn.commit()
        conn.close()
    print("[INFO] Excel import completed successfully.")
