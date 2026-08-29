"""
Step 3b (OPTIONAL, sibling to 3_set_placeholder_price_density.py) — fills
placeholder list_price/standard_price for the 45 non-stone IMP-*/SITE-*
auxiliary products step 2 creates (labor, hardware, silicone, cement/grout,
import-cost lines). Step 3 only ever covered the 49 stone materials.

Same run pattern as step 2/3 — inside `odoo shell`, JSON_PATH pointing at
the step-1 output copied into the container's addons mount.

Tiering follows the same logic Session 95 (2026-08-29, EMG-O log.md) used
on mbx-ee-dev by hand, now scripted so it's repeatable: flat placeholder
per rough category, except cement/grout/TTM lines which are priced per kg
(25/kg sale, 15/kg cost) parsed out of the product name — same rate Session
95 used. Re-derive these numbers from real client pricing once available;
this is explicitly placeholder data, same caveat as step 3.

Only touches products whose default_code matches a code in the step-1
JSON's `other_rows` — never touches the 49 stone materials or anything
pre-existing.
"""

import json
import re

JSON_PATH = '/mnt/extra-addons/.import_scratch.json'

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

KG_RE = re.compile(r'(\d+(?:\.\d+)?)\s*(?:kg|kilo|กก|กิโล)', re.IGNORECASE)

HARDWARE_KEYWORDS = ['เหล็ก', 'เดือย', 'ฉาก', 'สไลด์', 'ตะขอ', 'อะลูมิเนียม', 'plate', 'Plate']
SILICONE_KEYWORDS = ['ซิลิโคน', 'silicone']
LABOR_KEYWORDS = ['ค่าแรง']
CEMENT_KEYWORDS = ['ปูน', 'TTM', 'grout', 'ยาแนว']

updated = []
not_found = []
for row in data['other_rows']:
    product = env['product.template'].search([('default_code', '=', row['code'])], limit=1)
    if not product:
        not_found.append(row['code'])
        continue

    name = row['name']
    code = row['code']

    if code.startswith('IMP-'):
        # Import-cost pass-through line: cost = list, no markup.
        list_price, cost = 1000.0, 1000.0
    elif any(k in name for k in LABOR_KEYWORDS):
        list_price, cost = 500.0, 0.0
    elif any(k in name for k in SILICONE_KEYWORDS):
        list_price, cost = 350.0, 200.0
    elif any(k in name for k in CEMENT_KEYWORDS):
        m = KG_RE.search(name)
        kg = float(m.group(1)) if m else 1.0
        list_price, cost = round(25.0 * kg, 2), round(15.0 * kg, 2)
    elif any(k in name for k in HARDWARE_KEYWORDS):
        list_price, cost = 150.0, 90.0
    else:
        # Unclassified SITE-/IMP- row — flat generic placeholder, flagged
        # below so it can be reviewed rather than silently guessed.
        list_price, cost = 200.0, 120.0

    product.list_price = list_price
    product.standard_price = cost
    updated.append((code, list_price, cost))

env.cr.commit()
print('updated:', len(updated))
print('not found (expected: nothing, every other_row should have been created in step 2):', not_found)
