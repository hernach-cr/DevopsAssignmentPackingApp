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







