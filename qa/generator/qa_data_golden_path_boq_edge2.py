# Single source of truth for the EMG-O test-case set "BOQ — กรณีพิเศษ ชุดที่ 2" (the items that set 1, qa_data_golden_path_boq_edge.py, listed as not covered).
#
# Data provenance: every case was run on `eg-tst`, 2026-11-03, driven by Playwright as emgdemo (company Empire Granite), on boq_estimation 19.0.1.54.3 /
# stone_slab_inventory 19.0.2.109.68 (TC-EX2-10 after the fix; the other cases ran on 109.67).
# Fixture C (Cut List before the quotation, re-import, offcut scrap, partial return, credit note after payment): blank BOQ + cutlist-import-zz2-meeting.xlsx
#   -> BOQ1232 -> S01810 (warning on Confirm) -> MO EG01/STFG/00494 (offcut OC-EG01/STFG/00494-01, scrapped) + 00495 -> EG01/OUT/00778 -> INV/2026/00023 (paid)
#   -> return EG01/IN/00749 (3.000 + 4.320) -> credit note RINV/2026/00002 (27,878.90 + VAT 1,951.52).
# Fixture D (lamps delivered one at a time): BOQ1234 (2 lamps) -> S01812 -> Cut List after the sale -> assemblies EG01/STFG/00497 + 00498 -> EG01/OUT/00780 (lamp 1)
#   + backorder 00781 -> INV/2026/00024 (30,000.00).
# Fixture E (cancel a confirmed Project sale): boq-import-zz2-reception.xlsx -> BOQ1235 -> S01830 (Sold as Project) -> cancelled. The first run of this case (BOQ1233 / S01811, on 109.67)
#   left the draft production EG01/STFG/00496 behind holding two Slabs; that is the bug fixed in 109.68 and the production was cancelled by hand afterwards.
#
# Scope: error and exception paths. Not covered: the second lamp's invoice and a lamp return, scrapping several offcuts at once, refunding the money after a
# credit note, cancelling after delivery, and what the project/tasks should do after a cancel (that needs a decision, see the box on top).
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
    dict(id="TC-EX2-05", scenario="กด ชำรุด — ตัดทิ้ง (Scrap) ที่เศษ",
         note="ข้อควรรู้: การตัดทิ้งย้าย lot ไปที่ Inventory adjustment แต่ไม่เกิดรายการบัญชีตัดสต็อก (ต้นทุน 224.80 ไม่ถูกลงเป็นค่าใช้จ่าย) เพราะที่เก็บ Scrap / Inventory adjustment ไม่ได้ตั้งบัญชี — อยู่ในประเด็นที่ต้องการให้ยืนยัน",
         pre="ทำ TC-EX2-04 เสร็จแล้ว (ฟอร์ม OC-EG01/STFG/00494-01 ยังเปิดอยู่)",
         steps=["กด ชำรุด — ตัดทิ้ง (Scrap)",
                "กด Ok ในหน้าต่างยืนยัน แล้วโหลดฟอร์มใหม่"],
         sample="-",
         expected="หน้าต่าง Confirmation: ตัดทิ้งแผ่นนี้ออกจากสต็อก? · หลังกด Ok: ที่เก็บเป็น Inventory adjustment สถานะ Elsewhere ไม่มีปุ่มตรวจแล้วนำกลับไปขาย · ไม่มีใบสำคัญบัญชีใหม่ (SP/00025 มูลค่า 224.80 ไม่มีรายการบัญชี)",
         prio="High", shot=SHOT + "h1-03-offcut-scrapped.png"),
  ]),
  dict(cat_id="C", title="C. คืนของบางส่วนและคืนหลังจ่ายเงินแล้ว",
       subtitle="คืนเฉพาะบางชิ้นหรือบางจำนวน · Credit Note บางส่วนของใบแจ้งหนี้ที่ชำระแล้ว · 2 test cases",
       cases=[
    dict(id="TC-EX2-06", scenario="คืน FG บางส่วนของใบส่งของ (บางบรรทัด และบางจำนวนของ lot)",
         note="ต่างจากการส่ง (ที่ lot เดียวต้องส่งทั้งชิ้น) การรับคืนระบบยอมให้คืนบางจำนวนของ lot ได้ · lot FG-EG01/STFG/00494-01 (4.320) ถูกแบ่งเป็น 3.000 อยู่ EG01/Stock และ 1.320 ยังอยู่กับลูกค้า",
         pre="ส่งของ EG01/OUT/00778 ครบ (ห้องประชุม 8.700 และห้องน้ำ 4.320) แล้วออกใบแจ้งหนี้ INV/2026/00023 (54,624.24 ก่อน VAT) และชำระครบ",
         steps=["เปิดใบส่งของ EG01/OUT/00778 กด Return",
                "แก้ Quantity ของแถวแรกเป็น 3 แถวที่สองเป็น 4.32 กด Return แล้วเปิดใบรับคืน (EG01/IN/00749) กด Validate"],
         sample="คืน 3.000 ของห้องประชุม และ 4.320 ของห้องน้ำ (ทั้ง lot)",
         expected="ได้ใบรับคืน EG01/IN/00749 สองบรรทัด 3.000 และ 4.320 ปลายทาง EG01/Stock · Validate ผ่านเป็น Done ไม่มีข้อความห้ามแบ่ง",
         prio="High", shot=SHOT + "h3-01-return-wizard-partial.png"),
    dict(id="TC-EX2-07", scenario="ออก Credit Note เฉพาะส่วนที่คืน ของใบแจ้งหนี้ที่ชำระแล้ว",
         note="ใบแจ้งหนี้เดิมยอดรวม 58,447.94 ชำระแล้ว หลัง Credit Note 29,830.42 ใบเดิมแสดงยอดค้าง 28,617.52 ทั้งที่จ่ายเต็ม และ Credit Note แสดง Paid · ผู้จัดทำยังอธิบายยอดนี้ไม่ได้ ขอให้ฝ่ายบัญชีตรวจว่าเงินส่วนที่ต้องคืนลูกค้าอยู่ตรงไหน · ระบบไม่คืนเงินให้เอง",
         pre="ทำ TC-EX2-06 เสร็จแล้ว · ใบแจ้งหนี้ INV/2026/00023 ลงทะเบียนชำระแล้ว (Pay → Create Payment 58,447.94)",
         steps=["เปิดใบแจ้งหนี้ INV/2026/00023 กด Credit Note เลือก Reverse ได้ Credit Note ฉบับร่าง",
                "แก้จำนวนบรรทัดห้องประชุมจาก 8.700 เป็น 3.000 ลบบรรทัดค่าบริหารโครงการ (ห้องน้ำ 4.320 คงเดิม) แล้ว Confirm"],
         sample="ห้องประชุม 3.000 × 3,820.965517 = 11,462.90 · ห้องน้ำ 4.320 × 3,800.00 = 16,416.00",
         expected="RINV/2026/00002 Posted ก่อน VAT 27,878.90 · VAT 1,951.52 · รวม 29,830.42 · แสดง Paid · ใบ INV/2026/00023 ยอดค้าง 28,617.52 (ตรวจโดยบัญชี) · ไม่มีการคืนเงินอัตโนมัติ",
         prio="High", shot=SHOT + "h5-02-credit-note-posted.png"),
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
    dict(id="TC-EX2-09", scenario="ออกใบแจ้งหนี้ตามที่ส่ง (โคมใบเดียว)",
         note="ค่าบริหารโครงการ 5,000 ถูกเรียกเก็บเต็มจำนวนในใบแรก (เหมือน TC-EX-12) ไม่แบ่งตามสัดส่วน · ใบที่สองจะมีแต่โคมใบที่สอง 25,000",
         pre="ทำ TC-EX2-08 เสร็จแล้ว",
         steps=["ที่ใบสั่งขาย S01812 กด Create Invoice → Create Draft → Confirm"],
         sample="-",
         expected="INV/2026/00024 Posted: โคมประตูซ้าย 1.000 × 25,000.00 · ค่าบริหารโครงการ 5,000.00 · ก่อน VAT 30,000.00 · VAT 2,100.00 · รวม 32,100.00 · ไม่มีบรรทัดโคมขวา",
         prio="High", shot=SHOT + "m4-02-invoice-one-lamp.png"),
  ]),
  dict(cat_id="E", title="E. ยกเลิกใบสั่งขายที่ยืนยันเป็น Project แล้ว",
       subtitle="Cancel ที่ใบสั่งขายหลังยืนยัน · สิ่งที่ถูกยกเลิกและสิ่งที่ค้าง · 1 test case",
       cases=[
    dict(id="TC-EX2-10", scenario="กด Cancel ที่ใบสั่งขายที่ติ๊ก Sold as Project และยืนยันแล้ว (ยังไม่ผลิต ไม่ส่ง)",
         note="ใบสั่งขายและใบส่งของถูกยกเลิก และใบสั่งผลิตที่ยังเป็น Draft ถูกยกเลิกตามไปด้วย (แก้แล้ว stone_slab_inventory 19.0.2.109.68 เดิมใบสั่งผลิตค้างและจอง Slab ไว้ 2 แผ่น) · ใบสั่งผลิตที่ Confirm หรือเริ่มผลิตแล้วไม่ถูกยกเลิกให้ · Project และ Task ยังค้างใช้งาน ผู้จัดทำยังไม่แตะเพราะต้องให้ผู้ใช้ตัดสินใจ — อยู่ในประเด็นที่ต้องการให้ยืนยัน",
         pre="ใบเสนอราคา S01830 จาก BOQ1235 (7.2 ตร.ม. ไฟล์ boq-import-zz2-reception.xlsx) ติ๊ก Sold as Project แล้ว Confirm · มี Project 1 Task 1 ใบส่งของ 1 ใบสั่งผลิต 1 (Draft)",
         steps=["ที่ใบสั่งขาย กด Cancel แล้วกด Ok ในหน้าต่างยืนยัน",
                "โหลดหน้าใหม่ แล้วดูสถานะ ปุ่มสมาร์ท และใบสั่งผลิต"],
         sample="-",
         expected="สถานะ Cancelled · ใบส่งของ EG01/OUT/00787 Cancelled · ใบสั่งผลิต EG01/STFG/00504 Cancelled (ปุ่ม FG Production หายจากใบสั่งขาย) · ปุ่มสมาร์ทยังแสดง Projects 1 · Tasks 1 · Project และ Task (In Progress) ยังใช้งานอยู่",
         prio="High", shot=SHOT + "k2-02-cancelled.png"),
  ]),
]
