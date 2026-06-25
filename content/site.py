# 구구 마사지 — 서울 전문 출장마사지·홈타이 안내 사이트 공통 설정

BASE_URL = "https://gugu-home-massage.pages.dev"

BRAND = "구구 마사지"
BRAND_MARK = "구"
PHONE = "0508-202-4719"
PHONE_DISPLAY = "0508-202-4719"

# 제작·제휴 문의용 텔레그램 (푸터 오렌지 버튼)
TELEGRAM_URL = "https://t.me/googleseolab"

AREA_SERVED = "서울특별시"

# 검색엔진 사이트 소유확인(메인 페이지 head에 출력)
NAVER_SITE_VERIFICATION = "e05c653caabdf0bef44983b1033eb3c140ae211a"
GOOGLE_SITE_VERIFICATION = ""  # 구글 서치콘솔 HTML 태그 값(있으면 입력)

# IndexNow(빙·네이버 등 즉시 색인 통보) 키 — /{KEY}.txt 로 루트에 게시됨
INDEXNOW_KEY = "1e68090fb402a093772d9666cadfd172"

# 푸터 '주요 지역 바로가기' — 전 페이지 → 핵심 생활권으로의 내부링크(롱테일, 과도하지 않게 큐레이션)
FOOTER_QUICK = [
    ("강남·역삼 출장마사지", "/seoul/life/gangnam-yeoksam/"),
    ("잠실·송파 홈타이", "/seoul/life/jamsil-songpa/"),
    ("홍대·합정 출장마사지", "/seoul/life/hongdae-hapjeong/"),
    ("여의도·영등포 홈타이", "/seoul/life/yeouido-yeongdeungpo/"),
    ("성수·왕십리 출장마사지", "/seoul/life/seongsu-wangsimni/"),
    ("건대·광진 홈타이", "/seoul/life/kondae-gwangjin/"),
    ("용산·서울역 출장마사지", "/seoul/life/yongsan-seoul-station/"),
    ("신림·관악 홈타이", "/seoul/life/sillim-gwanak/"),
    ("종로·광화문 출장마사지", "/seoul/life/jongno-gwanghwamun/"),
    ("명동·을지로 홈타이", "/seoul/life/myeongdong-euljiro/"),
]

# 상단 메뉴 — 키워드("출장마사지") 반복 없음, 지역·역·생활권 명칭만 표시
NAV = [
    ("서울", "/", []),
    ("행정구 안내", "/seoul/area/", [
        ("강남구", "/seoul/gangnam-gu/"),
        ("서초구", "/seoul/seocho-gu/"),
        ("송파구", "/seoul/songpa-gu/"),
        ("마포구", "/seoul/mapo-gu/"),
        ("영등포구", "/seoul/yeongdeungpo-gu/"),
        ("용산구", "/seoul/yongsan-gu/"),
        ("성동구", "/seoul/seongdong-gu/"),
        ("광진구", "/seoul/gwangjin-gu/"),
        ("관악구", "/seoul/gwanak-gu/"),
        ("강서구", "/seoul/gangseo-gu/"),
        ("전체 25개 구 보기", "/seoul/area/"),
    ]),
    ("행정동 안내", "/seoul/area/", [
        ("역삼동", "/seoul/gangnam-gu/yeoksam-dong/"),
        ("논현동", "/seoul/gangnam-gu/nonhyeon-dong/"),
        ("잠실동", "/seoul/songpa-gu/jamsil-dong/"),
        ("서교동", "/seoul/mapo-gu/seogyo-dong/"),
        ("여의도동", "/seoul/yeongdeungpo-gu/yeouido-dong/"),
        ("성수동", "/seoul/seongdong-gu/seongsu-dong/"),
        ("한남동", "/seoul/yongsan-gu/hannam-dong/"),
        ("서초동", "/seoul/seocho-gu/seocho-dong/"),
    ]),
    ("지하철역 안내", "/seoul/station/", [
        ("강남역", "/seoul/station/gangnam-station/"),
        ("잠실역", "/seoul/station/jamsil-station/"),
        ("홍대입구역", "/seoul/station/hongik-univ-station/"),
        ("여의도역", "/seoul/station/yeouido-station/"),
        ("건대입구역", "/seoul/station/kondae-station/"),
        ("성수역", "/seoul/station/seongsu-station/"),
        ("용산역", "/seoul/station/yongsan-station/"),
        ("전체 역 보기", "/seoul/station/"),
    ]),
    ("생활권 안내", "/seoul/life/", [
        ("강남·역삼", "/seoul/life/gangnam-yeoksam/"),
        ("잠실·송파", "/seoul/life/jamsil-songpa/"),
        ("홍대·합정", "/seoul/life/hongdae-hapjeong/"),
        ("여의도·영등포", "/seoul/life/yeouido-yeongdeungpo/"),
        ("성수·왕십리", "/seoul/life/seongsu-wangsimni/"),
        ("용산·서울역", "/seoul/life/yongsan-seoul-station/"),
        ("전체 생활권 보기", "/seoul/life/"),
    ]),
    ("예약 안내", "/reservation/", []),
    ("이용 전 확인사항", "/check/", []),
    ("고객센터", "/support/", [
        ("이용 후기", "/reviews/"),
        ("홈타이 이용 가이드", "/guide/"),
        ("개인정보처리방침", "/support/privacy/"),
    ]),
]
