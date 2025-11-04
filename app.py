from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import db, init_db, CropRecord, AttributeInfo, Recommendation
from analytics import recommend_crops_for_input
from db_importer import import_excel_if_needed
from scraper import fetch_and_store_market_prices
import os

from apscheduler.schedulers.background import BackgroundScheduler


def create_app():
    app = Flask(__name__)

    # Config - use DATABASE_URL env var or default to sqlite file in project root
    DB_URL = os.environ.get('DATABASE_URL', 'sqlite:///cropcompass.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize DB and (if needed) import Excel into sqlite (when running locally)
    init_db(app)
    import_excel_if_needed(app)  # will import CropCompass.xlsx -> cropcompass.db if DB missing

    # start scheduler to fetch market prices periodically (lightweight example)
    scheduler = BackgroundScheduler()
    scheduler.add_job(lambda: fetch_and_store_market_prices(app), 'interval', hours=6, id='market_job', replace_existing=True)
    scheduler.start()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/input', methods=['GET', 'POST'])
    def user_input():
        if request.method == 'POST':
            data = request.form
            # create Recommendation entry only after calculating
            # For simplicity we keep this form minimal
            filters = {
                'location': data.get('location') or None,
                'soil_type': data.get('soil_type') or None,
                'ph': float(data.get('ph')) if data.get('ph') else None,
            }
            recs = recommend_crops_for_input(filters, db.session, top_n=5)
            # store recommendations
            saved = []
            for r in recs:
                rec = Recommendation(crop=r['crop'], expected_roi=r.get('expected_roi'), sowing_date=r.get('sowing_date'), harvest_date=r.get('harvest_date'))
                db.session.add(rec)
                saved.append(rec)
            db.session.commit()
            return render_template('recommendation.html', recommendations=recs)
        return render_template('input_form.html')

    @app.route('/api/crops')
    def api_crops():
        # returns distinct crops available in dataset
        rows = db.session.query(CropRecord.Crop).distinct().all()
        crops = [r[0] for r in rows]
        return jsonify(crops)

    @app.route('/api/attributes')
    def api_attributes():
        rows = AttributeInfo.query.all()
        data = [{'attribute': r.Attribute, 'description': r.Full_Form___Description} for r in rows]
        return jsonify(data)

    @app.route('/dashboard')
    def dashboard():
        # prepare data for charting: avg rainfall per crop example
        q = db.session.query(CropRecord.Crop, db.func.avg(CropRecord.Rainfall).label('avg_rain'))\
              .group_by(CropRecord.Crop).limit(40).all()
        chart_data = [{'crop': row[0], 'avg_rainfall': float(row[1]) if row[1] is not None else None} for row in q]
        return render_template('dashboard.html', chart_data=chart_data)

    @app.route('/api/recommendations')
    def api_recs():
        rows = db.session.query(Recommendation).order_by(Recommendation.created_at.desc()).limit(20).all()
        out = []
        for r in rows:
            out.append({'crop': r.crop, 'expected_roi': r.expected_roi, 'sowing_date': str(r.sowing_date), 'harvest_date': str(r.harvest_date)})
        return jsonify(out)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
