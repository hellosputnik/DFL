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
    `display_name` (e.g., "Brand - Product (Modified)"),
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
    - Log the entry with the canonical `display_name` and append "(Modified)" if applicable (e.g., "Bibigo - Crunchy Chicken (Modified)"). Do not include specific modification details in the `display_name`.
    - Decrement the quantity from `data/inventory.json` by the ID. If the quantity reaches 0, remove the item from the list entirely.
    - Update or create the daily log file in `logs/` and regenerate the dashboard using `make build`.

2.  **Inventory Management**:
    - When adding to inventory, always use existing IDs from `food_database.json`.
    - If a new product arrives, add the "pure" data to the database first.

4.  **Data Consistency**:
    - All text, such as product names, brands, and ingredients, should be consistently cased. Use title case for names and sentence case for descriptions.
    - Always run `make build` after any data modification to keep the dashboard up to date.
