# Single source of truth for EMG-O E2E flow test cases — Mode 5
# (Stone Production/FG, ADR-029): sell a finished good (e.g. a Countertop)
# that is fabricated from an already-cut Slab, not sold as raw stone
# itself. Same spirit as qa_data_e2e_mode1/2/3/4.py.
#
# FULL REWRITE 2026-09-14 (v2, not a screenshot refresh) — the Slab-cutting
# mechanism this doc's raw material depends on (Mode 3's native-MO Block
# cutting) was rebuilt the day before (ADR-061/062, see
# qa_data_e2e_mode3.py's own build notes) and the material_lot_id bug fix
# from that rebuild (qa_data_e2e_mode2.py) landed before this run — so this
# is also the first live Playwright click-through of the FG Production
# wizard (stone.fg.production.wizard, ADR-029) built on top of that fixed
# foundation. The wizard/Produce FG mechanism itself was NOT touched by the
# 2026-09-13 teardown (that only removed the old Cut-to-Order wizard/
# Factory Worklist) — verified this run, unchanged.
#
# Data provenance: fresh live run built specifically for this file, driven
# through the real Odoo web UI via Playwright (not odoo shell) on
# `mbx-ee-dev`, 2026-09-14, on a brand-new dedicated test material ("E2E
# Mode5 Fresh Test") so nothing carries over cost history from another
# mode's fixture (see qa_data_e2e_mode1.py for why that matters):
#   Quick Material Setup -> Material "E2E Mode5 Fresh Test" (Marble, Italy,
#   density 2.7) with all 3 products: Slab (sales 4,500/cost 2,800 per
#   Sq.Mt.), Block (sales 17,500/cost 15,000 per CBM), FG "Countertop"
#   (sales 8,500/cost 5,200 per unit, FG Category "Stone FG - Countertop")
#   -> PO P00054 (3.00 CBM @ 15,000 = 45,000 + VAT 3,150 = 48,150.00) ->
#   Bundle BLK-26-0029 created via the PO line's own "สร้าง Block" button
#   (NOT the normal Purchase Receipt — see note on TC-E2E-M5 fixture below)
#   -> Vendor Bill BILL/2026/09/0006 (48,150.00, created manually via
#   Accounting > Vendors > Bills, same reason as Mode 3's fixture: the
#   PO's own "Create Bill" never appears because Received stays 0.00 under
#   the Bundle mechanism) -> Internal Transfer EG01/INT/00060 (Block:
#   Stone Available -> Stone Production) -> MO EG01/STCUT/00043 (Stone
#   Block = BLK-26-0029, Target 1.5 x 1.0 m, Reason (No SO) = "อื่นๆ
#   (Other)" — cut speculatively, no sale yet) -> Complete Cut -> Slab
#   BLK-26-0029-1 (1.5 Sq.Mt.) -> Internal Transfer EG01/INT/00061 (Slab:
#   Stone Available -> Stone Production, same physical fabrication station
#   as Block cutting) -> SO1 S00127 (FG Countertop x1, 8,500 + VAT 595 =
#   9,095.00) confirmed, no FG stock yet -> "Produce FG" wizard: Slab
#   auto-matched (BLK-26-0029 #1), output qty raised 1 -> 2 (produce a
#   spare unit — ADR-029's output is decided at production time, not a
#   fixed 1:1 ratio) -> Produce -> MO EG01/STFG/00015 (qty 2.00, auto-
#   confirmed) -> Complete FG Production -> 2 Countertop units land in
#   stock, Slab flips to Consumed -> Delivery EG01/OUT/00081 (SO1)
#   validated -> Invoice INV/2026/00031 (9,095.00) posted -> SO2 S00128
#   (same customer, same FG Countertop x1, same 9,095.00) confirmed — this
#   time NO production needed, the spare unit from SO1's run covers it,
#   Delivery reserves immediately -> Delivery EG01/OUT/00082 validated ->
#   Invoice INV/2026/00032 (9,095.00) posted -> both invoices Register
#   Payment -> In Payment. Journal Items identical on both invoices:
#   Sales Revenue - FG Production 8,500 cr / Output VAT 595 cr / Trade
#   Receivables 9,095 dr / Inventory - Stone FG (Finished Goods) 375 cr /
#   Cost of Goods Sold 375 dr — balances 9,470.00 = 9,470.00, real non-zero
#   COGS, correct dedicated accounts, Analytic tags (Material + Bundle)
#   carried through on every line. Fixture kept on mbx-ee-dev as genuine
#   reference data.
#
# Real nuances found this run (not bugs, just non-obvious):
#   1) A Block-backed material's stock is NEVER received through a normal
#      Purchase Receipt — validating that receipt by hand throws "Invalid
#      Operation" (สต็อกถูกจัดการอัตโนมัติผ่านระบบ EMG-O Block แล้ว). The
#      correct path is the PO line's own "สร้าง Block" button, which also
#      auto-cancels the now-redundant receipt for you. Same as every other
#      Block-backed mode in this suite (1/3/5).
#   2) The Vendor Bill can't come from the PO's own "Create Bill" button
#      here — Received Qty stays 0.00 forever under the Bundle mechanism,
#      so that button never appears. Create the Bill manually (Accounting
#      > Vendors > Bills > New) and use the "Auto-Complete" field to pull
#      the PO's lines in instead. Same lesson as qa_data_e2e_mode3.py.
#   3) A freshly-cut Slab is NOT automatically at the fabrication station —
#      exactly like a Block before Mode 3's cutting, it must be moved to
#      "Stone Production" via a real Internal Transfer before "Produce FG"
#      will accept it as raw material (both fabrication steps share one
#      physical station by design, per stone_fg_production_wizard.py's own
#      comment).
#   4) The "Produce FG" link on the SO line is NOT gated on stock
#      availability — it stayed visible on SO2's confirmed line even
#      though that line's delivery reserved immediately from existing
#      stock with zero clicks needed. The real G2a/G2b distinction is
#      whether Admin NEEDS to click it (delivery already reservable) or
#      not (delivery stuck on "Waiting" until FG is actually produced),
#      not whether the link itself is shown.
#   5) One Slab can yield MORE finished-good units than any single order
#      needs — the output quantity is typed by hand at production time
#      (ADR-029: "decided at production time, not a fixed ratio"), so a
#      single Produce FG run can deliberately build spare stock for a
#      later, unrelated order, exactly as demonstrated by SO1 -> SO2 here.
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber/green callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low)
#   shot (filename under assets/e2e-mode5/, real Playwright screenshot)

CATEGORIES = [
  dict(cat_id="G1", title="G1. ขาย (Sale — สินค้าสำเร็จรูปที่ต้องผลิตจาก Slab)",
       subtitle="ADR-029 — ขายสินค้า FG (เช่น Countertop) ที่ยังไม่ได้ผลิตจริงได้เลย · 2 test cases",
       cases=[
    dict(id="TC-E2E-M5-01", scenario="เพิ่มบรรทัดสินค้า FG (Finished Good) ใน Sale Order ใหม่",
         pre="มี Slab พร้อมอยู่แล้วในสต็อกที่สถานีผลิต (Stone Production) จาก Material ที่ตั้งค่า FG ไว้ (มี Block/Slab/FG ครบ 3 สินค้า)",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้า", "เพิ่มบรรทัด เลือกสินค้า FG ของ Material นั้น"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = E2E Mode5 Fresh Test - Countertop",
         expected="เพิ่มบรรทัดสำเร็จ ราคาต่อหน่วยขึ้นเป็นราคาตั้งต้นของสินค้า FG (ตัวอย่างจริง: 8,500/หน่วย)", prio="Medium",
         shot="assets/e2e-mode5/m5-01-so-line-added.png"),
    dict(id="TC-E2E-M5-02", scenario="ยืนยัน (Confirm) Sale Order — ยังไม่มี FG ในสต็อกเลย",
         pre="ทำ TC-E2E-M5-01 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น Sales Order ยอดรวม 9,095.00 บาท (รวม VAT) — บรรทัดสินค้า FG ปรากฏลิงก์ \"Produce FG\" ให้กดเพื่อผลิต เพราะยังไม่มีสต็อก FG เลย — ตัวอย่างจริง: S00127", prio="High",
         shot="assets/e2e-mode5/m5-02-so-confirmed-produce-link.png"),
  ]),
  dict(cat_id="G2", title="G2. ผลิต — กรณี FG ไม่มี/ไม่พอในสต็อก (ต้องผลิตจริง)",
       subtitle="ADR-029, stone.fg.production.wizard — เปิด wizard \"Produce FG\" ตัดจาก Slab ที่มีอยู่ · 3 test cases",
       cases=[
    dict(id="TC-E2E-M5-03", scenario="เปิด wizard \"Produce FG\" — ระบบจับคู่ Slab ที่จะใช้ให้อัตโนมัติ",
         pre="ทำ TC-E2E-M5-02 เสร็จแล้ว มี Slab พร้อมอยู่ที่สถานีผลิตแล้ว (ย้ายด้วย Internal Transfer ล่วงหน้า)",
         steps=["กดลิงก์ \"Produce FG\" บนบรรทัดสินค้า FG ของ Sale Order"],
         sample="-",
         expected="เปิด wizard สำเร็จ ช่อง \"Slab to Consume\" เติมให้อัตโนมัติเป็น Slab ตัวแรกที่มี Material ตรงกันและสถานะ Available (v1: จับคู่ตาม Material อย่างเดียว) พร้อมบรรทัดผลผลิตเริ่มต้น 1 บรรทัดตรงกับสินค้าที่ขาย จำนวน 1 — ตัวอย่างจริง: Slab BLK-26-0029 #1", prio="High",
         shot="assets/e2e-mode5/m5-03-produce-fg-wizard.png"),
    dict(id="TC-E2E-M5-04", scenario="ปรับจำนวนผลผลิตแล้วกด \"Produce\" — สร้าง Manufacturing Order",
         note="ผลผลิตต่อ Slab กำหนดตอนผลิตจริง ไม่ใช่อัตราตายตัว (ADR-029) — เคสนี้ตั้งใจผลิต 2 หน่วยจาก Slab เดียว แม้บรรทัด SO ต้องการแค่ 1 หน่วย เพื่อเผื่อสต็อกไว้ขายลูกค้ารายถัดไป (ดู TC-E2E-M5-07)",
         pre="ทำ TC-E2E-M5-03 เสร็จแล้ว",
         steps=["แก้ไขจำนวนในบรรทัดผลผลิตจาก 1 เป็น 2", "กดปุ่ม \"Produce\""],
         sample="จำนวนผลผลิต = 2",
         expected="สร้าง Manufacturing Order สำเร็จ ยืนยันอัตโนมัติทันที (Confirmed) ระบบเติม Bill of Material ให้อัตโนมัติจาก FG Material ที่เลือก จำนวนที่จะผลิต = 2.00 Slab ที่เลือกถูกจับจองเป็นวัตถุดิบ (To Consume 1.00, Available) ผูกกับบรรทัด SO เดิม (\"For Sale Order Line\") — ตัวอย่างจริง: EG01/STFG/00015", prio="High",
         shot="assets/e2e-mode5/m5-04-fg-mo-confirmed.png"),
    dict(id="TC-E2E-M5-05", scenario="กด \"Complete FG Production\" — ได้สินค้า FG จริงเข้าสต็อก",
         pre="ทำ TC-E2E-M5-04 เสร็จแล้ว",
         steps=["กดปุ่ม \"Complete FG Production\" บน Manufacturing Order"],
         sample="-",
         expected="Manufacturing Order เสร็จสมบูรณ์ (สถานะ Done) จำนวนที่ผลิตจริง = 2.00/2.00 ได้ Lot/Serial ใหม่ของสินค้า FG (ตัวอย่างจริง: FG-EG01/STFG/00015) Slab ที่ใช้เป็นวัตถุดิบเปลี่ยนสถานะเป็น Consumed หมดสภาพขายต่อ สินค้า FG 2 หน่วยเข้าสต็อกจริง", prio="High",
         shot="assets/e2e-mode5/m5-05-fg-mo-done.png"),
  ]),
  dict(cat_id="G3", title="G3. จัดส่ง + ขายซ้ำ — กรณี FG มีสต็อกพอแล้ว (ไม่ต้องผลิตซ้ำ)",
       subtitle="ส่งของบรรทัดแรก แล้วขายลูกค้าใหม่ด้วยสต็อกส่วนเกินที่เหลือ ไม่ต้องผ่าน wizard อีก · 3 test cases",
       cases=[
    dict(id="TC-E2E-M5-06", scenario="จัดส่งใบส่งของของบรรทัดแรก (SO1)",
         pre="ทำ TC-E2E-M5-05 เสร็จแล้ว มีสินค้า FG พร้อมส่งแล้ว",
         steps=["เปิดใบส่งของ (Delivery) ที่เกิดขึ้นอัตโนมัติของ S00127", "กดปุ่ม Validate"],
         sample="-",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done สำเร็จทันที (จองสต็อกไว้ให้แล้วตั้งแต่ผลิตเสร็จ) — ตัวอย่างจริง: EG01/OUT/00081", prio="High",
         shot="assets/e2e-mode5/m5-06-delivery1-done.png"),
    dict(id="TC-E2E-M5-07", scenario="สร้าง Sale Order ใหม่ขายสินค้า FG ตัวเดียวกันอีกครั้ง — ใช้สต็อกส่วนเกิน",
         note="✨ พฤติกรรมจริงที่พบ: ลิงก์ \"Produce FG\" ยังปรากฏอยู่บนบรรทัดเสมอ ไม่ว่าสต็อกจะพอหรือไม่ — จุดต่างจริงของ G2a คือ \"ไม่จำเป็นต้องกด\" เพราะใบส่งของจองสต็อกสำเร็จได้เองทันที ไม่ใช่ว่าลิงก์หายไป",
         pre="ทำ TC-E2E-M5-06 เสร็จแล้ว มีสินค้า FG เหลือในสต็อก 1 หน่วยจากการผลิตครั้งก่อน",
         steps=["เปิด Sales &gt; Orders &gt; New", "เลือกลูกค้าเดิม", "เพิ่มบรรทัด เลือกสินค้า FG ตัวเดียวกัน จำนวน 1", "กด Confirm"],
         sample="ลูกค้า = \"ทดสอบ E2E - Test Customer\"<br>สินค้า = E2E Mode5 Fresh Test - Countertop<br>จำนวน = 1",
         expected="SO ยืนยันสำเร็จ ยอดรวม 9,095.00 บาทเท่าเดิม ใบส่งของที่เกิดขึ้นอัตโนมัติจองสต็อก (Reserved/Assigned) ได้ทันทีจากสต็อกส่วนเกินที่เหลือ โดยไม่ต้องเปิด \"Produce FG\" เลย — ตัวอย่างจริง: S00128", prio="High",
         shot="assets/e2e-mode5/m5-07-so2-confirmed-no-produce-needed.png"),
    dict(id="TC-E2E-M5-08", scenario="จัดส่งใบส่งของของบรรทัดที่สอง (SO2)",
         pre="ทำ TC-E2E-M5-07 เสร็จแล้ว",
         steps=["เปิดใบส่งของ (Delivery) ที่เกิดขึ้นอัตโนมัติของ S00128", "กดปุ่ม Validate"],
         sample="-",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done สำเร็จทันที เหมือนกับ TC-E2E-M5-06 ทุกประการ — ตัวอย่างจริง: EG01/OUT/00082", prio="High",
         shot="assets/e2e-mode5/m5-08-delivery2-done.png"),
  ]),
  dict(cat_id="G4", title="G4. บัญชี (Accounting + Payment)",
       subtitle="ออกใบแจ้งหนี้ทั้ง 2 ใบ + รับชำระเงิน + ตรวจรายการบัญชี (COGS ต้องไม่เป็น 0) · 5 test cases",
       cases=[
    dict(id="TC-E2E-M5-09", scenario="ออกใบแจ้งหนี้บรรทัดแรก (SO1)",
         pre="ทำ TC-E2E-M5-06 เสร็จแล้ว",
         steps=["เปิด Sale Order S00127 &gt; กดปุ่ม \"Create Invoice\"", "เลือก \"Regular Invoice\" &gt; Create Draft Invoice", "กด Confirm บนใบแจ้งหนี้"],
         sample="-",
         expected="ใบแจ้งหนี้ยืนยันสำเร็จ สถานะ Posted ยอดรวม 9,095.00 บาท (รวม VAT) — ตัวอย่างจริง: INV/2026/00031", prio="High",
         shot="assets/e2e-mode5/m5-09-invoice1-posted.png"),
    dict(id="TC-E2E-M5-10", scenario="ออกใบแจ้งหนี้บรรทัดที่สอง (SO2)",
         pre="ทำ TC-E2E-M5-08 เสร็จแล้ว",
         steps=["เปิด Sale Order S00128 &gt; กดปุ่ม \"Create Invoice\"", "เลือก \"Regular Invoice\" &gt; Create Draft Invoice", "กด Confirm บนใบแจ้งหนี้"],
         sample="-",
         expected="ใบแจ้งหนี้ยืนยันสำเร็จ สถานะ Posted ยอดรวม 9,095.00 บาทเท่ากับใบแรกทุกประการ (ราคาขายเท่ากัน) — ตัวอย่างจริง: INV/2026/00032", prio="High",
         shot="assets/e2e-mode5/m5-10-invoice2-posted.png"),
    dict(id="TC-E2E-M5-11", scenario="ตรวจรายการบัญชีของใบแจ้งหนี้ (Journal Items) — ต้นทุนขาย (COGS) ต้องไม่เป็น 0",
         pre="ทำ TC-E2E-M5-09 เสร็จแล้ว",
         steps=["เปิด Customer Invoice &gt; กดแท็บ \"Journal Items\""],
         sample="-",
         expected="เห็นรายการครบ 5 บรรทัด สมดุลกันทั้ง 2 ฝั่ง (เดบิต = เครดิต) พร้อม Analytic Distribution ผูกกับ Material/Block ทุกบรรทัด — ตัวอย่างจริง INV/2026/00031: เครดิต \"411150 Sales Revenue - FG Production\" 8,500.00, เครดิต \"213200 Output VAT\" 595.00, เดบิต \"112100 Trade Receivables\" 9,095.00, เครดิต \"113150 Inventory - Stone FG (Finished Goods)\" 375.00, เดบิต \"511100 Cost of Goods Sold\" 375.00 — รวมสมดุล 9,470.00 = 9,470.00 (COGS ไม่ใช่ 0 บาท ตัดจริงตามบัญชีที่ถูกต้อง)", prio="High",
         shot="assets/e2e-mode5/m5-11-journal-items.png"),
    dict(id="TC-E2E-M5-12", scenario="บันทึกรับชำระเงินใบแจ้งหนี้บรรทัดแรก (SO1)",
         pre="ทำ TC-E2E-M5-09 เสร็จแล้ว",
         steps=["เปิดใบแจ้งหนี้ &gt; กดปุ่ม \"Pay\"", "เลือกวิธีชำระเงินที่ต้องการ &gt; กดยืนยัน"],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นสถานะ \"In Payment\" ทันที — ตัวอย่างจริง: INV/2026/00031", prio="Medium",
         shot="assets/e2e-mode5/m5-12-invoice1-in-payment.png"),
    dict(id="TC-E2E-M5-13", scenario="บันทึกรับชำระเงินใบแจ้งหนี้บรรทัดที่สอง (SO2)",
         pre="ทำ TC-E2E-M5-10 เสร็จแล้ว",
         steps=["เปิดใบแจ้งหนี้ &gt; กดปุ่ม \"Pay\"", "เลือกวิธีชำระเงินที่ต้องการ &gt; กดยืนยัน"],
         sample="-",
         expected="ใบแจ้งหนี้ขึ้นสถานะ \"In Payment\" ทันทีเหมือนกัน — ตัวอย่างจริง: INV/2026/00032", prio="Medium",
         shot="assets/e2e-mode5/m5-13-invoice2-in-payment.png"),
  ]),
]
