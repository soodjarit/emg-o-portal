# Single source of truth for EMG-O E2E flow test cases — Mode 3
# (Cut-to-Order): sell a Block-backed material before any slab exists, then
# cut the exact slab(s) after the sale, price recalculating to the real cut
# size automatically. Same spirit as qa_data_e2e_mode1/2.py.
#
# FULL REWRITE 2026-09-16 (v3, not just a screenshot refresh) — the v2 doc
# (built 2026-09-14, native-MO mechanism replacing the deleted Factory
# Worklist/wizards, ADR-061/062) modeled 1 Cut Order MO as producing exactly
# 1 Slab (qty_producing=1). Later THAT SAME DAY (Session 135, ADR-066), the
# real factory process was corrected: 1 MO consumes 1 Block and can produce
# MULTIPLE Slabs in one physical cut — the system now auto-plans N expected
# Slabs from the Block's remaining CBM and the target size, Factory records
# each Slab's ACTUAL dimensions after cutting (may deviate from plan) in a
# new "Planned/Actual Slabs" tab, and a Yield % is computed automatically.
# Session 136-138 (2026-09-16) then added a guided step layout (Step 1/2/3
# groups + colored banners) and the "ย้ายด่วน (Move to Production)" one-click
# button (replaces manually creating+validating an Internal Transfer by
# hand) directly on the MO form. This doc tests that current combined
# mechanism — every screen/button v2 referenced for the production section
# changed shape, not just the underlying numbers.
#
# Built + the whole flow executed live on mbx-ee-dev (Playwright, 2026-09-16)
# before writing this file — every "sample data"/"expected result" below is
# a REAL observed number from that run, on a fresh Block (same dedicated
# test material as v2, "E2E Mode3 Fresh Test", to stay isolated from other
# modes' fixtures — see qa_data_e2e_mode1.py for why that matters):
#   PO P00055 (0.024 m3, rounds to 0.02 m3 at 2-decimal UoM precision) ->
#   Block BLK-26-0030 -> Vendor Bill BILL/2026/09/0007 (321.00) -> SO S00131
#   (uncut Slab line, confirmed at list price 4,815.00) -> MO EG01/STCUT/00044
#   (Stone Block = BLK-26-0030, Target 0.80 x 0.50 m -> system auto-plans 2
#   Slabs from 0.02 m3 remaining / 0.008 m3 per slab, For Sale Order Line =
#   S00131) -> Confirm blocked once for real (needed 0.016 m3, 0.000 at
#   Stone Production) -> "ย้ายด่วน (Move to Production)" one-click (moved
#   0.020 units) -> Confirm succeeds -> Work Orders (Transport + Gangsaw)
#   both finished -> Planned/Actual Slabs: Slab 1 actual 0.78 x 0.49 m
#   (real saw-kerf loss vs. 0.80 x 0.50 planned), Slab 2 actual exactly
#   matches plan -> Yield 97.78% (no exception, threshold is >10%) ->
#   Complete Cut -> 2 real Slabs minted (BLK-26-0030-1 auto-held to the SO
#   line at 0.3822 Sq.Mt., BLK-26-0030-2 stays Available as surplus stock)
#   -> SO price auto-recalculates 4,815.00 -> 1,840.29 -> Delivery
#   EG01/OUT/00085 (scan-verified against BLK-26-0030-1) -> Invoice
#   INV/2026/00033 (1,840.29 incl. VAT, COGS 150.00, correct dedicated
#   account, no duplicate JE), Posted + In Payment. Fixture kept on
#   mbx-ee-dev as genuine reference data.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber/green callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low), shot (screenshot path)

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
         expected="SO เปลี่ยนสถานะเป็น Sales Order ยอดรวมคำนวณจากราคาตั้งต้นของสินค้า (ตัวอย่างจริง: S00131, 4,500 + VAT 7% = 4,815.00 บาท) — ราคานี้ยังไม่ใช่ราคาจริง จะคำนวณใหม่อัตโนมัติหลังตัดเสร็จ (ดู TC-E2E-M3-09) มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ แต่ยังส่งไม่ได้เพราะยังไม่มีของจริง", prio="High",
         shot="assets/e2e-mode3/m3-02-so-confirmed.png"),
  ]),
  dict(cat_id="E2", title="E2. ผลิต (Production — ตัด Block→Slab แบบวางแผน/บันทึกจริง)",
       subtitle="กลไกใหม่ 14 ก.ย.-16 ก.ย. 2026 (ADR-066 + Session 136-138) — วางแผนจำนวนแผ่นอัตโนมัติ, ปุ่ม \"ย้ายด่วน\", banner นำทาง, บันทึกขนาดจริง+Yield % · 7 test cases",
       cases=[
    dict(id="TC-E2E-M3-03", scenario="สร้าง Manufacturing Order ผูกกับ Block และ SO line — ระบบวางแผนจำนวนแผ่นให้อัตโนมัติ",
         note="✨ กลไกใหม่ (เปลี่ยน 14 ก.ย. 2026, ADR-066): เลือก Block + กรอกขนาดที่ต้องการ (Target Slab L/H) แล้วระบบจะคำนวณเองว่าก้อนนี้ตัดได้กี่แผ่น เติมแถว \"Planned/Actual Slabs\" ให้อัตโนมัติ — ไม่ต้องสร้าง MO ทีละแผ่นแบบเดิมอีกแล้ว",
         pre="ทำ TC-E2E-M3-02 เสร็จแล้ว มี Block พร้อมอยู่แล้วในสต็อก (ยังไม่ตัด)",
         steps=["เปิด Manufacturing &gt; New", "เลือก \"Stone Block\" เป็น Block ที่ต้องการตัด", "กรอก \"Target Slab L (M)\" และ \"Target Slab H (M)\"", "เลือก \"For Sale Order Line\" ผูกกับบรรทัด SO ที่รอแผ่นอยู่"],
         sample="Stone Block = BLK-26-0030<br>Target Slab L (M) = 0.80<br>Target Slab H (M) = 0.50<br>For Sale Order Line = S00131",
         expected="สร้าง Manufacturing Order สำเร็จ (ตัวอย่างจริง: EG01/STCUT/00044) แท็บ \"Planned/Actual Slabs\" มี 2 แถวเกิดขึ้นเองอัตโนมัติ (ก้อนนี้ตัดได้ 2 แผ่นจากขนาดที่กรอก) banner สีเหลืองด้านบนแจ้งว่ายังไม่พร้อม Confirm", prio="High",
         shot="assets/e2e-mode3/m3-03-mo-created.png"),
    dict(id="TC-E2E-M3-04", scenario="พยายาม Confirm Manufacturing Order โดย Block ยังไม่ได้ย้ายไปสถานีตัด",
         pre="ทำ TC-E2E-M3-03 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Manufacturing Order ทันที"],
         sample="-",
         expected="ระบบฟ้อง error สองภาษาทันที ระบุปริมาณที่ต้องการเทียบกับที่มีอยู่จริงที่สถานีตัด บันทึกไม่ผ่าน — ตัวอย่างจริง: \"Block BLK-26-0030 ยังไม่ได้ย้ายไปสถานีตัด (Stone Production) เพียงพอ — ต้องการ 0.016 m&sup3; แต่อยู่ที่สถานีตัดแล้วแค่ 0.000 m&sup3;\"", prio="High",
         shot="assets/e2e-mode3/m3-04-confirm-blocked.png"),
    dict(id="TC-E2E-M3-05", scenario="กดปุ่ม \"ย้ายด่วน (Move to Production)\" — ย้าย Block ในคลิกเดียว",
         note="✨ ปุ่มใหม่ (Session 137, 16 ก.ย. 2026): แทนที่การออกไปสร้าง Internal Transfer เองที่เมนู Inventory แล้วต้องย้อนกลับมา — ปุ่มนี้อยู่บน MO เลย ย้าย+ยืนยันใบย้ายให้เสร็จในคลิกเดียว",
         pre="ทำ TC-E2E-M3-04 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["กดปุ่ม \"ย้ายด่วน (Move to Production)\" บน Manufacturing Order"],
         sample="-",
         expected="แจ้งเตือนสำเร็จทันที — ตัวอย่างจริง: \"ย้ายสำเร็จ (Moved). Block BLK-26-0030 ย้ายไป Stone Production แล้ว 0.020 หน่วย — กด Confirm ได้เลย\"", prio="High",
         shot="assets/e2e-mode3/m3-05-move-to-production.png"),
    dict(id="TC-E2E-M3-06", scenario="กลับไป Confirm Manufacturing Order อีกครั้ง",
         pre="ทำ TC-E2E-M3-05 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm อีกครั้ง"],
         sample="-",
         expected="ยืนยันสำเร็จ ไม่มี error แล้ว เพราะ Block ถูกย้ายมาสถานีตัดครบตามจำนวนแล้ว — สถานะเปลี่ยนเป็น Confirmed banner สีฟ้าด้านบนแนะนำขั้นตอนถัดไปให้ไปแท็บ \"Work Orders\"", prio="High",
         shot="assets/e2e-mode3/m3-06-mo-confirmed.png"),
    dict(id="TC-E2E-M3-07", scenario="ทำ Work Order ให้เสร็จ (Transport + ตัด)",
         pre="ทำ TC-E2E-M3-06 เสร็จแล้ว",
         steps=["ไปแท็บ \"Work Orders\"", "กดเริ่ม (▶) แต่ละขั้นตอนแล้วกดทำเสร็จตามลำดับจนครบทุกแถว"],
         sample="-",
         expected="ทุกแถวในแท็บ Work Orders ขึ้นสถานะ \"Finished\" ครบ (ตัวอย่างจริง: Transport → Gangsaw) MO เปลี่ยนสถานะเป็น \"To Close\" โดยอัตโนมัติ", prio="Medium",
         shot="assets/e2e-mode3/m3-07-work-orders-done.png"),
    dict(id="TC-E2E-M3-08", scenario="บันทึกขนาดที่ตัดได้จริงในแท็บ \"Planned/Actual Slabs\"",
         note="✨ กลไกใหม่ (ADR-066): แต่ละแผ่นมีคอลัมน์ Actual L/H/Thickness แยกจาก Planned — Factory แก้เฉพาะแผ่นที่ตัดได้ไม่ตรงแผน ระบบคำนวณ Yield % เทียบแผนให้อัตโนมัติที่ท้ายแท็บ",
         pre="ทำ TC-E2E-M3-07 เสร็จแล้ว",
         steps=["ไปแท็บ \"Planned/Actual Slabs\"", "แก้ไขคอลัมน์ Actual L/H ของแผ่นที่ตัดได้ไม่เท่าแผน (แผ่นอื่นปล่อยตามค่าเริ่มต้นถ้าตัดได้ตรงแผนจริง)"],
         sample="แผ่นที่ 1: Actual L = 0.78, Actual H = 0.49 (ของจริงเล็กกว่าแผนนิดหน่อยจากรอยตัด)<br>แผ่นที่ 2: Actual L = 0.80, Actual H = 0.50 (ตรงแผนเป๊ะ)",
         expected="บันทึกสำเร็จ ผลรวมท้ายแท็บคำนวณใหม่อัตโนมัติ — ตัวอย่างจริง: Planned Total 0.80 ตร.ม. / Actual Total 0.7822 ตร.ม. / Yield 97.78% (ไม่ขึ้น Exception เพราะเบี่ยงเบนไม่ถึง 10%)", prio="High",
         shot="assets/e2e-mode3/m3-08-actual-slabs-entered.png"),
    dict(id="TC-E2E-M3-09", scenario="กด \"Complete Cut\" — ได้แผ่นจริง 2 แผ่นจาก 1 ก้อน ราคา SO คำนวณใหม่อัตโนมัติ",
         note="✨ นี่คือจุดเด่นของกลไกใหม่ทั้งหมด: 1 ก้อนตัดได้หลายแผ่นในครั้งเดียว แผ่นที่ SO line ต้องการถูกจองอัตโนมัติ ส่วนแผ่นที่เหลือเก็บเป็นสต็อกส่วนเกินไว้ขายต่อ",
         pre="ทำ TC-E2E-M3-08 เสร็จแล้ว",
         steps=["กดปุ่ม \"Complete Cut\" บน Manufacturing Order", "กลับไปเปิด Sale Order เดิมดูราคา"],
         sample="-",
         expected="Manufacturing Order เสร็จสมบูรณ์ (สถานะ Done) เกิดแผ่นหินใหม่ 2 แผ่นจากก้อนเดียว (Lot/Serial ใหม่ทั้งคู่) — แผ่นที่ตรงกับความต้องการของบรรทัด SO ถูกจองให้อัตโนมัติ (ตัวอย่างจริง: BLK-26-0030-1, 0.78&times;0.49 ม.) ส่วนแผ่นที่เหลือค้างเป็นสต็อกว่างขายต่อได้ (BLK-26-0030-2, 0.80&times;0.50 ม.) ราคาต่อหน่วยของบรรทัด SO เปลี่ยนจากราคาตั้งต้นเป็นราคาจริงตามขนาดที่ตัดได้ทันที — ตัวอย่างจริง: ยอดรวม SO เปลี่ยนจาก 4,815.00 เป็น 1,840.29 (รวม VAT) ทันที เห็นการเปลี่ยนแปลงบันทึกไว้ใน chatter log ของ SO", prio="High",
         shot="assets/e2e-mode3/m3-09-complete-cut-done.png"),
  ]),
  dict(cat_id="E3", title="E3. จัดส่ง (Delivery — Scan Verification)",
       subtitle="ADR-009 — ต้องสแกน/กรอก Serial ให้ตรงก่อน Validate เสมอ ยังใช้ตรรกะเดิม ไม่เปลี่ยนตามกลไกตัดใหม่ · 2 test cases",
       cases=[
    dict(id="TC-E2E-M3-10", scenario="พยายาม Validate ใบส่งของโดยยังไม่กรอก Scanned Serial ให้ตรง",
         pre="ทำ TC-E2E-M3-09 เสร็จแล้ว มีใบส่งของสถานะ Ready รออยู่",
         steps=["เปิดใบส่งของ (Delivery) ที่เกิดขึ้นอัตโนมัติ", "กดปุ่ม Validate ทันทีโดยยังไม่กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial ของแผ่นที่ตัดจริง"],
         sample="-",
         expected="ระบบฟ้อง error สองภาษาทันที: \"สแกน Serial ไม่ตรง กรุณาสแกนให้ครบก่อน Validate: BLK-26-0030-1\" บันทึกไม่ผ่าน", prio="High",
         shot="assets/e2e-mode3/m3-11-delivery-scan-error.png"),
    dict(id="TC-E2E-M3-11", scenario="กรอก/สแกน Scanned Serial ให้ตรงแล้ว Validate",
         pre="ทำ TC-E2E-M3-10 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["เปิดบรรทัดในใบส่งของ กด \"Details\"", "กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial ของแผ่นที่ตัดจริง แล้วกด Save", "กดปุ่ม Validate อีกครั้ง"],
         sample="Scanned Serial = BLK-26-0030-1",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done สำเร็จ — แผ่นที่ขายหายจากสต็อกที่ขายได้ (Available) แล้ว — ตัวอย่างจริง: EG01/OUT/00085", prio="High",
         shot="assets/e2e-mode3/m3-12-scanned-correct.png"),
  ]),
  dict(cat_id="E4", title="E4. บัญชี (Accounting + Payment)",
       subtitle="ออกใบแจ้งหนี้ + รับชำระเงิน + ตรวจรายการบัญชี · 4 test cases",
       cases=[
    dict(id="TC-E2E-M3-12", scenario="สร้างและยืนยันใบแจ้งหนี้ลูกค้า (Customer Invoice)",
         pre="ทำ TC-E2E-M3-11 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; Create Draft", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO หลังคำนวณราคาใหม่แล้ว (ตัวอย่างจริง: INV/2026/00033, 1,840.29)", prio="High",
         shot="assets/e2e-mode3/m3-14-invoice-posted.png"),
    dict(id="TC-E2E-M3-13", scenario="รับชำระเงิน (Register Payment) บนใบแจ้งหนี้",
         pre="ทำ TC-E2E-M3-12 เสร็จแล้ว (Invoice = Posted)",
         steps=["เปิดใบแจ้งหนี้ &gt; กด \"Pay\"", "ตรวจ/ยืนยันยอดและวิธีชำระ &gt; กด Create Payment"],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นสถานะ \"In Payment\" — ตัวอย่างจริง: INV/2026/00033 จบที่สถานะ Posted + In Payment", prio="Medium",
         shot="assets/e2e-mode3/m3-15-invoice-paid.png"),
    dict(id="TC-E2E-M3-14", scenario="ตรวจรายการบัญชีบนใบแจ้งหนี้ (รายได้ + COGS + VAT + ลูกหนี้)",
         pre="ทำ TC-E2E-M3-12 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กด แท็บ \"Journal Items\""],
         sample="-",
         expected="เห็น 5 บรรทัดบนใบแจ้งหนี้ใบเดียว: เครดิต \"411130 Sales Revenue - Cut-to-Order (Mode 3)\" (บัญชีเฉพาะของ Mode 3 ไม่ใช่บัญชีทั่วไป), เครดิต \"113110 Inventory\" (ตัดออก), เดบิต \"511110 COGS - Stone Sales (all modes)\", เครดิต Output VAT, เดบิต Trade Receivables — ตัวอย่างจริง INV/2026/00033: รายได้ 1,719.90 / Inventory-COGS คู่ละ 150.00 / VAT 120.39 / ลูกหนี้ 1,840.29 (ยอดรวมสมดุล 1,990.29 = 1,990.29) พร้อม Analytic Distribution ครบ 3 มิติ (Material/Block/หมวดวัสดุ)", prio="High",
         shot="assets/e2e-mode3/m3-16-invoice-journal-items.png"),
    dict(id="TC-E2E-M3-15", scenario="ตรวจว่าไม่มี Journal Entry ซ้ำจากใบส่งของ (ไม่มี COGS ซ้ำ)",
         pre="ทำ TC-E2E-M3-11 เสร็จแล้ว (Delivery = Done)",
         steps=["เปิด Accounting &gt; Journal Entries", "ค้นหา entry ที่มี Reference ตรงกับเลขที่ใบส่งของ (เช่น EG01/OUT/00085)"],
         sample="-",
         expected="ไม่พบ Journal Entry แยกต่างหากสำหรับใบส่งของนี้เลย (มีเฉพาะ entry ของขั้นตอนตัด/ผลิตซึ่งเป็นคนละเรื่องกัน) — COGS มีบันทึกอยู่ที่เดียวคือในใบแจ้งหนี้ (INV/2026/00033) ไม่มีการนับซ้ำ ยืนยันแล้วว่ากลไกตัดแบบวางแผน/บันทึกจริง (16 ก.ย. 2026) ไม่กระทบพฤติกรรมนี้", prio="High",
         shot="assets/e2e-mode3/m3-16-invoice-journal-items.png"),
  ]),
]
