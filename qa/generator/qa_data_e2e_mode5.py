# Single source of truth for EMG-O E2E flow test cases — Mode 5
# (Stone Production / FG Production, ADR-029). Same spirit as
# qa_data_e2e_mode1/2/3/4.py: a single continuous "does the whole business
# flow work" story from a non-technical UI user's point of view, not
# feature-level field/validation checks.
#
# Starts from "already have a Slab in stock" (Purchase/Cut-to-Order that
# produces the raw Slab is out of scope here, same as Mode 1/2/3's files —
# see qa_data_e2e_mode3.py for that flow in detail).
#
# Mode 5 sells a Finished Good (FG, e.g. a countertop) that is cut/produced
# from an existing Slab via a second production step (ADR-029). Unlike
# Mode 1-3, an FG line genuinely branches two different ways depending on
# whether the FG itself already has enough free stock:
#   - G2a: FG already has enough stock -> no production needed at all,
#     delivers straight from existing stock.
#   - G2b: FG does not have enough stock -> Slab must be moved to the
#     Stone Production location, then "Produce FG" cuts/produces it.
#
# ✅ REAL BUG found + FIXED same session (2026-09-07), building this file:
# the system never checked the FG's own stock before flagging "needs
# production" — `sale_order_line._compute_stone_factory_action` only ever
# checked whether a Manufacturing Order had been completed for that exact
# SO line, so the Factory Worklist and the "Produce FG" button kept
# demanding production even when the FG already had stock sitting idle
# from a previous order. Fixed by adding `stone_fg_stock_sufficient`
# (checks `product.free_qty`, not `qty_available` — see below) and gating
# both the Worklist badge and the "Produce FG" button on it.
# Found DURING the live build (not before): the first fix used
# `qty_available` (bare on-hand qty) — this incorrectly reported "5 units
# on hand, sufficient" while ALL 5 were already reserved by an older,
# never-validated delivery (S00034/EG01/OUT/00009) left over from an
# earlier session, leaving 0 actually free to promise. Corrected to
# `product.free_qty` (on hand minus already-reserved) before this file's
# real fixture was built. Commits: `stone_slab_inventory` `202580f`
# (feature) + follow-up same-session fix (free_qty correction), pushed to
# `test/emg-erp-ee`. Deployed to `mbx-ee-dev` only so far.
#
# Data provenance: fresh live run built specifically for this file, driven
# through the real Odoo web UI via Playwright on `mbx-ee-dev`, 2026-09-07.
# Two real SOs cover the two branches (both use "Carrara White -
# Countertop", the only FG product with real Slab stock behind it — same
# scoping precedent as ADR-045/046):
#   G2b (production needed): SO S00112 (customer "ทดสอบ E2E - Test
#   Customer", qty 3, confirmed at 48,150.00 incl. VAT — Produce FG button
#   visible since free stock was 1 at the time) -> Internal Transfer
#   EG01/INT/00053 (Slab BDL-00002 #8: Stone Available -> Stone
#   Production) -> Produce FG wizard (auto-matched BDL-00002 #8) ->
#   produced qty overridden to 6 (more than this order's 3, deliberately
#   leaving surplus for the G2a fixture below) -> MO EG01/STFG/00012 ->
#   Complete FG Production (Slab fully consumed, FG lot
#   FG-EG01/STFG/00012 created) -> Delivery EG01/OUT/00066 (fully
#   available, Done) -> Invoice INV/2026/00018 (48,150.00, Posted).
#   G2a (no production needed): SO S00113 (same customer, qty 2 — fits
#   within the surplus G2b's overproduction just left behind) -> Produce
#   FG button correctly ABSENT, line never appears on the Factory Worklist
#   -> Delivery EG01/OUT/00067 delivers straight from stock (Done, no
#   production step at all) -> Invoice INV/2026/00019 (32,100.00, Posted).
#
# 🔴 OPEN FINDING, NOT FIXED (flagged to user, not silently treated as
# passing — same discipline as Mode 4's TC-03/09 callouts): the FG's
# Delivery posts NO accounting entry of its own at all (`stock.move
# .account_move_id` is empty on EG01/OUT/00066's move). Production DOES
# correctly transfer the consumed Slab's value into the FG's own inventory
# account (Journal Entry STJ/2026/09/0011: debit 113150 "Inventory - Stone
# FG" / credit 113110 "Inventory - Stone Blocks (Raw)", ฿2,800.00 exactly —
# matching the Slab's real FIFO value, no labor padding, per the
# session-101 addendum to ADR-029). But nothing ever credits that ฿2,800
# back out of 113150 when the FG is actually delivered to the customer —
# the invoice itself only carries Revenue/Tax/Receivable lines (see
# TC-E2E-M5-12), so the Inventory - Stone FG account keeps the Slab's value
# on the books forever even after the goods leave the building, and no
# COGS ever posts for an FG sale. Root cause not chased down this session
# (the category is real_time/FIFO like every other stone category, so this
# isn't a valuation-method misconfiguration) — this is a genuinely open gap
# for the user to decide how to prioritize, not something this file's build
# should quietly work around.
#
# Column model per test case (same as mode3/mode4, per
# feedback_qa_testcase_screenshot_export):
#   id, scenario, note (optional amber/green/red callout), pre, steps
#   (list), sample (str, '-' if nothing to key in), expected, prio
#   (High/Medium/Low), shot (filename under assets/mode5/, real Playwright
#   screenshot, chatter panel cropped out per standing convention)

CATEGORIES = [
  dict(cat_id="G1", title="G1. ขาย (Sale — Mode 5, FG Production)",
       subtitle="ADR-029 — เพิ่มบรรทัดสินค้าสำเร็จรูป (FG) แล้วยืนยันคำสั่งขาย · 2 test cases",
       cases=[
    dict(id="TC-E2E-M5-01", scenario="เพิ่มบรรทัดสินค้าสำเร็จรูป (FG) ในใบสั่งขาย",
         pre="มี Slab (วัตถุดิบตั้งต้นของ FG นี้) อยู่ในสต็อกที่ไหนสักแห่งแล้ว (ไม่จำเป็นต้องว่าง — ระบบจะเช็คให้เองตอน Confirm)",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าสำเร็จรูป (FG)", "กรอกจำนวนที่ต้องการขาย"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = \"Carrara White - Countertop\"<br>จำนวน = 3",
         expected="เพิ่มบรรทัดสำเร็จ ราคาต่อหน่วยขึ้นตามราคาตั้งต้นของสินค้า — ตัวอย่างจริง: 15,000.00 บาท/หน่วย &times; 3 = 45,000.00 + VAT 7% = 48,150.00 บาท", prio="High",
         shot="assets/mode5/tc01-add-fg-line.png"),
    dict(id="TC-E2E-M5-02", scenario="ยืนยัน (Confirm) Sale Order",
         pre="ทำ TC-E2E-M5-01 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น Sales Order เกิด Delivery Order อัตโนมัติ 1 ใบ — ถ้า FG ที่ขายมีสต็อกว่างพอ บรรทัดจะไม่มีปุ่ม \"Produce FG\" เลย (ไปต่อที่ G2a) แต่ถ้าไม่พอ ปุ่ม \"Cut to Order\"/\"Produce FG\" จะปรากฏให้กดต่อ (ไปต่อที่ G2b) — ตัวอย่างจริง (กรณีสต็อกไม่พอ): S00112 ยอดรวม 48,150.00 บาท, ปุ่ม Produce FG ปรากฏที่บรรทัด", prio="High",
         shot="assets/mode5/tc02-so-confirmed-insufficient.png"),
  ]),
  dict(cat_id="G2a", title="G2a. ผลิต — กรณี FG มีสต็อกพอแล้ว (ไม่ต้องผลิตซ้ำ)",
       subtitle="ระบบเช็คสต็อกว่างของ FG เองก่อนเสมอ — เพิ่งแก้ไขให้ถูกต้อง 2026-09-07 · 1 test case",
       cases=[
    dict(id="TC-E2E-M5-03", scenario="ระบบข้ามขั้นตอนผลิต เมื่อ FG มีสต็อกว่างพออยู่แล้ว",
         note="✅ เพิ่งแก้ไข 2026-09-07: ก่อนหน้านี้ระบบไม่เคยเช็คสต็อกของ FG เอง จะขึ้นเตือนให้ผลิตซ้ำทุกครั้งแม้มี FG เหลือพอขายอยู่แล้ว — ตอนนี้เช็คให้อัตโนมัติแล้วจากสต็อก \"ว่างจริง\" ที่ไม่ถูกจองไปกับออเดอร์อื่น",
         pre="สินค้า FG ตัวนี้มีสต็อกว่าง (ไม่ถูกจองไปกับออเดอร์อื่น) พอกับจำนวนที่จะขาย",
         steps=["เพิ่มบรรทัดสินค้า FG ในใบสั่งขายเหมือน TC-E2E-M5-01", "กด Confirm เหมือน TC-E2E-M5-02"],
         sample="สินค้า = \"Carrara White - Countertop\" จำนวน = 2 (ตอนนั้นมีสต็อกว่างเหลือ 4 หน่วยจากการผลิตเผื่อไว้ใน G2b)",
         expected="บรรทัดไม่มีปุ่ม \"Produce FG\" ปรากฏเลย (ต่างจาก TC-E2E-M5-02) และไม่ขึ้นแถวในหน้า Factory Worklist เลย — ไปต่อที่การจัดส่งได้ทันทีโดยไม่ต้องผลิตอะไรเพิ่ม — ตัวอย่างจริง: S00113 ยอดรวม 32,100.00 บาท", prio="High",
         shot="assets/mode5/tc03-g2a-no-produce-button.png"),
  ]),
  dict(cat_id="G2b", title="G2b. ผลิต — กรณี FG ไม่มี/ไม่พอในสต็อก (ต้องผลิตจริง)",
       subtitle="ย้าย Slab เข้าสถานีผลิต แล้วเปิด wizard \"Produce FG\" ตัด/ผลิตจริง · 5 test cases",
       cases=[
    dict(id="TC-E2E-M5-04", scenario="เห็นคิวงานที่หน้า Factory Worklist",
         pre="ทำ TC-E2E-M5-02 เสร็จแล้ว (กรณีสต็อกไม่พอ)",
         steps=["เปิดเมนู Stone Slab &gt; Tools &gt; Factory Worklist"],
         sample="-",
         expected="เห็นแถวของ SO นี้ขึ้นคิวงาน คอลัมน์ \"ต้องทำ\" ระบุ \"รอผลิต FG (Cut to Order / Produce FG)\" — ตัวอย่างจริง: S00112, สินค้า Carrara White - Countertop, จำนวน 3.00", prio="Medium",
         shot="assets/mode5/tc04-factory-worklist.png"),
    dict(id="TC-E2E-M5-05", scenario="ย้าย Slab (วัตถุดิบของ FG) เข้าสถานีผลิต",
         pre="มี Slab ของ Material เดียวกับ FG นี้ อยู่ที่ Location \"Stone Available\"",
         steps=["เปิด Inventory &gt; Internal Transfers &gt; New", "ตั้งต้นทาง (Source Location) = Stone Available", "ตั้งปลายทาง (Destination Location) = Stone Production", "เพิ่มสินค้า Slab ของ Material นั้น จำนวน 1", "กด Validate"],
         sample="สินค้า = \"Carrara White - Slab\" จำนวน = 1",
         expected="ใบโอนย้ายเปลี่ยนสถานะเป็น Done Slab ถูกย้ายเข้า Stone Production เรียบร้อย พร้อมให้ผลิตต่อ — ตัวอย่างจริง: EG01/INT/00053 (Slab BDL-00002 #8)", prio="High",
         shot="assets/mode5/tc05-slab-moved-to-production.png"),
    dict(id="TC-E2E-M5-06", scenario="เปิด wizard \"Produce FG\" — ระบบจับคู่ Slab ให้อัตโนมัติ",
         pre="ทำ TC-E2E-M5-05 เสร็จแล้ว",
         steps=["กลับไปที่บรรทัดสินค้า FG ใน Sale Order", "กดปุ่ม \"Produce FG\""],
         sample="-",
         expected="หน้าต่าง Produce FG เปิดขึ้น ช่อง \"Slab to Consume\" ถูกเติมชื่อ Slab ที่เพิ่งย้ายเข้าสถานีผลิตให้อัตโนมัติ (ไม่ต้องเลือกเอง) พร้อมบรรทัดผลผลิต 1 บรรทัดตรงกับสินค้าที่ขายอยู่แล้ว — ตัวอย่างจริง: Slab to Consume = BDL-00002 #8", prio="High",
         shot="assets/mode5/tc06-produce-fg-wizard.png"),
    dict(id="TC-E2E-M5-07", scenario="กรอกจำนวนผลผลิตจริงจาก Slab นี้ แล้วกดผลิต",
         note="1 Slab ตัดออกมาได้กี่ชิ้นไม่ตายตัว — ฝ่ายผลิตกรอกจำนวนจริงที่ตัดได้ตอนนี้เอง ไม่ต้องเท่ากับจำนวนที่ลูกค้าสั่งพอดี (ตัดเผื่อสต็อกไว้ขายออเดอร์ถัดไปได้)",
         pre="ทำ TC-E2E-M5-06 เสร็จแล้ว",
         steps=["แก้จำนวนในบรรทัดผลผลิตเป็นจำนวนที่ตัด/ผลิตได้จริงจาก Slab นี้", "กดปุ่ม \"Produce\""],
         sample="จำนวนผลผลิต = 6 (ลูกค้าสั่งแค่ 3 — ตัดเผื่อสต็อกไว้ขายรอบหน้าด้วย)",
         expected="เกิดใบสั่งผลิต (Manufacturing Order) ใหม่ ผูก Slab ที่เลือกเป็นวัตถุดิบ จำนวนที่ต้องผลิตตรงกับที่กรอก — ตัวอย่างจริง: EG01/STFG/00012 (To Produce 6.00)", prio="High",
         shot="assets/mode5/tc07-output-qty.png"),
    dict(id="TC-E2E-M5-08", scenario="กด \"Complete FG Production\" — ปิดงานผลิต",
         pre="ทำ TC-E2E-M5-07 เสร็จแล้ว",
         steps=["เปิดใบสั่งผลิตที่เพิ่งสร้าง", "กดปุ่ม \"Complete FG Production\""],
         sample="-",
         expected="ใบสั่งผลิตเปลี่ยนสถานะเป็น Done Slab ที่ใช้ถูกตัดออกจากสต็อกจนหมด (ใช้ครั้งเดียว ไม่เหลือให้ใช้ซ้ำ) FG เข้าสต็อกจริงตามจำนวนที่ผลิต พร้อม Lot ใหม่ — ตัวอย่างจริง: EG01/STFG/00012 ผลิตสำเร็จ 6.00/6.00 ได้ Lot \"FG-EG01/STFG/00012\"", prio="High",
         shot="assets/mode5/tc08-fg-production-complete.png"),
  ]),
  dict(cat_id="G3", title="G3. จัดส่ง (Delivery)",
       subtitle="ทั้ง 2 กรณี (ผลิตใหม่ / มีสต็อกอยู่แล้ว) ส่งมอบแบบเดียวกัน ไม่มีการดักสแกน Serial · 2 test cases",
       cases=[
    dict(id="TC-E2E-M5-09", scenario="ส่งมอบสินค้าที่เพิ่งผลิตเสร็จ (กรณี G2b)",
         pre="ทำ TC-E2E-M5-08 เสร็จแล้ว มีใบส่งของอัตโนมัติรออยู่ตั้งแต่ตอน Confirm",
         steps=["เปิด Inventory &gt; Deliveries", "เปิดใบส่งของของ SO นี้", "กด Validate"],
         sample="-",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done — ไม่มีการดักสแกน Serial เหมือนสินค้า Block/Slab (ส่งได้ทันทีเมื่อสต็อกพร้อม) — ตัวอย่างจริง: EG01/OUT/00066 (Carrara White - Countertop 3.00/3.00 พร้อมส่ง)", prio="High",
         shot="assets/mode5/tc09-delivery-produced-done.png"),
    dict(id="TC-E2E-M5-10", scenario="ส่งมอบสินค้าที่ไม่ต้องผลิต (กรณี G2a)",
         pre="ทำ TC-E2E-M5-03 เสร็จแล้ว",
         steps=["เปิด Inventory &gt; Deliveries", "เปิดใบส่งของของ SO นี้", "กด Validate"],
         sample="-",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done ทันที ดึงสต็อกจาก FG ที่มีอยู่แล้วโดยไม่ผ่านขั้นตอนผลิตเลยสักครั้ง — ตัวอย่างจริง: EG01/OUT/00067 (Carrara White - Countertop 2.00/2.00)", prio="Medium",
         shot="assets/mode5/tc10-delivery-sufficient-done.png"),
  ]),
  dict(cat_id="G4", title="G4. บัญชี (Accounting)",
       subtitle="ออกใบแจ้งหนี้ &amp; ตรวจรายการบัญชี · 2 test cases",
       cases=[
    dict(id="TC-E2E-M5-11", scenario="ออกใบแจ้งหนี้และยืนยัน (Post)",
         pre="ทำ TC-E2E-M5-09 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; กด \"Create Draft Invoice\"", "เปิดใบแจ้งหนี้ที่เกิดขึ้น &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดตรงกับ SO เป๊ะ — ตัวอย่างจริง: INV/2026/00018 (48,150.00 บาท จาก S00112)", prio="High",
         shot="assets/mode5/tc11-invoice-posted.png"),
    dict(id="TC-E2E-M5-12", scenario="ตรวจรายการบัญชีของใบแจ้งหนี้ (Journal Items)",
         note="🔴 พบปัญหาจริง (ยังไม่ได้แก้ไข แจ้งผู้ใช้แล้ว): ใบส่งของ (Delivery) ของ FG ไม่ได้ลงบัญชีต้นทุนขาย (COGS) เลยสักบาท — มูลค่า Slab ที่ใช้ผลิต (2,800.00 บาท) ที่โอนเข้าบัญชี \"Inventory - Stone FG\" ตอนผลิตเสร็จ ค้างอยู่ในบัญชีนั้นตลอดไป ต่อให้สินค้าถูกส่งมอบให้ลูกค้าไปแล้วก็ตาม — ต่างจาก Mode 1/2/3 ที่มีการโอนต้นทุนออกตอนส่งของ/ออกใบแจ้งหนี้ให้เห็นชัดเจน",
         pre="ทำ TC-E2E-M5-11 เสร็จแล้ว",
         steps=["เปิดใบแจ้งหนี้ &gt; กดแท็บ \"Journal Items\""],
         sample="-",
         expected="เดบิต/เครดิตสมดุลกัน (รวมเท่ากันทั้ง 2 ฝั่ง) — ตัวอย่างจริง: INV/2026/00018 เดบิต Trade Receivables 48,150.00 บาท = เครดิต Sales Revenue - FG Production 45,000.00 + Output VAT 3,150.00 บาท (ไม่มีรายการ COGS ปรากฏเลย — ดูหมายเหตุสีแดงด้านบน)", prio="Medium",
         shot="assets/mode5/tc12-journal-items.png"),
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
