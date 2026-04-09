import win32com.client
import os
import sys

def get_hwp_text(file_path):
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
        hwp.XHwpWindows.Item(0).Visible = False
        
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
            
        hwp.Open(file_path, "HWP", "force:True")
        
        # Get all text
        hwp.InitScan()
        text_list = []
        while True:
            res, text = hwp.GetText()
            if res in [0, 1]: # 0: Error, 1: End of document? 0 is usually nothing left, 1 is text found, 2 is end?
                # Actually GetText returns (state, text)
                # state: 0 (Init), 1 (Normal Text), 2 (End of Text), 3 (Section Change), etc.
                if res == 1:
                    text_list.append(text)
                elif res == 2:
                    text_list.append(text)
                    break
                else: break
            else:
                break
        hwp.ReleaseScan()
        hwp.Quit()
        return "\n".join(text_list)
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    path = sys.argv[1]
    print(get_hwp_text(path))
