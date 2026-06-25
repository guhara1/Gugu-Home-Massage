# -*- coding: utf-8 -*-
"""서울 메인 페이지."""
import json

from content import seoul_data as D
from content import generate as G
from content.site import BASE_URL, BRAND, PHONE

BASE = BASE_URL.rstrip("/")


def _hero():
    return """<section class="hero">
  <div class="hero-content">
    <span class="hero-badge">서울 전지역 방문 관리 · 24시간 상담</span>
    <h1 class="hero-title">서울 <span class="hero-accent">출장마사지</span> · 서울 홈타이<br>지역별 예약 안내</h1>
    <p class="hero-lead">서울 25개 행정구, 주요 행정동, 지하철역, 생활권별 방문 가능 지역과
    예약 전 확인사항을 안내합니다. 위치를 좁혀가며 빠르게 확인하세요.</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="/seoul/area/">행정구 찾기</a>
      <a class="btn btn-secondary" href="/seoul/gangnam-gu/yeoksam-dong/">행정동 찾기</a>
      <a class="btn btn-secondary" href="/seoul/station/">지하철역 찾기</a>
      <a class="btn btn-secondary" href="/seoul/life/">생활권 찾기</a>
      <a class="btn btn-secondary" href="/reservation/">예약 안내 보기</a>
    </div>
    <div class="hero-stats">
      <div class="stat"><div class="stat-number">25</div><div class="stat-label">행정구</div></div>
      <div class="stat"><div class="stat-number">46+</div><div class="stat-label">핵심 역세권</div></div>
      <div class="stat"><div class="stat-number">22</div><div class="stat-label">생활권</div></div>
      <div class="stat"><div class="stat-number">24h</div><div class="stat-label">상담 가능</div></div>
    </div>
  </div>
</section>
"""


def _gu_cards(limit=12):
    cards = ""
    for g in D.GU[:limit]:
        cards += (
            f'<a class="card" href="/seoul/{g["slug"]}/"><h3>{g["name"]}</h3>'
            f'<p>{g["trait"]} 자치구</p>'
            f'<span class="card-arrow">자세히 보기 →</span></a>'
        )
    return cards


def _station_cards(names):
    cards = ""
    for s in D.STATIONS:
        if s["name"] in names:
            cards += (
                f'<a class="card" href="/seoul/station/{s["slug"]}/"><h3>{s["name"]}</h3>'
                f'<p>{", ".join(s.get("lines", []))}</p>'
                f'<span class="card-arrow">자세히 보기 →</span></a>'
            )
    return cards


def _life_cards(limit=8):
    cards = ""
    for l in D.LIFE[:limit]:
        cards += (
            f'<a class="card" href="/seoul/life/{l["slug"]}/"><h3>{l["name"]}</h3>'
            f'<p>{l["role"]}</p>'
            f'<span class="card-arrow">자세히 보기 →</span></a>'
        )
    return cards


FAQ = [
    ("서울 어느 지역까지 방문 가능한가요?",
     "서울 25개 자치구 전역과 인접 생활권까지 방문 상담이 가능합니다. 정확한 주소와 "
     "건물 출입 방식을 알려주시면 도착 시간을 안내해 드립니다."),
    ("행정구·행정동·역세권·생활권 페이지는 어떻게 다른가요?",
     "행정구는 구 전체 개요와 생활권 허브, 행정동은 가까운 역·인접 동 중심 안내, "
     "역세권은 역명 기준 인접 지역 안내, 생활권은 실제 사용자가 부르는 권역 안내입니다."),
    ("환승역은 노선·출구별로 페이지가 따로 있나요?",
     "아니요. 강남역·잠실역·왕십리역 같은 환승역도 역명 기준 한 페이지로 안내하며, "
     "출구별 페이지는 만들지 않습니다."),
    ("예약은 어떻게 하나요?",
     '<a href="tel:0508-202-4719">0508-202-4719</a> 전화 또는 '
     '<a href="/reservation/">예약 안내</a> 페이지의 절차를 참고하시면 됩니다. '
     "연중무휴 24시간 상담을 받습니다."),
    ("불법·선정적 서비스도 가능한가요?",
     "불가능합니다. 구구 마사지는 건전한 방문 관리 서비스만 운영하며, 안내된 관리 "
     "범위와 위생·안전 기준을 벗어난 요청에는 어떤 경우에도 응하지 않습니다."),
]


def _body():
    parts = []
    parts.append(
        "<section><h2>서울에서 출장마사지를 찾을 때 먼저 확인할 기준</h2>"
        "<p>서울은 행정구·행정동·지하철역·생활권 검색 의도가 함께 움직이는 도시입니다. "
        "강남구는 강남역·역삼·삼성·청담 중심, 송파구는 잠실·문정·가락 중심, 마포구는 "
        "홍대·합정·공덕, 영등포구는 여의도·영등포·당산, 관악구는 신림·서울대입구 중심으로 "
        "방문 수요가 형성됩니다. 그래서 구구 마사지는 행정구·행정동·역세권·생활권 페이지를 "
        "나누되, 같은 본문을 반복하지 않고 각 지역의 위치와 동선을 고유하게 정리했습니다. "
        "서울 홈타이·방문 마사지를 예약하기 전, 내 위치와 가장 가까운 기준부터 확인하면 "
        "도착 시간과 동선이 정확해집니다.</p></section>"
    )
    parts.append(
        f'<section><h2>서울 25개 행정구별 안내</h2>'
        f"<p>자치구별 대표 행정동·지하철역·생활권을 한곳에 정리했습니다. 전체 25개 구는 "
        f'<a href="/seoul/area/">행정구 안내</a>에서 확인할 수 있습니다.</p>'
        f'<div class="card-grid">{_gu_cards()}</div></section>'
    )
    parts.append(
        "<section><h2>서울 행정동별 방문 가능 지역 안내</h2>"
        "<p>행정동 페이지는 실제 위치를 기준으로 가까운 역과 인접 행정동, 생활권을 "
        "연결합니다. 번호 동은 대표 동으로 묶어 정리했고, 본문은 지역마다 고유하게 "
        "작성했습니다. 예: "
        f'{G.link_dong("역삼동")}은 강남역·테헤란로, '
        f'{G.link_dong("잠실동")}은 잠실역·석촌호수, '
        f'{G.link_dong("서교동")}은 홍대입구역·합정 생활권과 이어집니다.</p></section>'
    )
    parts.append(
        f'<section><h2>서울 주요 지하철역별 안내</h2>'
        f"<p>역명 기준으로 인접 행정동과 생활권을 안내합니다. 환승역도 노선·출구로 "
        f'나누지 않습니다. 전체 역은 <a href="/seoul/station/">지하철역 안내</a>에서 '
        f'확인하세요.</p>'
        f'<div class="card-grid">'
        f'{_station_cards(["강남역","잠실역","홍대입구역","여의도역","건대입구역","성수역","용산역","서울역"])}'
        f'</div></section>'
    )
    parts.append(
        f'<section><h2>서울 생활권별 예약 기준</h2>'
        f"<p>생활권 페이지는 구와 행정동, 역세권을 잇는 허브입니다. 전체 권역은 "
        f'<a href="/seoul/life/">생활권 안내</a>에서 확인할 수 있습니다.</p>'
        f'<div class="card-grid">{_life_cards()}</div></section>'
    )
    parts.append(G.pricing_block())
    parts.append(G.check_block("서울 전지역 자택·오피스텔·호텔·숙소"))
    parts.append(G.faq_block(FAQ))
    return "\n".join(parts)


def _schema():
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "서울 출장마사지｜강남·잠실·홍대·여의도 홈타이 지역 안내",
        "description": "서울 출장마사지·홈타이 예약 전 강남, 잠실, 홍대, 여의도 등 주요 생활권 안내.",
        "url": BASE + "/",
        "inLanguage": "ko",
        "isPartOf": {"@id": BASE + "/#organization"},
        "publisher": {"@id": BASE + "/#organization"},
        "primaryImageOfPage": {
            "@type": "ImageObject",
            "url": BASE + "/assets/og-image.svg",
            "width": 1200, "height": 630,
        },
    }
    breadcrumb = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": BASE + "/"},
        ],
    }
    item_list = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "서울 25개 행정구 안내",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": g["name"],
             "url": BASE + f"/seoul/{g['slug']}/"}
            for i, g in enumerate(D.GU)
        ],
    }
    faqpage = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in FAQ
        ],
    }
    blocks = [webpage, breadcrumb, item_list, faqpage]
    return "".join(
        '<script type="application/ld+json">\n'
        + json.dumps(b, ensure_ascii=False, indent=2)
        + "\n</script>\n"
        for b in blocks
    )


PAGE = {
    "path": "",
    "title": "서울 출장마사지｜강남·잠실·홍대·여의도 홈타이 지역 안내",
    "desc": "서울 출장마사지·홈타이 예약 전 강남, 잠실, 홍대, 여의도 등 주요 생활권을 확인하세요.",
    "h1": "서울 출장마사지 · 서울 홈타이 지역별 예약 안내",
    "hero": _hero(),
    "body": _body(),
    "extra_head": _schema(),
}
