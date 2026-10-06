import traceback
try:
    for c in env['res.company'].search([('name', 'in', ['Empire Granite', 'Empire Stone'])]):
        j = env['account.journal'].search([('company_id', '=', c.id), ('code', '=', 'STJ')], limit=1)
        for cat in env['product.category'].search([]):
            cc = cat.with_company(c)
            if not cc.property_stock_journal:
                cc.property_stock_journal = j
    env.cr.commit(); print('JOURNALS set')
except Exception:
    traceback.print_exc(); env.cr.rollback()
try:
    for c in env['res.company'].search([('name', 'in', ['Empire Granite', 'Empire Stone'])]):
        c.account_stock_journal_id = env['account.journal'].search([('company_id', '=', c.id), ('code', '=', 'STJ')], limit=1)
    env.cr.commit(); print('COMPANY STOCK JOURNAL set')
except Exception:
    traceback.print_exc(); env.cr.rollback()
