# Single source of truth for EMG-O E2E flow test cases — Mode 4
# (Sold-as-Project, ADR-021). Same spirit as qa_data_e2e_mode1/2/3.py: a
# single continuous "does the whole business flow work" story from a
# non-technical UI user's point of view, not feature-level field/validation
# checks (those already live in qa_data.py's B2 category).
#
# Mode 4 is a billing/PM/analytics OVERLAY (ADR-021), not its own physical
# fulfillment path — is_project_sale only changes (a) Analytic Account
# routing to the Project's own account and (b) the revenue GL account used.
# Whatever physical product sits on the order's lines (stone slab/lot/block,
# service, ...) still follows its own normal mode (1/2/3) for delivery/COGS.
# This file's fixture deliberately includes one real Lot-mode stone line
# (Mode 2) so the "full lifecycle" requirement (purchase -> sell -> deliver
# -> invoice -> accounting) is genuinely exercised end to end, not just the
# BOQ/Project/billing overlay in isolation.
#
# Data provenance: fresh live run built specifically for this file, driven
# through the real Odoo web UI via Playwright (not odoo shell) on
# `mbx-ee-dev`, 2026-09-06:
#   BOQ BOQ0026 (customer "ทดสอบ Mode 4 Retest - Riverside Condo", Empire
#   Granite; 2 lines: Vietnam Limestone - Slab 0.5 m² = 900 lump sum,
#   Dry-Lay 1.5 m² @ 200/m² = 300; Preliminaries 5% = 60, Overhead & Profit
#   10% = 120; BOQ Amount Total 1,380) -> Generate Quotation -> SO S00109
#   (Sold as Project ticked) -> Select Lot Stock on the stone line (Lot
#   BLK-26-0004, typed qty 0.5 m²) -> Confirm -> Project 40 auto-created
#   ("ทดสอบ Mode 4 Retest - Riverside Condo - S00109", Analytic Account 61)
#   with 4 Tasks auto-created -> Down Payment invoicing 30/40/30
#   (INV/2026/00015 ฿442.98, INV/2026/00016 ฿590.64, INV/2026/00017
#   ฿442.98 — sums exactly to the order's ฿1,476.60 incl. VAT) -> Delivery
#   EG01/OUT/00064 (Done) -> the 2 real-work Tasks marked Done -> Milestone
#   "ปูพื้นระเบียงเสร็จสมบูรณ์ (Dry-Lay Complete)" auto-Reached -> Project
#   Dashboard Profitability (Total Revenues ฿1,380 Expected = ฿1,380
#   Invoiced, untaxed) -> Journal Items verified balanced on each invoice.
#
# CORRECTIONS vs. a naive reading of the ADR-021/prior-session notes (this
# file's own live run is what surfaced these — verify against current EE
# code before trusting an older memory/doc over this file):
#   - The old "30/40/30 milestone template" is NOT how billing works anymore
#     (ADR-038 replaced it) — 30/40/30 here is 3 manual Down Payment
#     (Percentage) invoices a staff member runs by hand; nothing auto-splits
#     it. Milestones today are opt-in per BOQ line (is_milestone) and drive
#     PM/dashboard display only, never invoicing.
#   - `action_open_stone_gantt()` / the old custom Gantt widget do not exist
#     in current EE code — Gantt is the native EE `project_enterprise`
#     Gantt view switcher on the Project's Tasks, reached via the Project's
#     own "Tasks" smart button, not a dedicated button.
#
# ✅ 3 REAL BUGS found + FIXED + RE-VERIFIED, same session (2026-09-06).
# A first live run of this exact flow (BOQ0023 -> SO S00102, same fixture
# shape, previous customer "ทดสอบ Mode 4 - Boutique Villa") surfaced 3
# previously-undocumented bugs in the Lot-mode stone-material path (not
# Mode-4-specific — anything selling Lot-mode material through any sales
# mode hit the same 2 root causes):
#   1. Delivery routing (ADR-051, 2026-08-31) sourced a Lot-mode line's
#      delivery from the "Stone Hold" location — correct for Serial/Cut-to-
#      Order (which physically moves stock there via a Select Slabs wizard)
#      but WRONG for Lot mode, which has no hold step at all; physical stock
#      never leaves "Stone Available". Real consequence before the fix: this
#      exact lot's Hold balance had drifted to -2.3 m² across several
#      deliveries. FIXED in `sale_order.py`'s `_fix_stone_delivery_destination()`
#      — Lot-mode now routes through Stone Available, same as a whole-Block
#      sale. Re-verified this run: the delivery's "Pick From" correctly
#      reads "Stone Inventory/Stone Available" (see TC-E2E-M4-09).
#   2. That phantom negative Hold balance silently UNDER-REPORTED real
#      sellable stock (`remaining_sqmt` sums every internal location) — pure
#      symptom of #1, needed no separate fix. Historical bad data on this
#      lot was also corrected (a real internal-transfer stock.move moving
#      the erroneous balance back from Hold to Available, verified via a
#      separate `psql` read) — Hold now sits at a clean 0.00.
#   3. A BOQ-generated stone line bakes its full negotiated price into a
#      `qty=1` placeholder (lump sum, not a per-unit rate). Running Select
#      Lot Stock afterward corrected the quantity but not the price — core
#      Odoo's own price recompute (triggered because `product_uom_qty`
#      changed) silently reverted to the product's plain list price,
#      discarding the BOQ-quoted amount (first observed: BOQ quoted ฿900
#      for 0.5 m², came out ฿400 after Select Lot Stock). FIXED in
#      `stone.lot.stock.select.wizard.action_confirm()` — for a BOQ-sourced
#      line it now redistributes price_unit so the *total* the BOQ quoted
#      survives the quantity correction (900 total ÷ 0.5 real m² = 1,800/m²
#      unit price); a plain, non-BOQ Lot-mode line is unaffected (its
#      price_unit already is a genuine per-sqm rate, kept as-is). Re-verified
#      this run: Unit Price 1,800.00 × Qty 0.50 = Amount 900.00 exactly (see
#      TC-E2E-M4-03), and Project Dashboard Profitability shows Materials
#      ฿900 (not ฿400).
# Fix commits: `stone_slab_inventory` `34be05d` (bugs #1/#3 first pass) +
# `1e09854` (bug #3 corrected properly after this exact retest caught the
# first pass's fix preserving the wrong number — see log.md Session 111
# for the full story). Deployed to `mbx-ee-dev` only so far — `eg-tst`
# still pending the same `-u` + restart.
#
# Column model per test case (same as mode3, per feedback_qa_testcase_screenshot_export):
#   id, scenario, note (optional amber callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low),
#   shot (filename under assets/mode4/, real Playwright screenshot)

CATEGORIES = [
  dict(cat_id="F1", title="F1. ตั้งต้นจาก BOQ — เข้าสู่โหมด Sold as Project",
       subtitle="ADR-021 — เริ่มจากใบประมาณราคา (BOQ) ไม่ใช่พิมพ์ Sale Order เปล่าๆ · 2 test cases",
       cases=[
    dict(id="TC-E2E-M4-01", scenario="สร้างใบเสนอราคาจากเอกสาร BOQ (\"Generate Quotation\")",
         pre="มีเอกสาร BOQ ที่กรอกรายการและราคาเรียบร้อยแล้ว (สถานะ Draft)",
         steps=["เปิดเอกสาร BOQ", "ตรวจรายการ + % Preliminaries/Overhead ให้ครบ", "กดปุ่ม \"สร้างใบเสนอราคา\" (สีม่วง มุมซ้ายบน)"],
         sample="BOQ0026 — ลูกค้า \"ทดสอบ Mode 4 Retest - Riverside Condo\"<br>2 รายการ: Vietnam Limestone - Slab 0.5 ตร.ม. + Dry-Lay 1.5 ตร.ม.<br>Preliminaries 5% + Overhead &amp; Profit 10%",
         expected="สถานะ BOQ เปลี่ยนเป็น \"Quotation Generated\" เกิด Sale Order ใหม่ 1 ใบอัตโนมัติ ดึงทุกรายการ + ค่า Preliminaries/Overhead มาเป็นบรรทัดในใบเสนอราคาให้ครบ — ตัวอย่างจริง: BOQ0026 (รวม 1,380.00 บาท ก่อน VAT) &rarr; SO S00109", prio="High",
         shot="assets/mode4/tc01-boq-document.png"),
    dict(id="TC-E2E-M4-02", scenario="ติ๊กกล่อง \"Sold as Project\" บนใบเสนอราคา",
         pre="ทำ TC-E2E-M4-01 เสร็จแล้ว (มี SO ที่ยังไม่ Confirm)",
         steps=["เปิด Sale Order ที่เพิ่งสร้าง", "ไปแท็บ \"Other Info\"", "ติ๊กกล่อง \"Sold as Project\" ในกลุ่ม INVOICING"],
         sample="-",
         expected="กล่อง \"Sold as Project\" ติ๊กเรียบร้อย (ยังไม่ต้องกด Confirm ตอนนี้) — เมื่อ Confirm ในขั้นถัดไป ระบบจะสร้าง Project ให้อัตโนมัติจากช่องนี้", prio="High",
         shot="assets/mode4/tc02-is-project-sale.png"),
  ]),
  dict(cat_id="F2", title="F2. เตรียมสต็อกหิน + ยืนยันคำสั่งขาย",
       subtitle="เลือกสต็อกจริงให้บรรทัดหิน แล้วยืนยัน SO ให้ระบบสร้าง Project+Task ให้อัตโนมัติ · 3 test cases",
       cases=[
    dict(id="TC-E2E-M4-03", scenario="เลือกสต็อกจริงให้บรรทัดสินค้าหิน (\"Select Lot Stock\")",
         note="✅ เคยพบปัญหาจริงตรงนี้ (ราคาที่ BOQ ตั้งไว้ถูกเขียนทับด้วยราคาป้ายสินค้าปกติ) — แก้ไขแล้วและทดสอบซ้ำผ่านในรอบนี้: ระบบคำนวณราคาต่อหน่วยใหม่ให้อัตโนมัติจากยอดรวมเดิมที่ BOQ ตั้งไว้ ไม่ใช้ราคาป้ายสินค้าอีกต่อไป",
         pre="ทำ TC-E2E-M4-02 เสร็จแล้ว บรรทัดสินค้าหินยังไม่ได้ผูกกับสต็อกจริง",
         steps=["ที่บรรทัดสินค้าหิน กดลิงก์ \"Select Lot Stock\"", "เลือก Lot ของ Material นั้น", "กรอกจำนวนตร.ม.ที่จะขายจริง (ดูได้จากคำอธิบายท้ายชื่อสินค้าในบรรทัด)", "กดยืนยัน"],
         sample="Lot = BLK-26-0004<br>จำนวน = 0.5 ตร.ม.",
         expected="บรรทัดผูกกับ Lot ที่เลือกสำเร็จ จำนวนเปลี่ยนเป็น 0.5 ตร.ม. ตามที่กรอก ราคารวมของบรรทัดยังคงเท่าเดิมกับที่ BOQ ตั้งไว้เป๊ะ (ระบบคำนวณราคาต่อหน่วยใหม่ให้เอง) — ตัวอย่างจริง: ราคาต่อหน่วยเปลี่ยนจาก 900.00 (ที่จำนวน 1 หน่วยตั้งต้น) เป็น 1,800.00 บาท/ตร.ม. &times; 0.5 ตร.ม. = ยอดรวม 900.00 บาท เท่าเดิมทุกบาท", prio="High",
         shot="assets/mode4/tc03-so-confirmed.png"),
    dict(id="TC-E2E-M4-04", scenario="ยืนยัน (Confirm) Sale Order — ระบบสร้าง Project ให้อัตโนมัติ",
         pre="ทำ TC-E2E-M4-03 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น \"Sales Order\" เกิดปุ่ม/สถิติใหม่มุมบน: \"Projects 1\", \"Tasks\", \"Delivery 1\", \"Invoices\" — ไม่ต้องสร้าง Project เองแยกต่างหาก — ตัวอย่างจริง: S00109 (ยอดรวม 1,476.60 บาท รวม VAT) &rarr; Project id 40", prio="High",
         shot="assets/mode4/tc02-is-project-sale.png"),
    dict(id="TC-E2E-M4-05", scenario="ตรวจสอบ Task ที่ระบบสร้างให้อัตโนมัติใน Project",
         note="หมายเหตุ: แต่ละบรรทัดใน SO (รวมถึงบรรทัด Preliminaries/Overhead &amp; Profit ที่เป็นแค่ตัวเลขสรุป ไม่ใช่งานจริง) จะได้ Task ของตัวเอง 1 งานเสมอ — เป็นพฤติกรรมที่ทราบอยู่แล้ว (ยังไม่กรองออก) ไม่ใช่ error หากเห็น Task ชื่อ \"BOQ Summary Line Preliminaries/Overhead &amp; Profit\" ปนอยู่กับงานจริง",
         pre="ทำ TC-E2E-M4-04 เสร็จแล้ว",
         steps=["กดปุ่มสถิติ \"Tasks\" บน Sale Order (หรือเปิด Project แล้วดู Tasks)"],
         sample="-",
         expected="เห็น Task ครบ 1 งานต่อ 1 บรรทัดสินค้า/บริการ — ตัวอย่างจริง: 4 Tasks (\"Vietnam Limestone - Slab (ปูพื้นระเบียง)...\", \"Dry-Lay\", \"BOQ Summary Line Preliminaries (5%)\", \"BOQ Summary Line Overhead &amp; Profit (10%)\")", prio="Medium",
         shot="assets/mode4/tc04-tasks-created.png"),
  ]),
  dict(cat_id="F3", title="F3. เรียกเก็บเงินแบบ Down Payment 30/40/30",
       subtitle="ออกใบแจ้งหนี้มัดจำ 3 งวดด้วยมือ (ไม่ใช่ระบบตัดให้อัตโนมัติ) · 3 test cases",
       cases=[
    dict(id="TC-E2E-M4-06", scenario="สร้างใบแจ้งหนี้มัดจำงวดที่ 1 (Down Payment 30%)",
         pre="ทำ TC-E2E-M4-04 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Down payment (Percentage)\" &gt; กรอก 30", "กด \"Create Draft Invoice\"", "เปิดใบแจ้งหนี้ที่เกิดขึ้น &gt; กด Confirm"],
         sample="Down Payment = 30%",
         expected="ใบแจ้งหนี้สถานะ Posted ยอด 30% ของยอดรวม SO — ตัวอย่างจริง: INV/2026/00015 (442.98 บาท จาก 1,476.60 &times; 30%)", prio="High",
         shot="assets/mode4/tc05-dp1-30pct.png"),
    dict(id="TC-E2E-M4-07", scenario="สร้างใบแจ้งหนี้มัดจำงวดที่ 2 (Down Payment 40%)",
         pre="ทำ TC-E2E-M4-06 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\" อีกครั้ง", "เลือก \"Down payment (Percentage)\" &gt; กรอก 40", "กด \"Create Draft Invoice\"", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="Down Payment = 40%",
         expected="ใบแจ้งหนี้สถานะ Posted ยอด 40% ของยอดรวม SO — ตัวอย่างจริง: INV/2026/00016 (590.64 บาท จาก 1,476.60 &times; 40%)", prio="High",
         shot="assets/mode4/tc06-dp2-40pct.png"),
    dict(id="TC-E2E-M4-08", scenario="สร้างใบแจ้งหนี้มัดจำงวดสุดท้าย (Down Payment 30% ปิดยอด)",
         pre="ทำ TC-E2E-M4-07 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\" อีกครั้ง", "เลือก \"Down payment (Percentage)\" &gt; กรอก 30", "กด \"Create Draft Invoice\"", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="Down Payment = 30%",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดงวดสุดท้าย รวม 3 ใบแล้วเท่ากับยอด SO เป๊ะ — ตัวอย่างจริง: INV/2026/00017 (442.98 บาท) รวม 3 ใบ = 442.98 + 590.64 + 442.98 = 1,476.60 บาท ตรงกับยอด SO พอดี", prio="High",
         shot="assets/mode4/tc07-dp3-30pct.png"),
  ]),
  dict(cat_id="F4", title="F4. ส่งมอบสินค้าจริง",
       subtitle="บรรทัดสินค้าหินยังต้องเดินตามขั้นตอนส่งมอบปกติของโหมดนั้นๆ (ที่นี่คือ Mode 2 Lot) · 1 test case",
       cases=[
    dict(id="TC-E2E-M4-09", scenario="ส่งมอบสินค้า (Delivery) ให้ลูกค้า",
         note="✅ เคยพบปัญหาจริงตรงนี้ (ระบบดึงสต็อกจากจุดพัก \"Stone Hold\" ที่โหมด Lot ไม่เคยย้ายของเข้าจริง ทำให้ยอดติดลบเพิ่มขึ้นทุกครั้งที่ส่งของ) — แก้ไขแล้วและทดสอบซ้ำผ่านในรอบนี้: ระบบดึงสต็อกจากจุดที่ของจริงอยู่ (\"Stone Available\") แทน ดูรายละเอียดที่ปุ่ม \"Details\" ในรายการส่งของ",
         pre="ทำ TC-E2E-M4-08 เสร็จแล้ว มีใบส่งของอัตโนมัติรออยู่ตั้งแต่ตอน Confirm",
         steps=["เปิด Inventory &gt; Deliveries", "เปิดใบส่งของของ SO นี้", "กด Validate"],
         sample="-",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done ดึงสต็อกจากจุดที่ของจริงอยู่ถูกต้อง — ตัวอย่างจริง: EG01/OUT/00064 (Vietnam Limestone - Slab 0.5 ตร.ม., Pick From \"Stone Inventory/Stone Available\")", prio="High",
         shot="assets/mode4/tc08-delivery-done.png"),
  ]),
  dict(cat_id="F5", title="F5. ติดตามงานผ่าน Task และ Milestone",
       subtitle="ปิดงานจริง ระบบขึ้น Milestone ให้อัตโนมัติ + ดู Gantt Chart ของทั้งโปรเจกต์ · 2 test cases",
       cases=[
    dict(id="TC-E2E-M4-10", scenario="ทำ Task งานจริงให้เสร็จ (Mark as Done) — Milestone ขึ้นสถานะสำเร็จให้อัตโนมัติ",
         pre="ทำ TC-E2E-M4-09 เสร็จแล้ว มี Task ที่ตั้ง Milestone ไว้ล่วงหน้าตอนสร้าง BOQ (บรรทัด Dry-Lay)",
         steps=["เปิด Task \"Dry-Lay\"", "เลื่อนสถานะ Task ไปช่อง/สถานะ Done"],
         sample="-",
         expected="Task ขึ้นเครื่องหมายเสร็จ และ Milestone ที่ผูกกับ Task นั้นเปลี่ยนเป็น \"Reached\" ให้อัตโนมัติ โดยไม่ต้องไปกดยืนยัน Milestone แยกต่างหาก — ตัวอย่างจริง: Milestone \"ปูพื้นระเบียงเสร็จสมบูรณ์ (Dry-Lay Complete)\" ขึ้นเครื่องหมายถูกในหน้า Project Dashboard ทันที", prio="Medium",
         shot="assets/mode4/tc10-dashboard-milestone-pl.png"),
    dict(id="TC-E2E-M4-11", scenario="เปิดดู Gantt Chart ของทั้งโปรเจกต์",
         pre="ทำ TC-E2E-M4-05 เสร็จแล้ว (มี Task พร้อมวันที่วางแผนแล้ว)",
         steps=["เปิด Project ของ SO นี้", "กดปุ่มสถิติ \"Tasks\"", "สลับมุมมองด้านขวาบนเป็น \"Gantt\""],
         sample="-",
         expected="เห็นแท่ง Gantt ของแต่ละ Task เรียงตามวันที่วางแผน (จากช่อง Duration ที่กรอกไว้ตอนสร้าง BOQ) กลุ่มตามผู้รับผิดชอบ — Task ที่ทำเสร็จแล้วแสดงเป็นแท่งสีเทาจาง", prio="Low",
         shot="assets/mode4/tc09-gantt.png"),
  ]),
  dict(cat_id="F6", title="F6. ตรวจสอบบัญชี — Project P&amp;L และ Journal Items",
       subtitle="ยืนยันว่ารายได้ที่ผูก Analytic Account ของโปรเจกต์ถูกต้อง และใบแจ้งหนี้แต่ละใบลงบัญชีสมดุล · 2 test cases",
       cases=[
    dict(id="TC-E2E-M4-12", scenario="ตรวจสอบกำไรขาดทุนของโปรเจกต์ (Project P&amp;L) บน Dashboard",
         pre="ทำ TC-E2E-M4-08 เสร็จแล้ว (ออกใบแจ้งหนี้ครบ 3 งวด)",
         steps=["เปิด Project ของ SO นี้", "ดูส่วน \"Profitability\" บนหน้า Dashboard ของ Project"],
         sample="-",
         expected="เห็นยอดรายได้แยกตามหมวด (Materials / Other Services / Down Payments) รวมกันแล้วต้องเท่ากับยอดใบแจ้งหนี้ทั้งหมด (ไม่รวม VAT) — ตัวอย่างจริง: Other Services 480 + Materials 900 = Total Revenues 1,380 บาท ตรงกับยอด Invoiced 1,380 บาททั้งหมด (ออกครบ 3 งวดแล้ว จึง Expected = Invoiced พอดี ไม่มียอดค้าง \"To Invoice\" — ยอด Materials 900 นี้คือหลักฐานว่าราคาที่ BOQ ตั้งไว้ไม่ถูกเขียนทับแล้ว, ดู TC-03)", prio="Medium",
         shot="assets/mode4/tc10-dashboard-milestone-pl.png"),
    dict(id="TC-E2E-M4-13", scenario="ตรวจรายการบัญชีของใบแจ้งหนี้แต่ละงวด (Journal Items)",
         pre="ทำ TC-E2E-M4-08 เสร็จแล้ว",
         steps=["เปิดใบแจ้งหนี้งวดใดงวดหนึ่ง &gt; กดแท็บ \"Journal Items\""],
         sample="-",
         expected="เดบิต/เครดิตสมดุลกัน (รวมเท่ากันทั้ง 2 ฝั่ง) เห็น Analytic Distribution ผูกกับบัญชี Analytic ของโปรเจกต์นี้บนบรรทัดรายได้ — ตัวอย่างจริง: INV/2026/00017 เดบิต Trade Receivables 442.98 = เครดิต Down Payment 414.00 + Output VAT 28.98 พอดี พร้อมป้าย Analytic \"BOQ0026 - ทดสอบ Mode 4 Retest...\"", prio="Medium",
         shot="assets/mode4/tc11-journal-items.png"),
  ]),
]

if __name__ == '__main__':
    total = sum(len(c['cases']) for c in CATEGORIES)
    prios = {'High': 0, 'Medium': 0, 'Low': 0}
    for c in CATEGORIES:
        for tc in c['cases']:
            prios[tc['prio']] += 1
    print('Total test cases:', total)
    print('Priority breakdown:', prios)
    print('Categories:', len(CATEGORIES))
