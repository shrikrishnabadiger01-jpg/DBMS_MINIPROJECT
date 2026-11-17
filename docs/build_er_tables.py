"""Generate an editable draw.io diagram and matching SVG from the supplied complete schema."""
from pathlib import Path
import xml.etree.ElementTree as ET
from html import escape

OUT = Path(__file__).parent
entities = {
    'Crime': (60, 130, [('PK', 'CrimeID'), ('', 'CrimeType'), ('', 'CrimeLocation'), ('', 'Description')]),
    'PoliceOfficer': (440, 130, [('PK', 'OfficerID'), ('', 'OfficerName'), ('', 'RankName'), ('FK', 'StationID')]),
    'PoliceStation': (820, 130, [('PK', 'StationID'), ('', 'StationName'), ('', 'Location'), ('', 'Phone')]),
    'CaseDetails': (440, 420, [('PK', 'CaseID'), ('', 'FIRNumber'), ('FK', 'CrimeID'), ('FK', 'OfficerID'), ('', 'CaseStatus'), ('', 'OpenedDate'), ('', 'ClosedDate')]),
    'CriminalCase': (820, 420, [('PK, FK', 'CriminalID'), ('PK, FK', 'CaseID'), ('', 'PersonRole')]),
    'CaseAudit': (60, 820, [('PK', 'AuditID'), ('FK', 'CaseID'), ('', 'OldStatus'), ('', 'NewStatus'), ('', 'ChangedAt')]),
    'Investigation': (440, 820, [('PK', 'InvestigationID'), ('FK', 'CaseID'), ('', 'InvestigationDate'), ('', 'Notes')]),
    'Criminal': (820, 820, [('PK', 'CriminalID'), ('', 'FullName'), ('', 'DateOfBirth'), ('', 'Address')]),
}
# Parent, child, referenced field, foreign-key field, routing points, attachment sides.
relations = [
    ('Crime', 'CaseDetails', 'CrimeID', 'CrimeID', [(190, 320), (190, 563), (440, 563)], '0.5,1', '0,0.5'),
    ('PoliceStation', 'PoliceOfficer', 'StationID', 'StationID', [(820, 225), (700, 225)], '0,0.5', '1,0.5'),
    ('PoliceOfficer', 'CaseDetails', 'OfficerID', 'OfficerID', [(570, 320), (570, 420)], '0.5,1', '0.5,0'),
    ('CaseDetails', 'CriminalCase', 'CaseID', 'CaseID', [(700, 499), (820, 499)], '1,0.2762237762', '0,0.5'),
    ('CaseDetails', 'CaseAudit', 'CaseID', 'CaseID', [(492, 706), (492, 760), (190, 760), (190, 820)], '0.2,1', '0.5,0'),
    ('CaseDetails', 'Investigation', 'CaseID', 'CaseID', [(570, 706), (570, 820)], '0.5,1', '0.5,0'),
    ('Criminal', 'CriminalCase', 'CriminalID', 'CriminalID', [(950, 820), (950, 578)], '0.5,0', '0.5,1'),
]

mx = ET.Element('mxfile', host='app.diagrams.net', type='device')
diagram = ET.SubElement(mx, 'diagram', id='criminal-db-er', name='ER Diagram')
model = ET.SubElement(diagram, 'mxGraphModel', dx='1200', dy='1240', grid='1', gridSize='10', page='1', pageScale='1', pageWidth='1160', pageHeight='1240')
root = ET.SubElement(model, 'root')
ET.SubElement(root, 'mxCell', id='0')
ET.SubElement(root, 'mxCell', id='1', parent='0')

def vertex(id_, value, style, x, y, w, h, parent='1'):
    cell = ET.SubElement(root, 'mxCell', id=id_, value=value, style=style, vertex='1', parent=parent)
    ET.SubElement(cell, 'mxGeometry', x=str(x), y=str(y), width=str(w), height=str(h), **{'as': 'geometry'})
    return cell

vertex('title', 'CRIMINAL DATABASE | Entity Relationship Diagram', 'text;html=1;align=left;fontSize=25;fontStyle=1;fontColor=#17324D;', 60, 30, 1040, 45)
vertex('subtitle', 'Complete attributes and one-to-many relationships from the supplied schema', 'text;html=1;align=left;fontSize=15;fontColor=#64748B;', 60, 80, 1000, 30)
for name, (x, y, fields) in entities.items():
    vertex(name, name, 'swimlane;html=1;startSize=42;horizontal=1;rounded=0;fillColor=#DAE8FC;swimlaneFillColor=#FFFFFF;strokeColor=#6C8EBF;fontColor=#17324D;fontSize=18;fontStyle=1;align=left;spacingLeft=16;collapsible=0;', x, y, 260, 62 + 32 * len(fields))
    for i, (key, field) in enumerate(fields):
        vertex(f'{name}-{field}', f'{key}    {field}', 'text;html=1;align=left;verticalAlign=middle;fontSize=15;fontColor=#334155;spacingLeft=16;', 0, 48 + 32*i, 260, 32, name)

for i, (parent, child, pk, fk, points, start, end) in enumerate(relations):
    sx, sy = start.split(','); ex, ey = end.split(',')
    style = f'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;startArrow=ERone;startFill=0;endArrow=ERmany;endFill=0;strokeColor=#475569;strokeWidth=2;exitX={sx};exitY={sy};exitPerimeter=1;entryX={ex};entryY={ey};entryPerimeter=1;'
    cell = ET.SubElement(root, 'mxCell', id=f'rel-{i}', value='', style=style, edge='1', parent='1', source=parent, target=child)
    geom = ET.SubElement(cell, 'mxGeometry', relative='1', **{'as': 'geometry'})
    if len(points) > 2:
        arr = ET.SubElement(geom, 'Array', **{'as': 'points'})
        for px, py in points[1:-1]:
            ET.SubElement(arr, 'mxPoint', x=str(px), y=str(py))

notes = ['PK = primary key. FK = foreign key. Crow\'s-foot end = many; single-bar end = one.',
         'CriminalCase uses the supplied composite primary key: (CriminalID, CaseID).',
         'Investigation.CaseID is a foreign key, as confirmed by the earlier relationship table.',
         'Minimum participation / nullability is not specified by the supplied schema.']
vertex('notes', '<br>'.join(notes), 'text;html=1;align=left;verticalAlign=top;fontSize=13;fontColor=#64748B;', 60, 1100, 1040, 110)
ET.indent(mx)
ET.ElementTree(mx).write(OUT / 'criminal-db-er.drawio', encoding='utf-8', xml_declaration=True)

svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1160" height="1240" viewBox="0 0 1160 1240">',
       '<rect width="1160" height="1240" fill="#f8fafc"/>',
       '<g font-family="Arial, sans-serif">',
       '<text x="60" y="60" fill="#17324d" font-size="25" font-weight="bold">CRIMINAL DATABASE | Entity Relationship Diagram</text>',
       '<text x="60" y="100" fill="#64748b" font-size="15">Complete attributes and one-to-many relationships from the supplied schema</text>']
for _, _, _, _, points, _, _ in relations:
    svg.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="#475569" stroke-width="2"/>')
    # One bar at the parent, crow's foot at the child. Minimum cardinalities are intentionally omitted.
    for is_parent in [True, False]:
        tip = points[0] if is_parent else points[-1]
        near = points[1] if is_parent else points[-2]
        dx = 0 if near[0] == tip[0] else (1 if near[0] > tip[0] else -1)
        dy = 0 if near[1] == tip[1] else (1 if near[1] > tip[1] else -1)
        bx, by = tip[0]+dx*17, tip[1]+dy*17
        if is_parent:
            svg.append(f'<path d="M {bx-dy*8} {by+dx*8} L {bx+dy*8} {by-dx*8}" stroke="#475569" stroke-width="2"/>')
        else:
            svg.append(f'<path d="M {tip[0]-dy*9} {tip[1]+dx*9} L {bx} {by} L {tip[0]+dy*9} {tip[1]-dx*9}" fill="none" stroke="#475569" stroke-width="2"/>')
for name, (x, y, fields) in entities.items():
    h = 62+32*len(fields)
    svg += [f'<rect x="{x}" y="{y}" width="260" height="{h}" fill="white" stroke="#6c8ebf" stroke-width="1.5"/>',
            f'<rect x="{x}" y="{y}" width="260" height="42" fill="#dae8fc" stroke="#6c8ebf"/>',
            f'<text x="{x+16}" y="{y+27}" font-size="18" font-weight="bold" fill="#17324d">{name}</text>']
    for i, (key, field) in enumerate(fields):
        svg.append(f'<text x="{x+16}" y="{y+70+32*i}" font-size="15" fill="#334155"><tspan font-weight="bold">{key}</tspan><tspan x="{x+90}">{field}</tspan></text>')
for i, line in enumerate(notes):
    svg.append(f'<text x="60" y="{1125+23*i}" font-size="13" fill="#64748b">{escape(line)}</text>')
svg += ['</g>', '</svg>']
(OUT / 'criminal-db-er.svg').write_text('\n'.join(svg), encoding='utf-8')

# Verify the generated documents are well-formed and all seven relationships are present.
ET.parse(OUT / 'criminal-db-er.svg')
parsed = ET.parse(OUT / 'criminal-db-er.drawio')
assert len(parsed.findall('.//mxCell[@edge="1"]')) == 7
print('Created criminal-db-er.drawio and criminal-db-er.svg (8 entities, 7 relationships).')
