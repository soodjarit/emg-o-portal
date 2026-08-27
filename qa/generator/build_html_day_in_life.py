import html as _html
from qa_data_day_in_life import CATEGORIES

def esc_attr(s):
    return _html.escape(s, quote=True)

def steps_html(steps):
    return '<ol>' + ''.join('<li>%s</li>' % s for s in steps) + '</ol>'

def note_html(note):
    return ('<div class="note">%s</div>' % note) if note else ''

def prio_badge(p):
    cls = {'High': 'prio-high', 'Medium': 'prio-med', 'Low': 'prio-low'}[p]
    return '<span class="prio-badge %s">%s</span>' % (cls, p)

GROUP_A = {'D1', 'D2', 'D3', 'D4'}
GROUP_B = {'D5', 'D6', 'D7'}

sidebar_a = []
sidebar_b = []
sidebar_c = []
for c in CATEGORIES:
    tag = c['cat_id']
    label = c['title'].split('. ', 1)[1]
    item = '<li class="tree-doc"><a href="#%s"><span class="tree-doc-tag">%s</span>%s</a></li>' % (tag, tag, label)
    if tag in GROUP_A:
        sidebar_a.append(item)
    elif tag in GROUP_B:
        sidebar_b.append(item)
    else:
        sidebar_c.append(item)

total = sum(len(c['cases']) for c in CATEGORIES)
prios = {'High': 0, 'Medium': 0, 'Low': 0}
for c in CATEGORIES:
    for tc in c['cases']:
        prios[tc['prio']] += 1

category_blocks = []
for c in CATEGORIES:
    rows = []
    for tc in c['cases']:
        rows.append(f'''        <tr>
          <td class="col-id"><span class="tc-id">{tc['id']}</span></td>
          <td class="col-scenario">{tc['scenario']}{note_html(tc.get('note'))}</td>
          <td class="col-pre">{tc['pre']}</td>
          <td class="col-steps">{steps_html(tc['steps'])}</td>
          <td class="col-sample">{tc['sample']}</td>
          <td class="col-expected">{tc['expected']}</td>
          <td class="col-prio">{prio_badge(tc['prio'])}</td>
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
<title>EMG-O — Test Cases: Day-in-the-Life (Order-to-Cash)</title>
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

  .layout{max-width:1440px;margin:0 auto;padding:76px 24px 100px;display:flex;align-items:flex-start;gap:40px;}
  .sidebar{width:272px;flex-shrink:0;position:sticky;top:24px;max-height:calc(100vh - 48px);overflow-y:auto;}
  .sidebar-title{font-size:11px;letter-spacing:1.5px;text-transform:uppercase;color:#9A9D9F;font-weight:700;margin-bottom:12px;padding-left:6px;}

  .tree, .tree-docs{list-style:none;margin:0;padding:0;}
  .tree-cat{margin-bottom:2px;border-radius:6px;}
  .tree-cat > summary{cursor:pointer;font-size:13px;font-weight:700;color:var(--charcoal);padding:7px 8px;border-radius:6px;list-style:none;display:flex;align-items:center;gap:7px;user-select:none;}
  .tree-cat > summary::-webkit-details-marker{display:none;}
  .tree-cat > summary::before{content:'▸';color:var(--copper);font-size:10px;flex-shrink:0;transition:transform .15s ease;}
  .tree-cat[open] > summary::before{transform:rotate(90deg);}
  .tree-cat > summary:hover{background:rgba(0,0,0,.04);}
  .tree-cat.current-section > summary{color:var(--copper-dark);}
  .tree-docs{margin:2px 0 10px 17px;padding-left:12px;border-left:2px solid var(--border);}
  .tree-doc > a{display:block;font-size:12.5px;color:#6B6E70;text-decoration:none;padding:5px 8px;border-radius:5px;line-height:1.4;}
  .tree-doc > a:hover{color:var(--charcoal);background:rgba(0,0,0,.04);}
  .tree-doc-tag{display:inline-block;min-width:24px;color:var(--copper-dark);font-weight:700;font-size:11px;margin-right:2px;}

  .main{flex:1;min-width:0;}
  header{margin-bottom:32px;}
  .eyebrow{font-size:14px;letter-spacing:2px;text-transform:uppercase;color:var(--copper);font-weight:700;margin-bottom:10px;}
  h1{font-size:30px;margin:0 0 10px 0;color:var(--charcoal);font-weight:700;font-family:Cambria,serif;}
  .sub{font-size:15px;color:#6B6E70;line-height:1.6;max-width:760px;margin-bottom:20px;}

  .stat-row{display:flex;gap:12px;flex-wrap:wrap;margin-bottom:8px;}
  .stat-pill{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:10px 16px;font-size:13px;}
  .stat-pill b{font-size:17px;display:block;color:var(--charcoal);font-family:Cambria,serif;}

  .download-bar{display:flex;align-items:center;gap:14px;background:var(--charcoal);border-radius:14px;padding:18px 22px;margin:24px 0 36px;flex-wrap:wrap;}
  .download-bar .dl-text{flex:1;min-width:200px;}
  .download-bar .dl-title{color:#fff;font-weight:700;font-size:15px;margin-bottom:2px;}
  .download-bar .dl-desc{color:#B8BCBE;font-size:13px;}
  .dl-btn{display:inline-flex;align-items:center;gap:8px;background:var(--copper);color:#fff;text-decoration:none;
    font-weight:700;font-size:14px;padding:11px 20px;border-radius:10px;white-space:nowrap;transition:background .15s ease;}
  .dl-btn:hover{background:var(--copper-dark);}

  .category{margin-bottom:52px;}
  .category-header{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;margin-bottom:18px;padding-bottom:12px;border-bottom:2px solid var(--charcoal);}
  .category-title{font-size:21px;font-weight:700;font-family:Cambria,serif;color:var(--charcoal);}
  .category-sub{font-size:13px;color:#9A9D9F;margin-top:2px;}

  .table-scroll{overflow-x:auto;border-radius:14px;border:1px solid var(--border);background:var(--card);}
  table.tc-table{border-collapse:collapse;width:100%;min-width:1160px;font-size:13px;}
  table.tc-table thead th{background:var(--charcoal);color:#fff;text-align:left;padding:10px 12px;font-size:12px;letter-spacing:.3px;position:sticky;top:0;}
  table.tc-table tbody td{padding:12px;border-bottom:1px solid var(--border);vertical-align:top;line-height:1.5;}
  table.tc-table tbody tr:nth-child(even){background:#FAF9F7;}
  table.tc-table tbody tr:hover{background:#F5EFE6;}
  .col-id{width:76px;}
  .col-scenario{width:180px;font-weight:600;color:var(--charcoal);}
  .col-pre{width:160px;color:#6B6E70;}
  .col-steps{width:230px;}
  .col-steps ol{margin:0;padding-left:18px;}
  .col-steps li{margin-bottom:3px;}
  .col-sample{width:220px;color:#5B4632;background:#FBF8F3;}
  .col-expected{width:220px;}
  .col-prio{width:78px;text-align:center;}
  .tc-id{font-family:Consolas,Menlo,monospace;font-size:12px;color:var(--copper-dark);font-weight:700;}
  .note{margin-top:6px;font-size:11.5px;color:var(--amber);background:var(--amber-bg);border-radius:6px;padding:4px 8px;}
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

<div class="layout">
  <aside class="sidebar">
    <div class="sidebar-title">หมวด Test Case</div>
    <ul class="tree" id="doc-tree">
      <details class="tree-cat" data-section="group-A" open>
        <summary>ตั้งค่า → เสนอราคา → มัดจำ</summary>
        <ul class="tree-docs">__SIDEBAR_A__</ul>
      </details>
      <details class="tree-cat" data-section="group-B" open>
        <summary>การผลิต → ค่าใช้จ่าย</summary>
        <ul class="tree-docs">__SIDEBAR_B__</ul>
      </details>
      <details class="tree-cat" data-section="group-C" open>
        <summary>ปิดงาน → ดูกำไร</summary>
        <ul class="tree-docs">__SIDEBAR_C__</ul>
      </details>
    </ul>
  </aside>
  <div class="main">
  <header>
    <div class="eyebrow">Empire Stone × Empire Granite — QA</div>
    <h1>Test Cases: Day-in-the-Life (Order-to-Cash)</h1>
    <div class="sub">Test Case ที่แยกหมวดตามเอกสาร "Day-in-the-Life" (งานโครงการ Mode 4 หนึ่งงาน ตั้งแต่ตั้งค่าสินค้าจนเห็นกำไรจริง) — เดินตามลำดับ flow จริงทุกจุดในเอกสารครบทุกสไลด์ในเธรดเดียว รวมถึงจุดที่เคยมี Test Case อยู่แล้วในหมวดอื่น (Material Setup/BOQ→Project/Cut Order) ก็ทดสอบซ้ำอีกครั้งที่นี่ (ระบุ "regression ของ..." ในหมายเหตุ) เพื่อจับ regression จากการแก้โค้ดล่าสุด ไม่ใช่แค่จุดที่ยังไม่เคยทดสอบ พร้อมข้อมูลตัวอย่างที่ต้องกรอกในแต่ละขั้นตอน</div>
    <div class="stat-row">
      <div class="stat-pill"><b>__TOTAL__</b>Test Case ทั้งหมด</div>
      <div class="stat-pill"><b>__NCAT__</b>หมวด</div>
      <div class="stat-pill"><b style="color:var(--red)">__NHIGH__</b>High Priority</div>
      <div class="stat-pill"><b style="color:var(--amber)">__NMED__</b>Medium Priority</div>
      <div class="stat-pill"><b style="color:var(--green)">__NLOW__</b>Low Priority</div>
    </div>
  </header>

  <div class="download-bar">
    <div class="dl-text">
      <div class="dl-title">ดาวน์โหลดเป็น Excel</div>
      <div class="dl-desc">ไฟล์ .xlsx แยกชีทตามหมวด พร้อมคอลัมน์ Actual Result / Status / Tester / Date สำหรับกรอกระหว่างทดสอบจริง</div>
    </div>
    <a class="dl-btn" href="../client-docs/test-cases/emg-o-test-cases-day-in-life.xlsx" download>⬇ ดาวน์โหลด .xlsx</a>
  </div>

__CATEGORY_BLOCKS__

  <footer>Empire Stone Internal System — จัดทำโดยทีมงาน · <a href="../library.html">กลับหน้าคลังเอกสาร</a></footer>
  </div>
</div>

<script>
  (function(){
    var catEls = Array.prototype.slice.call(document.querySelectorAll('#doc-tree .tree-cat'));
    catEls.forEach(function(c){
      var links = c.querySelectorAll('a[href^="#"]');
      links.forEach(function(a){
        var id = a.getAttribute('href').slice(1);
        var target = document.getElementById(id);
        if(!target) return;
      });
    });
    var sectionEls = Array.prototype.slice.call(document.querySelectorAll('.category'));
    if(!sectionEls.length) return;
    function setActive(id){
      document.querySelectorAll('.tree-doc a').forEach(function(a){
        a.style.fontWeight = (a.getAttribute('href') === '#' + id) ? '700' : '400';
        a.style.color = (a.getAttribute('href') === '#' + id) ? 'var(--copper-dark)' : '';
      });
    }
    var observer = new IntersectionObserver(function(entries){
      var visible = entries.filter(function(e){ return e.isIntersecting; });
      if(visible.length) setActive(visible[0].target.id);
    }, { rootMargin: '-15% 0px -70% 0px', threshold: 0 });
    sectionEls.forEach(function(s){ observer.observe(s); });
  })();
</script>
</body>
</html>
'''

PAGE = (PAGE
    .replace('__SIDEBAR_A__', ''.join(sidebar_a))
    .replace('__SIDEBAR_B__', ''.join(sidebar_b))
    .replace('__SIDEBAR_C__', ''.join(sidebar_c))
    .replace('__TOTAL__', str(total))
    .replace('__NCAT__', str(len(CATEGORIES)))
    .replace('__NHIGH__', str(prios['High']))
    .replace('__NMED__', str(prios['Medium']))
    .replace('__NLOW__', str(prios['Low']))
    .replace('__CATEGORY_BLOCKS__', '\n'.join(category_blocks))
)

if __name__ == '__main__':
    with open('test-cases-day-in-life.html', 'w', encoding='utf-8') as f:
        f.write(PAGE)
    print('wrote', len(PAGE), 'bytes')
