"""Generate editable Chen notation ER diagram and SVG."""
from pathlib import Path
from html import escape
import xml.etree.ElementTree as E
import math
import ast
P=Path(__file__).parent
old=ast.parse((P/'build_er_tables.py').read_text())
entities=next(ast.literal_eval(n.value) for n in old.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='entities' for t in n.targets))
positions={'Crime':(350,350),'PoliceOfficer':(950,350),'PoliceStation':(1550,350),'CaseDetails':(950,880),'CriminalCase':(1550,880),'CaseAudit':(350,1410),'Investigation':(950,1410),'Criminal':(1550,1410)}
rels=[('Crime','CaseDetails','Classifies',350,880),('PoliceStation','PoliceOfficer','Has officers',1250,350),('PoliceOfficer','CaseDetails','Handles',950,615),('CaseDetails','CriminalCase','Has links',1250,880),('CaseDetails','CaseAudit','Has audit',650,1145),('CaseDetails','Investigation','Investigates',950,1150),('Criminal','CriminalCase','Has links',1550,1150)]
mx=E.Element('mxfile',host='app.diagrams.net',type='device'); d=E.SubElement(mx,'diagram',id='criminal-db-er',name='Chen ER Diagram'); m=E.SubElement(d,'mxGraphModel',grid='0',page='1',pageScale='1',pageWidth='1900',pageHeight='1720',background='#FFFFFF'); r=E.SubElement(m,'root'); E.SubElement(r,'mxCell',id='0'); E.SubElement(r,'mxCell',id='1',parent='0')
nodes={}; lines=[]; labels=[]
def node(id,text,shape,x,y,w,h,pk=False):
 c=E.SubElement(r,'mxCell',id=id,value='<u>'+text+'</u>' if pk else text,style=f'{shape};whiteSpace=wrap;html=1;fillColor=#FFFFFF;strokeColor=#555555;strokeWidth=1.5;fontColor=#111111;fontFamily=Arial;fontSize=16;rounded=0;',vertex='1',parent='1'); E.SubElement(c,'mxGeometry',x=str(x-w/2),y=str(y-h/2),width=str(w),height=str(h),**{'as':'geometry'}); nodes[id]=(text,shape,x,y,w,h,pk)
def label(text,x,y,size=16):
 c=E.SubElement(r,'mxCell',id='label-'+str(len(labels)),value=text,style=f'text;html=1;align=center;verticalAlign=middle;fontFamily=Arial;fontSize={size};fontColor=#111111;',vertex='1',parent='1'); E.SubElement(c,'mxGeometry',x=str(x-880),y=str(y-15),width='1760',height='30',**{'as':'geometry'}); labels.append((text,x,y,size))
def boundary(id,toward):
 _,shape,x,y,w,h,_=nodes[id]; dx,dy=toward[0]-x,toward[1]-y
 if shape=='ellipse': k=1/math.sqrt((dx/(w/2))**2+(dy/(h/2))**2)
 elif shape=='rhombus': k=1/(abs(dx)/(w/2)+abs(dy)/(h/2))
 else: k=1/max(abs(dx)/(w/2),abs(dy)/(h/2))
 return x+dx*k,y+dy*k
def connect(a,b,card=None):
 pa,pb=nodes[a][2:4],nodes[b][2:4]; start,end=boundary(a,pb),boundary(b,pa)
 c=E.SubElement(r,'mxCell',id='edge-'+str(len(lines)),style='endArrow=none;startArrow=none;html=1;strokeColor=#666666;strokeWidth=1.3;',edge='1',parent='1',source=a,target=b); E.SubElement(c,'mxGeometry',relative='1',**{'as':'geometry'}); lines.append((start,end))
 if card:
  dx,dy=end[0]-start[0],end[1]-start[1]; l=math.hypot(dx,dy); label(card,start[0]+dx*24/l-dy*14/l,start[1]+dy*24/l+dx*14/l,17)
label('CRIMINAL DATABASE - ENTITY RELATIONSHIP DIAGRAM',950,45,26)
offsets=[(-140,-155),(140,-155),(-160,155),(160,155),(-240,0)]
case_offsets=[(-260,-210),(-110,-130),(130,-190),(270,-100),(250,115),(130,205),(-260,65)]
for name,(_,_,fields) in entities.items():
 x,y=positions[name]; node(name,name,'rectangle',x,y,170,50)
 for i,(key,field) in enumerate(fields):
  ox,oy=(case_offsets if name=='CaseDetails' else offsets)[i]; text=field+(' (FK)' if 'FK' in key else ''); node(name+'-'+field,text,'ellipse',x+ox,y+oy,max(170,len(text)*8+32),50,'PK' in key); connect(name,name+'-'+field)
for i,(a,b,text,x,y) in enumerate(rels):
 id='relationship-'+str(i); node(id,text,'rhombus',x,y,170,84); connect(a,id,'1'); connect(b,id,'M')
label('Rectangle: entity | Oval: attribute | Diamond: relationship | Underlined: primary key | (FK): foreign key',950,1650)
label('CriminalCase composite primary key: (CriminalID, CaseID). All relationships are 1 : M; minimum participation is unspecified.',950,1685)
E.indent(mx); E.ElementTree(mx).write(P/'criminal-db-er.drawio',encoding='utf-8',xml_declaration=True)
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1900" height="1720" viewBox="0 0 1900 1720">','<rect width="100%" height="100%" fill="white"/>','<g font-family="Arial, sans-serif" font-size="16" fill="#111">']
for (x1,y1),(x2,y2) in lines: svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#666" stroke-width="1.3"/>')
for text,shape,x,y,w,h,pk in nodes.values():
 attrs='fill="white" stroke="#555" stroke-width="1.5"'
 if shape=='ellipse': svg.append(f'<ellipse cx="{x}" cy="{y}" rx="{w/2}" ry="{h/2}" {attrs}/>')
 elif shape=='rhombus': svg.append(f'<polygon points="{x},{y-h/2} {x+w/2},{y} {x},{y+h/2} {x-w/2},{y}" {attrs}/>')
 else: svg.append(f'<rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}" {attrs}/>')
 dec=' text-decoration="underline"' if pk else ''; size=14 if shape=='rhombus' else 16
 svg.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="{size}"{dec}>{escape(text)}</text>')
for text,x,y,size in labels: svg.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" font-size="{size}">{escape(text)}</text>')
svg+=['</g>','</svg>']; (P/'criminal-db-er.svg').write_text('\n'.join(svg),encoding='utf-8')
E.parse(P/'criminal-db-er.svg'); E.parse(P/'criminal-db-er.drawio'); assert len(nodes)==50 and len(lines)==49
print('Verified 8 entities, 35 attributes, 7 relationship diamonds and 14 cardinality labels.')
