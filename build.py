#!/usr/bin/env python3
"""구구 마사지 — 서울 전문 출장마사지·홈타이 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 1,500자 미만 페이지는 robots noindex 처리(지시서 색인 조건)
  - sitemap.xml 에는 index 허용 페이지만 포함
  - meta description 은 80자 이내로 강제 트림
  - 모든 페이지에 Organization + WebPage + BreadcrumbList 스키마,
    faq 보유 시 FAQPage 스키마를 자동 주입
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content import PAGES
from content import reviews as RV
from datetime import datetime, timezone

from content.site import (BASE_URL, BRAND, BRAND_MARK, NAV, PHONE,
                          PHONE_DISPLAY, TELEGRAM_URL, AREA_SERVED, FOOTER_QUICK,
                          NAVER_SITE_VERIFICATION, GOOGLE_SITE_VERIFICATION,
                          INDEXNOW_KEY)

# 코스 요금(요금표와 동일) — Offer 스키마용
COURSE_OFFERS = [("60분 코스", "90000"), ("90분 코스", "150000"), ("120분 코스", "180000")]

ROOT = os.path.dirname(os.path.abspath(__file__))
# Cloudflare Pages가 저장소 루트를 그대로 배포하므로 결과물을 루트에 출력한다.
PUBLIC_DIR = ROOT
MIN_INDEX_CHARS = 1500
MAX_DESC_CHARS = 80


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수. 공통 요금/안내 블록은 측정에서 제외."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def _xml(t: str) -> str:
    """RSS/XML 텍스트 이스케이프."""
    return html.escape(t or "", quote=True)


def clamp_desc(desc: str) -> str:
    """메타 디스크립션을 80자 이내로 보장한다."""
    desc = re.sub(r"\s+", " ", desc).strip()
    if len(desc) <= MAX_DESC_CHARS:
        return desc
    return desc[:MAX_DESC_CHARS - 1].rstrip() + "…"


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


def _ld(obj: dict) -> str:
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(obj, ensure_ascii=False, indent=2)
        + "\n</script>\n"
    )


def make_org_schema() -> dict:
    base = BASE_URL.rstrip("/")
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": base + "/#organization",
        "name": BRAND,
        "url": base + "/",
        "logo": base + "/assets/apple-touch-icon.png",
        "image": base + "/assets/og-image.svg",
        "telephone": PHONE,
        "areaServed": {"@type": "AdministrativeArea", "name": AREA_SERVED},
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": PHONE,
            "contactType": "reservations",
            "availableLanguage": ["ko"],
            "areaServed": "KR",
        },
    }


def make_breadcrumb_schema(crumbs) -> dict:
    base = BASE_URL.rstrip("/")
    items = [{
        "@type": "ListItem",
        "position": 1,
        "name": "홈",
        "item": base + "/",
    }]
    rest = crumbs[1:] if crumbs and crumbs[0][1] == "/" else crumbs
    for i, (label, href) in enumerate(rest, start=2):
        entry = {"@type": "ListItem", "position": i, "name": label}
        if href:
            entry["item"] = base + href
        items.append(entry)
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def make_webpage_schema(title: str, desc: str, canonical: str) -> dict:
    base = BASE_URL.rstrip("/")
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": desc,
        "url": canonical,
        "inLanguage": "ko",
        "isPartOf": {"@id": base + "/#organization"},
        "publisher": {"@id": base + "/#organization"},
        "primaryImageOfPage": {
            "@type": "ImageObject",
            "url": base + "/assets/og-image.svg",
            "width": 1200,
            "height": 630,
        },
    }


def make_faq_schema(faq) -> dict:
    """[(q, a), ...] 형태의 FAQ를 FAQPage 스키마로 변환."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faq
        ],
    }


def _stars(rating) -> str:
    full = int(round(rating))
    return "★" * full + "☆" * (5 - full)


def render_reviews(shown, agg) -> str:
    """페이지 하단 '이용 후기' 가시 섹션(스키마와 1:1 일치)."""
    if not shown:
        return ""
    cards = ""
    for rv in shown:
        cards += (
            f'<article class="review-card">'
            f'<div class="review-stars" aria-label="별점 {rv["rating"]}점">{_stars(rv["rating"])}</div>'
            f'<p class="review-body">“{rv["body"]}”</p>'
            f'<p class="review-meta"><span class="review-author">{rv["author"]}</span>'
            f'<span class="review-area">{rv.get("area","")}</span>'
            f'<time datetime="{rv["date"]}">{rv["date"]}</time></p></article>'
        )
    return (
        '<section class="reviews-band" aria-label="이용 후기"><div class="container">'
        '<div class="reviews-head"><h2>이용 후기</h2>'
        f'<div class="reviews-score"><span class="reviews-avg">{agg["value"]}</span>'
        f'<span class="reviews-stars" aria-hidden="true">{_stars(agg["value"])}</span>'
        f'<span class="reviews-count">5점 만점 · 누적 후기 {agg["count"]}개</span></div></div>'
        f'<div class="reviews-grid">{cards}</div>'
        '<p class="reviews-note">실제 이용 고객이 남긴 후기를 바탕으로 합니다. '
        '<a href="/reviews/">전체 후기 보기 →</a></p>'
        '</div></section>'
    )


def make_service_schema(area_name: str, canonical: str, shown, agg) -> dict:
    """Service + AggregateOffer(요금) + AggregateRating/Review(후기) 스키마."""
    base = BASE_URL.rstrip("/")
    offers = [{
        "@type": "Offer", "name": n, "price": p, "priceCurrency": "KRW",
        "availability": "https://schema.org/InStock", "url": base + "/reservation/",
    } for n, p in COURSE_OFFERS]
    sch = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": "서울 출장마사지·홈타이 방문 관리",
        "serviceType": ["출장마사지", "홈타이", "방문 마사지"],
        "provider": {"@id": base + "/#organization"},
        "areaServed": {"@type": "AdministrativeArea", "name": area_name},
        "url": canonical,
        "offers": {
            "@type": "AggregateOffer", "priceCurrency": "KRW",
            "lowPrice": "90000", "highPrice": "180000", "offerCount": "3",
            "offers": offers,
        },
    }
    if agg["count"]:
        sch["aggregateRating"] = {
            "@type": "AggregateRating",
            "ratingValue": str(agg["value"]), "reviewCount": str(agg["count"]),
            "bestRating": "5", "worstRating": str(agg["worst"]),
        }
    if shown:
        sch["review"] = [{
            "@type": "Review",
            "author": {"@type": "Person", "name": rv["author"]},
            "datePublished": rv["date"],
            "reviewRating": {"@type": "Rating", "ratingValue": str(rv["rating"]),
                             "bestRating": "5", "worstRating": "1"},
            "reviewBody": rv["body"],
        } for rv in shown]
    return sch


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = clamp_desc(page["desc"])
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")
    faq = page.get("faq") or []

    chars = text_length(body)
    # 모든 페이지 색인 — noindex 미사용(정책)
    robots = '<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1">'
    canonical = BASE_URL.rstrip("/") + "/" + path

    # 검색엔진 소유확인 메타(메인 페이지에만 출력)
    verify_meta = ""
    if path == "":
        if NAVER_SITE_VERIFICATION:
            verify_meta += f'\n<meta name="naver-site-verification" content="{NAVER_SITE_VERIFICATION}">'
        if GOOGLE_SITE_VERIFICATION:
            verify_meta += f'\n<meta name="google-site-verification" content="{GOOGLE_SITE_VERIFICATION}">'

    page_head = hero if hero else ""
    h1_html = "" if hero else f"<h1>{h1}</h1>"

    body, toc_items = inject_toc(body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"

    # 스키마 자동 주입.
    if hero:
        # 메인은 main.py extra_head에 풍부한 스키마가 이미 있으므로 Organization만 보강.
        auto_schema = _ld(make_org_schema())
    else:
        blocks = [make_org_schema(), make_webpage_schema(title, desc, canonical)]
        if crumbs:
            blocks.append(make_breadcrumb_schema(crumbs))
        if faq:
            blocks.append(make_faq_schema(faq))
        auto_schema = "".join(_ld(b) for b in blocks)

    # 서비스(요금 Offer) + 후기/평점 스키마 + 가시 후기 섹션
    area_name = page.get("area_name", AREA_SERVED)
    no_reviews = page.get("no_reviews", False)
    agg = RV.aggregate()
    shown = RV.shown_for(path or "home") if not no_reviews else []
    reviews_html = render_reviews(shown, agg)
    if not no_reviews:
        auto_schema += _ld(make_service_schema(area_name, canonical, shown, agg))

    base = BASE_URL.rstrip("/")
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}{verify_meta}
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="{BRAND} 새 안내" href="/rss.xml">
<link rel="sitemap" type="application/xml" title="Sitemap" href="/sitemap.xml">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{base}/assets/og-image.svg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{base}/assets/og-image.svg">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg?v=2">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png?v=2">
<link rel="icon" href="/favicon.ico?v=2" sizes="48x48">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png?v=2">
<meta name="theme-color" content="#08090d">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css">
<link rel="stylesheet" href="/assets/style.css">
{auto_schema}{extra_head}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/"><span class="brand-mark">{BRAND_MARK}</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> 서울 전지역 방문 관리 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {body}
    </article>
  </div>
  {reviews_html}
</main>
<footer class="site-footer" role="contentinfo">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <a class="footer-brandwrap" href="/"><span class="brand-mark footer-mark">{BRAND_MARK}</span> <span class="footer-brand">{BRAND}</span></a>
      <p class="footer-desc">{BRAND}는 서울 전지역 출장마사지·홈타이 방문 관리를 안내합니다. 서울 25개 행정구와 주요 지하철역·생활권별 방문 가능 지역, 예약 절차를 한곳에서 확인할 수 있습니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">상호</span> {BRAND}</span>
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> 서울특별시 전지역</span>
      </address>
    </div>
    <nav class="footer-col" aria-label="지역 안내">
      <p class="footer-title">지역 안내</p>
      <ul>
        <li><a href="/seoul/area/">서울 행정구 안내</a></li>
        <li><a href="/seoul/gangnam-gu/yeoksam-dong/">행정동 안내</a></li>
        <li><a href="/seoul/station/">지하철역 안내</a></li>
        <li><a href="/seoul/life/">생활권 안내</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/reservation/">예약 안내</a></li>
        <li><a href="/reviews/">이용 후기</a></li>
        <li><a href="/check/">이용 전 확인사항</a></li>
        <li><a href="/guide/">홈타이 이용 가이드</a></li>
        <li><a href="/support/">고객센터</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 문의">
      <p class="footer-title">정책·문의</p>
      <ul>
        <li><a href="/support/privacy/">개인정보처리방침</a></li>
        <li><a href="tel:{PHONE}">전화 예약 {PHONE_DISPLAY}</a></li>
        <li><a href="{TELEGRAM_URL}" target="_blank" rel="noopener nofollow">제작·제휴 문의</a></li>
      </ul>
    </nav>
  </div>
  <nav class="container footer-quick" aria-label="주요 지역 바로가기">
    <span class="footer-quick-label">주요 지역</span>
    {"".join(f'<a href="{u}">{l}</a>' for l, u in FOOTER_QUICK)}
  </nav>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-biz">상호 {BRAND} · 예약전화 <a href="tel:{PHONE}">{PHONE_DISPLAY}</a> · 서비스 지역 서울특별시 전지역 · 상담 연중무휴 24시간</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법·선정적 요청은 어떤 경우에도 응하지 않습니다.</p>
      <p class="footer-copy">&copy; {BRAND}. All rights reserved.</p>
      <div class="footer-actions">
        <a class="btn-telegram" href="{TELEGRAM_URL}" target="_blank" rel="noopener nofollow" title="웹사이트 제작문의"><span class="btn-ic" aria-hidden="true">✦</span> 웹사이트 제작문의</a>
        <a class="btn-partnership" href="{TELEGRAM_URL}" target="_blank" rel="noopener nofollow" title="제휴문의"><span class="btn-ic" aria-hidden="true">✦</span> 제휴문의</a>
      </div>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def build() -> None:
    report = []
    sitemap_urls = []
    feed_items = []
    seen_paths = set()
    now = datetime.now(timezone.utc)
    lastmod = now.strftime("%Y-%m-%d")
    pubdate = now.strftime("%a, %d %b %Y %H:%M:%S +0000")

    os.makedirs(PUBLIC_DIR, exist_ok=True)

    for page in PAGES:
        path = page["path"]
        if path in seen_paths:
            print(f"  ⚠ 중복 경로: /{path}")
        seen_paths.add(path)
        out_dir = os.path.join(PUBLIC_DIR, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        chars = text_length(page["body"])
        # 전 페이지 색인 + 사이트맵/RSS 포함
        url = BASE_URL.rstrip("/") + "/" + path
        sitemap_urls.append(url)
        feed_items.append((url, page["title"], clamp_desc(page["desc"])))
        report.append((path or "/", chars, "THIN" if chars < MIN_INDEX_CHARS else "index"))

    base = BASE_URL.rstrip("/")
    host = base.split("://", 1)[-1]

    # sitemap.xml (lastmod 포함)
    urls = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{lastmod}</lastmod>"
        f"<changefreq>{'daily' if u==base+'/' else 'weekly'}</changefreq>"
        f"<priority>{'1.0' if u==base+'/' else '0.7'}</priority></url>"
        for u in sitemap_urls
    )
    with open(os.path.join(PUBLIC_DIR, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n"
        )

    # rss.xml (네이버/구글 콘텐츠 발견 가속)
    items = "\n".join(
        "  <item>"
        f"<title>{_xml(t)}</title>"
        f"<link>{u}</link>"
        f"<guid isPermaLink=\"true\">{u}</guid>"
        f"<description>{_xml(d)}</description>"
        f"<pubDate>{pubdate}</pubDate>"
        "</item>"
        for u, t, d in feed_items
    )
    with open(os.path.join(PUBLIC_DIR, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n<channel>\n'
            f"<title>{_xml(BRAND)} — 서울 출장마사지·홈타이 안내</title>\n"
            f"<link>{base}/</link>\n"
            f'<atom:link href="{base}/rss.xml" rel="self" type="application/rss+xml"/>\n'
            "<description>서울 25개 행정구·지하철역·생활권별 방문 안내</description>\n"
            "<language>ko-KR</language>\n"
            f"<lastBuildDate>{pubdate}</lastBuildDate>\n"
            f"{items}\n</channel>\n</rss>\n"
        )

    # IndexNow 키 파일(루트 게시) — 빙·네이버 즉시 색인 통보용
    if INDEXNOW_KEY:
        with open(os.path.join(PUBLIC_DIR, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
            f.write(INDEXNOW_KEY + "\n")

    # robots.txt — 전 봇 허용 + 사이트맵·RSS 안내
    with open(os.path.join(PUBLIC_DIR, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            "User-agent: *\n"
            "Allow: /\n\n"
            "# 주요 검색엔진 봇 (구글/네이버/빙/다음)\n"
            "User-agent: Googlebot\nAllow: /\n"
            "User-agent: Yeti\nAllow: /\n"          # 네이버
            "User-agent: bingbot\nAllow: /\n"
            "User-agent: Daum\nAllow: /\n\n"
            f"Sitemap: {base}/sitemap.xml\n"
            f"Sitemap: {base}/rss.xml\n"
        )

    open(os.path.join(PUBLIC_DIR, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    thin = 0
    for p, c, r in sorted(report):
        if r == "THIN":
            thin += 1
        flag = "  ⚠ 1500자 미만" if r == "THIN" else ""
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    print(f"\n{len(report)} pages built, all index, {len(sitemap_urls)} in sitemap, "
          f"{thin} thin(<1500).")


if __name__ == "__main__":
    build()
