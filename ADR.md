# Assignment 1
## 1. Backend language and framework
Date: 28/09
Status: Decided
Context: I needed to pick a backend framework for a small app, and I wanted something easy to work with rather than something more complex.
Decision: I used Flask as my backend framework, mainly because it's the one I know best and I found it the simplest and easiest to work with for an app like this.
Alternatives considered: I considered FastAPI because it looked interesting for its automatic input validation, but I don't have much experience with it, so I decided against it.
Consequences: I write every SQL query by hand instead of using an ORM, and I validate things like trip dates myself, which is more work, but I understand every part of the data much better.

## 2. How I decided for the two domains to be independent
Date: 03/10
Status: Decided
Context: I wanted better organization that visually separates the different activities the app performs, and makes it instantly clear to someone reading the repo where each domain's code lives.
Decision: The packing domain's routes never call the recommendation logic directly. They only read and write rows in packing_items using trip_id as the only connection point. When a trip is created, the trips domain calls the recommendation function once and inserts the results into packing_items. After that, the packing domain treats recommended and user-added items the same way, with no knowledge of how they were generated.
Alternatives considered: I thought about having the packing domain suggest quantities for new custom items based on the trip's days or climate, but I decided against it because I preferred letting the user decide the quantity themselves.
Consequences: This separation has held up well in practice as one domain only ever uses a  suggestion from the other at  time of the creation of the trip, and everything else stays fully independent. This also means the packing domain could become its own microservice later with no changes needed, since it never reaches into the trips domain's logic.

## 3. Data schema decision in SQLite
Date: 25/09
Status: Superseded by [7]
Context: I needed a schema that keeps my two feature domains separate from each other. One domain looks for information inside the climate dataset and suggests while the other domain takes that suggestion and lets the user add or delete items from it.
Decision: The first table contains the cities, and next to it the average precipitation and temperature for each month in 11 years. The trips table stores where and when a trip takes place, which is used to generate the clothing suggestion. The packing_items table uses the suggested data from a trip and lets the user add or erase items using that suggestion.
Alternatives considered: Another option would have been linking climate data to clothing types through a new dataset for the clothes. Instead, I chose to code that linking through Python, calculating quantities based on the weather and the number of days the user stays. I chose this because it gives less complexity when changing decisions about temperature, rain, or clothing rules later.
Consequences: This design makes it easier to change variables and rules later. However, some values aren't linked to real data and come back as null, in which case I skip the value instead of guessing it.

## 4. Testing approach
Date: 30/09
Status: Decided
Context: The assignment requires at least 70% coverage of the core business logic, so I had to decide where to spend the tests. Dates and clothing recommendation are where wrong answers would most likely appear, and recommending clothes for a specific trip is the core of the app.
Decision: I focused my tests on the thresholds and quantities, with assertions checking that a given temperature, rainfall amount or trip length returns the expected band, item or quantity. I also tested the month selection for trips and added route tests for the main success and error responses.
Alternatives considered: I could have tested the HTML page routes as well, but I judged them less important because any mistake there can be seen directly in the frontend and wouldn't break the core recommendation logic.
Consequences: Coverage is 83% overall. The recommendation.py  and dates.py files are at 94 and 100%  and packs/routes.py is at 96%, but trips/routes.py is the thinnest at 71%. Its untested lines are the routes I only checked by hand in the browser, such as the page and dropdown routes and the delete-trip route, plus a few error branches, and none of the frontend JavaScript is covered by automated tests. In exchange, when I change a clothing rule or a threshold, the tests show right away whether any recommendation changed.

## 5. Laundry assumption based on trip length 
Date: 28/09
Status: Decided
Context: The recommendation needs to know how many days of clothes to pack. Longer trips could assume laundry access, but that really depends on accommodation type (apartment vs hostel), not just trip length.
Decision: I assume laundry is available for any trip over 8 days, based on length alone. accommodation_type is stored in the  tripstable but not used by the recommendation algorithm.
Alternatives considered: I considered branching the laundry cap by accommodation type as for example, apartments getting a 8-day cap and hostels a longer one, since they're less likely to have a washing machine. I rejected this for v1 to keep the core algorithm and its tests simpler, at the cost of some accuracy for hostel or camping trips.
Consequences: A 12-day hostel trip is packed as if laundry exists at day 8, which may under-pack for travelers without real laundry access. 

# Assignment 2 
## 6. Splitting PackWise into two services
Date: 17/11
Status: Decided
Context: Assignment 2 requires one service per domain, each with its own database. In Assignment 1 both domains lived in one Flask app and shared one SQLite file.
Decision:+ The trips service owns trips, locations and climate_monthly, and the packs service owns packing_items, where trip_id is now a plain number with no foreign key. The only things that cross the seam are HTTP calls. Packs asks trips whether a trip exists before adding an item. If the other service does not answer, each service keeps working. The UI calls both services directly, so trips no longer returns items.
Alternatives considered: Refusing to create or delete a trip when packs is down would keep the data consistent, but it would make trips depend on packs, which is what I wanted to avoid. 
Consequences: Because there is no foreign key across the seam, a trip deleted while packs is down leaves orphaned items in packs. They are invisible to the user, and a cleanup job could remove them later. A trip created while packs is down has no packing list, and the response says that the packing list is false, but the user can regenerate the list by editing the trip once packs is back.


## 7. Moving from one SQLite file to one SQL Server database per service
Date: 24/11
Status: Decided
Context: Assignment 2 requires one database per service on SQL Server, and a schema that can change over time without losing the data already stored.
Decision: Locally, one SQL Server container holds two databases, trips and packs with one login per service. Each login can only open its own database, so trips cannot read packs's tables and the other way round. The script checks whether each database and login exists before creating it, so it is safe to run on every docker compose up. The schema is built by numbered SQL files in each service's migrations folder. A small runner applies them at start-up in number order and stores the name of each applied file in a migrations table. A migration and its record are committed together, so a failed migration is never marked as applied. 
Alternatives considered: Keeping schema.sql with CREATE TABLE IF NOT EXISTS, but that only works for new tables and cannot change a table that already has data. Using Alembic, which is more powerful but adds a tool I would have to learn and explain for only a few migrations.
Consequences: Integrity lost at the seam: the id of packing items has no foreign key to trips any more, and ON DELETE CASCADE is gone, because the two tables live in different databases. This is compensated in code, if packs is down at that moment, orphaned items can remain.  Recovery plan for a bad migration: A migration that has run anywhere shared is never edited or renamed so a mistake is fixed with a new numbered migration. If a bad migration reaches Azure, I redeploy the previous image and then ship a fix migration. Before a risky migration I can export the database with an Azure SQL backup, which serverless databases keep automatically.