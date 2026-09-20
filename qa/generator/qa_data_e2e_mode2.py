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
# REBUILT 2026-09-14 (v3) — full fresh live re-run per user request ("run
# playwrite ใหม่ ไม่เอาหน้าจอเก่า"), old v2 doc + screenshots moved to
# qa/_archive/. Uses 2 BRAND-NEW dedicated test materials ("E2E Mode2 Serial
# Fresh" / "E2E Mode2 Lot Fresh") instead of reusing old shared-instance
# stock, for the same "avoid cross-fixture FIFO contamination" reason
# documented in qa_data_e2e_mode1.py.
#
# REAL BUG FOUND + FIXED LIVE on 2026-09-14 (the day after Session
# 129/ADR-061/062 tore down the old Factory-Worklist/"Cut to Order" wizard,
# replacing it with a plain native Manufacturing Order): every cut
# (regardless of pricing_mode) landed on a fresh per-cut lot, but Lot-mode
# materials are meant to pool ALL their cut stock onto one single aggregate
# `stone_bundle.material_lot_id`. Fixed in mrp_production.py
# (action_stone_mark_done now calls bundle._ensure_material_lot() and reuses
# material_lot_id for lot-mode bundles instead of minting a new lot). Also
# resolved the OLD known-issue from the v1/v2 docs (TC-E2E-M2-12b, Lot-mode
# COGS always posting ฿0) — the broken lot linkage was the same root cause
# blocking FIFO consumption from ever finding the right valuation layer. See
# project_emg_o memory / decisions.md for the ADR entry.
#
# RE-RUN AGAIN 2026-09-16 (still v3 content-wise, screenshots + fixture
# refreshed) — after the Mode 3 batch-cut rebuild (ADR-066, Session 139)
# prompted the user to also archive Mode 1/2/4/5 and ask for fresh screens.
# Mode 2's own selling UI is untouched by that change, but the underlying
# cutting mechanism (native MO, no more wizard) is shared with Mode 3, so a
# fresh live re-run through that same mechanism is exactly what re-verifies
# both the material_lot_id fix and the COGS fix are still holding. Used
# brand-new "V2" materials ("E2E Mode2 Serial Fresh V2" / "E2E Mode2 Lot
# Fresh V2") since the original 2026-09-14 materials still had leftover
# on-hand Block stock (would have risked FIFO cross-contamination, same
# class of gotcha documented in qa_data_e2e_mode1.py). A real, separate
# fixture-building gotcha found this round: a Material's Slab/Block products
# created via the quick "Create <name>" one-liner inside the Material form
# default to `is_storable=False` ("Track Inventory" off) — any stock move
# against such a product marks itself "done" immediately but never creates a
# real stock.quant, so the freshly-cut Block silently showed 0 Remaining CBM
# even though the cut MO said "done". Fixed by explicitly enabling Track
# Inventory on both products before purchasing — not a product bug, a
# fixture-setup step this file's build process now knows to do.
#
# Built + the whole flow executed live on mbx-ee-dev (Playwright,
# 2026-09-14, fully re-run again 2026-09-16) before writing this file, so
# every "sample data"/"expected result" below is a REAL observed number from
# the 2026-09-16 run, not a guess:
#   - Serial (per-slab) path: PO P00058 (0.10 m3 @ 10,000/CBM) -> Block
#     BLK-26-0034 (E2E Mode2 Serial Fresh V2, Marble) cut via the native-MO
#     flow (EG01/STCUT/00045, auto-planned 5 slabs 1.2 x 0.8 m each) -> Slab
#     BLK-26-0034-1 (0.96 Sq.Mt.) -> SO S00133 -> Delivery EG01/OUT/00087 ->
#     Invoice INV/2026/00035 (4,622.40 incl. VAT, COGS 200.00), Posted + In
#     Payment.
#   - Lot (aggregate) path: PO P00059 (0.10 m3 @ 8,000/CBM) -> Block
#     BLK-26-0035 (E2E Mode2 Lot Fresh V2, Marble) cut via the native-MO flow
#     (EG01/STCUT/00046, auto-planned 5 slabs 1.0 x 1.0 m each, all correctly
#     pooled onto aggregate lot "BLK-26-0035-LOT" = 5.00 Sq.Mt. total) ->
#     sold 2.00 of that 5.00 Sq.Mt. via SO S00134 -> Delivery EG01/OUT/00088
#     -> Invoice INV/2026/00036 (8,560.00 incl. VAT, COGS 320.00, correctly
#     non-zero), Posted + In Payment.
#   Both fixtures kept on mbx-ee-dev as genuine reference data.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber/green callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low)
#
# ADDED 2026-09-20 (Session 152) — new category E5, "ตัดใหม่ (Cut Order)":
# this file previously started from "already have Slabs/Lot in stock" and
# explicitly left Cut Order out of scope (see the file's own opening note
# above). The client walkthrough that session covered the Cut Order sub-flow
# for the first time end-to-end, so it now has its own category here rather
# than a separate doc — same product classification (is_stone_material),
# same Sale Point 2 ("จุดขาย 2"), just the "don't have a Slab yet, only a
# Block" starting condition instead. Real run executed live on mbx-ee-dev,
# via the real Manufacturing UI (not odoo shell) — see E5's own dict comment
# below for the full real-data narrative.

CATEGORIES = [
  dict(cat_id="E1", title="E1. ขาย (Sale — Mode 2, Serial per-slab)",
       subtitle="ADR-002/006/009 — เลือกทีละแผ่นตามเลข Serial · 3 test cases",
       cases=[
    dict(id="TC-E2E-M2-01", scenario="เพิ่มบรรทัดสินค้า Material โหมด Serial ใน Sale Order",
         pre="มีแผ่นหินสถานะ Available อยู่แล้ว จาก Material ที่ตั้ง Pricing Mode = Serial (per-slab)",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material นั้น (ถ้ามี Finish หลายแบบ ระบบจะให้เลือกก่อน)"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = E2E Mode2 Serial Fresh V2 - Slab",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Select Slabs\" ปรากฏบนบรรทัดนั้น (ไม่ใช่ \"Select Lot Stock\")", prio="Medium",
         shot="assets/e2e-mode2/m2-s01-so-line-added.png"),
    dict(id="TC-E2E-M2-02", scenario="กด \"Select Slabs\" เลือกแผ่นตามเลข Serial",
         pre="ทำ TC-E2E-M2-01 เสร็จแล้ว",
         steps=["กดปุ่ม \"Select Slabs\" บนบรรทัด", "กด \"Add a line\" — หน้าต่างเลือกแผ่นแสดงรายการแผ่น Available พร้อมเลข Serial/ขนาด/สถานะ", "ติ๊กเลือกแผ่น กด \"Select\" แล้วกด \"Confirm Selection\""],
         sample="เลือกแผ่น = BLK-26-0034 #1 (BLK-26-0034-1)",
         expected="บรรทัด SO ผูกแผ่นที่เลือก จำนวน/ราคาต่อหน่วยเติมอัตโนมัติจากขนาด+ราคาจริงของแผ่น (ตัวอย่างจริง: 0.96 ตร.ม. &times; 4,500/ตร.ม. = 4,320)", prio="High",
         shot="assets/e2e-mode2/m2-s02-select-slabs-dialog.png"),
    dict(id="TC-E2E-M2-03", scenario="เช็ค Analytic Distribution แล้วยืนยัน (Confirm) Sale Order",
         pre="ทำ TC-E2E-M2-02 เสร็จแล้ว",
         steps=["เปิดคอลัมน์ \"Analytic Distribution\" ถ้ายังไม่เห็น (ปุ่มตัวเลือกคอลัมน์มุมขวาบนตาราง)", "กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="ช่อง Analytic Distribution ต้องมีค่าติดมาอัตโนมัติแล้วตั้งแต่ก่อน Confirm (Material + Block + หมวดวัสดุ รวม 3 มิติ) — SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ (ตัวอย่างจริง: S00133 &rarr; EG01/OUT/00087)", prio="High",
         shot="assets/e2e-mode2/m2-s03b-analytic-col-before-confirm.png"),
  ]),
  dict(cat_id="E2", title="E2. ขาย (Sale — Mode 2, Lot aggregate)",
       subtitle="ADR-020 — ระบุจำนวนตร.ม.บางส่วนจากล็อต ไม่ต้องขายทั้งล็อต · 3 test cases",
       cases=[
    dict(id="TC-E2E-M2-04", scenario="เพิ่มบรรทัดสินค้า Material โหมด Lot ใน Sale Order",
         pre="มีล็อตหินสถานะ Available อยู่แล้ว จาก Material ที่ตั้ง Pricing Mode = Lot (aggregate)",
         steps=["เปิด Sales &gt; Orders &gt; New (หรือใช้ SO เดิม)", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material โหมด Lot นี้"],
         sample="สินค้า = E2E Mode2 Lot Fresh V2 - Slab (Material โหมด Lot)",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Select Lot Stock\" ปรากฏบนบรรทัดนั้นแทนที่จะเป็น \"Select Slabs\"", prio="Medium",
         shot="assets/e2e-mode2/m2-l01-so-line-added.png"),
    dict(id="TC-E2E-M2-05", scenario="กด \"Select Lot Stock\" ระบุจำนวนตร.ม.บางส่วนจากล็อต",
         note="✅ ยืนยันซ้ำ (2026-09-16): บั๊กเดิม (lot ที่ตัดใหม่ไม่ผูกกับ material_lot_id ของ bundle ทำให้ขายผ่านปุ่มนี้ไม่ได้) ยังคงปิดอยู่จริง — ครั้งนี้ตัดสต๊อกใหม่ 5 แผ่น (5.00 ตร.ม.) ผ่านกลไก MO เดียวกับ Mode 3 แล้วรวมเป็นล็อตเดียวถูกต้องอัตโนมัติทันที ไม่ต้องแก้โค้ดเพิ่ม",
         pre="ทำ TC-E2E-M2-04 เสร็จแล้ว",
         steps=["กดปุ่ม \"Select Lot Stock\" บนบรรทัด", "เลือก Bundle ที่ต้องการในช่อง \"Lot (Block)\" — ระบบแสดงจำนวนตร.ม.ที่เหลืออยู่ให้ทันที", "กรอก \"Quantity to Sell (Sq.Mt.)\" เป็นจำนวนบางส่วน (ไม่จำเป็นต้องขายทั้งล็อต)", "กด \"Confirm Selection\""],
         sample="Lot = BLK-26-0035 (เหลือ 5.00 ตร.ม. เต็มล็อต)<br>Quantity to Sell (Sq.Mt.) = 2.00",
         expected="บรรทัด SO ผูก Lot ถูกต้อง จำนวน/ราคารวมปรับตาม 2.00 ตร.ม. ที่เลือกทันที (ตัวอย่างจริง: 2.00 &times; 4,000/ตร.ม. = 8,000) ไม่มีการเลือกแผ่นเดี่ยวใดๆ", prio="High",
         shot="assets/e2e-mode2/m2-l03-qty-entered.png"),
    dict(id="TC-E2E-M2-06", scenario="เช็ค Analytic Distribution แล้วยืนยัน (Confirm) Sale Order โหมด Lot",
         pre="ทำ TC-E2E-M2-05 เสร็จแล้ว",
         steps=["เปิดคอลัมน์ \"Analytic Distribution\" ถ้ายังไม่เห็น", "กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="ช่อง Analytic Distribution มีค่าติดมาอัตโนมัติเหมือนโหมด Serial — SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ — ตัวอย่างจริง: S00134 &rarr; EG01/OUT/00088 ส่วนที่เหลือของล็อตเดิม (3.00 ตร.ม.) ยังคงพร้อมขายต่อได้ตามปกติ", prio="High",
         shot="assets/e2e-mode2/m2-l04b-analytic-col.png"),
  ]),
  dict(cat_id="E3", title="E3. จัดส่ง (Delivery — Scan Verification)",
       subtitle="ADR-009 — ต้องสแกน/กรอก Serial ให้ตรงก่อน Validate เสมอ ใช้ร่วมกันทั้ง Serial และ Lot · 2 test cases",
       cases=[
    dict(id="TC-E2E-M2-07", scenario="พยายาม Validate ใบส่งของโดยยังไม่กรอก Scanned Serial ให้ตรง",
         note="หมายเหตุ: กันส่งแผ่น/ล็อตผิดให้ลูกค้าโดยไม่ได้ตรวจสอบก่อน (ADR-009) — ใช้ตรรกะเดียวกันไม่ว่าเป็นบรรทัด Serial หรือ Lot ยืนยันแล้วทั้งคู่จริงในรอบนี้",
         pre="ทำ TC-E2E-M2-03 หรือ TC-E2E-M2-06 เสร็จแล้ว มีใบส่งของสถานะ Ready รออยู่",
         steps=["เปิดใบส่งของ (Delivery) ที่เกิดขึ้นอัตโนมัติ", "กดปุ่ม Validate ทันทีโดยยังไม่กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial/Lot ที่จองไว้"],
         sample="-",
         expected="ระบบฟ้อง error สองภาษาทันที: \"สแกน Serial ไม่ตรง กรุณาสแกนให้ครบก่อน Validate\" พร้อมระบุชื่อ Serial/Lot ที่ยังไม่ตรง บันทึกไม่ผ่าน", prio="High",
         shot="assets/e2e-mode2/m2-s06-delivery-scan-error.png",
         shot_note="ภาพจากเส้นทาง Serial (EG01/OUT/00087) — เส้นทาง Lot เจอ error หน้าตาเดียวกัน (ดู EG01/OUT/00088)"),
    dict(id="TC-E2E-M2-08", scenario="กรอก/สแกน Scanned Serial ให้ตรงครบทุกบรรทัดแล้ว Validate",
         pre="ทำ TC-E2E-M2-07 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["กด \"Details\" ที่บรรทัดสินค้า", "กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial/Lot ที่จองไว้จริง แล้วกด Save", "กดปุ่ม Validate อีกครั้ง"],
         sample="Scanned Serial (Serial path) = BLK-26-0034-1<br>Scanned Serial (Lot path) = BLK-26-0035-LOT",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done สำเร็จ — แผ่น/ปริมาณที่ขายหายจากสต็อกที่ขายได้ (Available) แล้ว", prio="High",
         shot="assets/e2e-mode2/m2-s09-delivery-done.png"),
  ]),
  dict(cat_id="E4", title="E4. บัญชี (Accounting + Payment)",
       subtitle="ออกใบแจ้งหนี้ + รับชำระเงิน + ตรวจรายการบัญชี · 5 test cases",
       cases=[
    dict(id="TC-E2E-M2-09", scenario="สร้างและยืนยันใบแจ้งหนี้ลูกค้า (Customer Invoice)",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; Create Draft", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO รวม VAT — ตัวอย่างจริง Lot: INV/2026/00036 (8,560.00)", prio="High",
         shot="assets/e2e-mode2/m2-l11-invoice-posted.png"),
    dict(id="TC-E2E-M2-10", scenario="รับชำระเงิน (Register Payment) บนใบแจ้งหนี้",
         pre="ทำ TC-E2E-M2-09 เสร็จแล้ว (Invoice = Posted)",
         steps=["เปิดใบแจ้งหนี้ &gt; กด \"Pay\"", "ตรวจ/ยืนยันยอดและวิธีชำระ &gt; กด Create Payment"],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นสถานะ \"In Payment\" — ตัวอย่างจริงทั้งคู่ (INV/2026/00035, INV/2026/00036) จบที่สถานะ Posted + In Payment", prio="Medium",
         shot="assets/e2e-mode2/m2-s11-invoice-paid.png"),
    dict(id="TC-E2E-M2-11", scenario="ตรวจรายการบัญชีบนใบแจ้งหนี้ (รายได้ + VAT + ลูกหนี้ + บัญชี)",
         pre="ทำ TC-E2E-M2-09 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="บรรทัดรายได้ต้องขึ้นบัญชีถูกโหมด — Serial = \"411160 Sales Revenue - Serial Slab Sale (Mode 2)\", Lot = \"411120 Sales Revenue - Lot Material (Mode 2)\" — พร้อม Analytic Distribution ครบ ตรงกับใน SO", prio="High",
         shot="assets/e2e-mode2/m2-l12-invoice-journal-items.png",
         shot_note="ภาพตัวอย่าง Lot (INV/2026/00036) — ตัวอย่าง Serial (INV/2026/00035) ดูได้จาก TC-E2E-M2-12"),
    dict(id="TC-E2E-M2-12", scenario="ตรวจว่า Serial-mode ลงบัญชีต้นทุนขาย (COGS) ถูกต้องหรือไม่",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว (Delivery = Done), ใช้ Invoice ฝั่ง Serial (INV/2026/00035)",
         steps=["เปิด Customer Invoice ฝั่ง Serial &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="เห็นคู่ COGS/Inventory แนบอัตโนมัติบนใบแจ้งหนี้ใบเดียวกัน (เดบิต \"511110 COGS - Stone Sales (all modes)\" / เครดิต \"113110 Inventory - Stone Blocks (Raw)\") พร้อม Analytic Distribution ตรงกับบรรทัดรายได้ — ตัวอย่างจริง INV/2026/00035: COGS/Inventory คู่ละ 200.00 (ยอดรวมสมดุล 4,822.40 = 4,822.40)", prio="High",
         shot="assets/e2e-mode2/m2-s10-invoice-journal-items.png"),
    dict(id="TC-E2E-M2-12b", scenario="ตรวจ Lot-mode COGS ลงบัญชีถูกต้องหรือไม่",
         note="✅ เดิมเป็น known issue เปิดอยู่ (Lot-mode COGS ขึ้น 0 บาทเสมอ, v1/v2) — ปิดแล้วจริง ยืนยันซ้ำอีกครั้งด้วยการรันจริงรอบนี้ (2026-09-16) COGS ขึ้นถูกต้องไม่ใช่ 0",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว (Delivery = Done), ใช้ Invoice ฝั่ง Lot (INV/2026/00036)",
         steps=["เปิด Customer Invoice ฝั่ง Lot &gt; กด smart button \"Journal Items\"", "เทียบกับ TC-E2E-M2-11/12 ฝั่ง Serial"],
         sample="-",
         expected="เห็นคู่ COGS/Inventory แนบอัตโนมัติเหมือนฝั่ง Serial — ตัวอย่างจริง INV/2026/00036: COGS/Inventory คู่ละ 320.00 (ยอดรวมสมดุล 8,880.00 = 8,880.00) ไม่ใช่ 0 บาทอีกต่อไป", prio="Medium",
         shot="assets/e2e-mode2/m2-l12-invoice-journal-items.png"),
  ]),
  # Session 152 (2026-09-20): ADR-061 (B3b) tore down the old "Cut to Order"
  # wizard button entirely — Factory/Admin now creates a plain native
  # mrp.production directly in Manufacturing and manually links
  # stone_bundle_id (the Block) + sale_order_line_id back to the waiting SO
  # line, no automatic trigger from the SO line at all. This category covers
  # that whole sub-flow: SO line added with NO slab in stock yet -> Factory
  # cuts a fresh Block via the guided Step 1/2/3 MO form -> Sales picks the
  # newly-cut Slab back on the same SO line -> Delivery/Invoice/Payment, same
  # as the rest of Mode 2. Real run executed live on mbx-ee-dev 2026-09-20:
  # PO P00061 (0.10 m3 @ 10,000/CBM) -> Block BLK-26-0037 (E2E Mode2 Serial
  # Fresh, Marble) -> SO S00146 (line added before any stock existed) -> Cut
  # Order MO EG01/STCUT/00050 (Target 1.2x0.8m, auto-planned 5 slabs) ->
  # Slab BLK-26-0037-1 (0.96 Sq.Mt.) -> Delivery EG01/OUT/00093 -> Invoice
  # INV/2026/00039 (4,622.40 incl. VAT, COGS 300.00), Posted + In Payment.
  dict(cat_id="E5", title="E5. ตัดใหม่ (Cut Order — สร้าง Slab ใหม่จาก Block เมื่อยังไม่มีสต็อก)",
       subtitle="ADR-061/066 — Factory สร้าง Manufacturing Order ตัด Block เองโดยตรงในแอป Manufacturing ไม่มี wizard อัตโนมัติจากบรรทัด SO แล้ว · 11 test cases",
       cases=[
    dict(id="TC-E2E-M2-13", scenario="เพิ่มบรรทัดสินค้าใน SO ทั้งที่ยังไม่มีแผ่นพร้อมขาย",
         pre="ยังไม่มีแผ่นหินสถานะ Available ของ Material นี้เลย มีแต่ Block พร้อมอยู่ในสต็อก (ผ่านการซื้อ PO แบบเดียวกับ Mode 1)",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material นี้"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = E2E Mode2 Serial Fresh - Slab",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Select Slabs\" ปรากฏเหมือนปกติ แต่ตอนนี้ยังไม่มีแผ่นให้เลือกเลย (0 Available) — ราคาที่ขึ้นเป็นแค่ List Price เริ่มต้น ต้องให้ Factory ตัดสต็อกใหม่ก่อนถึงจะขายได้จริง", prio="Medium",
         shot="assets/e2e-mode2/m2-c01-so-line-added-no-stock.png"),
    dict(id="TC-E2E-M2-14", scenario="Factory สร้าง Manufacturing Order ตัด Block ใหม่ (ขั้นตอนที่ 1-3)",
         pre="ทำ TC-E2E-M2-13 เสร็จแล้ว (มี SO บรรทัดรออยู่), มี Block พร้อมอยู่ในสต็อก",
         steps=["เปิด Manufacturing &gt; New", "ช่อง \"Stone Block\" (ขั้นตอนที่ 1) เลือก Block ที่จะตัด — ระบบดึงสินค้า/BOM ที่จะผลิตให้อัตโนมัติ", "ช่อง \"Target Slab L/H (M)\" (ขั้นตอนที่ 2) ใส่ขนาดแผ่นที่ต้องการ — ระบบคำนวณจำนวนแผ่นที่จะได้ให้อัตโนมัติ (ดูที่แท็บ Planned/Actual Slabs)", "ช่อง \"For Sale Order Line\" (ขั้นตอนที่ 3) เลือกบรรทัด SO ที่รออยู่ แล้ว Save"],
         sample="Stone Block = BLK-26-0037<br>Target Slab L (M) = 1.20, Target Slab H (M) = 0.80<br>For Sale Order Line = S00146",
         expected="ระบบคำนวณจำนวนแผ่นที่จะผลิตอัตโนมัติจาก CBM ที่เหลือของ Block หารด้วยขนาดแผ่นที่ตั้ง (ตัวอย่างจริง: Block เหลือ 0.10 m&sup3; &divide; (1.20&times;0.80&times;0.02) = 5 แผ่นพอดี) พร้อมสร้างบรรทัด Planned Slabs ให้ครบอัตโนมัติ — ถ้าต้องการตัดน้อยกว่าที่ระบบคำนวณ ลบบรรทัดส่วนเกินออกได้เองก่อน Confirm",
         note="✨ ฟีเจอร์ใหม่ session นี้ — Manufacturing Order เดิมไม่มีทางผูกกลับมาที่ SO ให้เห็นได้เลย (ปุ่ม MO มาตรฐานของ Odoo นับไม่ได้เพราะ Cut Order นี้ไม่ได้ผ่านกลไก Procurement) จึงเพิ่มปุ่ม \"Cut Orders\" ใหม่ไว้บน SO (ดู TC-E2E-M2-18)",
         prio="High", shot="assets/e2e-mode2/m2-c02-mo-block-target-soline.png"),
    dict(id="TC-E2E-M2-15", scenario="ย้าย Block เข้าสถานีตัด (Move to Production) แล้ว Confirm MO",
         pre="ทำ TC-E2E-M2-14 เสร็จแล้ว — ระบบเตือนว่า Block ยังไม่ได้อยู่ที่สถานีตัด (Stone Production) เพียงพอ",
         steps=["กดปุ่ม \"ย้ายด่วน (Move to Production)\" มุมบนซ้าย — ระบบสร้าง+ยืนยัน Internal Transfer ย้าย Block ไปสถานีตัดให้อัตโนมัติในคลิกเดียว", "กด \"Confirm\""],
         sample="-",
         expected="แถบเตือนสีเหลืองเปลี่ยนเป็นข้อความสีเขียว \"พร้อม Confirm แล้ว\" หลังย้ายสำเร็จ — กด Confirm ผ่านทันที ไม่ต้องออกไปทำ Internal Transfer เองใน Inventory", prio="High",
         shot="assets/e2e-mode2/m2-c03-mo-move-to-production.png"),
    dict(id="TC-E2E-M2-16", scenario="ตัดจริงในแท็บ Work Orders แล้วกด Complete Cut",
         pre="ทำ TC-E2E-M2-15 เสร็จแล้ว (MO สถานะ Confirmed)",
         steps=["ไปแท็บ \"Work Orders\" ดูขั้นตอนที่ต้องทำ (เช่น Transport, Gangsaw)", "ไปแท็บ \"Planned/Actual Slabs\" กรอกขนาดจริงที่ตัดได้ในคอลัมน์ Actual L/H/Thickness (ค่าเริ่มต้น = ตามแผน)", "กดปุ่ม \"Complete Cut\""],
         sample="-",
         expected="MO เปลี่ยนสถานะเป็น Done ทันที — ระบบสร้าง Slab ใหม่ครบตามแผนพร้อม Serial Number ให้อัตโนมัติในตัว (ตัวอย่างจริง: 5 แผ่น, Serial Numbers 5)", prio="High",
         shot="assets/e2e-mode2/m2-c04-mo-complete-cut-done.png"),
    dict(id="TC-E2E-M2-17", scenario="กลับไปที่ SO เดิม เลือกแผ่นที่เพิ่งตัดได้",
         pre="ทำ TC-E2E-M2-16 เสร็จแล้ว",
         steps=["เปิด SO เดิมกลับมา (บรรทัดที่ทำไว้ใน TC-E2E-M2-13)", "กด \"Select Slabs\" บนบรรทัดนั้น"],
         sample="-",
         expected="หน้าต่าง Select Slabs เตรียมแผ่นที่เพิ่งตัดได้มาให้อัตโนมัติแล้ว (สถานะ Hold ผูกกับบรรทัดนี้โดยตรง เพราะ MO ระบุ \"For Sale Order Line\" ไว้ตั้งแต่ต้น) ไม่ต้องกด Add a line เลือกเองซ้ำ — กด \"Confirm Selection\" ได้ทันที", prio="High",
         shot="assets/e2e-mode2/m2-c05-so-select-slabs-prefilled.png"),
    dict(id="TC-E2E-M2-18", scenario="ยืนยัน (Confirm) Sale Order — เช็คปุ่ม Cut Orders ปรากฏ",
         pre="ทำ TC-E2E-M2-17 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ — smart button ใหม่ \"Cut Orders\" ปรากฏที่มุมบน (นับ Manufacturing Order ที่ตัดมาเพื่อ SO นี้โดยเฉพาะ แยกจาก \"Slabs\") กดเข้าไปเปิด MO ที่ตัดให้ตรงตัวได้เลย — ตัวอย่างจริง: S00146 &rarr; EG01/OUT/00093, Total 4,622.40", prio="High",
         shot="assets/e2e-mode2/m2-c06-so-confirmed-cutorders-btn.png"),
    dict(id="TC-E2E-M2-19", scenario="พยายาม Validate ใบส่งของโดยยังไม่สแกน Serial ให้ตรง",
         note="หมายเหตุ: กันส่งแผ่นผิดให้ลูกค้าโดยไม่ได้ตรวจสอบก่อน (ADR-009) — ใช้ตรรกะเดียวกับ Mode 2 ปกติ (TC-E2E-M2-07) ไม่ว่าแผ่นนั้นจะมาจากสต็อกเดิมหรือตัดใหม่",
         pre="ทำ TC-E2E-M2-18 เสร็จแล้ว มีใบส่งของสถานะ Ready รออยู่",
         steps=["เปิดใบส่งของ (Delivery) ที่เกิดขึ้นอัตโนมัติ", "กดปุ่ม Validate ทันทีโดยยังไม่กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial ที่จองไว้"],
         sample="-",
         expected="ระบบฟ้อง error สองภาษาทันทีเหมือน Mode 2 ปกติ: \"สแกน Serial ไม่ตรง กรุณาสแกนให้ครบก่อน Validate\" พร้อมระบุชื่อแผ่นที่ยังไม่ตรง (ตัวอย่างจริง: BLK-26-0037-1) บันทึกไม่ผ่าน", prio="Medium",
         shot="assets/e2e-mode2/m2-c07-delivery-scan-error.png"),
    dict(id="TC-E2E-M2-20", scenario="กรอก/สแกน Scanned Serial ให้ตรงแล้ว Validate",
         pre="ทำ TC-E2E-M2-19 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["กด \"Details\" ที่บรรทัดสินค้า", "กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial ที่จองไว้จริง แล้วกด Save", "กดปุ่ม Validate อีกครั้ง"],
         sample="Scanned Serial = BLK-26-0037-1",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done สำเร็จ — แผ่นที่ขายหายจากสต็อกที่ขายได้ (Available) แล้ว", prio="Medium",
         shot="assets/e2e-mode2/m2-c08-delivery-done.png"),
    dict(id="TC-E2E-M2-21", scenario="สร้างและยืนยันใบแจ้งหนี้ — เช็คบัญชีรายได้ที่ใช้",
         note="ℹ️ พฤติกรรมที่ตั้งใจไว้ ไม่ใช่บั๊ก — ระบบแยกบัญชีรายได้ตามว่า \"แผ่นนี้ถูกตัดมาเพื่อออเดอร์นี้โดยเฉพาะ\" (บัญชีนี้) หรือ \"หยิบจากสต็อกที่ตัดไว้ก่อนแล้ว\" (บัญชี Serial Slab Sale ปกติ ดู TC-E2E-M2-11) — ชื่อบัญชียังใช้คำว่า \"Mode 3\" หลงเหลือจากก่อนรวม Mode เข้ากับจุดขาย 2 ไม่กระทบความถูกต้องทางบัญชี เป็นแค่ชื่อที่อาจทำให้สับสนถ้าไม่รู้ที่มา — ควรพิจารณาเปลี่ยนชื่อบัญชีให้สื่อสารตรงกับจุดขาย 2 ในรอบถัดไป",
         pre="ทำ TC-E2E-M2-20 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; Create Draft", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO รวม VAT — ตัวอย่างจริง INV/2026/00039 (4,622.40) แต่บัญชีรายได้ที่ขึ้นคือ \"Sales Revenue - Cut-to-Order (Mode 3)\" ไม่ใช่ \"Serial Slab Sale (Mode 2)\" เหมือนบรรทัดที่ขายจากสต็อกที่มีอยู่แล้ว (ดูหมายเหตุ)", prio="High",
         shot="assets/e2e-mode2/m2-c09-invoice-posted-account.png"),
    dict(id="TC-E2E-M2-22", scenario="ตรวจรายการบัญชี COGS/Inventory บนใบแจ้งหนี้",
         pre="ทำ TC-E2E-M2-21 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="เห็นคู่ COGS/Inventory แนบอัตโนมัติเหมือน Mode 2 ปกติ พร้อม Analytic Distribution ครบ — ตัวอย่างจริง INV/2026/00039: เดบิต \"511110 COGS - Stone Sales (all modes)\" / เครดิต \"113110 Inventory - Stone Blocks (Raw)\" คู่ละ 300.00 ยอดรวมสมดุล 4,922.40 = 4,922.40", prio="High",
         shot="assets/e2e-mode2/m2-c10-invoice-journal-items.png"),
    dict(id="TC-E2E-M2-23", scenario="รับชำระเงิน (Register Payment)",
         pre="ทำ TC-E2E-M2-21 เสร็จแล้ว (Invoice = Posted)",
         steps=["เปิดใบแจ้งหนี้ &gt; กด \"Pay\"", "ตรวจ/ยืนยันยอดและวิธีชำระ &gt; กด Create Payment"],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นสถานะ \"In Payment\" — จบเส้นทาง \"ตัดใหม่\" ทั้งหมดตั้งแต่ยังไม่มีสต็อกจนถึงรับเงินสำเร็จ (ตัวอย่างจริง: INV/2026/00039)", prio="Medium",
         shot="assets/e2e-mode2/m2-c11-invoice-paid.png"),
  ]),
]
