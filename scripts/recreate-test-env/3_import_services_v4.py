# Run inside odoo shell. 73 service products from client sheet 12 (v4 returned 2026-11-06). Additive; skips existing codes.
import json
DRY_RUN = __DRY__
data = json.load(open('/mnt/extra-addons/.import_services.json'))
T = env['product.template']; cat = env.ref('product.product_category_services', raise_if_not_found=False) or env['product.category'].browse(3)
units = env.ref('uom.product_uom_unit')
made = skipped = 0
for m in data:
    if T.search([('default_code', '=', m['code'])], limit=1):
        skipped += 1; continue
    T.create({'name': m['name'], 'default_code': m['code'], 'type': 'service', 'categ_id': cat.id, 'uom_id': units.id,
              'sale_ok': True, 'purchase_ok': False, 'list_price': 0.0, 'standard_price': 0.0,
              'description': '<p>กลุ่ม SAP: %s · ประเภทที่เสนอ: %s<br/>บัญชีรายได้ที่ลูกค้าระบุ: %s %s (ยังไม่ผูก — รอผังบัญชีสุดท้าย ขายลง 411100 ไปก่อน)</p>' % (m['sap_group'], m['kind'], m['rev'], m['rev_name'])})
    made += 1
print('services created', made, 'skipped', skipped, 'dry', DRY_RUN)
if DRY_RUN: env.cr.rollback()
else: env.cr.commit()
