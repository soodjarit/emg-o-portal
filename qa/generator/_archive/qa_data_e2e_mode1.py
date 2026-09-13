# Single source of truth for EMG-O E2E flow test cases — Mode 1 (Block Direct
# Sale), the full lifecycle: purchase a Block -> sell it whole -> deliver ->
# book all the accounting. Distinct from qa_data.py (feature-level checks,
# includes required-field/validation cases) — every case here is a "does the
# whole business flow work" step, written purely from what a non-technical
# UI user clicks/sees. No field-validation/error-message cases at all.
#
# REBUILT 2026-09-09 (v2) after a Cost-by-Material Analytic-Architecture and
# 2 new features shipped since the original v1 run (2026-09-06):
#   - Sales Price / CBM (auto-price for "Sell Whole Block")
#   - "สร้าง Block" shortcut button on the PO line
# Precondition (Material/Slab/Block product setup) is now its OWN Golden Path
# doc (Test Cases: Product/Material Setup) instead of being folded in here.
#
# Built + the whole flow executed once live on eg-tst (Playwright, 2026-09-09)
# before writing this file, so every "sample data"/"expected result" below is
# a REAL observed number from that run, not a guess:
#   PO P00052 (2.00 m3 @ 15,000/CBM) -> Block BLK-26-0068 (via the new
#   shortcut button) -> Vendor Bill BILL/2026/09/0002 -> SO S00091 (Sell Whole
#   Block auto-priced 17,500/CBM from the Block's own Sales Price / CBM) ->
#   Delivery EG01/OUT/00067 -> Invoice INV/2026/00003 (37,450 incl. VAT).
#   Fixture kept on eg-tst as a genuine reference (not synthetic/seeded).
#
# CORRECTIONS vs. v1 (confirmed against real code + this live run):
#   - TC-E2E-M1-12 (double-COGS): the v1 doc flagged this as an open/unverified
#     known issue. ADR-054/055 fixed the root cause in a later session
#     (2026-09-06, same day) and this rebuild's fresh run confirms it holds —
#     flipped to a green "fixed and re-verified" note, no longer a red flag.
#   - TC-E2E-M1-10/11 now show the CORRECT GL accounts (113110 Inventory /
#     511110 COGS - Block Direct Sale) — v1's fixture predated a real,
#     separately-found-and-fixed bug where nearly every stone product had no
#     product category at all, routing Bills/Invoices to generic fallback
#     accounts (511100). Fixed at the code level 2026-09-09 (categ_id now
#     auto-assigned), not just patched on the old data.
#   - New E6 category showcases the Analytic-Architecture's 3-dimension tag
#     (Block + Material Category + exact Material) merging automatically onto
#     both the Vendor Bill line and the SO/Invoice line — real screenshots of
#     the "Analytic Distribution"/"Analytic D..." columns, not asserted.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber/green callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low)

CATEGORIES = [
  dict(cat_id="E1", title="E1. ซื้อ (Purchase)",
       subtitle="ซื้อ Block หินก้อนใหม่เข้าสต๊อก · 3 test cases",
       cases=[
    dict(id="TC-E2E-M1-01", scenario="สร้างใบสั่งซื้อ (PO) ซื้อ Block",
         pre="มี Material/Block Product พร้อมแล้ว (ดู Test Cases: Product/Material Setup) และมี Vendor อยู่แล้วในระบบ",
         steps=["เปิด Purchase &gt; Orders &gt; New", "เลือก Vendor", "เพิ่มบรรทัด เลือกสินค้า Block ของวัสดุที่ต้องการ", "กรอกจำนวน (หน่วยเป็น m&sup3;) และราคาต่อหน่วย", "กด Confirm Order"],
         sample="Vendor = \"Demo Supplier - Global Stone Quarry\"<br>สินค้า = SY-TST-Onyx-Rosa - Block<br>จำนวน = 2.00 m&sup3;<br>ราคา/หน่วย = 15,000",
         expected="PO ยืนยันสำเร็จ (state = Purchase Order) ยอดรวมคำนวณถูกต้อง (จำนวน &times; ราคา + VAT) — ตัวอย่างจริงที่ทดสอบ: P00052 ยอดรวม 32,100.00", prio="High",
         shot="assets/e2e-mode1-v2/m1v2-01-po-confirmed.png"),
    dict(id="TC-E2E-M1-02", scenario="สร้าง Block (Bundle) ผ่านปุ่มลัด \"สร้าง Block\" บนบรรทัด PO",
         note="✨ ใหม่ (2026-09-09): ไม่ต้องเปิด Inventory &gt; Blocks &gt; New แล้วไปหา PO Line เองอีกต่อไป — กดปุ่มนี้ตรงบรรทัด PO ได้เลย ระบบกรอก Material/Supplier/Warehouse/Total CBM ให้อัตโนมัติจากบรรทัดนั้น ยังคงไม่มีขั้นตอน \"Validate Receipt\" แยกต่างหาก — Receipt ที่ระบบสร้างให้อัตโนมัติจาก PO จะถูกยกเลิกให้เองเบื้องหลัง (กันสต๊อกซ้ำ) ไม่ต้องไปกดอะไรกับมัน",
         pre="ทำ TC-E2E-M1-01 เสร็จแล้ว",
         steps=["บนบรรทัดของ PO ที่เพิ่งยืนยัน กดปุ่ม \"สร้าง Block\"", "ฟอร์มสร้าง Block เปิดขึ้นพร้อมกรอก Material/Supplier/Warehouse/Total CBM ให้แล้ว", "กรอก Thickness (M) เพิ่ม", "กด Save"],
         sample="Thickness (M) = 0.02<br>(Total CBM/Material/Supplier/Warehouse กรอกมาให้แล้วจาก PO)",
         expected="บันทึกสำเร็จ ได้เลขก้อนอัตโนมัติ (ตัวอย่างจริง: BLK-26-0068) ช่อง \"PO Cost / CBM\" ขึ้น 15,000 ให้เอง, \"Sales Price / CBM\" ขึ้น 17,500 ให้เองจาก List Price ของ Block Product, Remaining CBM = 2.00 (รับสต๊อกเข้าจริงแล้ว)", prio="High",
         shot="assets/e2e-mode1-v2/m1v2-02-bundle-saved.png"),
    dict(id="TC-E2E-M1-03", scenario="สร้างและยืนยันบิลผู้ขาย (Vendor Bill)",
         pre="ทำ TC-E2E-M1-01 เสร็จแล้ว (PO อยู่สถานะ Purchase Order)",
         steps=["เปิด Accounting &gt; Vendors &gt; Bills &gt; New", "เลือก Vendor เดียวกับใน PO", "ที่ช่อง \"Auto-Complete\" เลือกเลขที่ PO — ระบบดึงบรรทัด/ยอดจาก PO มาให้อัตโนมัติ", "กรอก Bill Date", "กด Confirm"],
         sample="Vendor = \"Demo Supplier - Global Stone Quarry\"<br>Auto-Complete = P00052",
         expected="บิลสถานะ Posted ยอดตรงกับ PO บัญชีที่ลงถูกต้องเป็น \"113110 Inventory - Stone Blocks (Raw)\" ไม่ใช่บัญชี COGS ทั่วไป (ตัวอย่างจริง: BILL/2026/09/0002, 32,100.00)", prio="High",
         shot="assets/e2e-mode1-v2/m1v2-03-bill-posted.png"),
  ]),
  dict(cat_id="E2", title="E2. ขาย (Sale — Mode 1)",
       subtitle="ขายทั้งก้อนตาม CBM (ADR-019) · 3 test cases",
       cases=[
    dict(id="TC-E2E-M1-04", scenario="สร้าง Sale Order ให้ลูกค้า",
         pre="-",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้า Block ของวัสดุเดียวกับที่ซื้อไว้ (TC-E2E-M1-02)"],
         sample="ลูกค้า = \"E2E Test Customer\"<br>สินค้า = SY-TST-Onyx-Rosa - Block",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Sell Whole Block\" ปรากฏบนบรรทัดนั้น (ราคาที่ขึ้นตอนนี้เป็นแค่ List Price เริ่มต้นของสินค้า ยังไม่ใช่ราคาจริงของก้อนนี้)", prio="Medium",
         shot="assets/e2e-mode1-v2/m1v2-04-so-line-added.png"),
    dict(id="TC-E2E-M1-05", scenario="กด \"Sell Whole Block\" เลือกก้อนที่ซื้อมา — ราคาคำนวณอัตโนมัติ",
         note="✨ ใหม่ (2026-09-09): เดิม Unit Price ต้องพิมพ์เองหลังเลือกก้อน ตอนนี้ระบบดึง \"Sales Price / CBM\" ของก้อนนั้นมาใส่ให้อัตโนมัติทันทีที่กด Confirm Selection — พิมพ์ราคาอื่นทับไว้ก่อนก็ได้ ระบบจะเขียนทับด้วยราคาจริงของก้อนเสมอ",
         pre="ทำ TC-E2E-M1-04 เสร็จแล้ว, มี Block สถานะ Available จาก TC-E2E-M1-02",
         steps=["กดปุ่ม \"Sell Whole Block\" บนบรรทัด", "หน้าต่าง \"Select Block\" เลือก Block ที่ซื้อไว้ (เช่น BLK-26-0068)", "กด \"Confirm Selection\""],
         sample="เลือก Block = BLK-26-0068",
         expected="บรรทัด SO ปรับจำนวนเป็น CBM ทั้งหมดของก้อนนั้นอัตโนมัติ (2.00) ราคาต่อหน่วยเปลี่ยนเป็น 17,500.00 ทันที (จาก Sales Price / CBM ของก้อน ไม่ใช่ราคาที่พิมพ์ไว้ก่อนหน้า) ยอดรวมบรรทัด 35,000.00", prio="High",
         shot="assets/e2e-mode1-v2/m1v2-05-so-after-sell-whole-block.png",
         shot_note="เห็นในช่อง Log ด้านขวาด้วยว่าระบบเขียนทับราคาที่พิมพ์ไว้ก่อน (99,999) ด้วยราคาจริงของก้อน"),
    dict(id="TC-E2E-M1-06", scenario="ยืนยัน (Confirm) Sale Order",
         pre="ทำ TC-E2E-M1-05 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นให้อัตโนมัติ 1 ใบ (ตัวอย่างจริง: S00091 &rarr; EG01/OUT/00067)", prio="High",
         shot="assets/e2e-mode1-v2/m1v2-14-so-line-with-analytic-col.png",
         shot_note="ภาพเดียวกับ TC-E2E-M1-14 — เห็นทั้งสถานะ Sales Order และคอลัมน์ Analytic Distribution ในภาพเดียวกัน"),
  ]),
  dict(cat_id="E3", title="E3. ผลิต (Production)",
       subtitle="Mode 1 ไม่มีขั้นตอนนี้ · 0 test cases",
       cases=[
    dict(id="TC-E2E-M1-N/A", scenario="(ไม่มี Test Case ในหมวดนี้สำหรับ Mode 1)",
         note="Mode 1 ขายทั้งก้อนโดยไม่ผ่านการตัด/ผลิตใดๆ — ลูกค้าซื้อก้อนดิบทั้งก้อนไปทั้งดุ้น ไปต่อที่การจัดส่งได้เลย ขั้นตอนผลิตจะมีใน Mode 3 (Cut-to-Order)/Mode 5 (FG Production) เท่านั้น",
         pre="-", steps=["-"], sample="-", expected="-", prio="Low"),
  ]),
  dict(cat_id="E4", title="E4. จัดส่ง (Delivery)",
       subtitle="ส่งของจริงออกจากคลัง · 2 test cases",
       cases=[
    dict(id="TC-E2E-M1-07", scenario="เปิดใบส่งของ (Delivery Order) ที่เกิดขึ้นอัตโนมัติ",
         pre="ทำ TC-E2E-M1-06 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กดปุ่ม Delivery (smart button ด้านบน)"],
         sample="-",
         expected="เห็นใบส่งของสถานะ \"Ready\" สินค้า 1 บรรทัด จำนวนตรงกับ SO (2.00 m&sup3;)", prio="Medium",
         shot="assets/e2e-mode1-v2/m1v2-07-delivery-ready.png"),
    dict(id="TC-E2E-M1-08", scenario="ยืนยันการส่งของจริง (Validate)",
         pre="ทำ TC-E2E-M1-07 เสร็จแล้ว",
         steps=["กดปุ่ม Validate บนใบส่งของ"],
         sample="-",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done (ตัวอย่างจริง: EG01/OUT/00067) — Block ก้อนนั้นหายจากสต๊อกที่ขายได้ (Available) แล้ว", prio="High",
         shot="assets/e2e-mode1-v2/m1v2-08-delivery-done.png"),
  ]),
  dict(cat_id="E5", title="E5. บัญชี (Accounting)",
       subtitle="ออกใบแจ้งหนี้ + ตรวจรายการบัญชีของทั้งเรื่อง · 4 test cases",
       cases=[
    dict(id="TC-E2E-M1-09", scenario="สร้างและยืนยันใบแจ้งหนี้ลูกค้า (Customer Invoice)",
         pre="ทำ TC-E2E-M1-08 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; Create Draft", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO รวม VAT (ตัวอย่างจริง: INV/2026/00003, 37,450.00)", prio="High",
         shot="assets/e2e-mode1-v2/m1v2-09-invoice-posted.png"),
    dict(id="TC-E2E-M1-10", scenario="ตรวจรายการบัญชีฝั่งซื้อ — Vendor Bill",
         pre="ทำ TC-E2E-M1-03 เสร็จแล้ว",
         steps=["เปิด Vendor Bill &gt; แท็บ \"Journal Items\""],
         sample="-",
         expected="เห็น 3 บรรทัด: เดบิต 113110 Inventory - Stone Blocks (ยอดสินค้าก่อน VAT), เดบิต 114200 Input VAT, เครดิต 212100 Trade Payables (ยอดรวม) — ตัวอย่างจริง: 30,000 / 2,100 / 32,100 บัญชีถูกต้องตรงตัว ไม่ใช่บัญชี COGS ทั่วไป", prio="Medium",
         shot="assets/e2e-mode1-v2/m1v2-10-bill-journal-items.png"),
    dict(id="TC-E2E-M1-11", scenario="ตรวจรายการบัญชีฝั่งรายได้ + ต้นทุนขาย บนใบแจ้งหนี้",
         pre="ทำ TC-E2E-M1-09 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; แท็บ \"Journal Items\""],
         sample="-",
         expected="เห็น 5 บรรทัดบนใบแจ้งหนี้ใบเดียว: เครดิต 411110 Sales Revenue - Block Direct Sale (Mode 1), เดบิต 113110 Inventory (ตัดออก), เดบิต 511110 COGS - Block Direct Sale (Mode 1), เครดิต 213200 Output VAT, เดบิต 112100 Trade Receivables — ตัวอย่างจริง: รายได้ 35,000 / COGS-Inventory คู่ละ 30,000 / VAT 2,450 / ลูกหนี้ 37,450 (ยอดรวมสมดุล 67,450 = 67,450)", prio="High",
         shot="assets/e2e-mode1-v2/m1v2-11-invoice-journal-items.png"),
    dict(id="TC-E2E-M1-12", scenario="ตรวจว่าต้นทุนขาย (COGS) ถูกบันทึกซ้ำหรือไม่",
         note="✅ ปิดเคสแล้ว — ตรวจซ้ำด้วย fixture ใหม่ (2026-09-09) ยืนยันว่าการแก้ไข ADR-054/055 (session ก่อนหน้า) ยังใช้ได้ดี: ไม่มี Journal Entry แยกต่างหากจากใบส่งของอีกต่อไป (เดิมมีปัญหาชื่อขึ้นต้น STJ ซ้ำกับใบแจ้งหนี้) — Delivery ไม่สร้าง Journal Entry ของตัวเองแล้ว COGS มีบันทึกอยู่ที่เดียวคือในใบแจ้งหนี้ (TC-E2E-M1-11)",
         pre="ทำ TC-E2E-M1-08 เสร็จแล้ว (Delivery = Done)",
         steps=["เปิด Accounting &gt; Journal Entries", "ค้นหา entry ที่มี Reference ตรงกับเลขที่ใบส่งของ (เช่น EG01/OUT/00067)"],
         sample="-",
         expected="ไม่พบ Journal Entry แยกต่างหากสำหรับใบส่งของนี้เลย — COGS/Inventory มีบันทึกอยู่ที่เดียวคือในใบแจ้งหนี้ (INV/2026/00003) ไม่มีการนับซ้ำ", prio="High",
         shot="assets/e2e-mode1-v2/m1v2-11-invoice-journal-items.png",
         shot_note="ไม่มีภาพแยกของ Journal Entries ที่ว่างเปล่า — ใช้ภาพเดียวกับ TC-E2E-M1-11 อ้างอิงว่า COGS มีบันทึกอยู่ที่เดียวจริง"),
  ]),
  dict(cat_id="E6", title="E6. สรุปกำไร (Gross Margin)",
       subtitle="สรุปเทียบกำไรขั้นต้นของทั้งเรื่อง · 1 test case",
       cases=[
    dict(id="TC-E2E-M1-13", scenario="สรุปเทียบกำไรขั้นต้น (Gross Margin) ของรายการนี้",
         pre="ทำ TC-E2E-M1-11 เสร็จแล้ว",
         steps=["คำนวณเอง: รายได้ (ไม่รวม VAT) ลบ ต้นทุนขาย (COGS)"],
         sample="รายได้ = 35,000<br>COGS (นับครั้งเดียว) = 30,000",
         expected="กำไรขั้นต้น = 5,000.00 (35,000 &minus; 30,000) — ตัวเลขนี้ตรงกับที่เห็นในใบแจ้งหนี้ TC-E2E-M1-11 พอดี ไม่มี COGS ซ้ำมากวนตัวเลข", prio="Medium",
         shot="assets/e2e-mode1-v2/m1v2-11-invoice-journal-items.png",
         shot_note="ภาพเดียวกับ TC-E2E-M1-11 — ตัวเลขรายได้/COGS ที่ใช้คำนวณกำไรขั้นต้นอยู่ในภาพนี้แล้ว ไม่มีหน้าจอสรุปกำไรแยกต่างหาก"),
  ]),
  dict(cat_id="E7", title="E7. ต้นทุนแยกตามมิติ (Cost-by-Material Analytics)",
       subtitle="Analytic-Architecture ใหม่ 2026-09-09 · 2 test cases",
       cases=[
    dict(id="TC-E2E-M1-14", scenario="ตรวจว่า Analytic Account ทั้ง 3 มิติติดมาอัตโนมัติบนบรรทัด SO",
         note="✨ ใหม่ (2026-09-09): ทุกบรรทัดที่ผูกกับ Block จะถูกแท็กเข้า 3 มิติพร้อมกันโดยอัตโนมัติ — Block (ก้อนนี้โดยเฉพาะ), หมวดวัสดุ (เช่น Marble ใช้ร่วมกันได้ทุก Marble), และวัสดุ (เฉพาะ SY-TST-Onyx-Rosa) ไม่ต้องพิมพ์เอง ทำให้ดูกำไร/ต้นทุนแยกได้ทั้งรายก้อน รายหมวดวัสดุ หรือรายวัสดุเป๊ะๆ",
         pre="ทำ TC-E2E-M1-06 เสร็จแล้ว",
         steps=["เปิด Sale Order ที่ confirm แล้ว", "ที่ตาราง Order Lines กดไอคอนตั้งค่าคอลัมน์ (มุมขวาบนตาราง) เปิดคอลัมน์ \"Analytic Distribution\""],
         sample="-",
         expected="เห็น 2 ป้ายบนบรรทัดเดียว: \"Marble | SY-TST-Onyx-Rosa\" (หมวดวัสดุ+วัสดุ) และ \"BLK-26-0068\" (ก้อนนี้โดยเฉพาะ) — ไม่ต้องตั้งค่าเอง ระบบแท็กให้ตั้งแต่กด Sell Whole Block", prio="Medium",
         shot="assets/e2e-mode1-v2/m1v2-14-so-line-with-analytic-col.png"),
    dict(id="TC-E2E-M1-15", scenario="ตรวจว่า Analytic Account เดียวกันติดมาถึงบัญชีจริงด้วย ไม่ใช่แค่บนหน้าจอขาย",
         pre="ทำ TC-E2E-M1-11 เสร็จแล้ว",
         steps=["เปิด Vendor Bill หรือ Customer Invoice &gt; แท็บ Journal Items", "ดูคอลัมน์ \"Analytic Distribution\""],
         sample="-",
         expected="ทุกบรรทัดบัญชี (Inventory, COGS, Revenue) มีป้าย Analytic เดียวกันติดมาด้วย — ต้นทุน/รายได้ก้อนนี้ดึงแยกได้ทันทีจากรายงาน Analytic โดยไม่ต้องรอบัญชีมาแปะป้ายย้อนหลัง", prio="Medium",
         shot="assets/e2e-mode1-v2/m1v2-11-invoice-journal-items.png"),
  ]),
]
