import win32com.client
import os

content = """국가 연구개발사업 신청용 연구개발계획서 (초안)
작성 기준: Source 프로젝트 (Deepfusion AI 핵심 기술 및 IR 자료)

=============================================================================

1. 연구개발의 필요성

(1) 보유기술 개요
딥퓨전에이아이(DeepFusion AI)는 기존 3D 레이더의 한계를 극복하기 위해 안테나 개수를 대폭 늘려 정확한 높이 정보를 추가하고, 고비용의 LiDAR 수준에 필적하는 수많은 포인트 클라우드(Point Cloud)를 출력하는 '4D 이미징 레이더' 기술을 세계 최초 상용화 수준으로 보유하고 있습니다. 
핵심 인지 아키텍처인 RAPA(Real-time Attention-based Pillar Architecture) 기술은 전파계 인지 기술 부문에서 CES 2026 최고 혁신상(Best of Innovation)을 단독 수상하며 그 기술적 우수성을 국제적으로 입증받았습니다.
카메라와 융합하는 RAPA-RC(다중 레이더+카메라) 등 광학계와 전파계 센서의 '초기 융합(Early Fusion)' 모델을 완성하여, 기존 자율주행 센서 체계의 패러다임을 혁신적으로 전환할 수 있는 독보적인 기술을 확보하고 있습니다.

(2) 시장 및 기술동향
글로벌 자동차 시장의 규제(UN R152, Euro NCAP, ISO 21448)가 악천후 및 열악한 환경에서의 다중 센서 인지를 강제하는 방향으로 급격히 강화되고 있습니다. 미국, 중동, 유럽을 중심으로 로봇택시 및 무인 모빌리티 상용화가 촉진됨에 따라, 고신뢰 인지 센서에 대한 폭발적인 수요가 발생하고 있습니다.

(3) 기존 기술의 한계 및 자사 기술의 우위성
기존의 카메라 단독(Vision-only) 기술은 심한 안개, 폭우, 야간 및 역광 환경에서 인식률이 급격히 저하되는 치명적인 한계를 가집니다. 반면, 고가의 LiDAR 센서는 날씨의 영향을 덜 받지만, 양산형 차량에 전면 도입하기에는 단가 및 내구성의 장벽이 존재합니다.
당사의 기술은 다중 레이더의 노이즈 필터링 및 포인트 클라우드 가상화 기술을 통해 값비싼 LiDAR를 '4D 이미징 다중 레이더'로 완벽히 대체할 수 있습니다. 상용화 기준인 IOU 0.7에서 타사 모델(28%~38%)을 압도하는 52%~58%의 mAP 정확도를 달성하며, 세계 유일의 360도 실시간 인지를 실현하였습니다.

=============================================================================

2. 비즈니스모델의 개요

(1) 목표
자율주행 승용차 및 로봇택시의 필수 센서(LiDAR, Stereo Camera)를 당사의 RAPA-R 및 RAPA-RC 기반 인지 시스템으로 전면 대체하여 시스템 단가를 혁신적으로 낮추고 인지 신뢰도를 극대화합니다. 나아가 초기 1년 내 로보택시 완전 자율주행 양산 설계를 완료하고, 3년 내 승용차(고속도로-도심) 부분 자율주행 시장으로 진입하는 것을 목표로 합니다.

(2) 파급효과
고가의 LiDAR 센서 장착 비용을 절감함으로써 자동차 OEM 및 Tier 1 부품사의 가격 경쟁력을 극대화할 수 있습니다. 이로 인해 자율주행 기술의 도입 장벽이 낮아져, 로봇택시 및 대중 무인 셔틀 뿐 아니라 일반 보급형 승용차에서도 고성능 자율주행 인지 기술 탑재가 가능해집니다. 또한 해양 및 국방(무인 수상정 등) 분야로의 파급 확장성을 지니고 있습니다.

(3) 사업화를 위해 확보해야 할 핵심 기술
- 다중 4D 레이더 및 카메라 간의 Early Fusion(초기 결합) 최적화 기술
- 악천후(강우/강설) 환경에서의 AI 딥러닝 인지 정확도 고도화
- 상용화 제어기(ECU) 이식 및 환경, EMC, 진동 시험 통과를 통한 실차 신뢰성 확보
- 기존 고가 센서를 대체하는 다중 레이더 파도 탐지 시스템(해양) 및 무인전투차량 인지 시스템 고도화

=============================================================================

3. 목표 시장 분석 및 기술사업화 전략

(1) 국방 및 특수 모빌리티 선점 전략
딥퓨전에이아이는 LIG Nex1 및 방위사업청을 통해 향후 5년간의 방산 개발 수주 약 39.8억 원(정찰용/전투용 무인수상정, 무인전투차량 통합인지 시스템 등)을 확보하였으며, 2027년까지 300억 원 규모의 누적 수주를 목표로 하고 있습니다. 국방 실증을 통한 'High-Reliability' 레퍼런스를 기반으로 민수용 시장으로의 기술 이전을 가속화합니다.

(2) 글로벌 완성차 및 로보택시 사업화 전략
중국 GAC(광저우자동차)와의 로보택시 제어기 양산 계약 및 POC를 성공적으로 완료했으며, 현재 현대모비스, LIG Nex1 뿐 아니라 BMW, 혼다(Honda), 디디출싱(DiDi) 등 글로벌 Top-tier 완성차 및 모빌리티 업체와 POC 협약을 체결 및 진행 중입니다. 유럽 연구소를 설립하여 글로벌 양산 대응 체계를 조기에 구축할 계획입니다.

(3) 매출 및 IPO 로드맵
위의 확고한 시장 진입 전략을 바탕으로 2026년 매출 110억 원을 달성하여 손익분기점(BEP)을 돌파하고, 2027년에는 매출 612억 원, 영업이익 210억 원 달성을 시현할 것입니다. 압도적인 기술 격차 및 실적을 기반으로 2026~2027년경 성공적인 IPO(기업공개)를 추진하여 글로벌 스케일업을 완성할 계획입니다.
"""

# Save using Python to an actual HWPX file through OLE Automation
output_path = r"C:\Users\KIM SIYE\OneDrive - 딥퓨전에이아이주식회사\바탕 화면\SIYE\Marketing_Team\just\연구개발계획서_NotebookLM_초안.hwp"

try:
    hwp = win32com.client.Dispatch("HWPFrame.HwpObject")
    hwp.RegisterModule("FilePathCheckDLL", "SecurityModule")
    hwp.XHwpWindows.Item(0).Visible = False  # Run in background
    
    # 문서 생성
    hwp.XHwpDocuments.Add(isTab=False)
    
    # 폰트, 크기 등 기본 설정
    hwp.HAction.Run("SelectAll")
    act = hwp.CreateAction("CharShape")
    pset = act.CreateSet()
    act.GetDefault(pset)
    pset.SetItem("Height", 1100)  # 11pt
    pset.SetItem("FaceNameHangul", "맑은 고딕")
    act.Execute(pset)

    # 문자열 입력
    act_insert = hwp.CreateAction("InsertText")
    pset_insert = act_insert.CreateSet()
    act_insert.GetDefault(pset_insert)
    pset_insert.SetItem("Text", content)
    act_insert.Execute(pset_insert)
    
    # 저장 형식 지정 및 저장
    act_save = hwp.CreateAction("FileSaveAs_S")
    pset_save = act_save.CreateSet()
    act_save.GetDefault(pset_save)
    pset_save.SetItem("FileName", output_path)
    pset_save.SetItem("Format", "HWP")
    act_save.Execute(pset_save)
    hwp.Quit()
    print("HWPX document generated successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Failed to generate HWPX: {e}")
    try: hwp.Quit()
    except: pass
