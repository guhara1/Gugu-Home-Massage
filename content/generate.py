# -*- coding: utf-8 -*-
"""데이터 기반 본문 생성기.

seoul_data.py의 구조화 데이터(구·행정동·역·생활권)를 읽어
각 페이지마다 고유한 본문을 조합한다. 지역명만 바꾼 복제 본문을
피하기 위해, 각 엔티티의 고유 특성(character/landmarks/연결 데이터)을
중심에 두고 서술 골격은 slug 해시로 회전시킨다.
"""
import re

from content import seoul_data as D
from content.site import PHONE


# ── 이름 → URL 매핑 (내부 링크용) ──────────────────────────
def _build_maps():
    gu_by_name = {g["name"]: g for g in D.GU}
    dong_url, dong_obj = {}, {}
    for g in D.GU:
        for dn in g["dongs"]:
            dong_url[dn["name"]] = f"/seoul/{g['slug']}/{dn['slug']}/"
            dong_obj[dn["name"]] = (g, dn)
    station_url = {s["name"]: f"/seoul/station/{s['slug']}/" for s in D.STATIONS}
    life_url = {l["name"]: f"/seoul/life/{l['slug']}/" for l in D.LIFE}
    gu_url = {g["name"]: f"/seoul/{g['slug']}/" for g in D.GU}
    return gu_by_name, gu_url, dong_url, dong_obj, station_url, life_url


GU_BY_NAME, GU_URL, DONG_URL, DONG_OBJ, STATION_URL, LIFE_URL = _build_maps()
STATION_BY_NAME = {s["name"]: s for s in D.STATIONS}


def _hash(slug: str) -> int:
    return sum(ord(c) for c in slug)


def pick(slug: str, pool):
    return pool[_hash(slug) % len(pool)]


def link(name: str, url: str) -> str:
    return f'<a href="{url}">{name}</a>'


def link_station(name: str) -> str:
    url = STATION_URL.get(name)
    return link(name, url) if url else f"<strong>{name}</strong>"


def link_dong(name: str) -> str:
    url = DONG_URL.get(name)
    return link(name, url) if url else name


def link_life(name: str) -> str:
    url = LIFE_URL.get(name)
    return link(name, url) if url else name


def link_gu(name: str) -> str:
    url = GU_URL.get(name)
    return link(name, url) if url else name


def kw(slug: str) -> str:
    """첫 문단 키워드를 출장마사지/홈타이로 회전."""
    return pick(slug, ["출장마사지", "홈타이", "방문 마사지"])


# ── 서울 지하철 노선 색상(공식 라인컬러) ──────────────────
LINE_COLORS = {
    "1호선": "#0052A4", "2호선": "#00A84D", "3호선": "#EF7C1C",
    "4호선": "#00A5DE", "5호선": "#996CAC", "6호선": "#CD7C2F",
    "7호선": "#747F00", "8호선": "#E6186C", "9호선": "#BDB092",
    "신분당선": "#D4003B", "수인분당선": "#FABE00", "경의중앙선": "#77C4A3",
    "공항철도": "#0090D2", "경춘선": "#0C8E72", "우이신설선": "#B7C452",
    "신림선": "#6789CA",
}
LINE_ORDER = ["1호선", "2호선", "3호선", "4호선", "5호선", "6호선", "7호선",
              "8호선", "9호선", "신분당선", "수인분당선", "경의중앙선",
              "공항철도", "경춘선", "우이신설선", "신림선"]


def line_chip(line: str) -> str:
    c = LINE_COLORS.get(line, "#5a6275")
    return f'<span class="line-chip" style="background:{c}">{line}</span>'


def line_chips(lines) -> str:
    return ('<span class="line-chips">'
            + "".join(line_chip(l) for l in lines) + "</span>")


def visit_type(character: str, slug: str) -> str:
    """지역 특성에서 주된 방문 형태(자택·오피스텔·호텔·숙소)를 추정해 한 문장으로.
    같은 유형이라도 slug별로 표현을 회전해 인접 페이지 간 중복을 줄인다."""
    c = character or ""
    if any(k in c for k in ["오피스텔", "업무", "IT", "R&D", "법조", "비즈니스", "금융", "단지권"]):
        pool = ["오피스텔과 비즈니스호텔 방문 수요가 많아, 평일 저녁과 심야 시간대 예약이 비교적 많은 편입니다.",
                "업무·오피스텔 비중이 높아 퇴근 후·심야 시간대 방문 문의가 꾸준한 지역입니다.",
                "사무·오피스텔 권역이라 평일 야간과 주말 낮 시간대로 방문 수요가 나뉘는 편입니다."]
    elif any(k in c for k in ["상권", "관광", "숙박", "호텔", "유흥", "먹자"]):
        pool = ["주변에 호텔·숙소가 많아 자택뿐 아니라 숙소 방문 이용이 함께 나타나는 지역입니다.",
                "상권·숙박 시설이 밀집해 호텔·게스트하우스 방문 비중이 높은 편입니다.",
                "유동 인구와 숙소가 많아 자택과 숙소 방문이 고르게 섞이는 권역입니다."]
    elif any(k in c for k in ["대학", "원룸", "1인", "고시"]):
        pool = ["원룸·소형 주거와 숙소가 섞여 있어, 1인 가구 자택 방문 수요가 두드러집니다.",
                "대학가 원룸·오피스텔이 많아 1인 가구 중심의 자택 방문 문의가 많습니다.",
                "소형 주거가 밀집해 혼자 거주하는 분들의 자택 방문 비중이 높은 편입니다."]
    elif any(k in c for k in ["고급", "명품", "레지던스", "타워"]):
        pool = ["프라이버시를 중시하는 자택·레지던스 방문이 많아, 정확한 출입 안내가 특히 중요합니다.",
                "고급 주거·레지던스 비중이 높아 프라이버시와 출입 절차 확인이 중요한 지역입니다.",
                "보안이 갖춰진 고급 주거가 많아, 사전 출입 안내가 방문 동선에 큰 영향을 줍니다."]
    else:
        pool = ["아파트·주택 등 자택 방문 수요가 안정적으로 이어지는 지역으로, 정확한 주소와 출입 방식 확인이 중요합니다.",
                "주거가 중심이라 가족·개인 단위 자택 방문이 꾸준하며, 동·호수 확인이 중요합니다.",
                "대단지·주택가가 배후라 자택 방문 비중이 높고, 공동현관 출입 방식 확인이 필요합니다."]
    return pick(slug, pool)


# 지하철역 본문 회전 문장 풀(인접 역 간 중복 완화)
ST_TAIL = [
    "이 페이지는 {n} 기준으로 인접한 행정동·행정구·생활권을 정리해 방문 예약 전 위치를 빠르게 확인할 수 있도록 안내합니다.",
    "아래에서 {n}과 이어지는 행정동·생활권, 환승 노선을 함께 확인하면 방문 동선을 잡기 쉽습니다.",
    "{n}을 기준으로 인근 행정동과 생활권을 정리했으니, 방문 예약 전 위치 확인에 활용하세요.",
]
ST_LINE = [
    "{n}은 {l} 노선을 이용할 수 있습니다. 노선이 많을수록 다양한 생활권에서 접근이 쉬워 방문 동선의 기준점으로 적합합니다.",
    "{n}을 지나는 노선은 {l}입니다. 여러 방향에서 접근이 가능해 인근 지역 방문 동선을 잡을 때 기준점이 됩니다.",
    "{l}이 지나는 {n}은 환승·이동이 편리해, 인근 자택·숙소 방문 시 위치를 가늠하는 기준으로 삼기 좋습니다.",
]
ST_NDONG = [
    "{n}에서 가까운 행정동입니다. 같은 역세권 동선으로 방문이 이어지는 지역을 함께 안내합니다.",
    "{n} 인근 행정동을 정리했습니다. 역에서 가까운 동부터 방문 동선이 자연스럽게 이어집니다.",
    "{n} 주변에서 방문 문의가 많은 행정동입니다. 각 동 페이지에서 더 구체적인 위치를 확인할 수 있습니다.",
]
ST_GU = [
    "{n}은 {g} 권역과 이어집니다.{life} 인근 자치구의 같은 생활권 지역까지 방문 상담이 가능합니다.",
    "행정구로는 {g}에 걸쳐 있으며,{life} 이를 중심으로 방문 동선이 형성됩니다.",
    "{n} 주변은 {g}와 맞닿아 있습니다.{life} 함께 보면 위치를 더 정확히 잡을 수 있습니다.",
]
ST_VISIT_TAIL = [
    "{n}은 위치를 좁히는 기준일 뿐, 실제 방문은 역이 아니라 자택·오피스텔·호텔의 건물 주소를 기준으로 진행됩니다.",
    "실제 방문은 역이 아니라 머무는 건물 주소로 진행되므로, {n}은 위치 확인용 기준점으로 활용하시면 됩니다.",
    "{n}까지의 거리보다 정확한 건물 주소가 더 중요하며, 가까운 역과 함께 주소·동·호수를 알려주시면 됩니다.",
]


_LM_VERB = [
    "{lm} 일대를 중심으로 생활 동선이 형성됩니다.",
    "대표적으로 {lm} 주변이 방문 동선의 기준이 됩니다.",
    "{lm} 등이 자리해 위치를 가늠하기 쉽습니다.",
]


def landmark_line(landmarks, slug: str) -> str:
    if not landmarks:
        return ""
    return pick(slug, _LM_VERB).format(lm=", ".join(landmarks[:3]))


# ── 공통 블록 ───────────────────────────────────────────────
CHECK_ITEMS = [
    "방문 가능한 정확한 주소(자택·오피스텔·호텔·숙소)와 동·호수",
    "예약 가능 시간과 도착 예정 시간",
    "건물 출입 방식(공동현관 비밀번호, 엘리베이터, 주차 여부)",
    "추가 이동비·심야 할증 여부",
    "결제 방식과 예약 변경·취소 기준",
    "개인정보 처리 기준(연락처는 예약 확인 목적에만 사용)",
]


def check_block(place_phrase: str) -> str:
    items = "".join(f"<li>{x}</li>" for x in CHECK_ITEMS)
    return (
        f"<section><h2>예약 전 확인사항</h2>"
        f"<p>{place_phrase} 방문 예약 전에는 아래 항목을 미리 확인하면 "
        f"도착 시간과 동선이 정확해집니다.</p><ul>{items}</ul>"
        f"<p><strong>구구 마사지</strong>는 안내된 관리 범위와 위생·안전 기준 "
        f"안에서만 서비스를 제공하며, 불법·선정적 요청에는 어떤 경우에도 응하지 "
        f"않습니다. 자세한 내용은 "
        f'<a href="/check/">이용 전 확인사항</a>과 '
        f'<a href="/support/privacy/">개인정보처리방침</a>에서 확인할 수 있습니다.</p>'
        f"</section>"
    )


def pricing_block() -> str:
    """코스 시간별 기본 요금표. class="pricing"이라 본문 글자수 측정에서 제외된다
    (전 페이지 공통 블록이므로 고유 본문으로 계산하지 않는다)."""
    tel = f"tel:{PHONE}"
    return (
        '<section class="pricing">'
        '<h2>코스 시간으로 보는 기본 요금</h2>'
        '<p class="pricing-sub">관리 시간(60·90·120분)을 기준으로 정리한 기본 '
        '금액입니다. 표시되지 않은 별도 비용은 두지 않는 것을 원칙으로 안내합니다.</p>'
        '<div class="pricing-grid">'
        '<div class="price-card">'
        '<p class="price-name">60분 코스</p>'
        '<p class="price-amount">90,000<span class="won">원</span></p>'
        '<p class="price-min">60분</p>'
        '<p class="price-desc">핵심 부위 위주 가벼운 이완</p>'
        f'<a class="price-btn" href="{tel}">예약 문의</a>'
        '</div>'
        '<div class="price-card is-featured">'
        '<span class="price-badge">추천</span>'
        '<p class="price-name">90분 코스</p>'
        '<p class="price-amount">150,000<span class="won">원</span></p>'
        '<p class="price-min">90분</p>'
        '<p class="price-desc">전신 균형 표준 구성·아로마 포함</p>'
        f'<a class="price-btn price-btn-primary" href="{tel}">예약 문의</a>'
        '</div>'
        '<div class="price-card">'
        '<p class="price-name">120분 코스</p>'
        '<p class="price-amount">180,000<span class="won">원</span></p>'
        '<p class="price-min">120분</p>'
        '<p class="price-desc">구석구석 집중하는 프리미엄 구성</p>'
        f'<a class="price-btn" href="{tel}">예약 문의</a>'
        '</div>'
        '</div>'
        '<p class="pricing-note">방문 지역과 시간대, 이동 거리에 따라 최종 금액은 '
        '통화 시 확정됩니다. <a href="/reservation/">요금·예약 기준 자세히 보기 →</a></p>'
        '</section>'
    )


def faq_block(pairs) -> str:
    rows = "".join(f"<dt>{q}</dt><dd>{a}</dd>" for q, a in pairs)
    return (
        f'<section><h2>자주 묻는 질문</h2>'
        f'<dl class="faq-list">{rows}</dl></section>'
    )


_CLOSING = [
    "{name} 출장마사지·홈타이 예약은 전화 상담으로 지역과 시간을 확인한 뒤 진행되며, "
    "방문 전에는 <a href=\"/check/\">이용 전 확인사항</a>을 함께 확인하면 도착 시간과 "
    "동선이 한결 정확해집니다.",
    "{name} 방문 예약 절차와 가능 시간은 <a href=\"/reservation/\">예약 안내</a>에서 "
    "확인할 수 있으며, 연중무휴 24시간 상담을 받습니다. 정확한 주소와 출입 방식을 "
    "알려주시면 가장 가까운 일정으로 안내해 드립니다.",
    "{name}에서 출장마사지·홈타이를 이용하실 때는 자택·오피스텔·호텔·숙소 어디든 "
    "방문이 가능하며, 처음이라면 <a href=\"/guide/\">홈타이 이용 가이드</a>의 방문 "
    "흐름을 참고하시면 도움이 됩니다.",
    "{name} 권역의 예약 문의는 연중무휴 24시간 받고 있으며, 가까운 역이나 생활권 "
    "이름만 알려주셔도 위치를 함께 좁혀 드립니다. 자세한 절차는 "
    "<a href=\"/reservation/\">예약 안내</a>를 참고하세요.",
]


def closing_block(name: str, slug: str) -> str:
    return f"<section><p>{pick(slug, _CLOSING).format(name=name)}</p></section>"


def longtail_block(title, chips):
    """롱테일 주제 칩 내부링크. chips: [(label, url), ...] (None / (label,url) 중복 제거)."""
    seen, html_parts = set(), []
    for c in chips:
        if not c:
            continue
        label, url = c
        if (label, url) in seen:
            continue
        seen.add((label, url))
        html_parts.append(f'<a class="lt-chip" href="{url}">{label}</a>')
    return (
        f'<section class="longtail"><h2>{title}</h2>'
        f'<div class="lt-chips">{"".join(html_parts)}</div></section>'
    )


def dong_longtail(g, dn):
    name, life = dn["name"], dn.get("life_area")
    chips = [
        (f"{name} 자택 출장마사지", "/guide/"),
        (f"{name} 오피스텔 홈타이", "/guide/"),
        (f"{name} 호텔·숙소 방문 마사지", "/guide/"),
        (f"{name} 코스별 요금 안내", "/reservation/"),
        (f"{name} 예약 전 확인사항", "/check/"),
        (f"{g['name']} 출장마사지 지역 안내", f"/seoul/{g['slug']}/"),
    ]
    for s in dn.get("nearby_stations", [])[:2]:
        if s in STATION_URL:
            chips.append((f"{s} 인근 홈타이", STATION_URL[s]))
    if life in LIFE_URL:
        chips.append((f"{life} 생활권 방문 안내", LIFE_URL[life]))
    return longtail_block(f"{name} 주제별 안내 바로가기", chips)


def station_longtail(s):
    name, life = s["name"], s.get("life_area")
    chips = [
        (f"{name} 인근 자택 출장마사지", "/guide/"),
        (f"{name} 근처 오피스텔 홈타이", "/guide/"),
        (f"{name} 주변 호텔 방문 마사지", "/guide/"),
        (f"{name} 출장마사지 요금 안내", "/reservation/"),
        (f"{name} 예약 전 확인사항", "/check/"),
    ]
    for d in s.get("nearby_dongs", [])[:2]:
        if d in DONG_URL:
            chips.append((f"{d} 방문 안내", DONG_URL[d]))
    if life in LIFE_URL:
        chips.append((f"{life} 생활권 홈타이", LIFE_URL[life]))
    return longtail_block(f"{name} 주제별 안내 바로가기", chips)


def life_longtail(l):
    name = l["name"]
    chips = [
        (f"{name} 자택 출장마사지", "/guide/"),
        (f"{name} 오피스텔·호텔 홈타이", "/guide/"),
        (f"{name} 코스별 요금 안내", "/reservation/"),
        (f"{name} 예약 전 확인사항", "/check/"),
    ]
    for x in l.get("gu", [])[:2]:
        if x in GU_URL:
            chips.append((f"{x} 출장마사지 지역 안내", GU_URL[x]))
    for st in l.get("stations", [])[:2]:
        if st in STATION_URL:
            chips.append((f"{st} 인근 홈타이", STATION_URL[st]))
    return longtail_block(f"{name} 주제별 안내 바로가기", chips)


def gu_longtail(g):
    name = g["name"]
    chips = [
        (f"{name} 자택 출장마사지", "/guide/"),
        (f"{name} 오피스텔 홈타이", "/guide/"),
        (f"{name} 호텔·숙소 방문 마사지", "/guide/"),
        (f"{name} 코스별 요금 안내", "/reservation/"),
        (f"{name} 예약 전 확인사항", "/check/"),
    ]
    for la in g.get("life_areas", [])[:2]:
        if la in LIFE_URL:
            chips.append((f"{la} 생활권 방문 안내", LIFE_URL[la]))
    for st in g.get("stations", [])[:2]:
        if st in STATION_URL:
            chips.append((f"{st} 인근 홈타이", STATION_URL[st]))
    return longtail_block(f"{name} 주제별 안내 바로가기", chips)


def related_block(items) -> str:
    """롱테일 주제 카드 목록. items: [{label, sub, url}, ...] (None 무시)."""
    cards = ""
    for it in items:
        if not it:
            continue
        sub = f'<p>{it["sub"]}</p>' if it.get("sub") else ""
        cards += (
            f'<a class="card" href="{it["url"]}"><h3>{it["label"]}</h3>{sub}'
            f'<span class="card-arrow">자세히 보기 →</span></a>'
        )
    return (
        f'<section><h2>관련 지역·생활권 안내</h2>'
        f'<div class="card-grid">{cards}</div></section>'
    )


# ── 롱테일 관련 링크 헬퍼(지역 교차 내부링크 강화) ──────────
_RL_DONG = ["{n} 출장마사지·홈타이 안내", "{n} 방문 가능 지역 안내",
            "{n} 홈타이 예약 안내", "{n} 출장마사지 동네 안내"]
_RL_STATION = ["{n} 인근 출장마사지·홈타이", "{n} 역세권 방문 지역 안내",
               "{n} 주변 홈타이 예약 안내"]
_RL_LIFE = ["{n} 생활권 출장마사지·홈타이", "{n} 생활권 방문 예약 안내",
            "{n} 권역 홈타이 안내"]
_RL_GU = ["{n} 출장마사지·홈타이 안내", "{n} 지역별 방문 안내",
          "{n} 생활권 홈타이 안내"]


def rel_dong(name: str):
    if name not in DONG_URL:
        return None
    g, dn = DONG_OBJ[name]
    la = dn.get("life_area")
    sub = f"{g['name']} · {la} 생활권" if la else f"{g['name']} 방문 안내"
    return {"label": pick(name, _RL_DONG).format(n=name), "sub": sub,
            "url": DONG_URL[name]}


def rel_station(name: str):
    if name not in STATION_URL:
        return None
    obj = STATION_BY_NAME.get(name)
    sub = (", ".join(obj["lines"]) if obj else "") or "역세권 방문 안내"
    return {"label": pick(name, _RL_STATION).format(n=name), "sub": sub,
            "url": STATION_URL[name]}


def rel_life(name: str):
    if name not in LIFE_URL:
        return None
    obj = LIFE_BY_NAME.get(name)
    sub = obj["role"] if obj else "생활권 허브 안내"
    return {"label": pick(name, _RL_LIFE).format(n=name), "sub": sub,
            "url": LIFE_URL[name]}


def rel_gu(name: str):
    if name not in GU_URL:
        return None
    obj = GU_BY_NAME.get(name)
    sub = (obj.get("trait", "") + " 자치구") if obj else "자치구 안내"
    return {"label": pick(name, _RL_GU).format(n=name), "sub": sub,
            "url": GU_URL[name]}


REL_INFO = [
    {"label": "예약 안내·요금 기준", "sub": "코스별 기본 요금·예약 절차", "url": "/reservation/"},
    {"label": "이용 전 확인사항", "sub": "방문 전 필수 체크 항목", "url": "/check/"},
]


def dedupe_rel(items):
    """url 기준 중복 제거, None 제거."""
    seen, out = set(), []
    for it in items:
        if not it or it["url"] in seen:
            continue
        seen.add(it["url"])
        out.append(it)
    return out


# ── 행정구 페이지 ───────────────────────────────────────────
GU_INTRO = [
    "{gu}는 서울에서도 {trait} 자치구로, 생활권과 역세권이 함께 움직이는 곳입니다.",
    "{gu}에서 {kw}를 찾을 때는 행정동·지하철역·생활권을 함께 보는 것이 정확합니다. {gu}는 {trait} 지역입니다.",
    "{trait} {gu}는 방문형 관리 수요가 시간대별로 다르게 나타나는 자치구입니다.",
]


def gu_body(g) -> str:
    slug = g["slug"]
    name = g["name"]
    trait = g.get("trait", "생활권이 뚜렷한")
    parts = []

    intro = pick(slug, GU_INTRO).format(gu=name, trait=trait, kw=kw(slug))
    parts.append(
        f"<section><p>{intro} {g['lead']} 이 페이지는 {name}의 대표 행정동, "
        f"가까운 지하철역, 생활권을 한곳에 정리해 방문 예약 전 위치를 빠르게 "
        f"확인할 수 있도록 안내합니다.</p>"
        f"<p>{name}에서 {kw(slug)}·홈타이를 예약할 때는 행정동으로 위치를 좁히거나, "
        f"가까운 역과 생활권으로 동선을 잡는 두 가지 방법을 함께 쓰면 편리합니다. "
        f"방문 관리는 자택·오피스텔·호텔·숙소 등 머무는 공간으로 직접 찾아가는 "
        f"방식이므로, 정확한 주소와 건물 출입 방식을 미리 확인하는 것이 "
        f"중요합니다.</p></section>"
    )

    # 대표 행정동
    dong_cards = ""
    for dn in g["dongs"]:
        url = f"/seoul/{slug}/{dn['slug']}/"
        dong_cards += (
            f'<a class="card" href="{url}"><h3>{dn["name"]}</h3>'
            f'<p>{dn.get("character","")}</p>'
            f'<span class="card-arrow">자세히 보기 →</span></a>'
        )
    parts.append(
        f"<section><h2>{name} 대표 행정동</h2>"
        f"<p>{name}의 주요 행정동별 위치와 생활권을 안내합니다. 번호 동은 "
        f"대표 동으로 묶어 정리했습니다.</p>"
        f'<div class="card-grid">{dong_cards}</div></section>'
    )

    # 핵심 역세권
    st_links = " · ".join(link_station(s) for s in g["stations"])
    parts.append(
        f"<section><h2>{name} 핵심 지하철역</h2>"
        f"<p>{name}에서 방문 동선의 기준이 되는 주요 지하철역입니다. 역명 "
        f"기준으로 정리했으며, 환승역도 하나의 안내 페이지로 연결됩니다.</p>"
        f"<p>{st_links}</p></section>"
    )

    # 생활권
    life_links = "".join(
        f"<li>{link_life(l)} — {LIFE_BY_NAME[l]['role']}</li>"
        if l in LIFE_BY_NAME else f"<li>{l}</li>"
        for l in g["life_areas"]
    )
    parts.append(
        f"<section><h2>{name} 생활권 연결</h2>"
        f"<p>행정구와 행정동만으로는 검색 의도를 모두 담기 어렵기 때문에, "
        f"실제 사용자가 부르는 생활권 단위로도 안내합니다.</p>"
        f"<ul>{life_links}</ul></section>"
    )

    parts.append(pricing_block())
    parts.append(check_block(f"{name}"))

    faq = [
        (f"{name} 어느 지역까지 방문 가능한가요?",
         f"{name} 전 행정동과 인접 역세권까지 방문 상담이 가능합니다. 정확한 "
         f"주소와 건물 출입 방식을 알려주시면 도착 시간을 안내해 드립니다."),
        (f"{name} 행정동 페이지와 이 페이지는 어떻게 다른가요?",
         f"이 페이지는 {name} 전체 개요와 생활권 허브 역할을 하고, 각 행정동 "
         f"페이지는 가까운 역과 인접 동을 중심으로 더 구체적인 위치를 안내합니다."),
        ("예약은 어떻게 하나요?",
         f'<a href="tel:0508-202-4719">0508-202-4719</a> 전화 또는 '
         f'<a href="/reservation/">예약 안내</a> 페이지의 절차를 참고하시면 됩니다.'),
    ]
    parts.append(faq_block(faq))
    parts.append(closing_block(name, slug))

    # 관련 링크
    rel = dedupe_rel(
        [rel_dong(dn["name"]) for dn in g["dongs"][:3]]
        + [rel_station(s) for s in g["stations"][:2]]
        + [rel_life(la) for la in g["life_areas"][:1]]
        + REL_INFO
    )
    parts.append(gu_longtail(g))
    parts.append(related_block(rel))

    return "\n".join(parts), faq


# ── 행정동 페이지 ───────────────────────────────────────────
DONG_INTRO = [
    "{dong}에서 {kw}를 예약할 때는 가까운 역과 인접 행정동, 생활권을 함께 보면 동선이 정확해집니다.",
    "{gu} {dong}은 {character} 방문형 관리 수요가 꾸준한 지역입니다.",
    "{dong} 일대에서 {kw}·홈타이를 찾는다면 먼저 위치와 생활권을 확인하는 것이 좋습니다.",
]


def dong_body(g, dn) -> str:
    slug = dn["slug"]
    name = dn["name"]
    character = dn.get("character", "")
    parts = []

    intro = pick(slug, DONG_INTRO).format(
        dong=name, gu=g["name"], kw=kw(slug),
        character=(character + "으로" if character else ""))
    landmarks = dn.get("landmarks", [])
    lm = (" 대표적으로 " + ", ".join(landmarks) + " 일대가 포함됩니다.") if landmarks else ""
    parts.append(
        f"<section><p>{intro} {name}은 {g['name']}에 속하며, {character}{lm} "
        f"이 페이지는 {name} 방문 예약 전에 확인할 위치·역세권·생활권 정보를 "
        f"정리한 안내입니다.</p></section>"
    )

    life_html = (link_life(dn.get('life_area', ''))
                 if dn.get('life_area') in LIFE_URL else dn.get('life_area', ''))
    parts.append(
        f"<section><h2>{name}의 위치와 생활권</h2>"
        f"<p>{name}은 {link_gu(g['name'])} 안에서 {life_html} 생활권에 가깝습니다. "
        f"{character}{(' 지역으로, ' + landmark_line(landmarks, slug)) if landmarks else ' 지역입니다.'} "
        f"{g.get('lead','')}</p>"
        f"<p>{visit_type(character, slug)} 방문 관리는 자택, 오피스텔, 호텔·숙소 등 "
        f"머무는 공간으로 직접 찾아가는 방식이므로, {name}에서 예약할 때도 정확한 "
        f"주소와 건물 출입 방식을 미리 확인하는 것이 가장 중요합니다.</p></section>"
    )

    # 가까운 역
    near_st = dn.get("nearby_stations", [])
    st_rows = ""
    for s in near_st:
        obj = STATION_BY_NAME.get(s)
        note = (" — " + ", ".join(obj["lines"]) + " 이용") if obj else ""
        st_rows += f"<li>{link_station(s)}{note}</li>"
    parts.append(
        f"<section><h2>{name}에서 가까운 지하철역</h2>"
        f"<p>{name} 인근에서 방문 동선의 기준이 되는 지하철역입니다. 가까운 역을 "
        f"기준으로 위치를 알려주시면 도착 시간을 더 정확히 안내할 수 있습니다.</p>"
        f"<ul>{st_rows}</ul></section>"
    )

    # 인접 행정동
    near_dong = dn.get("nearby_dongs", [])
    dlinks = " · ".join(link_dong(d) for d in near_dong)
    first = near_dong[0] if near_dong else ""
    first_clause = (
        f"예약이 몰리는 시간대에는 {link_dong(first)} 등 인접 동과 동선을 함께 "
        f"조율하기도 합니다. " if first else ""
    )
    parts.append(
        f"<section><h2>{name} 인접 행정동</h2>"
        f"<p>{name}과 생활권이 이어지는 인접 행정동입니다. {first_clause}"
        f"같은 역세권·생활권에 묶이는 지역은 비슷한 동선으로 방문이 가능한 경우가 "
        f"많습니다.</p><p>{dlinks}</p></section>"
    )

    parts.append(pricing_block())
    parts.append(check_block(f"{name} 자택·오피스텔·숙소"))

    faq = [
        (f"{name}도 방문 가능한가요?",
         f"네, {name} 전역과 인접 행정동까지 방문 상담이 가능합니다. {g['name']} "
         f"내 다른 동이라도 주소를 알려주시면 도착 시간을 안내해 드립니다."),
        (f"{name}에서 호텔·오피스텔도 이용할 수 있나요?",
         "자택뿐 아니라 오피스텔, 호텔·숙소에서도 이용할 수 있습니다. 건물 출입 "
         "방식과 동·호수를 미리 알려주시면 동선이 정확해집니다."),
        ("예약 변경이나 취소는 어떻게 하나요?",
         '예약 변경·취소 기준은 <a href="/reservation/">예약 안내</a>에서 확인할 '
         "수 있으며, 가능한 한 일찍 연락 주시면 일정 조정이 수월합니다."),
    ]
    parts.append(faq_block(faq))
    parts.append(closing_block(name, slug))

    rel = dedupe_rel(
        [rel_station(s) for s in near_st[:2]]
        + [rel_life(dn.get("life_area"))]
        + [rel_gu(g["name"])]
        + [rel_dong(d) for d in near_dong[:3]]
        + REL_INFO[:1]
    )
    parts.append(dong_longtail(g, dn))
    parts.append(related_block(rel))

    return "\n".join(parts), faq


# ── 지하철역 페이지 ─────────────────────────────────────────
ST_INTRO = [
    "{st} 일대에서 {kw}·홈타이를 찾는다면 인접 행정동과 생활권을 함께 확인하는 것이 좋습니다.",
    "{st}은 {lines} 환승·이용객이 많은 역으로, 방문형 관리 동선의 기준점이 됩니다.",
    "{st} 주변에서 {kw}를 예약할 때는 가까운 행정동과 생활권을 먼저 보는 것이 정확합니다.",
]


def station_body(s) -> str:
    slug = s["slug"]
    name = s["name"]
    lines = ", ".join(s.get("lines", []))
    parts = []

    intro = pick(slug, ST_INTRO).format(st=name, kw=kw(slug), lines=lines)
    parts.append(
        f"<section><p>{intro} {s.get('character','')} {pick(slug, ST_TAIL).format(n=name)} "
        f"환승역도 노선·출구별로 나누지 않고 역명 기준 한 페이지로 안내합니다.</p></section>"
    )

    parts.append(
        f"<section><h2>{name} 환승 노선</h2>"
        f"{line_chips(s.get('lines', []))}"
        f"<p>{pick(slug, ST_LINE).format(n=name, l=lines)} 다만 출장마사지·홈타이 "
        f"방문은 노선이 아니라 실제 머무는 건물 위치를 기준으로 진행되므로, 역은 위치를 "
        f"가늠하는 참고점으로 활용하시면 됩니다.</p>"
        f'<p>전체 노선별 역은 <a href="/seoul/station/">지하철역 안내</a>의 '
        f"서울 지하철 1~9호선 노선도에서 확인할 수 있습니다.</p></section>"
    )

    near_dong = s.get("nearby_dongs", [])
    dlinks = "".join(f"<li>{link_dong(d)}</li>" for d in near_dong)
    parts.append(
        f"<section><h2>{name} 인접 행정동</h2>"
        f"<p>{pick(name, ST_NDONG).format(n=name)}</p><ul>{dlinks}</ul></section>"
    )

    near_gu = s.get("nearby_gu", [])
    glinks = " · ".join(link_gu(x) for x in near_gu)
    life = s.get("life_area", "")
    life_html = link_life(life) if life in LIFE_URL else life
    life_clause = f" 대표 생활권은 {life_html} 권역으로, 업무지구·상권·주거가 함께 분포합니다." if life else ""
    parts.append(
        f"<section><h2>{name} 행정구·생활권 연결</h2>"
        f"<p>{pick(name, ST_GU).format(n=name, g=glinks, life=life_clause)}</p></section>"
    )

    parts.append(
        f"<section><h2>{name} 방문 동선과 이용 형태</h2>"
        f"<p>{visit_type(s.get('character',''), slug)} {pick(slug, ST_VISIT_TAIL).format(n=name)} "
        f"가까운 역과 함께 정확한 주소·동·호수를 알려주시면 도착 시간과 동선이 "
        f"정확해집니다.</p>"
        f"<p>{name} 인근에서 예약하실 때는 "
        f"{', '.join(link_dong(d) for d in near_dong[:3])} 방향 동선을 함께 "
        f"안내해 드릴 수 있습니다. 행정구로는 "
        f"{', '.join(link_gu(x) for x in s.get('nearby_gu', []))} 권역과 이어지며, "
        f"인접 자치구의 같은 생활권 지역까지 방문 상담이 가능합니다.</p></section>"
    )

    parts.append(pricing_block())
    parts.append(check_block(f"{name} 인근"))

    faq = [
        (f"{name} 근처면 어디까지 방문되나요?",
         f"{name} 인접 행정동과 같은 생활권 지역까지 방문 상담이 가능합니다. "
         "정확한 주소를 알려주시면 도착 시간을 안내해 드립니다."),
        (f"{name}은 환승역인데 출구별로 안내가 다른가요?",
         "출구나 노선별로 페이지를 나누지 않습니다. 역명 기준으로 한 번에 "
         "안내하며, 실제 방문은 건물 주소를 기준으로 진행합니다."),
        ("심야에도 예약이 가능한가요?",
         '연중무휴 24시간 상담을 받고 있으며, 심야 할증 여부는 '
         '<a href="/reservation/">예약 안내</a>에서 확인할 수 있습니다.'),
    ]
    parts.append(faq_block(faq))
    parts.append(closing_block(name, slug))

    rel = dedupe_rel(
        [rel_dong(d) for d in near_dong[:3]]
        + [rel_life(life)]
        + [rel_gu(x) for x in near_gu[:2]]
        + REL_INFO[:1]
    )
    parts.append(station_longtail(s))
    parts.append(related_block(rel))

    return "\n".join(parts), faq


# ── 생활권 페이지 ───────────────────────────────────────────
LIFE_INTRO = [
    "{name} 생활권은 {role} 권역으로, 행정구·행정동·역세권을 잇는 허브 역할을 합니다.",
    "{name} 일대에서 {kw}·홈타이를 찾는다면 생활권 단위로 위치를 잡는 것이 편합니다. 이 권역은 {role} 성격을 가집니다.",
    "{name} 생활권은 실제 사용자가 부르는 권역 이름으로, {role} 안내에 적합합니다.",
]


def life_body(l) -> str:
    slug = l["slug"]
    name = l["name"]
    role = l.get("role", "")
    parts = []

    intro = pick(slug, LIFE_INTRO).format(name=name, role=role, kw=kw(slug))
    parts.append(
        f"<section><p>{intro} {l.get('lead','')} 이 페이지는 {name} 권역에 묶이는 "
        f"행정구, 행정동, 지하철역을 한곳에 정리해 방문 예약 전 위치를 빠르게 "
        f"확인할 수 있도록 안내합니다. 행정구·행정동만으로 위치를 잡기 애매할 때, "
        f"익숙한 생활권 이름으로 먼저 권역을 정하고 연결된 동·역으로 좁혀가면 "
        f"동선을 잡기 쉽습니다.</p></section>"
    )

    glinks = " · ".join(link_gu(x) for x in l.get("gu", []))
    parts.append(
        f"<section><h2>{name} 연결 행정구</h2>"
        f"<p>{name} 생활권은 {glinks} 권역에 걸쳐 있습니다.</p></section>"
    )

    dlinks = "".join(f"<li>{link_dong(d)}</li>" for d in l.get("dongs", []))
    parts.append(
        f"<section><h2>{name} 연결 행정동</h2>"
        f"<p>{name} 권역에서 방문 수요가 함께 움직이는 행정동입니다.</p>"
        f"<ul>{dlinks}</ul></section>"
    )

    slinks = "".join(f"<li>{link_station(s)}</li>" for s in l.get("stations", []))
    parts.append(
        f"<section><h2>{name} 연결 지하철역</h2>"
        f"<p>{name} 생활권의 방문 동선 기준이 되는 지하철역입니다.</p>"
        f"<ul>{slinks}</ul></section>"
    )

    gu_txt = ", ".join(l.get("gu", []))
    dong_txt = ", ".join(l.get("dongs", [])[:4])
    st_txt = ", ".join(l.get("stations", [])[:3])
    line_notes = []
    for sn in l.get("stations", []):
        obj = STATION_BY_NAME.get(sn)
        if obj:
            line_notes.append(f"{sn}({', '.join(obj['lines'])})")
    line_txt = (" 권역 내 주요 역의 노선은 " + ", ".join(line_notes) + " 등으로, "
                "여러 노선이 지나 다양한 방향에서 접근이 쉽습니다.") if line_notes else (
                " 연결된 역과 행정동을 함께 보면 권역 안에서 위치를 더 정확히 좁힐 수 "
                "있고, 방문 동선을 잡기도 수월합니다.")
    parts.append(
        f"<section><h2>{name} 권역 방문 안내</h2>"
        f"<p>{name} 생활권은 {gu_txt} 일대의 {dong_txt} 등을 묶는 권역으로, "
        f"{role.replace(' 안내','')} 성격이 강합니다. {st_txt}을 기준으로 동선을 "
        f"잡으면 권역 안에서 위치를 빠르게 좁힐 수 있습니다.{line_txt}</p>"
        f"<p>방문 관리는 자택, 오피스텔, 호텔·숙소 등 머무는 공간으로 직접 찾아가는 "
        f"방식이므로, {name} 권역에서 예약할 때도 정확한 주소와 건물 출입 방식을 "
        f"함께 알려주시면 도착 시간이 정확해집니다. 행정동 단위로 더 좁혀 보려면 "
        f"위 연결 행정동을, 가까운 역을 알고 있다면 연결 지하철역을 함께 "
        f"참고하세요.</p></section>"
    )

    parts.append(pricing_block())
    parts.append(check_block(f"{name} 권역"))

    faq = [
        (f"{name} 생활권은 어떤 지역을 말하나요?",
         f"{name}은 {', '.join(l.get('gu',[]))} 일대의 "
         f"{', '.join(l.get('dongs',[])[:4])} 등을 묶은 권역입니다."),
        ("생활권 페이지는 왜 따로 있나요?",
         "행정구·행정동만으로는 검색 의도를 모두 담기 어렵기 때문입니다. 실제 "
         "사용자가 부르는 생활권을 연결하면 위치를 더 직관적으로 찾을 수 있습니다."),
        ("이 권역도 24시간 예약되나요?",
         '연중무휴 24시간 상담을 받고 있습니다. 자세한 절차는 '
         '<a href="/reservation/">예약 안내</a>를 참고하세요.'),
    ]
    parts.append(faq_block(faq))
    parts.append(closing_block(name, slug))

    rel = dedupe_rel(
        [rel_station(s) for s in l.get("stations", [])[:2]]
        + [rel_dong(d) for d in l.get("dongs", [])[:3]]
        + [rel_gu(x) for x in l.get("gu", [])[:2]]
        + REL_INFO[:1]
    )
    parts.append(life_longtail(l))
    parts.append(related_block(rel))

    return "\n".join(parts), faq


LIFE_BY_NAME = {l["name"]: l for l in D.LIFE}
