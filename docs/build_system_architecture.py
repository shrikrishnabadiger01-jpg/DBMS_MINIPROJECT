"""Create editable draw.io architecture and a matching standalone SVG."""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as E

P = Path(__file__).parent
W, H = 1200, 1560
mx = E.Element('mxfile', host='app.diagrams.net', type='device')
d = E.SubElement(mx, 'diagram', id='system-architecture', name='System Architecture')
m = E.SubElement(d, 'mxGraphModel', grid='0', page='1', pageScale='1', pageWidth=str(W), pageHeight=str(H), background='#FFFFFF')
r = E.SubElement(m, 'root')
E.SubElement(r, 'mxCell', id='0'); E.SubElement(r, 'mxCell', id='1', parent='0')
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0 L8 4 L0 8 Z" fill="#555"/></marker></defs>', '<rect width="100%" height="100%" fill="white"/>', '<g font-family="Arial, sans-serif" fill="#111">']
boxes = {}

def cell(id, value, style, x, y, w, h):
    c = E.SubElement(r, 'mxCell', id=id, value=value, style=style, vertex='1', parent='1')
    E.SubElement(c, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as':'geometry'})

def text(id, value, x, y, w, size=16, bold=False, align='center'):
    cell(id, value, f'text;html=1;align={align};verticalAlign=middle;fontFamily=Arial;fontSize={size};fontColor=#111111;fontStyle={1 if bold else 0};', x, y-15, w, 30)
    anchor = 'middle' if align=='center' else 'start'
    px = x+w/2 if align=='center' else x
    svg.append(f'<text x="{px}" y="{y+5}" text-anchor="{anchor}" font-size="{size}" font-weight="{"bold" if bold else "normal"}">{escape(value)}</text>')

def tier(id, title, y, h):
    cell(id, '', 'rounded=0;fillColor=#FFFFFF;strokeColor=#999999;dashed=1;strokeWidth=1;pointerEvents=0;', 80,y,1040,h)
    svg.append(f'<rect x="80" y="{y}" width="1040" height="{h}" fill="white" stroke="#999" stroke-dasharray="6 5"/>')
    text(id+'-title',title,100,y+26,1000,17,True,'left')

def box(id, lines, y, h, cylinder=False):
    x,w=290,620
    shape='shape=cylinder;size=15;' if cylinder else 'rounded=0;'
    value='<b>'+lines[0]+'</b><br>'+'<br>'.join(lines[1:])
    cell(id,value,shape+'html=1;whiteSpace=wrap;fillColor=#FFFFFF;strokeColor=#555555;strokeWidth=1.5;fontColor=#111111;fontSize=17;fontFamily=Arial;spacing=14;',x,y,w,h)
    boxes[id]=(x,y,w,h)
    if cylinder:
        svg.append(f'<path d="M{x} {y+15} A{w/2} 15 0 0 1 {x+w} {y+15} L{x+w} {y+h-15} A{w/2} 15 0 0 1 {x} {y+h-15} Z" fill="white" stroke="#555" stroke-width="1.5"/>')
        svg.append(f'<ellipse cx="600" cy="{y+15}" rx="{w/2}" ry="15" fill="white" stroke="#555" stroke-width="1.5"/>')
    else:
        svg.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="white" stroke="#555" stroke-width="1.5"/>')
    start=y+h/2-(len(lines)-1)*12+5+(7 if cylinder else 0)
    for i,line in enumerate(lines):
        svg.append(f'<text x="600" y="{start+i*24}" text-anchor="middle" font-size="17" font-weight="{"bold" if i==0 else "normal"}">{escape(line)}</text>')

def arrow(a,b,label):
    y1=boxes[a][1]+boxes[a][3]; y2=boxes[b][1]
    c=E.SubElement(r,'mxCell',id=a+'-to-'+b,style='html=1;startArrow=block;endArrow=block;startFill=1;endFill=1;strokeColor=#555555;strokeWidth=1.5;exitX=0.5;exitY=1;entryX=0.5;entryY=0;',edge='1',parent='1',source=a,target=b)
    E.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'})
    svg.append(f'<line x1="600" y1="{y1+2}" x2="600" y2="{y2-2}" stroke="#555" stroke-width="1.5" marker-start="url(#arrow)" marker-end="url(#arrow)"/>')
    text(a+'-flow',label,620,(y1+y2)/2,470,14,False,'left')

text('title','CRIMINAL DATABASE MANAGEMENT SYSTEM',0,35,W,25,True)
text('subtitle','System Architecture | Current application and supplied database schema',0,70,W,17)
tier('presentation','PRESENTATION TIER - React + Vite | localhost:5173',200,330)
tier('application','APPLICATION TIER - Python + FastAPI | localhost:8000',610,500)
tier('data','DATA TIER - MySQL | default localhost:3306',1200,250)
box('user',['User / Web Browser'],110,50)
box('ui',['React User Interface - App.jsx','Dashboard, case and criminal records, forms','Client-side search, filters and summary counts'],260,110)
box('client',['HTTP Client - api.js','Fetch API: GET / POST / PUT / DELETE','JSON request, response and error handling'],420,90)
box('api',['REST API - main.py','Cases, criminals, case links, crimes and officers','CORS middleware + Pydantic request validation'],670,100)
box('logic',['Business Logic - route handlers in main.py','Create cases / criminals; update case status','Link / unlink records; build parameterized SQL'],820,100)
box('access',['Database Access - database.py','SQLAlchemy engine + PyMySQL driver','Connection pooling and write transactions'],970,110)
box('database',['CriminalDB','CaseDetails | Crime | PoliceOfficer | PoliceStation','Criminal | CriminalCase | Investigation | CaseAudit','Connection settings from environment variables / .env'],1260,160,True)
for a,b,label in [('user','ui','User actions / rendered records'),('ui','client','Function calls / results'),('client','api','HTTP REST / JSON responses'),('api','logic','Validated requests / results'),('logic','access','Parameterized SQL / rows'),('access','database','SQL queries / records; commit or rollback')]:
    arrow(a,b,label)
text('note1','Backend modules are logical responsibilities within one FastAPI application.',0,1490,W,15)
text('note2','PoliceStation, Investigation and CaseAudit are in the supplied schema; no dedicated API routes are implemented.',0,1520,W,14)
svg+=['</g>','</svg>']
(P/'system-architecture.svg').write_text('\n'.join(svg),encoding='utf-8')
E.indent(mx)
E.ElementTree(mx).write(P/'system-architecture.drawio',encoding='utf-8',xml_declaration=True)
E.parse(P/'system-architecture.svg')
check=E.parse(P/'system-architecture.drawio')
assert len(check.findall('.//mxCell[@edge="1"]'))==6
print('Created and validated system-architecture.drawio and system-architecture.svg.')
