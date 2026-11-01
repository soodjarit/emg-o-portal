# คู่มือกดตาม "Setup ระบบ EMG-O" — มาตรฐาน skill emg-o-guide (ทำไมใส่ค่านี้ + ควรเห็น, ไม่มีช่อง ☐ผ่าน).
# Head/CSS/logo = หัวของ guide-boq-import-excel-2026-10-28.html (สร้างจาก build_guide_boq_import.py).
# ข้อมูลและภาพมาจากการเดินจริงบน eg-tst เมื่อ 2026-11-01 (หินตัวอย่าง ZZ2 GUIDE MARBLE).
OLD = open('../guide-boq-import-excel-2026-10-28.html', encoding='utf-8').read()
head = OLD[:OLD.index('<h1>')]
head = head.replace('<title>คู่มือกดตาม BOQ นำเข้า Excel ถึง P&amp;L</title>', '<title>คู่มือกดตาม Setup ระบบ</title>')
head = head.replace('28\\10\\2569', '1\\11\\2569')
head = head.replace('</style>', '.dl{margin:3mm 0 0;font-size:.85rem}.dl a{color:#8a5a2b;font-weight:700}\n@media print{.no-print{display:none !important}}\n</style>', 1)
A = 'assets/guide-setup/'


def table(rows):
    out = ['<div class="mbx-table-wrap"><table class="mbx-table compact">',
           '<thead><tr><th>ข้อ</th><th>ทำอะไร (ค่าที่กรอก)</th><th>ทำไมใส่ค่านี้</th><th>ควรเห็น</th></tr></thead><tbody>']
    for no, do, why, see in rows:
        out.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (no, do, why, see))
    out.append('</tbody></table></div>')
    return '\n'.join(out)


def shot(name, cap):
    return ('<a href="%s%s" target="_blank"><img class="shot" src="%s%s" alt=""></a>'
            '<p class="cap">ตัวอย่างหน้าจอจริง: %s</p>') % (A, name, A, name, cap)


body = []
body.append('''<h1>Setup<br>ระบบ</h1>

  <section class="band">
    <div class="mbx-meta">คู่มือกดตามทีละขั้น<br>สำหรับผู้ใช้งาน · ระบบ eg-tst<br>อัปเดตล่าสุด: 1 พฤศจิกายน 2569</div>
    <p>คุณจะตั้งค่าที่ต้องมี <b>ก่อนเริ่มซื้อ ผลิต และขาย</b> ด้วยข้อมูลตัวอย่างหินหนึ่งชนิด: หมวดสินค้าสำเร็จรูป (FG) · หินตัวอย่างพร้อม Slab / Block / FG · ชุดวัสดุและชุดค่าแรงสำหรับ BOQ · แล้วดูว่าต้นทุนและบัญชี Analytic ตั้งอย่างไร แต่ละขั้นบอกว่ากรอกอะไร <b>ใส่ไปทำไม</b> และควรเห็นอะไรบนจอ ใช้เวลาประมาณ 30 นาที</p>
    <p class="dl no-print"><a href="guide-setup-2026-11-01.pdf" download="คู่มือกดตาม Setup ระบบ.pdf">⬇ ดาวน์โหลดฉบับ PDF (พิมพ์ได้)</a></p>
  </section>

  <h2><small>[00]</small>เตรียมก่อนเริ่ม</h2>
  <div class="mbx-table-wrap"><table class="mbx-table compact">
    <thead><tr><th>เรื่อง</th><th>ที่ต้องมี</th></tr></thead>
    <tbody>
      <tr><td>ระบบ</td><td>eg-tst.mx-erp.com · บริษัทมุมขวาบนต้องเป็น <b>Empire Granite</b></td></tr>
      <tr><td>ข้อมูลตัวอย่าง</td><td>หินชื่อ <b>ZZ2 GUIDE MARBLE</b> รหัสฐาน <b>ZZ2G</b> หมวด Marble · Slab 2,500 บาทต่อ ตร.ม. ต้นทุน 1,300 · Block 15,800 บาทต่อตัน ต้นทุน 12,000 · Density 2.65 · FG 3,800 ต้นทุน 2,000 · ค่าแรง FG 1,500 ต่อหน่วย ชื่อที่ขึ้นต้นด้วย <b>ZZ</b> คือข้อมูลทดสอบ แยกออกจากข้อมูลจริง</td></tr>
      <tr><td>ลำดับตอน</td><td>ทำ <b>ตอน 1 (หมวด FG) ก่อนตอน 2 (สินค้าหิน)</b> เพราะตอน 2 ต้องเลือกหมวด FG ที่ตั้งไว้แล้ว</td></tr>
      <tr><td>หน่วย</td><td>ขนาดแผ่นในหน้า Quick Material Setup กรอกเป็น <b>เมตร</b> (ยาว × กว้าง) ส่วนความหนาเป็น <b>ซม.</b></td></tr>
      <tr><td>เลขและรหัส</td><td>รหัสสินค้า (ZZ2G-SL ฯลฯ) ตั้งตามที่คุณกรอก แต่เลขลำดับอื่นในระบบจะเป็นของคุณเอง ให้ดูตามหน้าจอของคุณ</td></tr>
    </tbody>
  </table></div>
  <p class="mbx-table-note">การทำตามคู่มือนี้สร้างข้อมูลจริงในระบบ eg-tst (ไม่ใช่ระบบใช้งานจริง) ไม่ต้องลบทิ้ง · ถ้าจะทำซ้ำ ให้เปลี่ยนชื่อและรหัสฐาน เช่น ZZ3 GUIDE MARBLE / ZZ3G</p>

  <h2 id="setup-01-fgcat"><small>[01]</small>ตอน 1 · ตั้งหมวดสินค้าสำเร็จรูป (FG)</h2>''')
body.append(table([
 ('1.1', 'เมนู <b>Inventory → Configuration → Categories</b> กด <b>New</b>',
  'หมวดสินค้าเป็นที่เก็บกติกาของ FG ทุกชิ้นในหมวด ว่าติดตามสต็อกแบบไหน ค่าแรงเท่าไร ผลิตผ่านขั้นตอนอะไร ตั้งครั้งเดียวแล้วใช้ซ้ำกับหินทุกชนิด',
  'ฟอร์มหมวดว่าง มีช่อง <b>FG Tracking</b> (ค่าเริ่มต้น Lot) · <b>FG Standard Labor Cost</b> (0.00) และแท็บ <b>FG Production Operations</b>'),
 ('1.2', 'ช่อง Category พิมพ์ <b>ZZ Guide FG - Countertop</b> ส่วน Parent Category เว้นว่าง',
  'ชื่อนี้คือชื่อที่คุณจะเลือกในช่อง FG Category ตอน setup หิน (ตอน 2) · เว้น Parent ว่างไว้แบบเดียวกับหมวดจริง "Stone FG - Countertop"',
  'ชื่อหมวดขึ้นเป็นหัวฟอร์ม'),
 ('1.3', 'ช่อง <b>FG Tracking</b> คงไว้เป็น <b>Lot</b>',
  'Lot = หนึ่ง Lot ต่อรอบผลิตหรือต่อขนาด นับสต็อกเป็นจำนวน เหมาะกับแผ่นตัดตามขนาด · Serial ใช้กับงานชิ้นต่อชิ้นอย่างงานแกะสลัก · <b>เปลี่ยนไม่ได้อีก</b>เมื่อมี FG ในหมวดนี้เคยเคลื่อนไหวสต็อกหรือมีใบสั่งผลิตแล้ว',
  'ค่าเป็น Lot'),
 ('1.4', 'ช่อง <b>FG Standard Labor Cost</b> กรอก <b>1500</b>',
  'ค่าแรงมาตรฐานต่อหน่วยที่ผลิต อัตราเดียวต่อหมวด ไม่คำนวณจากเวลาที่ใช้จริง ระบบลงเป็นต้นทุนเข้า Analytic ตอนปิดงานผลิต FG',
  'ช่องแสดง 1,500.00'),
 ('1.5', 'ส่วน <b>Inventory Valuation</b> (ฝั่งขวา) ช่อง <b>Costing Method</b> เลือก <b>First In First Out (FIFO)</b> ช่อง <b>Inventory Valuation</b> เลือก <b>Perpetual (at invoicing)</b>',
  'ให้ระบบลงต้นทุนขายให้เองตอนออกใบแจ้งหนี้ (เดบิตต้นทุนขาย เครดิตสต็อก FG) · ถ้าปล่อยค่าเริ่มต้น (Standard Price และ Periodic) ใบแจ้งหนี้ของ FG จะไม่มีรายการต้นทุนขายเลย กำไรจึงดูสูงเกินจริง',
  'ช่อง Costing Method แสดง First In First Out (FIFO) · ช่อง Inventory Valuation แสดง Perpetual (at invoicing)'),
 ('1.6', 'ส่วน <b>Account Properties</b> ช่อง <b>Expense Account</b> เลือก <b>511110 COGS - Stone Sales (all modes)</b> ช่อง <b>Stock Account</b> เลือก <b>113150 Inventory - Stone FG (Finished Goods)</b> (ช่อง Income Account คงค่าเริ่มต้น 411100)',
  'ให้ต้นทุนของ FG ที่ผลิตเข้าบัญชีสต็อก FG แยกจากสต็อก Slab และเมื่อขายตัดไปเข้าบัญชีต้นทุนขายเดียวกับหมวด FG จริง (Stone FG - Countertop) · ฝ่ายบัญชีควรยืนยันบัญชีเหล่านี้ก่อนใช้งานจริง',
  'ช่อง Expense Account แสดง 511110 COGS - Stone Sales (all modes) · ช่อง Stock Account แสดง 113150 Inventory - Stone FG (Finished Goods)'),
 ('1.7', 'แท็บ <b>FG Production Operations</b> กด <b>Add a line</b> พิมพ์ <b>Cutting (ตัดตามแบบ)</b> กด Enter แล้วพิมพ์ <b>Edge (ทำขอบ)</b>',
  'เป็นรายการขั้นตอนผลิตเรียงตามลำดับ ระบบคัดลอกเข้า BOM ตอนผลิต FG ครั้งแรกของสินค้านั้น (ตามการออกแบบ ยังไม่ได้ลองผลิตในคู่มือนี้)',
  'ตารางมี 2 แถว Cutting (ตัดตามแบบ) · Edge (ทำขอบ)'),
 ('1.8', 'กด <b>Save</b> (ไอคอนก้อนเมฆข้างชื่อ)',
  'บันทึกแล้วหมวดนี้จึงขึ้นให้เลือกในตอน 2',
  'ชื่อ <b>ZZ Guide FG - Countertop</b> ขึ้นที่แถบนำทางด้านบน · ค่า วิธีคิดต้นทุน บัญชี และ 2 ขั้นตอนอยู่ครบ'),
]))
body.append(shot('s01-category-saved.webp', 'หมวด FG ที่บันทึกแล้ว (ข้อ 1.8)'))
body.append('<p class="mbx-table-note">ฟอร์มหมวดตอนนี้ <b>ยังไม่มีช่องต้นทุนวัสดุสิ้นเปลืองมาตรฐาน</b> (กาว เรซิน ฯลฯ) แม้ระบบมีช่องนี้ในข้อมูล ผู้ใช้จึงตั้งผ่านหน้าจอไม่ได้ และต้นทุนส่วนนี้ถูกคิดเป็น 0 · ถ้าต้องการใช้ ให้แจ้งทีมพัฒนา</p>')

body.append('<h2 id="setup-02-material"><small>[02]</small>ตอน 2 · ตั้งสินค้าหินด้วย Quick Material Setup</h2>')
body.append(table([
 ('2.1', 'เมนู <b>Stone Slab → Tools → Quick Material Setup</b>',
  'หน้าต่างเดียวสร้างทุกอย่างที่หินหนึ่งชนิดต้องมี ไม่ต้องไล่สร้างทีละเมนู',
  'หน้าต่าง Quick Material Setup เลือก <b>สร้าง Material ใหม่</b> ไว้แล้ว'),
 ('2.2', 'Material Name พิมพ์ <b>ZZ2 GUIDE MARBLE</b> · Category เลือก <b>Marble</b>',
  'ชื่อคือชื่อที่ทีมขายเห็นและเลือกตอนทำใบเสนอราคา · หมวดหินใช้จัดกลุ่ม Analytic เพื่อเทียบต้นทุนและกำไรตามหมวด',
  'ทั้งสองช่องมีค่า (ช่องบังคับ)'),
 ('2.3', 'Pricing Mode คงไว้เป็น <b>Serial (per-slab)</b>',
  'Serial ติดตามทีละแผ่น (ค่าเริ่มต้น) · Lot นับเป็นกองสำหรับหินราคาถูก · ตัวเลือก Finish และ FG ใช้ได้เฉพาะ Serial',
  'ค่าเป็น Serial (per-slab)'),
 ('2.4', 'Internal Reference (Base Code) พิมพ์ <b>ZZ2G</b>',
  'ระบบต่อท้ายให้เป็น ZZ2G-SL (Slab) · ZZ2G-BL (Block) · ZZ2G-FG (FG) เว้นว่างได้ แต่ควรกรอกเพื่อค้นหาสินค้าง่าย',
  'ช่องแสดง ZZ2G'),
 ('2.5', 'Density (Ton/CBM) พิมพ์ <b>2.65</b>',
  'ใช้แปลงราคา Block จากบาทต่อตันเป็นบาทต่อลูกบาศก์เมตร ถ้าจะตั้งราคา Block ต้องกรอก',
  'ช่องแสดง 2.65'),
]))
body.append(shot('s02-material-info.webp', 'ข้อมูลหินที่กรอกแล้ว (ข้อ 2.2–2.5)'))
body.append(table([
 ('2.6', 'ราคาขายฐาน Slab (บาทต่อ CBM) พิมพ์ <b>125000</b>',
  'ถ้ากรอก ระบบสร้างตารางราคาตามความหนาให้เอง (125,000 × ความหนาเป็นเมตร) · ถ้าเว้นว่าง ระบบใช้ราคาต่อ ตร.ม. เป็นราคาที่ความหนามาตรฐาน',
  'ช่องแสดง 125,000.00'),
 ('2.7', 'Slab Sales Price พิมพ์ <b>2500</b> · Slab Cost พิมพ์ <b>1300</b> (บาทต่อ ตร.ม.)',
  '2,500 = ราคาขายต่อ ตร.ม. ที่ความหนามาตรฐาน 2 ซม. (125,000 × 0.02) · ต้นทุนใช้คำนวณกำไรของ Slab · แก้ทีหลังได้ที่สินค้า',
  'ทั้งสองช่องแสดงค่าที่กรอก (ช่องบังคับ)'),
 ('2.8', 'ขนาดแผ่นมาตรฐาน คงไว้ <b>3.000 × 1.600</b> เมตร หนา <b>2 cm</b>',
  'ใช้คิดราคาต่อแผ่น และเป็นค่าตั้งต้นของใบสั่งตัด · บังคับกรอก',
  'ค่าเริ่มต้น 3.000 × 1.600 × 2 cm'),
 ('2.9', 'ตาราง Finish คงติ๊ก <b>Polished</b> และ <b>Honed</b> ไว้ ราคาส่วนต่าง 0.00',
  'แต่ละผิวคือ Slab 1 Variant ขายราคาต่างกันได้ ถ้าใส่ราคาส่วนต่าง ระบบบวกเข้าราคาของผิวนั้น (ตามการออกแบบ ยังไม่ได้ลองใส่ค่าในคู่มือนี้) · เลือกผิวได้เฉพาะ Serial',
  'สวิตช์ Polished และ Honed เป็นสีเขียว ผิวอื่นปิดอยู่'),
]))
body.append(shot('s02-slab.webp', 'ส่วน Slab และ Finish (ข้อ 2.6–2.9)'))
body.append(table([
 ('2.10', 'ติ๊กช่อง <b>BLOCK PRODUCT</b> แล้วกรอก Block Sales Price <b>15800</b> · Block Cost <b>12000</b> (บาทต่อตัน)',
  'เปิดให้ขายหินทั้งก้อนได้ · ระบบคูณ Density แปลงเป็นบาทต่อลูกบาศก์เมตร (15,800 × 2.65 = 41,870)',
  'มีช่องราคา Block ให้กรอกเพิ่มหลังติ๊ก'),
 ('2.11', 'ติ๊กช่อง <b>FINISHED GOOD</b> แล้วกรอก FG Category เลือก <b>ZZ Guide FG - Countertop</b> · FG Product Name <b>ZZ2 GUIDE MARBLE Countertop</b> · FG Sales Price <b>3800</b> · FG Cost <b>2000</b>',
  'FG คือสินค้าที่ตัดแล้วขายตามขนาด ต้องอยู่ในหมวด FG จากตอน 1 จึงได้ค่าแรงมาตรฐานและขั้นตอนผลิต · <b>เลือกหมวดจากรายการ</b> ห้ามพิมพ์ชื่อหมวดใหม่ เพราะอาจสร้างหมวดว่างขึ้นมา',
  'หมวด FG แสดง ZZ Guide FG - Countertop'),
]))
body.append(shot('s02-block-fg.webp', 'ส่วน Block และ FG ที่กรอกแล้ว (ข้อ 2.10–2.11)'))
body.append(table([
 ('2.12', 'กด <b>Create All</b>',
  'ระบบสร้างทุกอย่างให้พร้อมกัน แทนการไล่สร้างเองทีละเมนู',
  'เปิดหน้า Material <b>ZZ2 GUIDE MARBLE</b> สถานะใช้งาน · หมวด Marble · Slab Product <b>[ZZ2G-SL]</b> · Block Product <b>[ZZ2G-BL]</b> · ราคาขาย Block 15,800 บาท/ตัน ต้นทุน 12,000 · ความหนาแน่น 2.65'),
]))
body.append(shot('s02-after-create.webp', 'หน้า Material หลังกด Create All (ข้อ 2.12)'))
body.append('''<p class="mbx-table-note"><b>สิ่งที่ระบบสร้างให้</b> (ตรวจแล้วหลังกด Create All):</p>
<div class="mbx-table-wrap"><table class="mbx-table compact">
<thead><tr><th>ของที่ได้</th><th>ผลที่ออกมาในตัวอย่างนี้</th></tr></thead>
<tbody>
<tr><td>สินค้า Slab</td><td>ZZ2 GUIDE MARBLE - Slab ราคา 2,500 ติดตามทีละแผ่น (Serial) มี 2 Variant: <b>ZZ2G-SL</b> (Polished) และ <b>ZZ2G-SL-HON</b> (Honed)</td></tr>
<tr><td>สินค้า Block</td><td><b>ZZ2G-BL</b> หน่วย ลบ.ม. ติดตามเป็น Lot ราคาขาย <b>41,870</b> ต่อ ลบ.ม.</td></tr>
<tr><td>สินค้า FG</td><td><b>ZZ2G-FG</b> หน่วย ตร.ม. ติดตามเป็น Lot ราคา 3,800 อยู่ในหมวด ZZ Guide FG - Countertop</td></tr>
<tr><td>สินค้าภายใน</td><td>"ZZ2 GUIDE MARBLE - Cutting Plan WIP" ระบบสร้างเพิ่มให้ คุณไม่ต้องกรอกอะไรเกี่ยวกับตัวนี้</td></tr>
<tr><td>ตารางราคาตามความหนา</td><td>5 แถวอัตโนมัติ: 1.5 / 2 / 2.5 / 3 / 5 ซม. = <b>1,875 / 2,500 / 3,125 / 3,750 / 6,250</b> ต่อ ตร.ม.</td></tr>
<tr><td>Analytic Account</td><td>ได้ใหม่ 1 ตัวระดับวัสดุ (ZZ2 GUIDE MARBLE) ส่วนระดับหมวดหิน (Marble) ใช้ตัวที่มีอยู่แล้วร่วมกันทุกหินในหมวด</td></tr>
</tbody></table></div>''')
body.append('<p class="mbx-table-note">ถ้าจะเพิ่ม FG ให้หินที่มีอยู่แล้ว เลือก Setup Mode เป็น "ใช้ Material เดิม (เพิ่มแค่ FG)" ระบบจะสร้างเฉพาะ FG ไม่แตะ Slab/Block (ตามการออกแบบ ยังไม่ได้ทดลองในคู่มือนี้)</p>')

body.append('<h2 id="setup-03-boqset"><small>[03]</small>ตอน 3 · ตั้งชุดวัสดุและชุดค่าแรงสำหรับ BOQ</h2>')
body.append(table([
 ('3.1', 'เมนู <b>Inventory → Products → Products</b> กด <b>New</b> สร้างสินค้า <b>ZZ กาวและปูนยาแนวปูพื้น</b> ประเภท <b>Goods</b> เอาติ๊ก <b>Track Inventory</b> ออก · Sales Price <b>150</b> · Cost <b>90</b> · หน่วยท้ายราคา (per Units) เปลี่ยนเป็น <b>m²</b> แล้ว Save',
  'ชุดวัสดุคิดราคาต่อ ตร.ม. ของพื้นหิน สินค้าในชุดจึงต้องมีหน่วย m² · กาวเป็นวัสดุสิ้นเปลือง ไม่ต้องนับสต็อก จึงไม่ติ๊ก Track Inventory',
  'สินค้าบันทึกแล้ว หน่วยเป็น m² ราคา 150 ต้นทุน 90'),
 ('3.2', 'สร้างสินค้าอีกตัว <b>ZZ ค่าแรงติดตั้งพื้น</b> ประเภท <b>Service</b> · Sales Price <b>800</b> · Cost <b>500</b> · หน่วย <b>m²</b> แล้ว Save',
  'ค่าแรงติดตั้งหน้างานเป็นบริการ ไม่มีสต็อก · ราคาขายคือที่เรียกเก็บลูกค้า ต้นทุนคือที่จ่ายให้ช่าง',
  'สินค้าบันทึกแล้ว ประเภท Service หน่วย m²'),
]))
body.append(shot('s03-glue-product.webp', 'ฟอร์มสินค้ากาวที่กรอกแล้ว (ข้อ 3.1)'))
body.append(table([
 ('3.3', 'เมนู <b>BOQ Estimation → Consumable Sets</b> กด <b>New</b> Name <b>ZZ ชุดวัสดุพื้นมาตรฐาน</b> · Type เลือก <b>วัสดุสิ้นเปลือง</b> · กด Add a line เลือก <b>ZZ กาวและปูนยาแนวปูพื้น</b> แล้ว Save',
  'ชนิด "วัสดุสิ้นเปลือง" ไปอยู่ฝั่งวัสดุของใบเสนอราคา · ราคาและต้นทุนต่อ ตร.ม. ดึงจากสินค้ามาให้เอง · เว้น Company ว่าง = ใช้ร่วมทุกบริษัท',
  'แถวสินค้ามีหน่วย m² · Price/m² <b>150.00</b> · Cost/m² <b>90.00</b> · มุมบนขวา Total/m² <b>150.00</b>'),
]))
body.append(shot('s03-set-material.webp', 'ชุดวัสดุที่บันทึกแล้ว (ข้อ 3.3)'))
body.append(table([
 ('3.4', 'กด New อีกครั้ง Name <b>ZZ ชุดค่าแรงติดตั้งพื้น</b> · Type เลือก <b>ค่าแรงติดตั้งหน้างาน</b> · Add a line เลือก <b>ZZ ค่าแรงติดตั้งพื้น</b> แล้ว Save',
  'ชนิด "ค่าแรงติดตั้งหน้างาน" ไปอยู่ฝั่งค่าแรงของใบเสนอราคา แยกจากวัสดุ ทีมขายจึงเลือกชุดวัสดุและชุดค่าแรงได้อิสระต่อกัน',
  'Price/m² <b>800.00</b> · Cost/m² <b>500.00</b> · Total/m² <b>800.00</b>'),
]))
body.append(shot('s03-set-labor.webp', 'ชุดค่าแรงที่บันทึกแล้ว (ข้อ 3.4)'))
body.append('<p class="mbx-table-note">ชุดทั้งสองนี้ทีมขายเลือกเป็น "ชุดวัสดุตั้งต้น / ชุดค่าแรงตั้งต้น" ที่ BOQ แต่ละใบ แล้วกด "ดึงโซนจาก BOQ" และ "สร้างค่าแรง/วัสดุ" ที่แท็บ "② ค่าแรง &amp; วัสดุ" ระบบคิดวัสดุและค่าแรงต่อ ตร.ม. ของแต่ละโซนให้ (ทดลองแล้ว: พื้นที่ 10 ตร.ม. ได้วัสดุสิ้นเปลือง 1,500 และค่าแรง 8,000 เข้าไปในใบเสนอราคา ดูเคสตรวจผลใน <a href="test-cases-golden-path-setup.html">Golden Path Setup ระบบ</a>) · จะนำเข้ารายการจาก Excel ต่อ ดูคู่มือ <a href="guide-boq-import-excel-2026-10-28.html">BOQ นำเข้า Excel ถึง P&amp;L</a></p>')

body.append('<h2 id="setup-04-cost"><small>[04]</small>ตอน 4 · ดูการตั้งค่าต้นทุนและบัญชี (ดูอย่างเดียว)</h2>')
body.append('<p class="mbx-table-note">ตอนนี้เป็นการ <b>ดูว่าตั้งอะไรไว้ที่ไหน</b> ไม่มีการกรอกหรือแก้ข้อมูล เพราะสินค้าและบัญชีเหล่านี้ใช้ร่วมกับการทดสอบอื่น ผู้ดูแลระบบหรือฝ่ายบัญชีเป็นผู้ตั้งค่าจริง</p>')
body.append(table([
 ('4.1', 'เมนู <b>Inventory → Products → Products</b> ค้นหา <b>Landed Cost</b> เปิดสินค้า <b>Landed Cost - Container Freight/Duty</b> แล้วเปิดแท็บ <b>Accounting</b>',
  'สินค้านี้เป็นตัวแทนค่าขนส่งและภาษีนำเข้า ที่ระบบกระจายเข้าต้นทุน Block ตามปริมาตร · ต้องตั้ง <b>บัญชีค่าใช้จ่าย (Expense Account) แยกต่อบริษัท</b> ให้ตรงกับบัญชีที่ใช้ลงค่าขนส่งใน Vendor Bill',
  'ช่อง <b>Expense Account ว่างอยู่</b> ในระบบ eg-tst ตอนนี้ (ยังไม่ได้ตั้งค่า)'),
 ('4.2', 'เมนู <b>Accounting → Configuration → Analytic Accounts</b>',
  'Analytic Account คือป้ายต้นทุนที่ใช้ดูกำไรขาดทุนแยกตามหมวดหิน วัสดุ Container Block หรือโครงการ ส่วนใหญ่ระบบสร้างและติดป้ายให้เอง ผู้ดูแลตั้งเองเฉพาะ Analytic แผนก',
  'รายการแยกตามคอลัมน์ Plan: <b>Project</b> · <b>Department</b> (Accounting, Production, Sale, Warehouse) · <b>Material Category</b> (Granite, Limestone ฯลฯ) · <b>Materials</b> · Import Group · Block · พิมพ์ ZZ GUIDE ในช่องค้นหาจะเจอบัญชีที่ตอน 2 สร้างให้ อยู่ในแผน <b>Materials</b>'),
]))
body.append(shot('s04-landed-accounting.webp', 'แท็บ Accounting ของสินค้า Landed Cost ช่อง Expense Account ยังว่าง (ข้อ 4.1)'))
body.append(shot('s04-analytic-accounts.webp', 'รายการ Analytic Account แยกตาม Plan (ข้อ 4.2)'))
body.append('<p class="mbx-table-note">ที่ eg-tst ช่อง Expense Account นี้ว่างอยู่ แต่การลงต้นทุนตู้ตัวอย่างใน <a href="guide-container-2026-11-01.html">คู่มือกดตาม ตู้คอนเทนเนอร์</a> ทำงานถูกต้อง (ย้ายค่าขนส่งจากบัญชี 511100 เข้าสต็อก Block) ฝ่ายบัญชีควรยืนยันว่าจะตั้งบัญชีนี้สำหรับใช้งานจริงหรือไม่ · การผูก Vendor Bill ค่าขนส่งกับ Container ไม่อยู่ในคู่มือนี้</p>')

body.append('''<h2><small>[05]</small>ข้อควรรู้</h2>
  <div class="mbx-table-wrap"><table class="mbx-table compact">
    <thead><tr><th>เรื่อง</th><th>รายละเอียด</th></tr></thead>
    <tbody>
      <tr><td>ข้อมูลที่สร้างจากคู่มือนี้</td><td>หมวด ZZ Guide FG - Countertop · หิน ZZ2 GUIDE MARBLE (พร้อม Slab / Block / FG / ตารางราคา / Analytic) · สินค้า ZZ กาวและปูนยาแนวปูพื้น · ZZ ค่าแรงติดตั้งพื้น · ชุด ZZ ชุดวัสดุพื้นมาตรฐาน · ZZ ชุดค่าแรงติดตั้งพื้น ไม่ต้องลบทิ้ง</td></tr>
      <tr><td>ต้นทุนวัสดุสิ้นเปลือง FG</td><td>ฟอร์มหมวดยังไม่มีช่องให้ตั้ง (ดูหมายเหตุหลังตอน 1)</td></tr>
      <tr><td>Lot กับ Serial ของ FG</td><td>เปลี่ยนไม่ได้อีกเมื่อมี FG ในหมวดเคลื่อนไหวสต็อกหรือมีใบสั่งผลิตแล้ว ตัดสินใจก่อนเริ่มใช้งาน</td></tr>
      <tr><td>แก้ราคาทีหลัง</td><td>ราคาและต้นทุน Slab และ FG แก้ได้ที่สินค้าแต่ละตัว ไม่ต้องทำ setup ใหม่</td></tr>
      <tr><td>Block และ Slab ไม่ต้อง setup เอง</td><td>Block เกิดตอนยืนยันใบรับของจากใบสั่งซื้อ Slab เกิดจากการตัด Block (ตามเอกสาร Block และ Slab ในคู่มือ)</td></tr>
      <tr><td>ที่ยังไม่อยู่ในคู่มือนี้</td><td>Setup FG แบบกำหนดเอง (เจดีย์บัว โคม) · การตั้งบัญชีค่าใช้จ่ายของ Landed Cost · การผูก Vendor Bill กับ Container</td></tr>
      <tr><td>ถ้าเจอปัญหา</td><td>ส่งภาพหน้าจอ พร้อมบอกว่าอยู่ข้อไหน</td></tr>
    </tbody>
  </table></div>

  <h3>บันทึกของผู้ใช้งาน</h3>
  <div class="noteBox"></div>

  <div class="footer mbx-meta"><span>Empire Granite · EMG-O</span><span>หน้า 1</span></div>
</article>
</body>
</html>
''')
out = head + '\n'.join(body)
open('../guide-setup-2026-11-01.html', 'w', encoding='utf-8').write(out)
print('wrote', len(out))
