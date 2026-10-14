# Single source of truth for the EMG-O Golden Path "Slab — ตัดจาก Block ขาย ส่ง เก็บเงิน รับคืน ตรวจ และตัดทิ้ง".
#
# Data provenance: re-run end to end on `eg-tst`, 2026-10-14 (v19.0.2.109.24, branch test/emg-erp-ee), driven by
# Playwright as admin, company Empire Granite. Supersedes the 11 Oct run done by the user (BLK-26-0037).
# Fixtures left in place: PO P00308 -> receipt EG01/IN/00376 -> Block BLK-26-0431 (2.50 x 1.20 x 0.90, 7.30 t) ->
# Cut Order EG01/STCUT/00229 (51 Slabs BLK-26-0431-1..51, saw loss 15%) -> SO S00625 (10 slabs, 90,000) ->
# delivery EG01/OUT/00332 -> INV/2026/00031 -> return EG01/IN/00377 (-9, -10): -9 inspected OK, -10 scrapped (SP/00018);
# second return EG01/IN/00378 (-7, -8) left Pending Inspection (used for the pending-list screenshot).
#
# Golden Path discipline: happy path only, no validation/error cases, plain language.
# Column model per case: id, scenario, note, new (green "changed this round"), pre, steps, sample, expected, prio, shot, shot2.

SHOT = "assets/golden-path-slab-cut-to-scrap/"

CATEGORIES = [{'cat_id': 'A',
  'title': 'A. ซื้อ Block และรับเข้าคลัง',
  'subtitle': 'ซื้อเป็นตัน แล้วรับเป็นก้อนจริง ระบบสร้างเอกสาร Block ให้เอง · 2 test cases',
  'cases': [{'id': 'TC-GP-SCS-01',
             'scenario': 'สร้างใบสั่งซื้อ (PO) Block เป็นตัน แล้ว Confirm',
             'note': 'เลือกตันที่หาร 2.7 ลงตัว (7.29 ตัน = 2.70 ลบ.ม.) ราคาจะไม่เพี้ยนเศษสตางค์ · ตอนพิมพ์ชื่อสินค้า อย่ากดบรรทัด "Create ..." ใน dropdown เพราะจะสร้างสินค้าซ้ำ',
             'pre': 'เข้าระบบเป็น Empire Granite · มีผู้ขายและหินดำชานตง (SHANDONG BLACK) พร้อมสินค้า Block ในระบบ',
             'steps': ['เปิดแอป Purchase &gt; Orders &gt; Requests for Quotation &gt; New',
                       'เลือก Vendor แล้วกด "Add a product" เลือก "SHANDONG BLACK - Block"',
                       'กรอก Qty (Ton) และ Price / Ton — ช่อง Quantity (ลบ.ม.) และ Unit Price คำนวณให้เอง',
                       'กด Confirm Order'],
             'sample': 'Vendor = A-Test-Vender<br>Qty (Ton) = 7.29<br>Price / Ton = 10,000',
             'expected': 'Quantity 2.7000 ลบ.ม., Unit Price 27,000.00, ยอดก่อน VAT 72,900.00, VAT 7% 5,103.00, รวม 78,003.00 บาท · หลัง Confirm มีปุ่มสมาร์ท Receipt 1 ใบ (ตัวอย่างจริง P00308)',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-01-po.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — หน่วยและช่องเหมือนเดิม แต่ PO ใบนี้จะกลายเป็นบิลผู้ขายในหน่วยตัน (ดู Golden Path Block TC-GP-BPC-04)'},
            {'id': 'TC-GP-SCS-02',
             'scenario': 'รับ Block กรอกขนาด แล้ว Validate',
             'note': 'การ์ด Block แสดง "ประมาณ 28 แผ่น / 135.00 ตร.ม." ซึ่งเป็นค่าประมาณจากขนาด Slab มาตรฐานของวัสดุ ไม่ตรงกับจำนวนแผ่นในใบสั่งตัด (51 แผ่น) — ใช้เลขในใบสั่งตัดเป็นหลัก · '
                     'ตันตามใบส่งของเว้นว่างได้ ระบบจะใช้ ลบ.ม. × 2.7 แทน',
             'pre': 'ทำ TC-GP-SCS-01 เสร็จแล้ว',
             'steps': ['ที่ PO กดปุ่ม Receipt เพื่อเปิดใบรับของ',
                       'กดคำว่า Details ที่แถว Block แล้วกรอก ยาว / กว้าง / สูง และ ตันตามใบส่งของ ของก้อนที่รับ',
                       'กด Save แล้วกด Validate',
                       'เปิดแอป Stone Slab &gt; Blocks ค้นหา Block ใหม่ แล้วดูการ์ดสรุปด้านบน'],
             'sample': 'ขนาด Block = 2.50 × 1.20 × 0.90 ม.<br>ตันตามใบส่งของ = 7.300 ตัน',
             'expected': 'ใบรับของเป็น Done (EG01/IN/00376), Quantity 2.70 เท่ากับที่สั่ง จึงไม่มี Backorder · ได้ Block ใหม่ 1 ก้อน (ตัวอย่างจริง BLK-26-0431) สถานะ "ใช้ได้" ขนาด 2.50 × 1.20 × 0.90 '
                         '= 2.70 CBM · 7.30 ตัน ต้นทุน 10,000 บาท/ตัน (27,000 บาท/CBM) อ้างอิง PO P00308 % สูญเสียที่ใช้ 15.00 ผลการตัด "ยังไม่ได้ตัด"',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-02-block-card.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — ใบรับของมีช่อง "ตันตามใบส่งของ" (ตัวอย่างนี้ 7.300 ตัน) ตันนี้กลายเป็นตันของ Block และใช้คิดต้นทุน · การ์ด Block มีส่วน "% สูญเสียจากการเลื่อย" '
                    '(15%) และช่อง QC Note',
             'shot2': 'assets/golden-path-slab-cut-to-scrap/gp-ss-02b-receipt-done.webp'}]},
 {'cat_id': 'B',
  'title': 'B. ตัด Block เป็น Slab (Cut Order)',
  'subtitle': 'สร้างใบสั่งตัด ย้าย Block ไปสถานีตัด ยืนยัน แล้วตัดเสร็จ ได้ Slab ทีละแผ่น · 3 test cases',
  'cases': [{'id': 'TC-GP-SCS-03',
             'scenario': 'สร้างใบสั่งตัด เลือก Block ผิว และความหนา',
             'note': 'ใบสั่งตัดที่ยังเป็น Draft แท็บ Components อาจแสดงปริมาณ Block ตามสูตรมาตรฐานของ Odoo (เช่น 51.00 m³ Not Available) ไม่ใช่ปริมาณที่ใช้จริง พอ Confirm จะกลับเป็น 2.70 ลบ.ม. · '
                     'ถ้าไม่มี Sale Order ต้องเลือก "เหตุผล (กรณีไม่มี SO)" ก่อนจึงจะ Confirm ได้',
             'pre': 'ทำ TC-GP-SCS-02 เสร็จแล้ว (Block อยู่ที่ Stone Available)',
             'steps': ['เปิดแอป Manufacturing &gt; Operations &gt; Manufacturing Orders &gt; New',
                       'ช่อง "Block ที่จะตัด" เลือก Block',
                       'เลือก Finish และ Thickness',
                       'ช่อง "เหตุผล (กรณีไม่มี SO)" เลือกเหตุผล',
                       'กด Save'],
             'sample': 'Block = BLK-26-0431<br>Finish = Polished<br>Thickness = 2 cm<br>เหตุผล = งานเพิ่ม (Extra work)',
             'expected': 'การ์ดบนหน้าแสดง Block ที่ตัด BLK-26-0431 เหลือ 2.70 CBM · ขนาดเป้าหมาย 2.50 × 0.90 ม. Polished หนา 0.02 ม. · ความคืบหน้า ประมาณ 51 แผ่น = 114.75 ตร.ม. · "จะได้ Slab: ... '
                         'Slab (Polished, 2 cm)" · ข้อความเขียว "แผนใช้ 2.70 CBM (รวมสูญเสียเลื่อย 15%) พอ" · แท็บ "Slab ที่ตัดได้ (แผน/จริง)" มีแผน 51 แถว · มีแถบเหลืองบอกให้กด "ย้ายไปสถานีตัด" '
                         'ก่อน Confirm (ตัวอย่างจริง EG01/STCUT/00229)',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-03-cut-draft.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — แผนหัก "% สูญเสียจากการเลื่อย" 15% แล้ว: 51 แผ่น / 114.75 ตร.ม. (รอบ 11 ต.ค. เป็น 60 แผ่น / 135.00 ตร.ม.) และข้อความสีเขียวบอกว่าแผนใช้ 2.70 CBM '
                    'รวมสูญเสียเลื่อยแล้ว'},
            {'id': 'TC-GP-SCS-04',
             'scenario': 'ย้าย Block ไปสถานีตัด แล้ว Confirm',
             'note': 'ต้องกด "ย้ายไปสถานีตัด" ก่อน Confirm เสมอ เพราะ Block ต้องอยู่ที่สถานีตัดก่อน · หลังย้าย มีข้อความมุมจอ "ย้ายสำเร็จ ... กด Confirm ได้เลย"',
             'pre': 'ทำ TC-GP-SCS-03 เสร็จแล้ว',
             'steps': ['กดปุ่ม "ย้ายไปสถานีตัด" ที่หัวฟอร์ม', 'ดูข้อความมุมจอ แล้วกด Confirm'],
             'sample': '-',
             'expected': 'ข้อความ "ย้ายสำเร็จ (Moved). Block BLK-26-0431 ย้ายไป Stone Production แล้ว 2.700 หน่วย — กด Confirm ได้เลย" · หลัง Confirm ปุ่มเปลี่ยนเป็น "ตัดเสร็จ", Component Status = '
                         'Available, ผู้รับผิดชอบเป็นผู้ใช้ปัจจุบัน (EG01/STCUT/00229)',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-04-cut-confirmed.webp'},
            {'id': 'TC-GP-SCS-05',
             'scenario': 'กด "ตัดเสร็จ" ได้ Slab ทีละแผ่น',
             'note': 'ชื่อ Slab ที่ตัดจาก Block ตั้งตามชื่อ Block (BLK-26-0431-1, -2, ...) ส่วน SLB-26-xxxx ใช้กับ Slab ที่ซื้อมาเป็นแผ่น · Block ถูกใช้หมด (เหลือ 0 CBM) '
                     'เพราะแผนรวมส่วนสูญเสียเลื่อยแล้ว',
             'pre': 'ทำ TC-GP-SCS-04 เสร็จแล้ว',
             'steps': ['เปิดแท็บ "Slab ที่ตัดได้ (แผน/จริง)" ดูว่าแผนมี 51 แถว', 'กดปุ่ม "ตัดเสร็จ"', 'ดูแท็บ Slab อีกครั้ง และสมาร์ทปุ่ม Serial Numbers'],
             'sample': 'ขนาดจริงทุกแผ่น = ขนาดแผน (2.50 × 0.90 × 0.02) ไม่ต้องแก้ช่อง "จริง"',
             'expected': 'ข้อความ "Complete Cut สำเร็จ ... ตัดได้ 51 แผ่นจาก BLK-26-0431" · สถานะ Done · Serial Numbers 51 · การ์ดสรุป 114.75 ตร.ม. (100% ของแผน) · Block เหลือ 0 CBM · Slab '
                         'BLK-26-0431-1 ถึง -51 สถานะ Available ต้นทุนแผ่นละ 1,431.37 บาท (มูลค่าที่ย้ายจาก Block เป็น Slab 73,000.00 บาท) ราคาขาย 4,000 บาท/ตร.ม.',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-05-cut-done.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — ต้นทุนแผ่นแบ่งตามต้นทุนของ Block ก้อนนั้นเอง (7.30 ตัน × 10,000 = 73,000 บาท) หารจำนวนแผ่น 51 = 1,431.37 บาท/แผ่น (รอบ 11 ต.ค. คิด 540 บาท/ตร.ม. จาก '
                    '72,900 ÷ 135) เพราะแผนมีส่วนสูญเสียเลื่อยแล้ว'}]},
 {'cat_id': 'C',
  'title': 'C. ขาย ส่งของ และเก็บเงิน',
  'subtitle': 'เลือกแผ่นที่จะขายเข้าใบสั่งขาย ส่งโดยสแกน Serial แล้วออกใบแจ้งหนี้ · 5 test cases',
  'cases': [{'id': 'TC-GP-SCS-06',
             'scenario': 'สร้างใบเสนอราคา แล้วเลือกแผ่นที่จะขาย (Select Slabs)',
             'pre': 'ทำ TC-GP-SCS-05 เสร็จแล้ว (มี Slab Available)',
             'steps': ['เปิดแอป Sales &gt; Orders &gt; Quotations &gt; New เลือกลูกค้า',
                       'กด "Add a product" เลือก "SHANDONG BLACK - Slab" แล้วเลือก Finish กับ Thickness ในหน้าต่างที่ขึ้น กด Confirm แล้ว Save',
                       'ท้ายบรรทัดสินค้า กดไอคอนรายการ เลือก Select Slabs',
                       'กด Add a line เลือก Slab ทีละแผ่นให้ครบ แล้วกด "ยืนยันการเลือก"'],
             'sample': 'ลูกค้า = Demo Hotel Customer<br>Finish = Polished, Thickness = 2 cm<br>เลือก BLK-26-0431-1 ถึง -10 (10 แผ่น)',
             'expected': 'บรรทัดสินค้าเป็น "10 แผ่น = 22.50 ตร.ม. · 4,000 ฿/ตร.ม." แสดงรายชื่อ 10 แผ่น แต่ละแผ่น 2.50 × 0.90 × 0.020 ม. = 2.25 ตร.ม. · หนา (ซม.) 2.00 · Quantity 10.00 Units, Unit '
                         'Price 9,000.00 (2.25 × 4,000) · สมาร์ทปุ่ม Slabs = 10 (ตัวอย่างจริง S00625)',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-06-so-quote.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — ใบขายมีคอลัมน์ "หนา (ซม.)" และ "เตือนกำไร" ราคาต่อ ตร.ม. ตามความหนา (ราคาตามตารางความหนาของวัสดุ) ภาพที่ 2 แสดงคอลัมน์เหล่านี้ (ปกติเป็นคอลัมน์เสริม '
                    'เปิดได้จากไอคอนตั้งค่าท้ายหัวตาราง)',
             'note': 'ในภาพแรกซ่อนคอลัมน์เสริมเพื่อให้เห็นรายชื่อแผ่น',
             'shot2': 'assets/golden-path-slab-cut-to-scrap/gp-ss-06b-thickness-cols.webp'},
            {'id': 'TC-GP-SCS-07',
             'scenario': 'Confirm ใบสั่งขาย',
             'note': '⚠ แถบแดง "ขนาดแผ่นจริงต่างจากที่เสนอลูกค้า" ขึ้นได้ปกติ เพราะใบเสนอราคาใช้ขนาด Slab มาตรฐานของวัสดุ (3.00 × 1.60 = 4.80 ตร.ม.) แต่แผ่นจริงที่เลือกคือ 2.25 ตร.ม. '
                     'ระบบล็อกยอดไว้ที่ 90,000 ตามที่เสนอและเตือนเซลล์ให้แจ้งลูกค้า เป็นพฤติกรรมตามออกแบบ (ADR-079/085) ไม่ใช่ข้อผิดพลาดและไม่ห้ามการ Confirm',
             'pre': 'ทำ TC-GP-SCS-06 เสร็จแล้ว',
             'steps': ['กดปุ่ม Confirm บนใบเสนอราคา', 'ดูสถานะ แถบเตือน สมาร์ทปุ่ม และยอดรวมท้ายใบ'],
             'sample': '-',
             'expected': 'สถานะ Sales Order · มีสมาร์ทปุ่ม Delivery 1 ใบ และ Slabs 10 · บรรทัดสินค้าเขียน "ล็อกยอด 90,000 ฿ (ตามใบเสนอ) · แผ่นจริง 10 แผ่น = 22.50 ตร.ม. · ราคาสินค้า 4,000 ฿/ตร.ม." · '
                         'ยอดก่อน VAT 90,000.00, VAT 7% 6,300.00, รวม 96,300.00 บาท',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-07-so-confirmed.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — แถบแดง "ขนาดแผ่นจริงต่างจากที่เสนอลูกค้า" ยังเป็นพฤติกรรมเดิม'},
            {'id': 'TC-GP-SCS-08',
             'scenario': 'ส่งของ — สแกน Serial ทุกแผ่นแล้ว Validate',
             'pre': 'ทำ TC-GP-SCS-07 เสร็จแล้ว',
             'steps': ['ที่ใบสั่งขาย กดสมาร์ทปุ่ม Delivery', 'ที่แถวสินค้ากด Details', 'คอลัมน์ Scanned Serial ของแต่ละแถว สแกนหรือพิมพ์ชื่อ Serial ให้ตรงกับแผ่นในแถวนั้น', 'กด Save แล้วกด Validate'],
             'sample': 'Serial = BLK-26-0431-1 ถึง BLK-26-0431-10',
             'expected': 'ใบส่งของเป็น Done จาก Stone Inventory/Stone Available Demand 10.00 Quantity 10.00 Units · ใบสั่งขาย Delivered = 10 · Slab ทั้ง 10 แผ่นเปลี่ยนสถานะเป็น Sold (ตัวอย่างจริง '
                         'EG01/OUT/00332)',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-09-delivery-done.webp',
             'shot2': 'assets/golden-path-slab-cut-to-scrap/gp-ss-08b-scanned.webp'},
            {'id': 'TC-GP-SCS-09',
             'scenario': 'ออกใบแจ้งหนี้ลูกค้า และ Confirm',
             'pre': 'ทำ TC-GP-SCS-08 เสร็จแล้ว',
             'steps': ['กลับไปที่ใบสั่งขาย กดปุ่ม Create Invoice', 'เลือก Regular invoice แล้วกด Create Draft Invoice', 'กด Confirm บนใบแจ้งหนี้'],
             'sample': '-',
             'expected': 'ใบแจ้งหนี้สถานะ Posted · บรรทัดสินค้า 10.000 Units ราคา 9,000.00 รวม 90,000.00 บาท · ยอดก่อน VAT 90,000.00, VAT 7% 6,300.00, รวม 96,300.00 และ Amount Due 96,300.00 · แท็ก '
                         'Analytic เป็น Sale / Granite / วัสดุ / BLK-26-0431 (ตัวอย่างจริง INV/2026/00031) · ช่อง Qty (Ton) ว่างเป็นปกติสำหรับ Slab',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-10-invoice.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — จำนวนในใบแจ้งหนี้แสดง 3 ตำแหน่ง (10.000 Units) เพราะรอบ Block ตั้งทศนิยมจำนวนบรรทัดบิลเป็น 3 ตำแหน่งทั้งระบบ ยอดเงินไม่เปลี่ยน'},
            {'id': 'TC-GP-SCS-10',
             'scenario': 'ตรวจรายการบัญชีของใบแจ้งหนี้ (ต้นทุนขายตามต้นทุนแผ่นจริง)',
             'pre': 'ทำ TC-GP-SCS-09 เสร็จแล้ว',
             'steps': ['ที่ใบแจ้งหนี้ที่ Post แล้ว เปิดแท็บ Journal Items', 'ดูบรรทัดต้นทุนขายและสินค้าคงเหลือ'],
             'sample': 'ต้นทุน = 10 แผ่น × 1,431.375 = 14,313.73',
             'expected': 'เดบิต 112100 ลูกหนี้การค้า 96,300.00 · เครดิต 411100 รายได้จากการขาย 90,000.00 · เครดิต 213200 ภาษีขาย 6,300.00 · เดบิต 511110 ต้นทุนขาย (COGS) 14,313.73 · เครดิต 113120 '
                         'สินค้าคงเหลือ Slab (Ready-Made) 14,313.73 · ยอดรวมสองฝั่งเท่ากัน 110,613.73',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-10b-invoice-journal.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — ต้นทุนขายคือต้นทุนจริงของแผ่นที่ขาย (แผ่นละ 1,431.37 จากต้นทุน Block ก้อนนั้น) ไม่ใช่ 1,215 ของรอบ 11 ต.ค.'}]},
 {'cat_id': 'D',
  'title': 'D. ลูกค้าคืน Slab ตรวจรับ และตัดทิ้ง',
  'subtitle': 'แผ่นที่คืนเข้า Returned - Inspect ก่อนเสมอ ตรวจแล้วใช้ได้กลับไปขาย หรือชำรุดให้ตัดทิ้ง · 5 test cases',
  'cases': [{'id': 'TC-GP-SCS-11',
             'scenario': 'รับคืน Slab 2 แผ่นจากลูกค้า',
             'note': 'ใบรับคืนไม่เลือกแผ่นไว้ให้ ผู้รับของต้องระบุเองว่าแผ่นไหนถูกคืน เพราะลูกค้าอาจคืนไม่ครบ ตัวเลือกมีเฉพาะแผ่นที่อยู่ที่ลูกค้า · ช่อง Return ตอนเปิดครั้งแรกแสดง 0.00 เป็นปกติของ '
                     'Odoo ให้กด Return All · ปุ่ม Return ที่ถูกต้องคือปุ่มบนแถบสถานะ (ไม่ใช่สมาร์ทปุ่ม Returns ที่ขึ้นหลังมีใบคืนแล้ว)',
             'pre': 'ทำ TC-GP-SCS-08 เสร็จแล้ว (ใบส่งของ Done)',
             'steps': ['เปิดใบส่งของที่ Done กดปุ่ม Return แล้วกด Return All',
                       'ในใบรับคืนที่ได้ ที่แถวสินค้ากด Details',
                       'กด Add a line พิมพ์ชื่อ Slab ที่คืน ใส่จำนวน 1 ทำซ้ำทีละแผ่น',
                       'กด Save แล้วกด Validate เมื่อถาม Backorder เลือก No Backorder'],
             'sample': 'แผ่นที่คืน = BLK-26-0431-9 และ BLK-26-0431-10',
             'expected': 'ใบรับคืนเป็น Done รับจาก Demo Hotel Customer ปลายทาง Stone Inventory/Returned - Inspect เอกสารต้นทาง "Return of EG01/OUT/00332" · Demand 10.00 แต่ Quantity 2.00 และไม่มี '
                         'Backorder เกิดขึ้น (ตัวอย่างจริง EG01/IN/00377)',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-11-return-done.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — Validate ใบรับคืนที่รับน้อยกว่า Demand ระบบถาม Backorder ให้เลือก No Backorder (รอบนี้ยืนยันว่าไม่มี error และไม่เกิด Backorder)'},
            {'id': 'TC-GP-SCS-12',
             'scenario': 'หาแผ่นที่คืนและรอตรวจ',
             'note': 'หน้ารายการ Slab เปิดมาพร้อมตัวกรอง Available ซึ่งซ่อนแผ่นที่รอตรวจไว้ ให้เอาตัวกรองออกหรือใช้ตัวกรอง Pending Inspection · รายการจะมีแผ่นรอตรวจของงานอื่นบนระบบทดสอบปนอยู่ด้วย '
                     'ให้ดูเฉพาะแผ่นของเรา · ภาพนี้ถ่ายจากใบรับคืนใบที่สอง (EG01/IN/00378: BLK-26-0431-7 และ -8) เพราะ -9 และ -10 ถูกตรวจ/ตัดทิ้งไปแล้วตอนถ่ายภาพ TC-GP-SCS-13 ถึง 14',
             'pre': 'ทำ TC-GP-SCS-11 เสร็จแล้ว',
             'steps': ['เปิดแอป Stone Slab &gt; Slabs', 'ใช้ตัวกรอง Pending Inspection (หรือเอาตัวกรอง Available ออกแล้วค้นหา BLK-26-0431)'],
             'sample': '-',
             'expected': 'เห็นแผ่นที่คืนสถานะ "Returned - Pending Inspection" (สีส้ม) ขนาด 2.50 × 0.90 × 0.020 ม. = 2.25 ตร.ม. On Hand 1.00 (ตามเส้นทางหลัก คือ BLK-26-0431-9 และ -10 · ในภาพคือ -7 '
                         'และ -8 จากใบรับคืนใบที่สอง) · ยังไม่นับเป็นของพร้อมขาย และไม่โผล่ในตัวกรอง Available',
             'prio': 'Medium',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-12-pending-list.webp'},
            {'id': 'TC-GP-SCS-13',
             'scenario': 'ตรวจแล้วแผ่นใช้ได้ นำกลับไปขาย',
             'note': 'การ์ดอาจยังเขียน "ถูกเลือกในใบขาย: S00625" หลังตรวจแล้ว เป็นแค่ประวัติของใบขายเดิม ไม่ได้กันไม่ให้ขายซ้ำ (ระบบกันเฉพาะแผ่นที่ถูกเลือกในใบเสนอราคาที่ยังเป็นร่างหรือส่งแล้ว) · '
                     'การ์ดแสดง "แรงตัด 1,000 บาท" แยกจากต้นทุน เป็นข้อมูลแสดง ไม่ได้รวมในต้นทุนขายของใบแจ้งหนี้',
             'pre': 'ทำ TC-GP-SCS-12 เสร็จแล้ว',
             'steps': ['เปิดแผ่นที่ตรวจแล้วว่าใช้ได้ (ก่อนกด จะเห็นสถานะ Returned - Pending Inspection และปุ่ม "ตรวจแล้ว — นำกลับไปขาย" กับ "ชำรุด — ตัดทิ้ง (Scrap)")',
                       'กดปุ่ม "ตรวจแล้ว — นำกลับไปขาย"'],
             'sample': 'แผ่น = BLK-26-0431-9',
             'expected': 'สถานะกลับเป็น Available ที่เก็บ Stone Inventory/Stone Available · ขนาด 2.500 × 0.900 × 0.020 = 2.2500 ตร.ม. · ต้นทุน 1,431.375 บาท เท่าเดิม ราคาขาย 4,000.00 บาท/ตร.ม. (≈ '
                         '9,000 บาท/แผ่น) · ปุ่มตรวจและปุ่มตัดทิ้งหายไป และเลือกขายได้ใหม่',
             'prio': 'High',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-13b-inspect-after.webp'},
            {'id': 'TC-GP-SCS-14',
             'scenario': 'ตรวจแล้วแผ่นชำรุด — ตัดทิ้ง (Scrap)',
             'note': 'ย้ายสต็อกแล้วตัดทิ้ง (SP/00018 Done) มูลค่าสต็อกที่ตัดออก 1,431.38 บาท (ต้นทุนแผ่น) · ยังไม่ได้ตรวจรายการบัญชีของการตัดทิ้ง จึงยังไม่ระบุผลบัญชีใน test case นี้',
             'pre': 'ทำ TC-GP-SCS-12 เสร็จแล้ว',
             'steps': ['เปิดแผ่นที่ชำรุดจากรายการรอตรวจ', 'กดปุ่ม "ชำรุด — ตัดทิ้ง (Scrap)"', 'เมื่อระบบถาม "ตัดทิ้งแผ่นนี้ออกจากสต็อก?" กด Ok'],
             'sample': 'แผ่น = BLK-26-0431-10',
             'expected': 'สถานะแผ่นเป็น Elsewhere ที่เก็บ Inventory adjustment · ระบบสร้างเอกสาร Scrap ของ Odoo สถานะ Done จำนวน 1 ย้ายจาก Returned - Inspect ไป Inventory adjustment (ตัวอย่างจริง '
                         'SP/00018) · แผ่นไม่อยู่ในสต็อกขายอีก',
             'prio': 'Medium',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-14-scrap-form.webp'},
            {'id': 'TC-GP-SCS-15',
             'scenario': 'ตรวจยอดรวม Slab ของ Block หลังจบเส้นทาง',
             'pre': 'ทำ TC-GP-SCS-14 เสร็จแล้ว',
             'steps': ['เปิดแอป Stone Slab &gt; Blocks เปิด Block ที่ใช้ตัด (BLK-26-0431)', 'ดูสมาร์ทปุ่มนับจำนวนตามสถานะและการ์ดสรุป'],
             'sample': '-',
             'expected': 'Slab ทั้งหมด 51 แผ่น = Available 42 แผ่น (94.50 ตร.ม.) + Sold 6 แผ่น (13.50 ตร.ม.) + Returned รอตรวจ 2 แผ่น (4.50 ตร.ม. คือ -7 และ -8 จากใบรับคืนใบที่สอง) + ตัดทิ้ง 1 แผ่น '
                         '(2.25 ตร.ม.) · รวม 114.75 ตร.ม. ตรงกับที่ตัดได้ในใบสั่งตัด · การ์ด Block: 42 แผ่นพร้อมขาย ขายแล้ว 6'
                         'Sold 8 − ... ให้ใช้ตัวเลขตามที่ทำจริง)',
             'prio': 'Medium',
             'shot': 'assets/golden-path-slab-cut-to-scrap/gp-ss-15-block-totals.webp',
             'new': 'รอบ 14 ต.ค. 2569 (v109.24) — จำนวนแผ่นรวมเป็น 51 (ไม่ใช่ 60) เพราะหักสูญเสียเลื่อย'}]}]
