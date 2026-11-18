"""Genera un DOCX editable con ecuaciones OMML y un PDF vectorial sencillo.

No requiere paquetes externos. Las figuras se crean como SVG y se incrustan en
el DOCX; el índice es un campo TOC actualizable por Word.
"""
from __future__ import annotations
import html, json, math, struct, zlib
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).parents[1]
DATA = ROOT / "resultados" / "wenner" / "wenner_resultados.json"
OUT = ROOT / "entregables"

def esc(s): return html.escape(str(s), quote=True)
def p(text="", style=None):
    st = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ''
    return f'<w:p>{st}<w:r><w:t xml:space="preserve">{esc(text)}</w:t></w:r></w:p>'
def heading(text, level): return p(text, f"Heading{level}")
def equation(latex):
    # OMML nativo: el código conserva LaTeX y el documento recibe glifos matemáticos editables.
    native = latex.replace('\\rho_a', 'ρₐ').replace('\\pi', 'π').replace('\\', '').replace('^2', '²')
    return f'<w:p><m:oMathPara><m:oMath><m:r><m:t>{esc(native)}</m:t></m:r></m:oMath></m:oMathPara></w:p>'
def toc():
    return '<w:p><w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h </w:instrText></w:r><w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>Actualice este índice en Word.</w:t></w:r><w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
def table(headers, rows):
    body = '<w:tbl><w:tblPr><w:tblBorders><w:top w:val="single"/><w:left w:val="single"/><w:bottom w:val="single"/><w:right w:val="single"/><w:insideH w:val="single"/><w:insideV w:val="single"/></w:tblBorders></w:tblPr>'
    for row in [headers, *rows]:
        body += '<w:tr>' + ''.join(f'<w:tc><w:p><w:r><w:t>{esc(cell)}</w:t></w:r></w:p></w:tc>' for cell in row) + '</w:tr>'
    return body + '</w:tbl>'
def svg_chart(rows, path):
    width, height = 700, 360; left, bottom = 75, 300; plot_h = 230; maxv = max(r['rho_aparente_ohm_m'] for r in rows) * 1.12
    bars=[]
    for i,r in enumerate(rows):
        x=150+i*260; h=plot_h*r['rho_aparente_ohm_m']/maxv; y=bottom-h
        bars.append(f'<rect x="{x}" y="{y:.1f}" width="120" height="{h:.1f}" fill="#1769aa"/><text x="{x+60}" y="{bottom+25}" text-anchor="middle">{r["ensayo"]}</text><text x="{x+60}" y="{y-8:.1f}" text-anchor="middle">{r["rho_aparente_ohm_m"]:.2f}</text>')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/><text x="350" y="28" text-anchor="middle" font-size="18">Resistividad aparente simplificada (Ω·m)</text><line x1="{left}" y1="{bottom}" x2="650" y2="{bottom}" stroke="black"/><line x1="{left}" y1="60" x2="{left}" y2="{bottom}" stroke="black"/><text x="18" y="190" transform="rotate(-90 18 190)" text-anchor="middle">ρa (Ω·m)</text>{"".join(bars)}</svg>'
    path.write_text(svg, encoding='utf-8'); return svg.encode()
def image_para():
    drawing='<w:p><w:r><w:drawing><wp:inline xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"><wp:extent cx="5700000" cy="2925000"/><wp:docPr id="1" name="Figura Wenner"/><a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:nvPicPr><pic:cNvPr id="0" name="wenner.svg"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="rId1"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="5700000" cy="2925000"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>'
    return drawing
def docx_package(body, svg_bytes, path):
    document=f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><w:body>{body}<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1100" w:right="1100" w:bottom="1100" w:left="1100"/></w:sectPr></w:body></w:document>'''
    ct='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Default Extension="svg" ContentType="image/svg+xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/></Types>'
    rels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'
    drels='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="media/wenner.svg"/></Relationships>'
    settings='<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:updateFields w:val="true"/></w:settings>'
    with ZipFile(path,'w',ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml',ct); z.writestr('_rels/.rels',rels); z.writestr('word/document.xml',document); z.writestr('word/settings.xml',settings); z.writestr('word/_rels/document.xml.rels',drels); z.writestr('word/media/wenner.svg',svg_bytes)
def pdf_escape(s): return s.replace('\\','\\\\').replace('(','\\(').replace(')','\\)')
def write_pdf(data, path):
    lines=['BT /F1 16 Tf 50 760 Td (Informe academico Wenner - INA CENATE) Tj /F1 10 Tf 0 -28 Td']
    lines += [f'({pdf_escape(t)}) Tj 0 -16 Td' for t in ['Metodo de cuatro picas; resultados reproducibles.',f'W01: rho_a = {data["filas"][0]["rho_aparente_ohm_m"]:.2f} ohm m',f'W02: rho_a = {data["filas"][1]["rho_aparente_ohm_m"]:.2f} ohm m',f'R media = {data["estadisticas"]["resistencia_media_ohm"]:.4f} ohm; s = {data["estadisticas"]["desviacion_estandar_muestral_ohm"]:.4f} ohm',f'CV descriptivo = {data["estadisticas"]["coeficiente_variacion_descriptivo_pct"]:.4f} %','Las lecturas tienen separaciones diferentes; no son repetibilidad.']]
    lines += ['ET']; stream=' '.join(lines).encode(); objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream']
    out=b'%PDF-1.4\n'; offsets=[0]
    for i,obj in enumerate(objs,1): offsets.append(len(out)); out += f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n'
    xref=len(out); out += f'xref\n0 {len(objs)+1}\n0000000000 65535 f \n'.encode()+b''.join(f'{o:010d} 00000 n \n'.encode() for o in offsets[1:])+f'trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF'.encode(); path.write_bytes(out)
def main():
    OUT.mkdir(exist_ok=True); data=json.loads(DATA.read_text(encoding='utf-8')); svg=svg_chart(data['filas'],OUT/'figura_wenner_resistividad.svg')
    body=heading('Instituto Nacional de Aprendizaje (INA) — CENATE',1)+p('Informe académico: análisis de resistividad aparente mediante el método Wenner')+p('Alcance: cuatro picas; datos originales conservados.')+toc()+heading('Resumen',1)+p('Se auditaron dos lecturas de campo y se calcularon resistividades aparentes con rho_a = 2*pi*a*R. La separación cambió entre lecturas, por lo que la comparación es descriptiva y no un ensayo de repetibilidad.')+heading('Introducción y objetivos',1)+p('Documentar de forma reproducible la medición Wenner y separar evidencia original, datos transcritos y resultados derivados.')+heading('Fundamento teórico',1)+p('El arreglo usa cuatro electrodos alineados y espaciados uniformemente. La longitud total es L=3a.')+equation('\\rho_a = 2\\pi aR')+equation('L = 3a')+p('La corrección por profundidad finita se informa como sensibilidad:')+equation('rho_c = 4πaR / [1 + 2a/√(a²+4b²) − 2a/√(4a²+4b²)]')+heading('Materiales y metodología',1)+p('Telurómetro Fluke visible en la evidencia, cuatro picas, conductores y cinta métrica. Se conservaron las lecturas de pantalla del documento fuente.')+heading('Datos experimentales',1)+table(['Ensayo','a (m)','b (m)','R (Ω)','Fuente'],[[r['ensayo'],f'{r["a_m"]:.2f}',f'{r["b_m"]:.2f}',f'{r["resistencia_ohm"]:.1f}',r['fuente']] for r in data['filas']])+heading('Cálculos y estadística descriptiva',1)+table(['Ensayo','L (m)','ρa (Ω·m)','ρ corregida (Ω·m)'],[[r['ensayo'],f'{r["longitud_total_m"]:.1f}',f'{r["rho_aparente_ohm_m"]:.2f}',f'{r["rho_corregida_ohm_m"]:.2f}'] for r in data['filas']])+p('R media = 83,7500 Ω; desviación estándar muestral = 0,0707 Ω; CV descriptivo = 0,0844 %.')+heading('Visualización',1)+p('La figura compara únicamente las dos resistividades calculadas; no interpola datos.')+p('Figura 1. Resistividad aparente por ensayo.')+image_para()+heading('Discusión técnica y limitaciones',1)+p('Las cifras son coherentes dimensionalmente: Ω·m·Ω = Ω·m. Las imágenes verifican 83,8 Ω y 83,7 Ω. No se infieren intervalos de confianza ni se atribuye uniformidad del terreno sin caracterización adicional.')+heading('Conclusiones',1)+p('El flujo reproduce dos resultados Wenner y documenta su procedencia. La diferencia de separación exige interpretar la variación como descriptiva.')+heading('Referencias y anexos',1)+p('Informe con telurometro 1.docx, documento original conservado en la raíz del repositorio. Anexo: referencias a image7.png e image8.png dentro del DOCX original.')
    docx_package(body,svg,OUT/'informe_academico_wenner.docx'); write_pdf(data,OUT/'informe_academico_wenner.pdf')
if __name__=='__main__': main()
