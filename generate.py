import datetime
import glob
import json
import os
import re
import shutil
import time

import click


def format_title(text: str) -> str:
    if not text:
        return ""
    lower_words = {
        "a",
        "an",
        "the",
        "and",
        "but",
        "for",
        "or",
        "nor",
        "so",
        "yet",
        "as",
        "at",
        "by",
        "in",
        "of",
        "on",
        "to",
        "up",
        "with",
        "from",
        "into",
        "onto",
        "upon",
        "via",
        "mid",
    }
    upper_acronyms = {
        "bbq",
        "blt",
        "usda",
        "gmo",
        "msg",
        "pb&j",
        "bpa",
        "id",
        "p/c/f",
        "usa",
    }
    units = {"oz", "fl", "ml", "g", "mg", "kcal"}
    words = str(text).split()
    if not words:
        return ""
    formatted_words = []
    for index, word in enumerate(words):
        stripped = re.sub(r"^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$", "", word)
        clean = stripped.lower()
        if "-" in stripped:
            parts = stripped.split("-")
            formatted_parts = [part.capitalize() for part in parts]
            formatted_main = "-".join(formatted_parts)
            result = word.replace(stripped, formatted_main)
        elif clean in upper_acronyms:
            result = word.replace(stripped, stripped.upper())
        elif clean in units:
            result = word.replace(stripped, clean)
        elif index == 0 or index == len(words) - 1:
            result = word.replace(stripped, stripped.capitalize())
        elif clean in lower_words:
            result = word.replace(stripped, clean)
        else:
            result = word.replace(stripped, stripped.capitalize())
        formatted_words.append(result)
    return " ".join(formatted_words)


def get_shared_head(title: str) -> str:
    return f"""
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        :root {{
            --primary: #2563eb; --bg: #f8fafc; --card: #ffffff; --text: #1e293b;
            --success: #10b981; --warning: #f59e0b; --danger: #ef4444; --muted: #64748b; --border: #e2e8f0;
        }}
        body.dark-mode {{
            --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --muted: #94a3b8; --border: #334155;
        }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); line-height: 1.5; margin: 0; padding: 2rem; transition: background 0.3s, color 0.3s; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{ margin-bottom: 2rem; display: flex; justify-content: space-between; align-items: center; }}
        h1, h2 {{ color: var(--text); margin: 0; }}
        h2 {{ margin-top: 2rem; margin-bottom: 1rem; }}
        .nav-link {{ color: var(--primary); text-decoration: none; font-weight: 600; font-size: 0.875rem; }}
        .nav-link:hover {{ text-decoration: underline; }}
        
        .theme-toggle {{
            background: none; border: 1px solid var(--border); padding: 0.5rem; border-radius: 8px; cursor: pointer; color: var(--muted);
            display: flex; align-items: center; justify-content: center; transition: all 0.2s;
        }}
        .theme-toggle:hover {{ background: var(--border); color: var(--primary); }}
        .theme-toggle svg {{ width: 18px; height: 18px; }}
        .sun-icon {{ display: none; }}
        .dark-mode .sun-icon {{ display: block; }}
        .dark-mode .moon-icon {{ display: none; }}

        table {{ width: 100%; border-collapse: collapse; background: var(--card); border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: background 0.3s; border: 1px solid var(--border); }}
        th, td {{ padding: 1rem; text-align: left; border-bottom: 1px solid var(--border); }}
        th {{ background: #f1f5f9; font-weight: 600; font-size: 0.875rem; color: #475569; }}
        body.dark-mode th {{ background: #1e293b; color: #cbd5e1; border-bottom: 2px solid var(--primary); }}
        .text-center {{ text-align: center; }}
        .badge {{ display: inline-block; padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600; background: #f1f5f9; color: #475569; }}
        body.dark-mode .badge {{ background: var(--bg); color: var(--muted); }}
        .tag-modified {{ display: inline-block; padding: 0.15rem 0.4rem; border-radius: 4px; font-size: 0.65rem; font-weight: 700; text-transform: uppercase; background: #f0f9ff; color: #0369a1; margin-left: 0.5rem; vertical-align: middle; border: 1px solid #e0f2fe; }}
        .dark-mode .tag-modified {{ background: #0c4a6e; color: #7dd3fc; border-color: #0ea5e9; }}
    </style>
    <script>
        if (localStorage.getItem('theme') === 'dark') {{
            document.documentElement.classList.add('dark-mode');
            document.addEventListener('DOMContentLoaded', () => {{
                document.body.classList.add('dark-mode');
            }});
        }}
        function toggleTheme() {{
            const isDark = document.body.classList.toggle('dark-mode');
            document.documentElement.classList.toggle('dark-mode', isDark);
            localStorage.setItem('theme', isDark ? 'dark' : 'light');
        }}
    </script>
    """


def get_theme_toggle_html() -> str:
    return """
    <button onclick="toggleTheme()" class="theme-toggle" title="Toggle Dark Mode">
        <svg class="moon-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
        <svg class="sun-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" /></svg>
    </button>
    """


def get_log_path(base_dir: str, date_str: str, create_dirs: bool = False) -> str:
    """Constructs the path to a log file, sharded by year and month."""
    try:
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        year, month = str(date_obj.year), f"{date_obj.month:02d}"
        log_dir = os.path.join(base_dir, year, month)
        if create_dirs:
            os.makedirs(log_dir, exist_ok=True)
        return os.path.join(log_dir, f"{date_str}.json")
    except ValueError:
        # Fallback for non-date strings or different formats if any
        return os.path.join(base_dir, f"{date_str}.json")


def run_dashboard_generation(date_str: str = None, output_directory: str = ".") -> None:
    try:
        with open("data/goals.json", "r") as goals_file:
            goals = json.load(goals_file)
        with open("data/inventory.json", "r") as inventory_file:
            inventory = json.load(inventory_file)
        with open("data/food_database.json", "r") as database_file:
            database = json.load(database_file)
    except FileNotFoundError as error:
        click.echo(f"Error: Missing data file - {error}")
        return

    os.environ["TZ"] = os.environ.get("TZ", "America/Los_Angeles")
    time.tzset()
    target_date = date_str if date_str else datetime.datetime.now().strftime("%Y-%m-%d")
    log_path = get_log_path("logs", target_date)
    daily_log = (
        json.load(open(log_path, "r"))
        if os.path.exists(log_path)
        else {
            "entries": [],
            "totals": {
                "calories_kcal": 0,
                "protein_g": 0,
                "carbohydrate_g": 0,
                "fat_g": 0,
            },
        }
    )
    totals = daily_log["totals"]

    def get_percent(current: float, goal: float) -> int:
        return min(100, int((current / goal) * 100)) if goal and goal > 0 else 0

    def get_goal_value(value: float) -> str:
        return str(value) if value > 0 else ""

    inventory_rows_html = ""
    # Create a list of pairs (database_entry, inventory_item) for sorting
    inventory_to_display = []
    for inventory_item in inventory:
        database_entry = database.get(inventory_item["id"])
        if not database_entry:
            for database_id, database_value in database.items():
                if inventory_item["id"] in database_id:
                    database_entry = database_value
                    break
        if database_entry:
            inventory_to_display.append((database_entry, inventory_item))

    # Sort by protein (high to low), then calories (high to low), then product name
    inventory_to_display.sort(
        key=lambda pair: (
            -pair[0].get("protein_g", 0),
            -pair[0].get("calories_kcal", 0),
            pair[0].get("product_name", "").lower(),
        )
    )

    for database_entry, inventory_item in inventory_to_display:
        protein, carbohydrate, fat, calories = (
            database_entry.get("protein_g", 0),
            database_entry.get("carbohydrate_g", 0),
            database_entry.get("fat_g", 0),
            database_entry.get("calories_kcal", 0),
        )
        product = format_title(database_entry.get("product_name", ""))
        if database_entry.get("flavor"):
            product += f" ({format_title(database_entry['flavor'])})"
        inventory_rows_html += f"""
            <tr class='inventory-row' data-calories='{calories}' data-protein='{protein}' data-carbohydrate='{carbohydrate}' data-fat='{fat}' onclick='toggleProjection(this)' style='cursor: pointer;'>
                <td class='text-center'><span class='badge'>{database_entry.get('brand')}</span></td>
                <td style='font-weight: 500;'>{product}</td>
                <td class='text-center'>{inventory_item['quantity']}</td>
                <td class='text-center'>{calories}</td>
                <td class='text-center'>{protein}g / {carbohydrate}g / {fat}g</td>
            </tr>"""

    log_rows_html = ""
    if not daily_log["entries"]:
        log_rows_html = "<tr><td colspan='6' style='text-align:center; padding: 2rem; color: #94a3b8;'>No food logged yet today.</td></tr>"
    else:
        for entry in daily_log["entries"]:
            database_entry = database.get(entry.get("id"), {})
            brand = database_entry.get("brand", "N/A")
            product = format_title(
                database_entry.get("product_name", entry["display_name"])
            )
            if database_entry.get("flavor"):
                product += f" ({format_title(database_entry['flavor'])})"
            product_html = f"<span style='font-weight: 500;'>{product}</span>"
            if "(Modified)" in entry.get("display_name", ""):
                product_html += "<span class='tag-modified'>Modified</span>"
            log_rows_html += f"<tr><td class='text-center'><span class='badge'>{brand}</span></td><td>{product_html}</td><td class='text-center'>{entry['calories_kcal']}</td><td class='text-center'>{entry['protein_g']}g</td><td class='text-center'>{entry['carbohydrate_g']}g</td><td class='text-center'>{entry['fat_g']}g</td></tr>"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    {get_shared_head(f"Food Log Dashboard - {target_date}")}
    <style>
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1.5rem; margin-bottom: 2rem; }}
        .card {{ background: var(--card); padding: 1.25rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); display: flex; flex-direction: column; gap: 0.1rem; transition: background 0.3s; }}
        .stat-label {{ font-size: 0.7rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.2rem; }}
        .stat-val {{ font-size: 1.75rem; font-weight: 800; color: var(--text); line-height: 1.1; }}
        .goal-display-container {{ color: var(--muted); font-weight: 700; font-size: 1.1rem; display: flex; align-items: center; margin: 0.4rem 0; min-height: 1.5rem; }}
        .progress-bg {{ background: var(--border); height: 6px; border-radius: 3px; overflow: hidden; margin-top: 0.2rem; }}
        .progress-fill {{ background: var(--primary); height: 100%; transition: width 0.3s ease, background 0.3s ease; }}
        .tooltip {{ visibility: hidden; width: 130px; background-color: #1e293b; color: #fff; text-align: left; border-radius: 6px; padding: 8px 10px; position: absolute; z-index: 10; bottom: 140%; right: 0; opacity: 0; transition: opacity 0.2s; font-size: 0.7rem; text-transform: none; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); pointer-events: none; }}
        .info-icon:hover .tooltip {{ visibility: visible; opacity: 1; }}
        input[type=number]::-webkit-inner-spin-button {{ -webkit-appearance: none; margin: 0; }}
        .editable-goal {{ border: 1px solid transparent; background: transparent; color: inherit; font: inherit; width: 100%; padding: 0; margin: 0; text-align: left; cursor: pointer; }}
        .editable-goal:hover {{ color: var(--primary); }}
        .editable-goal:focus {{ border-bottom: 1px solid var(--primary); outline: none; cursor: text; color: var(--text); }}
        tr.selected {{ background: #bfdbfe !important; }}
        body.dark-mode tr.selected {{ background: #1e40af !important; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div><h1>Daily Food Log</h1><p style="color: var(--muted); margin-top: 0.25rem; font-weight: 500;">{target_date}</p></div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <a href="history.html" class="nav-link" style="color: var(--muted)">View History</a>
                <a href="food_database.html" class="nav-link">View Food Database →</a>
                {get_theme_toggle_html()}
            </div>
        </header>

        <div class="grid">
            <div class="card" id="card-calories">
                <div class="stat-label">Calories <div class="info-icon" style="cursor:help; position:relative; display:inline-flex; align-items:center;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg><div class="tooltip" id="calories-tooltip">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>Phase</span> <b style="text-transform: capitalize;">{goals.get('phase', 'cut')}</b></div>
                    <div style="display: flex; justify-content: space-between;"><span>Goal</span> <b>{goals['calories_target']}</b></div>
                    <div style="display: flex; justify-content: space-between;"><span>Maintenance</span> <b>{goals['calories_maintenance']}</b></div>
                </div></div></div>
                <div class="stat-val"><span class="current">{totals['calories_kcal']}</span></div>
                <div class="goal-display-container"><input type="number" class="editable-goal" id="goal-calories-input" data-mode="{goals.get('phase', 'cut')}" value="{goals['calories_target']}" placeholder="N/A" oninput="updateProjection()"></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {get_percent(totals['calories_kcal'], goals['calories_target'])}%"></div></div>
            </div>
            <div class="card" id="card-protein">
                <div class="stat-label">Protein</div>
                <div class="stat-val"><span class="current">{totals['protein_g']}g</span></div>
                <div class="goal-display-container"><input type="number" class="editable-goal" id="goal-protein-input" value="{goals['protein_g']}" placeholder="N/A" oninput="updateProjection()"></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {get_percent(totals['protein_g'], goals['protein_g'])}%"></div></div>
            </div>
            <div class="card" id="card-carbohydrate">
                <div class="stat-label">Carbohydrate</div>
                <div class="stat-val"><span class="current">{totals['carbohydrate_g']}g</span></div>
                <div class="goal-display-container"><input type="number" class="editable-goal" id="goal-carbohydrate-input" value="{get_goal_value(goals.get('carbohydrate_g', 0))}" placeholder="N/A" oninput="updateProjection()"></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {get_percent(totals['carbohydrate_g'], goals.get('carbohydrate_g', 0))}%"></div></div>
            </div>
            <div class="card" id="card-fat">
                <div class="stat-label">Fat</div>
                <div class="stat-val"><span class="current">{totals['fat_g']}g</span></div>
                <div class="goal-display-container"><input type="number" class="editable-goal" id="goal-fat-input" value="{get_goal_value(goals.get('fat_g', 0))}" placeholder="N/A" oninput="updateProjection()"></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {get_percent(totals['fat_g'], goals.get('fat_g', 0))}%"></div></div>
            </div>
        </div>

        <section><h2>Today's Log</h2><table id="log-table"><thead><tr><th class="text-center">Brand</th><th>Product</th><th class="text-center">Calories</th><th class="text-center">Protein</th><th class="text-center">Carbohydrate</th><th class="text-center">Fat</th></tr></thead><tbody>{log_rows_html}</tbody></table></section>
        <section style="margin-top: 2rem;"><h2>Current Inventory</h2><table id="inventory-table"><thead><tr><th class='text-center'>Brand</th><th>Product</th><th class='text-center'>Qty</th><th class='text-center'>Calories</th><th class='text-center'>Macros (P / C / F)</th></tr></thead><tbody>{inventory_rows_html}</tbody></table></section>
    </div>

    <script>
        const currentTotals = {{ calories: {totals['calories_kcal']}, protein: {totals['protein_g']}, carbohydrate: {totals['carbohydrate_g']}, fat: {totals['fat_g']} }};
        const maintenanceCalories = {goals['calories_maintenance']};

        function toggleProjection(row) {{
            row.classList.toggle('selected');
            updateProjection();
        }}

        function updateProjection() {{
            const goals = {{
                target: parseFloat(document.getElementById('goal-calories-input').value) || 0,
                protein: parseFloat(document.getElementById('goal-protein-input').value) || 0,
                carbohydrate: parseFloat(document.getElementById('goal-carbohydrate-input').value) || 0,
                fat: parseFloat(document.getElementById('goal-fat-input').value) || 0
            }};
            let projectedCalories = 0, projectedProtein = 0, projectedCarbohydrate = 0, projectedFat = 0;
            document.querySelectorAll('.inventory-row.selected').forEach(row => {{
                projectedCalories += parseFloat(row.dataset.calories);
                projectedProtein += parseFloat(row.dataset.protein);
                projectedCarbohydrate += parseFloat(row.dataset.carbohydrate);
                projectedFat += parseFloat(row.dataset.fat);
            }});
            updateCardCalories(currentTotals.calories + projectedCalories, projectedCalories, goals.target, maintenanceCalories);
            updateCardMacro('protein', currentTotals.protein + projectedProtein, projectedProtein, goals.protein, 'g', false);
            updateCardMacro('carbohydrate', currentTotals.carbohydrate + projectedCarbohydrate, projectedCarbohydrate, goals.carbohydrate, 'g', true);
            updateCardMacro('fat', currentTotals.fat + projectedFat, projectedFat, goals.fat, 'g', true);
        }}

        function updateCardCalories(total, projected, target, maintenance) {{
            const card = document.getElementById('card-calories');
            const span = card.querySelector('.current');
            const fill = card.querySelector('.progress-fill');
            const mode = document.getElementById('goal-calories-input').dataset.mode;
            
            span.textContent = total;
            let color = '';

            if (mode === 'bulk') {{
                if (total < maintenance) color = 'var(--danger)';
                else if (total < target) color = 'var(--warning)';
                else if (projected > 0) color = 'var(--primary)';
            }} else {{
                if (total > maintenance) color = 'var(--danger)';
                else if (total > target) color = 'var(--warning)';
                else if (projected > 0) color = 'var(--primary)';
            }}

            span.style.color = color;
            fill.style.background = color || 'var(--primary)';
            fill.style.width = target > 0 ? Math.min(100, Math.round((total / target) * 100)) + '%' : '0%';
        }}

        function updateCardMacro(id, total, projected, goal, unit, strict) {{
            const card = document.getElementById('card-' + id);
            const span = card.querySelector('.current');
            const fill = card.querySelector('.progress-fill');
            span.textContent = total + unit;
            let color = '';
            if (goal > 0 && strict && total > goal) color = 'var(--danger)';
            else if (projected > 0) color = 'var(--primary)';
            span.style.color = color;
            fill.style.background = color || 'var(--primary)';
            fill.style.width = goal > 0 ? Math.min(100, Math.round((total / goal) * 100)) + '%' : '0%';
        }}
        updateProjection();
    </script>
</body>
</html>"""

    out_path = (
        os.path.join(output_directory, "logs", f"{target_date}.html")
        if date_str
        else os.path.join(output_directory, "index.html")
    )
    with open(out_path, "w") as output_file:
        output_file.write(html)
    click.echo(f"Generated: {out_path}")


def run_database_generation(output_directory: str = ".") -> None:
    try:
        with open("data/food_database.json", "r") as database_file:
            database = json.load(database_file)
    except FileNotFoundError:
        return

    rows_html = ""
    # Sort by protein (high to low), then calories (high to low), then product name
    sorted_database = sorted(
        database.values(),
        key=lambda item: (
            -item.get("protein_g", 0),
            -item.get("calories_kcal", 0),
            item.get("product_name", "").lower(),
        ),
    )
    for value in sorted_database:
        brand = value.get("brand", "N/A")
        product = format_title(value.get("product_name", ""))
        flavor = format_title(value.get("flavor", ""))
        calories, protein, carbohydrate, fat = (
            value.get("calories_kcal", 0),
            value.get("protein_g", 0),
            value.get("carbohydrate_g", 0),
            value.get("fat_g", 0),
        )
        ingredients = ", ".join(value.get("ingredients", []))

        rows_html += f"""
            <tr class="food-row" data-search="{brand.lower()} {product.lower()} {flavor.lower()} {ingredients.lower()}">
                <td class="text-center"><span class="badge">{brand}</span></td>
                <td><div style="font-weight: 600;">{product}</div>{f'<div style="font-size: 0.75rem; color: var(--muted);">{flavor}</div>' if flavor else ''}</td>
                <td class="text-center">{calories}</td>
                <td class="text-center">{protein}g</td>
                <td class="text-center">{carbohydrate}g</td>
                <td class="text-center">{fat}g</td>
            </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    {get_shared_head("Food Database")}
    <style>
        .controls {{ background: var(--card); padding: 1.25rem; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 2rem; display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 1.5rem; align-items: end; transition: background 0.3s; }}
        .control-group {{ display: flex; flex-direction: column; gap: 0.5rem; }}
        .control-group label {{ font-size: 0.75rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: 0.05em; }}
        input, select {{ padding: 0.6rem; border: 1px solid var(--border); border-radius: 6px; font-size: 0.875rem; color: var(--text); background: var(--card); outline: none; transition: border-color 0.2s, background 0.3s; }}
        input:focus, select:focus {{ border-color: var(--primary); }}
        .empty-state {{ padding: 4rem; text-align: center; color: var(--muted); display: none; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div><h1>Food Database</h1><p style="color: var(--muted); margin-top: 0.25rem; font-weight: 500;">{len(database)} Items Cataloged</p></div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <a href="index.html" class="nav-link">← Back to Dashboard</a>
                {get_theme_toggle_html()}
            </div>
        </header>
        <div class="controls">
            <div class="control-group"><label>Search Product</label><input type="text" id="search" placeholder="Search name, ingredients, brand..." oninput="filterTable()"></div>
            <div class="control-group"><label>Filter by Brand</label><select id="brand-filter" onchange="filterTable()"><option value="">All Brands</option>{" ".join([f'<option value="{brand}">{brand}</option>' for brand in sorted(list(set(value.get('brand', 'N/A') for value in database.values())))])}</select></div>
            <div class="control-group"><label>Sort By</label><select id="sort-by" onchange="sortTable()"><option value="0">Brand</option><option value="1">Product</option><option value="2">Calories</option><option value="3" selected>Protein</option><option value="4">Carbohydrate</option><option value="5">Fat</option></select></div>
        </div>
        <table id="food-table"><thead><tr><th class="text-center">Brand</th><th>Product</th><th class="text-center">Calories</th><th class="text-center">Protein</th><th class="text-center">Carbohydrate</th><th class="text-center">Fat</th></tr></thead><tbody>{rows_html}</tbody></table>
        <div id="empty-state" class="empty-state">No items match your search criteria.</div>
    </div>
    <script>
        function filterTable() {{
            const search_term = document.getElementById('search').value.toLowerCase();
            const brand_filter = document.getElementById('brand-filter').value.toLowerCase();
            const rows = document.querySelectorAll('.food-row');
            let visible = 0;
            rows.forEach(row => {{
                const text = row.getAttribute('data-search');
                const brand = row.querySelector('.badge').textContent.toLowerCase();
                const match = text.includes(search_term) && (brand_filter === "" || brand === brand_filter);
                row.style.display = match ? '' : 'none';
                if (match) visible++;
            }});
            document.getElementById('empty-state').style.display = visible === 0 ? 'block' : 'none';
        }}
        function sortTable() {{
            const index = parseInt(document.getElementById('sort-by').value);
            const table = document.getElementById('food-table');
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            rows.sort((a, b) => {{
                let value_a = a.cells[index].textContent.replace('g','');
                let value_b = b.cells[index].textContent.replace('g','');
                if (!isNaN(value_a) && !isNaN(value_b)) return parseFloat(value_b) - parseFloat(value_a);
                return value_a.localeCompare(value_b);
            }});
            rows.forEach(row => table.querySelector('tbody').appendChild(row));
        }}
    </script>
</body>
</html>"""
    out_path = os.path.join(output_directory, "food_database.html")
    with open(out_path, "w") as output_file:
        output_file.write(html)
    click.echo(f"Generated: {out_path}")


def run_history_generation(output_directory: str = ".") -> None:
    log_files = sorted(glob.glob("logs/**/*.json", recursive=True), reverse=True)
    try:
        with open("data/goals.json", "r") as goals_file:
            goals = json.load(goals_file)
        with open("data/food_database.json", "r") as database_file:
            database = json.load(database_file)
    except FileNotFoundError:
        goals = {}
        database = {}

    phase = goals.get("phase", "cut")
    target = goals.get("calories_target", 1800)
    maintenance = goals.get("calories_maintenance", 2300)

    items_html = ""
    for log_path in log_files:
        date_str = os.path.basename(log_path).replace(".json", "")
        with open(log_path, "r") as log_file:
            data = json.load(log_file)

        totals = data.get("totals", {})
        entries = data.get("entries", [])
        calories, protein = totals.get("calories_kcal", 0), totals.get("protein_g", 0)

        calories_class = ""
        if phase == "bulk":
            if calories < maintenance:
                calories_class = "under-maint"
            elif calories < target:
                calories_class = "under-target"
        else:
            if calories > maintenance:
                calories_class = "over-maint"
            elif calories > target:
                calories_class = "over-cut"

        table_rows = ""
        for entry in entries:
            database_entry = database.get(entry.get("id"), {})
            brand, product = database_entry.get("brand", "N/A"), format_title(
                database_entry.get("product_name", entry["display_name"])
            )
            if database_entry.get("flavor"):
                product += f" ({format_title(database_entry['flavor'])})"
            tag = (
                '<span class="tag-modified">Modified</span>'
                if "(Modified)" in entry.get("display_name", "")
                else ""
            )
            table_rows += f"<tr><td class='text-center'><span class='badge'>{brand}</span></td><td><span style='font-weight:600'>{product}</span>{tag}</td><td class='text-center'>{entry['calories_kcal']}</td><td class='text-center'>{entry['protein_g']}g</td><td class='text-center'>{entry['carbohydrate_g']}g</td><td class='text-center'>{entry['fat_g']}g</td></tr>"

        items_html += f"""
            <div class="history-item">
                <div class="history-header" onclick="this.parentElement.classList.toggle('open')">
                    <div class="date-label"><span class="chevron">▶</span>{date_str}</div>
                    <div class="summary-stats">
                        <div class="stat-group"><span class="stat-label">Calories</span><span class="stat-val {calories_class}">{calories}</span></div>
                        <div class="stat-group"><span class="stat-label">Protein</span><span class="stat-val">{protein}g</span></div>
                    </div>
                </div>
                <div class="details"><table><thead><tr><th class="text-center">Brand</th><th>Product</th><th class="text-center">Calories</th><th class="text-center">Protein</th><th class="text-center">Carbohydrate</th><th class="text-center">Fat</th></tr></thead><tbody>{table_rows}</tbody></table></div>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    {get_shared_head("History")}
    <style>
        .history-list {{ display: flex; flex-direction: column; gap: 1.25rem; }}
        .history-item {{ background: var(--card); border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; border: 1px solid transparent; transition: background 0.3s, border-color 0.2s; }}
        .history-item:hover {{ border-color: var(--border); }}
        .history-header {{ padding: 1.5rem; display: flex; justify-content: space-between; align-items: center; cursor: pointer; user-select: none; }}
        .date-label {{ font-weight: 800; color: var(--text); font-size: 1.25rem; display: flex; align-items: center; gap: 0.75rem; }}
        .chevron {{ font-size: 0.8rem; color: var(--muted); transition: transform 0.2s; }}
        .history-item.open .chevron {{ transform: rotate(90deg); }}
        .summary-stats {{ display: flex; gap: 1.5rem; }}
        .stat-group {{ display: flex; flex-direction: column; align-items: flex-end; }}
        .stat-label {{ font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: var(--muted); }}
        .stat-val {{ color: var(--text); font-size: 1.1rem; font-weight: 700; }}
        .over-cut, .under-target {{ color: var(--warning); }}
        .over-maint, .under-maint {{ color: var(--danger); }}
        .details {{ display: none; padding: 1.5rem; border-top: 1px solid var(--border); background: var(--bg); transition: background 0.3s; }}
        .history-item.open .details {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div><h1>History</h1><p style="color: var(--muted); margin-top: 0.25rem; font-weight: 500;">Past Daily Food Logs</p></div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <a href="index.html" class="nav-link">← Back to Dashboard</a>
                {get_theme_toggle_html()}
            </div>
        </header>
        <div class="history-list">{items_html}</div>
    </div>
</body>
</html>"""
    out_path = os.path.join(output_directory, "history.html")
    with open(out_path, "w") as output_file:
        output_file.write(html)
    click.echo(f"Generated: {out_path}")


@click.group()
def cli():
    pass


@cli.command()
@click.option("--output-directory", default=".", help="Output directory")
def dashboard(output_directory: str):
    run_dashboard_generation(output_directory=output_directory)


@cli.command()
@click.option("--date", help="YYYY-MM-DD")
@click.option("--output-directory", default=".", help="Output directory")
def log(date: str, output_directory: str):
    run_dashboard_generation(date, output_directory=output_directory)


@cli.command()
@click.option("--output-directory", default=".", help="Output directory")
def history(output_directory: str):
    run_history_generation(output_directory=output_directory)


@cli.command()
@click.option("--output-directory", default=".", help="Output directory")
def database(output_directory: str):
    run_database_generation(output_directory=output_directory)


@cli.command()
@click.option("--output-directory", default=".", help="Output directory")
def all(output_directory: str):
    if output_directory != ".":
        os.makedirs(os.path.join(output_directory, "data"), exist_ok=True)
        for data_file in glob.glob("data/*.json"):
            shutil.copy(data_file, os.path.join(output_directory, "data"))
        
        # Handle sharded logs
        log_files = glob.glob("logs/**/*.json", recursive=True)
        for log_file in log_files:
            # Create corresponding directories in the output
            dest_dir = os.path.join(output_directory, os.path.dirname(log_file))
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy(log_file, dest_dir)
            
        if os.path.exists("screenshot.png"):
            shutil.copy("screenshot.png", output_directory)
            
    run_dashboard_generation(output_directory=output_directory)
    run_database_generation(output_directory=output_directory)
    run_history_generation(output_directory=output_directory)
    
    log_files = glob.glob("logs/**/*.json", recursive=True)
    for log_file in log_files:
        run_dashboard_generation(
            os.path.basename(log_file).replace(".json", ""),
            output_directory=output_directory,
        )


if __name__ == "__main__":
    cli()
