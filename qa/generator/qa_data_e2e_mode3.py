# Single source of truth for EMG-O E2E flow test cases — Mode 3
# (Cut-to-Order): sell a Block-backed material before any slab exists, then
# cut the exact slab after the sale, price recalculating to the real cut
# size automatically. Same spirit as qa_data_e2e_mode1/2.py.
#
# FULL REWRITE 2026-09-14 (v2, not just a screenshot refresh) — the day
# before (2026-09-13, Session 129, ADR-061/062), the ENTIRE mechanism this
# doc used to test was torn down: the "Factory Worklist" page and its
# "Cut to Order"/"Request Material" wizards (repair.order, Factory
# Worklist views) were deleted outright and replaced with a plain native
# Manufacturing Order — Admin picks the Block directly on a native MO (no
# wizard, no dedicated Worklist page), sets Target L/H and (if selling
# against a real order) links "For Sale Order Line" directly. The v1 case
# list (built around Factory Worklist/Request Material/Cut to Order
# buttons that no longer exist) is fully obsolete, not just stale numbers
# — see qa/_archive/test-cases-e2e-mode3.html for that version.
#
# This is also the SAME native-MO mechanism used to seed Mode 2's
# ready-made stock (see qa_data_e2e_mode2.py's build notes for the real
# material_lot_id bug found+fixed there) — that fix was already deployed
# before this doc was built, so this run reflects the corrected code.
# Cut-to-Order (Mode 3) uses Serial-mode materials only, so it was never
# exposed to that specific Lot-mode bug, but this is still the first real
# live Playwright click-through of the new mechanism's "has a real SO
# to link" path (sale_order_line_id + auto price recalc + auto-hold),
# which the Session 129/130 notes hadn't verified live either.
#
# Built + the whole flow executed live on mbx-ee-dev (Playwright, 2026-09-14)
# before writing this file — every "sample data"/"expected result" below is
# a REAL observed number from that run, on a brand-new dedicated test
# material ("E2E Mode3 Fresh Test") so nothing carries over cost history
# from another mode's fixture (see qa_data_e2e_mode1.py for why that
# matters — cross-fixture FIFO contamination):
#   PO P00053 (3.00 m3 @ 15,000/m3) -> Block BLK-26-0028 -> Vendor Bill
#   BILL/2026/09/0005 (48,150.00) -> SO S00125 (uncut Slab line, confirmed
#   at list price 4,815.00) -> MO EG01/STCUT/00042 (Stone Block =
#   BLK-26-0028, Target 1.2 x 0.8 m, For Sale Order Line = S00125, blocked
#   once for real until the Block was moved to Stone Production via
#   Internal Transfer EG01/INT/00058) -> Complete Cut -> Slab
#   BLK-26-0028-1 (0.96 Sq.Mt.) auto-holds to the SO line, SO price
#   auto-recalculates 4,815.00 -> 4,622.40 -> Delivery EG01/OUT/00079
#   (scan-verified) -> Invoice INV/2026/00027 (4,622.40 incl. VAT, COGS
#   300.00, correct dedicated account, no duplicate JE), Posted + In
#   Payment. Fixture kept on mbx-ee-dev as genuine reference data.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber/green callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low)

CATEGORIES = [
  dict(cat_id="E1", title="E1. ขาย (Sale — ก่อนมีแผ่นจริง)",
       subtitle="ADR-018 — ขายได้ทันทีแม้ยังไม่มีแผ่น ราคาจะคำนวณจริงหลังตัดเสร็จ · 2 test cases",
       cases=[
    dict(id="TC-E2E-M3-01", scenario="เพิ่มบรรทัดสินค้า Material ที่ยังไม่มีแผ่นจริงในสต็อก",
         pre="มี Block พร้อมอยู่แล้วในสต็อก (ยังไม่ตัด) จาก Material ที่ตั้ง Pricing Mode = Serial (per-slab)",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material นั้น"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = E2E Mode3 Fresh Test - Slab",
         expected="เพิ่มบรรทัดสำเร็จ ราคาต่อหน่วยขึ้นเป็นราคาตั้งต้นของสินค้า (list price) เนื่องจากยังไม่มีแผ่นจริงผูกกับบรรทัดนี้เลย (ตัวอย่างจริง: 4,500/หน่วย)", prio="Medium",
         shot="assets/e2e-mode3/m3-01-so-line-added.png"),
    dict(id="TC-E2E-M3-02", scenario="ยืนยัน (Confirm) Sale Order ทั้งที่ยังไม่มีแผ่นจริง",
         pre="ทำ TC-E2E-M3-01 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น Sales Order ยอดรวมคำนวณจากราคาตั้งต้นของสินค้า (ตัวอย่างจริง: S00125, 4,500 + VAT 7% = 4,815.00 บาท) — ราคานี้ยังไม่ใช่ราคาจริง จะคำนวณใหม่อัตโนมัติหลังตัดเสร็จ (ดู TC-E2E-M3-07) มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ แต่ยังส่งไม่ได้เพราะยังไม่มีของจริง", prio="High",
         shot="assets/e2e-mode3/m3-02-so-confirmed.png"),
  ]),
  dict(cat_id="E2", title="E2. ผลิต (Production — ตัด Slab จริง)",
       subtitle="กลไกใหม่ 13 ก.ย. 2026 — สร้าง Manufacturing Order ตรงในแอป Manufacturing ไม่ต้องผ่าน wizard แล้ว · 5 test cases",
       cases=[
    dict(id="TC-E2E-M3-03", scenario="สร้าง Manufacturing Order ผูกกับ Block และ SO line โดยตรง",
         note="✨ กลไกใหม่ (เปลี่ยน 13 ก.ย. 2026): ไม่มี \"Factory Worklist\"/\"Cut to Order\" wizard แล้ว — Admin สร้าง Manufacturing Order ตรงในแอป Manufacturing ได้เลย เลือก Block ที่ช่อง \"Stone Block\" ระบบจะเติม Product/Bill of Material ให้อัตโนมัติ",
         pre="ทำ TC-E2E-M3-02 เสร็จแล้ว มี Block พร้อมอยู่แล้วในสต็อก (ยังไม่ตัด)",
         steps=["เปิด Manufacturing &gt; New", "เลือก \"Stone Block\" เป็น Block ที่ต้องการตัด", "กรอก \"Target Slab L (M)\" และ \"Target Slab H (M)\"", "เลือก \"For Sale Order Line\" ผูกกับบรรทัด SO ที่รอแผ่นอยู่"],
         sample="Stone Block = BLK-26-0028<br>Target Slab L (M) = 1.2<br>Target Slab H (M) = 0.8<br>For Sale Order Line = S00125",
         expected="สร้าง Manufacturing Order สำเร็จ ระบบเติม Product และ Bill of Material ให้อัตโนมัติจาก Block ที่เลือก (ตัวอย่างจริง: EG01/STCUT/00042)", prio="High",
         shot="assets/e2e-mode3/m3-03-mo-linked-to-so.png"),
    dict(id="TC-E2E-M3-04", scenario="พยายาม Confirm Manufacturing Order โดย Block ยังไม่ได้ย้ายไปสถานีตัด",
         pre="ทำ TC-E2E-M3-03 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Manufacturing Order ทันที"],
         sample="-",
         expected="ระบบฟ้อง error สองภาษาทันที ระบุปริมาณที่ต้องการเทียบกับที่มีอยู่จริงที่สถานีตัด บันทึกไม่ผ่าน — ตัวอย่างจริง: \"Block BLK-26-0028 ยังไม่ได้ย้ายไปสถานีตัด (Stone Production) เพียงพอ — ต้องการ 0.019 m&sup3; แต่อยู่ที่สถานีตัดแล้วแค่ 0.000 m&sup3;\"", prio="High",
         shot="assets/e2e-mode3/m3-04-cut-blocked.png"),
    dict(id="TC-E2E-M3-05", scenario="ย้าย Block ไปสถานีตัด (Internal Transfer)",
         pre="ทำ TC-E2E-M3-04 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["เปิด Inventory &gt; Internal Transfers &gt; New", "Source Location = Stone Available, Destination Location = Stone Production", "เพิ่มสินค้า Block นั้น กรอกจำนวนที่ต้องการย้าย", "กด Validate"],
         sample="สินค้า = E2E Mode3 Fresh Test - Block<br>จำนวน = 0.02 m&sup3;",
         expected="ใบย้ายสถานะเปลี่ยนเป็น Done สำเร็จ — ตัวอย่างจริง: EG01/INT/00058 — Block ก้อนนั้นย้ายไปอยู่ที่ Location \"Stone Production\" ครบตามจำนวนที่ย้าย", prio="High",
         shot="assets/e2e-mode3/m3-06-transfer-done.png"),
    dict(id="TC-E2E-M3-06", scenario="กลับไป Confirm Manufacturing Order อีกครั้ง",
         pre="ทำ TC-E2E-M3-05 เสร็จแล้ว",
         steps=["กลับไปที่ Manufacturing Order เดิม", "กดปุ่ม Confirm อีกครั้ง"],
         sample="-",
         expected="ยืนยันสำเร็จ ไม่มี error แล้ว เพราะ Block ถูกย้ายมาสถานีตัดครบตามจำนวนแล้ว — สถานะเปลี่ยนเป็น Confirmed ปุ่ม \"Complete Cut\" ปรากฏพร้อมกดขั้นถัดไป", prio="High",
         shot="assets/e2e-mode3/m3-07-mo-confirmed-ok.png"),
    dict(id="TC-E2E-M3-07", scenario="กด \"Complete Cut\" — ได้แผ่นจริง ราคา SO คำนวณใหม่อัตโนมัติ",
         pre="ทำ TC-E2E-M3-06 เสร็จแล้ว",
         steps=["กดปุ่ม \"Complete Cut\" บน Manufacturing Order", "กลับไปเปิด Sale Order เดิมดูราคา"],
         sample="-",
         expected="Manufacturing Order เสร็จสมบูรณ์ (สถานะ Done) เกิดแผ่นหินใหม่ 1 แผ่นตามขนาดที่ตัดจริง (Lot/Serial ใหม่) ผูกกับบรรทัด SO เดิมให้อัตโนมัติ ราคาต่อหน่วยของบรรทัด SO เปลี่ยนจากราคาตั้งต้นเป็นราคาจริงตามขนาดที่ตัดได้ทันที — ตัวอย่างจริง: แผ่น BLK-26-0028-1 (1.2&times;0.8 ม. = 0.96 ตร.ม.) ยอดรวม SO เปลี่ยนจาก 4,815.00 เป็น 4,622.40 (รวม VAT) ทันที เห็นการเปลี่ยนแปลงบันทึกไว้ใน chatter log ของ SO", prio="High",
         shot="assets/e2e-mode3/m3-09-so-price-recalc.png"),
  ]),
  dict(cat_id="E3", title="E3. จัดส่ง (Delivery — Scan Verification)",
       subtitle="ADR-009 — ต้องสแกน/กรอก Serial ให้ตรงก่อน Validate เสมอ ยังใช้ตรรกะเดิม ไม่เปลี่ยนตามกลไกตัดใหม่ · 2 test cases",
       cases=[
    dict(id="TC-E2E-M3-08", scenario="พยายาม Validate ใบส่งของโดยยังไม่กรอก Scanned Serial ให้ตรง",
         pre="ทำ TC-E2E-M3-07 เสร็จแล้ว มีใบส่งของสถานะ Ready รออยู่",
         steps=["เปิดใบส่งของ (Delivery) ที่เกิดขึ้นอัตโนมัติ", "ถ้าสถานะยังเป็น \"Waiting\" ให้กด \"Check Availability\" ก่อน 1 ครั้ง", "กดปุ่ม Validate ทันทีโดยยังไม่กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial ของแผ่นที่ตัดจริง"],
         sample="-",
         expected="ระบบฟ้อง error สองภาษาทันที: \"สแกน Serial ไม่ตรง กรุณาสแกนให้ครบก่อน Validate: BLK-26-0028-1\" บันทึกไม่ผ่าน", prio="High",
         shot="assets/e2e-mode3/m3-11-delivery-scan-error.png"),
    dict(id="TC-E2E-M3-09", scenario="กรอก/สแกน Scanned Serial ให้ตรงแล้ว Validate",
         pre="ทำ TC-E2E-M3-08 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["เปิดบรรทัดในใบส่งของ กด \"Details\"", "กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial ของแผ่นที่ตัดจริง แล้วกด Save", "กดปุ่ม Validate อีกครั้ง"],
         sample="Scanned Serial = BLK-26-0028-1",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done สำเร็จ — แผ่นที่ขายหายจากสต็อกที่ขายได้ (Available) แล้ว — ตัวอย่างจริง: EG01/OUT/00079", prio="High",
         shot="assets/e2e-mode3/m3-13-delivery-done.png"),
  ]),
  dict(cat_id="E4", title="E4. บัญชี (Accounting + Payment)",
       subtitle="ออกใบแจ้งหนี้ + รับชำระเงิน + ตรวจรายการบัญชี · 4 test cases",
       cases=[
    dict(id="TC-E2E-M3-10", scenario="สร้างและยืนยันใบแจ้งหนี้ลูกค้า (Customer Invoice)",
         pre="ทำ TC-E2E-M3-09 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; Create Draft", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO หลังคำนวณราคาใหม่แล้ว (ตัวอย่างจริง: INV/2026/00027, 4,622.40)", prio="High",
         shot="assets/e2e-mode3/m3-14-invoice-posted.png"),
    dict(id="TC-E2E-M3-11", scenario="รับชำระเงิน (Register Payment) บนใบแจ้งหนี้",
         pre="ทำ TC-E2E-M3-10 เสร็จแล้ว (Invoice = Posted)",
         steps=["เปิดใบแจ้งหนี้ &gt; กด \"Pay\"", "ตรวจ/ยืนยันยอดและวิธีชำระ &gt; กด Create Payment"],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นสถานะ \"In Payment\" — ตัวอย่างจริง: INV/2026/00027 จบที่สถานะ Posted + In Payment", prio="Medium",
         shot="assets/e2e-mode3/m3-16-invoice-paid.png"),
    dict(id="TC-E2E-M3-12", scenario="ตรวจรายการบัญชีบนใบแจ้งหนี้ (รายได้ + COGS + VAT + ลูกหนี้)",
         pre="ทำ TC-E2E-M3-10 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="เห็น 5 บรรทัดบนใบแจ้งหนี้ใบเดียว: เครดิต \"411130 Sales Revenue - Cut-to-Order (Mode 3)\" (บัญชีเฉพาะของ Mode 3 ไม่ใช่บัญชีทั่วไป), เดบิต \"113110 Inventory\" (ตัดออก), เดบิต \"511110 COGS - Stone Sales (all modes)\", เครดิต Output VAT, เดบิต Trade Receivables — ตัวอย่างจริง INV/2026/00027: รายได้ 4,320.00 / COGS-Inventory คู่ละ 300.00 / VAT 302.40 / ลูกหนี้ 4,622.40 (ยอดรวมสมดุล 4,922.40 = 4,922.40) พร้อม Analytic Distribution ครบ 3 มิติ", prio="High",
         shot="assets/e2e-mode3/m3-15-invoice-journal-items.png"),
    dict(id="TC-E2E-M3-13", scenario="ตรวจว่าไม่มี Journal Entry ซ้ำจากใบส่งของ (ไม่มี COGS ซ้ำ)",
         pre="ทำ TC-E2E-M3-09 เสร็จแล้ว (Delivery = Done)",
         steps=["เปิด Accounting &gt; Journal Entries", "ค้นหา entry ที่มี Reference ตรงกับเลขที่ใบส่งของ (เช่น EG01/OUT/00079)"],
         sample="-",
         expected="ไม่พบ Journal Entry แยกต่างหากสำหรับใบส่งของนี้เลย (มีเฉพาะ entry ของขั้นตอนตัด/ผลิตซึ่งเป็นคนละเรื่องกัน) — COGS มีบันทึกอยู่ที่เดียวคือในใบแจ้งหนี้ (INV/2026/00027) ไม่มีการนับซ้ำ ยืนยันแล้วว่ากลไกตัดใหม่ (13 ก.ย. 2026) ไม่กระทบพฤติกรรมนี้", prio="High",
         shot="assets/e2e-mode3/m3-15-invoice-journal-items.png",
         shot_note="ไม่มีภาพแยกของ Journal Entries ที่ว่างเปล่า — ใช้ภาพเดียวกับ TC-E2E-M3-12 อ้างอิงว่า COGS มีบันทึกอยู่ที่เดียวจริง"),
  ]),
]
