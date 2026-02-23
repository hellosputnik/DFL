import json
import os
import re
import glob
import click
import shutil
from datetime import datetime

# --- SHARED UTILITIES ---

def format_title(text):
    if not text: return ""
    lower_words = {'a', 'an', 'the', 'and', 'but', 'for', 'or', 'nor', 'so', 'yet', 'as', 'at', 'by', 'in', 'of', 'on', 'to', 'up', 'with', 'from', 'into', 'onto', 'upon', 'via', 'mid'}
    upper_acronyms = {'bbq', 'blt', 'usda', 'gmo', 'msg', 'pb&j', 'bpa', 'id', 'p/c/f', 'usa'}
    units = {'oz', 'fl', 'ml', 'g', 'mg', 'kcal'}
    words = str(text).split()
    if not words: return ""
    formatted_words = []
    for i, word in enumerate(words):
        stripped = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', word)
        clean = stripped.lower()
        if '-' in stripped:
            parts = stripped.split('-')
            formatted_parts = [p.capitalize() for p in parts]
            formatted_main = '-'.join(formatted_parts)
            res = word.replace(stripped, formatted_main)
        elif clean in upper_acronyms:
            res = word.replace(stripped, stripped.upper())
        elif clean in units:
            res = word.replace(stripped, clean)
        elif i == 0 or i == len(words) - 1:
            res = word.replace(stripped, stripped.capitalize())
        elif clean in lower_words:
            res = word.replace(stripped, clean)
        else:
            res = word.replace(stripped, stripped.capitalize())
        formatted_words.append(res)
    return " ".join(formatted_words)

def get_shared_head(title):
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

def get_theme_toggle_html():
    return """
    <button onclick="toggleTheme()" class="theme-toggle" title="Toggle Dark Mode">
        <svg class="moon-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
        <svg class="sun-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" /></svg>
    </button>
    """

# --- CORE IMPLEMENTATIONS ---

def run_dashboard_gen(date_str=None, outdir='.'):
    try:
        with open('data/goals.json', 'r') as f: goals = json.load(f)
        with open('data/inventory.json', 'r') as f: inventory = json.load(f)
        with open('data/food_database.json', 'r') as f: db = json.load(f)
    except FileNotFoundError as e:
        click.echo(f"Error: Missing data file - {e}"); return

    target_date = date_str if date_str else datetime.now().strftime('%Y-%m-%d')
    log_path = f'logs/{target_date}.json'
    daily_log = json.load(open(log_path, 'r')) if os.path.exists(log_path) else {"entries": [], "totals": {"calories_kcal": 0, "protein_g": 0, "carbohydrate_g": 0, "fat_g": 0}}
    totals = daily_log['totals']
    
    def get_pct(current, goal):
        return min(100, int((current / goal) * 100)) if goal and goal > 0 else 0

    def get_goal_val(val):
        return str(val) if val > 0 else ""

    inv_rows_html = ""
    for inv_item in inventory:
        m = db.get(inv_item['id'])
        if not m:
            for db_id, db_val in db.items():
                if inv_item['id'] in db_id: m = db_val; break
        if not m: continue
        p, c, f, cal = m.get('protein_g', 0), m.get('carbohydrate_g', 0), m.get('fat_g', 0), m.get('calories_kcal', 0)
        prod = format_title(m.get('product_name', ''))
        if m.get('flavor'): prod += f" ({format_title(m['flavor'])})"
        inv_rows_html += f"""
            <tr class='inventory-row' data-cal='{cal}' data-p='{p}' data-c='{c}' data-f='{f}'>
                <td class='text-center'><input type='checkbox' class='project-toggle' style='width: 18px; height: 18px; cursor: pointer;' onchange='updateProjection()'></td>
                <td class='text-center'><span class='badge'>{m.get('brand')}</span></td>
                <td style='font-weight: 500;'>{prod}</td>
                <td class='text-center'>{inv_item['quantity']} {inv_item['unit']}</td>
                <td class='text-center'>{p}g / {c}g / {f}g</td>
            </tr>"""

    log_rows_html = ""
    if not daily_log['entries']:
        log_rows_html = "<tr><td colspan='6' style='text-align:center; padding: 2rem; color: #94a3b8;'>No food logged yet today.</td></tr>"
    else:
        for entry in daily_log['entries']:
            m = db.get(entry.get('id'), {})
            brand = m.get('brand', 'N/A')
            product = format_title(m.get('product_name', entry['display_name']))
            if m.get('flavor'): product += f" ({format_title(m['flavor'])})"
            product_html = f"<span style='font-weight: 500;'>{product}</span>"
            if "(Modified)" in entry.get('display_name', ''): product_html += "<span class='tag-modified'>Modified</span>"
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
                <div class="stat-label">Calories <div class="info-icon" style="cursor:help; position:relative; display:inline-flex; align-items:center;"><svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg><div class="tooltip" id="cal-tooltip">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;"><span>Phase</span> <b style="text-transform: capitalize;">{goals.get('phase', 'cut')}</b></div>
                    <div style="display: flex; justify-content: space-between;"><span>Goal</span> <b>{goals['calories_target']}</b></div>
                    <div style="display: flex; justify-content: space-between;"><span>Maintenance</span> <b>{goals['calories_maintenance']}</b></div>
                </div></div></div>
                <div class="stat-val"><span class="current">{totals['calories_kcal']}</span></div>
                <div class="goal-display-container"><input type="number" class="editable-goal" id="goal-cal-input" data-mode="{goals.get('phase', 'cut')}" value="{goals['calories_target']}" placeholder="N/A" oninput="updateProjection()"></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {get_pct(totals['calories_kcal'], goals['calories_target'])}%"></div></div>
            </div>
            <div class="card" id="card-protein">
                <div class="stat-label">Protein</div>
                <div class="stat-val"><span class="current">{totals['protein_g']}g</span></div>
                <div class="goal-display-container"><input type="number" class="editable-goal" id="goal-p-input" value="{goals['protein_g']}" placeholder="N/A" oninput="updateProjection()"></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {get_pct(totals['protein_g'], goals['protein_g'])}%"></div></div>
            </div>
            <div class="card" id="card-carbs">
                <div class="stat-label">Carbohydrate</div>
                <div class="stat-val"><span class="current">{totals['carbohydrate_g']}g</span></div>
                <div class="goal-display-container"><input type="number" class="editable-goal" id="goal-c-input" value="{get_goal_val(goals.get('carbohydrate_g', 0))}" placeholder="N/A" oninput="updateProjection()"></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {get_pct(totals['carbohydrate_g'], goals.get('carbohydrate_g', 0))}%"></div></div>
            </div>
            <div class="card" id="card-fat">
                <div class="stat-label">Fat</div>
                <div class="stat-val"><span class="current">{totals['fat_g']}g</span></div>
                <div class="goal-display-container"><input type="number" class="editable-goal" id="goal-f-input" value="{get_goal_val(goals.get('fat_g', 0))}" placeholder="N/A" oninput="updateProjection()"></div>
                <div class="progress-bg"><div class="progress-fill" style="width: {get_pct(totals['fat_g'], goals.get('fat_g', 0))}%"></div></div>
            </div>
        </div>

        <section><h2>Today's Log</h2><table id="log-table"><thead><tr><th class="text-center">Brand</th><th>Product</th><th class="text-center">Calories</th><th class="text-center">Protein</th><th class="text-center">Carbohydrate</th><th class="text-center">Fat</th></tr></thead><tbody>{log_rows_html}</tbody></table></section>
        <section style="margin-top: 2rem;"><h2>Current Inventory</h2><table id="inventory-table"><thead><tr><th style='width: 40px;' class='text-center'>Add</th><th class='text-center'>Brand</th><th>Product</th><th class='text-center'>Quantity</th><th class='text-center'>Macros (P / C / F)</th></tr></thead><tbody>{inv_rows_html}</tbody></table></section>
    </div>

    <script>
        const currentTotals = {{ cal: {totals['calories_kcal']}, p: {totals['protein_g']}, c: {totals['carbohydrate_g']}, f: {totals['fat_g']} }};
        const maintCal = {goals['calories_maintenance']};

        function updateProjection() {{
            const gs = {{
                target: parseFloat(document.getElementById('goal-cal-input').value) || 0,
                p: parseFloat(document.getElementById('goal-p-input').value) || 0,
                c: parseFloat(document.getElementById('goal-c-input').value) || 0,
                f: parseFloat(document.getElementById('goal-f-input').value) || 0
            }};
            let pCal = 0, pP = 0, pC = 0, pF = 0;
            document.querySelectorAll('.inventory-row').forEach(row => {{
                if (row.querySelector('.project-toggle').checked) {{
                    pCal += parseFloat(row.dataset.cal); pP += parseFloat(row.dataset.p); pC += parseFloat(row.dataset.c); pF += parseFloat(row.dataset.f);
                }}
            }});
            updateCardCal(currentTotals.cal + pCal, pCal, gs.target, maintCal);
            updateCardMacro('protein', currentTotals.p + pP, pP, gs.p, 'g', false);
            updateCardMacro('carbs', currentTotals.c + pC, pC, gs.c, 'g', true);
            updateCardMacro('fat', currentTotals.f + pF, pF, gs.f, 'g', true);
        }}

        function updateCardCal(total, proj, target, maint) {{
            const card = document.getElementById('card-calories');
            const span = card.querySelector('.current');
            const fill = card.querySelector('.progress-fill');
            const mode = document.getElementById('goal-cal-input').dataset.mode;
            
            span.textContent = total;
            let col = '';

            if (mode === 'bulk') {{
                if (total < maint) col = 'var(--danger)';
                else if (total < target) col = 'var(--warning)';
                else if (proj > 0) col = 'var(--primary)';
            }} else {{
                if (total > maint) col = 'var(--danger)';
                else if (total > target) col = 'var(--warning)';
                else if (proj > 0) col = 'var(--primary)';
            }}

            span.style.color = col;
            fill.style.background = col || 'var(--primary)';
            fill.style.width = target > 0 ? Math.min(100, Math.round((total / target) * 100)) + '%' : '0%';
        }}

        function updateCardMacro(id, total, proj, goal, unit, strict) {{
            const card = document.getElementById('card-' + id);
            const span = card.querySelector('.current');
            const fill = card.querySelector('.progress-fill');
            span.textContent = total + unit;
            let col = '';
            if (goal > 0 && strict && total > goal) col = 'var(--danger)';
            else if (proj > 0) col = 'var(--primary)';
            span.style.color = col;
            fill.style.background = col || 'var(--primary)';
            fill.style.width = goal > 0 ? Math.min(100, Math.round((total / goal) * 100)) + '%' : '0%';
        }}
        updateProjection();
    </script>
</body>
</html>"""
    
    out_path = os.path.join(outdir, 'logs', f"{target_date}.html") if date_str else os.path.join(outdir, "index.html")
    with open(out_path, 'w') as f: f.write(html)
    click.echo(f"Generated: {out_path}")

def run_database_gen(outdir='.'):
    try:
        with open('data/food_database.json', 'r') as f: db = json.load(f)
    except FileNotFoundError: return
    
    rows_html = ""
    for v in db.values():
        brand = v.get('brand', 'N/A')
        prod = format_title(v.get('product_name', ''))
        flav = format_title(v.get('flavor', ''))
        cal, p, c, f = v.get('calories_kcal', 0), v.get('protein_g', 0), v.get('carbohydrate_g', 0), v.get('fat_g', 0)
        ing = ", ".join(v.get('ingredients', []))
        
        rows_html += f"""
            <tr class="food-row" data-search="{brand.lower()} {prod.lower()} {flav.lower()} {ing.lower()}">
                <td class="text-center"><span class="badge">{brand}</span></td>
                <td><div style="font-weight: 600;">{prod}</div>{f'<div style="font-size: 0.75rem; color: var(--muted);">{flav}</div>' if flav else ''}</td>
                <td class="text-center">{cal}</td>
                <td class="text-center">{p}g</td>
                <td class="text-center">{c}g</td>
                <td class="text-center">{f}g</td>
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
            <div><h1>Food Database</h1><p style="color: var(--muted); margin-top: 0.25rem; font-weight: 500;">{len(db)} Items Cataloged</p></div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <a href="index.html" class="nav-link">← Back to Dashboard</a>
                {get_theme_toggle_html()}
            </div>
        </header>
        <div class="controls">
            <div class="control-group"><label>Search Product</label><input type="text" id="search" placeholder="Search name, ingredients, brand..." oninput="filterTable()"></div>
            <div class="control-group"><label>Filter by Brand</label><select id="brand-filter" onchange="filterTable()"><option value="">All Brands</option>{" ".join([f'<option value="{b}">{b}</option>' for b in sorted(list(set(v.get('brand', 'N/A') for v in db.values())))])}</select></div>
            <div class="control-group"><label>Sort By</label><select id="sort-by" onchange="sortTable()"><option value="0">Brand</option><option value="1">Product</option><option value="2">Calories</option><option value="3">Protein</option><option value="4">Carbohydrate</option><option value="5">Fat</option></select></div>
        </div>
        <table id="food-table"><thead><tr><th class="text-center">Brand</th><th>Product</th><th class="text-center">Calories</th><th class="text-center">Protein</th><th class="text-center">Carbohydrate</th><th class="text-center">Fat</th></tr></thead><tbody>{rows_html}</tbody></table>
        <div id="empty-state" class="empty-state">No items match your search criteria.</div>
    </div>
    <script>
        function filterTable() {{
            const st = document.getElementById('search').value.toLowerCase();
            const bf = document.getElementById('brand-filter').value.toLowerCase();
            const rows = document.querySelectorAll('.food-row');
            let visible = 0;
            rows.forEach(row => {{
                const text = row.getAttribute('data-search');
                const brand = row.querySelector('.badge').textContent.toLowerCase();
                const match = text.includes(st) && (bf === "" || brand === bf);
                row.style.display = match ? '' : 'none';
                if (match) visible++;
            }});
            document.getElementById('empty-state').style.display = visible === 0 ? 'block' : 'none';
        }}
        function sortTable() {{
            const idx = parseInt(document.getElementById('sort-by').value);
            const table = document.getElementById('food-table');
            const rows = Array.from(table.querySelectorAll('tbody tr'));
            rows.sort((a, b) => {{
                let vA = a.cells[idx].textContent.replace('g','');
                let vB = b.cells[idx].textContent.replace('g','');
                if (!isNaN(vA) && !isNaN(vB)) return parseFloat(vB) - parseFloat(vA);
                return vA.localeCompare(vB);
            }});
            rows.forEach(row => table.querySelector('tbody').appendChild(row));
        }}
    </script>
</body>
</html>"""
    out_path = os.path.join(outdir, 'food_database.html')
    with open(out_path, 'w') as f: f.write(html)
    click.echo(f"Generated: {out_path}")

def run_history_gen(outdir='.'):
    log_files = sorted(glob.glob('logs/*.json'), reverse=True)
    try:
        with open('data/goals.json', 'r') as f: goals = json.load(f)
        with open('data/food_database.json', 'r') as f: db = json.load(f)
    except FileNotFoundError: goals = {}; db = {}

    phase = goals.get('phase', 'cut')
    target = goals.get('calories_target', 1800)
    maint = goals.get('calories_maintenance', 2300)

    items_html = ""
    for log_path in log_files:
        date_str = os.path.basename(log_path).replace('.json', '')
        with open(log_path, 'r') as f:
            data = json.load(f)
        
        totals = data.get('totals', {})
        entries = data.get('entries', [])
        cal, p = totals.get('calories_kcal', 0), totals.get('protein_g', 0)
        
        cal_class = ""
        if phase == 'bulk':
            if cal < maint: cal_class = "under-maint"
            elif cal < target: cal_class = "under-target"
        else:
            if cal > maint: cal_class = "over-maint"
            elif cal > target: cal_class = "over-cut"
        
        table_rows = ""
        for entry in entries:
            m = db.get(entry.get('id'), {})
            brand, product = m.get('brand', 'N/A'), format_title(m.get('product_name', entry['display_name']))
            if m.get('flavor'): product += f" ({format_title(m['flavor'])})"
            tag = '<span class="tag-modified">Modified</span>' if '(Modified)' in entry.get('display_name','') else ''
            table_rows += f"<tr><td class='text-center'><span class='badge'>{brand}</span></td><td><span style='font-weight:600'>{product}</span>{tag}</td><td class='text-center'>{entry['calories_kcal']}</td><td class='text-center'>{entry['protein_g']}g</td><td class='text-center'>{entry['carbohydrate_g']}g</td><td class='text-center'>{entry['fat_g']}g</td></tr>"

        items_html += f"""
            <div class="history-item">
                <div class="history-header" onclick="this.parentElement.classList.toggle('open')">
                    <div class="date-label"><span class="chevron">▶</span>{date_str}</div>
                    <div class="summary-stats">
                        <div class="stat-group"><span class="stat-label">Calories</span><span class="stat-val {cal_class}">{cal}</span></div>
                        <div class="stat-group"><span class="stat-label">Protein</span><span class="stat-val">{p}g</span></div>
                    </div>
                </div>
                <div class="details"><table><thead><tr><th class="text-center">Brand</th><th>Product</th><th class="text-center">Calories</th><th class="text-center">Protein</th><th class="text-center">Carbohydrate</th><th class="text-center">Fat</th></tr></thead><tbody>{table_rows}</tbody></table></div>
            </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    {get_shared_head("Food Log History")}
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
        .details {{ display: none; padding: 0 1.5rem 1.5rem 1.5rem; border-top: 1px solid var(--border); background: var(--bg); transition: background 0.3s; }}
        .history-item.open .details {{ display: block; }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div><h1>Log History</h1><p style="color: var(--muted); margin-top: 0.25rem; font-weight: 500;">Past Daily Records</p></div>
            <div style="display: flex; gap: 1rem; align-items: center;">
                <a href="index.html" class="nav-link">← Back to Dashboard</a>
                {get_theme_toggle_html()}
            </div>
        </header>
        <div class="history-list">{items_html}</div>
    </div>
</body>
</html>"""
    out_path = os.path.join(outdir, 'history.html')
    with open(out_path, 'w') as f: f.write(html)
    click.echo(f"Generated: {out_path}")

# --- CLICK CLI ---

@click.group()
def cli(): pass

@cli.command()
@click.option('--outdir', default='.', help="Output directory")
def dashboard(outdir): run_dashboard_gen(outdir=outdir)

@cli.command()
@click.option('--date', help="YYYY-MM-DD")
@click.option('--outdir', default='.', help="Output directory")
def log(date, outdir): run_dashboard_gen(date, outdir=outdir)

@cli.command()
@click.option('--outdir', default='.', help="Output directory")
def history(outdir): run_history_gen(outdir=outdir)

@cli.command()
@click.option('--outdir', default='.', help="Output directory")
def database(outdir): run_database_gen(outdir=outdir)

@cli.command()
@click.option('--outdir', default='.', help="Output directory")
def all(outdir):
    if outdir != '.':
        os.makedirs(os.path.join(outdir, 'logs'), exist_ok=True)
        os.makedirs(os.path.join(outdir, 'data'), exist_ok=True)
        for f in glob.glob('data/*.json'): shutil.copy(f, os.path.join(outdir, 'data'))
        for f in glob.glob('logs/*.json'): shutil.copy(f, os.path.join(outdir, 'logs'))
        if os.path.exists('screenshot.png'): shutil.copy('screenshot.png', outdir)
    run_dashboard_gen(outdir=outdir)
    run_database_gen(outdir=outdir)
    run_history_gen(outdir=outdir)
    for log_file in glob.glob('logs/*.json'):
        run_dashboard_gen(os.path.basename(log_file).replace('.json',''), outdir=outdir)

if __name__ == "__main__":
    cli()
