## 1. Backend language and framework
Date: 28/09
Status: Decided
Context: I needed to pick a backend framework for a small app, and I wanted something easy to work with rather than something more complex.
Decision: I used Flask as my backend framework, mainly because it's the one I know best and I found it the simplest and easiest to work with for an app like this.
Alternatives considered: I considered FastAPI because it looked interesting for its automatic input validation, but I don't have much experience with it, so I decided against it.
Consequences: I write every SQL query by hand instead of using an ORM, and I validate things like trip dates myself, which is more work, but I understand every part of the data much better.

## 3. Data-model/schema decision in SQLite
Date: 25/09
Status: Decided
Context: I needed a schema that keeps my two feature domains separate from each other. One domain looks for information inside the climate dataset and suggests while the other domain takes that suggestion and lets the user add or delete items from it.
Decision: The first table contains the cities, and next to it the average precipitation and temperature for each month in 12 years. The trips table stores where and when a trip takes place, which is used to generate the clothing suggestion. The packing_items table uses the suggested data from a trip and lets the user add or erase items using that suggestion.
Alternatives considered: Another option would have been linking climate data to clothing types through a new dataset for the clothes. Instead, I chose to code that linking through Python, calculating quantities based on the weather and the number of days the user stays. I chose this because it gives less complexity when changing decisions about temperature, rain, or clothing rules later.
Consequences: This design makes it easier to change variables and rules later. However, some values aren't linked to real data and come back as null, in which case I skip the value instead of guessing it.