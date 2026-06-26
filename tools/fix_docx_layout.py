from docx import Document
from lxml import etree
from docx.shared import Cm

nsmap = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
doc = Document(r'输出/复习讲义/01_统计调查与直方图_复习讲义_含答案.docx')

# Fix sections: single column, A4, narrow margins
for section in doc.sections:
    sectPr = section._sectPr
    cols = sectPr.findall(f'{{{nsmap}}}cols')
    for col in cols:
        col.set(f'{{{nsmap}}}num', '1')
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(1.5)
    section.right_margin = Cm(1.5)

# Fix all tables to full width
for i, table in enumerate(doc.tables):
    tbl = table._tbl
    tblPr = tbl.find(f'{{{nsmap}}}tblPr')
    if tblPr is None:
        tblPr = etree.SubElement(tbl, f'{{{nsmap}}}tblPr')
    
    tblW = tblPr.find(f'{{{nsmap}}}tblW')
    if tblW is None:
        tblW = etree.Element(f'{{{nsmap}}}tblW')
        tblPr.insert(0, tblW)
    tblW.set(f'{{{nsmap}}}w', '5000')
    tblW.set(f'{{{nsmap}}}type', 'pct')
    
    for elem in tblPr.findall(f'{{{nsmap}}}tblLayout'):
        tblPr.remove(elem)
    
    for row in table.rows:
        for cell in row.cells:
            tcPr = cell._tc.find(f'{{{nsmap}}}tcPr')
            if tcPr is not None:
                tcW = tcPr.find(f'{{{nsmap}}}tcW')
                if tcW is not None:
                    tcPr.remove(tcW)
    
    tblGrid = tbl.find(f'{{{nsmap}}}tblGrid')
    if tblGrid is not None:
        gridCols = tblGrid.findall(f'{{{nsmap}}}gridCol')
        if gridCols:
            each = 5000 // len(gridCols)
            for gc in gridCols:
                gc.set(f'{{{nsmap}}}w', str(each))

    print(f'Table {i}: {len(table.rows)}r x {len(table.columns)}c fixed')

doc.save(r'输出/复习讲义/01_统计调查与直方图_复习讲义_含答案.docx')
print('Done')