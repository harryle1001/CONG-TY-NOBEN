import zipfile, sys, re
src, dst = sys.argv[1], sys.argv[2]
zi = zipfile.ZipFile(src)
zo = zipfile.ZipFile(dst, 'w', zipfile.ZIP_DEFLATED)
for it in zi.infolist():
    if it.filename == 'docProps/core.xml':
        continue
    data = zi.read(it.filename)
    if it.filename == '_rels/.rels':
        data = re.sub(rb'<Relationship [^>]*core-properties"[^>]*/>', b'', data)
    if it.filename == '[Content_Types].xml':
        data = re.sub(rb'<Override PartName="/docProps/core.xml"[^>]*/>', b'', data)
    zo.writestr(it, data)
zo.close()
