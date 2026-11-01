# Single source of truth for the EMG-O Golden Path "Block: สั่งซื้อ → รับของ → ต้นทุน → ใบแจ้งหนี้และแก้ขนาด → ตัดเป็น Slab".
#
# Data provenance: run end to end on `eg-tst`, 2026-11-01, driven by Playwright as emgdemo (company Empire Granite).
# Fixture: PO P00624 (ZZ2 GUIDE MARBLE - Block, 32.70 ton @ 12,000) -> receipt EG01/IN/00746 -> Blocks BLK-26-1486 (2.90x1.60x1.50 m, 18.10 t)
# + BLK-26-1487 (2.70x1.50x1.40 m, 14.60 t) -> bill BILL/2026/11/0013 (392,400) -> BLK-26-1487 height corrected to 1.30 m
# -> cut order EG01/STCUT/00427 on BLK-26-1486 -> 8 Slabs BLK-26-1486-1..8.
# Same run produced the click-along guide guide-block-2026-11-01.html (shots shared in qa/assets/block-guide/).
#
# Scope: happy path only. Sales of a whole Block, return to vendor, cut from a sale line, plan larger than the Block, Confirm before moving the
# Block, cancelling the cut order, and containers (see test-cases-golden-path-container) are NOT cases here.
# Column model per case: id, scenario, note (optional callout), pre, steps (list), sample, expected, prio, shot.

SHOT = "assets/block-guide/"

CATEGORIES = [
  dict(cat_id="A", title="A. รับ Block เข้าคลัง",
       subtitle="สั่งซื้อ Block เป็นตัน · รับของและกรอกขนาด · ดูต้นทุนในหน้า Block · 3 test cases",
       cases=[
    dict(id="TC-GP-BLK-01", scenario="สั่งซื้อ Block เป็นตัน และยืนยันใบสั่งซื้อ",
         note="Block ซื้อเป็นตัน ระบบแปลงเป็นลูกบาศก์เมตรให้เอง (÷ 2.65) · ช่อง Container / Import Group ที่หัวใบสั่งซื้อไม่ต้องกรอกสำหรับ Block",
         pre="เข้าระบบเป็น Empire Granite · ทำคู่มือ Setup ระบบตอน 2 แล้ว มีสินค้า ZZ2 GUIDE MARBLE - Block · มีผู้ขาย Demo Stone Supplier",
         steps=["เปิดแอป Purchase &gt; Orders &gt; Requests for Quotation แล้วกด New",
                "เลือก Vendor กด Add a product เลือกสินค้า Block กรอก Qty (Ton) และ Price / Ton",
                "กด Confirm Order"],
         sample="Vendor = Demo Stone Supplier · ZZ2 GUIDE MARBLE - Block · Qty (Ton) = 32.70 · Price / Ton = 12,000",
         expected="Quantity 12.3396 m³ · Unit Price 31,800.00 · ก่อน VAT 392,399.28 · สถานะเป็น Purchase Order (เช่น P00624) · มีปุ่มสมาร์ท Receive",
         prio="High", shot=SHOT + "b01-po-confirmed.webp"),
    dict(id="TC-GP-BLK-02", scenario="รับของ กรอกขนาด Block 2 ก้อน แล้ว Validate ให้ระบบสร้าง Block",
         note="ไม่ต้องสร้าง Block เองก่อนรับของ ไม่เช่นนั้นจะซ้ำ · กด Tab ที่ช่องสุดท้ายของ Details อาจเปิดแถวว่างเพิ่ม ระบบข้ามแถวว่างเอง · คอลัมน์ Qty (Ton) ในใบรับของแสดงตันตามใบส่งของที่กรอก (ไม่กรอก = ปริมาตร × 2.65) และขึ้นแถบเตือนถ้าต่างจากปริมาตร × 2.65 เกิน 3%",
         pre="ทำ TC-GP-BLK-01 เสร็จแล้ว",
         steps=["เปิดใบสั่งซื้อ กดปุ่มสมาร์ท Receive แล้วกด Details ที่แถว Block",
                "แถวแรกกรอก ยาว / กว้าง / สูง และ ตันตามใบส่งของ แล้วกด Add a line กรอกก้อนที่สอง จากนั้นกด Save",
                "กด Validate (ถ้าถามเรื่อง Backorder เลือก No Backorder)"],
         sample="ก้อนที่ 1 = 2.90 × 1.60 × 1.50 ม. 18.100 ตัน · ก้อนที่ 2 = 2.70 × 1.50 × 1.40 ม. 14.600 ตัน",
         expected="ปริมาตรต่อแถว 6.96 และ 5.67 ลบ.ม. (รวม 12.63) · ใบรับของเป็น Done (เช่น EG01/IN/00746) · Qty (Ton) ในใบรับของ 18.10 และ 14.60 (ตรงกับตันตามใบส่งของ) · ได้ Block 2 ก้อน (เช่น BLK-26-1486 และ BLK-26-1487)",
         prio="High", shot=SHOT + "b02-receipt-done.webp"),
    dict(id="TC-GP-BLK-03", scenario="ตรวจต้นทุน ขนาด และแถบเตือนในหน้า Block",
         note="แถบเตือนสีเหลืองเกิดเพราะปริมาตรที่วัดจริงรวม (12.63) เกินปริมาตรที่แปลงจากตันที่สั่ง (12.34) ถ้าเกิดจากการวัดจริง ไม่ต้องทำอะไร · ตัวกรองเริ่มต้นของหน้า Blocks ซ่อน Block ที่ใช้หมดแล้ว",
         pre="ทำ TC-GP-BLK-02 เสร็จแล้ว",
         steps=["เปิดแอป Stone Slab &gt; Blocks พิมพ์รหัส Block ในช่องค้นหาแล้วกด Enter",
                "เปิดการ์ด Block ก้อนที่ 1 ดูการ์ดสรุปและแถบเตือนด้านบน",
                "ดูแท็บ ข้อมูล Block และตัวนับ Slab"],
         sample="Block BLK-26-1486",
         expected="ขนาด 2.90 × 1.60 × 1.50 ม. = 6.96 CBM · 18.10 ตัน · คงเหลือ 6.96 CBM · ต้นทุน 12,000 บาท/ตัน (31,800 บาท/CBM) · PO ต้นทาง P00624 · แถบเตือน \"Block ที่ผูกกับบรรทัด PO นี้รวม 12.63 m³ เกินที่สั่งซื้อไว้ 12.34 m³ ...\" · Purchase Order Line = P00624 · ตัวนับ Slab (Total/Available/Hold/Consigned/Sold) = 0",
         prio="High", shot=SHOT + "b03-block-card.webp"),
  ]),
  dict(cat_id="B", title="B. ใบแจ้งหนี้และแก้ขนาด",
       subtitle="ใบแจ้งหนี้ผู้ขายดึงจากใบสั่งซื้อ · แก้ขนาด Block ที่วัดผิด · 2 test cases",
       cases=[
    dict(id="TC-GP-BLK-04", scenario="สร้างใบแจ้งหนี้ผู้ขายจากใบสั่งซื้อ Block",
         note="บิลเขียนเป็นตัน ราคาบาทต่อตัน ยอดจึงเท่ากับตันที่รับ × ราคาต่อตัน เสมอ · Bill Date เป็นช่องบังคับ",
         pre="ทำ TC-GP-BLK-02 เสร็จแล้ว",
         steps=["เปิดแอป Accounting &gt; Vendors &gt; Bills &gt; New เลือก Vendor",
                "ช่อง Auto-Complete เลือกใบสั่งซื้อ แล้วกรอก Bill Date",
                "กด Confirm"],
         sample="Vendor = Demo Stone Supplier · Auto-Complete = P00624 · Bill Date = วันนี้",
         expected="บรรทัดเดียว: Quantity 32.700 ตัน · Price 12,000.00 · ก่อน VAT 392,400.00 (= 18.10 + 14.60 ตัน × 12,000) · VAT 7% 27,468.00 · รวม 419,868.00 · สถานะ Posted (เช่น BILL/2026/11/0013)",
         prio="High", shot=SHOT + "b04-bill-posted.webp"),
    dict(id="TC-GP-BLK-05", scenario="แก้ขนาด Block ที่วัดผิด และตรวจประวัติ",
         note="ปุ่ม แก้ขนาด ใช้ได้เฉพาะผู้มีสิทธิ์ Inventory Administrator · ต้องระบุเหตุผล · น้ำหนัก (ตัน) และต้นทุนต่อ CBM ไม่เปลี่ยนตามขนาด · ไม่แก้ใบแจ้งหนี้ที่ Post แล้ว · ระบบหักสต็อกส่วนต่าง 0.405 ลบ.ม. มูลค่า 12,514.29 บาท ซึ่งตรวจจากฐานข้อมูล ไม่แสดงบนหน้าจอ",
         pre="ทำ TC-GP-BLK-02 เสร็จแล้ว · เป็นผู้ใช้ที่มีสิทธิ์ Inventory Administrator",
         steps=["เปิด Block ก้อนที่ 2 กดปุ่ม แก้ขนาด",
                "แก้ สูงใหม่ (ม.) และพิมพ์ เหตุผลที่แก้ไข แล้วกดปุ่ม แก้ขนาด ในหน้าต่าง",
                "ดูการ์ดสรุป แล้วเปิดแท็บ ประวัติแก้ขนาด"],
         sample="Block BLK-26-1487 · สูงใหม่ = 1.30 · เหตุผล = วัดความสูงผิดตอนรับของ วัดซ้ำได้ 1.30 ม.",
         expected="ในหน้าต่าง ปริมาตรใหม่ = 5.265 และ ใช้ไปแล้ว = 0.00 · หลังแก้ การ์ดแสดง 2.70 × 1.50 × 1.30 = 5.265 CBM · 14.60 ตัน · ต้นทุน 12,000 บาท/ตัน (31,800 บาท/CBM) คงเดิม · แท็บ ประวัติแก้ขนาด 1 แถว: ความสูงเก่า 1.400 ใหม่ 1.300 · ปริมาตร 5.6700 → 5.2650 ผลต่าง -0.405 · เหตุผลตามที่พิมพ์",
         prio="High", shot=SHOT + "b04-resize-history.webp"),
  ]),
  dict(cat_id="C", title="C. ตัด Block เป็น Slab",
       subtitle="ใบสั่งตัดจาก สร้างงานผลิต · ได้ Slab 1 Lot ต่อแผ่น · 1 test case",
       cases=[
    dict(id="TC-GP-BLK-06", scenario="ตัด Block เป็น Slab ด้วยใบสั่งตัด (ไม่มีใบขาย)",
         note="ต้องกด สร้างแผนใหม่ หลังเปลี่ยนความหนา ไม่เช่นนั้นแผนยังเป็น 80 แผ่นหนา 2 ซม. · แผ่นละ 0.1305 ลบ.ม. × 53 = 6.917 ลบ.ม. เหลือเศษ 0.043 · ตรวจจากฐานข้อมูล: ต้นทุนของ Block ที่ใช้ไป 215,858.10 บาท ถูกยกไปเป็นต้นทุน Slab 53 แผ่นรวม 215,858.10 บาท",
         pre="ทำ TC-GP-BLK-02 เสร็จแล้ว · มีสินค้า ZZ2 GUIDE MARBLE - Slab",
         steps=["เปิดแอป Stone Slab &gt; สร้างงานผลิต เลือก ตัด Block เป็น Slab เลือก Block แล้วกด เริ่มงาน",
                "เลือกผิวหน้า ความหนา (3 cm) และเหตุผล แล้วกด สร้างแผนใหม่ และ Ok",
                "กด ย้ายไปสถานีตัด แล้วกด Confirm",
                "เปิดแท็บ Slab ที่ตัดได้ (แผน/จริง) ตรวจขนาด แล้วกด ตัดเสร็จ",
                "เปิด Block แล้วดูแท็บ Slabs"],
         sample="Block BLK-26-1486 · ผิว Polished · ความหนา = 3 cm · เหตุผล = อื่นๆ (Other) · ขนาดแผ่น 2.90 × 1.50 ม. (ค่าเริ่มต้น)",
         expected="ก่อนสร้างแผนใหม่: ประมาณ 80 แผ่น 348.00 ตร.ม. · หลัง: 53 แผ่น 230.55 ตร.ม. · ย้ายสำเร็จ (6.960 หน่วย ไป Stone Production) · ตาราง 53 แถว แผน=จริง 2.90 × 1.50 × 0.03 · \"Complete Cut สำเร็จ ... ตัดได้ 53 แผ่นจาก BLK-26-1486\" · สถานะ Done · ตัดได้จริง 53 แผ่น 230.55 ตร.ม. (100% ของแผน) · Block เหลือ 0.043 CBM ป้าย ใช้ได้ · Slabs Total 53 / Available 53 · BLK-26-1486-1 ถึง -53 ขนาด 2.90 × 1.50 × 0.030 ม. = 4.35 ตร.ม.",
         prio="High", shot=SHOT + "b05-block-slabs.webp"),
  ]),
]
