# AI Usage Log: PackWise

| Date | Tool | Prompt | Disposition | What changed & why | In my own words |
|---|---|---|---|---|---|
| 2026-09-25 | Claude | Asked for help finding a global city-temperature dataset the recommendation system could use to suggest clothes from monthly temperature averages | Accepted | Used Berkeley Earth GlobalLandTemperaturesByCity (Kaggle) |The source has a temperature for every city and month. I kept January 2003 to August 2013 because it's the most recent period with complete data . For each city I average each calendar month over those years. |


| 2026-09-25 | Claude | Asked for a precipitation dataset to add a second climate variable | Modified | The first attempt included invented values for cities missing. |I Asked for a precipitation dataset to add a second climate variable, this one connected directly to 73 out 100 cities leaving the other ones as None |

| 2026-09-25 | Claude  | Asked for help with the SQLite schema | Modified | Made packing_items depend only on trip_id, so the two domains stay separate | locations and climate_monthly are fixed reference data, trips point to a location, and packing_items point to a trip.  |

| 2026-09-25 | Claude  | Asked for help with seed.py to connect the database with the backend | Accepted | database/seed.py loads the CSV into locations and climate_monthly | seed.py runs schema.sql, reads the CSV row by row, inserts each city once with its 12 monthly rows, and skips everything if climate_monthly already has rows, so restarting never duplicates data. |

| 2026-09-25 | Claude | Asked for help with the Flask app skeleton | Accepted | app.py with a health route and per-request database connection | app.py reads PORT from the environment, listens on 0.0.0.0, seeds the database at startup, and opens one database connection per request that is closed afterwards. |


| 2026-09-28 | Claude  | Asked how to add the quantity of clothes per number of days | Modified | I gave my own ratios (for example 2 jackets per 4 days) and they were converted into per_day rates. | item_quantity multiplies per_day by the trip days, rounds up, and never goes below the minimum. effective_days stops counting after the laundry threshold, so long trips don't need more clothes. |

| 2026-09-28 | Claude | Asked for the cities with a coast nearby so I could add beach clothes and materials | Modified | I decided which cities count as coastal (excluded New York and Istanbul, included Rome and Bilbao) and set the beach rule to warmer than 20 C and at most 200 mm of rain | wants_beach_items needs a coastal city, a temperature above 20 and rain not above 200 mm. If rain is None it still passes, because missing data should not remove items. |


| 2026-09-30 | Claude  | Asked for a way to choose which month's climate to use when a trip spans two months | Modified | I chose the month with the most trip days. I | dominant_month counts the trip days in each month and returns the month with the highest count. A tie goes to the earlier month. generate_packing_list then looks up that month's climate and calls recommend_clothing. |

| 2026-09-30 | Claude  | Asked for help writing tests and test fixtures | Modified | Fixed my own wrong assertions and added an in-memory database fixture and a temporary-database client fixture | test_db builds the real schema in memory. |

| 2026-10-01 | Claude  | Asked for help with  the trip routes | Accepted | trips/routes.py with a Blueprint | POST /trips validates the dates and city, calls generate_packing_list, then saves the trip and its items as recommended. GET /trips/id returns the trip and its items. |


| 2026-10-03 | Claude  | Asked for the frontend, | Modified | I asked for country first and then city, date pickers that limit each other, a preview before saving, deleting trips, and editing on the trip page instead of a separate page | The preview calls /trips/preview, which saves nothing. Save trip then calls POST /trips. Editing replaces the recommended items but keeps custom items and packed status. |

| 2026-10-04 | Claude  | Asked for a cleaner design, larger titles and the display of the avg temperature and precipitation | Modified | Iterated on the look and layout | get_trip_climate reads the month's average temperature and rainfall and turns them into labels, shown on the preview and on the saved trip. |

| 2026-09-28 to 2026-10-04 | Claude  | Asked for help structuring my ADR entries | Modified | I answered the questions in my own words and Claude mapped them into the six-field format and pointed out statements that did not match the code | The decisions and reasons in the ADRs are mine. Claude only fitted them into the required format. |









# ASSIGNMENT 2 AI Usage Log
| 2026-11-16 | Claude | Asked which endpoints packs should offer so trips can stop using the shared table, with skeletons for them | Modified | Wrote GET and DELETE items from the skeletons and added PUT|

| 2026-11-16 | Claude | Asked for the current_app library | Modified | adding the current_app library, it’s Flask’s way of saying “the app that is running right now”. Your routes live in a blueprint, not in app.py, so they can’t use app directly. current_app gives them access to it, and .logger is its built-in logger.|

| 2026-11-17 | Claude | Asked for a skeleton of trips_client.trip_exists with three outcomes | Accepted | Packs checks the trip over HTTP; if trips is down the item is still added and a warning is logged |

| 2026-11-17 | Claude | Asked how to allow the UI to call both services (CORS) | Accepted | Added flask-cors to both services, allowing only the UI origin from the UI_ORIGIN env var |

| 2026-11-17 | Claude | Asked how to turn the Jinja templates into a static UI| Modified | Moved templates to ui folder, removed all Jinja, filled the skeletons, fixed fetch URLs to use CONFIG.TRIPS_URL / CONFIG.PACKS_URL, removed render_template from trips | 

| 2026-11-18 | Claude | Asked why the unit tests failed after the split | Accepted | Added pytest.ini per service so tests find each service's modules
 | ... |
| 2026-11-18 | Claude | Asked how to test one service without calling the other | Accepted | conftest.py replaces packs_client / trips_client with fakes that record calls which makes tests no longer depend on the other service running | ... |

| 2026-11-18 | Claude | Asked how to rewrite the tests that broke after the split| Modified | Moved the keep custom items and keep ticks tests from trips to packs, wrote new packs tests from skeletons, added trips tests for packs being down, delete and climate | ... |

| 2026-11-18 | Claude | Asked why requirements.txt showed as binary in Git | Accepted | Re-saved both files as UTF-8 instead of UTF-16 so pip and Git read them as text | ... |

| 2026-11-19 | Claude | Asked how to write integration tests across the two services; got the first test complete and left the rest to build them by my own | Modified | tests/integration calls the real services over HTTP | ... |

| 2026-11-19 | Claude | Asked for a Dockerfile per service based on the class slides | Modified | My first version had several WORKDIRs, wrong COPY paths and inline comments used the corrected version | ... |

| 2026-11-19 | Claude | Asked for a docker-compose.yml for trips, packs and the UI | Modified | Filled in PACKS_URL / TRIPS_URL with service names | ... |

| 2026-11-20 | Claude | Asked how to add SQL Server to Docker Compose and keep the passwords out of Git | Accepted | Added the sqlserver service with a healthcheck | ... |

| 2026-11-20 | Claude | Asked for db/init.sql and a db-init job that create one database and one login per service | Accepted | init.sql creates trips and packs databases and logins only if missing so db-init waits for SQL Server to be healthy, runs the script and exits | ... |

| 2026-11-20 | Claude | Asked how to connect Flask to SQL Server without rewriting every route and got the Db wrapper and get_db | Accepted | Db wraps a pymssql connection so routes keep using db.execute(...).fetchone() | ... |

| 2026-11-20 | Claude | Asked for a migration runner and help translating schema.sql into 001_init.sql | Modified | I translated the packs and trips schemas to SQL Server types with a mapping table; used the given migrate.py with connection retries and a schema_migrations table | ... |

| 2026-11-24 | Claude | Asked how to run the unit tests on SQL Server; got new conftest.py files | Accepted | Tests create packs_test / trips_test, run the real migrations once, empty the tables before each test; Madrid's June set to the values the tests expect | ... |

| 2026-11-24 | Claude | Asked for failed tested problem | Accepted | lastrowid returns a Decimal in pymssql, so IDs became text in JSON; wrapped it in int(); renamed the fake test city so it doesn't clash with real data | ... |

| 2026-11-26 | Claude | Asked for the OpenAPI documents of both services | Modified | Claude generated both from my routes; I checked them against the code and added country to the City schema after calling /api/cities | ... |

| 2026-11-26 | Claude | Asked for system.yaml following the provided system.schema.json | Accepted | Values taken from my code (env defaults, calls, timeouts) | ... |

| 2026-11-26 | Claude | Asked for a CI yml | Accepted | ci.yml with validate, test ( flake8, pytest, coverage ≥70%) and integration (build all images, start the stack, integration tests) and throwing away passwords per run | ... |

| 2026-11-26 | Claude | Asked how to fix the flake8 errors from the first CI run | Modified | Ran autopep8 for whitespace Eto deliberate late imports, removed an unused import and deleted a duplicated generate_packing_list after comparing both versions | ... |
