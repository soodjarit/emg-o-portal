# Thai UI for EMG-O: install th_TH, translate our custom menus (keep Block / Slab / FG as-is), set Thai for client users.
TH = {
 'stone_slab_inventory': {454:'งานหิน (Stone Slab)',463:'แจ้งเตือนการวางบิล',457:'Block',468:'ตั้งค่า',469:'วัสดุหิน (Material)',456:'ตู้คอนเทนเนอร์',
   455:'แดชบอร์ด',462:'ตรวจวางเรียง (Dry-lay QC)',461:'FG',471:'รายงาน',473:'อนุมัติราคา',472:'ส่วนต่างราคา Slab',458:'Slab',459:'Slab ทั้งหมด',
   460:'Slab รอตรวจ',464:'เครื่องมือ',465:'กระทบยอดระหว่างบริษัท',467:'Gantt โครงการ',466:'ตั้งค่า Material ด่วน'},
 'boq_estimation': {474:'ประมาณราคา BOQ',475:'เอกสาร BOQ'},
}
Lang = env['res.lang'].with_context(active_test=False)
lang = Lang.search([('code','=','th_TH')], limit=1)
if not lang.active:
    env['base.language.install'].create({'lang_ids':[(6,0,lang.ids)],'overwrite':False}).lang_install()
    env.cr.commit()
print('th_TH active:', Lang.search([('code','=','th_TH')]).active)
Menu = env['ir.ui.menu'].with_context(lang=None)
for mod, mp in TH.items():
    for mid, th in mp.items():
        m = Menu.browse(mid).exists()
        if m: m.update_field_translations('name', {'th_TH': th})
users = env['res.users'].search([('login','in',['emgdemo','emgtest','egsale'])])
users.write({'lang':'th_TH'})
env.cr.commit()
print('users set Thai:', users.mapped('login'))
for mid in (454,457,461,473):
    print(mid, env['ir.ui.menu'].with_context(lang='th_TH').browse(mid).name)
