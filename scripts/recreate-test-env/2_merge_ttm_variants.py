"""
Merges the known SITE- near-duplicate TTM products into real Odoo product
variants (Size/Color), and removes 2 genuine duplicate imports — the exact
cleanup Session 95 (2026-08-29, EMG-O log.md) did by hand on `mbx-ee-dev`,
now scripted so a future `eg-tst` recreate doesn't have to redo it by hand.
Run inside `odoo shell` against the target DB, right after the bulk-import
toolkit (`bulk-import-products/`) and its placeholder-pricing steps.

Values (which SKU is 1kg vs 20kg, which color is which, price_extra
amounts) were read directly off `mbx-ee-dev`'s already-merged state
2026-08-29, not re-derived — re-verify against `mbx-ee-dev` before reusing
this script if a lot of time has passed and the client's real file/pricing
may have changed.

Safety: checks stock_move_line/sale_order_line/purchase_order_line/
stock_quant for every target product id first and refuses to touch
anything referenced — this is meant to run on a freshly-imported catalog
with zero transactions, not on a DB with real activity.
"""

DUPLICATES_TO_DELETE = ['SITE-034', 'SITE-037']  # keep SITE-016, SITE-028

# Each group: template name to end up with, attribute name ('size'/'color'
# on this DB's shared attribute ids), and (default_code, value_label,
# price_extra) triples in variant order. First value's price_extra should
# be 0 (it becomes the base variant).
GROUPS = [
    {
        'name': 'ปูนสกิมโค้ท TTM 104',
        'attribute': 'size',
        'list_price': 25.0,
        'variants': [
            ('SITE-030', '1kg', 0.0, 15.0),
            ('SITE-033', '20kg', 475.0, 300.0),
        ],
    },
    {
        'name': 'ปูน TTM 110',
        'attribute': 'size',
        'list_price': 75.0,
        'variants': [
            ('SITE-018', '3kg', 0.0, 45.0),
            ('SITE-029', '40kg', 925.0, 600.0),
        ],
    },
    {
        'name': 'ยาแนว TTM 901',
        'attribute': 'color',
        'list_price': 25.0,
        'variants': [
            ('SITE-019', 'Absolute White', 0.0, 15.0),
            ('SITE-020', 'Ivory Cream (ครีมงาช้าง)', 0.0, 15.0),
            ('SITE-031', 'Black Lignite (ดำลิกไนท์)', 0.0, 15.0),
        ],
    },
    {
        'name': 'ยาแนว TTM 902',
        'attribute': 'color',
        'list_price': 25.0,
        'variants': [
            ('SITE-021', 'Cream (ครีม)', 0.0, 15.0),
            ('SITE-022', 'Blue #2 (น้ำเงินคราม)', 0.0, 15.0),
            ('SITE-023', 'Black Lignite #7 Premium (ดำลิกไนท์ พรีเมียม)', 0.0, 15.0),
        ],
    },
]

Product = env['product.product'].sudo().with_context(active_test=False)
Template = env['product.template'].sudo()
Attribute = env['product.attribute'].sudo()
AttrValue = env['product.attribute.value'].sudo()
AttrLine = env['product.template.attribute.line'].sudo()

all_codes = list(DUPLICATES_TO_DELETE) + [v[0] for g in GROUPS for v in g['variants']]
targets = Product.search([('default_code', 'in', all_codes)])
assert len(targets) == len(all_codes), f"expected {len(all_codes)} products, found {len(targets)} — check default_code list against this DB"

for model, field in [
    ('stock.move.line', 'product_id'),
    ('sale.order.line', 'product_id'),
    ('purchase.order.line', 'product_id'),
    ('stock.quant', 'product_id'),
]:
    hits = env[model].sudo().search([(field, 'in', targets.ids)])
    assert not hits, f"{model} has {len(hits)} rows referencing these products — refusing to merge/delete, this script is only for a fresh untouched catalog"

# 1. Remove the 2 genuine duplicate imports.
dup_products = Product.search([('default_code', 'in', DUPLICATES_TO_DELETE)])
dup_templates = dup_products.product_tmpl_id
dup_templates.unlink()
print('deleted duplicate templates:', DUPLICATES_TO_DELETE)

# 2. Merge each group into one template with a real variant axis.
for g in GROUPS:
    codes = [v[0] for v in g['variants']]
    products = Product.search([('default_code', 'in', codes)])
    templates = products.product_tmpl_id
    keeper = templates[0]
    others = templates[1:]

    attribute = Attribute.search([('name', '=', g['attribute'])], limit=1)
    assert attribute, f"attribute '{g['attribute']}' not found on this DB"

    value_ids = []
    for _code, label, _extra, _cost in g['variants']:
        val = AttrValue.search([('attribute_id', '=', attribute.id), ('name', '=', label)], limit=1)
        if not val:
            val = AttrValue.create({'attribute_id': attribute.id, 'name': label})
        value_ids.append(val.id)

    # Remove the other SKUs' whole templates first, before assigning their
    # codes onto the new variants below — avoids a stale default_code
    # collision with the record about to take over that SKU's identity.
    # (Do this before touching `keeper` further — `products` still holds
    # ids that just got cascade-deleted, don't read from it again.)
    others.unlink()

    keeper.write({'name': g['name'], 'list_price': g['list_price']})
    line = AttrLine.create({
        'product_tmpl_id': keeper.id,
        'attribute_id': attribute.id,
        'value_ids': [(6, 0, value_ids)],
    })
    keeper._create_variant_ids()

    # _create_variant_ids() archives (doesn't delete) the old no-attribute
    # variant since it no longer matches any combination — unlink it so
    # its default_code is free for the new variant that replaces it.
    stale_variant = Product.search([
        ('product_tmpl_id', '=', keeper.id),
        ('product_template_attribute_value_ids', '=', False),
    ])
    stale_variant.unlink()

    for code, label, extra, cost in g['variants']:
        ptav = env['product.template.attribute.value'].sudo().search([
            ('product_tmpl_id', '=', keeper.id),
            ('product_attribute_value_id.name', '=', label),
        ], limit=1)
        assert ptav, f"no attribute value created for {label} on {g['name']}"
        ptav.price_extra = extra
        variant = Product.search([
            ('product_tmpl_id', '=', keeper.id),
            ('product_template_attribute_value_ids', 'in', ptav.id),
        ], limit=1)
        assert variant, f"no variant created for {label} on {g['name']}"
        variant.default_code = code
        variant.standard_price = cost

    print(f"merged {g['name']}: {codes} -> template {keeper.id}")

env.cr.commit()
print('DONE — committed.')
