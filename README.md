# PackWise

PackWise suggests what to pack for a trip. You choose a destination and dates, the app looks up the typical temperature and rainfall for that city in that month, and it generates a packing list with quantities. You then manage the list: tick items off as you pack, change quantities, add your own items, or remove items.

## Features

- 100 cities, picked by country and then city
- Packing list suggested from the destination's monthly temperature and rainfall
- Preview of the list before anything is saved
- Climate summary for the trip, for example "Hot temperature" and "Moderate rain"
- Saved trips that can be edited (destination, dates) or deleted
- Checklist with packed status, quantities, custom items and a progress bar

## Requirements

Python 3 and pip. It was developed on Python 3.14.

## Setup and run

```bash
git clone <repository-url>
cd <repository-folder>
python -m venv venv
venv\Scripts\activate          # Windows PowerShell
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000/ in a browser.

The first start creates the SQLite database and loads the climate data automatically, so no manual setup or migration is needed. Starting again keeps your saved trips.

## Configuration

Everything is configured with environment variables, and all of them are optional.

| Variable | Default | Purpose |
|---|---|---|
| `PORT` | `5000` | Port the app listens on (it binds to `0.0.0.0`) |
| `DATA_DIR` | the `data` folder in the project | Folder where the SQLite file `packing.db` is created |

Example (PowerShell): `$env:PORT = "8080"; python app.py`

## Tests and coverage

```bash
pytest --cov=trips --cov=packs --cov-report=term tests/
```

Result: 34 tests passed, 83% coverage on the `trips` and `packs` packages (`trips/recommendation.py` 94%, `trips/dates.py` 100%, `packs/routes.py` 96%, `trips/routes.py` 71%).

The tests use a temporary database, so they never touch your saved trips.

## Pages

| Page | Purpose |
|---|---|
| `/` | Home page |
| `/new` | Plan a trip: choose a destination and dates, preview the list, then save |
| `/trips` | List of saved trips |
| `/trips/<id>/view` | A trip's climate summary and packing checklist |

## API

| Method and path | Purpose |
|---|---|
| `POST /trips/preview` | Suggested list and climate summary, nothing saved |
| `POST /trips` | Create a trip and save its suggested list |
| `GET /trips/<id>` | A trip and its items as JSON |
| `PUT /trips/<id>` | Edit destination or dates and regenerate the suggested items |
| `DELETE /trips/<id>` | Delete a trip and its items |
| `POST /trips/<id>/items` | Add a custom item |
| `PATCH /items/<id>` | Change `packed` and/or `quantity` |
| `DELETE /items/<id>` | Remove an item |
| `GET /api/countries`, `GET /api/cities?country=` | Values for the destination dropdowns |
| `GET /health` | Liveness check |

## How the recommendation works

1. The month used is the one with the most days in the trip (a tie goes to the earlier month).
2. The month's average temperature picks a band: freezing below 0 °C, cold below 10, cool below 17, mild up to 25, hot above 25.
3. Each band has a list of items with a rate per day and a minimum. Quantity is rate × days, rounded up, never below the minimum. Trips longer than N days are packed for N days, assuming laundry is available.
4. Rainfall above 100 mm in the month adds a raincoat and an umbrella. If a city has no rainfall data, no rain gear is added.
5. Beach items are added for coastal cities when the month is warmer than 20 °C and has at most 200 mm of rain.

## Data

- **Temperature:** Berkeley Earth, "Climate Change: Earth Surface Temperature Data" (Kaggle). Monthly averages for Jan 2003 to Aug 2013, for 100 cities.
- **Rainfall:** Wikipedia, "List of cities by average precipitation". Available for 73 of the 100 cities; the other 27 are stored as empty values instead of guesses.

## Project structure

```
app.py               Flask app: configuration, database connection, home page
database/            schema.sql and seed.py (creates and fills the database)
data/                climate_monthly.csv (the SQLite file is created here too)
trips/               trips domain: recommendation.py, dates.py, routes.py
packs/               packing checklist domain: routes.py
templates/, static/  pages and stylesheet
tests/               automated tests
ADR.md               architecture decision records
AI_USAGE.md          log of AI use
```

## Known limitations

- No user accounts; all trips are shared.
- accommodation_type is saved with a trip but does not change the recommendation.
- Climate figures are monthly averages from 2003 to 2013, not forecasts.
- A trip that spans two months uses the climate of the month with more days.