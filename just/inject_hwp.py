import win32com.client
import os
import traceback

path_b = r'C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\KIAT_스케일업\(참고)(서식01) 스케일업 기술사업화 프로그램 연구개발계획서_접수번호(주관연구개발기관명).hwp'
output_path = r'C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\Marketing_Team\just\연구개발계획서_양식적용본.hwp'

content_dict = {
    "(1) 보유기술 개요": "딥퓨전에이아이(DeepFusion AI)는 기존 3D 레이더의 한계를 극복하기 위해 안테나 개수를 늘려 고비용의 LiDAR 수준에 필적하는 수많은 포인트 클라우드(Point Cloud)를 출력하는 '4D 이미징 레이더' 기술을 세계 최초 상용화 수준으로 보유하고 있습니다. RAPA(Real-time Attention-based Pillar Architecture) 기술은 전파계 인지 실시간 딥러닝 기술로 CES 2026 최고 혁신상(Best of Innovation)을 수상하였습니다.",
    "(2) 국내외 시장 및 기술동향": "글로벌 자동차 시장의 규제(UN R152, Euro NCAP, ISO 21448)가 악천후 및 열악한 환경에서의 다중 센서 인지를 강제하는 방향으로 급격히 강화되고 있습니다. 미국, 중동, 유럽을 중심으로 로봇택시 및 무인 모빌리티 상용화가 촉진됨에 따라, 고신뢰 인지 센서에 대한 폭발적인 수요가 발생하고 있습니다.",
    "(4) 추가기술개발 주요내용": "기존의 카메라 단독(Vision-only) 기술은 심한 안개, 폭우 등 환경에서 한계가 명확하므로, 다중 레이더와 카메라의 초기 융합(Early Fusion) 모델을 최적화하고 실차 검증을 통해 시스템 단가를 혁신적으로 낮춥니다.",
    "(2) 목표 및 핵심경쟁요인": "고가의 LiDAR 센서를 RAPA-R 및 RAPA-RC 기반 인지 시스템으로 대체하여 시스템 단가를 낮추고 신뢰도를 극대화합니다. 초기 1년 내 로보택시 자율주행 양산 설계를 완료하고 3년 내 승용차 부분 자율주행 시장 진입을 목표로 합니다.",
    "(3) 추가기술개발 및 사업화 성공시 예상되는 파급효과": "OEM 및 Tier 1 부품사의 가격 경쟁력을 극대화하여 다양한 보급형 차량 및 로봇택시, 해양 방산 분야에 저비용 고성능 자율주행 시스템 도입을 가속화합니다.",
    "(1) 시장현황 및 전망": "글로벌 자율주행 인식 기술은 Vision-only에서 한계를 느끼고 Multi-modal로 진화 중이며, 로봇택시 산업 성장으로 인해 극한 환경에서도 높은 신뢰도를 보장하는 전파계열 딥러닝 인지 센서의 수요가 증가하고 있습니다.",
    "(1) 주요고객 분석": "국방/방산: LIG Nex1 및 방위사업청을 통한 무인수상정, 무인전투차량 시장 진입. \n민수/모빌리티: 중국 GAC(광저우자동차), BMW, 현대모비스 등 글로벌 OEM 및 Tier1과 POC 진행 및 공급.",
}

try:
    hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    hwp.XHwpWindows.Item(0).Visible = False

    # Open with specific format and args to avoid parameter error
    hwp.Open(path_b, "HWP", "force:True")
    
    # Init FindReplace
    hwp.HAction.GetDefault("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
    hwp.HParameterSet.HFindReplace.IgnoreMessage = 1
    hwp.HParameterSet.HFindReplace.Direction = hwp.FindDir("Forward")
    
    for heading, text_to_insert in content_dict.items():
        hwp.HAction.Run("MoveDocBegin")
        hwp.HParameterSet.HFindReplace.FindString = heading
        res = hwp.HAction.Execute("RepeatFind", hwp.HParameterSet.HFindReplace.HSet)
        
        if res:
            # Found the heading, move to the end of this line
            hwp.HAction.Run("MoveLineEnd")
            hwp.HAction.Run("BreakPara") # Enter
            
            # Insert text
            act_insert = hwp.CreateAction("InsertText")
            pset_insert = act_insert.CreateSet()
            act_insert.GetDefault(pset_insert)
            pset_insert.SetItem("Text", text_to_insert)
            act_insert.Execute(pset_insert)
            print(f"Inserted under: {heading}")
        else:
            print(f"Heading not found: {heading}")

    act_save = hwp.CreateAction("FileSaveAs_S")
    pset_save = act_save.CreateSet()
    act_save.GetDefault(pset_save)
    pset_save.SetItem("FileName", output_path)
    pset_save.SetItem("Format", "HWP")
    act_save.Execute(pset_save)

    hwp.Quit()
    print("HWP 양식적용본 생성 완료!")

except Exception as e:
    traceback.print_exc()
    try: hwp.Quit()
    except: pass
