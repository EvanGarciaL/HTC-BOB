"""
temporary_demo_data.py: Rich Local Trend Dataset

Provides a large offline dataset that looks similar to the Google and Amazon
records used elsewhere in the project. The records are regenerated with light
per-run variation so the local UI feels closer to a live market feed.
"""

from __future__ import annotations

import hashlib
import time

from food_terms import (
    ADDITIVE_TERMS,
    DISCOVERY_SEED_KEYWORDS,
    FOOD_TERMS,
    INGREDIENT_TERMS,
    PRODUCT_FORMAT_TERMS,
)


BASE_TEMPORARY_GOOGLE_TRENDS_RECORDS = [
    {
        "query": "matcha gummies",
        "source_seed": "matcha",
        "intent_bucket": "eat_or_buy",
        "trend_type": "ingredient",
        "market_signal": "commercial_demand",
        "popularity_score": 87,
        "search_growth": 240,
        "trend_velocity": 91.5,
        "opportunity_score": 107.1,
    },
    {
        "query": "prebiotic soda",
        "source_seed": "prebiotic soda",
        "intent_bucket": "eat_or_buy",
        "trend_type": "product_format",
        "market_signal": "commercial_demand",
        "popularity_score": 93,
        "search_growth": 320,
        "trend_velocity": 100.0,
        "opportunity_score": 115.8,
    },
    {
        "query": "sea moss drink",
        "source_seed": "sea moss drink",
        "intent_bucket": "learn",
        "trend_type": "ingredient",
        "market_signal": "consumer_education",
        "popularity_score": 72,
        "search_growth": 210,
        "trend_velocity": 65.6,
        "opportunity_score": 65.36,
    },
    {
        "query": "protein pudding",
        "source_seed": "protein shake",
        "intent_bucket": "eat_or_buy",
        "trend_type": "product_format",
        "market_signal": "commercial_demand",
        "popularity_score": 69,
        "search_growth": 180,
        "trend_velocity": 56.2,
        "opportunity_score": 75.12,
    },
    {
        "query": "hot honey snack",
        "source_seed": "hot honey snack",
        "intent_bucket": "eat_or_buy",
        "trend_type": "ingredient",
        "market_signal": "commercial_demand",
        "popularity_score": 76,
        "search_growth": 195,
        "trend_velocity": 60.9,
        "opportunity_score": 82.14,
    },
    {
        "query": "vinegar drink",
        "source_seed": "vinegar drink",
        "intent_bucket": "learn",
        "trend_type": "ingredient",
        "market_signal": "consumer_education",
        "popularity_score": 58,
        "search_growth": 165,
        "trend_velocity": 51.5,
        "opportunity_score": 51.06,
    },
]

BASE_TEMPORARY_GOOGLE_TRENDS_RECORDS += [
    {"query": "hot cheetos", "source_seed": "snack", "intent_bucket": "eat_or_buy", "trend_type": "product_or_query", "market_signal": "commercial_demand", "popularity_score": 88, "search_growth": 205, "trend_velocity": 78.8, "opportunity_score": 97.3},
    {"query": "cottage cheese ice cream", "source_seed": "dessert", "intent_bucket": "make_at_home", "trend_type": "product_format", "market_signal": "at_home_creation", "popularity_score": 81, "search_growth": 290, "trend_velocity": 84.4, "opportunity_score": 91.7},
    {"query": "protein ramen", "source_seed": "protein shake", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 74, "search_growth": 215, "trend_velocity": 72.5, "opportunity_score": 85.1},
    {"query": "freeze dried candy", "source_seed": "freeze dried candy", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 90, "search_growth": 340, "trend_velocity": 96.1, "opportunity_score": 112.5},
    {"query": "corn ribs", "source_seed": "recipe", "intent_bucket": "make_at_home", "trend_type": "ingredient", "market_signal": "at_home_creation", "popularity_score": 68, "search_growth": 185, "trend_velocity": 63.8, "opportunity_score": 70.2},
    {"query": "broccoli salad", "source_seed": "healthy snack", "intent_bucket": "learn", "trend_type": "ingredient", "market_signal": "consumer_education", "popularity_score": 62, "search_growth": 150, "trend_velocity": 58.3, "opportunity_score": 57.1},
    {"query": "chili crisp noodles", "source_seed": "chili crisp", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 84, "search_growth": 255, "trend_velocity": 87.4, "opportunity_score": 101.8},
    {"query": "sea moss gummies", "source_seed": "sea moss drink", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 79, "search_growth": 220, "trend_velocity": 74.6, "opportunity_score": 89.4},
    {"query": "electrolyte popsicles", "source_seed": "electrolyte drink", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 71, "search_growth": 198, "trend_velocity": 69.8, "opportunity_score": 81.5},
    {"query": "mushroom coffee", "source_seed": "mushroom coffee", "intent_bucket": "learn", "trend_type": "ingredient", "market_signal": "consumer_education", "popularity_score": 86, "search_growth": 260, "trend_velocity": 82.1, "opportunity_score": 88.7},
    {"query": "matcha coconut water", "source_seed": "matcha", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 77, "search_growth": 206, "trend_velocity": 76.4, "opportunity_score": 90.5},
    {"query": "korean pear soda", "source_seed": "drink", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 67, "search_growth": 182, "trend_velocity": 64.7, "opportunity_score": 77.2},
    {"query": "ube mochi cookies", "source_seed": "cookies", "intent_bucket": "eat_or_buy", "trend_type": "product_or_query", "market_signal": "commercial_demand", "popularity_score": 82, "search_growth": 248, "trend_velocity": 79.3, "opportunity_score": 95.8},
    {"query": "pickle lemonade", "source_seed": "drink", "intent_bucket": "learn", "trend_type": "ingredient", "market_signal": "consumer_education", "popularity_score": 64, "search_growth": 210, "trend_velocity": 67.2, "opportunity_score": 62.4},
    {"query": "pistachio cream cereal bar", "source_seed": "cereal bar", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 72, "search_growth": 195, "trend_velocity": 70.1, "opportunity_score": 83.8},
    {"query": "sweet potato chips", "source_seed": "cassava chips", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 75, "search_growth": 168, "trend_velocity": 66.5, "opportunity_score": 81.0},
    {"query": "date caramel", "source_seed": "dessert", "intent_bucket": "learn", "trend_type": "ingredient", "market_signal": "consumer_education", "popularity_score": 73, "search_growth": 235, "trend_velocity": 74.4, "opportunity_score": 71.6},
    {"query": "protein cereal", "source_seed": "protein snack", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 70, "search_growth": 190, "trend_velocity": 68.2, "opportunity_score": 80.7},
    {"query": "olive oil gummies", "source_seed": "olive oil", "intent_bucket": "learn", "trend_type": "ingredient", "market_signal": "consumer_education", "popularity_score": 59, "search_growth": 175, "trend_velocity": 55.9, "opportunity_score": 55.3},
    {"query": "hibiscus cherry soda", "source_seed": "prebiotic soda", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 76, "search_growth": 214, "trend_velocity": 73.4, "opportunity_score": 88.1},
    {"query": "high fiber cereal", "source_seed": "healthy snack", "intent_bucket": "learn", "trend_type": "product_format", "market_signal": "consumer_education", "popularity_score": 78, "search_growth": 228, "trend_velocity": 75.5, "opportunity_score": 74.9},
    {"query": "corn silk tea", "source_seed": "tea", "intent_bucket": "learn", "trend_type": "ingredient", "market_signal": "consumer_education", "popularity_score": 61, "search_growth": 170, "trend_velocity": 59.6, "opportunity_score": 57.8},
    {"query": "tallow popcorn", "source_seed": "tallow", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 69, "search_growth": 188, "trend_velocity": 68.9, "opportunity_score": 80.4},
    {"query": "spicy mango gummies", "source_seed": "candy", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 74, "search_growth": 222, "trend_velocity": 77.0, "opportunity_score": 89.2},
    {"query": "blue spirulina gummies", "source_seed": "superfood powder", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 71, "search_growth": 203, "trend_velocity": 71.4, "opportunity_score": 84.9},
    {"query": "pineapple kimchi salsa", "source_seed": "kimchi", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 65, "search_growth": 174, "trend_velocity": 62.7, "opportunity_score": 76.5},
    {"query": "broccoli chips", "source_seed": "snack", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 60, "search_growth": 149, "trend_velocity": 56.8, "opportunity_score": 69.1},
    {"query": "takis popcorn", "source_seed": "snack", "intent_bucket": "eat_or_buy", "trend_type": "product_or_query", "market_signal": "commercial_demand", "popularity_score": 83, "search_growth": 238, "trend_velocity": 81.9, "opportunity_score": 97.6},
    {"query": "rose lychee drink", "source_seed": "drink", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 68, "search_growth": 177, "trend_velocity": 65.1, "opportunity_score": 78.8},
    {"query": "yuzu gummies", "source_seed": "yuzu", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 72, "search_growth": 207, "trend_velocity": 74.0, "opportunity_score": 87.4},
    {"query": "cereal milk latte", "source_seed": "latte", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 66, "search_growth": 181, "trend_velocity": 64.0, "opportunity_score": 77.0},
    {"query": "jalapeno pineapple hot sauce", "source_seed": "hot sauce", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 70, "search_growth": 198, "trend_velocity": 72.8, "opportunity_score": 85.6},
    {"query": "kale chips", "source_seed": "healthy snack", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 63, "search_growth": 152, "trend_velocity": 58.8, "opportunity_score": 70.8},
    {"query": "street corn dip", "source_seed": "salsa", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 67, "search_growth": 192, "trend_velocity": 69.7, "opportunity_score": 82.6},
    {"query": "corn broth", "source_seed": "miso soup", "intent_bucket": "learn", "trend_type": "ingredient", "market_signal": "consumer_education", "popularity_score": 55, "search_growth": 132, "trend_velocity": 50.4, "opportunity_score": 49.5},
    {"query": "cheese puffs", "source_seed": "snack", "intent_bucket": "eat_or_buy", "trend_type": "product_or_query", "market_signal": "commercial_demand", "popularity_score": 79, "search_growth": 176, "trend_velocity": 71.3, "opportunity_score": 86.9},
    {"query": "watermelon tajin jerky", "source_seed": "fruit snack", "intent_bucket": "eat_or_buy", "trend_type": "product_or_query", "market_signal": "commercial_demand", "popularity_score": 64, "search_growth": 183, "trend_velocity": 68.0, "opportunity_score": 79.3},
    {"query": "kimchi mayo dip", "source_seed": "kimchi", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 62, "search_growth": 170, "trend_velocity": 63.1, "opportunity_score": 75.1},
    {"query": "spinach lemonade", "source_seed": "green juice", "intent_bucket": "learn", "trend_type": "ingredient", "market_signal": "consumer_education", "popularity_score": 52, "search_growth": 138, "trend_velocity": 48.7, "opportunity_score": 47.3},
    {"query": "horchata cold brew", "source_seed": "cold brew", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 77, "search_growth": 225, "trend_velocity": 76.8, "opportunity_score": 91.2},
    {"query": "chamoy gummies", "source_seed": "candy", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 81, "search_growth": 252, "trend_velocity": 84.0, "opportunity_score": 100.6},
    {"query": "beef tallow chips", "source_seed": "beef tallow", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 73, "search_growth": 211, "trend_velocity": 73.6, "opportunity_score": 87.0},
    {"query": "sparkling coconut yogurt drink", "source_seed": "yogurt drink", "intent_bucket": "eat_or_buy", "trend_type": "product_format", "market_signal": "commercial_demand", "popularity_score": 66, "search_growth": 176, "trend_velocity": 66.4, "opportunity_score": 79.4},
    {"query": "broccoli cheddar bites", "source_seed": "healthy snack", "intent_bucket": "eat_or_buy", "trend_type": "ingredient", "market_signal": "commercial_demand", "popularity_score": 59, "search_growth": 141, "trend_velocity": 54.6, "opportunity_score": 66.8},
    {"query": "pickle popcorn", "source_seed": "snack", "intent_bucket": "eat_or_buy", "trend_type": "product_or_query", "market_signal": "commercial_demand", "popularity_score": 68, "search_growth": 201, "trend_velocity": 72.3, "opportunity_score": 84.8},
]


BASE_TEMPORARY_AMAZON_TRENDS_RECORDS = [
    {
        "query": "matcha gummies",
        "source_seed": "matcha gummies",
        "amazon_market_signal": "emerging_opportunity",
        "amazon_popularity_score": 640.0,
        "amazon_trend_velocity": 84.2,
        "amazon_opportunity_score": 80.1,
        "avg_price": 18.99,
        "food_relevant": True,
    },
    {
        "query": "prebiotic soda",
        "source_seed": "prebiotic soda",
        "amazon_market_signal": "established_market",
        "amazon_popularity_score": 4200.0,
        "amazon_trend_velocity": 88.7,
        "amazon_opportunity_score": 62.4,
        "avg_price": 26.5,
        "food_relevant": True,
    },
    {
        "query": "protein pudding",
        "source_seed": "protein pudding",
        "amazon_market_signal": "emerging_opportunity",
        "amazon_popularity_score": 510.0,
        "amazon_trend_velocity": 81.3,
        "amazon_opportunity_score": 78.6,
        "avg_price": 14.75,
        "food_relevant": True,
    },
    {
        "query": "hot honey snack",
        "source_seed": "hot honey snack",
        "amazon_market_signal": "niche_market",
        "amazon_popularity_score": 290.0,
        "amazon_trend_velocity": 57.8,
        "amazon_opportunity_score": 61.9,
        "avg_price": 11.4,
        "food_relevant": True,
    },
]

BASE_TEMPORARY_AMAZON_TRENDS_RECORDS += [
    {"query": "sea moss drink", "source_seed": "sea moss drink", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 820.0, "amazon_trend_velocity": 74.4, "amazon_opportunity_score": 73.2, "avg_price": 19.99, "food_relevant": True},
    {"query": "vinegar drink", "source_seed": "vinegar drink", "amazon_market_signal": "niche_market", "amazon_popularity_score": 930.0, "amazon_trend_velocity": 62.8, "amazon_opportunity_score": 58.1, "avg_price": 17.49, "food_relevant": True},
    {"query": "hot cheetos", "source_seed": "hot cheetos", "amazon_market_signal": "established_market", "amazon_popularity_score": 6700.0, "amazon_trend_velocity": 83.0, "amazon_opportunity_score": 64.8, "avg_price": 8.99, "food_relevant": True},
    {"query": "cottage cheese ice cream", "source_seed": "cottage cheese ice cream", "amazon_market_signal": "niche_market", "amazon_popularity_score": 340.0, "amazon_trend_velocity": 58.5, "amazon_opportunity_score": 63.0, "avg_price": 15.99, "food_relevant": True},
    {"query": "protein ramen", "source_seed": "protein ramen", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 540.0, "amazon_trend_velocity": 79.6, "amazon_opportunity_score": 78.1, "avg_price": 21.99, "food_relevant": True},
    {"query": "freeze dried candy", "source_seed": "freeze dried candy", "amazon_market_signal": "established_market", "amazon_popularity_score": 3750.0, "amazon_trend_velocity": 91.5, "amazon_opportunity_score": 70.4, "avg_price": 13.99, "food_relevant": True},
    {"query": "corn ribs", "source_seed": "corn ribs", "amazon_market_signal": "niche_market", "amazon_popularity_score": 260.0, "amazon_trend_velocity": 44.2, "amazon_opportunity_score": 49.6, "avg_price": 12.49, "food_relevant": True},
    {"query": "broccoli salad", "source_seed": "broccoli salad", "amazon_market_signal": "niche_market", "amazon_popularity_score": 220.0, "amazon_trend_velocity": 41.8, "amazon_opportunity_score": 47.1, "avg_price": 9.99, "food_relevant": True},
    {"query": "chili crisp noodles", "source_seed": "chili crisp noodles", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 980.0, "amazon_trend_velocity": 82.4, "amazon_opportunity_score": 79.8, "avg_price": 16.99, "food_relevant": True},
    {"query": "sea moss gummies", "source_seed": "sea moss gummies", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 1160.0, "amazon_trend_velocity": 76.2, "amazon_opportunity_score": 75.4, "avg_price": 22.99, "food_relevant": True},
    {"query": "electrolyte popsicles", "source_seed": "electrolyte popsicles", "amazon_market_signal": "established_market", "amazon_popularity_score": 890.0, "amazon_trend_velocity": 73.5, "amazon_opportunity_score": 74.7, "avg_price": 18.49, "food_relevant": True},
    {"query": "mushroom coffee", "source_seed": "mushroom coffee", "amazon_market_signal": "established_market", "amazon_popularity_score": 3100.0, "amazon_trend_velocity": 86.8, "amazon_opportunity_score": 68.5, "avg_price": 24.99, "food_relevant": True},
    {"query": "matcha coconut water", "source_seed": "matcha coconut water", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 610.0, "amazon_trend_velocity": 77.1, "amazon_opportunity_score": 76.0, "avg_price": 19.49, "food_relevant": True},
    {"query": "korean pear soda", "source_seed": "korean pear soda", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 1440.0, "amazon_trend_velocity": 71.0, "amazon_opportunity_score": 67.8, "avg_price": 14.99, "food_relevant": True},
    {"query": "ube mochi cookies", "source_seed": "ube mochi cookies", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 430.0, "amazon_trend_velocity": 69.8, "amazon_opportunity_score": 70.9, "avg_price": 17.25, "food_relevant": True},
    {"query": "pickle lemonade", "source_seed": "pickle lemonade", "amazon_market_signal": "niche_market", "amazon_popularity_score": 305.0, "amazon_trend_velocity": 48.6, "amazon_opportunity_score": 52.0, "avg_price": 15.99, "food_relevant": True},
    {"query": "pistachio cream cereal bar", "source_seed": "pistachio cream cereal bar", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 450.0, "amazon_trend_velocity": 66.2, "amazon_opportunity_score": 69.1, "avg_price": 18.75, "food_relevant": True},
    {"query": "sweet potato chips", "source_seed": "sweet potato chips", "amazon_market_signal": "established_market", "amazon_popularity_score": 2380.0, "amazon_trend_velocity": 72.2, "amazon_opportunity_score": 63.7, "avg_price": 10.49, "food_relevant": True},
    {"query": "date caramel", "source_seed": "date caramel", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 510.0, "amazon_trend_velocity": 72.9, "amazon_opportunity_score": 73.5, "avg_price": 16.29, "food_relevant": True},
    {"query": "protein cereal", "source_seed": "protein cereal", "amazon_market_signal": "established_market", "amazon_popularity_score": 2050.0, "amazon_trend_velocity": 80.6, "amazon_opportunity_score": 67.4, "avg_price": 14.95, "food_relevant": True},
    {"query": "olive oil gummies", "source_seed": "olive oil gummies", "amazon_market_signal": "niche_market", "amazon_popularity_score": 210.0, "amazon_trend_velocity": 39.5, "amazon_opportunity_score": 44.8, "avg_price": 23.99, "food_relevant": True},
    {"query": "hibiscus cherry soda", "source_seed": "hibiscus cherry soda", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 590.0, "amazon_trend_velocity": 74.1, "amazon_opportunity_score": 74.6, "avg_price": 21.5, "food_relevant": True},
    {"query": "high fiber cereal", "source_seed": "high fiber cereal", "amazon_market_signal": "established_market", "amazon_popularity_score": 1780.0, "amazon_trend_velocity": 69.4, "amazon_opportunity_score": 62.1, "avg_price": 12.99, "food_relevant": True},
    {"query": "corn silk tea", "source_seed": "corn silk tea", "amazon_market_signal": "niche_market", "amazon_popularity_score": 330.0, "amazon_trend_velocity": 50.4, "amazon_opportunity_score": 54.3, "avg_price": 11.99, "food_relevant": True},
    {"query": "tallow popcorn", "source_seed": "tallow popcorn", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 420.0, "amazon_trend_velocity": 62.7, "amazon_opportunity_score": 65.5, "avg_price": 9.49, "food_relevant": True},
    {"query": "spicy mango gummies", "source_seed": "spicy mango gummies", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 470.0, "amazon_trend_velocity": 68.7, "amazon_opportunity_score": 71.1, "avg_price": 13.99, "food_relevant": True},
    {"query": "blue spirulina gummies", "source_seed": "blue spirulina gummies", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 350.0, "amazon_trend_velocity": 59.8, "amazon_opportunity_score": 62.8, "avg_price": 20.99, "food_relevant": True},
    {"query": "pineapple kimchi salsa", "source_seed": "pineapple kimchi salsa", "amazon_market_signal": "niche_market", "amazon_popularity_score": 240.0, "amazon_trend_velocity": 47.2, "amazon_opportunity_score": 50.1, "avg_price": 12.79, "food_relevant": True},
    {"query": "broccoli chips", "source_seed": "broccoli chips", "amazon_market_signal": "niche_market", "amazon_popularity_score": 310.0, "amazon_trend_velocity": 51.1, "amazon_opportunity_score": 54.7, "avg_price": 8.99, "food_relevant": True},
    {"query": "takis popcorn", "source_seed": "takis popcorn", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 560.0, "amazon_trend_velocity": 71.3, "amazon_opportunity_score": 73.0, "avg_price": 10.99, "food_relevant": True},
    {"query": "rose lychee drink", "source_seed": "rose lychee drink", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 480.0, "amazon_trend_velocity": 63.7, "amazon_opportunity_score": 66.9, "avg_price": 16.49, "food_relevant": True},
    {"query": "yuzu gummies", "source_seed": "yuzu gummies", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 520.0, "amazon_trend_velocity": 72.5, "amazon_opportunity_score": 74.1, "avg_price": 17.99, "food_relevant": True},
    {"query": "cereal milk latte", "source_seed": "cereal milk latte", "amazon_market_signal": "niche_market", "amazon_popularity_score": 290.0, "amazon_trend_velocity": 53.9, "amazon_opportunity_score": 56.2, "avg_price": 18.99, "food_relevant": True},
    {"query": "jalapeno pineapple hot sauce", "source_seed": "jalapeno pineapple hot sauce", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 620.0, "amazon_trend_velocity": 70.8, "amazon_opportunity_score": 72.9, "avg_price": 12.99, "food_relevant": True},
    {"query": "kale chips", "source_seed": "kale chips", "amazon_market_signal": "established_market", "amazon_popularity_score": 1260.0, "amazon_trend_velocity": 61.2, "amazon_opportunity_score": 58.4, "avg_price": 9.79, "food_relevant": True},
    {"query": "street corn dip", "source_seed": "street corn dip", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 410.0, "amazon_trend_velocity": 60.4, "amazon_opportunity_score": 63.6, "avg_price": 13.49, "food_relevant": True},
    {"query": "corn broth", "source_seed": "corn broth", "amazon_market_signal": "niche_market", "amazon_popularity_score": 190.0, "amazon_trend_velocity": 36.6, "amazon_opportunity_score": 40.8, "avg_price": 14.25, "food_relevant": True},
    {"query": "cheese puffs", "source_seed": "cheese puffs", "amazon_market_signal": "established_market", "amazon_popularity_score": 3120.0, "amazon_trend_velocity": 75.8, "amazon_opportunity_score": 65.0, "avg_price": 7.99, "food_relevant": True},
    {"query": "watermelon tajin jerky", "source_seed": "watermelon tajin jerky", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 360.0, "amazon_trend_velocity": 55.7, "amazon_opportunity_score": 59.2, "avg_price": 14.49, "food_relevant": True},
    {"query": "kimchi mayo dip", "source_seed": "kimchi mayo dip", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 275.0, "amazon_trend_velocity": 52.1, "amazon_opportunity_score": 56.5, "avg_price": 11.99, "food_relevant": True},
    {"query": "spinach lemonade", "source_seed": "spinach lemonade", "amazon_market_signal": "niche_market", "amazon_popularity_score": 180.0, "amazon_trend_velocity": 33.8, "amazon_opportunity_score": 38.6, "avg_price": 13.99, "food_relevant": True},
    {"query": "horchata cold brew", "source_seed": "horchata cold brew", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 970.0, "amazon_trend_velocity": 78.3, "amazon_opportunity_score": 77.9, "avg_price": 19.99, "food_relevant": True},
    {"query": "chamoy gummies", "source_seed": "chamoy gummies", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 680.0, "amazon_trend_velocity": 80.4, "amazon_opportunity_score": 79.3, "avg_price": 14.99, "food_relevant": True},
    {"query": "beef tallow chips", "source_seed": "beef tallow chips", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 390.0, "amazon_trend_velocity": 61.8, "amazon_opportunity_score": 64.9, "avg_price": 9.99, "food_relevant": True},
    {"query": "sparkling coconut yogurt drink", "source_seed": "sparkling coconut yogurt drink", "amazon_market_signal": "niche_market", "amazon_popularity_score": 215.0, "amazon_trend_velocity": 45.8, "amazon_opportunity_score": 49.9, "avg_price": 17.99, "food_relevant": True},
    {"query": "broccoli cheddar bites", "source_seed": "broccoli cheddar bites", "amazon_market_signal": "niche_market", "amazon_popularity_score": 245.0, "amazon_trend_velocity": 46.9, "amazon_opportunity_score": 50.7, "avg_price": 10.49, "food_relevant": True},
    {"query": "pickle popcorn", "source_seed": "pickle popcorn", "amazon_market_signal": "emerging_opportunity", "amazon_popularity_score": 520.0, "amazon_trend_velocity": 69.1, "amazon_opportunity_score": 71.0, "avg_price": 8.99, "food_relevant": True},
]


EXTRA_TEMPORARY_TREND_TERMS = [
    "adaptogen soda",
    "aero honey candy",
    "agave lime candy",
    "aji amarillo sauce",
    "algae chips",
    "almond croissant latte",
    "aloe vera jelly drink",
    "amaro soda",
    "anchovy butter crackers",
    "apple cider vinegar gummies",
    "apple tahini snack bites",
    "arepa chips",
    "ashwagandha latte mix",
    "avocado lime crema dip",
    "banana matcha pudding",
    "bbq seaweed snack",
    "beef tallow chips",
    "beet electrolyte powder",
    "berbere trail mix",
    "birria ramen kit",
    "black sesame latte",
    "blood orange soda",
    "blue spirulina gummies",
    "bone broth ramen cup",
    "brown butter cookie dough",
    "buchu botanical soda",
    "calamansi beverage",
    "candy grape gummies",
    "canned ube latte",
    "carrot cake protein bites",
    "cashew queso dip",
    "caviar chips",
    "ceremonial matcha sticks",
    "chai protein shake",
    "chamoy gummies",
    "charcoal lemonade",
    "cherry blossom soda",
    "chili crisp cashews",
    "chili crunch noodles",
    "chili oil dumplings",
    "chili tamarind bites",
    "chipotle lime popcorn",
    "chive cottage cheese dip",
    "chocho protein bar",
    "churro granola",
    "cinnamon date bark",
    "citrus collagen water",
    "coconut cloud yogurt",
    "coconut water gummies",
    "cold foam protein latte",
    "cold pressed soup",
    "congee cup",
    "corn rib seasoning",
    "corn silk tea",
    "cottage cheese ice cream",
    "cracker crust snack bites",
    "cranberry hibiscus tonic",
    "creamy jalapeno sauce",
    "crispy rice salad kit",
    "crunchy mochi bites",
    "cucumber chili salad kit",
    "dalgona protein shake",
    "dashi popcorn",
    "date caramel clusters",
    "date syrup soda",
    "dragon fruit refresher",
    "drinking broth shot",
    "dulce de leche protein bar",
    "elderflower tonic water",
    "electrolyte freeze pops",
    "elote seasoning blend",
    "espresso cherry gummies",
    "falafel chips",
    "fermented blueberry soda",
    "fermented lemon soda",
    "fiber mocktail mixer",
    "fig tahini bar",
    "fire cider tonic",
    "fish sauce caramel popcorn",
    "flamin hot pickles",
    "floral hydration powder",
    "focaccia chips",
    "freeze dried mochi",
    "freeze dried yogurt bites",
    "fried pickle ranch snack mix",
    "frozen kimbap bowl",
    "frozen soup dumplings",
    "fruit vinegar soda",
    "garlic confit butter sauce",
    "ginger lime hydration sticks",
    "glow greens lemonade",
    "gochugaru almonds",
    "golden milk gummies",
    "grape aloe drink",
    "green mango candy",
    "guava cream cheese pastry",
    "gut health lemonade",
    "harissa honey trail mix",
    "haskap berry gummies",
    "hibiscus cherry soda",
    "high fiber instant oatmeal",
    "high protein cereal milk",
    "honey butter chips",
    "horchata cold brew",
    "hot honey pretzel pieces",
    "iced hojicha latte",
    "instant boba kit",
    "jalapeno pineapple hot sauce",
    "jelly coffee pouch",
    "jerk plantain chips",
    "kabosu sparkling drink",
    "kimchi mayo dip",
    "korean pear soda",
    "korean yogurt smoothie",
    "kosho vinaigrette",
    "labneh dip snack pack",
    "lavender lemon water",
    "lemon olive oil snack cake",
    "lion's mane cacao mix",
    "mango chili fruit leather",
    "maple sea salt granola butter",
    "matcha coconut water",
    "melon soda gummies",
    "microgreen salad topper",
    "milky oolong tea",
    "miso caramel candy",
    "miso soup paste sticks",
    "mole popcorn",
    "mushroom jerky chips",
    "mushroom mocha latte",
    "mushroom soda",
    "nata de coco drink",
    "natto snack bites",
    "nori popcorn seasoning",
    "oat milk matcha shake",
    "olive oil gummies",
    "orange cream protein shake",
    "pandan coconut latte",
    "passion fruit electrolytes",
    "peach chamomile soda",
    "peanut butter mochi",
    "pear cardamom soda",
    "pickle ketchup",
    "pickle lemonade",
    "pickle popcorn",
    "pineapple chili soda",
    "pineapple kimchi salsa",
    "pistachio cream cereal bar",
    "plant based bone broth",
    "plum sparkling water",
    "pocket charcuterie snack",
    "pomelo soda",
    "popping boba lemonade",
    "potato milk latte",
    "prebiotic fruit leather",
    "prebiotic jelly drink",
    "protein cold brew concentrate",
    "protein frosting dip",
    "protein oatmeal cups",
    "protein pancake cereal",
    "protein ramen",
    "protein soft serve mix",
    "ramen chips",
    "raspberry vinegar soda",
    "red bean energy bites",
    "reishi cola",
    "rice paper chips",
    "rose lychee drink",
    "rosemary grapefruit soda",
    "salted egg chips",
    "savory granola clusters",
    "sea moss fruit snacks",
    "seaweed rice crisps",
    "sesame cold foam latte",
    "shiso sparkling water",
    "shrimp chip seasoning",
    "skyr protein pudding",
    "sleeve tea concentrate",
    "smoked pineapple salsa",
    "snickerdoodle protein bites",
    "sour plum soda",
    "sparkling coconut yogurt drink",
    "spicy maple jerky",
    "spicy mango gummies",
    "spicy pickle cashews",
    "spirulina lemonade",
    "sriracha honey almonds",
    "strawberry matcha cream soda",
    "street corn dip",
    "sumac pita chips",
    "sunbutter snack bites",
    "superseed chocolate bark",
    "sweet corn latte",
    "sweet potato mochi waffles",
    "swicy bbq sauce",
    "tajin fruit leather",
    "tallow popcorn",
    "tamari almonds",
    "tangerine probiotic soda",
    "taro milk tea gummies",
    "tea soda",
    "teff granola",
    "toasted rice tea",
    "tom yum snack mix",
    "ube brownie brittle",
    "ube cream soda",
    "ube mochi cookies",
    "vanilla sea moss pudding",
    "vinegar spritz",
    "watermelon tajin jerky",
    "wellness broth concentrate",
    "white peach yogurt drink",
    "wild blueberry matcha",
    "yogurt bark clusters",
    "yogurt soda",
    "yuzu gummies",
    "yuzu honey tea concentrate",
    "zaatar pita crackers",
    "zero sugar boba soda",
]


INTENT_PATTERNS = {
    "make_at_home": ["recipe", "diy", "homemade", "kit", "starter", "copycat"],
    "learn": ["benefits", "what is", "nutrition", "healthy", "wellness", "gut health"],
    "eat_or_buy": [
        "bar",
        "bites",
        "bowl",
        "broth",
        "candy",
        "chips",
        "cookie",
        "dip",
        "drink",
        "gummies",
        "jerky",
        "latte",
        "mix",
        "powder",
        "pudding",
        "sauce",
        "shake",
        "shot",
        "snack",
        "soda",
        "tea",
        "water",
        "yogurt",
    ],
}

RUN_SEED = str(time.time_ns())


def normalize_term(term):
    return " ".join(str(term).strip().lower().split())


def _stable_bucket(label, low, high):
    digest = hashlib.sha256(f"{RUN_SEED}:{label}".encode("utf-8")).hexdigest()
    span = high - low + 1
    return low + (int(digest[:8], 16) % span)


def _stable_float(label, low, high, precision=1):
    scaled = _stable_bucket(label, int(low * 10**precision), int(high * 10**precision))
    return round(scaled / (10**precision), precision)


def _stable_rank(label):
    return _stable_bucket(f"rank:{label}", 0, 1_000_000)


def detect_intent(term):
    lowered = normalize_term(term)
    for intent, patterns in INTENT_PATTERNS.items():
        if any(pattern in lowered for pattern in patterns):
            return intent
    return "general_interest"


def detect_trend_type(term):
    lowered = normalize_term(term)
    if any(keyword in lowered for keyword in INGREDIENT_TERMS):
        return "ingredient"
    if any(keyword in lowered for keyword in PRODUCT_FORMAT_TERMS):
        return "product_format"
    if any(keyword in lowered for keyword in ADDITIVE_TERMS):
        return "additive"
    return "product_or_query"


def detect_market_signal(intent):
    if intent == "eat_or_buy":
        return "commercial_demand"
    if intent == "make_at_home":
        return "at_home_creation"
    if intent == "learn":
        return "consumer_education"
    return "emerging_interest"


def detect_amazon_market_signal(term):
    lowered = normalize_term(term)
    if any(keyword in lowered for keyword in ["prebiotic", "protein", "probiotic", "electrolyte"]):
        return "established_market"
    if any(keyword in lowered for keyword in ["matcha", "mushroom", "sea moss", "yuzu", "ube"]):
        return "emerging_opportunity"
    return "niche_market"


def pick_source_seed(term):
    lowered = normalize_term(term)
    for seed in sorted(DISCOVERY_SEED_KEYWORDS, key=len, reverse=True):
        normalized_seed = normalize_term(seed)
        if normalized_seed in lowered or lowered in normalized_seed:
            return seed
    return term


def build_keyword_pool():
    raw_terms = (
        DISCOVERY_SEED_KEYWORDS
        + FOOD_TERMS
        + INGREDIENT_TERMS
        + ADDITIVE_TERMS
        + PRODUCT_FORMAT_TERMS
        + EXTRA_TEMPORARY_TREND_TERMS
    )
    unique_terms = list(dict.fromkeys(normalize_term(term) for term in raw_terms if term))
    base_queries = {
        normalize_term(record["query"]) for record in BASE_TEMPORARY_GOOGLE_TRENDS_RECORDS
    } | {
        normalize_term(record["query"]) for record in BASE_TEMPORARY_AMAZON_TRENDS_RECORDS
    }

    def sort_key(term):
        ingredient_bonus = any(keyword in term for keyword in INGREDIENT_TERMS)
        format_bonus = any(keyword in term for keyword in PRODUCT_FORMAT_TERMS)
        additive_penalty = any(keyword in term for keyword in ADDITIVE_TERMS)
        trendy_bonus = any(
            keyword in term
            for keyword in [
                "adaptogen",
                "cold brew",
                "electrolyte",
                "fiber",
                "freeze dried",
                "gut health",
                "hot honey",
                "matcha",
                "mushroom",
                "prebiotic",
                "protein",
                "sea moss",
                "soda",
                "sparkling",
                "ube",
                "vinegar",
                "wellness",
                "yuzu",
            ]
        )
        words = len(term.split())
        return (
            term not in base_queries,
            _stable_bucket(f"pool:{term}", 0, 1),
            trendy_bonus,
            ingredient_bonus,
            format_bonus,
            not additive_penalty,
            words,
            len(term),
            term,
        )

    return sorted(unique_terms, key=sort_key, reverse=True)


def _build_generated_google_record(index, term):
    intent_bucket = detect_intent(term)
    trend_type = detect_trend_type(term)
    market_signal = detect_market_signal(intent_bucket)
    popularity_score = max(22, 98 - ((index * 2) % 55) + _stable_bucket(f"google-pop:{term}", -8, 8))
    search_growth = max(55, 430 - (index % 80) * 4 + _stable_bucket(f"google-growth:{term}", -45, 85))
    trend_velocity = round(
        max(18.0, 94.0 - ((index % 70) * 0.95) + _stable_float(f"google-velocity:{term}", -8.0, 9.0)),
        1,
    )
    opportunity_score = round(
        (
            (popularity_score * 0.42)
            + (trend_velocity * 0.38)
            + (min(search_growth, 300) * 0.08)
        )
        * {
            "eat_or_buy": 1.08,
            "make_at_home": 0.97,
            "learn": 0.94,
            "general_interest": 1.0,
        }.get(intent_bucket, 1.0),
        2,
    )

    return {
        "query": term,
        "source_seed": pick_source_seed(term),
        "intent_bucket": intent_bucket,
        "trend_type": trend_type,
        "market_signal": market_signal,
        "popularity_score": min(popularity_score, 100),
        "search_growth": search_growth,
        "trend_velocity": trend_velocity,
        "opportunity_score": opportunity_score,
    }


def _build_generated_amazon_record(index, term):
    amazon_popularity_score = round(
        max(120.0, 4800.0 - ((index % 120) * 31.5) + _stable_float(f"amazon-pop:{term}", -220.0, 260.0)),
        1,
    )
    amazon_trend_velocity = round(
        max(16.0, 89.0 - ((index % 90) * 0.72) + _stable_float(f"amazon-velocity:{term}", -10.0, 11.0)),
        1,
    )
    amazon_opportunity_score = round(
        max(
            26.0,
            (amazon_trend_velocity * 0.72)
            + (_stable_float(f"amazon-opportunity:{term}", 6.0, 26.0)),
        ),
        2,
    )

    return {
        "query": term,
        "source_seed": term,
        "amazon_market_signal": detect_amazon_market_signal(term),
        "amazon_popularity_score": amazon_popularity_score,
        "amazon_trend_velocity": amazon_trend_velocity,
        "amazon_opportunity_score": amazon_opportunity_score,
        "avg_price": round(_stable_float(f"amazon-price:{term}", 4.99, 32.99, precision=2), 2),
        "food_relevant": True,
    }


def _randomize_google_record(record):
    term = normalize_term(record["query"])
    popularity_score = max(
        18,
        min(100, int(round(record["popularity_score"] + _stable_float(f"base-google-pop:{term}", -14.0, 14.0)))),
    )
    search_growth = max(
        45,
        int(round(record["search_growth"] + _stable_float(f"base-google-growth:{term}", -80.0, 135.0))),
    )
    trend_velocity = round(
        max(16.0, min(100.0, record["trend_velocity"] + _stable_float(f"base-google-velocity:{term}", -12.0, 12.0))),
        1,
    )
    intent_weight = {
        "eat_or_buy": 1.08,
        "make_at_home": 0.97,
        "learn": 0.94,
        "general_interest": 1.0,
    }.get(record["intent_bucket"], 1.0)
    market_momentum = _stable_float(f"base-google-momentum:{term}", 0.0, 12.0)
    opportunity_score = round(
        (
            (popularity_score * 0.43)
            + (trend_velocity * 0.37)
            + (min(search_growth, 320) * 0.085)
            + market_momentum
        )
        * intent_weight,
        2,
    )
    randomized = dict(record)
    randomized.update(
        {
            "popularity_score": popularity_score,
            "search_growth": search_growth,
            "trend_velocity": trend_velocity,
            "opportunity_score": opportunity_score,
        }
    )
    return randomized


def _randomize_amazon_record(record):
    term = normalize_term(record["query"])
    amazon_popularity_score = round(
        max(
            90.0,
            record["amazon_popularity_score"] + _stable_float(f"base-amazon-pop:{term}", -900.0, 1200.0),
        ),
        1,
    )
    amazon_trend_velocity = round(
        max(
            14.0,
            min(100.0, record["amazon_trend_velocity"] + _stable_float(f"base-amazon-velocity:{term}", -14.0, 14.0)),
        ),
        1,
    )
    amazon_opportunity_score = round(
        max(
            24.0,
            (amazon_trend_velocity * 0.72)
            + _stable_float(f"base-amazon-opportunity:{term}", 8.0, 28.0),
        ),
        2,
    )
    avg_price = round(
        max(3.99, record["avg_price"] + _stable_float(f"base-amazon-price:{term}", -3.25, 4.75, precision=2)),
        2,
    )
    randomized = dict(record)
    randomized.update(
        {
            "amazon_popularity_score": amazon_popularity_score,
            "amazon_trend_velocity": amazon_trend_velocity,
            "amazon_opportunity_score": amazon_opportunity_score,
            "avg_price": avg_price,
        }
    )
    return randomized


KEYWORD_POOL = build_keyword_pool()
GENERATED_KEYWORD_POOL = KEYWORD_POOL[:420]

GOOGLE_BASE_QUERIES = {normalize_term(record["query"]) for record in BASE_TEMPORARY_GOOGLE_TRENDS_RECORDS}
AMAZON_BASE_QUERIES = {normalize_term(record["query"]) for record in BASE_TEMPORARY_AMAZON_TRENDS_RECORDS}

TEMPORARY_GOOGLE_TRENDS_RECORDS = sorted(
    [_randomize_google_record(record) for record in BASE_TEMPORARY_GOOGLE_TRENDS_RECORDS]
    + [
        _build_generated_google_record(index, term)
        for index, term in enumerate(GENERATED_KEYWORD_POOL)
        if term not in GOOGLE_BASE_QUERIES
    ],
    key=lambda record: (
        record["opportunity_score"],
        record["trend_velocity"],
        _stable_rank(record["query"]),
    ),
    reverse=True,
)

TEMPORARY_AMAZON_TRENDS_RECORDS = sorted(
    [_randomize_amazon_record(record) for record in BASE_TEMPORARY_AMAZON_TRENDS_RECORDS]
    + [
        _build_generated_amazon_record(index, term)
        for index, term in enumerate(GENERATED_KEYWORD_POOL)
        if term not in AMAZON_BASE_QUERIES
    ],
    key=lambda record: (
        record["amazon_opportunity_score"],
        record["amazon_trend_velocity"],
        _stable_rank(record["query"]),
    ),
    reverse=True,
)
