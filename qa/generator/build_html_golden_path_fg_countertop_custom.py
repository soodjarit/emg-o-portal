from qa_data_golden_path_fg_countertop_custom import CATEGORIES

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
<title>EMG-O — Golden Path: FG Countertop และ Custom FG</title>
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
<a id="export-btn" href="../client-docs/test-cases/emg-o-golden-path-fg-countertop-custom.xlsx" download="EMG-O Golden Path - FG Countertop และ Custom FG.xlsx" title="ดาวน์โหลดไฟล์ Excel"><svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12"/><path d="M7 10l5 5 5-5"/><path d="M4.5 19.5h15"/></svg>Export Excel</a>

<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-title">ขั้นตอนในเรื่องราวนี้</div>
    <ul class="tree-docs" id="doc-tree">__SIDEBAR__</ul>
  </aside>
  <div class="main">
  <header>
    <div class="eyebrow">Empire Stone × Empire Granite — QA</div>
    <h1>Golden Path — FG: Countertop และ Custom FG (เจดีย์บัว) ขายถึงเก็บเงิน</h1>
    <div class="doc-date">อัปเดตล่าสุด: 14 ตุลาคม 2569 (2026-10-14) · ระบบ stone_slab_inventory เวอร์ชัน 19.0.2.109.24 · รันใหม่ทั้งชุดบน eg-tst</div>
    <div class="sub">สองเส้นทางของสินค้า FG เดินครบวงจรหนึ่งครั้ง: <b>A Countertop</b> ขายเป็น ตร.ม. ใส่ชิ้นงานและงานขอบ/เจาะในใบขาย ระบบเลือก Slab ให้ ตัด ส่งของ เก็บเงิน &rarr; <b>B/C Custom FG เจดีย์บัว</b> ขายเป็นชิ้น เตรียมสูตรจาก BOQ (นำเข้า Cut List) ตัดหินทีละชนิด ประกอบ ส่งของ เก็บเงิน · รันใหม่ทั้งชุดบน eg-tst เมื่อ 14 ต.ค. 2569 (ต่อจากรอบ 11 ต.ค. ที่ผู้ใช้เดินเอง) · ชุดเก่า (6 ต.ค.) ยังเก็บไว้ เพราะหน้าจอและชื่อปุ่มเปลี่ยนไปแล้ว</div>
    <div class="stat-row">
      <div class="stat-pill"><b>__TOTAL__</b>Test Case ทั้งหมด</div>
      <div class="stat-pill"><b>__NCAT__</b>หมวด</div>
      <div class="stat-pill"><b style="color:var(--red)">__NHIGH__</b>High Priority</div>
      <div class="stat-pill"><b style="color:var(--amber)">__NMED__</b>Medium Priority</div>
      <div class="stat-pill"><b style="color:var(--green)">__NLOW__</b>Low Priority</div>
    </div>
  </header>

  <div class="changes">
    <h3>จุดที่ยืนยัน/แก้ในรอบนี้ (ป้ายเขียว "แก้/เพิ่ม" ในแต่ละเคส)</h3>
    <ul>
      <li><b>รันซ้ำทั้งสองเส้นทางบน v109.24 ตัวเลขเงินทุกจุดเท่าเดิม</b> ต้นทุน FG 2,430.00 / WIP 2,899.80 + 1,215.00 / FG เจดีย์บัว 4,506.30 / ค่าแรง 70,493.70</li>
      <li><b>การแก้ 3 จุดเมื่อ 11 ต.ค. ถูก commit และ deploy แล้ว</b> (ตัดแถว BoM ค้าง, ใบส่งของจอง Lot ของตัวเอง, ปุ่มคัดลอกแผนเป็นขนาดจริง) และผ่านการรันซ้ำ — TC-GP-FGS-05, 07, 13, 15</li>
      <li><b>ปริมาณบนใบแจ้งหนี้แสดง 3 ตำแหน่ง</b> (3.480 ตร.ม.) จากรอบ Block — TC-GP-FGS-08, 17</li>
      <li>ขั้นนำเข้า Cut List (TC-GP-FGS-09) ไม่ได้ถ่ายใหม่ เพราะหน้าจอไม่เปลี่ยน ยังใช้ภาพ 11 ต.ค.</li>
    </ul>
  </div>

  <div class="flow-banner">
    <b>เส้นทางที่รันจริง (eg-tst, 14 ต.ค. 2569, v109.24):</b><br>
    <b>A</b> S00626 (GP Block Marble 3.48 ตร.ม. + ขอบ + เจาะ = 48,920.40) &rarr; ใบสั่งผลิต EG01/STFG/00156 (Slab BLK-26-0006-34, -35) &rarr; FG 3 Lot &rarr; ส่งของ EG01/OUT/00333 &rarr; INV/2026/00032<br>
    <b>B/C</b> BOQ0024 (นำเข้าจาก Cut List 14 แถว ต้นทุน 3,906.92/ชิ้น) &rarr; S00627 (เจดีย์บัว 3 ชิ้น 160,500) &rarr; งานประกอบ EG01/STFG/00157 + ใบตัดหิน EG01/STCPL/00115 (NERO) และ 00116 (GP) &rarr; ส่งของ EG01/OUT/00334 (Serial CB-00031 ถึง -33) &rarr; INV/2026/00033 &rarr; ค่าแรง MISC/2026/10/0034<br><br>
    <b>ข้อสังเกต:</b> (1) เส้นทาง A รอบนี้ไม่พบแถวแดงใน Components และใบส่งของจองเฉพาะ Lot ของตัวเอง — ดู TC-GP-FGS-05, 07 (2) ต้นทุนที่ลงบัญชีของ Custom FG ถูกกติกาต้นทุนขั้นต่ำ 50% ครอบ ไม่ตรงกับประมาณการ BOQ — ดู TC-GP-FGS-18 (ควรถามลูกค้า)<br>
    <b>ยังไม่ครอบคลุมใน Golden Path นี้:</b> การบันทึกเศษที่เหลือ (ใบสั่งผลิต A และใบตัดหิน) · ตรวจเศษแล้วนำกลับไปขาย · Unbuild · สินค้า Custom Product 01 · การแก้ขนาดชิ้นหลัง Confirm · กรณีผิดพลาด (ตามหลัก Golden Path ไม่รวมเคสดักข้อผิดพลาด)
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
    with open('../test-cases-golden-path-fg-countertop-custom.html', 'w', encoding='utf-8') as f:
        f.write(PAGE)
    print('wrote', len(PAGE), 'bytes')
