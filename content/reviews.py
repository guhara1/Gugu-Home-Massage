# -*- coding: utf-8 -*-
"""이용 후기 데이터.

⚠️ 중요(구글 정책): 리뷰·평점 구조화 데이터는 사이트에 실제로 표시되는, 진짜
이용자 후기에 근거해야 합니다. 아래는 형식을 보여주는 예시이며, 운영 시에는
실제 수집한 후기로 교체하세요. (허위 평점 마크업은 검색 패널티 사유)

각 후기: author(이름), rating(1~5), date(YYYY-MM-DD), area(이용 지역, 선택), body
"""

REVIEWS = [
    {"author": "김OO", "rating": 5, "date": "2026-05-28", "area": "강남구",
     "body": "예약부터 방문까지 시간 약속이 정확했어요. 자택으로 와주셔서 이동 부담 없이 편하게 받았습니다."},
    {"author": "이OO", "rating": 5, "date": "2026-05-21", "area": "송파구",
     "body": "오피스텔로 방문 요청했는데 출입 안내까지 꼼꼼히 확인해 주셔서 좋았습니다. 90분 코스 만족해요."},
    {"author": "박OO", "rating": 4, "date": "2026-05-14", "area": "마포구",
     "body": "홍대 근처 숙소에서 받았어요. 친절하고 위생적으로 진행해 주셔서 안심됐습니다."},
    {"author": "최OO", "rating": 5, "date": "2026-05-09", "area": "영등포구",
     "body": "여의도 야근 후 늦은 시간에 연락했는데 24시간 상담이 정말 편했어요. 시간대 안내도 정확했습니다."},
    {"author": "정OO", "rating": 5, "date": "2026-04-30", "area": "성동구",
     "body": "성수동 자택으로 방문. 60분 가볍게 받으려 했는데 부위 설명도 잘해주셔서 다음엔 90분 예약하려고요."},
    {"author": "강OO", "rating": 4, "date": "2026-04-22", "area": "용산구",
     "body": "호텔에서 이용했습니다. 추가 비용 없이 안내받은 금액 그대로라 신뢰가 갔어요."},
    {"author": "윤OO", "rating": 5, "date": "2026-04-15", "area": "광진구",
     "body": "건대 근처 오피스텔이었는데 도착 시간 안내가 정확했어요. 응대가 차분하고 전문적이었습니다."},
    {"author": "임OO", "rating": 5, "date": "2026-04-08", "area": "서초구",
     "body": "교대 인근에서 받았어요. 예약 변경도 미리 연락드리니 유연하게 조정해 주셨습니다."},
    {"author": "한OO", "rating": 5, "date": "2026-03-30", "area": "관악구",
     "body": "신림 자택 방문. 처음이라 걱정했는데 확인사항을 미리 알려주셔서 준비가 수월했어요."},
    {"author": "오OO", "rating": 4, "date": "2026-03-22", "area": "노원구",
     "body": "상계동까지 와주셔서 감사했어요. 외곽인데도 동선 안내가 빠르고 깔끔했습니다."},
    {"author": "서OO", "rating": 5, "date": "2026-03-15", "area": "중구",
     "body": "명동 숙소에서 120분 코스 받았습니다. 구석구석 신경 써주셔서 여행 피로가 풀렸어요."},
    {"author": "신OO", "rating": 5, "date": "2026-03-07", "area": "강서구",
     "body": "마곡 오피스텔로 방문 요청. 응대가 친절하고 위생 관리가 꼼꼼해서 재예약했습니다."},
]


def aggregate():
    n = len(REVIEWS)
    avg = round(sum(r["rating"] for r in REVIEWS) / n, 1) if n else 0
    return {"value": avg, "count": n,
            "best": 5, "worst": min((r["rating"] for r in REVIEWS), default=1)}


def shown_for(key, k=3):
    """페이지별로 고르게 분산된 후기 부분집합(결정적). 방문 페이지마다 다른
    후기를 노출하되, 같은 페이지는 항상 같은 후기를 보여 스키마와 일치시킨다."""
    if not REVIEWS:
        return []
    n = len(REVIEWS)
    h = sum(ord(c) for c in str(key))
    k = min(k, n)
    return [REVIEWS[(h + i) % n] for i in range(k)]
