import os
import shutil

SOURCE_DIR = r"C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\Marketing_Team\just\output"
TARGET_DIR = r"C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\DFAI_Management - 비지니스\김시예 업무지시 내용\스타트업 리서치 추가 요청사항\변환결과"

def move_files():
    if not os.path.exists(TARGET_DIR):
        try:
            os.makedirs(TARGET_DIR)
        except Exception as e:
            print(f"Failed to create target dir: {e}")
            # If we can't create it there, we'll just keep them in the workspace
            return

    for file_name in os.listdir(SOURCE_DIR):
        if file_name.endswith("_변환본.hwp"):
            src = os.path.join(SOURCE_DIR, file_name)
            dst = os.path.join(TARGET_DIR, file_name)
            try:
                shutil.move(src, dst)
                print(f"Moved: {file_name}")
            except Exception as e:
                print(f"Failed to move {file_name}: {e}")

if __name__ == "__main__":
    move_files()
