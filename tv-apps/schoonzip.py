import sys, zipfile, time
src, dst = sys.argv[1], sys.argv[2]
zin = zipfile.ZipFile(src)
t = time.localtime()[:6]
with zipfile.ZipFile(dst, 'w') as out:
    for i in zin.infolist():
        zi = zipfile.ZipInfo(i.filename, date_time=t)
        zi.create_system = 3
        zi.external_attr = i.external_attr
        if i.is_dir():
            zi.compress_type = zipfile.ZIP_STORED
            out.writestr(zi, b'')
        else:
            zi.compress_type = zipfile.ZIP_DEFLATED
            out.writestr(zi, zin.read(i.filename))
