# Single source of truth for EMG-O E2E flow test cases — Mode 1 (Block Direct
# Sale), the full lifecycle: purchase a Block -> sell it whole -> deliver ->
# book all the accounting. Distinct from qa_data.py (feature-level checks,
# includes required-field/validation cases) — every case here is a "does the
# whole business flow work" step, written purely from what a non-technical
# UI user clicks/sees. No field-validation/error-message cases at all.
#
# Built + the whole flow executed once live on mbx-ee-dev (odoo shell,
# 2026-09-06) before writing this file, so every "sample data"/"expected
# result" below is a REAL observed number from that run, not a guess:
#   PO P00039 -> Bundle BLK-26-0016 -> Vendor Bill BILL/2026/09/0001 ->
#   SO S00085 -> Delivery EG01/OUT/00043 -> Invoice INV/2026/00009.
#   Committed as a genuine reference fixture (mbx-ee-dev only, not eg-tst).
#
# CORRECTIONS made vs. the original draft list (confirmed against real code
# + a real live run, not assumed):
#   - Dropped "validate the Receipt" as its own step — read stone_bundle.py's
#     create()/_ensure_receipt_cancelled(): saving the Bundle (Block) with a
#     linked Purchase Order Line IS what receives the stock (a custom stock
#     move fires automatically); the native PO Receipt is deliberately
#     auto-cancelled as a safety net so staff never accidentally validate it
#     and double the stock. Real flow has no separate "Receipt" screen at
#     all for this module's products.
#   - No "Production" category for Mode 1 at all (confirmed: whole-block
#     sale never touches MRP/Cut Order) — kept as a single explanatory
#     placeholder row instead of silently omitting the phase.
#   - TC-E2E-M1-12 documents a REAL, confirmed finding from the live run: the
#     Customer Invoice embeds its own COGS/Inventory lines (native Odoo 19
#     `display_type='cogs'`, account 511110) AND the Delivery separately
#     posts its own Inventory Valuation journal entry for the exact same
#     value (account 511100, a different/generic account) — i.e. Cost of
#     Goods Sold appears to be booked twice for one physical delivery. Cross
#     -checked against the existing Session 103 reference fixture
#     (INV/2026/00008 / S00083) and found the identical pattern there too —
#     not a new regression from today's test, a pre-existing condition.
#     Marked as a known issue, not silently treated as correct.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low)

CATEGORIES = [
  dict(cat_id="E1", title="E1. ซื้อ (Purchase)",
       subtitle="ซื้อ Block หินก้อนใหม่เข้าสต๊อก · 3 test cases",
       cases=[
    dict(id="TC-E2E-M1-01", scenario="สร้างใบสั่งซื้อ (PO) ซื้อ Block",
         pre="มี Vendor อยู่แล้วในระบบ (หรือสร้างใหม่ได้)",
         steps=["เปิด Purchase &gt; Orders &gt; New", "เลือก Vendor", "เพิ่มบรรทัด เลือกสินค้า Block ของวัสดุที่ต้องการ (เช่น \"Bianco Sardo Granite - Block\")", "กรอกจำนวน (หน่วยเป็น m&sup3;) และราคาต่อหน่วย", "กด Confirm Order"],
         sample="Vendor = \"ทดสอบ E2E - Test Quarry Vendor\"<br>สินค้า = Bianco Sardo Granite - Block<br>จำนวน = 8.5 m&sup3;<br>ราคา/หน่วย = 18,000",
         expected="PO ยืนยันสำเร็จ (state = Purchase Order) ยอดรวมคำนวณถูกต้อง (จำนวน &times; ราคา + VAT) — ตัวอย่างจริงที่ทดสอบ: P00039 ยอดรวม 163,710", prio="High"),
    dict(id="TC-E2E-M1-02", scenario="สร้าง Block (Bundle) ผูกกับ PO — ขั้นตอนนี้คือการรับสต๊อกจริง",
         note="หมายเหตุ: ไม่มีขั้นตอน \"Validate Receipt\" แยกต่างหาก — การกด Save ที่นี่คือการรับของเข้าคลังเลย ใบรับสินค้า (Receipt) ที่ระบบสร้างให้อัตโนมัติจาก PO จะถูกยกเลิกให้เองเบื้องหลัง (กันสต๊อกซ้ำ) ไม่ต้องไปกดอะไรกับมัน",
         pre="ทำ TC-E2E-M1-01 เสร็จแล้ว",
         steps=["เปิด Stone Slab &gt; Blocks &gt; New", "เลือก Material (ต้องตรงกับสินค้าใน PO)", "เลือก Warehouse", "ที่ช่อง Purchase Order Line เลือก PO Line ที่เพิ่งสร้าง", "กรอก Total CBM (ตรงกับจำนวนใน PO) และ Thickness (M)", "กด Save"],
         sample="Material = Bianco Sardo Granite<br>Purchase Order Line = P00039 (บรรทัด Block)<br>Total CBM = 8.5<br>Thickness (M) = 0.02",
         expected="บันทึกสำเร็จ ได้เลขก้อนอัตโนมัติ (เช่น BLK-26-0016) ช่อง \"PO Cost / CBM\" ขึ้นราคาต่อหน่วยจาก PO ให้เอง (18,000) — เปิด Inventory &gt; Blocks/Stone Available ดูจะเห็นสต๊อกก้อนนี้เข้ามาแล้วเท่ากับ Total CBM ที่กรอก", prio="High"),
    dict(id="TC-E2E-M1-03", scenario="สร้างและยืนยันบิลผู้ขาย (Vendor Bill)",
         pre="ทำ TC-E2E-M1-01 เสร็จแล้ว (PO อยู่สถานะ Purchase Order)",
         steps=["เปิด PO ที่สร้างไว้", "กดปุ่ม \"Create Bill\"", "ตรวจยอด/วันที่บิล", "กด Confirm (ยืนยันบิล)"],
         sample="-",
         expected="บิลสถานะ Posted ยอดตรงกับ PO (ตัวอย่างจริง: BILL/2026/09/0001, 163,710)", prio="High"),
  ]),
  dict(cat_id="E2", title="E2. ขาย (Sale — Mode 1)",
       subtitle="ขายทั้งก้อนตาม CBM (ADR-019) · 3 test cases",
       cases=[
    dict(id="TC-E2E-M1-04", scenario="สร้าง Sale Order ให้ลูกค้า",
         pre="-",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้า Block ของวัสดุเดียวกับที่ซื้อไว้ (TC-E2E-M1-02)"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = Bianco Sardo Granite - Block",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Sell Whole Block\" ปรากฏบนบรรทัดนั้น", prio="Medium"),
    dict(id="TC-E2E-M1-05", scenario="กด \"Sell Whole Block\" เลือกก้อนที่ซื้อมา",
         pre="ทำ TC-E2E-M1-04 เสร็จแล้ว, มี Block สถานะ Available จาก TC-E2E-M1-02",
         steps=["กดปุ่ม \"Sell Whole Block\" บนบรรทัด", "หน้าต่าง \"Select Block\" เลือก Block ที่ซื้อไว้ (เช่น BLK-26-0016)", "กด \"Confirm Selection\""],
         sample="เลือก Block = BLK-26-0016",
         expected="บรรทัด SO ปรับจำนวนเป็น CBM ทั้งหมดของก้อนนั้นอัตโนมัติ (8.5) ราคาต่อหน่วยคำนวณจากต้นทุน/CBM ของก้อน (ตัวอย่างจริง: ราคาต่อหน่วย 25,000, ยอดรวมบรรทัด 212,500)", prio="High"),
    dict(id="TC-E2E-M1-06", scenario="ยืนยัน (Confirm) Sale Order",
         pre="ทำ TC-E2E-M1-05 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นให้อัตโนมัติ 1 ใบ (ตัวอย่างจริง: S00085 &rarr; EG01/OUT/00043)", prio="High"),
  ]),
  dict(cat_id="E3", title="E3. ผลิต (Production)",
       subtitle="Mode 1 ไม่มีขั้นตอนนี้ · 0 test cases",
       cases=[
    dict(id="TC-E2E-M1-N/A", scenario="(ไม่มี Test Case ในหมวดนี้สำหรับ Mode 1)",
         note="Mode 1 ขายทั้งก้อนโดยไม่ผ่านการตัด/ผลิตใดๆ — ลูกค้าซื้อก้อนดิบทั้งก้อนไปทั้งดุ้น ไปต่อที่การจัดส่งได้เลย ขั้นตอนผลิตจะมีใน Mode 3 (Cut-to-Order)/Mode 5 (FG Production) เท่านั้น ซึ่งจะทำเป็นชุด test case แยกต่างหาก",
         pre="-", steps=["-"], sample="-", expected="-", prio="Low"),
  ]),
  dict(cat_id="E4", title="E4. จัดส่ง (Delivery)",
       subtitle="ส่งของจริงออกจากคลัง · 2 test cases",
       cases=[
    dict(id="TC-E2E-M1-07", scenario="เปิดใบส่งของ (Delivery Order) ที่เกิดขึ้นอัตโนมัติ",
         pre="ทำ TC-E2E-M1-06 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กดปุ่ม Delivery (smart button ด้านบน)"],
         sample="-",
         expected="เห็นใบส่งของสถานะ \"Ready\"/\"Waiting\" สินค้า 1 บรรทัด จำนวนตรงกับ SO (8.5 m&sup3;)", prio="Medium"),
    dict(id="TC-E2E-M1-08", scenario="ยืนยันการส่งของจริง (Validate)",
         pre="ทำ TC-E2E-M1-07 เสร็จแล้ว",
         steps=["กดปุ่ม Validate บนใบส่งของ"],
         sample="-",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done — Block ก้อนนั้นหายจากสต๊อกที่ขายได้ (Available) แล้ว", prio="High"),
  ]),
  dict(cat_id="E5", title="E5. บัญชี (Accounting)",
       subtitle="ออกใบแจ้งหนี้ + ตรวจรายการบัญชีของทั้งเรื่อง · 5 test cases",
       cases=[
    dict(id="TC-E2E-M1-09", scenario="สร้างและยืนยันใบแจ้งหนี้ลูกค้า (Customer Invoice)",
         pre="ทำ TC-E2E-M1-08 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; Create Draft Invoice", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO รวม VAT (ตัวอย่างจริง: INV/2026/00009, 227,375)", prio="High"),
    dict(id="TC-E2E-M1-10", scenario="ตรวจรายการบัญชีฝั่งซื้อ — Vendor Bill",
         pre="ทำ TC-E2E-M1-03 เสร็จแล้ว",
         steps=["เปิด Vendor Bill &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="เห็น 3 บรรทัด: เดบิต Inventory - Stone Blocks (ยอดสินค้าก่อน VAT), เดบิต Input VAT, เครดิต Trade Payables (ยอดรวม) — ตัวอย่างจริง: 153,000 / 10,710 / 163,710", prio="Medium"),
    dict(id="TC-E2E-M1-11", scenario="ตรวจรายการบัญชีฝั่งรายได้ + ต้นทุนขาย บนใบแจ้งหนี้",
         pre="ทำ TC-E2E-M1-09 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="เห็น 5 บรรทัดบนใบแจ้งหนี้ใบเดียว: เครดิต Sales Revenue, เครดิต Output VAT, เดบิต Trade Receivables (รวม), และคู่ COGS/Inventory ที่ระบบแนบมาด้วยอัตโนมัติ (เดบิต COGS / เครดิต Inventory) — ตัวอย่างจริง: รายได้ 212,500 / VAT 14,875 / ลูกหนี้ 227,375 / COGS-Inventory คู่ละ 153,000.08", prio="High"),
    dict(id="TC-E2E-M1-12", scenario="ตรวจว่าต้นทุนขาย (COGS) ถูกบันทึกซ้ำหรือไม่ — known issue",
         note="⚠️ พบจริงจากการทดสอบ (2026-09-06): เปิด Journal Entry ที่แยกต่างหากจากใบส่งของ (ชื่อขึ้นต้น STJ) จะเห็นคู่ COGS/Inventory อีกชุดหนึ่ง มูลค่าเท่ากันเป๊ะกับที่เห็นในใบแจ้งหนี้ (TC-E2E-M1-11) แต่ใช้บัญชีคนละตัว (511100 \"Cost of Goods Sold\" ธรรมดา แทนที่จะเป็น 511110 \"COGS - Block Direct Sale (Mode 1)\") — เช็คย้อนกลับไปที่ข้อมูลอ้างอิงเก่าของ session ก่อนหน้า (INV/2026/00008) ก็เจอรูปแบบเดียวกัน แปลว่าไม่ใช่บั๊กใหม่ แต่เป็นปัญหาที่มีอยู่แล้วและไม่เคยถูกจับได้มาก่อน ต้องส่งให้ทีม dev ตรวจว่าต้นทุนขายจริงถูกนับซ้ำสองครั้งในบัญชีหรือไม่",
         pre="ทำ TC-E2E-M1-08 เสร็จแล้ว (Delivery = Done)",
         steps=["เปิด Accounting &gt; Journal Entries", "ค้นหา entry ที่มี Reference ตรงกับเลขที่ใบส่งของ (เช่น EG01/OUT/00043)", "เปิดดูรายละเอียดบรรทัด"],
         sample="-",
         expected="(พฤติกรรมที่พบจริงตอนนี้ ยังไม่ใช่ผลที่ถูกต้อง) เห็นคู่ COGS/Inventory ซ้ำอีกชุดในบัญชีคนละตัวจากข้อ 11 — ควรแจ้งทีมพัฒนาให้ตรวจสอบ ไม่ควรถือว่าผ่านการทดสอบจนกว่าจะยืนยันว่าไม่ใช่การนับซ้ำจริง", prio="High"),
    dict(id="TC-E2E-M1-13", scenario="สรุปเทียบกำไรขั้นต้น (Gross Margin) ของรายการนี้",
         pre="ทำ TC-E2E-M1-11 เสร็จแล้ว",
         steps=["คำนวณเอง: รายได้ (ไม่รวม VAT) ลบ ต้นทุนขาย (COGS)", "เทียบกับตัวเลขที่ระบบโชว์ (เช่นใน Analytic/Reporting ถ้ามี)"],
         sample="รายได้ = 212,500<br>COGS (นับครั้งเดียว) = 153,000.08",
         expected="กำไรขั้นต้น = 59,499.92 — ใช้ตัวเลขนี้เป็นฐานเทียบ ถ้า TC-E2E-M1-12 ยืนยันว่ามีการนับ COGS ซ้ำจริง กำไรที่ระบบสรุปในรายงานภาพรวมอาจต่ำกว่าความเป็นจริง ต้องระวังตอนอ่านรายงาน", prio="Medium"),
  ]),
]
