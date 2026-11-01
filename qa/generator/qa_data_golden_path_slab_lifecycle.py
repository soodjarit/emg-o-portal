# Single source of truth for the EMG-O Golden Path "Slab: ดู Slab ที่ตัดได้ → ซื้อสำเร็จรูป → ขาย → ส่งของสแกน Serial → ใบแจ้งหนี้และต้นทุน".
#
# Data provenance: run end to end on `eg-tst`, 2026-11-01, driven by Playwright as emgdemo (company Empire Granite).
# Fixture: Slabs BLK-26-1486-1..8 (cut from BLK-26-1486, 20 cm) · PO P00622 (4 Slab @ 1,300/m2) -> receipt EG01/IN/00744
# -> SLB-26-0389..0388 (1.58x2.95, 1.60x3.00, 1.55x2.90, 1.60x3.00 m, 0.02 thick) -> S01692 (Demo Hotel Customer, 18.76 m2 @ 2,500 = 46,900)
# -> delivery EG01/OUT/00715 (scanned serials) -> invoice INV/2026/00003 (50,183.00) with COGS 24,382.80.
# Same run produced the click-along guide guide-slab-2026-11-01.html (shots shared in qa/assets/slab-guide/).
#
# Scope: happy path only. Slab resize, customer return, quote with actual size different from the offered size, Import from Excel,
# Hold / Consigned status are NOT cases here. This set does NOT replace the older Slab golden paths (left untouched).
# Column model per case: id, scenario, note (optional callout), pre, steps (list), sample, expected, prio, shot.

SHOT = "assets/slab-guide/"

CATEGORIES = [
  dict(cat_id="A", title="A. ได้ Slab มา",
       subtitle="ดู Slab ที่ได้จากการตัด Block · ซื้อ Slab สำเร็จรูป · รับของกรอกขนาดทีละแผ่น · 3 test cases",
       cases=[
    dict(id="TC-GP-SLB-01", scenario="ตรวจ Slab ที่ได้จากการตัด Block",
         note="ราคาขาย 3,750 บาท/ตร.ม. เพราะ Slab ชุดนี้หนา 3 ซม. ระบบคิดราคาตามความหนา (2,500 บาท/ตร.ม. ที่ 2 ซม.) · ตัวกรองเริ่มต้น Available ซ่อนแผ่นที่ขายแล้ว",
         pre="ทำ Golden Path Block (TC-GP-BLK-06) แล้ว มี Slab BLK-26-1486-1 ถึง -53",
         steps=["เปิดแอป Stone Slab &gt; Slabs &gt; All Slabs พิมพ์เลข Block ในช่องค้นหาแล้วกด Enter",
                "เปิดแผ่นแรก ดูการ์ดสรุป",
                "เปิดแท็บ ที่มา / เอกสารที่ผูก"],
         sample="Block BLK-26-1486 · แผ่น BLK-26-1486-1",
         expected="ตาราง 53 แถว ขนาด 1.50 × 2.90 × 0.030 ม. (กว้าง × ยาว × หนา) = 4.35 ตร.ม. สถานะ Available คอลัมน์ Block = BLK-26-1486 · การ์ด: ราคาขาย 3,750.00 บาท/ตร.ม. (≈ 16,312.50 บาท/แผ่น) · ต้นทุน 4,072.79 บาท (= 215,858.10 ÷ 53) · แรงตัด 522.00 บาท · ที่เก็บ Stone Inventory/Stone Available · แท็บที่มา ช่อง Block = BLK-26-1486",
         prio="High", shot=SHOT + "k01-cut-slab-card.webp"),
    dict(id="TC-GP-SLB-02", scenario="สั่งซื้อ Slab สำเร็จรูปเป็นจำนวนแผ่น",
         note="ตัวเลขในใบสั่งซื้อเป็นการประมาณ · ช่อง Qty (Sq.M) ไม่เปลี่ยนตาม Quantity (ขึ้น 4.8 ไม่ว่า Quantity เป็นเท่าใด) ต้องพิมพ์เอง ถ้าไม่พิมพ์ยอดจะเป็น 6,240 สำหรับ 4 แผ่น ต่ำกว่ามูลค่าจริงมาก (24,382.80) ยังไม่ได้ตรวจสาเหตุ",
         pre="ทำคู่มือ Setup ระบบตอน 2 แล้ว มีสินค้า ZZ2 GUIDE MARBLE - Slab · มีผู้ขาย Demo Stone Supplier",
         steps=["เปิดแอป Purchase &gt; Orders &gt; Requests for Quotation &gt; New เลือก Vendor",
                "กด Add a product เลือกสินค้า Slab กรอก Quantity, Qty (Sq.M) และ Price / Sq.M",
                "กด Confirm Order"],
         sample="Vendor = Demo Stone Supplier · ZZ2 GUIDE MARBLE - Slab · Quantity = 4 · Qty (Sq.M) = 19.2 · Price / Sq.M = 1,300",
         expected="สถานะ Purchase Order (เช่น P00622) · Quantity 4.0000 Units · Qty (Sq.M) 19.2000 · Price / Sq.M 1,300.00 · Unit Price 6,240.00 · ก่อน VAT 24,960.00 · VAT 1,747.20 · รวม 26,707.20 · ปุ่มสมาร์ท Receive 1",
         prio="High", shot=SHOT + "k02-po-confirmed.webp"),
    dict(id="TC-GP-SLB-03", scenario="รับของ กรอกขนาดจริงทีละแผ่น แล้ว Validate ให้ระบบสร้าง Slab",
         note="มูลค่าสต็อกคิดจากพื้นที่จริงของแต่ละแผ่น ไม่ใช่ขนาดมาตรฐาน · ช่อง Lot/Serial เว้นว่างได้ ระบบตั้งชื่อให้ · มูลค่าต่อแผ่นตรวจจากฐานข้อมูล ไม่แสดงบนหน้าจอใบรับของ",
         pre="ทำ TC-GP-SLB-02 เสร็จแล้ว",
         steps=["เปิดใบสั่งซื้อ กดปุ่มสมาร์ท Receive แล้วกด Details ที่แถว Slab",
                "กรอก กว้างแผ่น / ยาวแผ่น / สูง-หนาแผ่น ของแต่ละแถว (4 แถว) แล้วกด Save",
                "กด Validate"],
         sample="แผ่น 1 = 1.58 / 2.95 / 0.02 · แผ่น 2 = 1.60 / 3.00 / 0.02 · แผ่น 3 = 1.55 / 2.90 / 0.02 · แผ่น 4 = 1.60 / 3.00 / 0.02",
         expected="ใบรับของเป็น Done (เช่น EG01/IN/00744) · ได้ Slab 4 แผ่น SLB-26-0389 ถึง SLB-26-0392 ขนาดตามที่กรอก · มูลค่าสต็อกต่อแผ่น 6,059.30 · 6,240.00 · 5,843.50 · 6,240.00 รวม 24,382.80 (พื้นที่จริง 18.756 ตร.ม. × 1,300)",
         prio="High", shot=SHOT + "k02-details-filled.webp"),
  ]),
  dict(cat_id="B", title="B. ขายและส่งของ",
       subtitle="ใบเสนอราคาเลือก Slab ทีละแผ่น · ส่งของสแกน Serial · 2 test cases",
       cases=[
    dict(id="TC-GP-SLB-04", scenario="ทำใบเสนอราคาขาย Slab โดยเลือกแผ่นทีละแผ่น แล้ว Confirm",
         note="ราคาคิดจากพื้นที่จริงของแผ่นที่เลือก ไม่ใช่ขนาดมาตรฐาน 4.80 ตร.ม. ต่อแผ่น · ตัวเลขชั่วคราว 12,000 ก่อนเลือกแผ่นจะถูกแทนที่",
         pre="ทำ TC-GP-SLB-03 เสร็จแล้ว · มีลูกค้า Demo Hotel Customer",
         steps=["เปิดแอป Sales &gt; Orders &gt; Quotations &gt; New เลือก Customer",
                "กด Add a product เลือกสินค้า Slab เลือก Finish แล้วกด Confirm ในหน้าต่าง และกด Save",
                "ที่ท้ายบรรทัดสินค้ากดปุ่มเลือก Slab / Lot แล้ว Add a line เลือกแผ่นทีละแผ่นให้ครบ 4 แผ่น กด ยืนยันการเลือก",
                "กด Confirm"],
         sample="Customer = Demo Hotel Customer · ZZ2 GUIDE MARBLE - Slab (Polished) · แผ่น SLB-26-0389 ถึง SLB-26-0392",
         expected="หน้าต่างเลือกแสดงพื้นที่ 4.66 · 4.80 · 4.50 · 4.80 รวม 18.76 ตร.ม. · บรรทัดสินค้า \"4 แผ่น = 18.76 ตร.ม. · 2,500 ฿/ตร.ม.\" · ราคา 11,725.00 ต่อแผ่น · ก่อน VAT 46,900.00 · VAT 7% 3,283.00 · รวม 50,183.00 · สถานะ Sales Order (เช่น S01692) · ปุ่มสมาร์ท Delivery 1 และ Slabs 4",
         prio="High", shot=SHOT + "k03-select-slabs.webp"),
    dict(id="TC-GP-SLB-05", scenario="ส่งของโดยสแกน Serial ทุกแผ่น แล้วตรวจสถานะ Slab",
         note="ต้องสแกนหรือพิมพ์ Serial ให้ตรงกับแผ่นในคอลัมน์ Pick From ของแต่ละแถว ครบทุกแถว",
         pre="ทำ TC-GP-SLB-04 เสร็จแล้ว",
         steps=["ที่ใบสั่งขาย กดปุ่มสมาร์ท Delivery แล้วกด Details ที่แถวสินค้า",
                "ที่คอลัมน์ Scanned Serial ของแต่ละแถว พิมพ์ Serial ให้ตรงกับแผ่นใน Pick From ครบ 4 แถว แล้วกด Save",
                "กด Validate",
                "เปิดแผ่น SLB-26-0389 ที่ Stone Slab &gt; Slabs &gt; All Slabs (ลบตัวกรอง Available ถ้าหาไม่เจอ)"],
         sample="SLB-26-0389 ถึง SLB-26-0392 · ใบส่งของ EG01/OUT/00715",
         expected="ใบส่งของ Ready ก่อนกด เป็น Done หลัง Validate Quantity 4.00 · แผ่น SLB-26-0389: ป้าย Sold · ที่เก็บ Customers - Stone · \"ถูกเลือกในใบขาย: S01692\" · ต้นทุน 6,059.30 บาท · ปุ่มสมาร์ท Sales 1 / Purchases 1 / Transfers 1",
         prio="High", shot=SHOT + "k04-slab-sold.webp"),
  ]),
  dict(cat_id="C", title="C. ใบแจ้งหนี้และต้นทุน",
       subtitle="ออกใบแจ้งหนี้ ระบบลงต้นทุนขายให้ · 1 test case",
       cases=[
    dict(id="TC-GP-SLB-06", scenario="ออกใบแจ้งหนี้และตรวจรายการบัญชี (รายได้ ต้นทุนขาย)",
         note="ต้นทุนขาย 24,382.80 = ผลรวมมูลค่าสต็อกของ 4 แผ่นที่ขาย · กำไรขั้นต้น 46,900.00 − 24,382.80 = 22,517.20 บาท",
         pre="ทำ TC-GP-SLB-05 เสร็จแล้ว",
         steps=["ที่ใบสั่งขาย กด Create Invoice เลือก Regular invoice แล้วกด Create Draft",
                "กด Confirm",
                "เปิดแท็บ Journal Items"],
         sample="ใบสั่งขาย S01692 · Regular invoice",
         expected="ใบแจ้งหนี้ (เช่น INV/2026/00003) Posted · Quantity 4.000 Units × 11,725.00 · ก่อน VAT 46,900.00 · VAT 3,283.00 · รวม 50,183.00 · Journal Items: เดบิต 112100 ลูกหนี้ 50,183.00 · เครดิต 411100 รายได้ขาย 46,900.00 · เครดิต 213200 VAT ขาย 3,283.00 · เดบิต 511110 ต้นทุนขาย 24,382.80 · เครดิต 113120 สต็อก Slab สำเร็จรูป 24,382.80 · เดบิตรวม = เครดิตรวม 74,565.80",
         prio="High", shot=SHOT + "k04-journal.webp"),
  ]),
]
