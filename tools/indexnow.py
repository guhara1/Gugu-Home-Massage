#!/usr/bin/env python3
"""IndexNow 일괄/단건 색인 통보 (빙·네이버 등 IndexNow 참여 엔진 즉시 통보).

사용법:
  # 사이트맵의 모든 URL을 통보(첫 일괄 통보)
  python3 tools/indexnow.py

  # 특정 URL만 통보(글/페이지 추가·수정 시)
  python3 tools/indexnow.py https://gugu-home-massage.pages.dev/seoul/gangnam-gu/

  # 경로만 입력해도 됨(자동으로 도메인 결합)
  python3 tools/indexnow.py /seoul/songpa-gu/ /seoul/station/jamsil-station/

전제: 키 파일 https://{host}/{KEY}.txt 이 배포되어 있어야 한다(빌드 시 자동 생성).
IndexNow는 api.indexnow.org 한 곳에 보내면 참여 엔진(빙·네이버·얀덱스 등)에 전파된다.
구글은 IndexNow 미참여 — 구글은 사이트맵(GSC) 및 자연 크롤링으로 색인된다.
"""
import json
import os
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from content.site import BASE_URL, INDEXNOW_KEY  # noqa: E402

BASE = BASE_URL.rstrip("/")
HOST = BASE.split("://", 1)[-1]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# IndexNow 엔드포인트(여러 곳에 보내도 되며, 참여 엔진 간 공유됨)
ENDPOINTS = [
    "https://api.indexnow.org/indexnow",
    "https://www.bing.com/indexnow",
    "https://searchadvisor.naver.com/indexnow",  # 네이버
]


def sitemap_urls():
    path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(path):
        sys.exit("sitemap.xml 이 없습니다. 먼저 `python3 build.py` 를 실행하세요.")
    tree = ET.parse(path)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in tree.iterfind(".//s:loc", ns)]


def normalize(args):
    urls = []
    for a in args:
        if a.startswith("http"):
            urls.append(a)
        else:
            urls.append(BASE + "/" + a.lstrip("/"))
    return urls


def submit(urls):
    if not INDEXNOW_KEY:
        sys.exit("INDEXNOW_KEY 가 비어 있습니다(content/site.py).")
    payload = json.dumps({
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{BASE}/{INDEXNOW_KEY}.txt",
        "urlList": urls,
    }).encode("utf-8")

    print(f"통보 대상 {len(urls)}개 URL · 키 {INDEXNOW_KEY[:8]}…")
    for ep in ENDPOINTS:
        req = urllib.request.Request(
            ep, data=payload,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print(f"  ✓ {ep}  →  HTTP {r.status}")
        except urllib.error.HTTPError as e:
            # 200/202 외에도 일부 엔진은 빈 본문/상태코드를 반환
            print(f"  · {ep}  →  HTTP {e.code} ({e.reason})")
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {ep}  →  {e}")


if __name__ == "__main__":
    targets = normalize(sys.argv[1:]) if len(sys.argv) > 1 else sitemap_urls()
    # IndexNow 1회 요청 권장 상한(1만) 내에서 청크 분할
    CHUNK = 10000
    for i in range(0, len(targets), CHUNK):
        submit(targets[i:i + CHUNK])
    print("완료. (빙·네이버 등 IndexNow 참여 엔진에 전파됩니다)")
