# Click-along (self-test) guide for the BOQ flow: Import Excel -> quotation -> FG order -> delivery -> invoice -> cost + P&L.
# Template = head/CSS/logo of the 25 Oct lobby-lamps guide (archived). Steps verified in the live run of 2026-10-28 (see qa_data_golden_path_boq_import.py).
import re
OLD = open('../guide-boq-lobby-lamps-2026-10-25.html', encoding='utf-8').read()
head = OLD[:OLD.index('<h1>')]
head = head.replace('<title>คู่มือกดตาม BOQ พื้นและโคม</title>', '<title>คู่มือกดตาม BOQ นำเข้า Excel ถึง P&amp;L</title>')
head = head.replace('25\\10\\2569', '28\\10\\2569')
head = head.replace('</style>', '.shot{display:block;width:100%;max-width:150mm;margin:3mm 0 5mm;border:1px solid #d8d4c8;border-radius:3px}\n.cap{font-size:.78rem;color:#7a7a7a;margin:0}\nh2,h3{break-after:avoid;page-break-after:avoid}\ntr,.shot{break-inside:avoid}\n</style>', 1)
A = 'assets/golden-path-boq-import/'
CK = '<td class="ck">☐ ผ่าน ☐ ไม่ผ่าน</td>'

def table(rows):
    out = ['<div class="mbx-table-wrap"><table class="mbx-table compact">',
           '<thead><tr><th>ข้อ</th><th>ทำอะไร</th><th>ควรเห็น</th><th>ผล</th></tr></thead><tbody>']
    for no, do, see in rows:
        out.append('<tr><td>%s</td><td>%s</td><td>%s</td>%s</tr>' % (no, do, see, CK))
    out.append('</tbody></table></div>')
    return '\n'.join(out)

def shot(name, cap):
    return '<img class="shot" src="%s%s" alt=""><p class="cap">ตัวอย่างหน้าจอจริง: %s</p>' % (A, name, cap)

body = []
body.append('''<h1>BOQ<br>นำเข้า Excel</h1>

  <section class="band">
    <div class="mbx-meta">คู่มือกดตามทีละขั้น<br>สำหรับผู้ทดสอบ · ระบบ eg-tst<br>อัปเดตล่าสุด: 28 ตุลาคม 2569</div>
    <p>คุณจะนำรายการงานจากไฟล์ Excel เข้าเป็น BOQ ใบใหม่ ออกใบเสนอราคา ผลิต FG ตามขนาดที่สั่ง ส่งของ ออกใบแจ้งหนี้ แล้วดู <b>ต้นทุนที่เกิดขึ้นจริง</b> และ <b>P&amp;L</b> ของงานนี้ ทุกขั้นมีช่อง ☐ ผ่าน / ☐ ไม่ผ่าน ไว้ติ๊กตอนกด ใช้เวลาประมาณ 30 นาที</p>
  </section>

  <h2><small>[00]</small>เตรียมก่อนเริ่ม</h2>
  <div class="mbx-table-wrap"><table class="mbx-table compact">
    <thead><tr><th>เรื่อง</th><th>ที่ต้องมี</th></tr></thead>
    <tbody>
      <tr><td>ระบบ</td><td>eg-tst.mx-erp.com · บริษัทมุมขวาบนต้องเป็น <b>Empire Granite</b></td></tr>
      <tr><td>ลูกค้า</td><td>Demo Hotel Customer</td></tr>
      <tr><td>ไฟล์ตัวอย่าง</td><td><a href="assets/golden-path-boq-import/boq-import-sample.xlsx">boq-import-sample.xlsx</a> (ดาวน์โหลดเก็บไว้ก่อน) มี 2 บรรทัด: พื้นล็อบบี้หินดำ NERO RUSTENBURG (Polished) ขนาด 50 × 90 ซม. หนา 2 ซม. รวม 9 ตร.ม. (20 ชิ้น) และค่าขนส่งและติดตั้ง 15,000 บาท<br>หรือจะกรอกเองจากเทมเพลตในตอน 1 ก็ได้ ใช้ค่าตามตัวอย่างเพื่อให้ตัวเลขตรงกับคู่มือ</td></tr>
      <tr><td>ชุดไฟล์ตัวอย่างเพิ่มเติม</td><td>ใน Library (หมวดตัวอย่างไฟล์) มีชุดโรงแรม 2 ไฟล์ ใช้ทดสอบต่อได้: <a href="../client-docs/example-boq/boq-import-example-hotel.xlsx">BOQ โรงแรม</a> (ล็อบบี้ + ผนังลิฟต์) และ <a href="../client-docs/example-boq/cutlist-import-example-hotel-cm.xlsx">Cut List โรงแรม</a> (ใช้คู่กัน ชื่อโซนตรงกัน) ขนาดทุกช่องเป็น ซม.</td></tr>
      <tr><td>ราคาในเคสนี้</td><td>แผ่นหินดำ 12,000 ต่อตร.ม. · ค่าแรง 800 ต่อตร.ม. · Overhead 10%</td></tr>
      <tr><td>เลขที่เอกสาร</td><td>เลข BOQ / ใบขาย / ใบสั่งผลิต ในคู่มือ (BOQ0876, S01438 ฯลฯ) เป็นของรอบที่ทดสอบไว้ ของคุณจะได้เลขใหม่ ให้ดูตามเลขของคุณเอง</td></tr>
    </tbody>
  </table></div>
  <p class="mbx-table-note">การทดสอบนี้สร้างเอกสารจริงในระบบ eg-tst (ใช้ Slab จากคลัง) ไม่ต้องลบทิ้ง แต่ให้ทำในลูกค้าทดสอบ Demo Hotel Customer เท่านั้น</p>

  <h2><small>[01]</small>ตอน 1 · นำเข้า BOQ จาก Excel</h2>''')
body.append(table([
 ('1.1', 'เมนู <b>BOQ Estimation → BOQ Documents</b> กดปุ่ม <b>Import Excel</b> เลือก <b>ลูกค้า = Demo Hotel Customer</b> แล้วกด <b>ดาวน์โหลดเทมเพลต</b> (ข้ามได้ถ้าใช้ไฟล์ตัวอย่างข้างบน)', 'ได้ไฟล์ BOQ-Items-Template.xlsx ที่หัวตาราง: Zone / รายการ / สินค้าหิน / กว้าง (ซม.) / ยาว (ซม.) / หนา (ซม.) / จำนวน / หน่วย / ราคาวัสดุ/หน่วย / ค่าแรง/หน่วย / Overhead %<br><b>ระวัง:</b> ถ้ายังไม่เลือกลูกค้า ปุ่มดาวน์โหลดไม่ทำงาน ขึ้นข้อความ "Missing required fields"'),
 ('1.2', 'ในไฟล์ กรอก 2 บรรทัดตามตัวอย่าง: (1) Zone ล็อบบี้ · รายการ พื้นล็อบบี้ หินดำ ขัดมัน · สินค้าหิน <b>NERO RUSTENBURG (Polished)</b> (เลือกจาก dropdown ห้ามพิมพ์เอง) · กว้าง 50 · ยาว 90 · หนา 2 (ทุกช่องเป็น ซม.) · จำนวน 9 · หน่วย ตร.ม. · ค่าแรง 800 (2) Zone ล็อบบี้ · รายการ ค่าขนส่งและติดตั้ง · จำนวน 1 · หน่วย ชิ้น · ราคาวัสดุ 15,000 (ไม่เลือกสินค้า)', 'บรรทัดที่ 2 ไม่เลือกสินค้าได้ เพราะเป็นงานบริการ · 9 ตร.ม. ÷ แผ่นละ 0.45 ตร.ม. = 20 ชิ้นพอดี'),
 ('1.3', 'กลับหน้าต่าง Import Excel กด <b>Upload your file</b> เลือกไฟล์ แล้วกด <b>อ่านไฟล์</b>', 'หน้าตัวอย่างไม่มีแถวติดข้อผิดพลาด · จำนวนรายการ <b>2</b> · วัสดุรวม <b>123,000.00</b> · ค่าแรงรวม <b>7,200.00</b> · Overhead รวม <b>13,020.00</b> · รวม <b>143,220.00</b> · มีปุ่ม "สร้าง BOQ"'),
 ('1.4', 'กด <b>สร้าง BOQ</b>', 'เปิด BOQ ใบใหม่ (เช่น BOQ0876) ลูกค้า Demo Hotel Customer · 2 บรรทัดโซนล็อบบี้: พื้น 9.00 ตร.ม. ราคา/หน่วย 12,800 (วัสดุ 12,000 + แรง 800) รวม 115,200 · ค่าขนส่ง 15,000<br>ด้านล่าง: Direct Cost <b>130,200</b> · Overhead &amp; Profit <b>13,020</b> · Total <b>143,220</b>'),
]))
body.append(shot('gp-boq-03-wizard-preview.webp', 'หน้าตัวอย่างก่อนสร้าง BOQ (ข้อ 1.3)'))
body.append('<p class="mbx-table-note">ทุกครั้งที่นำเข้าจะได้ BOQ <b>ใบใหม่</b>เสมอ ไม่ทับหรือเติมเข้า BOQ เดิม · "Direct Cost" ใน BOQ คือวัสดุ + ค่าแรงที่ตั้งราคาขาย ไม่ใช่ต้นทุนจริงของโรงงาน ต้นทุนจริงดูในตอน 5</p>')

body.append('<h2><small>[02]</small>ตอน 2 · ออกใบเสนอราคาและ Confirm</h2>')
body.append(table([
 ('2.1', 'ที่ BOQ กดปุ่ม <b>สร้างใบเสนอราคา</b>', 'เปิดใบเสนอราคาใหม่ (เช่น S01438) ช่อง BOQ Document ชี้กลับ BOQ ของคุณ · มีบรรทัดค่าขนส่ง 15,000 · บรรทัดพื้น 9.00 ตร.ม. ราคา 12,800 รวม 115,200 · บรรทัด "ค่าบริหารโครงการ (10% ของยอดงานรวม)" 13,020 · ก่อน VAT <b>143,220.00</b> VAT 7% 8,064.00 รวม <b>151,284.00</b>'),
 ('2.2', 'ดูคอลัมน์ "สต็อก FG ตรงขนาด" ของบรรทัดพื้น', 'ขึ้น <b>ตรงขนาด 0.00 ตร.ม.</b> (ยังไม่มี FG ขนาด 0.5 × 0.9 ในคลัง จึงต้องผลิต)'),
 ('2.3', 'ที่บรรทัดพื้น กดไอคอน <b>รายชิ้น</b> (รูปรายการ) ท้ายแถว แล้วปิดหน้าต่าง', 'มี 1 รายการชิ้น กว้าง <b>50.00 ซม.</b> ยาว <b>90.00 ซม.</b> จำนวน <b>20</b> ชิ้น รวม 9.00 ตร.ม. (ขนาดติดมาจาก BOQ ไม่ต้องกรอกซ้ำ)'),
 ('2.4', 'ติ๊ก <b>Sold as Project</b> กด Save แล้วกด <b>Confirm</b>', 'สถานะเป็น Sales Order · ช่อง Project เติมเป็น "Demo Hotel Customer - S0xxxx" · สมาร์ทปุ่มด้านบนมี Projects 1 / Delivery 1 / FG Production 1<br>การติ๊ก Project ทำให้ดู P&amp;L ของงานนี้แยกได้ในตอน 5'),
]))
body.append(shot('gp-boq-05b-quote-pieces.webp', 'รายชิ้นของบรรทัดพื้น (ข้อ 2.3)'))

body.append('<h2><small>[03]</small>ตอน 3 · ผลิต FG</h2>')
body.append(table([
 ('3.1', 'กดสมาร์ทปุ่ม <b>FG Production</b> เปิดแท็บ <b>ผลผลิต FG</b>', 'ใบสั่งผลิต EG01/STFG/xxxxx สถานะ Draft · สินค้า NERO RUSTENBURG (Polished) 9.00 ตร.ม. · มี 1 แถว กว้าง 0.50 ยาว 0.90 หนา 0.02 (หน้าจอฝั่งโรงงานแสดงเป็นเมตร) จำนวน <b>20.00</b> ชิ้น'),
 ('3.2', 'เปิดแท็บ <b>Slab ที่จะตัด</b> กด <b>เลือก Slab อัตโนมัติ</b>', 'การ์ดบนสุดแสดง "ต้องใช้ 9.90 ตร.ม." (รวมเผื่อเสีย) และ "Slab ที่เลือก ≈ 10 ตร.ม." ป้ายเขียว <b>พอ</b>'),
 ('3.3', 'กดปุ่ม <b>ย้ายไปสถานีตัด</b> แล้วดูข้อความมุมจอ', 'ข้อความ "ย้ายสำเร็จ ... ย้าย N lot ไป Stone Production แล้ว — กด Confirm ได้เลย"'),
 ('3.4', 'กด <b>Confirm</b>', 'สถานะเป็น Confirmed และมีปุ่ม <b>ผลิต FG เสร็จ</b>'),
 ('3.5', 'กด <b>ผลิต FG เสร็จ</b>', 'ข้อความ "Complete FG Production สำเร็จ ... ผลิตสำเร็จ 9.00 หน่วย" · สถานะ Done · ได้ FG 1 Lot ชื่อ FG-EG01/STFG/xxxxx-01 จำนวน 20 ชิ้น ขนาด 0.50 × 0.90 × 0.02 ม. อยู่ที่ EG01/Stock/Stone FG'),
]))
body.append(shot('gp-boq-08-mo-slabs.webp', 'การ์ดและแท็บ Slab ที่จะตัด (ข้อ 3.2)'))
body.append('<p class="mbx-table-note">ถ้ากด "เลือก Slab อัตโนมัติ" แล้วขึ้น "ไม่พบ Slab ว่างของวัสดุนี้" แปลว่าไม่มี Slab ของสินค้า/ผิว/ความหนานั้นว่างในคลัง (ผิว Honed ของ NERO เป็นแบบนี้ตอนทดสอบ) ให้ใช้ผิว Polished ตามตัวอย่าง</p>')

body.append('<h2><small>[04]</small>ตอน 4 · ส่งของและออกใบแจ้งหนี้</h2>')
body.append(table([
 ('4.1', 'กลับที่ใบขาย กดสมาร์ทปุ่ม <b>Delivery</b> กด <b>Details</b> ที่แถวสินค้า', 'มีแถวเดียว <b>FG-EG01/STFG/xxxxx-01</b> (Lot ที่เพิ่งผลิต) จาก EG01/Stock/Stone FG จำนวน 9.00 ตร.ม. ไม่มี Lot ของงานอื่นปน'),
 ('4.2', 'กด Save แล้วกด <b>Validate</b>', 'ใบส่งของสถานะ Done · Demand 9.00 · Quantity 9.00'),
 ('4.3', 'กลับที่ใบขาย กด <b>Create Invoice</b> เลือก Regular invoice กด <b>Create Draft</b> แล้วกด <b>Confirm</b>', 'ใบแจ้งหนี้สถานะ Posted · 3 บรรทัดตามใบขาย · ก่อน VAT <b>143,220.00</b> VAT 8,064.00 รวม <b>151,284.00</b> · คอลัมน์ Analytic ขึ้น "BOQ0xxx - Demo Hotel Customer" ทุกบรรทัด'),
]))
body.append(shot('gp-boq-10-delivery-details.webp', 'Details ของใบส่งของ (ข้อ 4.1)'))

body.append('<h2><small>[05]</small>ตอน 5 · ดูต้นทุนที่เกิดจาก BOQ ใบนี้ และ P&amp;L</h2>')
body.append(table([
 ('5.1', 'เปิดใบสั่งผลิตของคุณ (สมาร์ทปุ่ม FG Production ที่ใบขาย) แท็บ <b>รายการบัญชี</b>', '4 รายการ สถานะ Posted: Inventory Valuation 2 รายการ (ค่า Slab ที่ใช้ตัด ราว 16,000 บาท) · <b>FG Production Labor</b> · <b>FG Production Consumables 900.00</b> · ยอดรวมที่ลงเป็นต้นทุนขายของงานนี้ ให้จดไว้'),
 ('5.2', 'เมนู <b>Accounting → Reporting → Profit and Loss</b> กดปุ่ม <b>Analytic</b> พิมพ์เลข BOQ ของคุณ เลือก "BOQ0xxx - Demo Hotel Customer"', 'มีคอลัมน์ของ BOQ คุณข้างคอลัมน์ Total'),
 ('5.3', 'กดขยายแถว <b>Revenue</b> และ <b>Less Costs of Revenue</b>', 'Revenue = <b>143,220.00</b> (411100) ตรงกับใบแจ้งหนี้ · Costs of Revenue แยกเป็น 511110 ต้นทุนหินส่ง · 511120 งานแปรรูป · 511130 วัสดุสิ้นเปลือง 900.00 · ยอดรวมต้นทุนตรงกับข้อ 5.1 · <b>Gross Profit = Revenue − Costs</b> (รอบทดสอบ: ต้นทุน 57,600 กำไรขั้นต้น 85,620)'),
]))
body.append(shot('gp-boq-14-pnl.webp', 'P&amp;L กรองด้วย Analytic ของ BOQ (ข้อ 5.3)'))
body.append('<p class="mbx-table-note">ต้นทุนรวมของพื้นถูกตั้งให้ไม่ต่ำกว่า 50% ของรายได้บรรทัดนั้น (กฎของเจ้าของ) ค่าแรงเป็นตัวปรับส่วนต่าง ดังนั้นถ้าค่า Slab ที่ระบบเลือกต่างจากรอบทดสอบ ตัวเลขแต่ละบัญชีจะขยับ แต่ต้นทุนรวมควรได้ ≈ 57,600</p>')

body.append('''<h2><small>[06]</small>ข้อควรรู้</h2>
  <div class="mbx-table-wrap"><table class="mbx-table compact">
    <thead><tr><th>เรื่อง</th><th>รายละเอียด</th></tr></thead>
    <tbody>
      <tr><td>หน่วยขนาด</td><td>กว้าง ยาว หนา ทุกช่องเป็น <b>ซม.</b> (ตรงกับ Cut List ของลูกค้า) ถ้ากรอกค่าที่ดูผิดหน่วย เช่น กว้าง 500 ระบบเตือน · ไฟล์เก่าที่หัวคอลัมน์เป็น (mm) ระบบแปลงเป็น ซม. ให้</td></tr>
      <tr><td>เพิ่มบรรทัดเองใน BOQ</td><td>ถ้าไม่ใช้ Excel แต่กรอกในฟอร์ม BOQ: เลือกสินค้าแล้วระบบใส่หน่วยและราคาวัสดุตั้งต้นให้ ส่วน <b>รายละเอียด</b> ต้องพิมพ์เอง ระบบไม่ใส่ชื่อสินค้าให้</td></tr>
      <tr><td>ปุ่มดาวน์โหลดเทมเพลต</td><td>ต้องเลือกลูกค้าก่อน ไม่งั้นขึ้น "Missing required fields" และไม่ดาวน์โหลด</td></tr>
      <tr><td>สินค้าในไฟล์</td><td>ใช้ได้เฉพาะสินค้า FG (แผ่นตัดตามขนาด หรือ FG ราคาคงที่) เลือกจาก dropdown ห้ามพิมพ์เอง · แผ่นตัดตามขนาดต้องมี กว้าง ยาว หนา ครบ</td></tr>
      <tr><td>ใบขายที่ไม่ติ๊ก Project</td><td>ไม่ได้ทดสอบในคู่มือนี้ P&amp;L แยกตาม BOQ ใช้ได้เมื่อติ๊ก Sold as Project</td></tr>
      <tr><td>ที่ยังไม่อยู่ในคู่มือนี้</td><td>งานเจดีย์บัว/โคม (Cut List → ต้นทุน) · ส่งของบางส่วนและรับคืนตามขนาด</td></tr>
      <tr><td>ถ้าเจอปัญหา</td><td>ส่งภาพหน้าจอ เลขที่ BOQ และเลขใบขาย พร้อมบอกว่าอยู่ข้อไหน</td></tr>
    </tbody>
  </table></div>

  <h3>บันทึกของผู้ทดสอบ</h3>
  <div class="noteBox"></div>

  <div class="footer mbx-meta"><span>Empire Granite · EMG-O</span><span>หน้า 1</span></div>
</article>
</body>
</html>
''')
out = head + '\n'.join(body)
open('../guide-boq-import-excel-2026-10-28.html', 'w', encoding='utf-8').write(out)
print('wrote', len(out))
