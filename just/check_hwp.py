import win32com.client
try:
    hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
    print("HWP_AVAILABLE")
    hwp.Quit()
except Exception as e:
    print(f"HWP_UNAVAILABLE: {e}")
