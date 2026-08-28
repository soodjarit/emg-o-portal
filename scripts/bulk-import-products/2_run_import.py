"""
Step 2 of 3 — run INSIDE `odoo shell` (needs the ORM). Reads the JSON that
step 1 produced and creates stone.material + Block/Slab/FG product.templates,
plus any non-stone auxiliary products (IMP-*/SITE-* style rows).

How to run (from the HOST, piping this file into the container):

    docker exec -i <container> odoo shell -d <db> \\
        --db_host <host> --db_port <port> --db_user <user> --db_password '<pw>' \\
        --no-http < 2_run_import.py

Before running:
  1. The JSON from step 1 must be readable from a path INSIDE the container.
     Copy it into whatever host directory is bind-mounted to the container's
     addons path (check `docker inspect <container> --format '{{.Mounts}}'`),
     then set JSON_PATH below to the container-side path. Delete the copy
     from the host addons dir again after the run — it's scratch data, not
     code, must never land in a git commit.
  2. The Finish product.attribute must already have every value referenced
     in the JSON's finish_values lists (see this module's
     data/stone_finish_attribute_data.xml) — if the client's file introduces
     a brand new Finish name step 1 didn't recognize, add it there first,
     `-u` the module, restart the container, THEN run this script. Anything
     in finish_values that doesn't match a real attribute value is silently
     skipped (falls back to a plain non-variant Slab) — check the printed
     summary for this.
  3. product.category "Stone FG - Countertop" (or whatever this DB's real FG
     category is named) must already exist with real Operations/Labor Cost
     set up (ADR-029) — this script does NOT create it, only looks it up by
     name. Change FG_CATEGORY_NAME below if this DB uses a different name.
  4. Always dry-run first (DRY_RUN = True) and read the summary before
     flipping to a real write — especially the "materials skipped (already
     exist)" list, since a name collision there means 2 different materials
     in the source resolved to the same name (a real data problem in the
     client's file, not a bug — needs a human decision, see step 1's
     name_conflicts output).

Known past mistakes, now fixed in this version — don't reintroduce them:
  - default_code was originally set on Template.create() BEFORE adding the
    Finish attribute line. Odoo regenerates product.product variants when an
    attribute line is added, and the new variants don't inherit the
    pre-variant-generation default_code — so every Slab's Internal Reference
    came out blank. This version sets default_code AFTER the variant exists.
  - A follow-up "fix" pass for the above bug matched existing records by
    material *name* to patch them — but 2 source rows sharing the same
    (post-conflict) name meant the second iteration silently overwrote the
    first one's just-fixed code. This version doesn't need a separate fix
    pass at all (see previous point), which also removes that whole failure
    mode. If a future variant of this script ever does a name-keyed UPDATE
    pass instead of a CREATE pass, match by something unique to the source
    row (e.g. slab_code), never by material name alone.
"""

import json

DRY_RUN = True
JSON_PATH = '/mnt/extra-addons/.import_scratch.json'  # container-side path, see docstring point 1
FG_CATEGORY_NAME = 'Stone FG - Countertop'
DEFAULT_PRICING_MODE = 'serial'  # this batch's materials are all individually-tracked slabs; use 'lot' per-material if the source data says otherwise

with open(JSON_PATH, encoding='utf-8') as f:
    data = json.load(f)

Template = env['product.template']
uom_unit = env.ref('uom.product_uom_unit')
uom_cbm = env.ref('uom.product_uom_cubic_meter')
finish_attr = env.ref('stone_slab_inventory.product_attribute_finish')
finish_value_by_name = {v.name: v for v in finish_attr.value_ids}
fg_category = env['product.category'].search([('name', '=', FG_CATEGORY_NAME)], limit=1)
if not fg_category:
    print('WARNING: FG category %r not found — FG products will be skipped entirely.' % FG_CATEGORY_NAME)

created_materials = []
skipped_existing = []
unknown_finish_values = set()

for m in data['materials']:
    existing = env['stone.material'].search([('name', '=', m['name'])], limit=1)
    if existing:
        skipped_existing.append(m['name'])
        continue

    if DRY_RUN:
        created_materials.append(m['name'])
        continue

    slab_tmpl = Template.create({
        'name': '%s - Slab' % m['name'],
        'type': 'consu',
        'is_storable': True,
        'tracking': 'serial' if DEFAULT_PRICING_MODE == 'serial' else 'lot',
        'uom_id': uom_unit.id,
        'list_price': 0.0,
        'standard_price': 0.0,
        'sale_ok': True,
        'purchase_ok': True,
    })

    value_ids = []
    for n in m['finish_values']:
        v = finish_value_by_name.get(n)
        if v:
            value_ids.append(v.id)
        else:
            unknown_finish_values.add(n)
    if value_ids:
        env['product.template.attribute.line'].create({
            'product_tmpl_id': slab_tmpl.id,
            'attribute_id': finish_attr.id,
            'value_ids': [(6, 0, value_ids)],
        })
    # IMPORTANT: set default_code AFTER the attribute line above, on the
    # actual resulting variant — see docstring for why.
    slab_variant = slab_tmpl.product_variant_ids.sorted('id')[:1]
    slab_variant.default_code = m['slab_code']

    block_tmpl = Template.create({
        'name': '%s - Block' % m['name'],
        'type': 'consu',
        'is_storable': True,
        'tracking': 'lot',
        'uom_id': uom_cbm.id,
        'default_code': m['block_code'],
        'list_price': 0.0,
        'standard_price': 0.0,
        'sale_ok': True,
        'purchase_ok': True,
    })

    material = env['stone.material'].create({
        'name': m['name'],
        'category': m['category'],
        'pricing_mode': DEFAULT_PRICING_MODE,
        'product_id': slab_variant.id,
        'product_id_block': block_tmpl.product_variant_id.id,
    })

    if fg_category:
        Template.create({
            'name': m['name'],
            'type': 'consu',
            'categ_id': fg_category.id,
            'stone_is_fg': True,
            'stone_fg_material_id': material.id,
            'default_code': m['fg_code'],
            'list_price': 0.0,
            'standard_price': 0.0,
            'sale_ok': True,
            'purchase_ok': True,
        })

    created_materials.append(m['name'])

# --- non-stone auxiliary products (IMP-*/SITE-* style rows) ---
expenses_categ = env['product.category'].search([('name', '=', 'Expenses')], limit=1)
goods_categ = env['product.category'].search([('name', '=', 'Goods')], limit=1)

created_others = []
skipped_others_existing = []
for r in data.get('other_rows', []):
    existing = env['product.template'].search([('default_code', '=', r['code'])], limit=1)
    if existing:
        skipped_others_existing.append(r['code'])
        continue
    is_imp = r['code'].startswith('IMP-')
    name = r['name']
    if name.startswith(r['code'] + ' '):
        name = name[len(r['code']) + 1:]
    if DRY_RUN:
        created_others.append((r['code'], name))
        continue
    Template.create({
        'name': name,
        'type': 'service' if is_imp else 'consu',
        'is_storable': False,
        'categ_id': (expenses_categ if is_imp else goods_categ).id,
        'uom_id': uom_unit.id,
        'default_code': r['code'],
        'list_price': 0.0,
        'standard_price': 0.0,
        'sale_ok': False,
        'purchase_ok': True,
    })
    created_others.append((r['code'], name))

print('DRY_RUN =', DRY_RUN)
print('materials created/would-create:', len(created_materials))
print('materials skipped (already exist — check for a name collision, see step 1 name_conflicts):', skipped_existing)
print('unknown finish values in source not matched to a real attribute value (extend the Finish attribute first):', unknown_finish_values)
print('other products created/would-create:', len(created_others))
print('other products skipped (already exist):', skipped_others_existing)

if not DRY_RUN:
    env.cr.commit()
    print('COMMITTED.')
else:
    print('DRY RUN ONLY — nothing written. Review the summary above, then flip DRY_RUN=False and re-run.')
