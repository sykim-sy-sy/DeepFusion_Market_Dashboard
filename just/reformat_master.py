import win32com.client
import os
import zipfile
import xml.etree.ElementTree as ET
import shutil

# Paths
BASE_DIR = r"C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\DFAI_Management - 비지니스\김시예 업무지시 내용\스타트업 리서치 추가 요청사항"
TEMPLATE_NAME = "딥퓨전에이아이 공문 서식.hwp"
TEMPLATE_PATH = os.path.join(BASE_DIR, TEMPLATE_NAME)
OUTPUT_DIR = r"C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\Marketing_Team\just\output"

FILES_TO_PROCESS = [
    "주권 미발행 확인서_스타트업리엔필드투자조합4호.hwpx",
    "주권 미발행 확인서_에스알글로벌그로스투자조합23호.hwpx",
    "주금납입영수증_스타트업리엔필드투자조합4호.hwpx",
    "주금납입영수증_에스알글로벌그로스투자조합23호.hwpx"
]

def extract_hwpx_text(hwpx_path):
    try:
        with zipfile.ZipFile(hwpx_path, 'r') as z:
            section_paths = [name for name in z.namelist() if name.startswith('Contents/section') and name.endswith('.xml')]
            all_text = []
            namespaces = {'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph'}
            for path in sorted(section_paths):
                with z.open(path) as f:
                    root = ET.parse(f).getroot()
                    for t in root.findall('.//hp:t', namespaces):
                        if t.text:
                            all_text.append(t.text)
            return "\n".join(all_text)
    except Exception as e:
        return f"Error extracting HWPX: {e}"

def process_file(file_name, hwp):
    file_path = os.path.join(BASE_DIR, file_name)
    extracted_text = extract_hwpx_text(file_path)
    
    # 1. Open Template (we do this fresh for each file to ensure layout is clean)
    # We copy template to a temp path for OLE safety
    temp_template = os.path.join(OUTPUT_DIR, "temp_template.hwp")
    shutil.copy2(TEMPLATE_PATH, temp_template)
    
    hwp.Open(temp_template, "HWP", "force:True")
    
    # 2. Inject content
    # We'll try to find a placeholder or just insert in the main body.
    # Official forms usually have headings. We'll try to find "개요" or just go to end of document.
    
    # Let's try to clear existing sample text if any
    # (This is tricky without knowing the fields, so we'll just append or use a specific action)
    
    # Move to the beginning and find a good spot.
    # If the template has "개요", "추진방안" etc., we'll put certificates in "개요" or "본문"
    # For now, let's just insert at the end of the first page or find a heading.
    
    hwp.HAction.Run("MoveDocEnd")
    hwp.HAction.Run("BreakPara")
    hwp.HAction.Run("BreakPara")
    
    # Insert extracted text
    act = hwp.CreateAction("InsertText")
    pset = act.CreateSet()
    act.GetDefault(pset)
    pset.SetItem("Text", extracted_text)
    act.Execute(pset)
    
    # 3. Save as new file
    output_name = file_name.replace(".hwpx", "_변환본.hwp")
    output_path = os.path.join(OUTPUT_DIR, output_name)
    
    act_save = hwp.CreateAction("FileSaveAs_S")
    pset_save = act_save.CreateSet()
    act_save.GetDefault(pset_save)
    pset_save.SetItem("FileName", output_path)
    pset_save.SetItem("Format", "HWP")
    act_save.Execute(pset_save)
    
    print(f"Processed: {output_name}")
    os.remove(temp_template)

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    hwp = None
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.XHwpWindows.Item(0).Visible = False
        
        for file_name in FILES_TO_PROCESS:
            try:
                process_file(file_name, hwp)
            except Exception as e:
                print(f"Failed to process {file_name}: {e}")
                
        hwp.Quit()
        print("All files processed.")
    except Exception as e:
        print(f"Fatal error: {e}")
        if hwp: hwp.Quit()

if __name__ == "__main__":
    main()
