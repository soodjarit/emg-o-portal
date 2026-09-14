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
# REBUILT 2026-09-14 (v2) — full fresh live re-run per user request ("run
# playwrite ใหม่ ไม่เอาหน้าจอเก่า"), old doc + screenshots moved to
# qa/_archive/. Unlike Mode 2/3, this overlay mechanism itself was NOT
# touched by the 2026-09-13 Factory Worklist teardown (that only affected
# the Cut-to-Order wizard) — verified this run: BOQ->Project->Milestone->
# Down Payment billing all behave identically to the v1 doc. Reused the
# existing Rate Library items ([VNL-M4-02] Vietnam Limestone, [BCH-08]
# Dry-Lay) that earlier Mode 4 sessions built specifically for this
# purpose, and the same shared "Vietnam Limestone" stock pool (still has
# real Available stock under its own long-lived material_lot_id, unaffected
# by the Mode 2 bug/fix since that bundle was never cut through the new
# native-MO mechanism) — only the BOQ document + Sale Order + Project +
# Invoices are a fresh fixture.
#
# Data provenance: fresh live run built specifically for this file, driven
# through the real Odoo web UI via Playwright (not odoo shell) on
# `mbx-ee-dev`, 2026-09-14:
#   BOQ0029 (customer "ทดสอบ Mode4 Fresh - Sample Project", Empire Granite;
#   2 lines: Vietnam Limestone - Slab 0.5 m² = 900 lump sum, Dry-Lay 1.5 m²
#   @ 200/m² = 300; Preliminaries 5% = 60, Overhead & Profit 10% = 120; BOQ
#   Amount Total 1,380) -> Generate Quotation -> SO S00126 (Sold as Project
#   ticked) -> Select Lot Stock on the stone line (Lot BLK-26-0004, typed
#   qty 0.5 m²) -> Confirm -> Project 41 auto-created ("ทดสอบ Mode4 Fresh -
#   Sample Project - S00126") with 4 Tasks auto-created -> Down Payment
#   invoicing 30/40/30 (INV/2026/00028 ฿442.98, INV/2026/00029 ฿590.64,
#   INV/2026/00030 ฿442.98 — sums exactly to the order's ฿1,476.60 incl.
#   VAT) -> Delivery EG01/OUT/00080 (Done, scan-verified) -> the Dry-Lay
#   Task marked Done -> Milestone "ปูพื้นเสร็จสมบูรณ์ (Dry-Lay Complete)"
#   auto-Reached -> Project Dashboard Profitability (Total Revenues ฿1,380
#   Expected = ฿1,380 Invoiced, untaxed) -> Journal Items verified balanced
#   on each invoice.
#
# Real nuance found this run (not a bug, just non-obvious): the Sale
# Order's own "Tasks" smart button only shows tasks with sale_line_id set
# (service-tracked lines only — physical material lines can't carry
# sale_line_id due to a native sale_project constraint) — 3 of the 4
# Tasks. To see the material line's own Task too, open the Project directly
# and use its own Tasks view instead of the SO's smart button. TC-05 below
# is written around that reliable path.
#
# ✅ Both real bugs found+fixed in the original v1 build (2026-09-06) still
# verified fixed this run: (1) BOQ-quoted lump-sum price is NOT overwritten
# by the product's plain list price once Select Lot Stock corrects the
# quantity (TC-03) — Materials revenue on the Dashboard (900) is the direct
# evidence; (2) Delivery correctly pulls stock from "Stone Available", not
# the never-populated "Stone Hold" bucket (TC-09).
#
# Column model per test case (same as qa_data.py):
#   id, scenario, note (optional amber/green callout), pre, steps (list),
#   sample (str, the "key this in" data - '-' if the case has nothing to key),
#   expected, prio (High/Medium/Low)
#   shot (filename under assets/e2e-mode4/, real Playwright screenshot)

CATEGORIES = [
  dict(cat_id="F1", title="F1. ตั้งต้นจาก BOQ — เข้าสู่โหมด Sold as Project",
       subtitle="ADR-021 — เริ่มจากใบประมาณราคา (BOQ) ไม่ใช่พิมพ์ Sale Order เปล่าๆ · 2 test cases",
       cases=[
    dict(id="TC-E2E-M4-01", scenario="สร้างใบเสนอราคาจากเอกสาร BOQ (\"สร้างใบเสนอราคา\")",
         pre="มีเอกสาร BOQ ที่กรอกรายการและราคาเรียบร้อยแล้ว (สถานะ Draft)",
         steps=["เปิดเอกสาร BOQ", "ตรวจรายการ + % Preliminaries/Overhead ให้ครบ", "กดปุ่ม \"สร้างใบเสนอราคา\" (สีม่วง มุมซ้ายบน)"],
         sample="BOQ0029 — ลูกค้า \"ทดสอบ Mode4 Fresh - Sample Project\"<br>2 รายการ: Vietnam Limestone - Slab 0.5 ตร.ม. + Dry-Lay 1.5 ตร.ม.<br>Preliminaries 5% + Overhead &amp; Profit 10%",
         expected="สถานะ BOQ เปลี่ยนเป็น \"Quotation Generated\" เกิด Sale Order ใหม่ 1 ใบอัตโนมัติ ดึงทุกรายการ + ค่า Preliminaries/Overhead มาเป็นบรรทัดในใบเสนอราคาให้ครบ — ตัวอย่างจริง: BOQ0029 (รวม 1,380.00 บาท ก่อน VAT) &rarr; SO S00126", prio="High",
         shot="assets/e2e-mode4/tc01-boq-document.png"),
    dict(id="TC-E2E-M4-02", scenario="ติ๊กกล่อง \"Sold as Project\" บนใบเสนอราคา",
         pre="ทำ TC-E2E-M4-01 เสร็จแล้ว (มี SO ที่ยังไม่ Confirm)",
         steps=["เปิด Sale Order ที่เพิ่งสร้าง", "ไปแท็บ \"Other Info\"", "ติ๊กกล่อง \"Sold as Project\" ในกลุ่ม INVOICING"],
         sample="-",
         expected="กล่อง \"Sold as Project\" ติ๊กเรียบร้อย (ยังไม่ต้องกด Confirm ตอนนี้) — เมื่อ Confirm ในขั้นถัดไป ระบบจะสร้าง Project ให้อัตโนมัติจากช่องนี้", prio="High",
         shot="assets/e2e-mode4/tc02-is-project-sale.png"),
  ]),
  dict(cat_id="F2", title="F2. เตรียมสต็อกหิน + ยืนยันคำสั่งขาย",
       subtitle="เลือกสต็อกจริงให้บรรทัดหิน แล้วยืนยัน SO ให้ระบบสร้าง Project+Task ให้อัตโนมัติ · 3 test cases",
       cases=[
    dict(id="TC-E2E-M4-03", scenario="เลือกสต็อกจริงให้บรรทัดสินค้าหิน (\"Select Lot Stock\")",
         note="✅ ยืนยันแล้วว่าบั๊กเดิม (ราคาที่ BOQ ตั้งไว้ถูกเขียนทับด้วยราคาป้ายสินค้าปกติ) ยังคงปิดอยู่จริง: ระบบคำนวณราคาต่อหน่วยใหม่ให้อัตโนมัติจากยอดรวมเดิมที่ BOQ ตั้งไว้ ไม่ใช้ราคาป้ายสินค้า",
         pre="ทำ TC-E2E-M4-02 เสร็จแล้ว บรรทัดสินค้าหินยังไม่ได้ผูกกับสต็อกจริง",
         steps=["ที่บรรทัดสินค้าหิน กดลิงก์ \"Select Lot Stock\"", "เลือก Lot ของ Material นั้น", "กรอกจำนวนตร.ม.ที่จะขายจริง", "กดยืนยัน"],
         sample="Lot = BLK-26-0004<br>จำนวน = 0.5 ตร.ม.",
         expected="บรรทัดผูกกับ Lot ที่เลือกสำเร็จ จำนวนเปลี่ยนเป็น 0.5 ตร.ม. ตามที่กรอก ราคารวมของบรรทัดยังคงเท่าเดิมกับที่ BOQ ตั้งไว้เป๊ะ (ตัวอย่างจริง: ยอดรวม SO ยังคงเป็น 1,476.60 บาท เท่าเดิม ไม่เปลี่ยนหลังผูก Lot)", prio="High",
         shot="assets/e2e-mode4/tc03-so-confirmed.png"),
    dict(id="TC-E2E-M4-04", scenario="ยืนยัน (Confirm) Sale Order — ระบบสร้าง Project ให้อัตโนมัติ",
         pre="ทำ TC-E2E-M4-03 เสร็จแล้ว",
         steps=["กดปุ่ม Confirm บน Sale Order"],
         sample="-",
         expected="SO เปลี่ยนสถานะเป็น \"Sales Order\" เกิดปุ่ม/สถิติใหม่มุมบน: \"Projects 1\", \"Tasks 3\", \"Delivery 1\" — ไม่ต้องสร้าง Project เองแยกต่างหาก — ตัวอย่างจริง: S00126 (ยอดรวม 1,476.60 บาท รวม VAT) &rarr; Project id 41", prio="High",
         shot="assets/e2e-mode4/tc04-so-confirmed.png"),
    dict(id="TC-E2E-M4-05", scenario="ตรวจสอบ Task ที่ระบบสร้างให้อัตโนมัติใน Project",
         note="หมายเหตุ: ปุ่มสถิติ \"Tasks\" บน Sale Order เอง จะโชว์ให้เห็นแค่ Task ที่เป็นบรรทัดบริการ (3 จาก 4 งาน) เพราะบรรทัดสินค้าวัสดุจริงผูก sale_line_id ไม่ได้ตามข้อจำกัดของระบบ — ต้องเปิด Project เองแล้วดู Tasks จากตรงนั้นถึงจะเห็นครบทั้ง 4 งาน แต่ละบรรทัดใน SO (รวมถึงบรรทัด Preliminaries/Overhead &amp; Profit ที่เป็นแค่ตัวเลขสรุป ไม่ใช่งานจริง) จะได้ Task ของตัวเอง 1 งานเสมอ",
         pre="ทำ TC-E2E-M4-04 เสร็จแล้ว",
         steps=["เปิด Project ของ SO นี้ (กดปุ่มสถิติ \"Projects\" บน Sale Order)", "กดปุ่มสถิติ \"Tasks\" บน Project (ไม่ใช่บน Sale Order)"],
         sample="-",
         expected="เห็น Task ครบ 4 งาน หนึ่งงานต่อหนึ่งบรรทัดสินค้า/บริการ — ตัวอย่างจริง: \"Vietnam Limestone - Slab (ปูพื้นระเบียง) — 0.5 m²\", \"Dry-Lay\", \"BOQ Summary Line Preliminaries (5%)\", \"BOQ Summary Line Overhead &amp; Profit (10%)\"", prio="Medium",
         shot="assets/e2e-mode4/tc05-tasks-created.png"),
  ]),
  dict(cat_id="F3", title="F3. เรียกเก็บเงินแบบ Down Payment 30/40/30",
       subtitle="ออกใบแจ้งหนี้มัดจำ 3 งวดด้วยมือ (ไม่ใช่ระบบตัดให้อัตโนมัติ) · 3 test cases",
       cases=[
    dict(id="TC-E2E-M4-06", scenario="สร้างใบแจ้งหนี้มัดจำงวดที่ 1 (Down Payment 30%)",
         pre="ทำ TC-E2E-M4-04 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\"", "เลือก \"Down payment (Percentage)\" &gt; กรอก 30", "กด \"Create Draft Invoice\"", "เปิดใบแจ้งหนี้ที่เกิดขึ้น &gt; กด Confirm"],
         sample="Down Payment = 30%",
         expected="ใบแจ้งหนี้สถานะ Posted ยอด 30% ของยอดรวม SO — ตัวอย่างจริง: INV/2026/00028 (442.98 บาท จาก 1,476.60 &times; 30%)", prio="High",
         shot="assets/e2e-mode4/tc06-dp1-30pct.png"),
    dict(id="TC-E2E-M4-07", scenario="สร้างใบแจ้งหนี้มัดจำงวดที่ 2 (Down Payment 40%)",
         pre="ทำ TC-E2E-M4-06 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\" อีกครั้ง", "เลือก \"Down payment (Percentage)\" &gt; กรอก 40", "กด \"Create Draft Invoice\"", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="Down Payment = 40%",
         expected="ใบแจ้งหนี้สถานะ Posted ยอด 40% ของยอดรวม SO — ตัวอย่างจริง: INV/2026/00029 (590.64 บาท จาก 1,476.60 &times; 40%)", prio="High",
         shot="assets/e2e-mode4/tc07-dp2-40pct.png"),
    dict(id="TC-E2E-M4-08", scenario="สร้างใบแจ้งหนี้มัดจำงวดสุดท้าย (Down Payment 30% ปิดยอด)",
         pre="ทำ TC-E2E-M4-07 เสร็จแล้ว",
         steps=["เปิด Sale Order &gt; กด \"Create Invoice\" อีกครั้ง", "เลือก \"Down payment (Percentage)\" &gt; กรอก 30", "กด \"Create Draft Invoice\"", "เปิดใบแจ้งหนี้ &gt; กด Confirm"],
         sample="Down Payment = 30%",
         expected="ใบแจ้งหนี้สถานะ Posted ยอดงวดสุดท้าย รวม 3 ใบแล้วเท่ากับยอด SO เป๊ะ — ตัวอย่างจริง: INV/2026/00030 (442.98 บาท) รวม 3 ใบ = 442.98 + 590.64 + 442.98 = 1,476.60 บาท ตรงกับยอด SO พอดี", prio="High",
         shot="assets/e2e-mode4/tc08-dp3-30pct.png"),
  ]),
  dict(cat_id="F4", title="F4. ส่งมอบสินค้าจริง",
       subtitle="บรรทัดสินค้าหินยังต้องเดินตามขั้นตอนส่งมอบปกติของโหมดนั้นๆ (ที่นี่คือ Mode 2 Lot) · 1 test case",
       cases=[
    dict(id="TC-E2E-M4-09", scenario="ส่งมอบสินค้า (Delivery) ให้ลูกค้า",
         note="✅ ยืนยันแล้วว่าบั๊กเดิม (ระบบดึงสต็อกจากจุดพัก \"Stone Hold\" ที่โหมด Lot ไม่เคยย้ายของเข้าจริง ทำให้ยอดติดลบเพิ่มขึ้นทุกครั้งที่ส่งของ) ยังคงปิดอยู่จริง: ระบบดึงสต็อกจากจุดที่ของจริงอยู่ (\"Stone Available\") ถูกต้อง — ต้องกรอก Scanned Serial ให้ตรงกับชื่อ Lot ก่อน Validate เสมอ (ตรรกะเดียวกับ Mode 2/3)",
         pre="ทำ TC-E2E-M4-08 เสร็จแล้ว มีใบส่งของอัตโนมัติรออยู่ตั้งแต่ตอน Confirm",
         steps=["เปิด Sale Order &gt; กดปุ่มสถิติ \"Delivery\"", "กด \"Details\" ที่บรรทัดสินค้า กรอกช่อง \"Scanned Serial\" ให้ตรงกับชื่อ Lot แล้ว Save", "กด Validate"],
         sample="Scanned Serial = BLK-26-0004-LOT",
         expected="ใบส่งของเปลี่ยนสถานะเป็น Done ดึงสต็อกจากจุดที่ของจริงอยู่ถูกต้อง — ตัวอย่างจริง: EG01/OUT/00080 (Vietnam Limestone - Slab 0.5 ตร.ม., Source Location \"EG01/Stock\")", prio="High",
         shot="assets/e2e-mode4/tc09-delivery-done.png"),
  ]),
  dict(cat_id="F5", title="F5. ติดตามงานผ่าน Task และ Milestone",
       subtitle="ปิดงานจริง ระบบขึ้น Milestone ให้อัตโนมัติ + ดู Gantt Chart ของทั้งโปรเจกต์ · 2 test cases",
       cases=[
    dict(id="TC-E2E-M4-10", scenario="ทำ Task งานจริงให้เสร็จ (Mark as Done) — Milestone ขึ้นสถานะสำเร็จให้อัตโนมัติ",
         pre="ทำ TC-E2E-M4-09 เสร็จแล้ว มี Task ที่ตั้ง Milestone ไว้ล่วงหน้าตอนสร้าง BOQ (บรรทัด Dry-Lay)",
         steps=["เปิด Task \"Dry-Lay\"", "กดป้ายสถานะมุมขวาบน (เช่น \"In Progress\") เลือก \"Done\""],
         sample="-",
         expected="Task ขึ้นป้ายสถานะ \"Done\" และ Milestone ที่ผูกกับ Task นั้นเปลี่ยนเป็นติ๊กถูกให้อัตโนมัติ โดยไม่ต้องไปกดยืนยัน Milestone แยกต่างหาก — ตัวอย่างจริง: Milestone \"ปูพื้นเสร็จสมบูรณ์ (Dry-Lay Complete)\" ขึ้นเครื่องหมายถูกในหน้า Project Dashboard ทันที", prio="Medium",
         shot="assets/e2e-mode4/tc10-task-done.png"),
    dict(id="TC-E2E-M4-11", scenario="เปิดดู Gantt Chart ของทั้งโปรเจกต์",
         pre="ทำ TC-E2E-M4-05 เสร็จแล้ว (มี Task พร้อมวันที่วางแผนแล้ว)",
         steps=["เปิด Project ของ SO นี้ &gt; กดปุ่มสถิติ \"Tasks\"", "สลับมุมมองด้านขวาบนเป็น \"Gantt\""],
         sample="-",
         expected="เห็นแท่ง Gantt ของแต่ละ Task เรียงตามวันที่วางแผน กลุ่มตามผู้รับผิดชอบ — Task ที่ทำเสร็จแล้ว (Dry-Lay) จะหายไปจากมุมมองนี้เพราะ filter เริ่มต้นกรองเฉพาะงานที่ยังเปิดอยู่ (\"Open\") — ปิด filter นี้ถ้าต้องการเห็นงานที่เสร็จแล้วด้วย", prio="Low",
         shot="assets/e2e-mode4/tc11-gantt.png"),
  ]),
  dict(cat_id="F6", title="F6. ตรวจสอบบัญชี — Project P&amp;L และ Journal Items",
       subtitle="ยืนยันว่ารายได้ที่ผูก Analytic Account ของโปรเจกต์ถูกต้อง และใบแจ้งหนี้แต่ละใบลงบัญชีสมดุล · 2 test cases",
       cases=[
    dict(id="TC-E2E-M4-12", scenario="ตรวจสอบกำไรขาดทุนของโปรเจกต์ (Project P&amp;L) บน Dashboard",
         pre="ทำ TC-E2E-M4-08 เสร็จแล้ว (ออกใบแจ้งหนี้ครบ 3 งวด)",
         steps=["เปิด Project ของ SO นี้", "กดปุ่มสถิติ \"Dashboard\""],
         sample="-",
         expected="เห็นยอดรายได้แยกตามหมวด (Materials / Other Services / Down Payments) รวมกันแล้วต้องเท่ากับยอดใบแจ้งหนี้ทั้งหมด (ไม่รวม VAT) — ตัวอย่างจริง: Other Services 480 + Materials 900 = Total Revenues 1,380 บาท ตรงกับยอด Invoiced 1,380 บาททั้งหมด (ออกครบ 3 งวดแล้ว จึง Expected = Invoiced พอดี ไม่มียอดค้าง \"To Invoice\" — ยอด Materials 900 นี้คือหลักฐานว่าราคาที่ BOQ ตั้งไว้ไม่ถูกเขียนทับแล้ว, ดู TC-03)", prio="Medium",
         shot="assets/e2e-mode4/tc12-dashboard-milestone-pl.png"),
    dict(id="TC-E2E-M4-13", scenario="ตรวจรายการบัญชีของใบแจ้งหนี้แต่ละงวด (Journal Items)",
         pre="ทำ TC-E2E-M4-08 เสร็จแล้ว",
         steps=["เปิดใบแจ้งหนี้งวดใดงวดหนึ่ง &gt; กดแท็บ \"Journal Items\""],
         sample="-",
         expected="เดบิต/เครดิตสมดุลกัน (รวมเท่ากันทั้ง 2 ฝั่ง) เห็น Analytic Distribution ผูกกับบัญชี Analytic ของโปรเจกต์นี้บนบรรทัดรายได้ — ตัวอย่างจริง: INV/2026/00030 เดบิต Trade Receivables 442.98 = เครดิต Down Payment 414.00 + Output VAT 28.98 พอดี พร้อมป้าย Analytic \"BOQ0029 - ทดสอบ Mode4 Fresh...\"", prio="Medium",
         shot="assets/e2e-mode4/tc13-journal-items.png"),
  ]),
]
