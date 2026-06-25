# -*- coding: utf-8 -*-
"""페이지 조립.

seoul_data + generate 로 행정구·행정동·역세권·생활권 페이지를 만들고,
main / info 페이지를 합쳐 PAGES 리스트를 구성한다.

색인 정책(지시서 1차/2차 단계 색인):
  - priority == 1 → 색인(index)
  - priority >= 2 → 빌드하되 noindex(DB 보관/draft 단계)
"""
from content import seoul_data as D
from content import generate as G


def _noindex(priority: int) -> bool:
    return priority is not None and priority >= 2


PAGES = []

# ── 메인 ────────────────────────────────────────────────
from content.main import PAGE as MAIN_PAGE  # noqa: E402
PAGES.append(MAIN_PAGE)


# ── 행정구 안내 인덱스 ──────────────────────────────────
def _area_index():
    cards = ""
    for g in D.GU:
        cards += (
            f'<a class="card" href="/seoul/{g["slug"]}/"><h3>{g["name"]}</h3>'
            f'<p>{g["trait"]} 자치구</p>'
            f'<span class="card-arrow">자세히 보기 →</span></a>'
        )
    body = (
        "<section><p>서울특별시 25개 자치구별 방문 가능 지역을 안내합니다. "
        "구구 마사지는 서울 전지역을 대상으로 출장마사지·홈타이 방문 관리를 "
        "안내하며, 행정구 → 행정동 → 지하철역 → 생활권 순으로 위치를 좁혀가며 "
        "확인할 수 있도록 구성했습니다.</p></section>"
        f'<section><h2>서울 25개 행정구</h2><div class="card-grid">{cards}</div></section>'
        "<section><h2>행정구 안내를 보는 방법</h2>"
        "<p>각 구 페이지는 대표 행정동, 가까운 지하철역, 생활권을 함께 정리해 "
        "방문 예약 전 위치를 빠르게 확인할 수 있도록 했습니다. 행정구만으로 위치가 "
        "분명하지 않을 때는 생활권 안내를, 가까운 역을 알고 있다면 지하철역 안내를 "
        "함께 이용하면 동선이 정확해집니다.</p>"
        + G.pricing_block()
        + G.check_block("서울 전지역")
        + G.faq_block([
            ("서울 어느 구까지 방문 가능한가요?",
             "서울 25개 자치구 전역과 인접 생활권까지 방문 상담이 가능합니다. "
             "정확한 주소와 건물 출입 방식을 알려주시면 도착 시간을 안내해 드립니다."),
            ("행정구·행정동·생활권 페이지는 어떻게 다른가요?",
             "행정구는 구 전체 개요와 생활권 허브, 행정동은 가까운 역·인접 동 중심의 "
             "위치 안내, 생활권은 실제 사용자가 부르는 권역 단위 안내입니다."),
            ("예약은 어떻게 하나요?",
             '<a href="tel:0508-202-4719">0508-202-4719</a> 전화 또는 '
             '<a href="/reservation/">예약 안내</a> 절차를 참고하세요.'),
        ])
    )
    return {
        "path": "seoul/area/",
        "title": "서울 행정구 안내｜강남·송파·마포 등 25개 구 출장마사지·홈타이",
        "desc": "서울 25개 행정구별 출장마사지·홈타이 방문 가능 지역과 생활권을 확인하세요.",
        "h1": "서울 행정구별 출장마사지 · 홈타이 안내",
        "breadcrumb": [("행정구 안내", None)],
        "body": body,
    }


PAGES.append(_area_index())

# ── 행정구 + 행정동 ────────────────────────────────────
for g in D.GU:
    gbody, gfaq = G.gu_body(g)
    life_names = "·".join(la.replace("·", "") for la in g["life_areas"][:3]) or g["name"]
    PAGES.append({
        "path": f"seoul/{g['slug']}/",
        "title": f"{g['name']} 출장마사지｜{life_names} 생활권 홈타이 안내",
        "desc": f"{g['name']} 출장마사지·홈타이 예약 전 대표 행정동과 가까운 역, 생활권을 확인하세요.",
        "h1": f"{g['name']} 출장마사지 · 홈타이 지역 안내",
        "area_name": g["name"],
        "breadcrumb": [("행정구 안내", "/seoul/area/"), (g["name"], None)],
        "body": gbody,
        "faq": gfaq,
        "noindex": _noindex(g.get("priority", 1)),
    })
    for dn in g["dongs"]:
        dbody, dfaq = G.dong_body(g, dn)
        near = "·".join(dn.get("nearby_stations", [])[:2]) or dn.get("life_area", g["name"])
        PAGES.append({
            "path": f"seoul/{g['slug']}/{dn['slug']}/",
            "title": f"{dn['name']} 출장마사지｜{near} 생활권 홈타이 안내",
            "desc": f"{g['name']} {dn['name']} 출장마사지·홈타이 방문 전 가까운 역과 인접 동을 확인하세요.",
            "h1": f"{dn['name']} 출장마사지 · 홈타이 안내",
            "area_name": dn["name"],
            "breadcrumb": [("행정구 안내", "/seoul/area/"),
                           (g["name"], f"/seoul/{g['slug']}/"),
                           (dn["name"], None)],
            "body": dbody,
            "faq": dfaq,
            "noindex": _noindex(dn.get("priority", 1)),
        })


# ── 지하철역 인덱스 ────────────────────────────────────
def _station_index():
    cards = ""
    for s in D.STATIONS:
        if s.get("priority", 1) != 1:
            continue  # 핵심(1차) 역만 카드로, 2차 확장 역은 아래 노선도에서 안내
        lines = ", ".join(s.get("lines", []))
        cards += (
            f'<a class="card" href="/seoul/station/{s["slug"]}/"><h3>{s["name"]}</h3>'
            f'<p>{lines}</p>'
            f'<span class="card-arrow">자세히 보기 →</span></a>'
        )

    # 서울 지하철 1~9호선 + 그 외 전 노선별 역 안내(접기/펼치기 노선도)
    by_line = {}
    for s in D.STATIONS:
        for ln in s.get("lines", []):
            by_line.setdefault(ln, []).append(s)
    line_rows = ""
    for i, ln in enumerate(G.LINE_ORDER):
        sts = by_line.get(ln, [])
        if sts:
            links = " · ".join(
                f'<a href="/seoul/station/{s["slug"]}/">{s["name"]}</a>' for s in sts
            )
        else:
            links = '<span class="line-empty">해당 노선 역세권은 순차 추가 예정</span>'
        # 1~3호선은 기본 펼침, 나머지는 접힘
        opened = " open" if i < 3 else ""
        line_rows += (
            f'<details class="line-acc"{opened}><summary>'
            f'{G.line_chip(ln)}<span class="line-count">역 {len(sts)}곳</span>'
            f'<span class="line-toggle" aria-hidden="true"></span></summary>'
            f'<div class="line-stations">{links}</div></details>'
        )
    line_map = (
        '<section><h2>서울 지하철 노선별 역 안내 (1~9호선)</h2>'
        '<p>서울 지하철 1호선부터 9호선까지, 그리고 신분당선·경의중앙선·공항철도 등 '
        '주요 노선을 노선별로 펼쳐 볼 수 있습니다. 노선 제목을 누르면 해당 노선의 역 '
        '목록이 열립니다. 환승역은 노선마다 중복 표시되며, 실제 방문은 역이 아니라 '
        '건물 주소를 기준으로 진행됩니다.</p>'
        f'<div class="line-map">{line_rows}</div></section>'
    )

    body = (
        "<section><p>서울 주요 지하철역별 방문 가능 지역을 안내합니다. 역명 기준으로 "
        "한 페이지씩 정리했으며, 환승역도 노선·출구별로 나누지 않고 한곳에서 인접 "
        "행정동과 생활권을 확인할 수 있도록 했습니다.</p></section>"
        f'<section><h2>서울 핵심 지하철역</h2><div class="card-grid">{cards}</div></section>'
        "<section><h2>역세권 안내를 보는 방법</h2>"
        "<p>가까운 지하철역을 알고 있다면 역 페이지에서 인접 행정동과 생활권을 바로 "
        "확인할 수 있습니다. 실제 방문은 역이 아니라 건물 주소를 기준으로 진행되므로, "
        "예약 시 자택·오피스텔·호텔의 정확한 주소를 함께 알려주시면 됩니다.</p></section>"
        + line_map
        + G.pricing_block()
        + G.check_block("지하철역 인근")
        + G.faq_block([
            ("환승역은 노선별로 안내가 다른가요?",
             "아니요. 강남역·잠실역·왕십리역 같은 환승역도 역명 기준 한 페이지로 "
             "안내하며, 출구별로 페이지를 나누지 않습니다."),
            ("역 이름만 알아도 예약이 되나요?",
             "역은 위치를 좁히는 기준일 뿐이며, 실제 방문은 건물 주소가 필요합니다. "
             "가까운 역과 함께 자택·숙소 주소를 알려주시면 됩니다."),
            ("심야에도 가능한가요?",
             '연중무휴 24시간 상담을 받습니다. 자세한 내용은 '
             '<a href="/reservation/">예약 안내</a>를 참고하세요.'),
        ])
    )
    return {
        "path": "seoul/station/",
        "title": "서울 지하철역 안내｜강남·잠실·홍대입구역 출장마사지·홈타이",
        "desc": "서울 주요 지하철역별 출장마사지·홈타이 방문 가능 지역과 인접 동을 확인하세요.",
        "h1": "서울 지하철역별 출장마사지 · 홈타이 안내",
        "breadcrumb": [("지하철역 안내", None)],
        "body": body,
    }


PAGES.append(_station_index())

for s in D.STATIONS:
    sbody, sfaq = G.station_body(s)
    near = "·".join(s.get("nearby_dongs", [])[:2]) or "인접 생활권"
    PAGES.append({
        "path": f"seoul/station/{s['slug']}/",
        "title": f"{s['name']} 출장마사지｜{near} 생활권 홈타이 안내",
        "desc": f"{s['name']} 출장마사지·홈타이 예약 전 인접 행정동과 생활권을 확인하세요.",
        "h1": f"{s['name']} 출장마사지 · 홈타이 안내",
        "area_name": s["name"],
        "breadcrumb": [("지하철역 안내", "/seoul/station/"), (s["name"], None)],
        "body": sbody,
        "faq": sfaq,
        "noindex": _noindex(s.get("priority", 1)),
    })


# ── 생활권 인덱스 ──────────────────────────────────────
def _life_index():
    cards = ""
    for l in D.LIFE:
        cards += (
            f'<a class="card" href="/seoul/life/{l["slug"]}/"><h3>{l["name"]}</h3>'
            f'<p>{l["role"]}</p>'
            f'<span class="card-arrow">자세히 보기 →</span></a>'
        )
    body = (
        "<section><p>서울은 행정구·행정동만으로는 검색 의도를 모두 담기 어렵습니다. "
        "강남·역삼, 홍대·합정, 여의도·영등포처럼 실제 사용자가 부르는 생활권 단위로 "
        "행정구·행정동·역세권을 연결해 방문 동선을 안내합니다.</p></section>"
        f'<section><h2>서울 핵심 생활권</h2><div class="card-grid">{cards}</div></section>'
        "<section><h2>생활권 안내를 보는 방법</h2>"
        "<p>생활권 페이지는 구 페이지와 역 페이지 사이를 잇는 허브 역할을 합니다. "
        "내가 있는 지역을 행정동으로 부르기 애매할 때, 익숙한 생활권 이름으로 위치를 "
        "잡고 연결된 행정동·역세권으로 좁혀가면 편리합니다. 예를 들어 강남·역삼은 "
        "업무지구와 오피스텔, 홍대·합정은 상권과 숙소, 여의도·영등포는 금융·업무권을 "
        "중심으로 방문 수요가 형성됩니다.</p>"
        + G.pricing_block()
        + G.check_block("생활권 권역")
        + G.faq_block([
            ("생활권은 행정동과 어떻게 다른가요?",
             "행정동은 행정 구역이고, 생활권은 사람들이 실제로 부르는 권역입니다. "
             "강남·역삼처럼 여러 동·역을 묶어 위치를 직관적으로 잡을 수 있습니다."),
            ("어느 생활권까지 방문 가능한가요?",
             "서울 전 생활권과 인접 지역까지 방문 상담이 가능합니다. 정확한 주소를 "
             "알려주시면 도착 시간을 안내해 드립니다."),
            ("예약 절차가 궁금합니다.",
             '<a href="/reservation/">예약 안내</a>에서 단계별 절차를 확인할 수 있습니다.'),
        ])
    )
    return {
        "path": "seoul/life/",
        "title": "서울 생활권 안내｜강남·역삼, 홍대·합정 출장마사지·홈타이",
        "desc": "서울 생활권별 출장마사지·홈타이 안내. 행정구·행정동·역세권을 연결해 드립니다.",
        "h1": "서울 생활권별 출장마사지 · 홈타이 안내",
        "breadcrumb": [("생활권 안내", None)],
        "body": body,
    }


PAGES.append(_life_index())

for l in D.LIFE:
    lbody, lfaq = G.life_body(l)
    PAGES.append({
        "path": f"seoul/life/{l['slug']}/",
        "title": f"{l['name']} 출장마사지｜생활권 홈타이 방문 안내",
        "desc": f"{l['name']} 생활권 출장마사지·홈타이 안내. 연결 행정구·행정동·역을 확인하세요.",
        "h1": f"{l['name']} 출장마사지 · 홈타이 생활권 안내",
        "area_name": l["name"],
        "breadcrumb": [("생활권 안내", "/seoul/life/"), (l["name"], None)],
        "body": lbody,
        "faq": lfaq,
        "noindex": _noindex(l.get("priority", 1)),
    })


# ── 정보 페이지 ────────────────────────────────────────
from content.info import PAGES as INFO_PAGES  # noqa: E402
PAGES.extend(INFO_PAGES)
