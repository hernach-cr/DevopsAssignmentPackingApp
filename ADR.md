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
Status: Decided
Context: I needed a schema that keeps my two feature domains separate from each other. One domain looks for information inside the climate dataset and suggests while the other domain takes that suggestion and lets the user add or delete items from it.
Decision: The first table contains the cities, and next to it the average precipitation and temperature for each month in 12 years. The trips table stores where and when a trip takes place, which is used to generate the clothing suggestion. The packing_items table uses the suggested data from a trip and lets the user add or erase items using that suggestion.
Alternatives considered: Another option would have been linking climate data to clothing types through a new dataset for the clothes. Instead, I chose to code that linking through Python, calculating quantities based on the weather and the number of days the user stays. I chose this because it gives less complexity when changing decisions about temperature, rain, or clothing rules later.
Consequences: This design makes it easier to change variables and rules later. However, some values aren't linked to real data and come back as null, in which case I skip the value instead of guessing it.

## 5. Laundry assumption based on trip length 
Date: 28/09
Status: Decided
Context: The recommendation needs to know how many days of clothes to pack. Longer trips could assume laundry access, but that really depends on accommodation type (apartment vs hostel), not just trip length.
Decision: I assume laundry is available for any trip over 7 days, based on length alone. accommodation_type is stored in the  tripstable but not used by the recommendation algorithm.
Alternatives considered: I considered branching the laundry cap by accommodation type as for example, apartments getting a 7-day cap and hostels a longer one, since they're less likely to have a washing machine. I rejected this for v1 to keep the core algorithm and its tests simpler, at the cost of some accuracy for hostel or camping trips.
Consequences: A 12-day hostel trip is packed as if laundry exists at day 7, which may under-pack for travelers without real laundry access. 