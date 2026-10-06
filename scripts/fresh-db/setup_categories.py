import traceback
try:
    Acc = env['account.account']; Categ = env['product.category']
    companies = env['res.company'].search([('name', 'in', ['Empire Granite', 'Empire Stone'])])
    spec = {  # code: (name, type)
        '113110': ('Inventory - Stone Blocks (Raw)', 'asset_current'),
        '113120': ('Inventory - Stone Slabs (Ready-Made)', 'asset_current'),
        '113150': ('Inventory - Stone FG (Finished Goods)', 'asset_current'),
        '511110': ('COGS - Stone Sales (all modes)', 'expense_direct_cost'),
        # looked up BY NAME by mrp_production._get_stone_labor_cost_account / _get_stone_consumable_cost_account
        '511120': ('COGS - FG Production (Fabrication)', 'expense_direct_cost'),
        '511130': ('COGS - FG Production (Consumables)', 'expense_direct_cost'),
    }
    acc = {}
    for c in companies:
        for code, (name, typ) in spec.items():
            a = Acc.with_company(c).search([('code', '=', code), ('company_ids', 'in', c.id)], limit=1)
            if not a:
                a = Acc.with_company(c).create({'code': code, 'name': name, 'account_type': typ, 'company_ids': [(6, 0, [c.id])]})
            acc[(c.id, code)] = a
    def categ(name, labor=0, tracking='lot', consumable=0):
        cat = Categ.search([('name', '=', name)], limit=1) or Categ.create({'name': name})
        cat.write({'stone_fg_tracking': tracking, 'stone_fg_labor_cost': labor, 'stone_fg_consumable_cost': consumable})
        for c in companies:
            cc = cat.with_company(c)
            cc.property_valuation = 'real_time'
            cc.property_cost_method = 'fifo'
        return cat
    stone = categ('Stone')
    block = categ('Stone - Block'); block.parent_id = False
    fg = categ('Stone FG - Countertop', labor=1500, consumable=100)   # placeholders; cost floor of 50% tops up (fg_min_cost_ratio)
    for cat, code in ((stone, '113120'), (block, '113110'), (fg, '113150')):
        for c in companies:
            cc = cat.with_company(c)
            cc.property_stock_valuation_account_id = acc[(c.id, code)]
            cc.property_account_expense_categ_id = acc[(c.id, '511110')]
    custom = Categ.search([('name', '=', 'Stone FG - Custom')], limit=1)
    custom.stone_fg_labor_cost = 10000.0   # placeholder per piece
    for c in companies:
        cc = custom.with_company(c)
        cc.property_valuation = 'real_time'; cc.property_cost_method = 'fifo'
        cc.property_stock_valuation_account_id = acc[(c.id, '113150')]
        cc.property_account_expense_categ_id = acc[(c.id, '511110')]
    env.cr.commit()
    print('CATEG', Categ.search([]).mapped('name'))
except Exception:
    traceback.print_exc(); env.cr.rollback()
