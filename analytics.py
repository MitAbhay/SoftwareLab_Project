import pandas as pd
from datetime import datetime, timedelta

# simple ROI-based recommender using historical dataset and rec_* fields in dataset

def recommend_crops_for_input(filters, session, top_n=5):
    """
    filters: dict with optional keys: location, soil_type, ph
    session: SQLAlchemy session
    """
    # load dataset to pandas for easier filtering
    df = pd.read_sql_table('dataset', session.bind)

    # apply filters
    if filters.get('location'):
        df = df[df['location'] == filters['location']]
    if filters.get('soil_type'):
        df = df[df['soil_type'] == filters['soil_type']]
    if filters.get('ph') is not None:
        # allow +/- 0.5 pH tolerance
        df = df[(df['pH'] >= filters['ph'] - 0.5) & (df['pH'] <= filters['ph'] + 0.5)]

    # compute simple score using columns present: use rec_temp/rec_rainfall/N_rec etc. if available
    # For each crop, compute avg N_rec and avg rec_rainfall as a proxy then compute a dummy ROI
    if df.empty:
        return []

    group = df.groupby('Crop').agg({'N_rec': 'mean', 'P_rec': 'mean', 'K_rec': 'mean', 'rec_rainfall': 'mean'})
    group = group.fillna(0)

    results = []
    for crop, row in group.iterrows():
        # heuristic: higher N_rec & P_rec mean higher input needs (cost). We invert to prefer lower input crops
        nutrient_need = (row.get('N_rec', 0) + row.get('P_rec', 0) + row.get('K_rec', 0))
        rainfall_score = row.get('rec_rainfall', 0)
        # compute a synthetic ROI: (rainfall_score + 100) / (1 + nutrient_need)
        roi = (float(rainfall_score) + 100.0) / (1.0 + float(nutrient_need))
        sow = datetime.utcnow().date() + timedelta(days=30)
        harvest = sow + timedelta(days=100)
        results.append({'crop': crop, 'expected_roi': round(roi, 3), 'sowing_date': sow, 'harvest_date': harvest})

    results = sorted(results, key=lambda x: x['expected_roi'], reverse=True)
    return results[:top_n]
