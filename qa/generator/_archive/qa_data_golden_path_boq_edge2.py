# Single source of truth for the EMG-O test-case set "BOQ — กรณีพิเศษ ชุดที่ 2" (the items that set 1, qa_data_golden_path_boq_edge.py, listed as not covered).
#
# Data provenance: every case was run on `eg-tst`, 2026-11-03, driven by Playwright as emgdemo (company Empire Granite), on boq_estimation 19.0.1.54.3 /
# stone_slab_inventory 19.0.2.109.68 (TC-EX2-10 after the fix; the other cases ran on 109.67).
# Fixture C (Cut List before the quotation, re-import, offcut scrap): blank BOQ + cutlist-import-zz2-meeting.xlsx
#   -> BOQ1232 -> S01810 (warning on Confirm) -> MO EG01/STFG/00494 (offcut OC-EG01/STFG/00494-01, scrapped) + 00495 -> EG01/OUT/00778 -> INV/2026/00023.
#   (Its payment PAY00002 never posted: the Bank journal had no Outstanding Receipts account, see TC-EX2-07. The old credit note RINV/2026/00002 is superseded evidence.)
# Fixture C3 (partial return, credit note after payment, refund; Outstanding accounts set on the Bank journal): fixture C2's S01831 -> EG01/OUT/00788 (7.200)
#   -> INV/2026/00025 (46,024.00 + VAT 3,221.68 = 49,245.68) paid by PBNK1/2026/00001 -> return EG01/IN/00750 (3.000) -> credit note RINV/2026/00003 (14,100.00 + VAT 987.00 = 15,087.00)
#   -> refunded by PBNK1/2026/00002.
# Fixture C2 (scrap with the loss account set on the Scrap / Inventory adjustment locations): boq-import-zz2-reception.xlsx -> BOQ1236 -> S01831 -> MO EG01/STFG/00505 -> offcut OC-EG01/STFG/00505-01 scrapped -> STJ/2026/11/0092.
# Fixture C4 (FG lot split in pieces, on 109.69): BOQ1359 / S02047 (boq-import-zz2-reception.xlsx) -> MO EG01/STFG/00570 (lot FG-EG01/STFG/00570-01, 10 pieces) -> EG01/OUT/00898 (3 pieces = 2.160)
#   + backorder 00899 (5.04) -> INV/2026/00028 -> return EG01/IN/00828 (2 pieces = 1.440). Used by TC-EX-10 (set 1) and TC-EX2-06.
# Fixture D (lamps delivered one at a time): BOQ1234 (2 lamps) -> S01812 -> Cut List after the sale -> assemblies EG01/STFG/00497 + 00498 -> EG01/OUT/00780 (lamp 1)
#   + backorder 00781 (lamp 2). First invoice INV/2026/00024 (30,000.00, fee billed in full, before fix d) was cancelled; on BOQ 1.54.4: INV/2026/00026 (lamp 1 + half the fee = 27,500.00)
#   and INV/2026/00027 (lamp 2 + the other half = 27,500.00).
# Fixture E (cancel a confirmed Project sale): boq-import-zz2-reception.xlsx -> BOQ1235 -> S01830 (Sold as Project) -> cancelled. The first run of this case (BOQ1233 / S01811, on 109.67)
#   left the draft production EG01/STFG/00496 behind holding two Slabs; that is the bug fixed in 109.68 and the production was cancelled by hand afterwards.
#
# Scope: error and exception paths. Not covered: a lamp return, scrapping several offcuts at once,
# cancelling after delivery, (the project/tasks after a cancel are left alone on purpose, decided 3 Nov 2026).
# Column model per case: id, scenario, note (optional callout), pre, steps (list), sample, expected, prio, shot.

SHOT = "assets/boq-ex2/"

CATEGORIES = [
  dict(cat_id="A", title="A. Cut List ก่อนออกใบเสนอราคา และนำเข้าซ้ำ",
       subtitle="BOQ ที่ยังไม่มีบรรทัดสร้างบรรทัดจาก Cut List ได้ · นำเข้าซ้ำไม่ทำให้ชิ้นงานซ้อน · ยืนยันขายโดยยังไม่มีของ · 3 test cases",
       cases=[
    dict(id="TC-EX2-01", scenario="นำเข้า Cut List ก่อนออกใบเสนอราคา (สร้างบรรทัดใหม่จากชิ้นงาน)",
         note="ตัวเลือก สร้างบรรทัดใหม่จากชิ้นงาน ใช้ได้เมื่อ BOQ ยังไม่ออกใบเสนอราคา ระบบรวมยอดตามโซนและจับคู่สินค้าให้ตามสินค้าที่เลือกไว้ที่แท็บ ③ · เส้นทาง 2 และ 5 ใช้แบบหลังขาย (เติมเข้าบรรทัดเดิม)",
         pre="BOQ ใหม่ที่เลือกลูกค้า Demo Hotel Customer แล้วบันทึก ยังไม่มีบรรทัด · เลือกสินค้า ZZ2G-FG ที่แท็บ ③ Cut List · ไฟล์ cutlist-import-zz2-meeting.xlsx (18 ชิ้น 2 โซน)",
         steps=["ที่ BOQ เปิดแท็บ ③ Cut List กด นำเข้า Cut List",
                "อัปโหลดไฟล์ cutlist-import-zz2-meeting.xlsx กด อ่านไฟล์ แล้วดูตารางตรวจทาน",
                "กด ยืนยันนำเข้า แล้วเปิดแท็บ ① ประเมินพื้นที่"],
         sample="โซน ห้องประชุม 12 ชิ้น 8.7480 ตร.ม. · โซน ห้องน้ำ 6 ชิ้น 4.3200 ตร.ม.",
         expected="ตารางตรวจทานเลือกวิธี สร้างบรรทัดใหม่จากชิ้นงาน และจับคู่สินค้า [ZZ2G-FG] ให้ทั้งสองโซน · หลังยืนยัน แท็บ ① มี 2 บรรทัด: ห้องประชุม 8.75 ตร.ม. × 3,800.00 = 33,242.40 · ห้องน้ำ 4.32 × 3,800.00 = 16,416.00 · Direct Cost 49,658.40 · Overhead 4,965.84 · Amount Total 54,624.24",
         prio="High", shot=SHOT + "f1-03-parse.png"),
    dict(id="TC-EX2-02", scenario="นำเข้า Cut List ไฟล์เดิมซ้ำอีกครั้ง",
         note="ครั้งที่สองระบบเลือกวิธี เติมชิ้นงานเข้าบรรทัดเดิมตามโซน ให้เอง จึงไม่สร้างบรรทัดซ้ำและไม่เพิ่มชิ้นงานซ้อน · ผลตรวจในฐานข้อมูล: ห้องประชุม 12 ชิ้น ห้องน้ำ 6 ชิ้น เท่าเดิม",
         pre="ทำ TC-EX2-01 เสร็จแล้ว",
         steps=["กด นำเข้า Cut List อัปโหลดไฟล์เดิม cutlist-import-zz2-meeting.xlsx กด อ่านไฟล์",
                "กด ยืนยันนำเข้า แล้วดูข้อความแจ้งและแท็บ ①"],
         sample="ไฟล์เดียวกับเคสก่อน",
         expected="ข้อความ เติมชิ้นงานเข้าบรรทัดเดิมแล้ว. ห้องประชุม: ประเมิน 8.75 / Cut List 8.75 ตร.ม. (ตรงกัน) | ห้องน้ำ: ประเมิน 4.32 / Cut List 4.32 ตร.ม. (ตรงกัน) · แท็บ ① ยังมี 2 บรรทัดเท่าเดิม · Amount Total 54,624.24 ไม่เปลี่ยน · ชิ้นงานต่อบรรทัด 12 และ 6 ไม่ซ้อน",
         prio="High", shot=SHOT + "f2-05-second-confirm.png"),
    dict(id="TC-EX2-03", scenario="ยืนยันขายทั้งที่ FG ยังไม่มีของและไม่มี PO",
         note="หน้าต่างเตือนนี้ไม่บล็อก กด Confirm ต่อ ได้ (FG ผลิตตามออเดอร์จึงไม่มีสต็อกตอนขายเป็นปกติ) · ผู้จัดทำยังไม่ทราบเงื่อนไขที่ทำให้ขึ้นเฉพาะบางใบ (ใบอื่นที่ทำวันเดียวกันไม่ขึ้นหน้าต่างนี้)",
         pre="BOQ จาก TC-EX2-01 ออกใบเสนอราคาแล้ว (S01810 รวม 58,447.94 รวม VAT)",
         steps=["ที่ใบเสนอราคา กด Confirm",
                "อ่านหน้าต่าง แล้วกด Confirm ต่อ"],
         sample="-",
         expected="หน้าต่าง ยืนยัน Confirm ทั้งที่ยังไม่มีของ รายชื่อสินค้า 2 บรรทัด ข้อความ ถ้าสุดท้ายผลิต/หาของไม่ได้จริง สามารถ Cancel SO นี้ได้ภายหลัง · หลังกด Confirm ต่อ ใบสั่งขายเป็น Sales Order มีปุ่ม Delivery 1 และ FG Production 2 (ใบสั่งผลิต EG01/STFG/00494 และ 00495)",
         prio="Medium", shot=SHOT + "g2-01-confirm-warning.png"),
  ]),
  dict(cat_id="B", title="B. เศษหินที่ตรวจแล้วชำรุด",
       subtitle="บันทึกเศษเล็กที่ใช้ไม่ได้ แล้วตัดทิ้งที่ Slabs Pending Inspection · 2 test cases",
       cases=[
    dict(id="TC-EX2-04", scenario="ผลิต FG เสร็จพร้อมเศษเล็กที่แตกร้าว",
         note="วิธีบันทึกเศษเหมือน TC-EX-06 ขนาดเป็นเมตร · เศษเข้า Returned - Inspect รอตรวจ ต้นทุนคิดตามพื้นที่",
         pre="ใบสั่งผลิต EG01/STFG/00494 (ห้องประชุม 8.75 ตร.ม.) ย้ายไปสถานีตัดและ Confirm แล้ว",
         steps=["เปิดแท็บ เศษที่เหลือ กด Add a line กรอก กว้าง 0.4 ยาว 0.6 จำนวนชิ้น 1 หมายเหตุ เศษมุมแผ่น แตกร้าว ใช้ไม่ได้",
                "กด ผลิต FG เสร็จ แล้วเปิดเมนู Stone Slab &gt; Slabs &gt; Slabs Pending Inspection เปิดแถว OC-EG01/STFG/00494-01"],
         sample="เศษ 0.40 × 0.60 ม. = 0.24 ตร.ม.",
         expected="ใบสั่งผลิต Done · เศษได้ Offcut Lot OC-EG01/STFG/00494-01 ต้นทุน 224.80 · ฟอร์ม Lot: สถานะ Returned - Pending Inspection ที่เก็บ Stone Inventory/Returned - Inspect ขนาด 0.400 × 0.600 × 0.030 · มีปุ่ม ตรวจแล้ว — นำกลับไปขาย และ ชำรุด — ตัดทิ้ง (Scrap)",
         prio="Medium", shot=SHOT + "h1-01-offcut-pending.png"),
    dict(id="TC-EX2-05", scenario="กด ชำรุด — ตัดทิ้ง (Scrap) ที่เศษ แล้วตรวจรายการบัญชี",
         note="การตัดทิ้งลงบัญชีได้ก็ต่อเมื่อที่เก็บ Scrap และ Inventory adjustment ตั้ง Stock Valuation Account ไว้ · รอบแรก (ใบ S01810 เศษ 224.80) ยังไม่ได้ตั้ง จึงไม่มีรายการบัญชีเลย ต้นทุนเศษค้างอยู่ในบัญชีสต็อก · ตั้งบัญชี Inventory Write-down (511300) ที่ 4 ที่เก็บของ Empire Granite และ Empire Stone บน eg-tst แล้ว เคสนี้รันซ้ำหลังตั้ง · บัญชีที่เลือกเป็นข้อสมมติ รอฝ่ายบัญชียืนยัน",
         pre="ทำซ้ำ TC-EX2-04 บนใบเสนอราคา S01831 (BOQ1236 จาก boq-import-zz2-reception.xlsx) ใบสั่งผลิต EG01/STFG/00505 ได้เศษ OC-EG01/STFG/00505-01 ต้นทุน 224.71 · ที่เก็บ Scrap และ Inventory adjustment ของบริษัทตั้ง Stock Valuation Account = Inventory Write-down (511300)",
         steps=["เปิด Slabs Pending Inspection แถว OC-EG01/STFG/00505-01 กด ชำรุด — ตัดทิ้ง (Scrap)",
                "กด Ok ในหน้าต่างยืนยัน แล้วเปิดรายการบัญชี (Accounting &gt; Journal Entries) ดูใบที่อ้างอิง SP/00026"],
         sample="-",
         expected="หน้าต่าง Confirmation: ตัดทิ้งแผ่นนี้ออกจากสต็อก? · หลังกด Ok: ที่เก็บ Inventory adjustment สถานะ Elsewhere ไม่มีปุ่มตรวจแล้วนำกลับไปขาย · ได้ใบสำคัญ STJ/2026/11/0092 อ้างอิง SP/00026 ยอด 224.71: เดบิต Inventory Write-down 224.71 เครดิต Inventory - Stone Slabs (Ready-Made) 224.71 · ถ้ายังไม่ตั้งบัญชีที่ที่เก็บ จะไม่มีใบสำคัญนี้",
         prio="High", shot=SHOT + "n3-03-offcut-scrapped.png"),
  ]),
  dict(cat_id="C", title="C. คืนของบางส่วนและคืนหลังจ่ายเงินแล้ว",
       subtitle="คืนเฉพาะบางชิ้นหรือบางจำนวน · Credit Note บางส่วนของใบแจ้งหนี้ที่ชำระแล้ว · 2 test cases",
       cases=[
    dict(id="TC-EX2-06", scenario="คืน FG เป็นชิ้นเต็มของใบส่งของที่ส่งบางชิ้น",
         note="การคืนใช้กติกาเดียวกับการส่ง: ต้องเป็นจำนวนเต็มของชิ้น (ชิ้นละ 0.72 ตร.ม.) · ระบบตรวจตอนกด Return ก่อนสร้างใบรับคืน · รอบแรกของเคสนี้ (S01831 คืน 3.000 ตร.ม.) ทำก่อนมีกติกานี้ ซึ่งตอนนี้ 3.000 จะไม่ผ่านเพราะเป็น 4.17 ชิ้น (คืนได้ 2.88 หรือ 3.60)",
         pre="ใบส่งของ EG01/OUT/00898 (S02047 ส่ง 3 ชิ้น = 2.160 จาก lot 10 ชิ้น ดู TC-EX-10) สถานะ Done",
         steps=["เปิดใบส่งของ EG01/OUT/00898 กด Return แก้ Quantity เป็น 0.5 กด Return",
                "แก้ Quantity เป็น 1.44 (2 ชิ้น) กด Return แล้วเปิดใบรับคืน (EG01/IN/00828) กด Validate"],
         sample="คืน 0.50 (ไม่ลงตัว) แล้วคืน 1.44 (2 ชิ้น)",
         expected="ใส่ 0.50: Invalid Operation หิน Lot FG-EG01/STFG/00570-01 คืนได้เป็นชิ้นเต็มเท่านั้น (ชิ้นละ 0.7200 ตร.ม.) แต่ใส่ 0.50 · ใส่ 1.44: ได้ใบรับคืน EG01/IN/00828 1.440 ปลายทาง EG01/Stock Validate ผ่านเป็น Done",
         prio="High", shot=SHOT + "w7-01-return-not-whole-pieces.png"),
    dict(id="TC-EX2-07", scenario="ชำระเงิน ออก Credit Note เฉพาะส่วนที่คืน และคืนเงินลูกค้า",
         note="ระบบไม่คืนเงินให้เอง ต้องกด Pay บน Credit Note · Credit Note ใช้ยอดเต็มของแต่ละบรรทัดที่ยกมา ต้องลบบรรทัดที่ไม่ได้คืน (ค่าใช้จ่ายส่วนเพิ่มของห้อง และค่าบริหารโครงการ) ออกเอง · ต้องตั้งบัญชี Outstanding Receipts/Payments ที่ Manual Payment ของ Bank ก่อน (ดูคู่มือ Setup) ไม่เช่นนั้นการชำระจะไม่ลงบัญชี ใบแจ้งหนี้ไม่ถูกตัดยอด และสถานะ In Payment หลอกว่าจ่ายแล้ว (รอบแรกของเคสนี้เจอเรื่องนี้ ยอดค้าง 28,617.52 ที่เคยรายงานไว้คือผลจากสาเหตุนี้ ไม่ใช่ความผิดปกติของ Credit Note)",
         pre="ใบแจ้งหนี้ INV/2026/00025 (S01831 ส่งเต็ม 7.200 รับคืนไป 3.000 ตามรอบแรกก่อนมีกติกาชิ้นเต็ม) Posted · Bank ของบริษัทตั้ง Outstanding Receipts และ Outstanding Payments แล้ว",
         steps=["เปิด INV/2026/00025 กด Pay → Create Payment (49,245.68) ได้ PBNK1/2026/00001 ใบแจ้งหนี้ยอดค้าง 0",
                "หลังรับคืน 3.000 (EG01/IN/00750) เปิด INV/2026/00025 กด Credit Note เลือก Reverse ได้ Credit Note ฉบับร่าง",
                "แก้จำนวนบรรทัดเคาน์เตอร์จาก 7.200 เป็น 3.000 ลบบรรทัดค่าใช้จ่ายส่วนเพิ่มของห้อง และค่าบริหารโครงการ แล้ว Confirm",
                "บน Credit Note กด Pay → Create Payment (ยอด 15,087.00) เพื่อคืนเงินลูกค้า"],
         sample="เคาน์เตอร์ 3.000 × 4,700.00 = 14,100.00 · VAT 7% = 987.00 · รวม 15,087.00",
         expected="RINV/2026/00003 Posted ก่อน VAT 14,100.00 · VAT 987.00 · รวม 15,087.00 ยอดค้าง 15,087.00 (ยังไม่ Paid จนกว่าจะคืนเงิน) · ตอน Confirm ระบบลงกลับต้นทุนขาย 3,300.37 (เดบิต Inventory - Stone FG เครดิต COGS) · หลังกด Pay ได้ PBNK1/2026/00002 (ขาออก 15,087.00) แสดง In Payment ยอดค้าง 0 · ใบแจ้งหนี้เดิมยังยอดค้าง 0",
         prio="High", shot=SHOT + "p5-03-credit-note-refunded.png"),
  ]),
  dict(cat_id="D", title="D. ส่งโคม (Custom FG ซีเรียล) ทีละใบ",
       subtitle="โคมแต่ละใบมีซีเรียลของตัวเอง ส่งแยกได้ต่างจากพื้นที่เป็น lot เดียว · 2 test cases",
       cases=[
    dict(id="TC-EX2-08", scenario="ส่งโคมใบแรก แล้วสร้างใบค้างส่งสำหรับใบที่สอง",
         note="ใบสั่งขายมีโคมซ้ายและโคมขวาเป็นคนละบรรทัด ตั้ง Quantity ของบรรทัดที่ยังไม่ส่งเป็น 0 · ใบสั่งผลิตของโคมเกิดหลังนำเข้า Cut List (เหมือนเส้นทาง 5)",
         pre="BOQ1234 (โคมประตูซ้ายและขวา ใบละ 25,000) ยืนยันขายก่อนมี Cut List แล้วนำเข้า cutlist-import-zz2-lamps.xlsx · ผลิตโคมทั้งสองใบเสร็จ (EG01/STFG/00497 และ 00498 ผ่านใบตัดและใบประกอบ) · ใบส่งของ EG01/OUT/00780 มี 2 บรรทัด Ready",
         steps=["เปิดใบส่งของ แก้ Quantity ของบรรทัดที่สองเป็น 0",
                "กด Validate แล้วกด Create Backorder"],
         sample="บรรทัด 1 ส่ง 1.000 · บรรทัด 2 ส่ง 0 (จาก 1.000)",
         expected="หน้าต่าง Create Backorder? ขึ้น · หลังกด ใบ EG01/OUT/00780 Done 1.000 หน่วย (โคมใบแรก) · เกิด EG01/OUT/00781 Ready อีก 1 หน่วย อ้างอิง Back Order of EG01/OUT/00780",
         prio="High", shot=SHOT + "m3-03-dialog.png"),
    dict(id="TC-EX2-09", scenario="ออกใบแจ้งหนี้ตามที่ส่ง ค่าบริหารโครงการเรียกตามสัดส่วนมูลค่าที่ส่ง (ใบโคมใบแรก และใบโคมใบที่สอง)",
         note="ผลหลังแก้ (BOQ 1.54.4): ค่าบริหารโครงการ 5,000 เรียกตามสัดส่วนมูลค่าสินค้าที่ส่ง · โคมใบแรก (ครึ่งหนึ่งของมูลค่า) เรียกค่าบริหาร 0.500 = 2,500 โคมใบที่สองเรียกอีก 0.500 = 2,500 รวมครบ 5,000 · ก่อนแก้ (รอบแรก INV/2026/00024) ใบแรกเรียกเต็ม 5,000 ใบนั้นถูกยกเลิกและออกใหม่ · ถ้าสินค้าไม่ถูกส่งเลย ค่าบริหารยังไม่ถูกเรียกเก็บ",
         pre="ทำ TC-EX2-08 เสร็จแล้ว (ส่งโคมใบแรกแล้ว ใบที่สองยังอยู่ที่ใบค้างส่ง EG01/OUT/00781)",
         steps=["ที่ใบสั่งขาย S01812 กด Create Invoice → Create Draft → Confirm ได้ใบของโคมใบแรก",
                "ส่งโคมใบที่สอง (EG01/OUT/00781 กด Validate) แล้วกลับมาที่ S01812 กด Create Invoice → Create Draft → Confirm"],
         sample="โคม 25,000 × 2 ใบ · ค่าบริหารโครงการ 5,000 · ใบละครึ่ง",
         expected="INV/2026/00026 Posted: โคมประตูซ้าย 1.000 × 25,000.00 · ค่าบริหารโครงการ 0.500 × 5,000.00 = 2,500.00 · ก่อน VAT 27,500.00 · VAT 1,925.00 · รวม 29,425.00 · INV/2026/00027 Posted: โคมประตูขวา 25,000.00 · ค่าบริหารโครงการ 2,500.00 · รวม 29,425.00 · สองใบรวมค่าบริหารครบ 5,000.00",
         prio="High", shot=SHOT + "q1-02-invoice-one-lamp.png"),
  ]),
  dict(cat_id="E", title="E. ยกเลิกใบสั่งขายที่ยืนยันเป็น Project แล้ว",
       subtitle="Cancel ที่ใบสั่งขายหลังยืนยัน · สิ่งที่ถูกยกเลิกและสิ่งที่ค้าง · 1 test case",
       cases=[
    dict(id="TC-EX2-10", scenario="กด Cancel ที่ใบสั่งขายที่ติ๊ก Sold as Project และยืนยันแล้ว (ยังไม่ผลิต ไม่ส่ง)",
         note="ใบสั่งขายและใบส่งของถูกยกเลิก และใบสั่งผลิตที่ยังเป็น Draft ถูกยกเลิกตามไปด้วย (แก้แล้ว stone_slab_inventory 19.0.2.109.68 เดิมใบสั่งผลิตค้างและจอง Slab ไว้ 2 แผ่น) · ใบสั่งผลิตที่ Confirm หรือเริ่มผลิตแล้วไม่ถูกยกเลิกให้ · Project และ Task ยังค้างใช้งาน ตัดสินใจแล้ว (3 พ.ย. 2569) ว่าปล่อยไว้ให้ผู้ใช้ปิดหรือเก็บเอง ระบบไม่ปิดให้",
         pre="ใบเสนอราคา S01830 จาก BOQ1235 (7.2 ตร.ม. ไฟล์ boq-import-zz2-reception.xlsx) ติ๊ก Sold as Project แล้ว Confirm · มี Project 1 Task 1 ใบส่งของ 1 ใบสั่งผลิต 1 (Draft)",
         steps=["ที่ใบสั่งขาย กด Cancel แล้วกด Ok ในหน้าต่างยืนยัน",
                "โหลดหน้าใหม่ แล้วดูสถานะ ปุ่มสมาร์ท และใบสั่งผลิต"],
         sample="-",
         expected="สถานะ Cancelled · ใบส่งของ EG01/OUT/00787 Cancelled · ใบสั่งผลิต EG01/STFG/00504 Cancelled (ปุ่ม FG Production หายจากใบสั่งขาย) · ปุ่มสมาร์ทยังแสดง Projects 1 · Tasks 1 · Project และ Task (In Progress) ยังใช้งานอยู่",
         prio="High", shot=SHOT + "k2-02-cancelled.png"),
  ]),
]
