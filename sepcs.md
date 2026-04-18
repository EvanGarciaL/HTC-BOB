_“Prince Of Pieace (POP) runs an on-premises ERP (Microsoft Dynamics GP) with Cavallo SalesPad for order management, purchasing, inventory tracking, and warehouse picking. There is no cloud data warehouse, no API layer, and no demand planning software_"

_“In both cases, POP spotted the opportunity early. The gap is in the time between identification and action. POP's compliance standards are non-negotiable**, which means it needs to see trends earlier than competitors who move fast and loose.** ”_

**_Develop a solution, in any format, that helps non-technical buyers systematically spot emerging products, brands, ingredient trends, and category shifts before the market catches up. The solution should filter against POP's sourcing criteria and surface opportunities actionable for both distribution and internal product development._**

**_AI Product Discovery & Trend Intelligence Tool_**

# **_Problem Statement_**

**_Design and build a product discovery tool that helps PoP's buying team identify emerging products, ingredient trends, and category shifts before competitors, using publicly available data._**

**_The tool should go beyond generic trend reporting. It should filter against real business constraints and surface opportunities that are actionable._**

**Step by Step Outline:**

1. Scrape [Google trends](https://pypi.org/project/pytrends/), [amazon](https://pypi.org/project/python-amazon-sp-api/) (links to APIs)
   1. Scrape files, ranked based on some sort of scoring. We have to refine our scoring as we go, but can start with a very basic algorithm:
      1. “_Identify trending products, ingredients, or categories in food, beverage, wellness, or personal care_”. What constitutes as trending? How can we filter products/ingredients/categories against constraints? (FDA, Tariffs, shelf life).
      2. How do we **score** opportunities/trends?
2. Implement filtering criteria
   1. Filter out products under 12+ months shelf life AND products on FDA restriction lists AND products that are highly tariffed
      1. We need to figure out what is considered a high tariff  
         2. We need to compile a list of ingredients, additives, imports that the FDA restricts
3. Once scoring and ranking is done, categorize “new trends” based on PoP’s categorization standards
4. Feed that data into our frontend interface (react).
5. **Steps 1-4 we need to prioritize**
6. Once we finish the basic tool, we can keep refining the ranking/scoring algorithm and also the interface

# **Suggested Approach**

Instead of trying to build a complete platform, focus on a clear pipeline:

- **Data Collection:** Pick 2-3 public data sources and pull relevant signals (trending search terms, bestseller movement, new product listings, social media mentions)

- **Scoring & Ranking:** Define a simple scoring model. What makes a trend signal strong vs. weak? Recency, growth rate, category relevance, and competition level are good starting factors.

- **Filtering:** Apply PoP's sourcing constraints (shelf life, FDA, tariff) to eliminate non-viable opportunities before they reach the buyer.

- **Presentation:** Build a simple interface or report that shows top recommendations with context: what the trend is, why it's relevant to PoP, and what action the buyer should consider.

A focused prototype covering one product category well is better than a broad but shallow scan across everything.