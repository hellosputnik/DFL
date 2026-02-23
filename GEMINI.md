# Food Log & Inventory Manager

This project tracks daily food consumption, nutritional macros, and current food inventory to provide suggestions based on available stock.

## Data Structure

### `data/food_database.json`
A dictionary of "pure" official food items mirroring full nutrition labels.
- `key`: Unique ID (e.g., `brand_product_flavor`)
- `value`: {
    "brand",
    "product_name",
    "flavor",
    "calories_kcal",
    "protein_g",
    "carbohydrate_g",
    "fat_g",
    "total_fat_g",
    "saturated_fat_g",
    "trans_fat_g",
    "cholesterol_mg",
    "sodium_mg",
    "dietary_fiber_g",
    "total_sugars_g",
    "added_sugars_g",
    "vitamin_d_mcg",
    "calcium_mg",
    "iron_mg",
    "potassium_mg",
    "serving_size",
    "serving_unit",
    "servings_per_container",
    "total_weight_oz",
    "ingredients": []
  }

### `data/inventory.json`
A list of items currently on hand, linked by ID.
- `id`: Unique ID from database
- `quantity`: Amount remaining
- `unit`: Measurement unit

### `logs/YYYY-MM-DD.json`
Daily consumption records.
- `entries`: List of {
    `id`,
    `display_name` (can include modification notes like "1/2 sauce"),
    `amount`,
    `calories_kcal`,
    `protein_g`,
    `carbohydrate_g`,
    `fat_g`
  }
- `totals`: { `calories_kcal`, `protein_g`, `carbohydrate_g`, `fat_g` }

## Instructions for Gemini CLI

1.  **Logging Food**:
    - When I eat something, check `data/food_database.json` by ID or attributes.
    - If I am modifying the item (e.g., "half sauce"), calculate the new macros based on the "pure" database entry and my description.
    - Log the entry with a descriptive `display_name` (e.g., "Bibigo - Crunchy Chicken (1/2 Sauce)").
    - Decrement the quantity from `data/inventory.json` by the ID.
    - Update or create the daily log file in `logs/` and regenerate the dashboard using `generate_dashboard.py`.

2.  **Inventory Management**:
    - When adding to inventory, always use existing IDs from `food_database.json`.
    - If a new product arrives, add the "pure" data to the database first.

3.  **Dashboards**:
    - Always run `python3 generate_dashboard.py` after any data modification to keep `dashboard.html` up to date.
