import re
import urllib.request

def main():
    print("Testing http://localhost:3000/settings ...")
    req = urllib.request.Request("http://localhost:3000/settings")
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")
        print("Page HTTP Status:", resp.status)
        css_files = re.findall(r'href="(/_next/static/css/[^"]+)"', html)
        print("Found CSS files:", css_files)
        for c in css_files:
            with urllib.request.urlopen("http://localhost:3000" + c) as css_resp:
                content = css_resp.read()
                print(f"  CSS {c}: HTTP {css_resp.status}, size {len(content)} bytes")
        
        js_files = re.findall(r'src="(/_next/static/chunks/[^"]+)"', html)
        print(f"Found {len(js_files)} JS chunks.")
        for j in js_files[:6]:
            with urllib.request.urlopen("http://localhost:3000" + j) as js_resp:
                content = js_resp.read()
                print(f"  JS {j}: HTTP {js_resp.status}, size {len(content)} bytes")

if __name__ == "__main__":
    main()
