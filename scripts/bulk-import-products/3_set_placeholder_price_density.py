"""
Step 3 of 3 (OPTIONAL) — run INSIDE `odoo shell`, same invocation pattern as
step 2. Only run this if the client's source file had no real price/density
data (has been true both times so far) AND you've been explicitly told to
fill in placeholders rather than leave them at 0/blank — leaving them at
0/blank is the more honest default; only override that when downstream
workflows genuinely need non-zero values to proceed (e.g. quotation/BOQ
flows that reject a 0-price line).

These are NOT real client numbers. Density is a defensible physical estimate
(real typical ranges per stone type). Price/Cost are placeholders scaled off
this DB's own existing reference materials at time of writing (Bianco Sardo
Granite, Carrara White, Vietnam Limestone) — re-derive PROFILE below from
whatever real reference materials exist in the target DB if it's been a
while, rather than blindly reusing these numbers forever.

Only touches materials listed in the step-1 JSON — does not touch any
pre-existing material's price/density, even if it's also at 0 (that's a
separate, possibly deliberately-owned gap — don't silently overwrite it).
"""

import json

JSON_PATH = '/mnt/extra-addons/.import_scratch.json'

# Slab/Block/FG values are (list_price, standard_price/cost) tuples.
PROFILE = {
    'granite':   {'density': 2.70, 'slab': (4000, 2200), 'block': (26000, 15000), 'fg': (12000, 6500)},
    'marble':    {'density': 2.70, 'slab': (4500, 2500), 'block': (32000, 18000), 'fg': (13500, 7500)},
    'quartzite': {'density': 2.65, 'slab': (4200, 2300), 'block': (27000, 15500), 'fg': (12500, 7000)},
    'limestone': {'density': 2.50, 'slab': (1500, 700), 'block': (10000, 5000), 'fg': (4500, 2200)},
    'other':     {'density': 2.70, 'slab': (6000, 3500), 'block': (40000, 22000), 'fg': (18000, 10000)},
}

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

updated = []
not_found = []
for m in data['materials']:
    mat = env['stone.material'].search([('name', '=', m['name'])], limit=1)
    if not mat:
        not_found.append(m['name'])
        continue
    profile = PROFILE[m['category']]
    if not mat.density_ton_per_cbm:
        mat.density_ton_per_cbm = profile['density']

    slab_list, slab_cost = profile['slab']
    mat.product_id.list_price = slab_list
    mat.product_id.standard_price = slab_cost

    if mat.product_id_block:
        block_list, block_cost = profile['block']
        mat.product_id_block.list_price = block_list
        mat.product_id_block.standard_price = block_cost

    fg = env['product.template'].search([('stone_fg_material_id', '=', mat.id)], limit=1)
    if fg:
        fg_list, fg_cost = profile['fg']
        fg.list_price = fg_list
        fg.standard_price = fg_cost

    updated.append(m['name'])

env.cr.commit()
print('updated:', len(set(updated)))
print('not found (expected: any material skipped in step 2, e.g. a name conflict):', set(not_found))
