# Single source of truth for the EMG-O Golden Path "ตู้คอนเทนเนอร์: สั่งซื้อ Block → ผูกตู้ → ค่าขนส่ง → ต้นทุนเข้า Block".
#
# Data provenance: run end to end on `eg-tst`, 2026-11-01, driven by Playwright as emgdemo (company Empire Granite).
# Fixture: container ZZ2-CNT-01 (id 61) -> PO P00619 (ZZ2 GUIDE MARBLE - Block, 34.66 ton @ 12,000) -> receipt EG01/IN/00741
# -> Blocks BLK-26-1480 (3.00x1.60x1.50 m, 19.08 t) + BLK-26-1481 (2.80x1.50x1.40 m, 15.58 t) -> bill BILL/2026/11/0010 (13,080)
# -> landed cost LC/2026/0057 + entry STJ/2026/11/0013 -> container closed and reopened.
# Same run produced the click-along guide guide-container-2026-11-01.html (shots shared in qa/assets/container-guide/).
#
# Scope: happy path only. Cancelling a booked bill (auto reversal), the delete guard, several bills / USD bills and cutting the Block
# into Slabs are NOT cases here (error/edge paths, or covered by test-cases-golden-path-block-purchase-to-cut).
# Column model per case: id, scenario, note (optional callout), pre, steps (list), sample, expected, prio, shot.

SHOT = "assets/container-guide/"

CATEGORIES = [
  dict(cat_id="A", title="A. เตรียมตู้และรับ Block",
       subtitle="สร้างตู้ · สั่งซื้อและรับ Block 2 ก้อน · ผูก Block เข้าตู้และกดตู้ถึงแล้ว · 3 test cases",
       cases=[
    dict(id="TC-GP-CNT-01", scenario="สร้างตู้คอนเทนเนอร์ใบใหม่",
         note="ระบบสร้าง Analytic Account (กลุ่ม Import Group) ชื่อเดียวกับเลขตู้ให้เอง",
         pre="เข้าระบบเป็น Empire Granite · มีผู้ขาย Demo Stone Supplier",
         steps=["เปิดแอป Stone Slab &gt; Containers แล้วกด New",
                "กรอกเลขตู้ ชื่อตู้ เลือกผู้ขาย และวันที่คาดว่าถึง",
                "กด Save"],
         sample="Container Number = ZZ2-CNT-01 · Container Name = ZZ2 Guide Container 01 · Supplier = Demo Stone Supplier · Expected Date = 15 พ.ย.",
         expected="บันทึกสำเร็จ เลขตู้ขึ้นที่แถบนำทาง · สถานะ Pending · Landed Cost Total = 0.00 · Total Weight = 0.00 · มี Analytic Account ชื่อ ZZ2-CNT-01",
         prio="High", shot=SHOT + "c01-container-saved.webp"),
    dict(id="TC-GP-CNT-02", scenario="สั่งซื้อ Block เป็นตัน รับของ 2 ก้อน แล้ว Validate ให้ระบบสร้าง Block",
         note="ไม่ต้องกรอกช่อง Container / Import Group ที่หัวใบสั่งซื้อสำหรับ Block · กด Tab ที่ช่องสุดท้ายของ Details อาจเปิดแถวว่าง 0.000 เพิ่ม ระบบข้ามแถวว่างเอง",
         pre="ทำคู่มือ Setup ระบบตอน 2 แล้ว มีสินค้า ZZ2 GUIDE MARBLE - Block",
         steps=["เปิดแอป Purchase &gt; Orders &gt; Requests for Quotation &gt; New เลือก Vendor กด Add a product เลือก Block กรอก Qty (Ton) และ Price / Ton แล้วกด Confirm Order",
                "กด Receive แล้วกด Details ที่แถว Block",
                "แถวแรกกรอก ยาว / กว้าง / สูง และ ตันตามใบส่งของ แล้วกด Add a line กรอกก้อนที่สอง จากนั้นกด Save",
                "กด Validate (ถ้าถามเรื่อง Backorder เลือก No Backorder)"],
         sample="Vendor = Demo Stone Supplier · ZZ2 GUIDE MARBLE - Block · Qty (Ton) = 34.66 · Price / Ton = 12,000 · ก้อนที่ 1 = 3.00 × 1.60 × 1.50 ม. 19.080 ตัน · ก้อนที่ 2 = 2.80 × 1.50 × 1.40 ม. 15.580 ตัน",
         expected="ใบสั่งซื้อ: Quantity 13.0792 m³ · Unit Price 31,800.00 · ก่อน VAT 415,918.56 · รวม 445,032.86 · ใบรับของเป็น Done · ได้ Block 2 ก้อน ปริมาตร 7.20 และ 5.88 ลบ.ม. น้ำหนัก 19.08 และ 15.58 ตัน ต้นทุนซื้อ 31,800 ต่อ ลบ.ม. (เช่น BLK-26-1480 และ BLK-26-1481)",
         prio="High", shot=SHOT + "c02-receipt-done.webp"),
    dict(id="TC-GP-CNT-03", scenario="ผูก Block เข้าตู้ แล้วกดตู้ถึงแล้ว",
         note="Block เกิดจากใบรับของ ไม่ได้เข้าตู้เอง ต้องผูกเอง · ผลรวมราคาซื้อบนตู้ 415,944.00 ต่างจากยอดใบสั่งซื้อ 415,918.56 เล็กน้อย เพราะสั่ง 13.0792 ลบ.ม. แต่วัดจริงรวม 13.08 ลบ.ม.",
         pre="ทำ TC-GP-CNT-01 และ TC-GP-CNT-02 เสร็จแล้ว",
         steps=["เปิดแอป Stone Slab &gt; Containers เปิดตู้ แท็บ Blocks กด Link Existing Block",
                "เลือก Block ทั้ง 2 ก้อน แล้วกด Link",
                "กดปุ่ม ตู้ถึงแล้ว"],
         sample="ตู้ ZZ2-CNT-01 · Block BLK-26-1480 และ BLK-26-1481",
         expected="แท็บ Blocks มี 2 แถว: 7.20 ลบ.ม. / 19.08 ตัน / ราคาซื้อ 228,960.00 และ 5.88 / 15.58 / 186,984.00 · รวม 13.08 ลบ.ม. 34.66 ตัน 415,944.00 · สถานะตู้เป็น Arrived · Arrival Date เป็นวันนี้ · Total Weight (Ton) = 34.66",
         prio="High", shot=SHOT + "c02-container-arrived.webp"),
  ]),
  dict(cat_id="B", title="B. ค่าขนส่งและต้นทุน",
       subtitle="บันทึกใบแจ้งหนี้ค่าขนส่งและลงต้นทุนเข้า Block · ดูต้นทุนต่อ Block · ดูรายการบัญชี · 3 test cases",
       cases=[
    dict(id="TC-GP-CNT-04", scenario="บันทึกใบแจ้งหนี้ค่าขนส่ง ผูกกับตู้ แล้วลงต้นทุนเข้า Block",
         note="ใบแจ้งหนี้ต้องสร้างที่เมนูบัญชี ไม่ใช่ที่ใบสั่งซื้อ · ต้อง Confirm (Post) ก่อน · Bill Date เป็นช่องบังคับ · แบ่งค่าขนส่งตามปริมาตร (ลบ.ม.) ของ Block อย่างเดียว",
         pre="ทำ TC-GP-CNT-03 เสร็จแล้ว · มีสินค้าบริการ ZZ ค่าระวางและขนส่งตู้คอนเทนเนอร์ (Service ซื้อได้)",
         steps=["เปิดแอป Accounting &gt; Vendors &gt; Bills &gt; New เลือก Vendor กรอก Bill Date เพิ่มบรรทัดสินค้าค่าขนส่ง กรอกราคา แล้วกด Confirm",
                "กลับที่ตู้ ช่อง Landed Cost Bills เลือกบิลที่ Post แล้ว แล้วกด Save",
                "กดปุ่ม ลงต้นทุนค่าขนส่งเข้าสต็อก"],
         sample="Vendor = Demo Stone Supplier · ZZ ค่าระวางและขนส่งตู้คอนเทนเนอร์ ราคา 13,080 (1,000 บาทต่อ ลบ.ม.)",
         expected="บิลสถานะ Posted: ก่อน VAT 13,080.00 · VAT 7% 915.60 · รวม 13,995.60 · ที่ตู้ Landed Cost Total = 13,080.00 · หลังกดปุ่มขึ้นข้อความ \"ลงต้นทุนค่าขนส่งของ Bill ที่ Post แล้วเรียบร้อย\" · แท็บ Blocks: ค่าขนส่งก้อนที่ 1 = 7,200.00 ก้อนที่ 2 = 5,880.00 · ต้นทุนรวม 236,160.00 และ 192,864.00 · เกิดเอกสาร Landed Cost 1 ใบ (เช่น LC/2026/0057)",
         prio="High", shot=SHOT + "c03-after-apply.webp"),
    dict(id="TC-GP-CNT-05", scenario="ตรวจการแบ่งค่าขนส่งและต้นทุนต่อ Block ที่แท็บ ค่าใช้จ่าย / บัญชี",
         pre="ทำ TC-GP-CNT-04 เสร็จแล้ว",
         steps=["เปิดตู้ แล้วเปิดแท็บ ค่าใช้จ่าย / บัญชี",
                "ดูรายการค่าใช้จ่ายของตู้และตารางการแบ่งค่าขนส่ง"],
         sample="ตู้ ZZ2-CNT-01",
         expected="รายการค่าใช้จ่าย: BILL/2026/11/0010 บัญชี 511100 จำนวน 13,080.00 · ตารางแบ่ง: ก้อนที่ 1 สัดส่วน CBM 55.05% ค่าขนส่ง 7,200.00 ราคาซื้อ 228,960.00 ต้นทุนรวม 236,160.00 · ก้อนที่ 2 สัดส่วน 44.95% ค่าขนส่ง 5,880.00 ราคาซื้อ 186,984.00 ต้นทุนรวม 192,864.00 · รวม ค่าขนส่ง 13,080.00 ราคาซื้อ 415,944.00 ต้นทุนรวม 429,024.00 · ต้นทุนต่อตัน 12,377.36 และ 12,378.95",
         prio="High", shot=SHOT + "c04-cost-tab.webp"),
    dict(id="TC-GP-CNT-06", scenario="ดูรายการบัญชีของตู้ และเอกสาร Landed Cost",
         note="ค่าขนส่งถูกย้ายจากค่าใช้จ่ายไปบวกในมูลค่าสต็อก Block · มูลค่าเดิมของก้อนที่ 2 ในเอกสาร Landed Cost คือ 186,960.00 (น้ำหนักตัน × ราคาต่อตัน) ต่างจาก 186,984.00 ที่แท็บ Blocks 24 บาท เพราะคิดคนละฐาน (ตันกับลูกบาศก์เมตร)",
         pre="ทำ TC-GP-CNT-04 เสร็จแล้ว",
         steps=["ที่ตู้ กดปุ่ม ดูรายการบัญชี แล้วกดขยายทั้ง 2 กลุ่ม",
                "เปิดแอป Inventory &gt; Operations &gt; Landed Costs เปิดเอกสารของบิลนี้ แล้วเปิดแท็บ Valuation Adjustments"],
         sample="BILL/2026/11/0010 · LC/2026/0057",
         expected="กลุ่มบิล BILL/2026/11/0010: เดบิต 511100 ค่าขนส่ง 13,080.00 · เดบิต 114200 ภาษีซื้อ 915.60 · เครดิต 212100 เจ้าหนี้ 13,995.60 · กลุ่ม STJ/2026/11/0013: เดบิต 113110 Inventory - Stone Blocks 7,200.00 และ 5,880.00 · เครดิต 511100 7,200.00 และ 5,880.00 · เดบิตรวมเท่ากับเครดิตรวม (27,075.60) · เอกสาร Landed Cost สถานะ Posted อ้างถึง EG01/IN/00741 และ BILL/2026/11/0010 · มูลค่าสต็อก 228,960 → 236,160 (+7,200) และ 186,960 → 192,840 (+5,880)",
         prio="Medium", shot=SHOT + "c04-journal.webp"),
  ]),
  dict(cat_id="C", title="C. ปิดตู้",
       subtitle="ปิดตู้เมื่อบิลครบ และเปิดกลับมาได้ · 1 test case",
       cases=[
    dict(id="TC-GP-CNT-07", scenario="ปิดตู้ แล้วเปิดตู้อีกครั้ง",
         pre="ทำ TC-GP-CNT-04 เสร็จแล้ว",
         steps=["ที่ตู้ กดปุ่ม ปิดตู้ แล้วกด Ok ในหน้าต่างยืนยัน",
                "ดูสถานะและปุ่มบนหน้าตู้",
                "กดปุ่ม เปิดตู้อีกครั้ง"],
         sample="ตู้ ZZ2-CNT-01",
         expected="หน้าต่างถาม \"ปิดตู้แล้วจะแก้ไขข้อมูล ผูก Block หรือผูก Bill เพิ่มไม่ได้ (เปิดตู้อีกครั้งได้) ยืนยันปิดตู้?\" · หลัง Ok สถานะ Closed · ปุ่ม Link Existing Block และปุ่มลงต้นทุนหายไป เหลือ ดูรายการบัญชี และ เปิดตู้อีกครั้ง · หลังเปิดอีกครั้งสถานะกลับเป็น Arrived",
         prio="Medium", shot=SHOT + "c05-closed.webp"),
  ]),
]
