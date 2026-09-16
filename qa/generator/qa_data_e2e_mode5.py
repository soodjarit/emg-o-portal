# Single source of truth for EMG-O E2E flow test cases — Mode 5
# (Stone Production/FG): sell a finished good fabricated from a Slab, not
# sold as raw stone itself. Same spirit as qa_data_e2e_mode1/2/3/4.py.
#
# FULL REWRITE 2026-09-16 (v3, not a screenshot refresh) — 2 real mechanism
# changes since the v2 doc (built 2026-09-14):
#   1) ADR-067 (Session 135) retired the old stone.fg.production.wizard
#      popup entirely for the STANDARD path — "Produce FG" on an SO line now
#      creates a real draft mrp.production directly (auto-matches an
#      available Slab) and opens its own form, same "no wizard, native MO"
#      pattern B3b already established for Mode 3. Output is recorded in a
#      new "FG Output" tab (stone_fg_output_line_ids) after physically
#      cutting, not typed into a wizard field before producing.
#   2) ADR-068 (Session 141, THIS session, same day as this rewrite) added
#      an entirely new CUSTOM variant of Mode 5 for one-off bespoke jobs
#      (เจดีย์บัว/ซุ้มบัว-style) that don't fit a fixed reusable BOM — a
#      2-stage pipeline: Stage 2 "Cutting Plan" (an existing Slab -> N
#      smaller pieces sharing 1 lot) then Stage 3 "Assembly" (that lot ->
#      the final custom FG product, via an extended stone.custom.bom.wizard,
#      ADR-064). This is the FIRST Golden Path doc to cover the Custom
#      variant at all — no v1/v2 predecessor existed for it.
#
# Data provenance: fresh live run built specifically for this file, driven
# through the real Odoo web UI (Playwright) AND `odoo shell` (both hitting
# the real ORM business methods — action_confirm(), action_stone_move_to_
# production(), the wizard's action_confirm(), etc. — never a raw model
# write bypassing real logic) on `mbx-ee-dev`, 2026-09-16, on a brand-new
# dedicated test material ("E2E Mode5 Fresh Test V2") so nothing carries
# over cost history from another mode's fixture:
#
# STANDARD flow — PO P00060 (3.00 CBM @ 16,000/CBM = 48,000 + VAT 3,360 =
#   51,360.00) -> Block BLK-26-0036 (via the PO line's own "สร้าง Block"
#   button) -> Vendor Bill BILL/2026/09/0009 (51,360.00, via Accounting >
#   Vendors > Bills > New + Auto-Complete, same as every other Block-backed
#   mode — Received Qty never reaches the PO's own "Create Bill" button) ->
#   Cut MO EG01/STCUT/00048 (Target 1.5 x 1.0 m, Reason "อื่นๆ" — cut
#   speculatively ahead of any sale, same as v2) -> Complete Cut -> Slab
#   BLK-26-0036 #1 (1.50 Sq.Mt., Block's remaining CBM correctly drops
#   3.00 -> 2.97, surplus preserved for later) -> SO1 S00137 (FG
#   "Countertop" x1, 9,000 + VAT 630 = 9,630.00) confirmed -> "Produce FG"
#   link on the line creates MO EG01/STFG/00022 DIRECTLY (no wizard popup),
#   Slab BLK-26-0036 #1 auto-matched into stone_slab_id -> "ย้ายด่วน (Move
#   to Production)" -> Confirm -> FG Output tab: 1 row (1.48 x 0.98 x 0.02 m,
#   qty 1 — real saw-kerf loss vs. the 1.50 x 1.00 m Slab) -> "Complete FG
#   Production" -> MO Done, new Lot FG-EG01/STFG/00022, Slab flips to
#   Consumed -> Delivery EG01/OUT/00091 validated -> Invoice INV/2026/00037
#   (9,630.00) posted -> Register Payment -> In Payment. Journal Items:
#   Sales Revenue - FG Production 9,000 cr / Output VAT 630 cr / Trade
#   Receivables 9,630 dr / Inventory - Stone FG 480 cr / COGS 480 dr —
#   balances 10,110.00 = 10,110.00, real non-zero COGS.
#
# CUSTOM flow (ADR-068) — reused the same Block's surplus CBM: a 2nd Cut
#   Order produced Slab BLK-26-0036 #2 (kept small deliberately) -> Stage 2
#   "Cutting Plan" MO EG01/STCPL/00009 (Source Slab = BLK-26-0036 #2, 3
#   Planned/Actual Pieces rows: 0.25x0.20m, 0.20x0.15m, 0.15x0.10m) ->
#   "ย้ายด่วน" -> Confirm -> "Complete Cutting Plan" -> 3 real stone.slab
#   pieces (BLK-26-0036 #620-#622 in the raw sequence, all status "Staged
#   (Cutting Plan WIP)"), ALL sharing exactly 1 lot (CUT-EG01/STCPL/00009,
#   3.00 units on hand) -> new BOQ Document BOQ0032 + SO S00138 selling a
#   genuinely one-off custom product ("เจดีย์บัว S (Custom)", 12,000 + VAT
#   840 = 12,840.00, no fixed FG Raw Material — this is what makes "Produce
#   FG" route to the CUSTOM wizard instead of a direct MO) -> "Produce FG"
#   opens "สร้าง BOM จาก BOQ" -> picked "Cutting Plan Lot (Stage 2)" =
#   CUT-EG01/STCPL/00009 (no separate BOQ consumable line needed this run)
#   -> submit leaves the MO in DRAFT for review (this is the one behavior
#   difference from a pure-BOQ custom job, which still auto-confirms) ->
#   Stage 3 MO EG01/STFG/00023 shows "Cutting Plan Lot (Stage 2)" +
#   "Cutting Plan MO" smart button already linked back to EG01/STCPL/00009
#   -> Confirm (the component line + its real stock.move both appear
#   automatically, pinned to the full 3.00 on-hand qty of that exact lot)
#   -> Complete (native Produce/Mark Done, per ADR-064 — no custom button)
#   -> MO Done, all 3 pieces flip Staged -> Consumed, "Assembly MOs" smart
#   button now shows on the Stage-2 MO -> Delivery EG01/OUT/00092 validated
#   -> Invoice INV/2026/00038 (12,840.00) posted -> Register Payment -> In
#   Payment. Journal Items: Sales Revenue - FG Production 12,000 cr /
#   Output VAT 840 cr / Trade Receivables 12,840 dr / Inventory - Stone
#   Blocks (Raw) 76.89 cr / COGS 76.89 dr — balances 12,916.89 = 12,916.89.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber/green callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low), shot (screenshot path)

CATEGORIES = [
  dict(cat_id="G1", title="G1. เตรียมแผ่น (Slab) ก่อนผลิต — เหมือน Mode 3 ทุกประการ",
       subtitle="ตัด Block เป็น Slab ล่วงหน้า ก่อนขายจริง — reuse กลไกเดียวกับ Mode 3 (Block-to-Slab) ไม่มีอะไรใหม่ · 1 test case",
       cases=[
    dict(id="TC-E2E-M5-01", scenario="ตัด Block เป็น Slab ไว้ล่วงหน้า (ยังไม่ผูกกับ SO ใดๆ)",
         note="ใช้กลไกเดียวกับ Mode 3 (Block-to-Slab) เป๊ะๆ — Mode 5 ไม่มีขั้นตอนตัดของตัวเอง ต้องมี Slab พร้อมอยู่ในสต็อกก่อนเสมอ",
         pre="มี Block พร้อมอยู่แล้วในสต็อก (ยังไม่ตัด) จาก Material ที่ตั้งค่า Finished Good ไว้ครบ (มี Block/Slab/FG 3 สินค้า)",
         steps=["เปิด Manufacturing &gt; New", "เลือก Block ที่ต้องการตัด + กรอกขนาดที่ต้องการ", "ย้ายด่วน (Move to Production) &gt; Confirm &gt; ทำ Work Orders &gt; Complete Cut"],
         sample="Stone Block = BLK-26-0036<br>Target Slab L (M) = 1.50<br>Target Slab H (M) = 1.00",
         expected="ได้แผ่นหินจริง 1 แผ่นเข้าสต็อก (ตัวอย่างจริง: BLK-26-0036 #1, 1.50 ตร.ม.) Block เหลือ CBM ส่วนที่ยังไม่ตัดไว้ขายต่อได้ (ตัวอย่างจริง: เหลือ 2.97 CBM จาก 3.00)", prio="Medium",
         shot="assets/e2e-mode5/m5-04-slab-cut-done.png"),
  ]),
  dict(cat_id="G2", title="G2. ขาย + ผลิต — สินค้า FG มาตรฐาน (Standard, เช่น Countertop)",
       subtitle="ADR-029/067 — Produce FG สร้าง MO ตรงเลย ไม่ผ่าน wizard แล้ว · 6 test cases",
       cases=[
    dict(id="TC-E2E-M5-02", scenario="เพิ่มบรรทัดสินค้า FG มาตรฐานใน Sale Order แล้ว Confirm",
         pre="มี Slab พร้อมอยู่แล้วในสต็อกจาก TC-E2E-M5-01",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้า FG มาตรฐาน", "กด Confirm"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = E2E Mode5 Fresh Test V2 - Countertop",
         expected="SO ยืนยันสำเร็จ ยอดรวม 9,630.00 บาท (รวม VAT) บรรทัดสินค้า FG ปรากฏลิงก์ \"Produce FG\" เพราะยังไม่มีสต็อก FG เลย — ตัวอย่างจริง: S00137", prio="High",
         shot="assets/e2e-mode5/m5-05-so1-fg-line.png"),
    dict(id="TC-E2E-M5-03", scenario="กดลิงก์ \"Produce FG\" — ระบบสร้าง Manufacturing Order ตรงทันที ไม่มี wizard popup แล้ว",
         note="✨ กลไกใหม่ (ADR-067, 14 ก.ย. 2026): เดิมกดแล้วเด้ง wizard ให้เลือก Slab/จำนวน ตอนนี้กดแล้วได้ MO ฉบับร่างเปิดขึ้นมาเลย ระบบจับคู่ Slab ที่ Material ตรงกันให้อัตโนมัติ ไม่ต้องเลือกเองก็ได้",
         pre="ทำ TC-E2E-M5-02 เสร็จแล้ว",
         steps=["กดลิงก์ \"Produce FG\" บนบรรทัดสินค้า FG ของ Sale Order"],
         sample="-",
         expected="เปิดหน้า Manufacturing Order ฉบับร่างทันที (ไม่ใช่ popup) ช่อง Slab ที่ใช้ผลิตเติมให้อัตโนมัติเป็นแผ่นที่มี Material ตรงกันและสถานะ Available — ตัวอย่างจริง: MO EG01/STFG/00022, Slab BLK-26-0036 #1, ผูกกับ \"For Sale Order Line\" = S00137 ให้อัตโนมัติ", prio="High",
         shot="assets/e2e-mode5/m5-06-produce-fg-mo-draft.png"),
    dict(id="TC-E2E-M5-04", scenario="ย้ายด่วน (Move to Production) แล้ว Confirm Manufacturing Order",
         pre="ทำ TC-E2E-M5-03 เสร็จแล้ว",
         steps=["กดปุ่ม \"ย้ายด่วน (Move to Production)\" บน MO", "กดปุ่ม Confirm"],
         sample="-",
         expected="Slab ถูกย้ายไปสถานีผลิต (Stone Production) สำเร็จ แล้ว Confirm ผ่านทันที ไม่มี error — สถานะ MO เปลี่ยนเป็น Confirmed", prio="High",
         shot="assets/e2e-mode5/m5-06-produce-fg-mo-draft.png"),
    dict(id="TC-E2E-M5-05", scenario="ทำ Work Order ให้เสร็จ แล้วบันทึกขนาดจริงในแท็บ \"FG Output\"",
         note="✨ กลไกใหม่ (ADR-067): แท็บนี้แทนที่ wizard เดิมทั้งหมด — Factory กรอกขนาด/จำนวนที่ตัดได้จริงหลังตัดเสร็จ ตรงกับใบรายงานตัดกระดาษของโรงงานเป๊ะ ไม่มีคอลัมน์สินค้าเพราะทุกแถวนับรวมเป็นสินค้า FG ตัวเดียวของ MO นี้อยู่แล้ว",
         pre="ทำ TC-E2E-M5-04 เสร็จแล้ว",
         steps=["ไปแท็บ \"Work Orders\" กดเริ่ม/เสร็จตามลำดับจนครบ", "ไปแท็บ \"FG Output\" เพิ่มแถวขนาดจริงที่ตัดได้"],
         sample="Width = 1.48, Length = 0.98, Thickness = 0.02, Qty = 1",
         expected="Work Orders ขึ้น Finished ครบ MO เปลี่ยนสถานะเป็น \"To Close\" แท็บ FG Output มี 1 แถวตามที่กรอก", prio="Medium",
         shot="assets/e2e-mode5/m5-07-mo1-done.png"),
    dict(id="TC-E2E-M5-06", scenario="กด \"Complete FG Production\" — ได้สินค้า FG จริงเข้าสต็อก",
         pre="ทำ TC-E2E-M5-05 เสร็จแล้ว",
         steps=["กดปุ่ม \"Complete FG Production\" บน Manufacturing Order"],
         sample="-",
         expected="MO เสร็จสมบูรณ์ (สถานะ Done) ได้ Lot/Serial ใหม่ของสินค้า FG (ตัวอย่างจริง: FG-EG01/STFG/00022) Slab ที่ใช้เป็นวัตถุดิบเปลี่ยนสถานะเป็น Consumed สินค้า FG 1 หน่วยเข้าสต็อกจริง", prio="High",
         shot="assets/e2e-mode5/m5-07-mo1-done.png"),
    dict(id="TC-E2E-M5-07", scenario="จัดส่ง ออกใบแจ้งหนี้ และรับชำระเงิน (Standard)",
         pre="ทำ TC-E2E-M5-06 เสร็จแล้ว",
         steps=["เปิดใบส่งของที่เกิดขึ้นอัตโนมัติ &gt; Validate", "เปิด SO &gt; Create Invoice &gt; Regular Invoice &gt; Confirm", "เปิดใบแจ้งหนี้ &gt; Pay &gt; ยืนยันการชำระ"],
         sample="-",
         expected="ใบส่งของ Done (ตัวอย่างจริง: EG01/OUT/00091) ใบแจ้งหนี้ Posted ยอด 9,630.00 (ตัวอย่างจริง: INV/2026/00037) แล้วขึ้น In Payment — Journal Items 5 บรรทัด สมดุล 10,110.00 = 10,110.00 (COGS 480.00 ไม่ใช่ 0)", prio="High",
         shot="assets/e2e-mode5/m5-09-invoice1-posted.png"),
  ]),
  dict(cat_id="G3", title="G3. ขาย + ผลิต — งาน Custom สั่งทำพิเศษ (ADR-068, เช่น เจดีย์บัว/ซุ้มบัว)",
       subtitle="ใหม่ทั้งหมด session นี้ — Stage 2 (ถอดแบบ) + Stage 3 (ประกอบ) สำหรับงานที่ไม่มี BOM ตายตัว · 6 test cases",
       cases=[
    dict(id="TC-E2E-M5-08", scenario="Stage 2 — สร้าง \"Cutting Plan\" MO ถอดแบบ Slab เป็นชิ้นย่อย",
         note="✨ กลไกใหม่ทั้งหมด (ADR-068, session นี้): ใช้เมื่องานสั่งทำไม่มีสินค้า FG มาตรฐานให้เลือก ต้องเอา Slab มา \"ถอดแบบ\" เป็นชิ้นเล็กๆ ก่อน ทุกชิ้นจาก MO เดียวกันจะแชร์ Lot เดียวกัน (กันของปนกันตอนขนย้าย ไม่ใช่ QC รายชิ้น)",
         pre="มี Slab พร้อมอยู่แล้วในสต็อก (แยกจาก Slab ที่ใช้ใน G2)",
         steps=["เปิด Manufacturing &gt; New", "เลือก \"Source Slab (Cutting Plan)\" เป็น Slab ที่จะถอดแบบ", "ไปแท็บ \"Planned/Actual Pieces\" เพิ่มแถวขนาดชิ้นที่ต้องการ", "ย้ายด่วน &gt; Confirm &gt; Work Orders &gt; \"Complete Cutting Plan\""],
         sample="Source Slab = BLK-26-0036 #2<br>ชิ้นที่ 1: 0.25 x 0.20 m<br>ชิ้นที่ 2: 0.20 x 0.15 m<br>ชิ้นที่ 3: 0.15 x 0.10 m",
         expected="MO เสร็จสมบูรณ์ (ตัวอย่างจริง: EG01/STCPL/00009) ได้ชิ้นงานจริง 3 ชิ้้น สถานะ \"Staged (Cutting Plan WIP)\" ทุกชิ้น — แชร์ Lot เดียวกันทั้งหมด (ตัวอย่างจริง: CUT-EG01/STCPL/00009, รวม 3.00 หน่วย) ชิ้นเหล่านี้จะไม่โผล่ในหน้า \"Select Slabs\" ของโหมดขายอื่นเลย เพราะยังไม่ใช่สต็อกขายได้จริง", prio="High",
         shot="assets/e2e-mode5/m5-12-stage2-pieces.png"),
    dict(id="TC-E2E-M5-09", scenario="สร้าง Sale Order ขายสินค้า Custom (ไม่มี FG มาตรฐานให้เลือก)",
         pre="ทำ TC-E2E-M5-08 เสร็จแล้ว มี BOQ Document ผูกกับ Sale Order นี้ไว้ (จำเป็นสำหรับ wizard สร้าง BOM ในขั้นถัดไป)",
         steps=["เปิด Sales &gt; Orders &gt; New (ผูก BOQ Document)", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้า Custom", "กด Confirm"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = เจดีย์บัว S (Custom)",
         expected="SO ยืนยันสำเร็จ ยอดรวม 12,840.00 บาท (รวม VAT) บรรทัดสินค้าปรากฏลิงก์ \"Produce FG\" เหมือนเดิม แต่จะพาไปหน้าต่าง \"สร้าง BOM จาก BOQ\" แทน (ไม่ใช่สร้าง MO ตรงแบบ G2) เพราะสินค้านี้ไม่มี FG Raw Material ตายตัว — ตัวอย่างจริง: S00138", prio="High",
         shot="assets/e2e-mode5/m5-10-so2-custom-confirmed.png"),
    dict(id="TC-E2E-M5-10", scenario="Stage 3 — กด \"Produce FG\" เปิด wizard \"สร้าง BOM จาก BOQ\" เลือก Cutting Plan Lot",
         note="✨ ส่วนขยายใหม่ของ wizard เดิม (ADR-064 เดิม + ADR-068 เพิ่มเข้ามา): นอกจากเลือกวัสดุจาก BOQ ได้เหมือนเดิม ตอนนี้เลือก \"Cutting Plan Lot (Stage 2)\" ได้ด้วย — ระบบดึงมาทั้งก้อน (จำนวนเต็มของ Lot นั้น) ไม่ต้องกรอกจำนวนเอง",
         pre="ทำ TC-E2E-M5-09 เสร็จแล้ว",
         steps=["กดลิงก์ \"Produce FG\" บนบรรทัดสินค้า", "เลือกช่อง \"Cutting Plan Lot (Stage 2)\" เป็น Lot จาก Stage 2", "กด \"สร้าง BOM + MO\""],
         sample="Cutting Plan Lot (Stage 2) = CUT-EG01/STCPL/00009",
         expected="สร้าง BOM + Manufacturing Order สำเร็จ แต่ MO ยังอยู่สถานะ Draft ให้ตรวจสอบก่อน (ต่างจากงาน Custom ที่ไม่ใช้ Cutting Plan Lot ซึ่งจะ Confirm ให้อัตโนมัติทันที) — ตัวอย่างจริง: EG01/STFG/00023 มีปุ่ม \"Cutting Plan MO\" เชื่อมกลับไปหา MO ของ Stage 2 ให้แล้ว", prio="High",
         shot="assets/e2e-mode5/m5-13-stage3-mo-done.png"),
    dict(id="TC-E2E-M5-11", scenario="Confirm MO Stage 3 — ระบบเติมวัตถุดิบจาก Lot ให้อัตโนมัติ",
         pre="ทำ TC-E2E-M5-10 เสร็จแล้ว",
         steps=["ตรวจแท็บ \"Components\" ก่อน Confirm", "กดปุ่ม Confirm"],
         sample="-",
         expected="แท็บ Components เติมแถววัตถุดิบจาก Cutting Plan Lot ให้อัตโนมัติ จำนวนเท่ากับที่มีอยู่เต็มก้อน (ตัวอย่างจริง: E2E Mode5 Fresh Test V2 - Cutting Plan WIP, 3.00 หน่วย) Confirm ผ่านสำเร็จ ไม่ต้องกรอกอะไรเพิ่มเอง", prio="High",
         shot="assets/e2e-mode5/m5-13-stage3-mo-done.png"),
    dict(id="TC-E2E-M5-12", scenario="ทำ MO ให้เสร็จด้วยปุ่ม Produce มาตรฐานของ Odoo (ไม่มีปุ่มเฉพาะ)",
         note="งาน Custom ใช้ปุ่ม Produce ธรรมดาของ Odoo เลย (ตาม ADR-064 เดิม \"มาตรฐาน ODOO\") ต่างจาก Stage 2/G2 ที่มีปุ่มเฉพาะของโมดูล",
         pre="ทำ TC-E2E-M5-11 เสร็จแล้ว",
         steps=["กรอกจำนวนที่ผลิตจริง &gt; กด Generate Lot ถ้ายังไม่มี &gt; กดปุ่ม Produce All"],
         sample="-",
         expected="MO เสร็จสมบูรณ์ (สถานะ Done) ได้สินค้า Custom 1 หน่วยเข้าสต็อกจริง ชิ้นงานทั้ง 3 ชิ้นจาก Stage 2 เปลี่ยนสถานะจาก \"Staged\" เป็น \"Consumed\" อัตโนมัติ (ไม่ค้างโชว์เป็น WIP อีกต่อไป) — กลับไปดูที่ MO ของ Stage 2 จะเห็นปุ่ม \"Assembly MOs\" เชื่อมมาที่ MO นี้แล้ว", prio="High",
         shot="assets/e2e-mode5/m5-13-stage3-mo-done.png"),
    dict(id="TC-E2E-M5-13", scenario="จัดส่ง ออกใบแจ้งหนี้ และรับชำระเงิน (Custom)",
         pre="ทำ TC-E2E-M5-12 เสร็จแล้ว",
         steps=["เปิดใบส่งของที่เกิดขึ้นอัตโนมัติ &gt; Validate", "เปิด SO &gt; Create Invoice &gt; Regular Invoice &gt; Confirm", "เปิดใบแจ้งหนี้ &gt; Pay &gt; ยืนยันการชำระ"],
         sample="-",
         expected="ใบส่งของ Done (ตัวอย่างจริง: EG01/OUT/00092) ใบแจ้งหนี้ Posted ยอด 12,840.00 (ตัวอย่างจริง: INV/2026/00038) แล้วขึ้น In Payment — Journal Items 5 บรรทัด สมดุล 12,916.89 = 12,916.89 (COGS 76.89 ไม่ใช่ 0)", prio="High",
         shot="assets/e2e-mode5/m5-16-invoice2-journal.png"),
  ]),
]
