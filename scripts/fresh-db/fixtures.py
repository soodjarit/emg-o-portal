"""Demo fixtures for eg-tst after the ADR-087 cutover (run inside `odoo shell -d eg-tst`).

Creates 3 partners and 3 Blocks of 3 serial materials; the first two Blocks are cut into
Slab lots with a Cut Order (3.0 x 1.6 m), the third stays a Block.
"""
import traceback
try:
    eg = env['res.company'].search([('name', '=', 'Empire Granite')], limit=1)
    env = env(context=dict(env.context, allowed_company_ids=[eg.id]), user=env.ref('base.user_admin'))
    env.user.company_id = eg
    wh = env['stock.warehouse'].search([('code', '=', 'EG01')], limit=1)
    P = env['res.partner']
    sup = P.search([('name', '=', 'Demo Stone Supplier')], limit=1) or P.create({'name': 'Demo Stone Supplier', 'supplier_rank': 1, 'is_company': True})
    P.search([('name', '=', 'Demo Hotel Customer')], limit=1) or P.create({'name': 'Demo Hotel Customer', 'customer_rank': 1, 'is_company': True})
    P.search([('name', '=', 'Demo Pagoda Temple')], limit=1) or P.create({'name': 'Demo Pagoda Temple', 'customer_rank': 1, 'is_company': True})
    mats = env['stone.material'].search([('pricing_mode', '=', 'serial'), ('product_id_block', '!=', False)], limit=3)
    out = []
    for i, m in enumerate(mats):
        b = env['stone.bundle'].create({
            'supplier_id': sup.id, 'material_id': m.id, 'warehouse_id': wh.id,
            'sales_price_sqmt': 1800.0, 'sales_price_cbm': 90000.0,
            'block_length_m': 3.0, 'block_width_m': 1.6, 'block_height_m': 0.3 if i < 2 else 0.6})
        if i < 2:
            mo = env['sale.order.line']._stone_create_cut_order_mo(b, 3.0, 1.6, link_to_line=False, production_reason='extra_work')
            mo.action_stone_move_to_production(); mo.action_confirm(); mo.action_stone_mark_done()
        out.append((b.name, m.name))
    env.cr.commit()
    lots = env['stock.lot'].search([('stone_bundle_id', '!=', False)])
    print('BUNDLES', out)
    print('SLAB LOTS', len(lots), sorted(set(lots.mapped('stone_state'))))
except Exception:
    traceback.print_exc(); env.cr.rollback()
