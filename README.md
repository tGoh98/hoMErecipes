# Home Recipes

Since the COVID-19 pandemic began, the real risk of encountering coronavirus in public areas such as stores means it’s often best to avoid grocery shopping unless it’s absolutely necessary, especially for elderly or otherwise immunocompromised individuals. Home Recipes was created to help you find recipes for the ingredients you already have at home so that you can push off that grocery store trip a little bit longer while still making delicious food.
[(presentation and demo link ADD THIS)](https://www.youtube.com)
 
## Features
* Uses Google Vision API's Optical Character Recognition to parse a menu
* Filters results based on user preferences (budget, dietary. restrictions, etc)
* Collects reviews from multiple services, including Google Reviews and Yelp, to create an accurate prediction of the best dishes at a resteraunt.
* Factors in a user's previous Yelp reviews to help predict which menu items would be most appealing to them
* Creates a personalized account tied to a user's Yelp account to help learn a user's preferenences.
* Pulls food items from online libraries and dictionaries to give a full featured prediction of a user's tastes.
* Uses simplified relational calculus to calculate a score for each individual menu item.

## How to run
1. Obtain and set up API key from [spoonacular](https://spoonacular.com/food-api)
2. Install neccesary dependencies with ```pip install -r requirements.txt```
3. Start the server with ```python3 main.py```

## Team
Home Recipes was created by Timothy Goh (tGoh98), Michael Sprintson (michaelsprintson), Camsy Huang, and Christina Zhou for UTSA's hackathon, RowdyHack. Read more about it in the [Devpost](https://devpost.com/software/me-nu).
