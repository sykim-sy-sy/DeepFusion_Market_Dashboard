import zipfile
import xml.etree.ElementTree as ET
import subprocess

path_a = r'C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\붙임1-1. (필수) 신청용 연구개발계획서(AX혁신기업창의기술개발사업)_취합제출본_260210.hwpx'
path_b = r'C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\KIAT_스케일업\(참고)(서식01) 스케일업 기술사업화 프로그램 연구개발계획서_접수번호(주관연구개발기관명).hwp'

# Extract A (HWPX)
try:
    with zipfile.ZipFile(path_a, 'r') as zf:
        xml_data = zf.read('Contents/section0.xml')
        # Use a namespace to parse correctly if needed, but ElementTree handles endswith fine for tags
        root = ET.fromstring(xml_data)
        texts = []
        for elem in root.iter():
            if elem.tag.endswith('t'):
                text = elem.text
                if text:
                    texts.append(text)
        
        with open('FileA_text.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(texts))
    print('Extract A success')
except Exception as e:
    print(f'Extract A failed: {e}')

# Extract B (HWP)
try:
    result = subprocess.run(['hwp5txt', path_b], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    with open('FileB_text.txt', 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    if result.returncode != 0:
        print(f'Extract B warning/error: {result.stderr}')
    else:
        print('Extract B success')
except Exception as e:
    print(f'Extract B execute failed: {e}')
