# Single source of truth for EMG-O E2E flow test cases — Mode 3
# (Cut-to-Order). Same spirit as qa_data_e2e_mode1.py/qa_data_e2e_mode2.py: a
# single continuous "does the whole business flow work" story from a
# non-technical UI user's point of view, not feature-level field/validation
# checks (those already live in qa_data.py's B2 category).
#
# Starts from "already have a Block in stock" (Ensure Supply — the
# rebalance/receiving flow — is out of scope here, same as Mode 1/2's files).
# Unlike Mode 1/2, Mode 3 sells a slab that does NOT exist yet at SO-confirm
# time — the Sale Order is confirmed on a placeholder price, then Production
# (Factory Worklist) decides which Block to cut and at what size, via a real
# Manufacturing Order (ADR-018). This file also covers the brand-new
# "Request Material" step (ADR-053, built same session as this file,
# 2026-09-06) — a Block must now be physically requested/moved to the
# Stone Production location via a dedicated Internal Transfer BEFORE Cut to
# Order will succeed; this was previously a manual/undocumented step.
#
# Data provenance: NOT pulled from an older static deck (the existing
# presentations/e2e-mode3-cut.html deck predates both the ADR-053 Request
# Material step and today's ADR-051/054/055 accounting fixes, so its numbers
# are stale). Two independent real runs back this file, same Block/dims/
# numbers both times:
#   (1) A first pass via `odoo shell` against `mbx-ee-dev` (SO S00095 ->
#       EG01/STCUT/00036 -> INV/2026/00010), committed as a reference
#       fixture — confirmed the business logic end to end.
#   (2) A second pass driven live through the actual Odoo web UI via
#       Playwright (real clicks, not ORM calls) — this is the fixture the
#       screenshots below are taken from, and the one all "ตัวอย่างจริง"
#       numbers in the cases below cite:
#   Block BLK-26-0013 (Rosso Levanto Test material, already in stock) -> SO
#   S00096 (Rosso Levanto Test - Slab, qty 1, confirmed at placeholder price
#   4,500 + 7% VAT = 4,815.00) -> Factory Worklist -> Cut to Order blocked
#   (0.000 m3 at Stone Production, need 0.019 m3) -> Request Material wizard
#   (target 1.2 x 0.8 x 0.02 m = 0.0192 m3) -> Internal Transfer
#   EG01/STPR/00010 (Lot BLK-26-0013-BLK) -> Cut to Order succeeds -> Cut
#   Order EG01/STCUT/00037 -> Complete Cut -> Slab BLK-26-0013 #3
#   (1.2 x 0.8 m, 4,320.00) -> SO price auto-recomputed live, amount_total
#   4,622.40 -> Delivery EG01/OUT/00053 (scan-gated, same as Mode 2) ->
#   Invoice INV/2026/00011 (Posted, 4,622.40 incl. VAT) -> Payment (In
#   Payment via the "Pay" button).
#
# Every step/button label/error-message string below is taken verbatim from
# the real run's actual output (stone_cut_order_wizard.py,
# stone_production_request_wizard.py, stock_picking.py, stone_factory_worklist
# views), not paraphrased from an old screenshot. Per-case screenshots (see
# `shot` field) are real, live-traced captures from run (2) above, cropped
# per the standard chatter-panel-removal convention — not mockups.
#
# CONFIRMED FINDING (positive, not a warning): the Mode 1/2 files' open
# question about double-booked COGS (TC-E2E-M1-12 / TC-E2E-M2-12) does NOT
# reproduce here — both runs executed AFTER today's ADR-054/055 fix, and a
# direct query for any Journal Entry referencing the Delivery
# (EG01/OUT/00053) besides the Invoice itself came back empty (both times).
# The Invoice's own embedded COGS pair (debit 400.00 / credit 400.00) is the
# only material-cost posting. See TC-E2E-M3-14.
#
# NOTE (cosmetic, not a bug): the COGS account the Invoice posts to is coded
# "511110 COGS - Block Direct Sale (Mode 1)" even though this transaction is
# a Mode 3 sale — the account is genuinely shared by any Block-derived
# material regardless of which sales mode consumed it (it's the *product's*
# own valuation/expense account, not a per-mode account); the account's own
# name is simply left over from when Mode 1 was the first mode built. Flagged
# here so a client reading the Chart of Accounts doesn't mistake this for a
# miscategorization.
#
# Column model per test case (extends qa_data_e2e_mode1.py/mode2.py with one
# new field, per feedback_qa_testcase_screenshot_export — every NEW case
# going forward needs a real per-case screenshot with a clickable link):
#   id, scenario, note (optional amber callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low),
#   shot (filename under assets/mode3/, real Playwright screenshot of this
#         exact step from the live run described above)

CATEGORIES = [
  dict(cat_id="F1", title="F1. ขาย (Sale — Mode 3, Cut-to-Order)",
       subtitle="ADR-018 — ยืนยันคำสั่งขายได้ทันทีแม้ยังไม่มีแผ่นหินจริง · 2 test cases",
       cases=[
    dict(id="TC-E2E-M3-01", scenario="เพิ่มบรรทัดสินค้า Material โหมด Cut-to-Order ใน Sale Order",
         pre="มี Block พร้อมอยู่แล้วในสต็อกของ Material นี้ (Pricing Mode = Serial) แต่ยังไม่มีแผ่นสำเร็จรูปขนาดที่ลูกค้าต้องการอยู่ในสต็อก",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material นั้น"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = \"Rosso Levanto Test - Slab\"",
         expected="เพิ่มบรรทัดสำเร็จ ราคาต่อหน่วยขึ้นเป็นราคาตั้งต้นของสินค้า (list price) เนื่องจากยังไม่มีแผ่นจริงผูกกับบรรทัดนี้เลย", prio="Medium",
         shot="assets/mode3/tc01-so-line.png"),
    dict(id="TC-E2E-M3-02", scenario="ยืนยัน (Confirm) Sale Order ได้ทันที โดยยังไม่ทราบขนาดที่จะตัด",
         pre="ทำ TC-E2E-M3-01 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น Sales Order ยอดรวมคำนวณจากราคาตั้งต้นของสินค้า (ตัวอย่างจริง: S00096, 4,500 + VAT 7% = 4,815.00 บาท) — ราคานี้ยังไม่ใช่ราคาจริง จะคำนวณใหม่อัตโนมัติหลังฝ่ายผลิตตัดแผ่นเสร็จ (ดู TC-E2E-M3-08) มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ", prio="High",
         shot="assets/mode3/tc02-so-confirmed.png"),
  ]),
  dict(cat_id="F2", title="F2. การผลิต (Production — Factory Worklist / Request Material / Cut Order)",
       subtitle="ADR-018 + ADR-053 — ย้าย Block ไปสถานีตัดก่อนเสมอ ก่อนสร้างใบสั่งผลิตได้ · 6 test cases",
       cases=[
    dict(id="TC-E2E-M3-03", scenario="เห็นคิวงานที่หน้า Factory Worklist",
         pre="ทำ TC-E2E-M3-02 เสร็จแล้ว",
         steps=["เปิดเมนู Factory Worklist"],
         sample="-",
         expected="เห็นแถวของ SO นี้ขึ้นคิวงาน ช่อง \"ต้องทำ\" ระบุ \"รอเลือก/ตัด Slab (Cut to Order)\" คอลัมน์ \"ความพร้อม Block\" ขึ้น badge สีส้ม \"ต้องย้าย Block ก่อน\"", prio="Medium",
         shot="assets/mode3/tc03-factory-worklist.png"),
    dict(id="TC-E2E-M3-04", scenario="พยายามกด \"Cut to Order\" ก่อนย้าย Block ไปสถานีตัด",
         note="หมายเหตุ: กันตัดจากก้อนที่ยังไม่ได้อยู่หน้างานจริง (ADR-053) — จำลองขั้นตอนหน้างานจริงที่ต้องยกก้อนหินไปวางที่แท่นตัดก่อนเริ่มงาน",
         pre="ทำ TC-E2E-M3-03 เสร็จแล้ว",
         steps=["กดปุ่ม \"Cut to Order\" บนแถวนั้น", "เลือกก้อนหินที่จะตัด กรอกขนาดที่จะตัด", "กด \"Create Cut Order\""],
         sample="Block = BLK-26-0013<br>ขนาดที่จะตัด = 1.2 &times; 0.8 ม.",
         expected="ระบบฟ้อง error สองภาษาทันที ระบุปริมาณที่ต้องการเทียบกับที่มีอยู่จริงที่สถานีตัด บันทึกไม่ผ่าน — ตัวอย่างจริง: \"Block BLK-26-0013 ยังไม่ได้ย้ายไปสถานีตัด (Stone Production) เพียงพอ — ต้องการ 0.019 m&sup3; แต่อยู่ที่สถานีตัดแล้วแค่ 0.000 m&sup3;\"", prio="High",
         shot="assets/mode3/tc04-cut-blocked.png"),
    dict(id="TC-E2E-M3-05", scenario="กด \"Request Material\" ขอย้าย Block ไปสถานีตัด",
         pre="ทำ TC-E2E-M3-04 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["กลับไปที่ Factory Worklist กดปุ่ม \"Request Material\" บนแถวเดิม", "กรอกขนาด/ความหนาเป้าหมายที่จะตัด", "กด \"Request Material\" ยืนยัน"],
         sample="Target L = 1.2 ม.<br>Target H = 0.8 ม.<br>Target Thickness = 0.02 ม.",
         expected="ระบบสร้างใบขอย้ายสินค้า (Internal Transfer) อัตโนมัติ 1 ใบ ปลายทาง \"Stone Production\" — ตัวอย่างจริง: EG01/STPR/00010 (Demand 0.02 m&sup3;)", prio="High",
         shot="assets/mode3/tc05-request-material.png"),
    dict(id="TC-E2E-M3-06", scenario="(ฝ่ายคลัง) ยืนยันใบขอย้าย — ระบุก้อนหินจริงที่จะใช้แล้ว Validate",
         note="เช่นเดียวกับ Barcode app จริง: ระบบยังไม่เลือกก้อนหินให้ล่วงหน้า ฝ่ายคลังเป็นผู้ระบุว่าจะใช้ก้อนไหนตอนย้ายจริง (ADR-053)",
         pre="ทำ TC-E2E-M3-05 เสร็จแล้ว มีใบขอย้ายสถานะรออยู่",
         steps=["เปิดใบขอย้ายที่เกิดขึ้น", "ระบุ/สแกนก้อนหิน (Lot) ที่จะใช้จริงพร้อมจำนวน", "กด Validate"],
         sample="Lot = BLK-26-0013-BLK",
         expected="ใบขอย้ายเปลี่ยนสถานะเป็น Done ก้อนหินย้ายไปอยู่ที่ Location \"Stone Production\" ครบตามจำนวนที่ขอ — ตัวอย่างจริง: EG01/STPR/00010 เลือก Lot ให้อัตโนมัติเพราะมีอยู่ตัวเดียวในสต็อกจุดนั้น", prio="High",
         shot="assets/mode3/tc06-transfer-done.png"),
    dict(id="TC-E2E-M3-07", scenario="กด \"Cut to Order\" อีกครั้ง — สร้างใบสั่งผลิตสำเร็จ",
         pre="ทำ TC-E2E-M3-06 เสร็จแล้ว",
         steps=["กลับไปที่ Factory Worklist กดปุ่ม \"Cut to Order\" อีกครั้ง", "เลือกก้อนหินเดิม กรอกขนาดเดิม", "กด \"Create Cut Order\""],
         sample="Block = BLK-26-0013<br>ขนาดที่จะตัด = 1.2 &times; 0.8 ม.",
         expected="สร้างใบสั่งผลิต (Manufacturing Order) สำเร็จ ไม่มี error แล้ว เพราะ Block ถูกย้ายมาสถานีตัดครบตามจำนวนแล้ว — ตัวอย่างจริง: EG01/STCUT/00037 ปุ่ม \"Complete Cut\" ปรากฏพร้อมกดขั้นถัดไป", prio="High",
         shot="assets/mode3/tc07-mo-created.png"),
    dict(id="TC-E2E-M3-08", scenario="ตัดแผ่นเสร็จ (Complete Cut) — ราคาคำนวณใหม่อัตโนมัติ",
         pre="ทำ TC-E2E-M3-07 เสร็จแล้ว",
         steps=["เปิดใบสั่งผลิต", "กดปุ่ม \"Complete Cut\""],
         sample="-",
         expected="ใบสั่งผลิตเสร็จสมบูรณ์ (สถานะ Done) เกิดแผ่นหินใหม่ 1 แผ่นตามขนาดที่ตัดจริง (Lot/Serial ใหม่) ผูกกับบรรทัด SO เดิมให้อัตโนมัติ ราคาต่อหน่วยของบรรทัด SO เปลี่ยนจากราคาตั้งต้นเป็นราคาจริงตามขนาดที่ตัดได้ — ตัวอย่างจริง: แผ่น BLK-26-0013 #3 (1.2&times;0.8 ม.) ราคา 4,320.00 บาท ยอดรวม SO เปลี่ยนจาก 4,815.00 เป็น 4,622.40 (รวม VAT) ทันที เห็นการเปลี่ยนแปลงบันทึกไว้ใน chatter log ของ SO", prio="High",
         shot="assets/mode3/tc08-mo-done.png"),
  ]),
  dict(cat_id="F3", title="F3. จัดส่ง (Delivery — Scan Verification)",
       subtitle="ADR-009 — ต้องสแกน/กรอก Serial ให้ตรงก่อน Validate เสมอ เหมือน Mode 2 · 2 test cases",
       cases=[
    dict(id="TC-E2E-M3-09", scenario="พยายาม Validate ใบส่งของโดยยังไม่กรอก Scanned Serial ให้ตรง",
         note="หมายเหตุ: กันส่งแผ่นผิดให้ลูกค้าโดยไม่ได้ตรวจสอบก่อน (ADR-009) — กลไกเดียวกับ Mode 2 (พบจากการรันจริง: ใบส่งของอาจค้างสถานะ \"Waiting\" อยู่ ต้องกด \"Check Availability\" ก่อน 1 ครั้งให้ขึ้น \"Ready\" แล้วค่อยกด Validate ต่อ)",
         pre="ทำ TC-E2E-M3-08 เสร็จแล้ว มีใบส่งของอัตโนมัติรออยู่",
         steps=["เปิดใบส่งของ (Delivery) ที่เกิดขึ้นอัตโนมัติ", "ถ้าสถานะยังเป็น \"Waiting\" ให้กด \"Check Availability\" ก่อน 1 ครั้ง", "กดปุ่ม Validate ทันทีโดยยังไม่กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial ของแผ่นที่ตัดจริง"],
         sample="-",
         expected="ระบบฟ้อง error สองภาษาทันที: \"สแกน Serial ไม่ตรง กรุณาสแกนให้ครบก่อน Validate: BLK-26-0013-3\" บันทึกไม่ผ่าน", prio="High",
         shot="assets/mode3/tc09-scan-blocked.png"),
    dict(id="TC-E2E-M3-10", scenario="กรอก/สแกน Scanned Serial ให้ตรงแล้ว Validate",
         pre="ทำ TC-E2E-M3-09 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["เปิดบรรทัดในใบส่งของ กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial ของแผ่นที่ตัดจริง", "กดปุ่ม Validate อีกครั้ง"],
         sample="Scanned Serial = BLK-26-0013-3",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done สำเร็จ — แผ่นที่ขายหายจากสต็อกที่ขายได้ (Available) แล้ว — ตัวอย่างจริง: EG01/OUT/00053", prio="High",
         shot="assets/mode3/tc10-delivery-done.png"),
  ]),
  dict(cat_id="F4", title="F4. บัญชี (Accounting + Payment)",
       subtitle="ออกใบแจ้งหนี้ + รับชำระเงิน + ตรวจรายการบัญชี · 4 test cases",
       cases=[
    dict(id="TC-E2E-M3-11", scenario="สร้างและยืนยันใบแจ้งหนี้ลูกค้า (Customer Invoice)",
         pre="ทำ TC-E2E-M3-10 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; กด \"Create Draft\"", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO หลังตัดแผ่นเสร็จ รวม VAT — ตัวอย่างจริง: INV/2026/00011 (4,622.40 บาท = 4,320.00 ก่อน VAT + VAT 7% 302.40) บัญชีรายได้ขึ้น \"411130 Sales Revenue - Cut-to-Order (Mode 3)\" ถูกต้องตามโหมด", prio="High",
         shot="assets/mode3/tc11-invoice-posted.png"),
    dict(id="TC-E2E-M3-12", scenario="รับชำระเงินบนใบแจ้งหนี้",
         note="ปุ่มจริงในหน้าจอชื่อ \"Pay\" (ไม่ใช่ \"Register Payment\" ตามชื่อ technical เดิม)",
         pre="ทำ TC-E2E-M3-11 เสร็จแล้ว (Invoice = Posted)",
         steps=["เปิดใบแจ้งหนี้ &gt; กด \"Pay\"", "ตรวจ/ยืนยันยอดและวิธีชำระ &gt; กด \"Create Payment\""],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นริบบิ้น \"IN PAYMENT\" มุมขวาบน (Payment Status: Not Paid &rarr; In Payment) — ตัวอย่างจริง: INV/2026/00011", prio="Medium",
         shot="assets/mode3/tc12-payment.png"),
    dict(id="TC-E2E-M3-13", scenario="ตรวจรายการบัญชีบนใบแจ้งหนี้ (รายได้ + VAT + ลูกหนี้ + COGS)",
         pre="ทำ TC-E2E-M3-11 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กด tab \"Journal Items\""],
         sample="-",
         expected="เห็นเครดิต Sales Revenue - Cut-to-Order (Mode 3) 4,320.00, เครดิต Output VAT 302.40, เดบิต Trade Receivables 4,622.40 (รวม) ตรงตามยอดใบแจ้งหนี้ พร้อมคู่ COGS/Inventory ที่ระบบแนบมาด้วยอัตโนมัติบนใบแจ้งหนี้ใบเดียวกัน (เดบิต COGS 400.00 / เครดิต Inventory 400.00)<br><br><b>หมายเหตุชื่อบัญชี:</b> บัญชี COGS ที่ขึ้นชื่อ \"COGS - Block Direct Sale (Mode 1)\" เป็นบัญชีเดียวกับที่ใช้ทุกโหมดที่ตัดสต็อกจาก Block (ไม่ได้จำกัดเฉพาะโหมด 1) ชื่อบัญชีเป็นเพียงชื่อที่ตั้งไว้ตอนสร้างบัญชีแรกสุด ไม่ใช่ตัวบ่งชี้ประเภทการขาย ไม่ใช่ error", prio="Medium",
         shot="assets/mode3/tc13-journal-items.png"),
    dict(id="TC-E2E-M3-14", scenario="ตรวจว่าต้นทุนขาย (COGS) ไม่ถูกบันทึกซ้ำ",
         note="✅ ยืนยันแล้วจากการรันจริง 2 รอบอิสระ: ปัญหา COGS บันทึกซ้ำที่เคยพบใน Mode 1/2 (TC-E2E-M1-12 / TC-E2E-M2-12) ไม่เกิดกับการรันนี้ — เพราะรันหลัง ADR-054/055 แก้ไขแล้วในวันเดียวกัน (2026-09-06) ก่อนหน้านี้ Mode 1/2 พบคู่ COGS/Inventory ขึ้นซ้ำสองชุด (ใบแจ้งหนี้ฝังเองชุดหนึ่ง + Journal Entry แยกจากใบส่งของอีกชุด) จากบั๊ก native ของ Odoo ที่แก้ไปแล้ว",
         pre="ทำ TC-E2E-M3-10 เสร็จแล้ว (Delivery = Done) และ TC-E2E-M3-11 เสร็จแล้ว (Invoice = Posted)",
         steps=["เปิด Accounting &gt; Journal Entries", "ค้นหา entry ที่มี Reference ตรงกับเลขที่ใบส่งของ (EG01/OUT/00053)", "เทียบกับคู่ COGS/Inventory ที่เห็นใน TC-E2E-M3-13"],
         sample="-",
         expected="ไม่พบ Journal Entry แยกต่างหากที่อ้างอิงใบส่งของเลย (ผลค้นหา 0 รายการ) — คู่ COGS/Inventory ที่เห็นใน TC-E2E-M3-13 (ฝังอยู่ในใบแจ้งหนี้) เป็นชุดเดียวที่มีอยู่จริง ไม่ซ้ำ", prio="Medium",
         shot="assets/mode3/tc14-no-duplicate-je.png"),
  ]),
]

if __name__ == '__main__':
    total = sum(len(c['cases']) for c in CATEGORIES)
    prios = {'High': 0, 'Medium': 0, 'Low': 0}
    for c in CATEGORIES:
        for tc in c['cases']:
            prios[tc['prio']] += 1
    print('Total test cases:', total)
    print('Priority breakdown:', prios)
    print('Categories:', len(CATEGORIES))
