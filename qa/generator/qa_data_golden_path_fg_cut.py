# Single source of truth for the EMG-O Golden Path "FG: ใบเสนอราคาแผ่นตัดตามขนาด → งานผลิต FG → ส่งของ → ใบแจ้งหนี้และต้นทุน".
#
# Data provenance: run end to end on `eg-tst`, 2026-11-01, driven by Playwright as emgdemo (company Empire Granite).
# Fixture: S01694 (Demo Hotel Customer; ZZ2 GUIDE MARBLE Countertop; pieces A 100x100 x4 + B 60x90 x5 = 6.70 m2 @ 3,800 = 25,460.00)
# -> FG Production EG01/STFG/00421 (Slabs BLK-26-1482-1, -2; need 7.37 m2 incl. 10% waste, selected 8.70) -> FG lots FG-EG01/STFG/00421-01, -02
# -> delivery EG01/OUT/00717 -> invoice INV/2026/00005 (25,460.00 / VAT 1,782.20 / 27,242.20) with COGS 8,149.12; labour accrual 10,050.00.
# Same run produced the click-along guide guide-fg-2026-11-01.html (shots shared in qa/assets/fg-guide/).
# The FG category "ZZ Guide FG - Countertop" had to be set to FIFO + Perpetual (+ accounts) first, otherwise the invoice has no COGS lines.
# An earlier run on the un-configured category (S01693, EG01/STFG/00420, INV/2026/00004) is left on eg-tst as a superseded fixture.
#
# Scope: happy path only. Edge/cut-out processing jobs, offcut entry, Work Order timing, FG return, buying FG from a vendor and the
# Custom FG (เจดีย์บัว) path are NOT cases here. This set does NOT replace the older FG golden paths (left untouched).
# Column model per case: id, scenario, note (optional callout), pre, steps (list), sample, expected, prio, shot.

SHOT = "assets/fg-guide/"

CATEGORIES = [
  dict(cat_id="A", title="A. ขายและเตรียมงานผลิต",
       subtitle="ใบเสนอราคา FG ระบุรายชิ้น · ยืนยันใบสั่งขาย · เตรียมใบสั่งผลิต · 3 test cases",
       cases=[
    dict(id="TC-GP-FG-01", scenario="ทำใบเสนอราคา FG ระบุรายชิ้น (กว้าง × ยาว × จำนวน)",
         note="ขนาดรายชิ้นกรอกเป็น ซม. · กรอกทีละช่อง กด Tab และรอให้ตัวเลขเข้าก่อนช่องถัดไป · จำนวนของบรรทัดสินค้าเปลี่ยนเป็นพื้นที่รวมของรายชิ้นเอง",
         pre="ทำคู่มือ Setup ระบบตอน 2 แล้ว มีสินค้า ZZ2 GUIDE MARBLE Countertop (3,800 บาทต่อ ตร.ม.) · มีลูกค้า Demo Hotel Customer",
         steps=["เปิดแอป Sales &gt; Orders &gt; Quotations &gt; New เลือก Customer",
                "กด Add a product เลือกสินค้า FG แล้วกด Save",
                "กดไอคอนรายชิ้นที่ท้ายบรรทัดสินค้า กด New กรอกรหัสชิ้น กว้าง ยาว จำนวนชิ้น แล้วทำซ้ำสำหรับชิ้นที่สอง จากนั้นปิดหน้าต่าง"],
         sample="Customer = Demo Hotel Customer · ZZ2 GUIDE MARBLE Countertop · A = 100 × 100 ซม. × 4 ชิ้น · B = 60 × 90 ซม. × 5 ชิ้น",
         expected="ตารางรายชิ้น A = 4.00 ตร.ม. · B = 2.70 ตร.ม. · รวม 6.70 · บรรทัดสินค้า Quantity 6.700 m² × 3,800.00 · ก่อน VAT 25,460.00 · VAT 7% 1,782.20 · รวม 27,242.20",
         prio="High", shot=SHOT + "l01-pieces.webp"),
    dict(id="TC-GP-FG-02", scenario="กด Confirm ใบสั่งขาย ระบบสร้างใบสั่งผลิตและใบส่งของให้เอง",
         note="ระบบเตือน \"ยืนยัน Confirm ทั้งที่ยังไม่มีของ\" เพราะ FG ผลิตตามออเดอร์ ให้กด Confirm ต่อ",
         pre="ทำ TC-GP-FG-01 เสร็จแล้ว",
         steps=["กด Confirm ที่ใบเสนอราคา",
                "ถ้าขึ้นหน้าต่างเตือน กด Confirm ต่อ"],
         sample="-",
         expected="ใบสั่งขายสถานะ Sales Order (เช่น S01694) · ปุ่มสมาร์ท Delivery 1 และ FG Production 1 · ยอดคงเดิม 27,242.20",
         prio="High", shot=SHOT + "l02-so-confirmed.webp"),
    dict(id="TC-GP-FG-03", scenario="เปิดใบสั่งผลิต ตรวจ Slab ที่ระบบเลือก ย้ายไปสถานีตัดแล้ว Confirm",
         note="ต้องใช้ 7.37 ตร.ม. = 6.70 + เผื่อเสีย 10% · ระบบเลือก Slab ให้ 2 แผ่น (8.70 ตร.ม.) · ต้องกดย้ายไปสถานีตัดก่อน Confirm",
         pre="ทำ TC-GP-FG-02 เสร็จแล้ว · มี Slab ของ ZZ2 GUIDE MARBLE ที่ Available อย่างน้อย 2 แผ่น",
         steps=["ที่ใบสั่งขาย กดปุ่มสมาร์ท FG Production",
                "เปิดแท็บ Slab ที่จะตัด ดูแผ่นที่ระบบเลือก",
                "กดปุ่ม ย้ายไปสถานีตัด แล้วกด Confirm"],
         sample="-",
         expected="ใบสั่งผลิต (เช่น EG01/STFG/00421) Draft ก่อนกด · ต้องใช้ 7.37 ตร.ม. · Slab ที่เลือก 8.70 ตร.ม. (2 แผ่น แผ่นละ 1.50 × 2.90 × 0.030 ม. = 4.35 ตร.ม.) · หลัง Confirm สถานะ Confirmed และ Component Status Available",
         prio="High", shot=SHOT + "l02-mo-confirmed.webp"),
  ]),
  dict(cat_id="B", title="B. ผลิตและส่งของ",
       subtitle="ผลิต FG เสร็จ · ส่งของ · 2 test cases",
       cases=[
    dict(id="TC-GP-FG-04", scenario="ผลิต FG เสร็จ ระบบสร้างสต็อก FG ตามขนาดและลงต้นทุน",
         note="ช่องขนาดในแท็บ ผลผลิต FG เป็นเมตร (1.00 = 100 ซม.) และช่องความหนาเป็น 0.00 ได้ ระบบใช้ความหนาของ Slab · ค่าแรง 6.70 × 1,500 = 10,050.00 ลงเป็นค่าใช้จ่ายค้างจ่ายตอนผลิตเสร็จ ไม่รวมในต้นทุนสต็อก FG · ยังไม่ได้ทดลองบันทึกเศษที่เหลือ",
         pre="ทำ TC-GP-FG-03 เสร็จแล้ว",
         steps=["เปิดแท็บ ผลผลิต FG ตรวจขนาดและจำนวนชิ้นที่ตัดได้จริง",
                "กดปุ่ม ผลิต FG เสร็จ"],
         sample="ผลผลิต: 1.00 × 1.00 จำนวน 4 (A) · 0.60 × 0.90 จำนวน 5 (B)",
         expected="ใบสั่งผลิตสถานะ Done · Lot FG-EG01/STFG/00421-01 (1.00 × 1.00 × 0.03 ม. 4 ชิ้น) และ FG-EG01/STFG/00421-02 (0.60 × 0.90 × 0.03 ม. 5 ชิ้น) · ตรวจจากฐานข้อมูล: Slab 2 แผ่นมูลค่า 8,149.12 ย้ายเป็นสต็อก FG (เดบิต 113150 เครดิต 113120) · ค่าแรง 10,050.00 (เดบิต 511120 เครดิต 212300)",
         prio="High", shot=SHOT + "l03-mo-done.webp"),
    dict(id="TC-GP-FG-05", scenario="ส่งของ FG ให้ลูกค้า",
         note="ระบบจองสต็อก FG ให้ใบส่งของเองตามขนาดที่ขาย ไม่ต้องเลือก Lot · ใบส่งของ FG ไม่ต้องสแกน Serial",
         pre="ทำ TC-GP-FG-04 เสร็จแล้ว",
         steps=["ที่ใบสั่งขาย กดปุ่มสมาร์ท Delivery",
                "กด Validate"],
         sample="ใบส่งของ EG01/OUT/00717",
         expected="ใบส่งของ Ready ก่อนกด (Demand 6.700 Quantity 6.700 m²) เป็น Done หลัง Validate · มูลค่าที่ตัดจากสต็อก 8,149.12 (ตรวจจากฐานข้อมูล)",
         prio="High", shot=SHOT + "l04-delivery-done.webp"),
  ]),
  dict(cat_id="C", title="C. ใบแจ้งหนี้และต้นทุน",
       subtitle="ออกใบแจ้งหนี้ ระบบลงต้นทุนขายให้ · 1 test case",
       cases=[
    dict(id="TC-GP-FG-06", scenario="ออกใบแจ้งหนี้และตรวจรายการบัญชี (รายได้ ต้นทุนขาย)",
         note="ต้องตั้งหมวด FG เป็น FIFO + Perpetual ก่อน (คู่มือ Setup ตอน 1 ข้อ 1.5–1.6) ไม่เช่นนั้นไม่มีรายการต้นทุนขายในใบแจ้งหนี้ · กำไรขั้นต้น 25,460.00 − 8,149.12 − 10,050.00 = 7,260.88 บาท",
         pre="ทำ TC-GP-FG-05 เสร็จแล้ว",
         steps=["ที่ใบสั่งขาย กด Create Invoice เลือก Regular invoice แล้วกด Create Draft",
                "กด Confirm",
                "เปิดแท็บ Journal Items"],
         sample="ใบสั่งขาย S01694 · Regular invoice",
         expected="ใบแจ้งหนี้ (เช่น INV/2026/00005) Posted · 6.700 m² × 3,800.00 · ก่อน VAT 25,460.00 · VAT 1,782.20 · รวม 27,242.20 · Journal Items: เดบิต 112100 ลูกหนี้ 27,242.20 · เครดิต 411100 รายได้ขาย 25,460.00 · เครดิต 213200 VAT ขาย 1,782.20 · เดบิต 511110 ต้นทุนขาย 8,149.12 · เครดิต 113150 สต็อก FG 8,149.12",
         prio="High", shot=SHOT + "l05-journal.webp"),
  ]),
]
