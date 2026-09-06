# Single source of truth for EMG-O E2E flow test cases — Mode 2 (Ready-Made
# Slab sale, both pricing sub-modes: Serial per-slab AND Lot aggregate). Same
# spirit as qa_data_e2e_mode1.py: a single continuous "does the whole business
# flow work" story from a non-technical UI user's point of view, not
# feature-level field/validation checks (those already live in qa_data.py's
# B2 category).
#
# Starts from "already have Slabs/Lot in stock" (Ensure Supply — the
# rebalance/receiving flow — is out of scope here, same as Mode 1's file).
#
# Data provenance for every "sample data"/"expected result" below is NOT a
# fresh live run done for this file — it is pulled from the two Mode 2 E2E
# decks that were already built from real, live-traced runs on mbx-ee-dev and
# reviewed/confirmed in the portal:
#   - Serial (per-slab) path: presentations/e2e-mode2-slab.html, confirmed
#     21 ส.ค. 2026. Real numbers: Slabs BDL-00014-1 / BDL-00014-2 (2 slabs,
#     8.32 Sq.Mt. total) -> SO S108405 (avg 4,200/Sq.Mt., 34,944 pre-VAT) ->
#     Invoice INV/2026/00017 (37,390.08 incl. 7% VAT).
#   - Lot (aggregate) path: presentations/e2e-mode2-lot-stock.html, live-run
#     4 ส.ค. 2026, reviewed 21 ส.ค. 2026. Real numbers: Lot BP-B-0001
#     (Bianco Perla Marble Slab, 6.00 Sq.Mt. total, 4.00 remaining at time of
#     sale) -> sold 1.50 Sq.Mt. @ 1,200/Sq.Mt. -> SO S108370 -> Invoice
#     INV/2026/00016 (1,926.00 incl. VAT), Posted + Paid.
# Every step/button label/error-message string below was re-checked against
# the current source on 2026-09-06 (sale_order_line.py, stock_move_line.py,
# stock_picking.py, stone_lot_stock_select_wizard.py) to confirm it still
# matches the live code, not just the old screenshots.
#
# CORRECTIONS / findings vs. a naive reading of the two decks:
#   - The "scan Serial before delivery" gate (stock_picking.py
#     button_validate(), scanned_lot_id field on stock.move.line) applies to
#     BOTH the Serial and the Lot sub-path identically — it matches on
#     is_stone_material (keyed off stone.bundle's product_tmpl_id), not on
#     pricing mode. The Lot deck's own slide 7 ("lot2-06-scan-error.png")
#     confirms this is real, not an assumption — kept as its own shared
#     Delivery category instead of duplicating it per sub-mode.
#   - Added a payment test case (TC-E2E-M2-11) that Mode 1's file never
#     covered — the Lot deck's real run went all the way to Invoice
#     "Posted, Paid", so this flow has a real reference point Mode 1 doesn't.
#   - The Mode 1 file's known issue (TC-E2E-M1-12 — COGS booked twice: once
#     on the Customer Invoice itself via native display_type='cogs', once
#     again as a separate Journal Entry off the Delivery) is a native Odoo
#     inventory-valuation behavior, not something stone_slab_inventory adds
#     per sales mode — so it is EXPECTED to reproduce here too. Documented as
#     TC-E2E-M2-12 but marked as "not independently re-verified with a fresh
#     live run for Mode 2" — do not treat as confirmed-closed or
#     confirmed-reproducing until someone actually opens the Journal Entries
#     for S108405/INV-00017 and checks.
#
# Column model per test case (same as qa_data_e2e_mode1.py):
#   id, scenario, note (optional amber callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low)

CATEGORIES = [
  dict(cat_id="E1", title="E1. ขาย (Sale — Mode 2, Serial per-slab)",
       subtitle="ADR-002/006/009 — เลือกทีละแผ่นตามเลข Serial · 3 test cases",
       cases=[
    dict(id="TC-E2E-M2-01", scenario="เพิ่มบรรทัดสินค้า Material โหมด Serial ใน Sale Order",
         pre="มีแผ่นหินสถานะ Available อยู่แล้วอย่างน้อย 2 แผ่น จาก Material เดียวกันที่ตั้ง Pricing Mode = Serial (per-slab)",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material นั้น"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = Material โหมด Serial ที่มีแผ่นพร้อมขาย",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Select Slabs\" ปรากฏบนบรรทัดนั้น (ไม่ใช่ \"Select Lot Stock\")", prio="Medium"),
    dict(id="TC-E2E-M2-02", scenario="กด \"Select Slabs\" เลือกหลายแผ่นพร้อมกันตามเลข Serial",
         pre="ทำ TC-E2E-M2-01 เสร็จแล้ว",
         steps=["กดปุ่ม \"Select Slabs\" บนบรรทัด", "หน้าต่างเลือกแผ่นแสดงรายการแผ่น Available พร้อมเลข Serial ขนาด และสถานะ", "ติ๊กเลือกหลายแผ่นพร้อมกันในคลิกเดียว", "กด \"Confirm Selection\""],
         sample="เลือก 2 แผ่น = BDL-00014-1, BDL-00014-2",
         expected="บรรทัด SO ผูกทั้ง 2 แผ่น จำนวนรวมเป็น Sq.Mt. ของทั้ง 2 แผ่นรวมกันอัตโนมัติ (ตัวอย่างจริง: รวม 8.32 ตร.ม.)", prio="High"),
    dict(id="TC-E2E-M2-03", scenario="ยืนยัน (Confirm) Sale Order — ราคาเฉลี่ยคำนวณจากขนาดจริงแต่ละแผ่น",
         pre="ทำ TC-E2E-M2-02 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น Sales Order ราคาต่อหน่วยเป็นค่าเฉลี่ยถ่วงน้ำหนักจากขนาดจริงของทุกแผ่น (ไม่ใช่ราคาคงที่ต่อแผ่น) — ตัวอย่างจริง: S108405, 8.32 ตร.ม. &times; 4,200/ตร.ม. เฉลี่ย = 34,944 (ก่อน VAT) มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ", prio="High"),
  ]),
  dict(cat_id="E2", title="E2. ขาย (Sale — Mode 2, Lot aggregate)",
       subtitle="ADR-020 — ระบุจำนวนตร.ม.บางส่วนจากล็อต ไม่ต้องขายทั้งล็อต · 3 test cases",
       cases=[
    dict(id="TC-E2E-M2-04", scenario="เพิ่มบรรทัดสินค้า Material โหมด Lot ใน Sale Order",
         pre="มีล็อตหินสถานะ Available อยู่แล้ว จาก Material ที่ตั้ง Pricing Mode = Lot (aggregate, cheap stone)",
         steps=["เปิด Sales &gt; Orders &gt; New (หรือใช้ SO เดิม)", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material โหมด Lot นี้"],
         sample="สินค้า = Bianco Perla Marble Slab (Material โหมด Lot)",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Select Lot Stock\" ปรากฏบนบรรทัดนั้นแทนที่จะเป็น \"Select Slabs\"", prio="Medium"),
    dict(id="TC-E2E-M2-05", scenario="กด \"Select Lot Stock\" ระบุจำนวนตร.ม.บางส่วนจากล็อต",
         pre="ทำ TC-E2E-M2-04 เสร็จแล้ว",
         steps=["กดปุ่ม \"Select Lot Stock\" บนบรรทัด", "เลือกล็อตที่ต้องการ — ระบบแสดงจำนวนตร.ม.ที่เหลืออยู่ในล็อตนั้นให้ทันที", "กรอก \"Quantity to Sell (Sq.Mt.)\" เป็นจำนวนบางส่วน (ไม่จำเป็นต้องขายทั้งล็อต)", "กด \"Confirm Selection\""],
         sample="ล็อต = BP-B-0001 (เหลือ 4.00 ตร.ม. จากทั้งล็อต 6.00 ตร.ม.)<br>Quantity to Sell (Sq.Mt.) = 1.50",
         expected="บรรทัด SO ผูก Lot ถูกต้อง จำนวน/ราคารวมปรับตาม 1.50 ตร.ม. ที่เลือกทันที ไม่มีการเลือกแผ่นเดี่ยวใดๆ", prio="High"),
    dict(id="TC-E2E-M2-06", scenario="ยืนยัน (Confirm) Sale Order โหมด Lot",
         pre="ทำ TC-E2E-M2-05 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ — ตัวอย่างจริง: S108370, 1.50 ตร.ม. &times; 1,200/ตร.ม. = 1,800 (ก่อน VAT) ส่วนที่เหลือของล็อตเดิม (2.50 ตร.ม.) ยังคงพร้อมขายต่อได้ตามปกติ", prio="High"),
  ]),
  dict(cat_id="E3", title="E3. จัดส่ง (Delivery — Scan Verification)",
       subtitle="ADR-009 — ต้องสแกน/กรอก Serial ให้ตรงก่อน Validate เสมอ ใช้ร่วมกันทั้ง Serial และ Lot · 2 test cases",
       cases=[
    dict(id="TC-E2E-M2-07", scenario="พยายาม Validate ใบส่งของโดยยังไม่กรอก Scanned Serial ให้ตรง",
         note="หมายเหตุ: กันส่งแผ่น/ล็อตผิดให้ลูกค้าโดยไม่ได้ตรวจสอบก่อน (ADR-009) — ใช้ตรรกะเดียวกันไม่ว่าเป็นบรรทัด Serial หรือ Lot",
         pre="ทำ TC-E2E-M2-03 หรือ TC-E2E-M2-06 เสร็จแล้ว มีใบส่งของสถานะ Ready รออยู่",
         steps=["เปิดใบส่งของ (Delivery) ที่เกิดขึ้นอัตโนมัติ", "กดปุ่ม Validate ทันทีโดยยังไม่กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial ที่จองไว้"],
         sample="-",
         expected="ระบบฟ้อง error สองภาษาทันที: \"สแกน Serial ไม่ตรง กรุณาสแกนให้ครบก่อน Validate\" พร้อมระบุชื่อ Serial ที่ยังไม่ตรง บันทึกไม่ผ่าน", prio="High"),
    dict(id="TC-E2E-M2-08", scenario="กรอก/สแกน Scanned Serial ให้ตรงครบทุกบรรทัดแล้ว Validate",
         pre="ทำ TC-E2E-M2-07 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["เปิดแต่ละบรรทัดในใบส่งของ กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial/Lot ที่จองไว้จริงให้ครบทุกบรรทัด", "กดปุ่ม Validate อีกครั้ง"],
         sample="Scanned Serial ของแต่ละบรรทัด = Serial/Lot เดียวกับที่ระบบจองไว้ (เช่น BDL-00014-1, BDL-00014-2 หรือ BP-B-0001)",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done สำเร็จ — แผ่น/ปริมาณที่ขายหายจากสต็อกที่ขายได้ (Available) แล้ว", prio="High"),
  ]),
  dict(cat_id="E4", title="E4. บัญชี (Accounting + Payment)",
       subtitle="ออกใบแจ้งหนี้ + รับชำระเงิน + ตรวจรายการบัญชี · 4 test cases",
       cases=[
    dict(id="TC-E2E-M2-09", scenario="สร้างและยืนยันใบแจ้งหนี้ลูกค้า (Customer Invoice)",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; Create Draft Invoice", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO รวม VAT — ตัวอย่างจริง Serial: INV/2026/00017 (37,390.08); ตัวอย่างจริง Lot: INV/2026/00016 (1,926.00)", prio="High"),
    dict(id="TC-E2E-M2-10", scenario="รับชำระเงิน (Register Payment) บนใบแจ้งหนี้",
         note="หมายเหตุ: จุดนี้เป็นส่วนต่างจากเอกสาร Golden Path ของ Mode 1 ซึ่งไม่ได้เดินไปถึงขั้นตอนรับชำระเงิน — ที่นี่มีข้อมูลจริงยืนยันแล้วว่าไหลไปจนจบ",
         pre="ทำ TC-E2E-M2-09 เสร็จแล้ว (Invoice = Posted)",
         steps=["เปิดใบแจ้งหนี้ &gt; กด \"Register Payment\"", "ตรวจ/ยืนยันยอดและวิธีชำระ &gt; กด Create Payment"],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นสถานะ \"Paid\" (Payment Status) — ตัวอย่างจริง: INV/2026/00016 จบที่สถานะ Posted + Paid", prio="Medium"),
    dict(id="TC-E2E-M2-11", scenario="ตรวจรายการบัญชีบนใบแจ้งหนี้ (รายได้ + VAT + ลูกหนี้)",
         pre="ทำ TC-E2E-M2-09 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="เห็นเครดิต Sales Revenue, เครดิต Output VAT, เดบิต Trade Receivables (รวม) ตรงตามยอดใบแจ้งหนี้ พร้อมคู่ COGS/Inventory ที่ระบบแนบมาด้วยอัตโนมัติบนใบแจ้งหนี้ใบเดียวกัน (เดบิต COGS / เครดิต Inventory)", prio="Medium"),
    dict(id="TC-E2E-M2-12", scenario="ตรวจว่าต้นทุนขาย (COGS) ถูกบันทึกซ้ำหรือไม่ — คาดว่าจะเกิดเหมือน Mode 1 แต่ยังไม่ได้ verify ซ้ำสำหรับ Mode 2",
         note="⚠️ ยังไม่ได้ทดสอบจริงสำหรับเคสนี้โดยเฉพาะ — เป็นการคาดการณ์จากสาเหตุเดียวกันกับ TC-E2E-M1-12 (Odoo native display_type='cogs' บนใบแจ้งหนี้ + Journal Entry แยกจากใบส่งของ) เพราะเป็นกลไก stock valuation มาตรฐานของ Odoo ไม่ใช่โค้ดเฉพาะของโหมดการขาย ไม่ควรถือว่ายืนยันแล้วจนกว่าจะเปิด Journal Entries ของ S108405/INV-00017 จริงมาเทียบ",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว (Delivery = Done)",
         steps=["เปิด Accounting &gt; Journal Entries", "ค้นหา entry ที่มี Reference ตรงกับเลขที่ใบส่งของ", "เปิดดูรายละเอียดบรรทัด เทียบกับคู่ COGS/Inventory ที่เห็นใน TC-E2E-M2-11"],
         sample="-",
         expected="(ยังไม่ verify) หากพฤติกรรมเหมือน Mode 1 จะเห็นคู่ COGS/Inventory ซ้ำอีกชุดในบัญชีคนละตัว — ถ้าพบจริง ให้ถือเป็น known issue เดียวกับ TC-E2E-M1-12 ไม่ใช่บั๊กใหม่ ต้องแจ้งทีม dev รวมกัน", prio="Medium"),
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
