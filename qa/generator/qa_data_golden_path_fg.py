# Single source of truth for EMG-O Golden Path test cases — "FG" (ชุดที่ 3 จาก 3:
# Block -> Slab -> FG), rebuilt after ADR-087 "Slab = Lot" (รอบ Slab-Lot, 2026-10-05).
#
# This is story 3. Stories 1-2 left 80 Slab lots BLK-26-0006-1..80 (3.00 x 1.25 x 0.02 m,
# cost 1,215 each) in Stone Available; this story sells a Countertop (m2) made from them.
#
# Golden Path discipline (see feedback_golden_path_test_case memory): happy path only,
# no field-validation/error cases, every step phrased for a non-technical user.
# Cut by the user's earlier call: returns of FG are not part of this story.
#
# SCOPE NOTE — เจดีย์บัว (custom carved FG, Serial) is NOT a case here. Run live on
# 2026-10-05 it cannot finish through the screens: the product had no "FG Raw Material"
# (set during the run), the Sale Order made an FG Production that "Complete FG Production"
# refuses ("Serial FG is not available yet"), and the Cutting Plan -> Assembly chain it is
# meant to use (Phase 5b) can only be created by code today — there is no button for it.
# Reported as an observation, no product code was changed.
#
# Data provenance: fresh live run, 2026-10-05, driven through the real Odoo web UI
# (Playwright, headless Chromium) on `eg-tst` (https://eg-tst.mx-erp.com, company
# Empire Granite, user admin), code v2.106 on branch test/emg-erp-ee. What this run created:
#   SO S00178 (Demo Hotel Customer): GP Block Marble Countertop 3.48 m2 @ 12,000 = 41,760.00
#   + Edge 3.60 m @ 350 + Cut-out hob 1,500 + Cut-out sink 1,200 -> 45,720.00 + VAT 7% = 48,920.40
#   FG Production EG01/STFG/00034 -> Slab lots BLK-26-0006-3, -4 consumed (7.50 m2 for 3.48 m2 of pieces)
#   FG lots FG-EG01/STFG/00034-01..03 (2.40x0.65, 1.20x0.60, 2.00x0.60), cost 1,153.44 = 331.45/m2
#   Offcuts OC-EG01/STFG/00034-01 (1.20x1.20, 466.56) and -02 (2.00x1.25, 810.00) -> inspected -> Available
#   Delivery EG01/OUT/00062, invoice INV/2026/00006 (Posted).
#   Left behind: BLK-26-0006-5 sits in Stone Production (moved for an abandoned เจดีย์บัว attempt, S00179 cancelled);
#   เจดีย์บัว product now has FG Raw Material = GP Block Marble, price 8,500, VAT 7%.
#
# Column model per case: id, scenario, note (optional amber callout), pre, steps (list),
# sample ('-' if nothing to key), expected, prio, shot (screenshot path, clickable).

SHOT = "assets/golden-path-fg/"

CATEGORIES = [
  dict(cat_id="F1", title="F1. ใบสั่งขาย Countertop (ท็อปครัว)",
       subtitle="เปิดใบสั่งขาย → ใส่รายการชิ้นงานและงานแปรรูป → ตรวจราคา → Confirm · 5 test cases",
       cases=[
    dict(id="TC-GP-FG-01", scenario="สร้างใบสั่งขาย แล้วเลือกสินค้า Countertop",
         note="Countertop คิดเป็นตารางเมตร (m²) ตามชิ้นงานที่ลูกค้าสั่ง ไม่ใช่เป็นแผ่น — ตอนเลือกสินค้า จำนวนจะขึ้น 1.00 m² ไว้ก่อน แล้วถูกแทนที่ด้วยพื้นที่รวมของชิ้นงานในขั้นถัดไป",
         pre="มีลูกค้า (Demo Hotel Customer) และสินค้า Countertop ที่ผูกกับวัสดุแล้ว (GP Block Marble ราคา 12,000 ต่อ m²)",
         steps=["เปิดแอป Sales &gt; Orders &gt; Quotations &gt; New",
                "เลือก Customer",
                "กด \"Add a product\" เลือกสินค้า Countertop",
                "กด Save"],
         sample="Customer = Demo Hotel Customer · Product = GP Block Marble",
         expected="ใบเสนอราคาใหม่ (ตัวอย่างจริง S00178) มีบรรทัดสินค้า GP Block Marble หน่วย m² ราคา 12,000.00 ต่อหน่วย และมีไอคอนรายการชิ้นงานบนบรรทัด",
         prio="High", shot=SHOT + "gp-fg-01-so-product.png"),
    dict(id="TC-GP-FG-02", scenario="ใส่รายการชิ้นงาน (กว้าง × ยาว ของแต่ละชิ้น)",
         pre="ทำ TC-GP-FG-01 เสร็จแล้ว และกด Save แล้ว",
         steps=["กดไอคอนรายชิ้น (ไอคอนรายการ) บนบรรทัดสินค้า",
                "กดปุ่ม \"New\" แล้วกรอกรหัสชิ้น กว้าง ยาว และจำนวน",
                "ทำซ้ำจนครบทุกชิ้น แล้วปิดหน้าต่าง"],
         sample="A ท็อปครัว 2.40 × 0.65 · B เกาะกลาง 1.20 × 0.60 · C ท็อปอ่างล้างจาน 2.00 × 0.60 (ชิ้นละ 1)",
         expected="ตารางรายชิ้นแสดง 3 ชิ้น พื้นที่ 1.56 + 0.72 + 1.20 = 3.48 ตร.ม. และจำนวนในใบสั่งขายเปลี่ยนเป็น 3.48 m² ตามพื้นที่จริงอัตโนมัติ",
         prio="High", shot=SHOT + "gp-fg-02-pieces.png"),
    dict(id="TC-GP-FG-03", scenario="เพิ่มงานแปรรูป (ขอบ / เจาะช่อง) ให้แต่ละชิ้น",
         pre="ทำ TC-GP-FG-02 เสร็จแล้ว",
         steps=["ที่แถวของชิ้นงาน กดไอคอนประแจ (งานแปรรูป)",
                "กด \"Add a line\" เลือกงานแปรรูป (เช่น งานขอบ โค้งมน) แล้วติ๊กด้านที่ทำขอบ",
                "เพิ่มงานเจาะ/ตัดช่อง เลือกประเภท (ช่องเตา / ช่องซิงค์)",
                "กด Save — ทำซ้ำกับชิ้นอื่น"],
         sample="A: ขอบโค้งมนด้านกว้าง 1 (2.40 ม.) + ตัดช่องเตา · B: ขอบโค้งมนด้านกว้าง 1 (1.20 ม.) · C: ตัดช่องซิงค์",
         expected="ระบบคำนวณความยาวขอบให้เองจากด้านที่ติ๊ก (A = 2.400, B = 1.200) และงานเจาะนับเป็นจุด (1.000) — ราคาตามชนิดงานแต่ละแบบ",
         prio="High", shot=SHOT + "gp-fg-03-ops.png"),
    dict(id="TC-GP-FG-04", scenario="ตรวจใบเสนอราคา — งานแปรรูปกลายเป็นบรรทัดบริการให้เอง",
         pre="ทำ TC-GP-FG-03 เสร็จแล้ว",
         steps=["กลับมาที่หน้าใบเสนอราคา ดูบรรทัดสินค้าและยอดรวม"],
         sample="-",
         expected="ใต้บรรทัดหิน 3.48 m² = 41,760.00 มีบรรทัดบริการเพิ่มให้เอง: งานขอบ โค้งมน 3.60 ม. @ 350 = 1,260.00 · งานเจาะ (ช่องเตา) 1 จุด = 1,500.00 · งานเจาะ (ช่องซิงค์) 1 จุด = 1,200.00 — รวมก่อน VAT 45,720.00 + VAT 7% = 48,920.40 บาท",
         prio="High", shot=SHOT + "gp-fg-04-quotation-total.png"),
    dict(id="TC-GP-FG-05", scenario="กด Confirm ยืนยันใบสั่งขาย",
         pre="ทำ TC-GP-FG-04 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm"],
         sample="-",
         expected="ใบเสนอราคาเปลี่ยนเป็น Sales Order · มีสมาร์ทปุ่มใหม่ \"Delivery 1\" และ \"FG Production 1\" ที่ด้านบน (ระบบสร้างใบสั่งผลิตฉบับร่างให้เองทันที)",
         prio="High", shot=SHOT + "gp-fg-05-confirmed.png"),
  ]),
  dict(cat_id="F2", title="F2. ผลิต Countertop (FG Production)",
       subtitle="เปิดใบสั่งผลิต → ระบบเลือก Slab ให้ → ย้ายไปสถานีผลิต → Confirm → บันทึกชิ้นที่ตัดได้ + เศษ → Complete · 6 test cases",
       cases=[
    dict(id="TC-GP-FG-06", scenario="เปิดใบสั่งผลิต FG — ระบบเลือก Slab ให้ครบพื้นที่",
         note="แถบเตือนสีส้มและแท็บ Components ยังแสดงแผ่นมาตรฐานตามสูตร (Honed 3 cm, Not Available) ไว้ก่อน — จะถูกแทนที่ด้วยแผ่นที่เลือกจริงตอน Confirm เป็นแค่ข้อความ ไม่กระทบการทำงาน",
         pre="ทำ TC-GP-FG-05 เสร็จแล้ว",
         steps=["บน Sales Order กดสมาร์ทปุ่ม \"FG Production\"",
                "เปิดแท็บ \"Slab ที่จะตัด\" ดูรายการ Slab และพื้นที่"],
         sample="-",
         expected="ใบสั่งผลิต EG01/STFG/00034 (Draft) — พื้นที่งาน 3.48 ตร.ม. · ต้องใช้รวมเผื่อเสีย 3.83 ตร.ม. (เผื่อเสีย 10% ตามที่ตั้งไว้ในบริษัท) · ระบบเลือก Slab ให้เอง 2 แผ่น (BLK-26-0006-3 และ -4 แผ่นละ 3.75 ตร.ม.) รวม 7.50 ตร.ม. พอสำหรับงาน",
         prio="High", shot=SHOT + "gp-fg-06-mo-sources.png"),
    dict(id="TC-GP-FG-07", scenario="ย้าย Slab ไปสถานีผลิต (ย้ายด่วน)",
         pre="ทำ TC-GP-FG-06 เสร็จแล้ว",
         steps=["กดปุ่ม \"ย้ายด่วน (Move to Production)\" บนใบสั่งผลิต"],
         sample="-",
         expected="ระบบแจ้งเตือนสีเขียว \"ย้ายสำเร็จ ย้าย 2 lot ไป Stone Production แล้ว — กด Confirm ได้เลย\" (Slab ทั้ง 2 แผ่นออกจาก Stone Available มาอยู่สถานีผลิต)",
         prio="High", shot=SHOT + "gp-fg-07-move-to-production.png"),
    dict(id="TC-GP-FG-08", scenario="กด Confirm ใบสั่งผลิต",
         note="แท็บ Work Orders มี 4 ขั้นตอน (ตัดตามแบบ → ทำขอบ → เจาะ/ตัดช่อง → ตรวจก่อนส่ง) แต่ไม่ต้องกด Start ทีละขั้นก็ปิดงานได้ ในชุดนี้ข้ามส่วนจับเวลา — ขั้นตอนเหล่านี้ไม่ได้ทดสอบ · ช่อง Component Status ยังขึ้น Not Available แม้ย้าย Slab มาแล้ว แต่ไม่ขวางการ Complete",
         pre="ทำ TC-GP-FG-07 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm"],
         sample="-",
         expected="ใบสั่งผลิตเป็น Confirmed · ข้อความนำทางสีฟ้าบอกขั้นถัดไป (กรอก FG Output แล้วกด Complete FG Production)",
         prio="High", shot=SHOT + "gp-fg-08-mo-confirmed.png"),
    dict(id="TC-GP-FG-09", scenario="ตรวจรายการชิ้นที่ตัดได้จริง (FG Output)",
         note="รายการนี้ถูกเติมให้จากชิ้นงานในใบสั่งขาย โรงงานแก้เฉพาะชิ้นที่ตัดออกมาไม่ตรง และความหนา 0.00 ไม่ต้องกรอก — ระบบใช้ความหนาของ Slab ที่ตัด (0.02 ม.) ให้เอง",
         pre="ทำ TC-GP-FG-08 เสร็จแล้ว",
         steps=["เปิดแท็บ \"FG Output\" ดูรายการ",
                "(ถ้าตัดจริงได้ขนาดต่างจากที่สั่ง แก้ Width/Length/Qty ในแถวนั้น)"],
         sample="ตัดได้ตรงตามสั่ง จึงไม่ต้องแก้",
         expected="มี 3 แถวตรงกับชิ้น A (2.40 × 0.65), B (1.20 × 0.60), C (2.00 × 0.60) พร้อมหมายเหตุงานแปรรูปของแต่ละชิ้น (เช่น งานขอบ × 2.4, ช่องเตา × 1) ให้ช่างอ่านตอนตัด",
         prio="High", shot=SHOT + "gp-fg-09-fg-output.png"),
    dict(id="TC-GP-FG-10", scenario="บันทึกเศษหินที่เหลือจากการตัด",
         pre="ทำ TC-GP-FG-09 เสร็จแล้ว",
         steps=["เปิดแท็บ \"เศษที่เหลือ\"",
                "กด \"Add a line\" เลือก Slab ต้นทาง ใส่ กว้าง ยาว จำนวนชิ้น",
                "ทำซ้ำสำหรับเศษแต่ละก้อน แล้วกด Save"],
         sample="เศษจาก -3: 1.20 × 1.20 (1 ชิ้น) · เศษจาก -4: 2.00 × 1.25 (1 ชิ้น)",
         expected="ตารางเศษแสดง 2 แถว พื้นที่ 1.44 และ 2.50 ตร.ม. รวม 3.94 ตร.ม. — คอลัมน์ต้นทุนยังเป็น 0.00 จนกว่าจะปิดงาน",
         prio="Medium", shot=SHOT + "gp-fg-10-offcut-entry.png"),
    dict(id="TC-GP-FG-11", scenario="กด Complete FG Production ปิดงานผลิต",
         note="หลังปิดงาน แท็บ Components ยังมีแถวแผ่นมาตรฐานตามสูตร (Honed 3 cm) ที่ Consumed 0.00 คู่กับแถวแผ่นจริงที่ใช้ (Polished 2 cm, Consumed 2.00) — เป็นแค่การแสดงผล ไม่กระทบสต็อก",
         pre="ทำ TC-GP-FG-10 เสร็จแล้ว",
         steps=["กดปุ่ม \"Complete FG Production\""],
         sample="-",
         expected="แจ้งเตือนสีเขียว \"Complete FG Production สำเร็จ EG01/STFG/00034 ผลิตสำเร็จ 3.48 หน่วย\" · ใบสั่งผลิตขึ้น Done · Quantity 3.48 / 3.48 · Slab 2 แผ่นถูกใช้ไป (Consumed 2.00) · ได้ FG 3 Lot ตามขนาดชิ้น (FG-EG01/STFG/00034-01 ถึง -03) เข้าสต็อกคลัง และต้นทุนรวม 1,153.44 บาท (331.45 ต่อ m²) = ค่า Slab 2,430.00 หักส่วนของเศษ 1,276.56",
         prio="High", shot=SHOT + "gp-fg-11-mo-done.png"),
  ]),
  dict(cat_id="F3", title="F3. เศษหินกลับเข้าสต็อก",
       subtitle="เศษที่เหลือกลายเป็น Lot ใหม่รอตรวจ → ตรวจแล้วนำกลับไปขาย · 2 test cases",
       cases=[
    dict(id="TC-GP-FG-12", scenario="ตรวจว่าเศษถูกบันทึกเป็น Lot ใหม่ในสถานะ \"รอตรวจ\"",
         pre="ทำ TC-GP-FG-11 เสร็จแล้ว",
         steps=["เปิดแอป Stone Slab &gt; Slabs &gt; All Slabs",
                "ลบตัวกรอง \"Available\" ออก แล้วค้นหา \"OC-EG01/STFG/00034\"",
                "เปิดเศษ OC-EG01/STFG/00034-01 ดู Location, Status และต้นทุน"],
         sample="OC-EG01/STFG/00034-01",
         expected="เศษแต่ละก้อนเป็น Lot ของตัวเอง ขนาดจริง (1.20 × 1.20 × 0.02 ม. = 1.44 ตร.ม.) · อยู่ที่ Stone Inventory/Returned - Inspect · Status \"Returned - Pending Inspection\" · ต้นทุน 466.56 บาท (ส่วนแบ่งตามพื้นที่) — ก้อนที่ 2 (2.00 × 1.25) ต้นทุน 810.00 บาท",
         prio="High", shot=SHOT + "gp-fg-12-offcut-pending.png"),
    dict(id="TC-GP-FG-13", scenario="ตรวจเศษแล้วนำกลับไปขายได้",
         note="ถ้าเศษแตกหรือใช้ไม่ได้ ให้กด \"ชำรุด — ตัดทิ้ง (Scrap)\" แทน (ไม่ได้ทดสอบในชุดนี้ เพราะนอก Happy Path)",
         pre="ทำ TC-GP-FG-12 เสร็จแล้ว",
         steps=["เปิดหน้าเศษที่สถานะ Returned - Pending Inspection",
                "กดปุ่ม \"ตรวจแล้ว — นำกลับไปขาย\" ด้านบนซ้าย",
                "ทำซ้ำกับเศษก้อนที่เหลือ"],
         sample="OC-EG01/STFG/00034-01 และ -02",
         expected="สถานะเปลี่ยนเป็น Available · Location เป็น Stone Inventory/Stone Available · ปุ่มตรวจแล้ว/ชำรุดหายไป · ต้นทุนยังเป็น 466.56 และ 810.00 บาทเท่าเดิม — เศษกลับมาขายเป็น Slab ขนาดเล็กได้",
         prio="Medium", shot=SHOT + "gp-fg-13-offcut-ok.png"),
  ]),
  dict(cat_id="F4", title="F4. ส่งของและเก็บเงิน Countertop",
       subtitle="ใบส่งของ → Validate → ใบแจ้งหนี้ → Post · 4 test cases",
       cases=[
    dict(id="TC-GP-FG-14", scenario="เปิดใบส่งของ ตรวจว่าระบบจอง FG ถูก Lot",
         pre="ทำ TC-GP-FG-11 เสร็จแล้ว",
         steps=["เปิด Sales Order กดสมาร์ทปุ่ม \"Delivery\"",
                "ที่แถวสินค้า กด \"Details\" ดูรายการ Lot"],
         sample="-",
         expected="ใบส่งของ EG01/OUT/00062 สถานะ Ready · Product Availability = Available · Detailed Operations ระบุ Lot ครบ 3 แถว: FG-EG01/STFG/00034-01 (1.56 m²), -02 (0.72 m²), -03 (1.20 m²) รวม 3.48 m² ตรงกับที่สั่ง — ไม่ต้องสแกนหรือเลือก Lot เอง",
         prio="High", shot=SHOT + "gp-fg-14-delivery-details.png"),
    dict(id="TC-GP-FG-15", scenario="กด Validate ส่งของ",
         pre="ทำ TC-GP-FG-14 เสร็จแล้ว",
         steps=["กดปุ่ม Validate บนใบส่งของ"],
         sample="-",
         expected="ใบส่งของขึ้น Done · Quantity 3.48 จาก Demand 3.48 · มี Effective Date · ปุ่ม Traceability ปรากฏ (ย้อนดูได้ว่าสินค้ามาจาก Slab แผ่นไหน)",
         prio="High", shot=SHOT + "gp-fg-15-delivery-done.png"),
    dict(id="TC-GP-FG-16", scenario="สร้างใบแจ้งหนี้จาก Sales Order",
         pre="ทำ TC-GP-FG-15 เสร็จแล้ว",
         steps=["กลับไปที่ Sales Order กดปุ่ม \"Create Invoice\"",
                "เลือก \"Regular invoice\" แล้วกด \"Create Draft\""],
         sample="Regular invoice",
         expected="ได้ใบแจ้งหนี้ฉบับร่าง 4 บรรทัดตรงกับ Sales Order: GP Block Marble 3.48 m² = 41,760.00 · งานขอบ 3.60 ม. = 1,260.00 · งานเจาะช่องเตา 1,500.00 · งานเจาะช่องซิงค์ 1,200.00 — รวม 45,720.00 + VAT 3,200.40 = 48,920.40 บาท",
         prio="High", shot=SHOT + "gp-fg-16-invoice-draft.png"),
    dict(id="TC-GP-FG-17", scenario="กด Confirm ใบแจ้งหนี้ให้ Posted",
         pre="ทำ TC-GP-FG-16 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บนใบแจ้งหนี้"],
         sample="-",
         expected="ใบแจ้งหนี้ INV/2026/00006 เป็น Posted · ยอดค้างชำระ 48,920.40 บาท · บรรทัดหินติดแท็ก Analytic (Sale / Marble / GP Block Marble / BLK-26-0006) ทำให้รายงานต้นทุนอ้างอิงกลับไปถึง Block ต้นทางได้ · มีปุ่ม Pay และ Credit Note พร้อมใช้",
         prio="High", shot=SHOT + "gp-fg-17-invoice-posted.png"),
  ]),
]
