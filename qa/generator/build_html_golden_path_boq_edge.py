from qa_data_golden_path_boq_edge import CATEGORIES

def steps_html(steps):
    return '<ol>' + ''.join('<li>%s</li>' % s for s in steps) + '</ol>'

def note_html(note):
    return ('<div class="note">%s</div>' % note) if note else ''

def new_html(new):
    return ('<div class="upd"><b>แก้/เพิ่ม</b> %s</div>' % new) if new else ''

def prio_badge(p):
    cls = {'High': 'prio-high', 'Medium': 'prio-med', 'Low': 'prio-low'}[p]
    return '<span class="prio-badge %s">%s</span>' % (cls, p)

def shot_html(shot, shot2=None):
    if not shot:
        return '-'
    if shot2:
        return _shot_one(shot) + '<div style="height:6px"></div>' + _shot_one(shot2)
    return _shot_one(shot)

def _shot_one(shot):
    return '<a class="tc-shot-link" href="%s" target="_blank" title="เปิดภาพหน้าจอจริงขนาดเต็ม"><img src="%s" loading="lazy"></a>' % (shot, shot)

sidebar_items = []
for c in CATEGORIES:
    tag = c['cat_id']
    label = c['title'].split('. ', 1)[1]
    sidebar_items.append('<li class="tree-doc"><a href="#%s"><span class="tree-doc-tag">%s</span>%s</a></li>' % (tag, tag, label))

real_cases = [tc for c in CATEGORIES for tc in c['cases'] if not tc['id'].endswith('N/A')]
total = len(real_cases)
prios = {'High': 0, 'Medium': 0, 'Low': 0}
for tc in real_cases:
    prios[tc['prio']] += 1

category_blocks = []
for c in CATEGORIES:
    rows = []
    for tc in c['cases']:
        rows.append(f'''        <tr>
          <td class="col-id"><span class="tc-id">{tc['id']}</span></td>
          <td class="col-scenario">{tc['scenario']}{new_html(tc.get('new'))}{note_html(tc.get('note'))}</td>
          <td class="col-pre">{tc['pre']}</td>
          <td class="col-steps">{steps_html(tc['steps'])}</td>
          <td class="col-sample">{tc['sample']}</td>
          <td class="col-expected">{tc['expected']}</td>
          <td class="col-prio">{prio_badge(tc['prio'])}</td>
          <td class="col-shot">{shot_html(tc.get('shot'), tc.get('shot2'))}</td>
        </tr>''')
    rows_joined = '\n'.join(rows)
    category_blocks.append(f'''  <div class="category" id="{c['cat_id']}">
    <div class="category-header">
      <div>
        <div class="category-title">{c['title']}</div>
        <div class="category-sub">{c['subtitle']}</div>
      </div>
    </div>
    <div class="table-scroll">
    <table class="tc-table">
      <thead>
        <tr>
          <th class="col-id">TC ID</th>
          <th class="col-scenario">Scenario</th>
          <th class="col-pre">Precondition</th>
          <th class="col-steps">Steps</th>
          <th class="col-sample">ข้อมูลตัวอย่าง</th>
          <th class="col-expected">Expected Result</th>
          <th class="col-prio">Priority</th>
          <th class="col-shot">ภาพหน้าจอ</th>
        </tr>
      </thead>
      <tbody>
{rows_joined}
      </tbody>
    </table>
    </div>
  </div>''')

PAGE = '''<!doctype html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EMG-O — Golden Path: BOQ Cut List หลังขาย</title>
<style>
  :root{
    --copper:#B8763E;
    --copper-dark:#8F5A2C;
    --charcoal:#2B2E31;
    --text:#3A3D40;
    --bg:#F3F1EE;
    --card:#FFFFFF;
    --border:#E4DFD8;
    --red:#B8432E;
    --red-bg:#FBEAE7;
    --amber:#B8892E;
    --amber-bg:#FBF2E2;
    --green:#2E7D4F;
    --green-bg:#E9F5EE;
  }
  *{box-sizing:border-box;}
  html,body{margin:0;padding:0;background:var(--bg);font-family:Calibri,Arial,sans-serif;color:var(--text);}
  a{color:inherit;}

  #home-btn{position:fixed;top:16px;left:16px;z-index:50;width:38px;height:38px;border-radius:50%;
    background:var(--charcoal);color:#fff;display:flex;align-items:center;justify-content:center;
    text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.25);transition:background .15s ease;}
  #home-btn:hover{background:var(--copper);}

  #export-btn{position:fixed;top:16px;right:16px;z-index:50;display:flex;align-items:center;gap:7px;
    padding:9px 16px 9px 14px;border-radius:99px;background:var(--green);color:#fff;font-size:13px;font-weight:700;
    text-decoration:none;box-shadow:0 4px 14px rgba(0,0,0,.25);transition:background .15s ease;}
  #export-btn:hover{background:#255F3F;}

  .layout{max-width:1440px;margin:0 auto;padding:76px 24px 100px;display:flex;align-items:flex-start;gap:40px;}
  .sidebar{width:272px;flex-shrink:0;position:sticky;top:24px;max-height:calc(100vh - 48px);overflow-y:auto;}
  .sidebar-title{font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#9A9D9F;font-weight:700;margin-bottom:12px;padding-left:6px;}

  .tree-docs{list-style:none;margin:0;padding:0;}
  .tree-doc > a{display:block;font-size:12.5px;color:#6B6E70;text-decoration:none;padding:5px 8px;border-radius:5px;line-height:1.4;}
  .tree-doc > a:hover{color:var(--charcoal);background:rgba(0,0,0,.04);}
  .tree-doc-tag{display:inline-block;min-width:24px;color:var(--copper-dark);font-weight:700;font-size:11px;margin-right:2px;}

  .main{flex:1;min-width:0;}
  header{margin-bottom:32px;}
  .eyebrow{font-size:14px;letter-spacing:2px;text-transform:uppercase;color:var(--copper);font-weight:700;margin-bottom:10px;}
  h1{font-size:30px;margin:0 0 10px 0;color:var(--charcoal);font-weight:700;font-family:Cambria,serif;}
  .doc-date{font-size:13px;color:#8F5A2C;font-weight:700;margin:-2px 0 12px;}
  .sub{font-size:15px;color:#6B6E70;line-height:1.6;max-width:760px;margin-bottom:20px;}

  .stat-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px;}
  .stat-pill{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:10px 16px;font-size:13px;}
  .stat-pill b{font-size:17px;display:block;color:var(--charcoal);font-family:Cambria,serif;}

  .flow-banner{background:var(--charcoal);border-radius:14px;padding:18px 22px;margin:24px 0 36px;color:#fff;font-size:13.5px;line-height:1.7;}
  .flow-banner b{color:var(--copper);}

  .category{margin-bottom:52px;}
  .category-header{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:18px;padding-bottom:12px;border-bottom:2px solid var(--charcoal);}
  .category-title{font-size:21px;font-weight:700;font-family:Cambria,serif;color:var(--charcoal);}
  .category-sub{font-size:13px;color:#9A9D9F;margin-top:2px;}

  .table-scroll{overflow-x:auto;border-radius:14px;border:1px solid var(--border);background:var(--card);}
  table.tc-table{border-collapse:collapse;width:100%;min-width:1340px;font-size:13px;}
  table.tc-table thead th{background:var(--charcoal);color:#fff;text-align:left;padding:10px 12px;font-size:12px;letter-spacing:.3px;position:sticky;top:0;}
  table.tc-table tbody td{padding:12px;border-bottom:1px solid var(--border);vertical-align:top;line-height:1.5;}
  table.tc-table tbody tr:nth-child(even){background:#FAF9F7;}
  table.tc-table tbody tr:hover{background:#F5EFE6;}
  .col-id{width:76px;}
  .col-scenario{width:280px;font-weight:600;color:var(--charcoal);}
  .col-pre{width:150px;color:#6B6E70;}
  .col-steps{width:230px;}
  .col-steps ol{margin:0;padding-left:18px;}
  .col-steps li{margin-bottom:3px;}
  .col-sample{width:210px;color:#5B4632;background:#FBF8F3;}
  .col-expected{width:250px;}
  .col-prio{width:78px;text-align:center;}
  .col-shot{width:92px;text-align:center;}
  .tc-shot-link{display:inline-block;}
  .tc-shot-link img{width:76px;border-radius:6px;border:1px solid var(--border);display:block;transition:transform .15s ease,box-shadow .15s ease;}
  .tc-shot-link:hover img{transform:scale(1.6);position:relative;z-index:5;box-shadow:0 8px 24px rgba(0,0,0,.3);}
  .tc-id{font-family:Consolas,Menlo,monospace;font-size:11.5px;color:var(--copper-dark);font-weight:700;}
  .note{margin-top:6px;font-size:11.5px;color:var(--amber);background:var(--amber-bg);border-radius:6px;padding:4px 8px;}
  .upd{margin-top:6px;font-size:11.5px;color:var(--green);background:var(--green-bg);border:1px solid #BFE0CD;border-radius:6px;padding:4px 8px;}
  .upd b{background:var(--green);color:#fff;border-radius:99px;padding:1px 8px;margin-right:4px;font-size:10.5px;}
  .changes{background:var(--green-bg);border:1px solid #BFE0CD;border-radius:14px;padding:16px 22px;margin:0 0 28px;font-size:13.5px;line-height:1.7;color:var(--charcoal);}
  .changes h3{margin:0 0 6px;font-size:15px;color:var(--green);}
  .changes ul{margin:4px 0 0;padding-left:20px;}
  .prio-badge{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.3px;padding:3px 10px;border-radius:99px;}
  .prio-high{background:var(--red-bg);color:var(--red);}
  .prio-med{background:var(--amber-bg);color:var(--amber);}
  .prio-low{background:var(--green-bg);color:var(--green);}

  footer{margin-top:56px;font-size:13px;color:#9A9D9F;}

  @media (max-width:900px){
    .layout{flex-direction:column;padding:64px 16px 80px;gap:20px;}
    .sidebar{position:static;width:100%;top:auto;max-height:none;overflow-y:visible;}
  }
</style>
</head>
<body>

<a id="home-btn" href="../library.html" title="กลับไปหน้า Portal" aria-label="กลับไปหน้า Portal"><svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 11.5 12 4l9 7.5"/><path d="M5.5 10v9.5h13V10"/></svg></a>
<a id="export-btn" href="../client-docs/test-cases/emg-o-golden-path-boq-edge.xlsx" download="EMG-O Test Cases - BOQ กรณีพิเศษและเคสผิดพลาด.xlsx" title="ดาวน์โหลดไฟล์ Excel"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M4.5 19.5h15"/></svg>Export Excel</a>

<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-title">ขั้นตอนในเรื่องราวนี้</div>
    <ul class="tree-docs" id="doc-tree">__SIDEBAR__</ul>
  </aside>
  <div class="main">
  <header>
    <div class="eyebrow">Empire Stone × Empire Granite — QA</div>
    <h1>ชุดทดสอบ BOQ — กรณีพิเศษและเคสผิดพลาด</h1>
    <div class="doc-date">อัปเดตล่าสุด: 3 พฤศจิกายน 2569 (2026-11-03) · รันจริงบน eg-tst ผ่านหน้าจอ ใช้ผู้ใช้ emgdemo บริษัท Empire Granite</div>
    <div class="sub">เคสที่ Golden Path ทั้ง 5 เส้นทางไม่ได้ทดสอบ (เพราะเดินเฉพาะทางที่ถูก): ไฟล์นำเข้าผิด · Cut List ผิด · เศษหินหลังตัด · ส่งและวางบิลบางส่วน · ลูกค้าคืนของ · ทุกเคสเดินจริงและตัวเลขมาจากระบบ</div>
    <div style="background:#FFF4DC;border:1px solid #E5B84B;border-left:6px solid #E5B84B;border-radius:12px;padding:14px 20px;margin:16px 0;font-size:13.5px;line-height:1.7;">
      <b>ประเด็นที่ต้องการการยืนยัน</b> (ผู้จัดทำตัดสินใจแทนไปก่อน โปรดยืนยันหรือแจ้งให้ปรับ)
      <ol style="margin:6px 0 0 18px;padding:0;"><li><b>ค่าบริหารโครงการเรียกเก็บเต็มจำนวนในใบแจ้งหนี้ใบแรกของการส่งบางส่วน</b> — ใบแรก 46,699.20 = หิน 40,608.00 (ที่ส่งแล้ว) + ค่าบริหารโครงการ 6,091.20 ทั้งก้อน ใบที่สองมีแต่หิน <b>แก้แล้วในโมดูล BOQ 1.54.4</b> ให้เรียกเก็บตามสัดส่วนมูลค่าที่ส่ง (ตรวจซ้ำแล้วใน TC-EX2-09 ชุดที่ 2) ผลในเคสนี้เป็นของก่อนแก้</li><li><b>FG หนึ่ง lot ส่งแบ่งเป็นชิ้นเต็มได้</b> — แก้แล้ว (โมดูล 109.69) ตามที่ลูกค้าแจ้งว่าของจริงแบ่งส่งได้ ต้องเป็นจำนวนเต็มของชิ้น เช่น 3 ชิ้น = 2.16 ตร.ม. ตรวจซ้ำใน TC-EX-10 ขอให้ลูกค้ายืนยันว่าแบ่งเป็นชิ้นถูกต้อง (หินแผ่นเดียวยังส่งทั้งแผ่น)</li><li><b>ใบคืนของ FG เข้า EG01/Stock ตรง ไม่ผ่านการตรวจ</b> — Slab คืนต้องผ่าน Returned - Inspect แต่ FG คืนเข้าสต็อกขายได้ทันที ขอยืนยันว่าไม่ต้องการให้ตรวจสภาพก่อน</li><li><b>การคืนของไม่ออก Credit Note ให้เอง</b> — ต้องกด Credit Note ที่ใบแจ้งหนี้แยก (TC-EX-16) ขอยืนยันว่ารับได้</li><li><b>ต้นทุนเศษคิดตามพื้นที่</b> — 1.50 ตร.ม. จาก 8.70 ตร.ม. ได้ 1,405.02 จากต้นทุน Slab 8,149.12 ไม่ได้ถ่วงตามรูปร่างหรือความเสียหาย</li></ol>
    </div>
    <div class="stat-row">
      <div class="stat-pill"><b>__TOTAL__</b>Test Case ทั้งหมด</div>
      <div class="stat-pill"><b>__NCAT__</b>หมวด</div>
      <div class="stat-pill"><b style="color:var(--red)">__NHIGH__</b>High Priority</div>
      <div class="stat-pill"><b style="color:var(--amber)">__NMED__</b>Medium Priority</div>
      <div class="stat-pill"><b style="color:var(--green)">__NLOW__</b>Low Priority</div>
    </div>
  </header>

  <div class="changes">
    <h3>ชุดนี้ใช้คู่กับ Golden Path เส้นทางที่ 1–5</h3>
    <ul>
      <li>ใช้ตรวจเรื่องที่เส้นทางหลักข้ามไป · เส้นทางหลักดู <a href="guide-boq-excel-2026-11-03.html">เส้นทาง 1</a> · <a href="guide-boq-cutlist-2026-11-03.html">เส้นทาง 2</a> · <a href="guide-boq-manual-2026-11-03.html">เส้นทาง 3</a> · <a href="guide-boq-project-2026-11-03.html">เส้นทาง 4</a> · <a href="guide-boq-lamps-2026-11-03.html">เส้นทาง 5</a></li>
      <li>ไฟล์ตัวอย่างที่ผิดโดยตั้งใจอยู่ในหน้า <a href="../test-boq.html">ไฟล์ทดสอบ BOQ</a> (4 ไฟล์) · ต้องผ่าน <a href="guide-setup-2026-11-01.html">Setup ระบบ</a> มาก่อน และมี Slab ZZ2 GUIDE MARBLE ที่ Available อย่างน้อย 5 แผ่น</li>
      <li>ขอบเขต 16 เคส: นำเข้า BOQ ผิด 3 · Cut List ผิด 2 · เศษหิน 4 · ส่งและวางบิลบางส่วน 5 · ลูกค้าคืนของ 2</li>
    </ul>
  </div>

  <div class="flow-banner">
    <b>ข้อมูลที่รันจริง (eg-tst, 3 พ.ย. 2569) ใช้ 2 ชุด:</b><br>
    <b>ชุด A:</b> boq-import-zz2-reception.xlsx &rarr; BOQ1228 &rarr; ใบเสนอราคา S01806 &rarr; ใบสั่งผลิต EG01/STFG/00491 (เศษ OC-EG01/STFG/00491-01) &rarr; ใบส่งของ EG01/OUT/00775 &rarr; ใบแจ้งหนี้ INV/2026/00020 &rarr; ใบรับคืน EG01/IN/00748 &rarr; Credit Note RINV/2026/00001<br>
    <b>ชุด B:</b> boq-import-zz2-meeting.xlsx &rarr; BOQ1231 &rarr; ใบเสนอราคา S01809 (67,003.20 ก่อน VAT) &rarr; ใบสั่งผลิต EG01/STFG/00492 และ 00493 &rarr; ส่งบางส่วน EG01/OUT/00776 + ใบค้างส่ง 00777 &rarr; ใบแจ้งหนี้ INV/2026/00021 (46,699.20) และ INV/2026/00022 (20,304.00)<br>
    <b>ตัวเลขหลัก:</b> เศษ 1.50 ตร.ม. ต้นทุน 1,405.02 · ต้นทุน Slab ลงบัญชีใน FG 6,744.10 (แทน 8,149.12) · Credit Note 49,245.68 รวม VAT ตรงใบเดิม · สองใบแจ้งหนี้รวม 67,003.20 ก่อน VAT<br>
    <b>ผลข้างเคียงที่ควรรู้:</b> ระหว่างเปิดรายการ Slabs Pending Inspection ผู้จัดทำกดตรวจเศษเก่า OC-EG01/STFG/00418-01 (ค้างตั้งแต่ 31 ต.ค.) ให้กลับไป Available โดยไม่ตั้งใจ ไม่กระทบเอกสารชุดนี้<br>
    <b>เรื่องที่ชุดนี้ไม่ครอบคลุมอยู่ใน <a href="test-cases-golden-path-boq-edge2.html" style="color:#FFBD59;">ชุดกรณีพิเศษ ชุดที่ 2</a>:</b> Cut List ก่อนออกใบเสนอราคา · นำเข้า Cut List ซ้ำ · คืนของบางส่วน · ตัดเศษทิ้ง · คืนของหลังจ่ายเงินแล้ว · ส่งโคมซีเรียลทีละใบ · ยกเลิกงานขาย Project<br>
    <b>คำถามค้างลูกค้า/บัญชี:</b> FG คืนต้องตรวจสภาพก่อนเข้าสต็อกขายหรือไม่ · ต้องการให้ระบบออก Credit Note อัตโนมัติจากใบรับคืนหรือไม่
  </div>

__CATEGORY_BLOCKS__

  <footer>Empire Stone Internal System — จัดทำโดยทีมงาน · <a href="../library.html">กลับหน้าคลังเอกสาร</a></footer>
  </div>
</div>

</body>
</html>
'''

PAGE = (PAGE
    .replace('__SIDEBAR__', ''.join(sidebar_items))
    .replace('__TOTAL__', str(total))
    .replace('__NCAT__', str(len(CATEGORIES)))
    .replace('__NHIGH__', str(prios['High']))
    .replace('__NMED__', str(prios['Medium']))
    .replace('__NLOW__', str(prios['Low']))
    .replace('__CATEGORY_BLOCKS__', '\n'.join(category_blocks))
)

if __name__ == '__main__':
    with open('../test-cases-golden-path-boq-edge.html', 'w', encoding='utf-8') as f:
        f.write(PAGE)
    print('wrote', len(PAGE), 'bytes')
