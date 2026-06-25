# -*- coding: utf-8 -*-
"""서울 지역 데이터 집합.

- GU: 25개 자치구(각 dongs 중첩) — 배치 모듈에서 취합
- STATIONS: 1차 핵심 역세권
- LIFE: 1차 핵심 생활권(행정구·행정동·역세권을 잇는 허브)
"""
from content._data_gangnam import GU as _GU_GANGNAM
from content._data_c import GU as _GU_C
from content._data_d import GU as _GU_D
from content._data_e import GU as _GU_E
from content._data_f import GU as _GU_F
from content._data_g import GU as _GU_G
from content._data_stations import STATIONS as _STATIONS1
from content._data_stations2 import STATIONS2 as _STATIONS2

STATIONS = _STATIONS1 + _STATIONS2

# 행정구 안내 노출 순서(생활권 비중이 큰 구 우선).
_GU_ORDER = [
    "강남구", "송파구", "마포구", "영등포구", "서초구", "강서구", "구로구",
    "금천구", "관악구", "동작구", "광진구", "성동구", "용산구", "양천구",
    "은평구", "노원구", "중랑구", "종로구", "중구", "강동구", "강북구",
    "도봉구", "동대문구", "서대문구", "성북구",
]

_ALL = (_GU_GANGNAM + _GU_C + _GU_D + _GU_E + _GU_F + _GU_G)
_BY_NAME = {g["name"]: g for g in _ALL}
GU = [_BY_NAME[n] for n in _GU_ORDER if n in _BY_NAME]
# 순서 목록에 없는 구가 있으면 뒤에 덧붙인다(누락 방지).
GU += [g for g in _ALL if g["name"] not in set(_GU_ORDER)]


LIFE = [
    {"slug": "gangnam-yeoksam", "name": "강남·역삼", "priority": 1,
     "role": "업무지구·오피스텔·상권 중심 안내",
     "lead": "테헤란로 업무지구와 오피스텔이 밀집해 평일·심야 가릴 것 없이 방문 수요가 꾸준한 권역입니다.",
     "gu": ["강남구", "서초구"], "dongs": ["역삼동", "논현동", "서초동"],
     "stations": ["강남역", "역삼역", "교대역"]},
    {"slug": "samseong-seolleung", "name": "삼성·선릉", "priority": 1,
     "role": "코엑스·테헤란로 업무·전시 권역 안내",
     "lead": "코엑스와 무역센터를 중심으로 한 업무·전시 권역으로, 비즈니스호텔과 오피스텔 이용이 많습니다.",
     "gu": ["강남구"], "dongs": ["삼성동", "대치동", "역삼동"],
     "stations": ["삼성역", "선릉역"]},
    {"slug": "cheongdam-apgujeong", "name": "청담·압구정", "priority": 1,
     "role": "명품상권·고급주거 권역 안내",
     "lead": "명품거리와 고급 주거가 모인 권역으로, 프라이버시를 중시하는 자택·레지던스 방문 수요가 특징입니다.",
     "gu": ["강남구"], "dongs": ["청담동", "압구정동", "신사동"],
     "stations": ["압구정역", "청담역"]},
    {"slug": "jamsil-songpa", "name": "잠실·송파", "priority": 1,
     "role": "주거·상권·호텔 인접권 안내",
     "lead": "잠실 일대의 대단지 주거와 관광·상권, 호텔이 인접해 자택부터 숙소까지 방문 형태가 다양합니다.",
     "gu": ["송파구"], "dongs": ["잠실동", "석촌동", "방이동", "송파동"],
     "stations": ["잠실역", "석촌역"]},
    {"slug": "munjeong-garak", "name": "문정·가락", "priority": 1,
     "role": "법조타운·물류·업무권 안내",
     "lead": "문정 법조타운과 가락시장을 낀 업무·물류 권역으로, 오피스텔과 비즈니스 숙소 이용이 많습니다.",
     "gu": ["송파구"], "dongs": ["문정동", "가락동", "장지동"],
     "stations": ["문정역", "잠실역"]},
    {"slug": "hongdae-hapjeong", "name": "홍대·합정", "priority": 1,
     "role": "상권·숙소·오피스텔 인접권 안내",
     "lead": "홍대·합정·연남으로 이어지는 상권과 게스트하우스·오피스텔이 밀집해 방문 동선이 촘촘한 권역입니다.",
     "gu": ["마포구"], "dongs": ["서교동", "합정동", "연남동", "망원동"],
     "stations": ["홍대입구역", "합정역"]},
    {"slug": "gongdeok-mapo", "name": "공덕·마포", "priority": 1,
     "role": "업무·주거 혼합권 안내",
     "lead": "공덕 환승권을 중심으로 업무지구와 주거가 섞여 있어 출퇴근 동선과 방문 수요가 함께 움직입니다.",
     "gu": ["마포구"], "dongs": ["공덕동", "아현동", "도화동"],
     "stations": ["공덕역", "홍대입구역"]},
    {"slug": "yeouido-yeongdeungpo", "name": "여의도·영등포", "priority": 1,
     "role": "금융·업무·상권 중심 안내",
     "lead": "여의도 금융업무지구와 영등포 상권이 맞물려, 평일 업무권과 주말 상권 수요가 뚜렷이 나뉩니다.",
     "gu": ["영등포구"], "dongs": ["여의도동", "영등포동", "당산동"],
     "stations": ["여의도역", "영등포역", "당산역"]},
    {"slug": "mullae-dangsan", "name": "문래·당산", "priority": 1,
     "role": "창작촌·주거·업무 혼합권 안내",
     "lead": "문래 창작촌과 당산 주거·업무가 어우러진 권역으로, 오피스텔과 신축 주거 단지 이용이 늘고 있습니다.",
     "gu": ["영등포구"], "dongs": ["문래동", "당산동", "양평동"],
     "stations": ["당산역", "영등포역"]},
    {"slug": "sillim-gwanak", "name": "신림·관악", "priority": 1,
     "role": "대학가·주거 밀집권 안내",
     "lead": "신림 상권과 대단지 원룸·주거가 밀집한 권역으로, 1인 가구와 자택 방문 수요가 두드러집니다.",
     "gu": ["관악구"], "dongs": ["신림동", "봉천동", "남현동"],
     "stations": ["신림역", "서울대입구역"]},
    {"slug": "seoul-natl-univ-bongcheon", "name": "서울대입구·봉천", "priority": 1,
     "role": "대학가·주거권 안내",
     "lead": "서울대입구·봉천 일대의 대학가와 주거 밀집 지역으로, 합리적 동선의 자택 방문 수요가 많습니다.",
     "gu": ["관악구"], "dongs": ["봉천동", "신림동"],
     "stations": ["서울대입구역", "신림역"]},
    {"slug": "kondae-gwangjin", "name": "건대·광진", "priority": 1,
     "role": "대학가·상권·숙박권 안내",
     "lead": "건대 상권과 자양·구의 주거가 이어진 권역으로, 대학가 숙소부터 오피스텔까지 방문 형태가 다양합니다.",
     "gu": ["광진구"], "dongs": ["화양동", "자양동", "구의동"],
     "stations": ["건대입구역", "구의역"]},
    {"slug": "guro-gasan-digital", "name": "구디·가디", "priority": 1,
     "role": "IT·업무단지권 안내",
     "lead": "구로·가산 디지털단지를 낀 IT 업무권으로, 오피스텔과 비즈니스 숙소의 야간·주말 수요가 특징입니다.",
     "gu": ["구로구", "금천구"], "dongs": ["구로동", "가산동", "독산동"],
     "stations": ["구로디지털단지역", "가산디지털단지역"]},
    {"slug": "seongsu-wangsimni", "name": "성수·왕십리", "priority": 1,
     "role": "IT·카페상권·주거권 안내",
     "lead": "성수 카페·IT 상권과 왕십리 환승 주거권이 맞닿아, 신축 오피스텔과 자택 방문 수요가 함께 늡니다.",
     "gu": ["성동구"], "dongs": ["성수동", "행당동", "옥수동"],
     "stations": ["성수역", "왕십리역", "서울숲역"]},
    {"slug": "yongsan-seoul-station", "name": "용산·서울역", "priority": 1,
     "role": "교통허브·업무·숙박권 안내",
     "lead": "용산·서울역 교통 허브를 중심으로 업무·숙박 시설이 밀집해, 호텔·레지던스 방문 수요가 두드러집니다.",
     "gu": ["용산구", "중구"], "dongs": ["한강로동", "이촌동", "후암동"],
     "stations": ["용산역", "서울역"]},
    {"slug": "hannam-itaewon", "name": "한남·이태원", "priority": 1,
     "role": "상권·고급주거·숙박권 안내",
     "lead": "이태원 상권과 한남 고급 주거가 어우러진 권역으로, 외국인 방문객과 레지던스 이용이 많은 편입니다.",
     "gu": ["용산구"], "dongs": ["한남동", "이태원동", "보광동"],
     "stations": ["이태원역", "한강진역"]},
    {"slug": "mokdong-yangcheon", "name": "목동·양천", "priority": 1,
     "role": "주거·학원가권 안내",
     "lead": "목동 대단지 주거와 학원가가 중심인 권역으로, 가족 단위 자택 방문 수요가 안정적으로 이어집니다.",
     "gu": ["양천구"], "dongs": ["목동", "신정동", "신월동"],
     "stations": ["목동역", "오목교역"]},
    {"slug": "yeonsinnae-eunpyeong", "name": "연신내·은평", "priority": 1,
     "role": "주거·환승상권권 안내",
     "lead": "연신내 환승 상권과 은평 주거 단지가 이어진 권역으로, 아파트·주택 자택 방문 수요가 꾸준합니다.",
     "gu": ["은평구"], "dongs": ["불광동", "응암동", "역촌동"],
     "stations": ["연신내역", "불광역"]},
    {"slug": "nowon-sanggye", "name": "노원·상계", "priority": 1,
     "role": "주거·학원·상권권 안내",
     "lead": "상계·중계 대단지 주거와 학원가, 노원 상권이 묶인 권역으로 가족 단위 자택 방문 수요가 많습니다.",
     "gu": ["노원구"], "dongs": ["상계동", "중계동", "하계동"],
     "stations": ["노원역", "상계역"]},
    {"slug": "sangbong-jungnang", "name": "상봉·중랑", "priority": 1,
     "role": "환승·주거·상권권 안내",
     "lead": "상봉 환승역과 면목·망우 주거권이 이어진 권역으로, 주거 밀집 지역의 자택 방문 수요가 특징입니다.",
     "gu": ["중랑구"], "dongs": ["상봉동", "면목동", "망우동"],
     "stations": ["상봉역", "면목역"]},
    {"slug": "jongno-gwanghwamun", "name": "종로·광화문", "priority": 1,
     "role": "도심업무·관광권 안내",
     "lead": "광화문 업무지구와 종로 관광·상권이 맞물린 도심 권역으로, 호텔·오피스텔 방문 수요가 뚜렷합니다.",
     "gu": ["종로구"], "dongs": ["혜화동", "창신동", "청운효자동"],
     "stations": ["종로3가역", "광화문역"]},
    {"slug": "myeongdong-euljiro", "name": "명동·을지로", "priority": 1,
     "role": "도심상권·관광·숙박권 안내",
     "lead": "명동 관광 상권과 을지로 업무·인쇄 골목이 인접한 도심 권역으로, 호텔·숙소 방문 수요가 많습니다.",
     "gu": ["중구"], "dongs": ["명동", "을지로동", "신당동"],
     "stations": ["명동역", "을지로입구역"]},
]
