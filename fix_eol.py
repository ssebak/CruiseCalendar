import pathlib
for fn in ['index.py','calendar.cgi']:
    p = pathlib.Path(fn)
    text = p.read_text(encoding='utf-8')
    new = text.replace('\r\n', '\n')
    # write with explicit LF newline and utf-8 encoding
    p.write_text(new, encoding='utf-8', newline='\n')
    print(f'fixed {fn}')
