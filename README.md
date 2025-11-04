# CropCompass

Flask-based decision-support system for crop recommendations.

## Quick start

1. Create a virtualenv and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Place `CropCompass.xlsx` in the project root (optional). The app will import it into `cropcompass.db` if `cropcompass.db` does not exist.

3. Run:
   ```
   python app.py
   ```

4. Open http://localhost:5000


## Notes
- The recommender is a simple heuristic; swap with a data-driven model when you have enough labeled examples.
- Replace `scraper.py` with a real market data scraper (obeying ToS and robots.txt).
