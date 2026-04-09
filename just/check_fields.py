import win32com.client
import os

path_b = r'C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\KIAT_스케일업\(참고)(서식01) 스케일업 기술사업화 프로그램 연구개발계획서_접수번호(주관연구개발기관명).hwp'

hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
# RegisterModule is needed to avoid security popups in newer versions if applicable, but we'll try without it first
hwp.RegisterModule('FilePathCheckDLL', 'SecurityModule')

hwp.Open(path_b)

# Get Field List
# option: 1=Cell, 2=ClickHere, 0=All
fields = hwp.GetFieldList(0, 0)
if fields:
    print("Fields found:")
    print(fields)
else:
    print("No fields (누름틀 or Cell names) found in the document.")

hwp.Quit()
