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
# REBUILT 2026-09-09 (v2) after a Mode 2 Analytic-Architecture regression
# spot-check (Session 120) turned up 2 real bugs found+fixed live, plus 2
# more real findings left open — every case below is from fresh Playwright
# runs on eg-tst that day, not the old 21 ส.ค. decks the v1 file was built
# from (those numbers/screenshots are gone from this file entirely now):
#   - Serial (per-slab) path: Bundle BLK-26-0050 (บลู ซุปเปอร์เจนติ/BLUE
#     SERPERGENTI, Marble, Finish=Polished), 1 available slab -> SO S00107 ->
#     Delivery EG01/OUT/00077 -> Invoice INV/2026/00008, Posted + Paid.
#   - Lot (aggregate) path: Bundle BLK-26-0047 (ดำอัฟริกา/BLACK AFRICA,
#     Granite), sold 2.00 of 6.00 Sq.Mt. remaining -> SO S00111 -> Delivery
#     EG01/OUT/00078 -> Invoice INV/2026/00009 (8,560.00 incl. 7% VAT),
#     Posted + Paid.
#   Both fixtures kept on eg-tst as genuine reference data, not synthetic.
#
# BUGS FOUND + FIXED LIVE THIS SESSION (Session 120):
#   1. Every Serial-mode sale (Select Slabs) was silently posting revenue to
#      the Mode 3 Cut-to-Order GL account instead of its own — sale_order_line
#      ._get_stone_sale_mode() couldn't tell a genuine Serial line (no MRP
#      involved) apart from a real Cut-to-Order line (mrp.production with
#      stone_bundle_id set), both being is_stone_material=True. Fixed by
#      mirroring the same Cut Order check res.company._stone_classify_order_
#      mode() already used for report-time labeling. New account "Sales
#      Revenue - Serial Slab Sale (Mode 2)" (411160), both companies, both
#      DBs. Confirmed on this file's own S00107/S00096 fixtures.
#   2. Most of eg-tst's existing stock (bundles received before this session,
#      likely the 2026-08-29 bulk demo import) never had real cost injected
#      into Odoo's native FIFO valuation at all — despite the module's own
#      cost tracking (po_cost_cbm/po_cost_sqmt/stone.slab.cost) being
#      correct throughout, so every sale posted ฿0 COGS. Backfilled the
#      missing product.value records at both the Block level (13 bundles,
#      eg-tst; 1, mbx-ee-dev) and the Slab level (53 slabs, eg-tst; 15,
#      mbx-ee-dev) — Slab needed a SEPARATE fix from Block because Serial
#      mode sells the cut Slab product, a different product.product record
#      from the raw Block it came from. Also renamed the shared Stone-
#      category COGS account from the misleading "COGS - Block Direct Sale
#      (Mode 1)" (it's used for every mode, not just Mode 1) to "COGS -
#      Stone Sales (all modes)".
#
# KNOWN ISSUES FOUND, LEFT OPEN (not fixed this session — real, but lower
# priority / needs more careful work than a quick backfill):
#   - Lot-mode sales still post ฿0 COGS even after the backfill above — the
#     receiving move's FIFO layer (real value, confirmed present) never
#     gets consumed by the delivery move (remaining_qty stays at its full
#     original amount after a real sale). Root cause not yet found — see
#     TC-E2E-M2-12b.
#   - Bundle BLK-26-0051 (เทาดำอัฟริกา/NERO RUSTENBURG) has corrupted stock.lot
#     data unrelated to any of the above (both its slabs' lots point to a
#     completely different, unrelated material) — avoid this bundle for any
#     demo/test until fixed. Not a live code bug, looks like leftover
#     corruption from the same 2026-08-29 import.
#   - BLK-26-0050's own material (BLUE SERPERGENTI) has no List Price
#     configured — its SO line's price is correctly computed at Select
#     Slabs time but resets to 0 on Confirm (a native Odoo pricelist
#     recompute picking up the missing price, not a bug in Select Slabs
#     itself). Real, unrelated data-setup gap — this is exactly why this
#     fixture's own Invoice below shows ฿0 revenue while still proving the
#     COGS fix; don't mistake the ฿0 for a regression.
#
# Column model per test case (same as qa_data_e2e_mode1.py):
#   id, scenario, note (optional amber/green/copper callout), pre, steps
#   (list), sample (str, the "key this in" data - '-' if the case has
#   nothing to key), expected, prio (High/Medium/Low)

CATEGORIES = [
  dict(cat_id="E1", title="E1. ขาย (Sale — Mode 2, Serial per-slab)",
       subtitle="ADR-002/006/009 — เลือกทีละแผ่นตามเลข Serial · 3 test cases",
       cases=[
    dict(id="TC-E2E-M2-01", scenario="เพิ่มบรรทัดสินค้า Material โหมด Serial ใน Sale Order",
         pre="มีแผ่นหินสถานะ Available อยู่แล้ว จาก Material ที่ตั้ง Pricing Mode = Serial (per-slab)",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material นั้น (ถ้ามี Finish หลายแบบ ระบบจะให้เลือกก่อน)"],
         sample="ลูกค้า = \"E2E Test Customer\"<br>สินค้า = บลู ซุปเปอร์เจนติ/BLUE SERPERGENTI - Slab, Finish = Polished",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Select Slabs\" ปรากฏบนบรรทัดนั้น (ไม่ใช่ \"Select Lot Stock\")", prio="Medium",
         shot="assets/e2e-mode2-v2/m2v2-s01-so-line-added.png"),
    dict(id="TC-E2E-M2-02", scenario="กด \"Select Slabs\" เลือกแผ่นตามเลข Serial (รองรับเลือกหลายแผ่นพร้อมกันในคลิกเดียว)",
         pre="ทำ TC-E2E-M2-01 เสร็จแล้ว",
         steps=["กดปุ่ม \"Select Slabs\" บนบรรทัด", "กด \"Add a line\" — หน้าต่างเลือกแผ่นแสดงรายการแผ่น Available พร้อมเลข Serial/ขนาด/สถานะ ติ๊กเลือกได้หลายแผ่นพร้อมกัน", "กด Select แล้วกด \"Confirm Selection\""],
         sample="เลือกแผ่น = BLK-26-0050 #1",
         expected="บรรทัด SO ผูกแผ่นที่เลือก จำนวน/ราคาต่อหน่วยเติมอัตโนมัติจากขนาด+ราคาจริงของแผ่น", prio="High",
         shot="assets/e2e-mode2-v2/m2v2-s02b-slab-added.png"),
    dict(id="TC-E2E-M2-03", scenario="เช็ค Analytic Distribution แล้วยืนยัน (Confirm) Sale Order",
         pre="ทำ TC-E2E-M2-02 เสร็จแล้ว",
         steps=["เปิดคอลัมน์ \"Analytic Distribution\" ถ้ายังไม่เห็น (ปุ่มตัวเลือกคอลัมน์มุมขวาบนตาราง)", "กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="ช่อง Analytic Distribution ต้องมีค่าติดมาอัตโนมัติแล้วตั้งแต่ก่อน Confirm (Category + Material + Block รวม 3 มิติ) — SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ", prio="High",
         shot="assets/e2e-mode2-v2/m2v2-s03b-analytic-col-before-confirm.png"),
  ]),
  dict(cat_id="E2", title="E2. ขาย (Sale — Mode 2, Lot aggregate)",
       subtitle="ADR-020 — ระบุจำนวนตร.ม.บางส่วนจากล็อต ไม่ต้องขายทั้งล็อต · 3 test cases",
       cases=[
    dict(id="TC-E2E-M2-04", scenario="เพิ่มบรรทัดสินค้า Material โหมด Lot ใน Sale Order",
         pre="มีล็อตหินสถานะ Available อยู่แล้ว จาก Material ที่ตั้ง Pricing Mode = Lot (aggregate)",
         steps=["เปิด Sales &gt; Orders &gt; New (หรือใช้ SO เดิม)", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้าของ Material โหมด Lot นี้"],
         sample="สินค้า = ดำอัฟริกา/BLACK AFRICA - Slab (Material โหมด Lot)",
         expected="เพิ่มบรรทัดสำเร็จ ปุ่ม \"Select Lot Stock\" ปรากฏบนบรรทัดนั้นแทนที่จะเป็น \"Select Slabs\"", prio="Medium",
         shot="assets/e2e-mode2-v2/m2v2-l01-so-line-added.png"),
    dict(id="TC-E2E-M2-05", scenario="กด \"Select Lot Stock\" ระบุจำนวนตร.ม.บางส่วนจากล็อต",
         pre="ทำ TC-E2E-M2-04 เสร็จแล้ว",
         steps=["กดปุ่ม \"Select Lot Stock\" บนบรรทัด", "เลือก Bundle ที่ต้องการในช่อง \"Lot (Block)\" — ระบบแสดงจำนวนตร.ม.ที่เหลืออยู่ให้ทันที", "กรอก \"Quantity to Sell (Sq.Mt.)\" เป็นจำนวนบางส่วน (ไม่จำเป็นต้องขายทั้งล็อต)", "กด \"Confirm Selection\""],
         sample="Lot = BLK-26-0047 (เหลือ 6.00 ตร.ม. เต็มล็อต)<br>Quantity to Sell (Sq.Mt.) = 2.00",
         expected="บรรทัด SO ผูก Lot ถูกต้อง จำนวน/ราคารวมปรับตาม 2.00 ตร.ม. ที่เลือกทันที (ตัวอย่างจริง: 2.00 &times; 4,000/ตร.ม. = 8,000) ไม่มีการเลือกแผ่นเดี่ยวใดๆ", prio="High",
         shot="assets/e2e-mode2-v2/m2v2-l03-qty-entered.png"),
    dict(id="TC-E2E-M2-06", scenario="เช็ค Analytic Distribution แล้วยืนยัน (Confirm) Sale Order โหมด Lot",
         pre="ทำ TC-E2E-M2-05 เสร็จแล้ว",
         steps=["เปิดคอลัมน์ \"Analytic Distribution\" ถ้ายังไม่เห็น", "กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="ช่อง Analytic Distribution มีค่าติดมาอัตโนมัติเหมือนโหมด Serial — SO เปลี่ยนสถานะเป็น Sales Order มี Delivery Order เกิดขึ้นอัตโนมัติ 1 ใบ — ตัวอย่างจริง: S00111 ส่วนที่เหลือของล็อตเดิม (4.00 ตร.ม.) ยังคงพร้อมขายต่อได้ตามปกติ", prio="High",
         shot="assets/e2e-mode2-v2/m2v2-l04b-analytic-col.png"),
  ]),
  dict(cat_id="E3", title="E3. จัดส่ง (Delivery — Scan Verification)",
       subtitle="ADR-009 — ต้องสแกน/กรอก Serial ให้ตรงก่อน Validate เสมอ ใช้ร่วมกันทั้ง Serial และ Lot · 2 test cases",
       cases=[
    dict(id="TC-E2E-M2-07", scenario="พยายาม Validate ใบส่งของโดยยังไม่กรอก Scanned Serial ให้ตรง",
         note="หมายเหตุ: กันส่งแผ่น/ล็อตผิดให้ลูกค้าโดยไม่ได้ตรวจสอบก่อน (ADR-009) — ใช้ตรรกะเดียวกันไม่ว่าเป็นบรรทัด Serial หรือ Lot ยืนยันแล้วทั้งคู่จริงในรอบนี้ (ไม่ใช่แค่ Serial แบบ v1)",
         pre="ทำ TC-E2E-M2-03 หรือ TC-E2E-M2-06 เสร็จแล้ว มีใบส่งของสถานะ Ready รออยู่",
         steps=["เปิดใบส่งของ (Delivery) ที่เกิดขึ้นอัตโนมัติ", "กดปุ่ม Validate ทันทีโดยยังไม่กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial/Lot ที่จองไว้"],
         sample="-",
         expected="ระบบฟ้อง error สองภาษาทันที: \"สแกน Serial ไม่ตรง กรุณาสแกนให้ครบก่อน Validate\" พร้อมระบุชื่อ Serial/Lot ที่ยังไม่ตรง บันทึกไม่ผ่าน", prio="High",
         shot="assets/e2e-mode2-v2/m2v2-s06-delivery-scan-error.png",
         shot_note="ภาพจากเส้นทาง Serial — เส้นทาง Lot เจอ error หน้าตาเดียวกัน (ดู EG01/OUT/00078)"),
    dict(id="TC-E2E-M2-08", scenario="กรอก/สแกน Scanned Serial ให้ตรงครบทุกบรรทัดแล้ว Validate",
         pre="ทำ TC-E2E-M2-07 เสร็จแล้ว (เจอ error มาก่อน)",
         steps=["กด \"Details\" ที่บรรทัดสินค้า", "กรอกช่อง \"Scanned Serial\" ให้ตรงกับ Serial/Lot ที่จองไว้จริง แล้วกด Save", "กดปุ่ม Validate อีกครั้ง"],
         sample="Scanned Serial (Serial path) = BLK-26-0050-1<br>Scanned Serial (Lot path) = BLK-26-0047-LOT",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done สำเร็จ — แผ่น/ปริมาณที่ขายหายจากสต็อกที่ขายได้ (Available) แล้ว", prio="High",
         shot="assets/e2e-mode2-v2/m2v2-s08-delivery-done.png"),
  ]),
  dict(cat_id="E4", title="E4. บัญชี (Accounting + Payment)",
       subtitle="ออกใบแจ้งหนี้ + รับชำระเงิน + ตรวจรายการบัญชี · 5 test cases",
       cases=[
    dict(id="TC-E2E-M2-09", scenario="สร้างและยืนยันใบแจ้งหนี้ลูกค้า (Customer Invoice)",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Regular invoice\" &gt; Create Draft Invoice", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="-",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดรวมตรงกับ SO รวม VAT — ตัวอย่างจริง Lot: INV/2026/00009 (8,560.00)", prio="High",
         shot="assets/e2e-mode2-v2/m2v2-l11-invoice-posted.png"),
    dict(id="TC-E2E-M2-10", scenario="รับชำระเงิน (Register Payment) บนใบแจ้งหนี้",
         pre="ทำ TC-E2E-M2-09 เสร็จแล้ว (Invoice = Posted)",
         steps=["เปิดใบแจ้งหนี้ &gt; กด \"Pay\"", "ตรวจ/ยืนยันยอดและวิธีชำระ &gt; กด Create Payment"],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นสถานะ \"Paid\" (Payment Status) — ตัวอย่างจริงทั้งคู่ (INV/2026/00008, INV/2026/00009) จบที่สถานะ Posted + Paid", prio="Medium",
         shot="assets/e2e-mode2-v2/m2v2-s11-invoice-paid.png"),
    dict(id="TC-E2E-M2-11", scenario="ตรวจรายการบัญชีบนใบแจ้งหนี้ (รายได้ + VAT + ลูกหนี้ + บัญชี)",
         note="✅ แก้บั๊กจริงแล้ว (2026-09-09): ก่อนหน้านี้ Serial-mode ทุกเคสลงบัญชีรายได้ผิดเป็นของ Mode 3 (Cut-to-Order) — เจอจากการทดสอบนี้เอง แก้ไขที่โค้ด (สร้างบัญชีใหม่ \"Sales Revenue - Serial Slab Sale (Mode 2)\") และ verify แล้วว่าเคสใหม่ๆ ขึ้นบัญชีถูกต้องเองอัตโนมัติ ไม่ต้องแก้มือ",
         pre="ทำ TC-E2E-M2-09 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="บรรทัดรายได้ต้องขึ้นบัญชีถูกโหมด — Serial = \"Sales Revenue - Serial Slab Sale (Mode 2)\", Lot = \"Sales Revenue - Lot Material (Mode 2)\" — พร้อม Analytic Distribution ครบ ตรงกับใน SO", prio="High",
         shot="assets/e2e-mode2-v2/m2v2-l12-invoice-journal-items.png",
         shot_note="ภาพตัวอย่าง Lot (INV/2026/00009) — ตัวอย่าง Serial (INV/2026/00008) ดูได้จาก TC-E2E-M2-12"),
    dict(id="TC-E2E-M2-12", scenario="ตรวจว่า Serial-mode ลงบัญชีต้นทุนขาย (COGS) ถูกต้องหรือไม่",
         note="✅ แก้บั๊กจริงแล้ว (2026-09-09): ก่อนหน้านี้แทบทุก Bundle ในระบบ (ที่ไม่ได้สร้างผ่าน Session นี้) ไม่เคยมีต้นทุนจริงถูกฝังเข้าไปในระบบ valuation ของ Odoo เลย (ทั้งที่ตัวเลขต้นทุนในโมดูลเองถูกต้องอยู่แล้ว) ทำให้ COGS ออกมาเป็น 0 บาททุกครั้ง — backfill ต้นทุนที่ขาดหายทั้งระดับ Block และระดับ Slab (แยกกันคนละจุด) ทั้ง 2 ฐานข้อมูลแล้ว ยืนยันด้วย live test จริงว่า COGS ขึ้นถูกต้อง",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว (Delivery = Done), ใช้ Invoice ฝั่ง Serial (INV/2026/00008)",
         steps=["เปิด Customer Invoice ฝั่ง Serial &gt; กด smart button \"Journal Items\""],
         sample="-",
         expected="เห็นคู่ COGS/Inventory แนบอัตโนมัติบนใบแจ้งหนี้ใบเดียวกัน (เดบิต \"COGS - Stone Sales (all modes)\" / เครดิต \"Inventory - Stone Blocks (Raw)\") พร้อม Analytic Distribution ตรงกับบรรทัดรายได้ — ตัวอย่างจริง INV/2026/00008: 9,000.00 ทั้งคู่ (ราคาขายของ Material ตัวอย่างนี้บังเอิญยังไม่ได้ตั้งไว้เลยโชว์รายได้ 0 — ไม่เกี่ยวกับ COGS ที่กำลังเช็ค)", prio="High",
         shot="assets/e2e-mode2-v2/m2v2-s10-invoice-journal-items.png"),
    dict(id="TC-E2E-M2-12b", scenario="⚠️ ตรวจ Lot-mode COGS — ยังไม่ผ่าน (known issue เปิดอยู่)",
         note="⚠️ พบบั๊กจริง ยังไม่ได้แก้ (2026-09-09): ต่างจาก Serial-mode ข้างบน โหมด Lot ยังโพสต์ COGS เป็น 0 อยู่ แม้ backfill ต้นทุนแล้ว — ตรวจโค้ดพบว่า FIFO layer ที่รับเข้ามา (มีมูลค่าจริงถูกต้อง) ไม่ถูกดึงมาใช้ตอนส่งของเลย (remaining quantity ไม่ลดลงหลังขายจริง) สาเหตุที่แท้จริงยังไม่พบ ต้องสืบเพิ่มอีก Session หน้า",
         pre="ทำ TC-E2E-M2-08 เสร็จแล้ว (Delivery = Done), ใช้ Invoice ฝั่ง Lot (INV/2026/00009)",
         steps=["เปิด Customer Invoice ฝั่ง Lot &gt; กด smart button \"Journal Items\"", "เทียบกับ TC-E2E-M2-11/12 ฝั่ง Serial"],
         sample="-",
         expected="(ยังไม่ผ่าน) ตัวอย่างจริง INV/2026/00009: มีแค่บรรทัดรายได้/VAT/ลูกหนี้ — ไม่มีคู่ COGS/Inventory เลย ทั้งที่ Material นี้ตั้งค่าเป็น real_time/FIFO เหมือนกับฝั่ง Serial", prio="Medium",
         shot="assets/e2e-mode2-v2/m2v2-l12-invoice-journal-items.png"),
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
