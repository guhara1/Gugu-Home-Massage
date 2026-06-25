#!/usr/bin/env python3
"""(선택) 구글 Indexing API 즉시 색인 통보.

⚠️ 주의:
  - 구글 Indexing API는 공식적으로 JobPosting/BroadcastEvent 구조화 데이터 페이지를
    대상으로 합니다. 일반 페이지 제출은 보장되지 않습니다.
  - 가장 확실한 구글 색인 경로는 (1) 서치콘솔에 sitemap.xml 제출,
    (2) URL 검사 → 색인 요청, (3) 자연 크롤링입니다.
  - 구글은 IndexNow에 참여하지 않습니다(빙·네이버는 tools/indexnow.py 사용).

사전 준비:
  1) pip install google-auth requests
  2) Google Cloud 콘솔에서 서비스 계정 생성 → JSON 키 다운로드
  3) Search Console 속성에 해당 서비스 계정 이메일을 '소유자'로 추가
  4) export GOOGLE_APPLICATION_CREDENTIALS=/path/service-account.json

사용:
  python3 tools/google_indexing.py                 # 사이트맵 전체
  python3 tools/google_indexing.py https://.../a/  # 특정 URL
"""
import os
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from content.site import BASE_URL  # noqa: E402

BASE = BASE_URL.rstrip("/")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
SCOPES = ["https://www.googleapis.com/auth/indexing"]


def sitemap_urls():
    tree = ET.parse(os.path.join(ROOT, "sitemap.xml"))
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text for loc in tree.iterfind(".//s:loc", ns)]


def main(args):
    try:
        from google.oauth2 import service_account
        from google.auth.transport.requests import AuthorizedSession
    except ImportError:
        sys.exit("먼저 설치하세요:  pip install google-auth requests")

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path or not os.path.exists(cred_path):
        sys.exit("GOOGLE_APPLICATION_CREDENTIALS 환경변수에 서비스계정 JSON 경로를 지정하세요.")

    creds = service_account.Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    session = AuthorizedSession(creds)

    urls = [a if a.startswith("http") else BASE + "/" + a.lstrip("/") for a in args] \
        or sitemap_urls()
    print(f"구글 Indexing API 통보 {len(urls)}개 (일 200건 한도 주의)")
    for u in urls:
        r = session.post(ENDPOINT, json={"url": u, "type": "URL_UPDATED"})
        print(f"  {r.status_code}  {u}")


if __name__ == "__main__":
    main(sys.argv[1:])
