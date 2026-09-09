# Single source of truth for EMG-O Golden Path test cases — Product/Material
# Setup: the full lifecycle of creating a new stone Material via the Quick
# Material Setup Wizard, through to it being genuinely usable in a real
# Purchase/Sale. Every other Golden Path doc (Mode 1-5) assumes this already
# happened — this is the ONE doc that actually covers it, split out
# 2026-09-09 (previously TC-E2E-M1-00 lived inside the Mode 1 doc as a
# one-off addition; now its own full doc). No field-validation/error cases —
# purely "does the whole setup flow work," written for a non-technical user.
#
# Built + the whole flow executed once live on eg-tst (Playwright, 2026-09-09)
# before writing this file — every "sample data"/"expected result" below is a
# REAL observed number from that run, not a guess:
#   Material "SY-TST-Onyx-Rosa" (Marble, Serial, Italy, density 2.65) with
#   Finish=Polished + Edge=ไม่ลบมุม selected -> Slab Product [SYTST02-SL]
#   (4,500/2,800), Block Product [SYTST02-BL] (17,500/15,000), Finished Good
#   [SYTST02-FG] "Countertop" (8,500/5,200) -> confirmed selectable in a real
#   PO and SO -> a second Finished Good ("Vanity Top") added afterward via
#   the wizard's "ใช้ Material เดิม" quick path, proving no duplicate
#   Slab/Block gets created on that path.
#
# Real bug fixed same session, both found while building this exact doc:
#   1. The wizard's "Attribute"/"Value" readonly Finish/Edge grid crashed on
#      every new-Material+Serial save (Odoo web client dirty-tracking gap) -
#      fixed with force_save="1" (stone_material_setup_wizard_views.xml).
#   2. Neither the wizard nor stone.material's own hooks ever set the new
#      Slab/Block product's categ_id, silently routing every future Bill/
#      Invoice to the wrong GL account - fixed via
#      stone.material._ensure_product_category() (2026-09-09).
#   Both already fixed and verified before this doc's fixture was built, so
#   every screenshot below reflects the CORRECTED behavior directly.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber/green callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low)

CATEGORIES = [
  dict(cat_id="P1", title="P1. เปิด Wizard + ข้อมูลพื้นฐาน",
       subtitle="เริ่มสร้าง Material ใหม่ · 2 test cases",
       cases=[
    dict(id="TC-PS-01", scenario="เปิด Quick Material Setup Wizard",
         pre="-",
         steps=["เปิด Stone Slab &gt; Tools &gt; Quick Material Setup", "เลือก Setup Mode = \"สร้าง Material ใหม่\" (ค่าเริ่มต้นอยู่แล้ว)"],
         sample="-",
         expected="หน้าต่าง Quick Material Setup เปิดขึ้น พร้อมฟอร์มข้อมูลหิน/Slab/Finish/Block/Finished Good ให้กรอกทีเดียวจบ", prio="Medium",
         shot="assets/product-setup/ps-01-wizard-open.png"),
    dict(id="TC-PS-02", scenario="กรอกข้อมูลพื้นฐานของ Material",
         pre="ทำ TC-PS-01 เสร็จแล้ว",
         steps=["กรอก Material Name", "เลือก Category", "เลือก Pricing Mode (Serial สำหรับหินที่ขายเป็นแผ่น/ก้อน แยกราคาแต่ละชิ้น)", "กรอก Internal Reference (Base Code) — ระบบจะต่อท้าย -SL/-BL/-FG ให้อัตโนมัติ", "กรอก Origin Country และ Density (Ton/CBM)"],
         sample="Material Name = SY-TST-Onyx-Rosa<br>Category = Marble<br>Pricing Mode = Serial (per-slab)<br>Base Code = SYTST02<br>Origin Country = Italy<br>Density = 2.65",
         expected="กรอกครบทุกช่องโดยไม่มี error — Base Code จะถูกใช้ตั้งรหัสสินค้าให้อัตโนมัติตอนกด Create All ทีหลัง", prio="High",
         shot="assets/product-setup/ps-02-basic-info.png"),
  ]),
  dict(cat_id="P2", title="P2. ตั้งราคา Slab + เลือก Finish/Edge",
       subtitle="เฉพาะ Pricing Mode = Serial · 1 test case",
       cases=[
    dict(id="TC-PS-03", scenario="ตั้งราคาขาย/ต้นทุน Slab และเลือก Finish/Edge ที่จะขาย",
         note="แต่ละ Attribute (Finish, มุม, ...) จะโชว์ทุกค่าที่ทีมงานตั้งไว้ล่วงหน้าให้ติ๊กเลือก — ค่าแรกที่ติ๊กของแต่ละ Attribute ถือเป็นค่ามาตรฐานของ Material นี้ (ไม่มีรหัสต่อท้าย) ค่าอื่นที่ติ๊กเพิ่มจะกลายเป็น Variant แยกพร้อมราคาส่วนต่างของตัวเอง",
         pre="ทำ TC-PS-02 เสร็จแล้ว",
         steps=["กรอก Slab Sales Price และ Slab Cost", "ในตาราง Finish/มุม/ตัวเลือกอื่นๆ ติ๊กเลือกค่าที่จะขาย", "กรอกราคาส่วนต่างของแต่ละค่าที่ติ๊ก (ถ้ามี)"],
         sample="Slab Sales Price = 4,500<br>Slab Cost = 2,800<br>ติ๊ก Finish = Polished (ราคาส่วนต่าง 0)<br>ติ๊ก มุม = ไม่ลบมุม (ราคาส่วนต่าง 0)",
         expected="ติ๊กสำเร็จ เห็นสวิตช์เปลี่ยนเป็นสีเขียวและช่องราคาส่วนต่างเปิดให้กรอกเฉพาะแถวที่ติ๊ก", prio="High",
         shot="assets/product-setup/ps-03-finish-edge.png"),
  ]),
  dict(cat_id="P3", title="P3. ตั้งค่า Block + Finished Good (ทางเลือก)",
       subtitle="เปิดใช้เมื่อวัสดุนี้ขายทั้งก้อนได้ และ/หรือ ผลิตสินค้าสำเร็จรูปได้ · 1 test case",
       cases=[
    dict(id="TC-PS-04", scenario="เปิดใช้งาน Block Product และ Finished Good พร้อมตั้งราคา",
         pre="ทำ TC-PS-03 เสร็จแล้ว",
         steps=["ติ๊ก \"ขายทั้งก้อนได้ (Block Product)\" แล้วกรอก Block Sales Price/Cost", "ติ๊ก \"มี Finished Good\" แล้วเลือก FG Category ที่มีอยู่แล้ว (หรือสร้างใหม่)", "กรอกชื่อ FG Product และราคาขาย/ต้นทุน"],
         sample="Block Sales Price = 17,500<br>Block Cost = 15,000<br>FG Category = Stone FG - Countertop<br>FG Product Name = SY-TST-Onyx-Rosa - Countertop<br>FG Sales Price = 8,500<br>FG Cost = 5,200",
         expected="กรอกครบทุกช่องโดยไม่มี error ฟอร์มพร้อมกด Create All", prio="Medium",
         shot="assets/product-setup/ps-04-block-fg.png"),
  ]),
  dict(cat_id="P4", title="P4. สร้างและตรวจผลลัพธ์",
       subtitle="กด Create All แล้วตรวจว่าทุกอย่างถูกสร้างจริง · 4 test cases",
       cases=[
    dict(id="TC-PS-05", scenario="กด Create All ยืนยันสร้าง Material",
         note="✅ เคยเจอบั๊กจริงตรงนี้ (แก้แล้ว 2026-09-09): กด Create All แล้ว error \"Missing required value for the field 'Attribute'\" ทุกครั้งที่เลือก Serial mode — เป็นช่องโหว่จริงของหน้าจอ (ไม่ใช่ผู้ใช้กรอกผิด) แก้ไขที่โค้ดแล้ว ตอนนี้กดผ่านได้ปกติ",
         pre="ทำ TC-PS-01 ถึง TC-PS-04 เสร็จแล้ว",
         steps=["กดปุ่ม \"Create All\""],
         sample="-",
         expected="สร้างสำเร็จ เปิดหน้า Material ใหม่ให้อัตโนมัติ เห็น Slab Product, Block Product, Finished Good ที่สร้างครบทั้ง 3 รายการในตาราง \"Linked Products\"", prio="High",
         shot="assets/product-setup/ps-05-material-created.png"),
    dict(id="TC-PS-06", scenario="ตรวจสอบ Slab Product ที่ถูกสร้าง",
         pre="ทำ TC-PS-05 เสร็จแล้ว",
         steps=["จากหน้า Material กดที่ Slab Product"],
         sample="-",
         expected="เปิดหน้าสินค้า [SYTST02-SL] SY-TST-Onyx-Rosa - Slab — Sales Price 4,500, Cost 2,800, Track Inventory = By Unique Serial Number, Category = Stone (ไม่ใช่ค่าว่าง)", prio="High",
         shot="assets/product-setup/ps-06-slab-product.png"),
    dict(id="TC-PS-07", scenario="ตรวจสอบ Block Product ที่ถูกสร้าง",
         pre="ทำ TC-PS-05 เสร็จแล้ว",
         steps=["เปิด Inventory &gt; Products ค้นหารหัส Block Product"],
         sample="ค้นหา = SYTST02-BL",
         expected="เปิดหน้าสินค้า [SYTST02-BL] SY-TST-Onyx-Rosa - Block — Sales Price 17,500, Cost 15,000, Track Inventory = By Lots, Category = Stone", prio="High",
         shot="assets/product-setup/ps-07-block-product.png"),
    dict(id="TC-PS-08", scenario="ตรวจสอบ Analytic Account ที่ถูกสร้างอัตโนมัติ",
         note="✨ Analytic-Architecture (2026-09-09): ทุก Material ใหม่จะได้ Analytic Account 2 ตัวอัตโนมัติ — ตัวหนึ่งใช้ร่วมกันทั้งหมวดวัสดุ (เช่น Marble) อีกตัวเฉพาะวัสดุนี้เป๊ะๆ ไม่ต้องสร้างเอง",
         pre="ทำ TC-PS-05 เสร็จแล้ว",
         steps=["ที่หน้า Material ดูช่อง \"Analytic Account (Category)\" และ \"Analytic Account (Material)\""],
         sample="-",
         expected="เห็นทั้งสองช่องมีค่าให้อัตโนมัติ — ตัวอย่างจริง: Category = Marble (ใช้ร่วมกับ Material หมวด Marble อื่นๆ ทุกตัว), Material = SY-TST-Onyx-Rosa (เฉพาะตัวนี้)", prio="Medium",
         shot="assets/product-setup/ps-05-material-created.png",
         shot_note="ภาพเดียวกับ TC-PS-05 — เห็นทั้งช่อง Analytic Account ทั้งสองในภาพเดียวกันแล้ว"),
  ]),
  dict(cat_id="P5", title="P5. พร้อมใช้งานจริง",
       subtitle="ยืนยันว่าสินค้าใหม่ซื้อ-ขายได้จริงทันที · 2 test cases",
       cases=[
    dict(id="TC-PS-09", scenario="ยืนยันว่าสินค้าใหม่เลือกได้ในหน้าสร้าง PO",
         pre="ทำ TC-PS-05 เสร็จแล้ว",
         steps=["เปิด Purchase &gt; Orders &gt; New", "เลือก Vendor", "เพิ่มบรรทัด พิมพ์ค้นหา Base Code ของ Material ใหม่"],
         sample="ค้นหา = SYTST02",
         expected="เห็นสินค้าทั้ง 3 ตัว (Block/Countertop/Slab) ขึ้นในรายการให้เลือกทันที ไม่ต้องรอตั้งค่าอะไรเพิ่ม", prio="High",
         shot="assets/product-setup/ps-08-po-product-search.png"),
    dict(id="TC-PS-10", scenario="ยืนยันว่าสินค้าใหม่เลือกได้ในหน้าสร้าง SO",
         pre="ทำ TC-PS-05 เสร็จแล้ว",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด พิมพ์ค้นหา Base Code ของ Material ใหม่"],
         sample="ค้นหา = SYTST02",
         expected="เห็นสินค้าทั้ง 3 ตัวขึ้นในรายการให้เลือกทันทีเช่นกัน", prio="High",
         shot="assets/product-setup/ps-09-so-product-search.png"),
  ]),
  dict(cat_id="P6", title="P6. เพิ่ม Finished Good ให้ Material เดิม",
       subtitle="เส้นทางลัดที่ 2 ของ wizard — ไม่ต้องสร้าง Material ใหม่ทุกครั้งที่มี FG เพิ่ม · 2 test cases",
       cases=[
    dict(id="TC-PS-11", scenario="ใช้ Material เดิม เพิ่มแค่ Finished Good ใหม่",
         pre="ทำ TC-PS-05 เสร็จแล้ว (มี Material อยู่แล้วในระบบ)",
         steps=["เปิด Quick Material Setup Wizard อีกครั้ง", "เลือก Setup Mode = \"ใช้ Material เดิม (เพิ่มแค่ FG)\"", "เลือก Material เดิมจากรายการ", "กรอก FG Category, FG Product Name, ราคาขาย/ต้นทุนของ FG ใหม่"],
         sample="Material เดิม = SY-TST-Onyx-Rosa<br>FG Category = Stone FG - Countertop<br>FG Product Name = SY-TST-Onyx-Rosa - Vanity Top<br>FG Sales Price = 9,800<br>FG Cost = 6,100",
         expected="ฟอร์มย่อลงเหลือแค่ส่วน Finished Good อย่างเดียว (ไม่มีให้กรอก Slab/Block ซ้ำ) กรอกครบพร้อมกด Create All", prio="Medium",
         shot="assets/product-setup/ps-10-existing-material-fg.png"),
    dict(id="TC-PS-12", scenario="ตรวจว่า Finished Good ใหม่ถูกเพิ่มเข้า Material เดิมโดยไม่สร้าง Slab/Block ซ้ำ",
         pre="ทำ TC-PS-11 เสร็จแล้ว",
         steps=["กด Create All", "เปิดหน้า Material เดิม ดูตาราง \"Linked Products\""],
         sample="-",
         expected="เห็น Finished Good ตัวใหม่ (\"Vanity Top\") เพิ่มเข้ามาเป็นแถวที่ 4 — Slab Product และ Block Product ยังเป็นตัวเดิม ไม่ถูกสร้างซ้ำ", prio="High",
         shot="assets/product-setup/ps-11-fg-added.png"),
  ]),
]
