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
# REAL BUG FOUND + FIXED LIVE while building this doc (2026-09-14): the day
# before (2026-09-13), Session 129/ADR-061/062 tore down the old
# Factory-Worklist/"Cut to Order" wizard entirely, replacing it with a plain
# native Manufacturing Order (Admin picks the Block directly on a native MO,
# no wizard) — this had never had a real live Playwright click-through
# before this session. Building Mode 2's Lot-aggregate fixture through that
# new mechanism surfaced a genuine regression: every cut (regardless of
# pricing_mode) landed on a fresh per-cut lot, but Lot-mode materials are
# meant to pool ALL their cut stock onto one single aggregate
# `stone_bundle.material_lot_id` (stone.slab.create() already branches on
# this correctly — mrp_production.py's new action_stone_mark_done() just
# never called the existing _ensure_material_lot() helper). Effect: any
# fresh Lot-mode cut through the new MO flow was invisible to "Select Lot
# Stock" ("Not enough lot stock left: requested 0.50 sqm, only 0.00 sqm
# remaining" despite the physical stock genuinely existing) — this wasn't
# scoped to this test's own fixture, it would have hit any real Lot-mode
# use of the new cutting flow. Fixed in mrp_production.py
# (action_stone_mark_done now calls bundle._ensure_material_lot() and reuses
# material_lot_id for lot-mode bundles instead of minting a new lot), deployed
# to mbx-ee-dev, then re-verified live via a second real cut + sale on this
# same doc's own fixture before writing the numbers below. As a side effect,
# this same fix also resolves the OLD known-issue from the v1/v2 docs
# (TC-E2E-M2-12b, Lot-mode COGS always posting ฿0) — the broken lot linkage
# was the same root cause blocking FIFO consumption from ever finding the
# right valuation layer. See project_emg_o memory / decisions.md for the
# ADR entry.
#
# Built + the whole flow executed live on mbx-ee-dev (Playwright, 2026-09-14)
# before writing this file — every "sample data"/"expected result" below is
# a REAL observed number from that run:
#   - Serial (per-slab) path: Block BLK-26-0026 (E2E Mode2 Serial Fresh,
#     Marble) cut via the new native-MO flow -> Slab BLK-26-0026-1 (1.2 x
#     0.8 m, 0.96 Sq.Mt.) -> SO S00123 -> Delivery EG01/OUT/00077 ->
#     Invoice INV/2026/00025 (4,622.40 incl. VAT, COGS 300.00), Posted + In
#     Payment.
#   - Lot (aggregate) path: Block BLK-26-0027 (E2E Mode2 Lot Fresh, Marble).
#     First cut (1.0 Sq.Mt.) ran before the fix and landed on an orphan
#     per-cut lot ("BLK-26-0027-1", the bug reproduction — left in place as
#     historical evidence, harmless leftover); a second cut (also 1.0
#     Sq.Mt.) ran after deploying the fix and correctly landed on the
#     aggregate lot "BLK-26-0027-LOT" -> sold 0.50 of that 1.00 Sq.Mt. via
#     SO S00124 -> Delivery EG01/OUT/00078 -> Invoice INV/2026/00026
#     (2,140.00 incl. VAT, COGS 120.00, correctly non-zero), Posted + In
#     Payment.
#   Both fixtures kept on mbx-ee-dev as genuine reference data.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber/green callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low)

CATEGORIES = [
  dict(cat_id="E1", title="E1. ขาย (Sale — Mode 2, Serial per-slab)",
       subtitle="ADR-002/006/009 — เลือกทีละแผ่นตามเลข Serial · 3 test cases",
       cases=[
    dict(id="TC-E2E-M2-01", scenario="เพิ่มบรรทัดสินค้า Material โหมด Serial ใน Sale Order",
         pre="มีแผ่นหินสถานะ Available อยู่แล้ว จาก Material ที่ตั้ง Pricing Mode = Serial (per-slab)",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material นั้น (ถ้ามี Finish หลายแบบ ระบบจะให้เลือกก่อน)"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = E2E Mode2 Serial Fresh - Slab",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Select Slabs\" ปรากฏบนบรรทัดนั้น (ไม่ใช่ \"Select Lot Stock\")", prio="Medium",
         shot="assets/e2e-mode2/m2-s01-so-line-added.png"),
    dict(id="TC-E2E-M2-02", scenario="กด \"Select Slabs\" เลือกแผ่นตามเลข Serial",
         pre="ทำ TC-E2E-M2-01 เสร็จแล้ว",
         steps=["กดปุ่ม \"Select Slabs\" บนบรรทัด", "กด \"Add a line\" — หน้าต่างเลือกแผ่นแสดงรายการแผ่น Available พร้อมเลข Serial/ขนาด/สถานะ", "ติ๊กเลือกแผ่น กด \"Select\" แล้วกด \"Confirm Selection\""],
         sample="เลือกแผ่น = BLK-26-0026 #1 (BLK-26-0026-1)",
         expected="บรรทัด SO ผูกแผ่นที่เลือก จำนวน/ราคาต่อหน่วยเติมอัตโนมัติจากขนาด+ราคาจริงของแผ่น (ตัวอย่างจริง: 0.96 ตร.ม. &times; 4,500/ตร.ม. = 4,320)", prio="High",
         shot="assets/e2e-mode2/m2-s02-select-slabs-dialog.png"),
    dict(id="TC-E2E-M2-03", scenario="เช็ค Analytic Distribution แล้วยืนยัน (Confirm) Sale Order",
         pre="ทำ TC-E2E-M2-02 เสร็จแล้ว",
         steps=["เปิดคอลัมน์ \"Analytic Distribution\" ถ้ายังไม่เห็น (ปุ่มตัวเลือกคอลัมน์มุมขวาบนตาราง)", "กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="ช่อง Analytic Distribution ต้องมีค่าติดมาอัตโนมัติแล้วตั้งแต่ก่อน Confirm (Material + Block + หมวดวัสดุ รวม 3 มิติ) — SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ (ตัวอย่างจริง: S00123 &rarr; EG01/OUT/00077)", prio="High",
         shot="assets/e2e-mode2/m2-s03b-analytic-col-before-confirm.png"),
  ]),
  dict(cat_id="E2", title="E2. ขาย (Sale — Mode 2, Lot aggregate)",
       subtitle="ADR-020 — ระบุจำนวนตร.ม.บางส่วนจากล็อต ไม่ต้องขายทั้งล็อต · 3 test cases",
       cases=[
    dict(id="TC-E2E-M2-04", scenario="เพิ่มบรรทัดสินค้า Material โหมด Lot ใน Sale Order",
         pre="มีล็อตหินสถานะ Available อยู่แล้ว จาก Material ที่ตั้ง Pricing Mode = Lot (aggregate)",
         steps=["เปิด Sales &gt; Orders &gt; New (หรือใช้ SO เดิม)", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material โหมด Lot นี้"],
         sample="สินค้า = E2E Mode2 Lot Fresh - Slab (Material โหมด Lot)",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Select Lot Stock\" ปรากฏบนบรรทัดนั้นแทนที่จะเป็น \"Select Slabs\"", prio="Medium",
         shot="assets/e2e-mode2/m2-l01-so-line-added.png"),
    dict(id="TC-E2E-M2-05", scenario="กด \"Select Lot Stock\" ระบุจำนวนตร.ม.บางส่วนจากล็อต",
         note="✅ พบ+แก้บั๊กจริงระหว่างสร้างเคสนี้ (2026-09-14): กลไกตัดหินใหม่ (แทนที่ Factory Worklist เดิม เมื่อวาน) ไม่ได้ผูก lot ก้อนที่ตัดเข้ากับ material_lot_id ของ bundle ทำให้ขายผ่านปุ่มนี้ไม่ได้เลย (ระบบเห็นสต็อกเหลือ 0 ทั้งที่มีจริง) แก้ไขที่โค้ด (mrp_production.py เรียกใช้ _ensure_material_lot() ที่มีอยู่แล้ว) deploy แล้วบน mbx-ee-dev ตัวเลขด้านล่างมาจากการรันซ้ำหลังแก้แล้วจริง",
         pre="ทำ TC-E2E-M2-04 เสร็จแล้ว",
         steps=["กดปุ่ม \"Select Lot Stock\" บนบรรทัด", "เลือก Bundle ที่ต้องการในช่อง \"Lot (Block)\" — ระบบแสดงจำนวนตร.ม.ที่เหลืออยู่ให้ทันที", "กรอก \"Quantity to Sell (Sq.Mt.)\" เป็นจำนวนบางส่วน (ไม่จำเป็นต้องขายทั้งล็อต)", "กด \"Confirm Selection\""],
         sample="Lot = BLK-26-0027 (เหลือ 1.00 ตร.ม. เต็มล็อต)<br>Quantity to Sell (Sq.Mt.) = 0.50",
         expected="บรรทัด SO ผูก Lot ถูกต้อง จำนวน/ราคารวมปรับตาม 0.50 ตร.ม. ที่เลือกทันที (ตัวอย่างจริง: 0.50 &times; 4,000/ตร.ม. = 2,000) ไม่มีการเลือกแผ่นเดี่ยวใดๆ", prio="High",
         shot="assets/e2e-mode2/m2-l03-qty-entered.png"),
    dict(id="TC-E2E-M2-06", scenario="เช็ค Analytic Distribution แล้วยืนยัน (Confirm) Sale Order โหมด Lot",
         pre="ทำ TC-E2E-M2-05 เสร็จแล้ว",
         steps=["เปิดคอลัมน์ \"Analytic Distribution\" ถ้ายังไม่เห็น", "กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="ช่อง Analytic Distribution มีค่าติดมาอัตโนมัติเหมือนโหมด Serial — SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ — ตัวอย่างจริง: S00124 &rarr; EG01/OUT/00078 ส่วนที่เหลือของล็อตเดิม (0.50 ตร.ม.) ยังคงพร้อมขายต่อได้ตามปกติ", prio="High",
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
         shot_note="ภาพจากเส้นทาง Serial (EG01/OUT/00077) — เส้นทาง Lot เจอ error หน้าตาเดียวกัน (ดู EG01/OUT/00078)"),
    dict(id="TC-E2E-M2-08", scenario="กรอก/สแกน Scanned Serial ให้ตรงครบทุกบรรทัดแล้ว Validate",
         pre="ทำ TC-E2E-M2-07 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["กด \"Details\" ที่บรรทัดสินค้า", "กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial/Lot ที่จองไว้จริง แล้วกด Save", "กดปุ่ม Validate อีกครั้ง"],
         sample="Scanned Serial (Serial path) = BLK-26-0026-1<br>Scanned Serial (Lot path) = BLK-26-0027-LOT",
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
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO รวม VAT — ตัวอย่างจริง Lot: INV/2026/00026 (2,140.00)", prio="High",
         shot="assets/e2e-mode2/m2-l11-invoice-posted.png"),
    dict(id="TC-E2E-M2-10", scenario="รับชำระเงิน (Register Payment) บนใบแจ้งหนี้",
         pre="ทำ TC-E2E-M2-09 เสร็จแล้ว (Invoice = Posted)",
         steps=["เปิดใบแจ้งหนี้ &gt; กด \"Pay\"", "ตรวจ/ยืนยันยอดและวิธีชำระ &gt; กด Create Payment"],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นสถานะ \"In Payment\" — ตัวอย่างจริงทั้งคู่ (INV/2026/00025, INV/2026/00026) จบที่สถานะ Posted + In Payment", prio="Medium",
         shot="assets/e2e-mode2/m2-s11-invoice-paid.png"),
    dict(id="TC-E2E-M2-11", scenario="ตรวจรายการบัญชีบนใบแจ้งหนี้ (รายได้ + VAT + ลูกหนี้ + บัญชี)",
         pre="ทำ TC-E2E-M2-09 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="บรรทัดรายได้ต้องขึ้นบัญชีถูกโหมด — Serial = \"411160 Sales Revenue - Serial Slab Sale (Mode 2)\", Lot = \"411120 Sales Revenue - Lot Material (Mode 2)\" — พร้อม Analytic Distribution ครบ ตรงกับใน SO", prio="High",
         shot="assets/e2e-mode2/m2-l12-invoice-journal-items.png",
         shot_note="ภาพตัวอย่าง Lot (INV/2026/00026) — ตัวอย่าง Serial (INV/2026/00025) ดูได้จาก TC-E2E-M2-12"),
    dict(id="TC-E2E-M2-12", scenario="ตรวจว่า Serial-mode ลงบัญชีต้นทุนขาย (COGS) ถูกต้องหรือไม่",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว (Delivery = Done), ใช้ Invoice ฝั่ง Serial (INV/2026/00025)",
         steps=["เปิด Customer Invoice ฝั่ง Serial &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="เห็นคู่ COGS/Inventory แนบอัตโนมัติบนใบแจ้งหนี้ใบเดียวกัน (เดบิต \"511110 COGS - Stone Sales (all modes)\" / เครดิต \"113110 Inventory - Stone Blocks (Raw)\") พร้อม Analytic Distribution ตรงกับบรรทัดรายได้ — ตัวอย่างจริง INV/2026/00025: COGS/Inventory คู่ละ 300.00 (ยอดรวมสมดุล 4,922.40 = 4,922.40)", prio="High",
         shot="assets/e2e-mode2/m2-s10-invoice-journal-items.png"),
    dict(id="TC-E2E-M2-12b", scenario="ตรวจ Lot-mode COGS ลงบัญชีถูกต้องหรือไม่",
         note="✅ เดิมเป็น known issue เปิดอยู่ (Lot-mode COGS ขึ้น 0 บาทเสมอ, v1/v2) — ตอนนี้ปิดแล้วจริง เป็นผลพลอยได้จากการแก้บั๊ก material_lot_id ในเคส TC-E2E-M2-05 (สาเหตุเดียวกัน: lot ที่ผูกผิดทำให้ FIFO หาต้นทุนที่ถูกต้องไม่เจอ) ยืนยันด้วยการรันจริงรอบนี้ COGS ขึ้นถูกต้องไม่ใช่ 0 อีกต่อไป",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว (Delivery = Done), ใช้ Invoice ฝั่ง Lot (INV/2026/00026)",
         steps=["เปิด Customer Invoice ฝั่ง Lot &gt; กด smart button \"Journal Items\"", "เทียบกับ TC-E2E-M2-11/12 ฝั่ง Serial"],
         sample="-",
         expected="เห็นคู่ COGS/Inventory แนบอัตโนมัติเหมือนฝั่ง Serial — ตัวอย่างจริง INV/2026/00026: COGS/Inventory คู่ละ 120.00 (ยอดรวมสมดุล 2,260.00 = 2,260.00) ไม่ใช่ 0 บาทอีกต่อไป", prio="Medium",
         shot="assets/e2e-mode2/m2-l12-invoice-journal-items.png"),
  ]),
]
