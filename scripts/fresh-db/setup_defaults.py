import traceback
try:
    M = env['stone.material']
    M.search([('default_slab_l', '=', 0)]).write({'default_slab_l': 3.0, 'default_slab_h': 1.6, 'default_thickness_key': '20', 'default_slab_thickness_m': 0.02})
    if not M.search([('pricing_mode', '=', 'lot')]):
        w = env['stone.material.setup.wizard'].create({
            'setup_mode': 'new_material', 'material_name': 'DEMO Onyx (Lot-Mode)', 'material_category': 'marble',
            'pricing_mode': 'lot', 'base_code': 'DEMO-ONYX', 'density_ton_per_cbm': 2.7,
            'slab_l': 1.0, 'slab_h': 2.0, 'slab_thickness_key': '20', 'slab_sales_price': 2000.0, 'slab_cost': 1000.0})
        w.attr_value_line_ids.write({'selected': False})
        w.action_confirm()
    env.cr.commit()
    print('MAT', M.read_group([], ['pricing_mode'], ['pricing_mode']) and [(m.pricing_mode, m.default_slab_l) for m in M.search([('pricing_mode', '=', 'lot')])])
except Exception:
    traceback.print_exc(); env.cr.rollback()

# Work orders need (a) the Manufacturing "Work Orders" setting and (b) an employee linked to the
# user in the MO's own company, otherwise Start fails with "link this user to an employee of this company".
try:
    if not env.ref('base.user_admin').has_group('mrp.group_mrp_routings'):
        env['res.config.settings'].create({'group_mrp_routings': True}).execute()
    # Lot/Serial column on Details popups (the delivery scan check needs to show which lot each row is)
    if not env.ref('base.user_admin').has_group('stock.group_production_lot'):
        env['res.config.settings'].create({'group_stock_production_lot': True}).execute()
    admin = env.ref('base.user_admin')
    for company in env['res.company'].search([('id', '!=', 1)]):
        Emp = env['hr.employee'].with_context(allowed_company_ids=[company.id])
        if not Emp.search([('user_id', '=', admin.id), ('company_id', '=', company.id)]):
            Emp.create({'name': 'Administrator (%s)' % company.name, 'user_id': admin.id, 'company_id': company.id})
    env.cr.commit()
    print('EMPLOYEES', env['hr.employee'].search_count([('user_id', '=', admin.id)]))
except Exception:
    traceback.print_exc(); env.cr.rollback()
