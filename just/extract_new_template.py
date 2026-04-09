import subprocess

path_new = r'C:\Users\KIM SIYE\Downloads\한글 깔끔한 보고서 양식 샘플 2.hwp'

try:
    result = subprocess.run(['hwp5txt', path_new], capture_output=True, text=True, encoding='utf-8', errors='ignore')
    with open('NewTemplate_text.txt', 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    if result.returncode != 0:
        print(f'Extract Target warning/error: {result.stderr}')
    else:
        print('Extract Target success')
except Exception as e:
    print(f'Extract Target execute failed: {e}')
