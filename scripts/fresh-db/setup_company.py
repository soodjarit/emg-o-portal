import traceback
try:
    thb = env.ref('base.THB'); thb.active = True
    th = env.ref('base.th')
    Company = env['res.company']
    def mk(name, vat=False):
        c = Company.search([('name', '=', name)], limit=1) or Company.create(
            {'name': name, 'currency_id': thb.id, 'country_id': th.id, 'vat': vat})
        return c
    eg = mk('Empire Granite', '0105534018100')
    es = mk('Empire Stone')
    env['res.users'].browse(2).write({'company_ids': [(4, eg.id), (4, es.id)]})
    for c in (eg, es):
        env['account.chart.template'].with_company(c).try_loading('th', company=c, install_demo=False)
    for c, code in ((eg, 'EG01'), (es, 'ES01')):
        if not env['stock.warehouse'].search([('company_id', '=', c.id)]):
            env['stock.warehouse'].with_company(c).create({'name': '%s Warehouse' % c.name, 'code': code, 'company_id': c.id})
    # users
    grp = lambda x: env.ref('stone_slab_inventory.' + x)
    internal = env.ref('base.group_user')
    def user(login, name, pw, groups):
        u = env['res.users'].search([('login', '=', login)], limit=1)
        vals = {'name': name, 'login': login, 'password': pw, 'company_id': eg.id,
                'company_ids': [(6, 0, [eg.id, es.id])],
                'group_ids': [(4, internal.id)] + [(4, grp(g).id) for g in groups] +
                             [(4, env.ref('stock.group_production_lot').id)]}
        if u: u.write(vals)
        else: u = env['res.users'].with_context(no_reset_password=True).create(vals)
        return u
    user('emgdemo', 'EMG Demo', 'demo0emg', ['group_emgo_internal_manager', 'group_emgo_factory', 'group_emgo_sale_supervisor', 'group_emgo_cost_controller'])
    user('emgtest', 'EMG Test', 'demo0emg', ['group_emgo_internal_manager', 'group_emgo_factory', 'group_emgo_sale_supervisor'])
    user('egsale', 'EG Sale', 'demo0emg', ['group_emgo_internal_manager', 'group_emgo_factory', 'group_emgo_sale_supervisor'])
    env['res.users'].browse(2).write({'password': 'sy@odoo', 'group_ids': [(4, grp(g).id) for g in ('group_emgo_internal_manager', 'group_emgo_factory', 'group_emgo_sale_supervisor', 'group_emgo_cost_controller')]})
    env.cr.commit()
    print('COMPANIES', [(c.id, c.name) for c in Company.search([])])
    print('WH', [(w.code, w.company_id.name, bool(w.stone_available_location_id)) for w in env['stock.warehouse'].search([])])
except Exception:
    traceback.print_exc(); env.cr.rollback()
