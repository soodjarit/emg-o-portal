# Single source of truth for the EMG-O Golden Path "Custom FG (เจดีย์บัว): ตั้งสินค้า → BOQ → Cut List → ใบเสนอราคา → ตัดและประกอบ → ส่งของและต้นทุน".
#
# Data provenance: run end to end on `eg-tst`, 2026-11-01, driven by Playwright as emgdemo (company Empire Granite).
# Fixture: product ZZ2 เจดีย์บัว (Serial, Stone FG - Custom, 50,000) · BOQ1119 (import boq-import-zz2-chedi.xlsx, 2 pcs) · Cut List
# cutlist-import-zz2-chedi.xlsx (10 pieces / 0.90 m2 per pc) · S01695 (100,000 / 107,000) · cutting plan EG01/STCPL/00384 (Slab BLK-26-1482-5, 20 pcs, WIP 4,074.56)
# · assembly EG01/STFG/00422 (Serials 0000008, 0000009) · delivery EG01/OUT/00718 · INV/2026/00006 (COGS 4,074.56) · labour MISC/2026/11/0003 (45,925.44 = 50% floor).
# Same run produced the click-along guide guide-custom-fg-2026-11-01.html (shots shared in qa/assets/custom-fg-guide/).
#
# Scope: happy path only. Several stones in one product, lamps / several Custom FG zones in one BOQ, offcut entry, Unbuild, customer return and the
# per-piece estimated cost on the quote are NOT cases here. This set does NOT replace the older Custom FG story in test-cases-golden-path-fg-countertop-custom.html.
# Column model per case: id, scenario, note (optional callout), pre, steps (list), sample, expected, prio, shot.

SHOT = "assets/custom-fg-guide/"

CATEGORIES = [
  dict(cat_id="A", title="A. ตั้งสินค้า BOQ และ Cut List",
       subtitle="ตั้งสินค้า Custom FG · นำเข้า BOQ · นำเข้า Cut List เป็นสูตรของสินค้า · 3 test cases",
       cases=[
    dict(id="TC-GP-CFG-01", scenario="ตั้งสินค้า Custom FG (เจดีย์บัว) ให้ติดตามด้วย Serial",
         note="ต้องติ๊ก \"เป็น Custom FG\" ไม่เช่นนั้นตอนนำเข้า BOQ ระบบแจ้งว่า \"ไม่ใช่สินค้า FG ที่นำเข้าได้\" · ไม่ต้องเลือก FG Raw Material เพราะชิ้นหินมาจาก Cut List",
         pre="เข้าระบบเป็น Empire Granite · มีสิทธิ์เข้าเมนู Inventory",
         steps=["เปิดแอป Inventory &gt; Products &gt; Products แล้วกด New",
                "พิมพ์ชื่อ เลือก Goods ติ๊ก Track Inventory แล้วเลือก By Unique Serial Number กรอก Sales Price",
                "เลือก Category Stone FG - Custom ติ๊ก Is Stone FG Product และ เป็น Custom FG แล้วกด Save"],
         sample="ชื่อ ZZ2 เจดีย์บัว · Goods · By Unique Serial Number · Sales Price 50000 · Category Stone FG - Custom",
         expected="บันทึกสำเร็จ · Track Inventory = By Unique Serial Number · Sales Price 50,000.00 · Category = Stone FG - Custom · ช่อง Is Stone FG Product และ เป็น Custom FG ติ๊กอยู่",
         prio="High", shot=SHOT + "c01-product-saved.webp"),
    dict(id="TC-GP-CFG-02", scenario="นำเข้า BOQ ของเจดีย์บัว (ราคาคงที่ต่อชิ้น)",
         note="ไฟล์ตัวอย่างใส่ Overhead 0% ทุกแถว ราคาจึงเป็น 50,000 ต่อชิ้นตามที่ตั้ง · ชื่อโซนต้องจำไว้ใช้ใน Cut List",
         pre="ทำ TC-GP-CFG-01 เสร็จแล้ว · ไฟล์ boq-import-zz2-chedi.xlsx",
         steps=["เปิดแอป BOQ Estimation &gt; BOQ Documents แล้วกด Import Excel",
                "เลือกลูกค้า อัปโหลดไฟล์ แล้วกด อ่านไฟล์",
                "ตรวจหน้าตัวอย่าง แล้วกด สร้าง BOQ"],
         sample="Customer = Demo Hotel Customer · ไฟล์ = boq-import-zz2-chedi.xlsx (โซน เจดีย์บัว · ZZ2 เจดีย์บัว · 2 ชิ้น · 50,000)",
         expected="หน้าตัวอย่างไม่มีแถวแดง · จำนวนรายการ 1 · วัสดุรวม 100,000.00 · รวม 100,000.00 · ได้ BOQ ใหม่ (เช่น BOQ1119) แท็บ ① มี 1 บรรทัด 2.00 ชิ้น × 50,000.00 = 100,000.00",
         prio="High", shot=SHOT + "c02-import-preview.webp"),
    dict(id="TC-GP-CFG-03", scenario="นำเข้า Cut List ของเจดีย์บัว 1 ชิ้น เป็นสูตรของสินค้า",
         note="Cut List ใส่ชิ้นหินของสินค้า 1 ชิ้น ระบบคูณตามจำนวนที่ขายเอง · \"รายการ\" ในไฟล์ต้องเป็นชื่อเดียวกับที่เทมเพลตให้ ถ้าไม่ตรงช่องสินค้าในหน้าตัวอย่างว่างและกดยืนยันไม่ผ่าน · ชิ้นหินไม่ขึ้นใบเสนอราคา ราคาไม่เปลี่ยน",
         pre="ทำ TC-GP-CFG-02 เสร็จแล้ว · ไฟล์ cutlist-import-zz2-chedi.xlsx",
         steps=["เปิด BOQ แท็บ ③ Cut List ช่อง รายการที่ใช้ในโปรเจกต์นี้ เลือกสินค้าหิน แล้วกด Save",
                "กด นำเข้า Cut List คงวิธีนำเข้า เติมชิ้นงานเข้าบรรทัดเดิมตามโซน อัปโหลดไฟล์ แล้วกด อ่านไฟล์",
                "ตรวจหน้าตัวอย่าง แล้วกด ยืนยันนำเข้า"],
         sample="รายการที่ใช้ = ZZ2 GUIDE MARBLE Countertop · ไฟล์ = cutlist-import-zz2-chedi.xlsx (10 ชิ้น โซน เจดีย์บัว)",
         expected="หน้าตัวอย่าง: โซน เจดีย์บัว จำนวนแถว 10 ปริมาณรวม 0.9000 ตร.ม. ผลจับคู่ \"สูตรของ ZZ2 เจดีย์บัว\" · หลังยืนยัน: แท็บ ① มีบรรทัดสูตร [ZZ2G-FG] ZZ2 GUIDE MARBLE Countertop 0.90 m² ช่องรวม 0.00 · ยอดรวม BOQ ยัง 100,000.00 · แท็บ ③ ชิ้นงานที่นำเข้าแล้ว 10",
         prio="High", shot=SHOT + "c03-preview.webp"),
  ]),
  dict(cat_id="B", title="B. ใบเสนอราคาและสั่งผลิต",
       subtitle="ออกใบเสนอราคาจาก BOQ · ยืนยัน ระบบสร้างใบตัดหินและใบประกอบ · 1 test case",
       cases=[
    dict(id="TC-GP-CFG-04", scenario="ออกใบเสนอราคาจาก BOQ แล้ว Confirm ระบบสร้างใบสั่งผลิตให้ครบ",
         note="บรรทัดสูตรไม่ขึ้นใบเสนอราคาและ PDF · ถ้าขึ้นหน้าต่างเตือนว่าไม่มีของ กด Confirm ต่อ · ใบประกอบ Confirm ไม่ได้จนกว่าใบตัดหินจะเสร็จ",
         pre="ทำ TC-GP-CFG-03 เสร็จแล้ว",
         steps=["ที่ BOQ กด สร้างใบเสนอราคา",
                "กด Confirm ที่ใบเสนอราคา",
                "กดสมาร์ทปุ่ม FG Production แล้วกดสมาร์ทปุ่ม แผนตัด ที่ใบประกอบ"],
         sample="-",
         expected="ใบเสนอราคา (เช่น S01695) ก่อน VAT 100,000.00 VAT 7% 7,000.00 รวม 107,000.00 · หลัง Confirm เป็น Sales Order มีปุ่ม Delivery 1 และ FG Production 1 · ได้ใบประกอบ EG01/STFG/00422 (2 Units ป้าย งานกำหนดเอง) และใบตัดหิน EG01/STCPL/00384 (20 ชิ้น แผน 1.80 ตร.ม.) สถานะ Draft",
         prio="High", shot=SHOT + "c04-so-confirmed.webp"),
  ]),
  dict(cat_id="C", title="C. ตัดหินและประกอบ",
       subtitle="ตัดตามแผน · ประกอบเป็นเจดีย์บัวทีละ Serial · 2 test cases",
       cases=[
    dict(id="TC-GP-CFG-05", scenario="ใบตัดหิน — ย้ายไปสถานีตัด Confirm คัดลอกแผนเป็นขนาดจริง แล้วถอดแบบเสร็จ",
         note="ปุ่ม คัดลอกแผนเป็นขนาดจริง เติมขนาดจริงให้เท่าแผนทุกแถว ช่างแก้เฉพาะชิ้นที่ตัดไม่ตรงแบบ · ไม่ได้บันทึกเศษ ต้นทุน Slab ทั้งแผ่นจึงเข้า WIP ทั้งหมด · ความหนาในแผน 0.02 ม. ต่างจาก Slab ที่หนา 0.03 ม. (ข้อสงสัยที่ค้างถามลูกค้า)",
         pre="ทำ TC-GP-CFG-04 เสร็จแล้ว · มี Slab ZZ2 GUIDE MARBLE ที่ Available อย่างน้อย 1 แผ่น",
         steps=["ที่ใบประกอบ กดสมาร์ทปุ่ม แผนตัด เปิดใบตัดหิน",
                "แท็บ Slab ที่จะตัด ตรวจแผ่นที่เลือก กดปุ่ม ย้ายไปสถานีตัด แล้วกด Confirm",
                "แท็บ ชิ้นงาน (แผน/จริง) กดปุ่ม คัดลอกแผนเป็นขนาดจริง แล้วกด ถอดแบบเสร็จ"],
         sample="Slab ที่ระบบเลือก = BLK-26-1482-5 (1.50 × 2.90 × 0.030 ม. = 4.35 ตร.ม.) · ชิ้นงาน 20 ชิ้น รวม 1.80 ตร.ม.",
         expected="พื้นที่งาน 1.80 ต้องใช้รวมเผื่อเสีย 1.98 แผ่นที่เลือก 4.35 · หลัง Confirm สถานะ Confirmed · หลังถอดแบบเสร็จ Done แผน 1.80 ตัดได้จริง 1.80 ตร.ม. · ได้ Lot WIP CUT-EG01/STCPL/00384 20 ชิ้นที่ Stone Production มูลค่า 4,074.56 บาท",
         prio="High", shot=SHOT + "c05-plan-done.webp"),
    dict(id="TC-GP-CFG-06", scenario="ใบประกอบ — Confirm แล้ว Produce All ได้เจดีย์บัวทีละ Serial",
         note="Confirm ใบประกอบไม่ได้จนกว่าใบตัดหินที่ผูกกันทุกใบจะ Done · ใบประกอบที่ Done มีปุ่ม Unbuild (ยังไม่ได้ทดลอง)",
         pre="ทำ TC-GP-CFG-05 เสร็จแล้ว",
         steps=["เปิดใบประกอบ EG01/STFG/00422 กด Confirm",
                "ตรวจ Component Status และช่อง Lot จาก Cutting Plan",
                "กดปุ่ม Produce All"],
         sample="-",
         expected="Component Status = Available · ช่อง Lot จาก Cutting Plan = CUT-EG01/STCPL/00384 · หลัง Produce All สถานะ Done Quantity 2.000 / 2.000 · สมาร์ทปุ่ม Serial Numbers 2 (ในรอบทดสอบ 0000008 และ 0000009)",
         prio="High", shot=SHOT + "c05-assembly-done.webp"),
  ]),
  dict(cat_id="D", title="D. ส่งของ ใบแจ้งหนี้ และต้นทุน",
       subtitle="ส่งของตาม Serial · ใบแจ้งหนี้และต้นทุนขาย · ค่าแรงตามกติกา 50% · 2 test cases",
       cases=[
    dict(id="TC-GP-CFG-07", scenario="ส่งของตาม Serial แล้วออกใบแจ้งหนี้ ตรวจรายการบัญชี",
         note="ถ้ากด Create Invoice ก่อนส่งของ ระบบแจ้งว่าไม่มีรายการให้ออกใบแจ้งหนี้ ให้ Validate ใบส่งของก่อน",
         pre="ทำ TC-GP-CFG-06 เสร็จแล้ว",
         steps=["ที่ใบสั่งขาย กดสมาร์ทปุ่ม Delivery แล้วกด Validate",
                "กลับที่ใบสั่งขาย กด Create Invoice เลือก Regular invoice แล้วกด Create Draft",
                "กด Confirm แล้วเปิดแท็บ Journal Items"],
         sample="ใบส่งของ EG01/OUT/00718 · ใบสั่งขาย S01695",
         expected="ใบส่งของ Ready ก่อนกด เป็น Done หลัง Validate 2.000 Units · ใบแจ้งหนี้ (เช่น INV/2026/00006) Posted 2.000 × 50,000.00 · ก่อน VAT 100,000.00 · VAT 7,000.00 · รวม 107,000.00 · Journal Items: เดบิต 112100 ลูกหนี้ 107,000.00 · เครดิต 411100 รายได้ 100,000.00 · เครดิต 213200 VAT 7,000.00 · เดบิต 511110 ต้นทุนขาย 4,074.56 · เครดิต 113150 สต็อก FG 4,074.56",
         prio="High", shot=SHOT + "c06-journal.webp"),
    dict(id="TC-GP-CFG-08", scenario="ตรวจรายการบัญชีค่าแรงของใบประกอบ (กติกาต้นทุนไม่ต่ำกว่า 50%)",
         note="ข้อสังเกตที่ควรถามลูกค้า: ต้นทุนรวมที่ลงบัญชี 50,000 (วัสดุ 4,074.56 + ค่าแรง 45,925.44) = 50% ของรายได้ ไม่ใช่ต้นทุนจริง เพราะระบบมีกติกาต้นทุนไม่ต่ำกว่า 50% แล้วเติมส่วนต่างเป็นค่าแรง · ค่าแรงและวัสดุสิ้นเปลืองที่อยู่ใน BOQ เป็นประมาณการเท่านั้น ไม่ได้ลงบัญชี · ค่าแรงลงตอนผลิตเสร็จ ไม่อยู่ในใบแจ้งหนี้",
         pre="ทำ TC-GP-CFG-06 เสร็จแล้ว",
         steps=["เปิดแอป Accounting &gt; Accounting &gt; Journal Entries",
                "ค้นหา FG Production Labor ของใบประกอบ EG01/STFG/00422",
                "เปิดรายการ ดูเดบิตและเครดิต"],
         sample="รายได้บรรทัดงาน = 100,000 · วัสดุ = 4,074.56 · ต้นทุนขั้นต่ำ 50%",
         expected="รายการ (เช่น MISC/2026/11/0003) เดบิต 511120 ค่าแรง 45,925.44 เครดิต 212300 ค้างจ่าย 45,925.44 (= 50% × 100,000 − 4,074.56)",
         prio="High", shot=SHOT + "c06-labour.webp"),
  ]),
]
