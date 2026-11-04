import os


def scan_files():
    encoding_issues = []
    mojibake_patterns = [
        '\u00c3\u00a9', '\u00c3\u00a8', '\u00c3\u00a0',
        '\u00e2\u20ac\u2122', '\u00e2\u20ac\u0153', '\u00e2\u20ac\u009d',
        '\u00e2\u20ac\u2014', '\u00e2\u20ac\u2013', '\u00c2\u00a0',
        '\ufffd'
    ]
    
    for root, dirs, files in os.walk('.'):
        if any(p in root for p in ['.git', '.venv', 'node_modules', '.next', '__pycache__', 'data', 'browser_profile']):
            continue
        for f in files:
            if f.endswith(('.py', '.ts', '.tsx', '.md', '.json', '.txt', '.ps1')):
                p = os.path.join(root, f)
                try:
                    with open(p, 'rb') as fp:
                        content_bytes = fp.read()
                    
                    has_bom = content_bytes.startswith(b'\xef\xbb\xbf')
                    if has_bom:
                        encoding_issues.append((p, 'UTF-8 BOM detected'))
                    
                    text = content_bytes.decode('utf-8')
                    if '\ufffd' in text:
                        encoding_issues.append((p, f'Unicode replacement character (U+FFFD) count: {text.count(chr(0xFFFD))}'))
                    
                    for m in mojibake_patterns:
                        if m != '\ufffd' and m in text:
                            encoding_issues.append((p, f'Mojibake pattern found: {repr(m)} (count {text.count(m)})'))
                except UnicodeDecodeError as e:
                    encoding_issues.append((p, f'Decode error: {e}'))

    print(f"Total encoding issues found: {len(encoding_issues)}")
    for item in encoding_issues:
        print(f"  {item[0]}: {item[1]}")

if __name__ == "__main__":
    scan_files()

