import win32com.client
import os
import sys

def get_hwp_content(file_path):
    hwp = None
    try:
        hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
        # hwp.XHwpWindows.Item(0).Visible = True # For debugging
        
        abs_path = os.path.abspath(file_path)
        print(f"Opening: {abs_path}")
        
        # Try simple Open first
        res = hwp.Open(abs_path)
        if not res:
            return f"Error: Failed to open file {abs_path}"
        
        # Get Field List to see if it's a form
        fields = hwp.GetFieldList()
        print(f"Fields: {fields}")
        
        # Get All Text
        text_list = []
        hwp.InitScan()
        while True:
            state, text = hwp.GetText()
            if state == 1: # Normal text
                text_list.append(text)
            elif state == 2: # End of text
                text_list.append(text)
                break
            elif state == 0: # Error or no text
                break
            else: # Other states (section change etc)
                pass
        hwp.ReleaseScan()
        
        content = "\n".join(text_list)
        return content
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: {e}"
    finally:
        if hwp:
            hwp.Quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_text.py <file_path>")
        sys.exit(1)
    print(get_hwp_content(sys.argv[1]))
