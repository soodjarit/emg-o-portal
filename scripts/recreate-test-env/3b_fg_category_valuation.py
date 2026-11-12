C = env['product.category']
ref = C.browse(620).with_company(2)
print('ref620', ref.property_cost_method, ref.property_valuation, ref.property_stock_valuation_account_id.display_name)
for c in C.browse([535,536,537,538,539,540]):
    c = c.with_company(2)
    c.write({'property_cost_method': ref.property_cost_method, 'property_valuation': ref.property_valuation,
             'property_stock_valuation_account_id': ref.property_stock_valuation_account_id.id})
env.cr.commit()
for c in C.browse([535,536,537,538,539,540,620]).with_company(2):
    print(c.id, c.property_cost_method, c.property_valuation, c.property_stock_valuation_account_id.code)
