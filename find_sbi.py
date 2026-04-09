import os

def find_sbi_folders(root_path):
    results = []
    for root, dirs, files in os.walk(root_path):
        for d in dirs:
            if 'SBI' in d:
                results.append(os.path.join(root, d))
    return results

root = r'C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면'
sbi_paths = find_sbi_folders(root)

with open(r'c:\Users\KIM SIYE\.gemini\antigravity\brain\fcc6c4ca-9199-49f4-b568-79196da05034\sbi_paths.txt', 'w', encoding='utf-8') as f:
    for p in sbi_paths:
        f.write(p + '\n')
