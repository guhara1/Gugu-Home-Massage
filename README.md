# 구구 마사지 — 서울 전문 출장마사지·홈타이 안내 사이트

서울특별시 전지역 방문 관리 서비스(출장마사지·홈타이) 안내 정적 사이트입니다.

**상호**: 구구 마사지
**예약전화**: 0508-202-4719
**서비스 지역**: 서울특별시 25개 자치구 전역

## 구조

- **정적 HTML 사이트** — 어느 호스팅(Cloudflare Pages, GitHub Pages, Netlify)에서든 그대로 서빙
- **build.py** + **content/** — 페이지를 Python으로 정의하고 정적 HTML 생성
- **데이터 기반 생성** — 지역명만 바꾼 복제 본문이 아니라, 각 지역의 고유 데이터(인접 역·동·생활권·랜드마크)를 엮어 페이지마다 다른 본문 생성

```
build.py                     # 빌드 스크립트(스키마·noindex·디스크립션 트림 자동 처리)
content/
  site.py                    # 상호·전화·도메인·텔레그램·메뉴
  seoul_data.py              # 구/역/생활권 데이터 취합 + 22개 생활권
  _data_gangnam.py           # 강남구 데이터(스키마 예시)
  _data_c~g.py               # 나머지 24개 구 데이터(권역별 분할)
  _data_stations.py          # 46개 핵심 역세권 데이터
  generate.py                # 데이터 → 본문 생성기(구/동/역/생활권)
  main.py                    # 서울 메인 페이지(히어로 + 스키마)
  info.py                    # 예약·확인사항·가이드·고객센터·개인정보
  __init__.py                # 페이지 조립(PAGES)
assets/
  style.css                  # 프리미엄 다크 + 앰버/골드 + Pretendard + 글래스 오버레이
  og-image.svg               # 선호 썸네일(1200×630)
  favicon.svg / *.png        # 파비콘
```

## 빌드

```bash
python3 build.py
```

빌드 시 페이지별 본문 글자수와 색인(index/noindex) 리포트가 출력됩니다.

## SEO 운영 원칙(구글 정책 반영)

- **전 페이지 색인(noindex 미사용)** — 모든 페이지를 `index,follow`로 색인, 전부 사이트맵 포함.
  모든 페이지가 1,500자 이상 고유 본문을 갖추도록 보강하여 thin 페이지 0
- **SEO 최적화 푸터** — NAP(상호·예약전화·상담시간·서비스지역), 정리된 내비게이션 4열,
  주요 지역 롱테일 바로가기, 정책·문의 링크, `role="contentinfo"`/시맨틱 `<nav aria-label>`
- **메뉴명·URL에 키워드 미반복** — `/seoul/gangnam-gu/`, `/seoul/station/gangnam-station/` 등 지역·역명 기준
- **환승역 단일 URL** — 노선·출구별로 페이지를 쪼개지 않음
- **번호 동 → 대표 동 병합** — `역삼1·2동` → `역삼동`
- **생활권 허브** — 행정구·행정동·역세권을 잇는 22개 생활권 페이지
- **고유 본문** — 지역별 데이터 + 회전 서술 골격으로 중복 문장 최소화
- **E-E-A-T / 건전성 안내** — 모든 페이지에 이용 전 확인사항·개인정보·불법/선정 불가 안내
- **지하철 노선도** — 지하철역 안내 페이지에 서울 1~9호선 + 신분당선·경의중앙선·공항철도·
  우이신설선 등 전 노선별 **접기/펼치기 노선도(`<details>` 아코디언, JS 불필요)**, 노선 컬러
  칩·역 수 표기, 각 역 페이지 노선 칩. 2차 확장 구(강동·강북·도봉·동대문·서대문·성북) 역
  33곳 추가로 노선 커버리지 확대(역 46→79개, priority=2 단계 색인)
- **도어웨이 방지** — 자동 리다이렉트·클로킹 없음, 페이지마다 고유 데이터 본문(중앙값
  1,800자+)과 롱테일 주제 교차 내부링크 제공. 1,500자 미만 thin 페이지는 개인정보처리방침
  (법적 고지) 외 없음. 키워드 도배 URL·메뉴 미사용, 단일 목적지 깔때기 구조 아님

### 스키마(JSON-LD) — 전 페이지 자동 주입

- `Organization`(전역) · `WebPage`(`primaryImageOfPage` 포함) · `BreadcrumbList`
- `FAQPage`(FAQ 보유 페이지) · 메인은 `ItemList`(25개 구) 추가
- `Service` — 페이지별 `areaServed`(구/동/역/생활권), `AggregateOffer`(60·90·120분 요금),
  `AggregateRating`(평점)·`Review`(후기). **페이지에 실제로 보이는 후기 섹션과 1:1 일치**
- 선호 썸네일: `og:image` + `ImageObject`로 `assets/og-image.svg` 지정

### 이용 후기·평점 (`content/reviews.py`)

전 페이지 하단 '이용 후기' 섹션 + `/reviews/` 전체 후기 페이지. ⚠️ **구글 정책상 리뷰·평점
구조화 데이터는 실제 후기에 근거해야 합니다.** `content/reviews.py`의 샘플 후기를 실제
수집한 후기로 교체하세요(허위 평점 마크업은 검색 패널티 사유). 평점·후기 수는 데이터에서
자동 산출됩니다.

### 롱테일 내부링크 강화

- 메인: '서울 지역별 바로가기' 허브(25개 구·22개 생활권·핵심 역 롱테일 앵커)
- 전 지역 페이지: '주제별 안내 바로가기' 칩(자택/오피스텔/호텔·요금·확인사항·인근 지역) +
  '관련 지역·생활권' 카드 + 푸터 주요 지역 링크

## 현재 페이지 구성

- 서울 메인 1
- 행정구 안내 + 25개 구
- 행정동 163개(1차 색인 67개 / 2·3차 대기 noindex)
- 지하철역 안내 + 46개 핵심 역
- 생활권 안내 + 22개 생활권
- 예약·확인사항·홈타이 가이드·고객센터·개인정보처리방침
- **총 265 페이지 / 1차 색인 168 / 단계 대기 noindex 97**

## 푸터

- **웹사이트 제작문의 · 제휴문의** 오렌지(앰버/골드) 프리미엄 버튼 → 텔레그램 연결
- 텔레그램: `content/site.py`의 `TELEGRAM_URL`에서 변경

## 색인 초고속화 (네이버·구글·빙)

빌드 시 자동 생성: `sitemap.xml`(lastmod 포함) · `rss.xml`(전 페이지) · `robots.txt`(전 봇 허용 +
사이트맵·RSS 안내) · `{INDEXNOW_KEY}.txt`(IndexNow 키 파일) · 메인 페이지 네이버 소유확인 메타.

**1) 소유확인 / 사이트맵 제출 (배포 후 1회)**
- 네이버 서치어드바이저: 메인 페이지 `naver-site-verification` 메타로 사이트 등록 →
  `sitemap.xml`·`rss.xml` 제출
- 구글 서치콘솔: 속성 등록 → `sitemap.xml` 제출 (`GOOGLE_SITE_VERIFICATION` 값을
  `content/site.py`에 넣으면 메인에 메타 출력)
- 빙 웹마스터: 사이트 추가 → 사이트맵 제출 (GSC 가져오기 가능)

**2) IndexNow 즉시 통보 (빙·네이버 등) — 글 올릴 때마다**
```bash
python3 build.py                      # 산출물 갱신(키 파일 포함)
# ↓ 배포 후(키 파일이 도메인 루트에 올라간 뒤) 실행
python3 tools/indexnow.py             # 사이트맵 전체 일괄 통보(첫 통보)
python3 tools/indexnow.py /seoul/gangnam-gu/yeoksam-dong/   # 특정 URL만
```
IndexNow는 `api.indexnow.org` 한 곳에 보내면 빙·네이버 등 참여 엔진에 전파됩니다.
키 파일(`/{KEY}.txt`)이 도메인에 배포된 뒤 실행해야 검증됩니다.

**3) 구글은 IndexNow 미참여** → 사이트맵(GSC) + 자연 크롤링이 기본.
선택적으로 `tools/google_indexing.py`(서비스계정 필요, JobPosting/BroadcastEvent 위주 공식 지원).
참고: 구글·빙의 `sitemap ping` 엔드포인트는 2023년 폐지되어 사용하지 않습니다.

## 배포 전 할 일

1. `content/site.py`의 `BASE_URL`을 실제 도메인으로 변경 후 `python3 build.py` 재실행
2. `assets/favicon-32.png` · `apple-touch-icon.png` · `favicon.ico`는 이전 자산이 남아 있으므로 새 로고(구)로 재생성 권장(현재 SVG 파비콘·OG 이미지는 구구 마사지 브랜딩 적용 완료)
3. Google Search Console에 `sitemap.xml` 제출
4. GSC 유입·노출 데이터를 보고 `priority` 값을 조정해 2·3차 색인 단계적 확장

## 디자인

- **프리미엄 옵시디언 팔레트**: `#08090d` 베이스 + 앰버 오렌지 `#FF7A2F` + 골드 `#C9A35C`
- **Pretendard / Noto Serif KR** · **글래스모피즘 오버레이** · 골드 헤어라인 · 반응형 · 접근성(WAI-ARIA)
