import zipfile
import os
import xml.etree.ElementTree as ET

def extract_hwpx_text(hwpx_path):
    try:
        with zipfile.ZipFile(hwpx_path, 'r') as z:
            # HWPX stores content in Contents/section0.xml
            # There might be multiple sections, but usually section0.xml has the bulk
            section_paths = [name for name in z.namelist() if name.startswith('Contents/section') and name.endswith('.xml')]
            
            all_text = []
            for path in sorted(section_paths):
                with z.open(path) as f:
                    tree = ET.parse(f)
                    root = tree.getroot()
                    # Find all <hp:t> (text) elements
                    # The namespace is usually http://www.hancom.co.kr/hwpml/2011/paragraph
                    namespaces = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
                    for t in root.findall('.//hp:t', namespaces):
                        if t.text:
                            all_text.append(t.text)
            
            return "\n".join(all_text)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python extract_hwpx.py <file_path>")
    else:
        print(extract_hwpx_text(sys.argv[1]))
