import win32com.client
import os
import traceback

path_template = r'C:\Users\KIM SIYE\Downloads\한글 깔끔한 보고서 양식 샘플 2.hwp'
output_path = r'C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\Marketing_Team\just\Deepfusion_보고서_작성본.hwp'

replace_dict = {
    "최신 기술을 접목한 OOOO 시스템의 사용자 친화적 UI/UX 개선을 위한 용역사업 추진": "CES 2026 인공지능 부문 최고혁신상을 수상한 4D 이미징 레이더 딥러닝(RAPA) 기술을 기반으로, 글로벌 자율주행 모빌리티 시장 선점 및 국방 무인화 체계 수주를 통해 글로벌 탑티어 센서 퓨전 기업으로 도약",
    
    "추진방안 1 : 사용자 온라인 수요조사 수행 ": "1. 고가의 LiDAR 및 스테레오 비전을 대체하는 4D 이미징 레이더 딥러닝 모델(RAPA-RC) 기반 글로벌 자율주행 시장 공략",
    "추진방안 2 : 용역 공고를 통한 UI/UX 경험을 가진 전문 업체의 선정": "2. 국방 및 해양 무인화 사업 수주: LIG Nex1 등과 국방 무인수상정 및 무인전투차량 인지 시스템 공급 전력화",
    "추진방안 3 : 2024년도까지 시스템 오픈을 위한 일정 준수": "3. 딥러닝 기술 기반 에비던스 팩(Evidence Pack)을 통한 글로벌 안전 규제 선제 대응 및 반복적 소프트웨어 매출 기반 마련",
    
    "내용1": "하드웨어·소프트웨어 통합 레퍼런스 실증(PoC) 고도화 및 글로벌 고객사(BMW, 혼다 등)에 양산 라인 단계적 포팅",
    "내용2": "유럽 현지 연구소(거점) 설립을 통한 현지 고객 밀착 지원 체계 구축 및 3만 건(30K) 4D 레이더 실차 데이터셋 조기 달성",
    
    "수요조사 : 00억원 ": "유럽 연구소 운영 및 글로벌 R&D 연구 인력 확충 : 25억원",
    "시스템개발 : 00억원 ": "B2B 상용화용 4D 인지 솔루션 및 신규 알고리즘 (RAPA-RL/RC) 고도화 : 15억원",
    "시스템 안정화 : 00억원": "제어기(Fusion ECU) 양산 조립 검사 라인 및 실차 검증 인프라 구축 : 10억원",
    
    "OO부서의 협력 필요 ": "1. 원활한 글로벌 현지 실도로 주행 파일럿 테스트를 위한 테스트 차량 배차 및 로깅 인프라 지원 요청",
    "환율 문제로 인한 리스크 대응 필요 ": "2. 국방 파트너사(LIG Nex1 등) 연계 해상 시험평가 인허가 및 보안 행정 처리 우선 지원",
    "서비스 오픈을 위한 일정 준수 필요": "3. 해외 진출을 위한 Euro NCAP, ISO 안전 기준 컴플라이언스 사전 검토(법무) 협조"
}

try:
    hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    hwp.XHwpWindows.Item(0).Visible = False

    hwp.Open(path_template, "HWP", "force:True")
    
    def replace_text(find_str, replace_str):
        hwp.HAction.GetDefault("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
        hwp.HParameterSet.HFindReplace.FindString = find_str
        hwp.HParameterSet.HFindReplace.ReplaceString = replace_str
        hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
        hwp.HAction.Execute("AllReplace", hwp.HParameterSet.HFindReplace.HSet)
    
    for old_text, new_text in replace_dict.items():
        replace_text(old_text, new_text)

    act_save = hwp.CreateAction("FileSaveAs_S")
    pset_save = act_save.CreateSet()
    act_save.GetDefault(pset_save)
    pset_save.SetItem("FileName", output_path)
    pset_save.SetItem("Format", "HWP")
    act_save.Execute(pset_save)

    hwp.Quit()
    print("새 보고서 양식 내용 채우기 완료!")

except Exception as e:
    traceback.print_exc()
    try: hwp.Quit()
    except: pass
