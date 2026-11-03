# Single source of truth for the EMG-O Golden Path "Setup ระบบ → ใช้ค่าที่ตั้งกับ BOQ และใบเสนอราคา".
#
# Why this doc exists: qa/test-cases-product-setup.html (old) still talks about the Rate Library, the "มุม" attribute and a PO-line
# button that creates Blocks, none of which exist any more. This is the replacement for the setup part (old doc left untouched).
#
# Data provenance: run end to end on `eg-tst`, 2026-11-01, driven by Playwright as emgdemo (company Empire Granite).
# Fixture (all names start with ZZ): FG category id 541 -> material "ZZ2 GUIDE MARBLE" (id 2442, base code ZZ2G) -> products
# ZZ กาวและปูนยาแนวปูพื้น / ZZ ค่าแรงติดตั้งพื้น -> sets "ZZ ชุดวัสดุพื้นมาตรฐาน" / "ZZ ชุดค่าแรงติดตั้งพื้น" -> BOQ1187 -> quotation S01752.
# Same run produced the click-along guide guide-setup-2026-11-01.html (shots reused from qa/assets/guide-setup/).
#
# Updated 2026-11-03: the sets (old SET-03..05) were removed with the BOQ redesign; BOQ usage now lives in test-cases-golden-path-boq-items.html. 3 cases remain.
# Scope note (agreed 2026-11-01): the "use the setup" half that needs real stock (buy and receive a Block, cut Slabs, produce FG,
# P&L by the material analytic) is NOT re-run here with the ZZ stone — it is already covered by the Golden Paths linked in the
# flow banner. 5 cases, not 8.
#
# Golden Path discipline: happy path only, no validation/error cases, plain language.
# Column model per case: id, scenario, note (optional callout), new (green callout), pre, steps (list), sample, expected, prio, shot.

SHOT = "assets/golden-path-setup/"

CATEGORIES = [
  dict(cat_id="A", title="A. ตั้งค่าระบบ",
       subtitle="ตั้งหมวด FG · ตั้งสินค้าหินด้วย Quick Material Setup · ตั้งชุดวัสดุและชุดค่าแรง · 3 test cases",
       cases=[
    dict(id="TC-GP-SET-01", scenario="ตั้งหมวดสินค้าสำเร็จรูป (FG) พร้อมค่าแรงและขั้นตอนผลิต",
         note="หมวด FG ต้องตั้งก่อนตั้งสินค้าหิน เพราะตอนตั้งหินต้องเลือกหมวดนี้ · ฟอร์มหมวดยังไม่มีช่องต้นทุนวัสดุสิ้นเปลือง (ระบบมีช่องในข้อมูล แต่หน้าจอไม่แสดง) ต้นทุนส่วนนี้จึงเป็น 0",
         pre="เข้าระบบเป็น Empire Granite · มีสิทธิ์เข้าเมนู Inventory &gt; Configuration",
         steps=["เปิดแอป Inventory &gt; Configuration &gt; Categories แล้วกด New",
                "พิมพ์ชื่อหมวด คง FG Tracking เป็น Lot กรอก FG Standard Labor Cost ตั้ง Costing Method เป็น FIFO และ Inventory Valuation เป็น Perpetual แล้วเลือกบัญชี Expense และ Stock",
                "แท็บ FG Production Operations กด Add a line พิมพ์ขั้นตอนที่ 1 กด Enter แล้วพิมพ์ขั้นตอนที่ 2 จากนั้นกด Save"],
         sample="ชื่อ ZZ Guide FG - Countertop · FG Tracking = Lot · ค่าแรงมาตรฐาน 1500 · Costing Method = FIFO · Inventory Valuation = Perpetual (at invoicing) · Expense Account = 511110 · Stock Account = 113150 · ขั้นตอน: Cutting (ตัดตามแบบ), Edge (ทำขอบ)",
         expected="บันทึกสำเร็จ ชื่อหมวดขึ้นที่แถบนำทาง · FG Tracking = Lot · FG Standard Labor Cost = 1,500.00 · Costing Method = FIFO และ Inventory Valuation = Perpetual · บัญชี 511110 และ 113150 · ตารางขั้นตอนมี 2 แถวตามลำดับที่พิมพ์",
         prio="High", shot=SHOT + "gp-set-01-category.webp"),
    dict(id="TC-GP-SET-02", scenario="ตั้งสินค้าหินด้วย Quick Material Setup ให้ได้ Slab, Block และ FG ในครั้งเดียว",
         note="Setup Mode ใช้ \"สร้าง Material ใหม่\" · ขนาดแผ่นมาตรฐานกรอกเป็นเมตร ส่วนความหนาเป็น ซม. · ระบบสร้างสินค้าให้ 4 ตัว (Slab, Block, FG และสินค้าภายใน Cutting Plan WIP) · ผิวอื่นนอกจากผิวแรกได้รหัสต่อท้าย เช่น Honed = -SL-HON",
         pre="ทำ TC-GP-SET-01 เสร็จแล้ว",
         steps=["เปิดแอป Stone Slab &gt; Tools &gt; Quick Material Setup",
                "กรอกข้อมูลหิน: ชื่อ หมวด รหัสฐาน Density แล้วกรอกส่วน Slab: ราคาขายฐานต่อ CBM ราคาขายต่อ ตร.ม. และต้นทุนต่อ ตร.ม. คงขนาดแผ่นและผิว Polished กับ Honed ไว้",
                "ติ๊ก BLOCK PRODUCT กรอกราคาขายและต้นทุนต่อตัน แล้วติ๊ก FINISHED GOOD เลือกหมวด FG จาก TC-GP-SET-01 (เลือกจากรายการ ห้ามพิมพ์หมวดใหม่) กรอกชื่อ ราคาขาย และต้นทุน",
                "กด Create All"],
         sample="ZZ2 GUIDE MARBLE · หมวด Marble · Serial · รหัสฐาน ZZ2G · Density 2.65 · ราคาฐาน 125,000 ต่อ CBM · Slab 2,500 / ต้นทุน 1,300 ต่อ ตร.ม. · แผ่น 3.000 × 1.600 ม. หนา 2 ซม. · Block 15,800 / ต้นทุน 12,000 บาทต่อตัน · FG 3,800 / ต้นทุน 2,000",
         expected="เปิดหน้า Material ZZ2 GUIDE MARBLE สถานะใช้งาน · Slab Product [ZZ2G-SL] (Variant Polished และ ZZ2G-SL-HON) · Block Product [ZZ2G-BL] ราคาขาย 41,870 ต่อ ลบ.ม. (15,800 × 2.65) · FG [ZZ2G-FG] 3,800 ต่อ ตร.ม. อยู่ในหมวด ZZ Guide FG - Countertop · ตารางราคาตามความหนา 5 แถว: 1.5 / 2 / 2.5 / 3 / 5 ซม. = 1,875 / 2,500 / 3,125 / 3,750 / 6,250 ต่อ ตร.ม. · ได้ Analytic ใหม่ 1 ตัวระดับวัสดุ (ระดับหมวด Marble ใช้ตัวเดิมร่วมกัน)",
         prio="High", shot=SHOT + "gp-set-02-material.webp"),
    dict(id="TC-GP-SET-03", scenario="ตั้งสินค้าค่าแรงและวัสดุสิ้นเปลือง และระบุประเภทรายการ BOQ",
         note="ไม่มีชุดค่าแรง/ชุดวัสดุแล้ว (เลิกใช้ 3 พ.ย. 2569) · ค่าแรง/วัสดุเป็นสินค้าธรรมดาที่ใส่เป็นบรรทัดใน BOQ เอง · Cost ของสินค้าคือต้นทุนที่ลงบัญชีตอนผลิต",
         pre="เข้าระบบเป็น Empire Granite",
         steps=["เปิดแอป Inventory &gt; Products &gt; Products กด New สร้างสินค้ากาว (Goods ไม่ติ๊ก Track Inventory) ตั้งหน่วยเป็น m² ช่อง ประเภทรายการ BOQ เลือก วัสดุสิ้นเปลือง แล้ว Save",
                "กด New อีกครั้งสร้างสินค้าค่าแรง (Service) ตั้งหน่วยเป็น m² ช่อง ประเภทรายการ BOQ เลือก ค่าแรง แล้ว Save"],
         sample="สินค้า ZZ กาวและปูนยาแนวปูพื้น ขาย 150 ทุน 90 ต่อ ตร.ม. (วัสดุสิ้นเปลือง) · ZZ ค่าแรงติดตั้งพื้น ขาย 1,500 ทุน 500 ต่อ ตร.ม. (ค่าแรง)",
         expected="สินค้ากาว: ช่อง ประเภทรายการ BOQ แสดง วัสดุสิ้นเปลือง · Sales Price 150.00 · Cost 90.00 · สินค้าค่าแรง: ประเภทรายการ BOQ แสดง ค่าแรง · Sales Price 1,500.00 · Cost 500.00 · ทั้งสองบันทึกสำเร็จ · สินค้าทั้งสองจะขึ้นใน dropdown ของเทมเพลต Excel นำเข้า BOQ",
         prio="High", shot=SHOT + "gp-set-03-items.png"),
  ]),
]
