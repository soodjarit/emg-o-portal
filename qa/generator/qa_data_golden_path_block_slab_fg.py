# Single source of truth for EMG-O Golden Path test cases — "Block → Slab →
# Finished Goods" flow, rebuilt end-to-end after ADR-071/072/073 (2026-09-25).
#
# Why this doc exists: ADR-071 (Block W x L x H -> computed Total CBM/Weight,
# Thickness/Finish removed from Block entirely), ADR-072 (Thickness/Finish
# moved to per-Slab attributes, resolved to a real product.product Variant),
# and ADR-073 (FG production spec-matches an available Slab by Finish +
# Thickness instead of matching any Slab of the Material regardless of spec)
# changed this flow enough that every previous Golden Path doc covering it
# (Mode 3 Cut-to-Order, Mode 5 FG Production) is now conceptually stale —
# archived by the user 2026-09-26, this is a from-scratch rebuild, not a
# refresh. Extended same week to also cover Material/pricing setup and the
# other 2 sale modes (whole-Block, ready-made Slab, BOQ/Project) once the
# user asked whether those still needed re-validation after the same redesign.
#
# Golden Path discipline (see feedback_golden_path_test_case memory): happy
# path only, no field-validation/error cases, full lifecycle end to end
# (purchase -> receive Block -> sell -> produce -> deliver -> invoice), every
# step phrased so a non-technical user can follow it with no backend
# knowledge.
#
# Data provenance: fresh live run built specifically for this file, driven
# through the real Odoo web UI (Playwright, headless Chromium) on `eg-tst`
# (client-facing test DB), 2026-09-26, hitting the real business methods
# (action_confirm(), action_stone_mark_done(), the MO's own "Move to
# Production"/Confirm/"Complete FG Production" buttons, stock.picking.
# button_validate(), account.move.action_post(), boq.document.
# action_generate_quotation()) — never a raw model write bypassing real
# logic (2 exceptions, both noted inline below: the BOQ Rate/Document/Line
# for SETUP2/MODE3 were created via env[].create() in an `odoo shell` run
# instead of clicking through the Rate Library's inline-edit grid, after
# that grid's cell layout proved unreliable to drive blind; the resulting
# SO/Project/Delivery/Invoice were still driven for real through the browser):
#
#   SETUP — Quick Material Setup Wizard, filled in full (name/category/
#   density/has_block ticked), with Finish=Polished+Honed and Thickness=
#   2cm+3cm already pre-ticked (2026-09-26 default), PLUS Brushed and 5cm
#   ticked on top as the "need something extra" case -> Create All ->
#   Material "E2E GP Test Marble" (Marble, Serial, density 2.65) with a
#   9-variant Slab product (3 Finish x 3 Thickness) and a Block product, no
#   collisions. Then, on the Slab template's own Attributes & Variants tab
#   (Configure > Product Variant Values), set Honed Extra Price = -800 and
#   Brushed = +500 -> Polished 9,000 (base) / Honed 8,200 / Brushed 9,500
#   confirmed on the real Product Variants list.
#
#   G1-G4 (core Block->Slab->FG lifecycle) — PO P00133 (EMG-test, 2.40 CBM
#   Block product @ 6,666.67/ton = 43,200 + VAT 3,024 = 46,224.00) -> Confirm
#   -> "สร้าง Block" -> 1.00 x 2.00 x 1.20 m -> Block BLK-26-0266 (Total CBM
#   2.40, Weight 6.48 both auto-computed, density 2.7) -> SO S00320 (QA-A B2C
#   Test User) -> "ดำซานซี/ABSOLUTE BLACK" -> Configure your Product (Finish/
#   Thickness) -> default Polished/2cm, qty 2 -> Confirm at 25,680.00 (incl.
#   VAT) -> "Produce FG" -> MO EG01/STFG/00057 auto-matches Slab BLK-26-0265
#   #3 (already-existing stock, exact spec match, ADR-073) -> Move to
#   Production -> Confirm -> FG Output (1.00x2.00m, 0.02m, qty 2) -> Complete
#   FG Production (Done) -> Delivery EG01/OUT/00179 (Done) -> Invoice
#   INV/2026/00001 (25,680.00, Posted, "411150 Sales Revenue - FG
#   Production", 3-dim Analytic). Finish/Thickness price deltas verified
#   live in the same Configure-product popup: Polished/2cm=12,000 (base),
#   Honed/2cm=11,000, Polished/3cm=18,000, Honed/3cm=17,000.
#
#   MODE1 (Sale Mode 1 — ขายทั้งก้อน Block) — PO P00134 (E2E GP Test Marble
#   Block, 1.8 CBM) -> Confirm -> Block BLK-26-0268 (1.50x1.00x1.20m, Total
#   CBM 1.80, Weight 4.77, Sales Price/CBM manually set to 50,000 since this
#   Material supports whole-block sale) -> SO S00321, added the Block product
#   directly -> "Sell Whole Block" button -> Select Block wizard -> picked
#   BLK-26-0268 -> qty/price auto-filled from its remaining CBM (1.80 x
#   50,000 = 90,000) -> Confirm at 96,300.00 (incl. VAT) -> Delivery (Done)
#   -> Invoice INV/2026/00002 (96,300.00, Posted, "411110 Sales Revenue -
#   Block").
#
#   MODE2 (Sale Mode 2 — ขาย Slab พร้อมขายที่มีสต็อกอยู่แล้ว) — SO S00323,
#   added "ดำซานซี/ABSOLUTE BLACK - Slab (Polished)" directly (the raw Slab
#   product, is_stone_material, not the FG product used in G1-G4) -> "Select
#   Slabs" button -> Add a line -> candidate list correctly pre-filtered to
#   80 real Available Polished/2cm slabs only (ADR-072's variant_id domain,
#   never live-tested before today) -> picked 3 (BLK-26-0265 #4/#5/#6) ->
#   Confirm Selection -> SO qty/price auto-updated to 61,632.00 (incl. VAT)
#   -> Confirm -> Delivery (required a physical Scanned Serial match per
#   line before Validate would accept it — ADR-009's own safeguard against
#   shipping the wrong physical slab, satisfied here by keying in each
#   slab's serial) -> Invoice INV/2026/00003 (61,632.00, Posted).
#
#   MODE3 (Sale Mode 3 — ขายแบบ BOQ/Project) — new Rate Library item
#   "[GP-TEST-01] Countertop Slab" (Material 8,000 + Labour 1,000 = 9,000/
#   unit, linked to the E2E GP Test Marble Slab product) -> BOQ Document
#   BOQ0041 (1 line, qty 2, 18,000 direct cost + 1,800 Overhead & Profit 10%
#   = 19,800) -> "สร้างใบเสนอราคา" -> SO S00324 -> ticked "Sold as Project"
#   (Other Info tab) -> Confirm (hard-confirmation warning accepted, no cut
#   Slab stock existed yet for this brand-new test Material) -> Project 34
#   ("QA-A B2C Test User - S00324") auto-created with 2 Tasks (one per order
#   line, incl. the BOQ Summary overhead line) — confirms the BOQ->Project
#   auto-creation mechanism is unaffected by ADR-071/072/073, matching the
#   code-read finding that boq_estimation never references finish_key/
#   thickness_key directly. Delivery/Invoice not re-executed for this specific
#   fixture (no real cut Slab existed for this brand-new Material to ship) —
#   already proven identical/working via G4 and MODE2 above, not a gap in
#   Mode 3 itself.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low), shot (screenshot path)

CATEGORIES = [
  dict(cat_id="S1", title="S1. ตั้งค่า Material ใหม่ (Setup)",
       subtitle="Quick Material Setup Wizard — Finish/Thickness มาตรฐานติ๊กไว้ให้อัตโนมัติ เพิ่มนอกเหนือได้ในหน้าเดียว · 3 test cases",
       cases=[
    dict(id="TC-GP-BSF-01", scenario="เปิด Quick Material Setup Wizard กรอกข้อมูล Material ใหม่ให้ครบ",
         note="✨ 2026-09-26: Finish (Polished/Honed) และ Thickness (2cm/3cm) ติ๊กไว้ให้อัตโนมัติล่วงหน้าแล้ว ไม่ต้องเลือกเอง",
         pre="ไม่มี — เปิดจากเมนูได้ทันที",
         steps=["เปิด Stone Slab &gt; Tools &gt; Quick Material Setup", "กรอกชื่อ Material, Category, Density", "ติ๊ก \"ขายทั้งก้อนได้\" ถ้า Material นี้ขายทั้งก้อนได้ด้วย"],
         sample="ชื่อ = E2E GP Test Marble<br>Category = Marble<br>Density = 2.65 ตัน/คิว",
         expected="เห็น Finish (Polished, Honed) และ Thickness (2cm, 3cm) ติ๊กไว้ให้อัตโนมัติแล้วในตาราง Finish/มุม/Thickness ด้านล่าง", prio="High",
         shot="assets/golden-path-block-slab-fg/gp14-material-wizard-filled.png"),
    dict(id="TC-GP-BSF-02", scenario="ติ๊กเพิ่ม Finish/Thickness นอกเหนือจากค่ามาตรฐาน",
         note="ถ้า Material นี้ต้องการตัวเลือกที่ไม่ใช่ค่ามาตรฐาน (เช่น Brushed, 5cm) แค่ติ๊กเพิ่มในหน้าเดียวกัน ไม่ต้องไปตั้งค่าที่อื่น",
         pre="ทำ TC-GP-BSF-01 เสร็จแล้ว",
         steps=["ติ๊กเพิ่มค่า Finish/Thickness ที่ต้องการนอกเหนือจากที่ติ๊กไว้ให้แล้ว"],
         sample="ติ๊กเพิ่ม: Finish = Brushed, Thickness = 5 cm",
         expected="ค่าที่ติ๊กเพิ่มแสดงเป็นเลือกแล้ว (สีเขียว) อยู่ร่วมกับค่ามาตรฐานที่ติ๊กไว้ก่อนหน้า", prio="Medium",
         shot="assets/golden-path-block-slab-fg/gp15-material-wizard-extra-ticked.png"),
    dict(id="TC-GP-BSF-03", scenario="กด \"Create All\" สร้าง Material พร้อม Slab/Block Product ทุก Variant",
         pre="ทำ TC-GP-BSF-02 เสร็จแล้ว",
         steps=["กดปุ่ม \"Create All\""],
         sample="-",
         expected="ได้ Material ใหม่พร้อม Slab Product ที่มี Variant ครบทุกค่าที่เลือก (มาตรฐาน + ที่เพิ่มเอง) รหัสสินค้าไม่ชนกัน — ตัวอย่างจริง: \"E2E GP Test Marble\" ได้ 9 variant (Polished/Honed/Brushed × 2cm/3cm/5cm) พร้อม Block Product เชื่อมให้แล้ว", prio="High",
         shot="assets/golden-path-block-slab-fg/gp16-material-created.png"),
  ]),
  dict(cat_id="S2", title="S2. ตั้งราคาต่างกันตาม Finish/Thickness (Setup)",
       subtitle="ฝั่งแอดมิน — ปรับราคาส่วนต่างแยกตามค่า Finish/Thickness ให้สินค้าที่มีอยู่แล้ว · 1 test case",
       cases=[
    dict(id="TC-GP-BSF-04", scenario="เปิดหน้า Product Variant Values ของ Slab Product ปรับราคาส่วนต่างตาม Finish",
         pre="มี Material ที่มี Finish/Thickness มากกว่า 1 ค่าแล้ว (เช่น จาก S1)",
         steps=["เปิด Slab Product &gt; แท็บ Attributes &amp; Variants", "กด \"Configure\" ที่แถว Finish", "เลือกค่าที่ต้องการปรับราคา กรอก Extra Price", "Save"],
         sample="Honed Extra Price = -800 บาท (ถูกกว่า Polished)<br>Brushed Extra Price = +500 บาท (แพงกว่า Polished)",
         expected="ราคาขายจริงของแต่ละ Variant คำนวณใหม่ถูกต้องทันที — ตัวอย่างจริง: Polished 9,000 (ฐาน), Honed 8,200, Brushed 9,500 บาท (ทุก Thickness ในกลุ่มเดียวกัน)", prio="Medium",
         shot="assets/golden-path-block-slab-fg/gp19-variants-computed-prices.png"),
  ]),
  dict(cat_id="G1", title="G1. จัดซื้อ + รับ Block เข้าคลัง (ADR-071)",
       subtitle="Block กรอกแค่ กว้าง×ยาว×สูง ระบบคำนวณ CBM/น้ำหนักให้อัตโนมัติ ไม่ต้องคีย์เอง · 3 test cases",
       cases=[
    dict(id="TC-GP-BSF-05", scenario="สร้าง Purchase Order สั่งซื้อ Block จาก Supplier แล้ว Confirm",
         pre="มี Material ที่ตั้งค่า Block Product ไว้แล้ว (เช่น ดำซานซี/ABSOLUTE BLACK)",
         steps=["เปิด Purchase &gt; New", "เลือก Vendor", "Add a product เลือกสินค้า Block ของ Material ที่ต้องการ", "กรอก Quantity (คิว/CBM ที่ซื้อจริง)", "กด Confirm Order"],
         sample="Vendor = EMG-test<br>สินค้า = ดำซานซี/ABSOLUTE BLACK - Block<br>Quantity = 2.40 (คิว)",
         expected="PO ยืนยันสำเร็จ ระบบคำนวณ Qty(Ton)/Price-per-Ton ให้อัตโนมัติจากความหนาแน่นของ Material — ตัวอย่างจริง: P00133, ยอดรวม 46,224.00 บาท (รวม VAT)", prio="High",
         shot="assets/golden-path-block-slab-fg/gp01-po-confirmed.png"),
    dict(id="TC-GP-BSF-06", scenario="กดปุ่ม \"สร้าง Block\" บนบรรทัดของ PO",
         pre="ทำ TC-GP-BSF-05 เสร็จแล้ว (PO ต้องอยู่สถานะ Confirmed)",
         steps=["บนบรรทัดสินค้าของ PO กดปุ่ม \"สร้าง Block\""],
         sample="-",
         expected="เปิดฟอร์ม Block ใหม่ทันที โดยกรอก Material/Supplier/Warehouse/Company/Purchase Order Line ให้อัตโนมัติจาก PO — เหลือแค่กรอกขนาดจริง", prio="High",
         shot="assets/golden-path-block-slab-fg/gp02-block-form-prefilled.png"),
    dict(id="TC-GP-BSF-07", scenario="กรอกขนาดก้อนจริง (กว้าง×ยาว×สูง) แล้ว Save — ระบบคำนวณ CBM/น้ำหนักให้อัตโนมัติ",
         note="✨ ADR-071: Block ไม่มีช่อง Thickness/Finish อีกต่อไป — กรอกแค่ 3 มิติ ระบบคำนวณ Total CBM (=กว้าง×ยาว×สูง) และ Weight (Ton) (=CBM×ความหนาแน่น) ให้เองทั้งคู่ ไม่ต้องคีย์เลย",
         pre="ทำ TC-GP-BSF-06 เสร็จแล้ว",
         steps=["กรอกความยาวก้อนดิบ (ม.)", "กรอกความกว้างก้อนดิบ (ม.)", "กรอกความสูงก้อนดิบ (ม.)", "กด Save"],
         sample="ความยาว = 2.00 ม.<br>ความกว้าง = 1.00 ม.<br>ความสูง = 1.20 ม.",
         expected="Total CBM และ Weight (Ton) ขึ้นให้อัตโนมัติ ไม่ต้องพิมพ์เอง — ตัวอย่างจริง: BLK-26-0266, Total CBM = 2.40, Weight (Ton) = 6.48 (2.40 × 2.7)", prio="High",
         shot="assets/golden-path-block-slab-fg/gp03-block-cbm-weight-computed.png"),
  ]),
  dict(cat_id="G2", title="G2. ขาย — เลือก Finish/Thickness ตอนสร้าง Sale Order (ADR-072)",
       subtitle="Finish/Thickness เป็นของแต่ละ Slab ไม่ใช่ของ Block อีกต่อไป ราคาต่างกันได้จริงตามที่เลือก · 3 test cases",
       cases=[
    dict(id="TC-GP-BSF-08", scenario="สร้าง Sale Order เพิ่มสินค้าหิน — ระบบเปิดหน้าต่างให้เลือก Finish/Thickness",
         pre="มีลูกค้าและสินค้าหิน (FG) ที่ผูกกับ Material พร้อมแล้ว",
         steps=["เปิด Sales &gt; New", "เลือกลูกค้า", "Add a product เลือกสินค้าหิน (เช่น ดำซานซี/ABSOLUTE BLACK)"],
         sample="ลูกค้า = QA-A B2C Test User<br>สินค้า = ดำซานซี/ABSOLUTE BLACK",
         expected="หน้าต่าง \"Configure your product\" เปิดขึ้นให้เลือก Finish (Polished/Honed) และ Thickness (2cm/3cm) พร้อมราคารวมที่อัปเดตตามที่เลือกทันที", prio="High",
         shot="assets/golden-path-block-slab-fg/gp04-so-configurator-opens.png"),
    dict(id="TC-GP-BSF-09", scenario="ยืนยัน Finish/Thickness ที่ต้องการ — ราคาต่างกันจริงตามตัวเลือก",
         note="ตั้งราคาต่างกันตาม Finish/Thickness ผ่าน price_extra ของแต่ละค่า (native Odoo variant pricing, ตั้งค่าไว้ที่ S2) — หน้าต่างเลือกโชว์ป้ายราคาส่วนต่างให้เห็นเลยว่าเลือกแล้วแพง/ถูกลงเท่าไร",
         pre="เปิดหน้าต่าง Configure your product จาก TC-GP-BSF-08 แล้ว",
         steps=["เลือก Finish ที่ต้องการ (Polished/Honed)", "เลือก Thickness ที่ต้องการ (2cm/3cm)", "สังเกตราคารวมที่มุมขวาบน", "กด Confirm"],
         sample="Base (Polished, 2cm) = 12,000 บาท",
         expected="ราคาต่างกันจริงตามตัวเลือก — ตัวอย่างจริง: Polished/2cm=12,000, Honed/2cm=11,000 (ป้าย \"-1,000\"), Polished/3cm=18,000 (ป้าย \"+6,000\"), Honed/3cm=17,000 บาท", prio="Medium",
         shot="assets/golden-path-block-slab-fg/gp05-finish-thickness-price-delta.png"),
    dict(id="TC-GP-BSF-10", scenario="กด Confirm ยืนยัน Sale Order",
         pre="ทำ TC-GP-BSF-09 เสร็จแล้ว (มีบรรทัดสินค้าหินพร้อม Finish/Thickness ที่เลือกแล้ว)",
         steps=["กดปุ่ม Confirm บนหัว Sale Order"],
         sample="-",
         expected="SO ยืนยันสำเร็จ เปลี่ยนสถานะเป็น Sales Order มีสมาร์ทปุ่ม Delivery ปรากฏ และลิงก์ \"Produce FG\" บนบรรทัดสินค้า — ตัวอย่างจริง: S00320, ยอดรวม 25,680.00 บาท (รวม VAT)", prio="High",
         shot="assets/golden-path-block-slab-fg/gp06-so-confirmed.png"),
  ]),
  dict(cat_id="G3", title="G3. ผลิต FG ตาม Spec ที่ลูกค้าสั่ง (ADR-073)",
       subtitle="ระบบหา Slab ที่ Finish/Thickness ตรงกับที่ลูกค้าสั่งให้อัตโนมัติ ไม่ต้องเลือกเอง · 4 test cases",
       cases=[
    dict(id="TC-GP-BSF-11", scenario="กดลิงก์ \"Produce FG\" บนบรรทัดสินค้าใน Sale Order",
         note="✨ ADR-073: ระบบค้นหา Slab ที่มี Finish/Thickness ตรงกับที่ลูกค้าสั่งให้อัตโนมัติ (ไม่ใช่ Slab ของ Material นั้นแบบสุ่มๆ) — ถ้าลูกค้าเคยเลือก Slab แผ่นใดแผ่นหนึ่งไว้ล่วงหน้าแล้ว ระบบจะเคารพแผ่นนั้นก่อนเสมอ",
         pre="ทำ TC-GP-BSF-10 เสร็จแล้ว",
         steps=["กดลิงก์ \"Produce FG\" บนบรรทัดสินค้า"],
         sample="-",
         expected="เปิดหน้า Manufacturing Order ฉบับร่างทันที ช่อง \"Slab Consumed (FG)\" เติมให้อัตโนมัติเป็นแผ่นที่มี Finish/Thickness ตรงกับที่ลูกค้าสั่ง — ตัวอย่างจริง: MO EG01/STFG/00057, Slab = BLK-26-0265 #3 (Polished, 2cm ตรงกับที่ลูกค้าสั่งเป๊ะ)", prio="High",
         shot="assets/golden-path-block-slab-fg/gp07-produce-fg-auto-matched-slab.png"),
    dict(id="TC-GP-BSF-12", scenario="กด \"ย้ายด่วน (Move to Production)\" แล้ว Confirm ใบสั่งผลิต",
         pre="ทำ TC-GP-BSF-11 เสร็จแล้ว",
         steps=["กดปุ่ม \"ย้ายด่วน (Move to Production)\"", "กดปุ่ม Confirm"],
         sample="-",
         expected="Slab ที่ระบบจับคู่ให้ถูกย้ายไปสถานีผลิต (Stone Production) สำเร็จ ไม่มี error เรื่องหาสต็อกไม่เจอ แล้ว Confirm ผ่านทันที สถานะ Component Status ขึ้นเป็น Available", prio="High",
         shot="assets/golden-path-block-slab-fg/gp08-move-to-production-confirm.png"),
    dict(id="TC-GP-BSF-13", scenario="บันทึกขนาดที่ตัดได้จริงในแท็บ \"FG Output\"",
         pre="ทำ TC-GP-BSF-12 เสร็จแล้ว",
         steps=["ไปแท็บ \"FG Output\"", "กด Add a line", "กรอกความกว้าง/ยาว/หนา/จำนวนที่ตัดได้จริง"],
         sample="Width = 1.00 ม.<br>Length = 2.00 ม.<br>Thickness = 0.02 ม.<br>Qty = 2",
         expected="บันทึกแถวผลผลิตจริงสำเร็จ พร้อมให้กด Complete FG Production ต่อได้", prio="Medium",
         shot="assets/golden-path-block-slab-fg/gp09-fg-output-filled.png"),
    dict(id="TC-GP-BSF-14", scenario="กด \"Complete FG Production\" ปิดงานผลิต",
         pre="ทำ TC-GP-BSF-13 เสร็จแล้ว",
         steps=["กดปุ่ม \"Complete FG Production\""],
         sample="-",
         expected="MO เปลี่ยนสถานะเป็น Done มีข้อความแจ้งผลิตสำเร็จตามจำนวนที่กรอก — ตัวอย่างจริง: \"ผลิตสำเร็จ 2.00 หน่วย\"", prio="High",
         shot="assets/golden-path-block-slab-fg/gp10-complete-fg-production-done.png"),
  ]),
  dict(cat_id="G4", title="G4. ส่งของ + วางบิล",
       subtitle="ขั้นตอนมาตรฐานของ Odoo ไม่มีอะไรเปลี่ยนจาก concept เดิม · 2 test cases",
       cases=[
    dict(id="TC-GP-BSF-15", scenario="Validate ใบส่งของ (Delivery)",
         pre="ทำ TC-GP-BSF-14 เสร็จแล้ว",
         steps=["เปิดสมาร์ทปุ่ม \"Delivery\" จาก Sale Order", "กดปุ่ม Validate"],
         sample="-",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done จำนวนที่ส่งตรงกับที่ผลิตได้ — ตัวอย่างจริง: EG01/OUT/00179, 2.00/2.00", prio="Medium",
         shot="assets/golden-path-block-slab-fg/gp11-delivery-validated.png"),
    dict(id="TC-GP-BSF-16", scenario="สร้างและ Post ใบแจ้งหนี้ (Invoice)",
         pre="ทำ TC-GP-BSF-15 เสร็จแล้ว",
         steps=["กลับไปที่ Sale Order กดปุ่ม \"Create Invoice\"", "เลือก \"Regular invoice\" กด Create Draft", "กดปุ่ม Confirm เพื่อ Post ใบแจ้งหนี้"],
         sample="-",
         expected="ใบแจ้งหนี้ Post สำเร็จ ยอดตรงกับ Sale Order — ตัวอย่างจริง: INV/2026/00001, 25,680.00 บาท, ลงบัญชี \"411150 Sales Revenue - FG Production\" พร้อม Analytic tag ครบ 3 มิติ (Material/Block/หมวดหิน)", prio="High",
         shot="assets/golden-path-block-slab-fg/gp12-invoice-posted.png"),
  ]),
  dict(cat_id="M1", title="M1. โหมดขาย 1 — ขายทั้งก้อน Block (Block Direct Sale)",
       subtitle="ไม่มีการตัด Slab เลย ขาย Block ทั้งก้อนตรงๆ ราคาคิดจาก CBM จริง · 3 test cases",
       cases=[
    dict(id="TC-GP-BSF-17", scenario="เพิ่มสินค้า Block ลงบรรทัด Sale Order แล้วกด \"Sell Whole Block\"",
         pre="มี Block พร้อมขายอยู่แล้ว (ทำตามขั้นตอน G1 ก่อน — ตั้ง Sales Price/CBM ให้ Block ด้วยถ้า Material นี้เพิ่งสร้างใหม่)",
         steps=["เปิด Sales &gt; New เลือกลูกค้า", "Add a product เลือกสินค้า Block โดยตรง (ไม่ใช่ Slab/FG)", "Save", "กดปุ่ม \"Sell Whole Block\" บนบรรทัด"],
         sample="สินค้า = E2E GP Test Marble - Block",
         expected="หน้าต่าง \"Select Block\" เปิดขึ้นให้เลือก Block ก้อนที่จะขาย", prio="High",
         shot="assets/golden-path-block-slab-fg/gp20-mode1-block-created.png"),
    dict(id="TC-GP-BSF-18", scenario="เลือก Block ที่จะขาย — ราคา/จำนวนคำนวณจาก CBM จริงให้อัตโนมัติ",
         pre="ทำ TC-GP-BSF-17 เสร็จแล้ว",
         steps=["เลือก Block ที่ต้องการจากช่อง Block", "กด Confirm Selection", "กลับมาที่ Sale Order กด Confirm"],
         sample="Block = BLK-26-0268 (คงเหลือ 1.80 คิว)",
         expected="Quantity เติมเป็น CBM ที่เหลือของ Block ให้อัตโนมัติ ราคารวมคำนวณจาก Sales Price/CBM × CBM — ตัวอย่างจริง: SO S00321, 1.80 × 50,000 = 90,000 บาท (ก่อน VAT) ยืนยันสำเร็จที่ 96,300.00 บาท", prio="High",
         shot="assets/golden-path-block-slab-fg/gp21-mode1-sell-whole-block.png"),
    dict(id="TC-GP-BSF-19", scenario="ส่งของ + วางบิล (กลไกเดียวกับ G4)",
         pre="ทำ TC-GP-BSF-18 เสร็จแล้ว",
         steps=["Validate Delivery", "Create Invoice &gt; Regular invoice &gt; Create Draft &gt; Confirm"],
         sample="-",
         expected="ส่งของและวางบิลสำเร็จเหมือน G4 ทุกประการ — ตัวอย่างจริง: Invoice INV/2026/00002, 96,300.00 บาท, ลงบัญชี \"411110 Sales Revenue - Block\"", prio="Medium",
         shot="assets/golden-path-block-slab-fg/gp22-mode1-invoice-posted.png"),
  ]),
  dict(cat_id="M2", title="M2. โหมดขาย 2 — ขาย Slab ที่มีสต็อกพร้อมขายอยู่แล้ว (Ready-Made Slab)",
       subtitle="ADR-072 domain fix — กรองเฉพาะ Slab ที่ Finish/Thickness ตรงกับที่ลูกค้าสั่งเท่านั้น (รันจริงครั้งแรกหลังแก้โค้ด) · 3 test cases",
       cases=[
    dict(id="TC-GP-BSF-20", scenario="เพิ่มสินค้า Slab (ระบุ Finish/Thickness) ลง Sale Order แล้วกด \"Select Slabs\"",
         pre="มี Slab พร้อมขายอยู่แล้วในสต็อก (Finish/Thickness ตรงกับที่จะเลือกขาย)",
         steps=["เปิด Sales &gt; New เลือกลูกค้า", "Add a product เลือกสินค้า Slab (ระบุ Finish ที่ต้องการ ไม่ใช่สินค้า FG)", "Save", "กดปุ่ม \"Select Slabs\" บนบรรทัด", "กด Add a line"],
         sample="สินค้า = ดำซานซี/ABSOLUTE BLACK - Slab (Polished)",
         expected="รายการ Slab ที่แสดงกรองเฉพาะแผ่นที่ Finish/Thickness ตรงกับสินค้าที่เลือกและสถานะ Available เท่านั้น ไม่ปนแผ่นอื่น — ตัวอย่างจริง: เจอ 80 แผ่น Polished/2cm ที่พร้อมขาย", prio="High",
         shot="assets/golden-path-block-slab-fg/gp23-mode2-select-slabs-candidates.png"),
    dict(id="TC-GP-BSF-21", scenario="เลือกแผ่นที่ต้องการ กด Confirm Selection แล้ว Confirm Sale Order",
         pre="ทำ TC-GP-BSF-20 เสร็จแล้ว",
         steps=["ติ๊กเลือกแผ่นที่ต้องการ", "กด Select แล้วกด Confirm Selection", "กลับมาที่ Sale Order กด Confirm"],
         sample="เลือก 3 แผ่น (BLK-26-0265 #4, #5, #6)",
         expected="Quantity/ราคาบนบรรทัดอัปเดตอัตโนมัติตามจำนวนแผ่นที่เลือกจริง แผ่นที่เลือกเปลี่ยนสถานะเป็น Hold ทันที — ตัวอย่างจริง: SO S00323 ยืนยันที่ 61,632.00 บาท", prio="High",
         shot="assets/golden-path-block-slab-fg/gp24-mode2-so-confirmed.png"),
    dict(id="TC-GP-BSF-22", scenario="ส่งของ + วางบิล",
         note="การส่งของ Slab ต้องกรอก \"Scanned Serial\" ให้ตรงกับ Serial จริงของแต่ละแผ่นก่อน Validate ได้ (ป้องกันส่งผิดแผ่น) — คลิก \"Details\" บนบรรทัดสินค้าเพื่อกรอก",
         pre="ทำ TC-GP-BSF-21 เสร็จแล้ว",
         steps=["เปิดสมาร์ทปุ่ม Delivery", "กด Details กรอก/ยืนยัน Serial ของแต่ละแผ่นให้ตรง", "Save แล้วกด Validate", "กลับไป Sale Order สร้าง + Post Invoice"],
         sample="-",
         expected="ส่งของและวางบิลสำเร็จ — ตัวอย่างจริง: Invoice INV/2026/00003, 61,632.00 บาท", prio="Medium",
         shot="assets/golden-path-block-slab-fg/gp25-mode2-invoice-posted.png"),
  ]),
  dict(cat_id="M3", title="M3. โหมดขาย 3 — ขายแบบ BOQ/Project (Sold-as-Project)",
       subtitle="กลไก BOQ→Project ไม่ถูกกระทบจาก ADR-071/072/073 เลย (โค้ดไม่แตะ Finish/Thickness) · 2 test cases",
       cases=[
    dict(id="TC-GP-BSF-23", scenario="สร้าง BOQ Document ใส่รายการที่ผูกกับสินค้าหินจริง แล้วสร้างใบเสนอราคา",
         pre="มี Rate Library Item ที่ผูกกับสินค้าหิน (Finish/Thickness) ที่ต้องการแล้ว",
         steps=["เปิด BOQ Estimation &gt; BOQ Documents &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัดเลือก Rate Library Item ที่ต้องการ กรอกจำนวน", "กด \"สร้างใบเสนอราคา\""],
         sample="Rate = [GP-TEST-01] Countertop Slab (9,000/หน่วย)<br>Quantity = 2",
         expected="ได้ Sale Order ใหม่ที่มีบรรทัดสินค้าจริงตรงกับ Rate ที่เลือก บวก Overhead & Profit อัตโนมัติ — ตัวอย่างจริง: BOQ0041 (18,000 + 1,800 = 19,800) → SO S00324", prio="High",
         shot="assets/golden-path-block-slab-fg/gp26-mode3-boq-document.png"),
    dict(id="TC-GP-BSF-24", scenario="ติ๊ก \"Sold as Project\" แล้ว Confirm — ระบบสร้าง Project + Task ให้อัตโนมัติ",
         pre="ทำ TC-GP-BSF-23 เสร็จแล้ว",
         steps=["เปิดแท็บ Other Info บน Sale Order", "ติ๊ก \"Sold as Project\"", "กด Confirm"],
         sample="-",
         expected="SO ยืนยันสำเร็จ มี Project ใหม่เชื่อมให้อัตโนมัติ พร้อม Task 1 รายการต่อ 1 บรรทัดสินค้า — ตัวอย่างจริง: Project \"QA-A B2C Test User - S00324\" พร้อม 2 Tasks (บรรทัดสินค้าจริง + Overhead)", prio="High",
         shot="assets/golden-path-block-slab-fg/gp27-mode3-project-tasks.png"),
  ]),
]
