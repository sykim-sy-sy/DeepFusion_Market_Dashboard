import win32com.client
import os
import sys

def check_fields(file_path):
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        # hwp.RegisterModule("FilePathCheckDLL", "SecurityModule") # Sometimes needed, sometimes not
        hwp.XHwpWindows.Item(0).Visible = False
        
        if not os.path.exists(file_path):
            return f"Error: File not found at {file_path}"
            
        hwp.Open(file_path) # Default open
        
        field_list = hwp.GetFieldList().split("\x02") # HWP uses 0x02 as separator
        hwp.Quit()
        return field_list
    except Exception as e:
        try: hwp.Quit()
        except: pass
        return f"Error: {e}"

if __name__ == "__main__":
    path = sys.argv[1]
    print(check_fields(path))
