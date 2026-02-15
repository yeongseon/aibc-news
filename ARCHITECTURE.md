# [Architecture] AI Broadcasting Channel (AIBC)

**작성일:** 2026-01-25
**최종 수정:** 2026-02-15
**기준 PRD:** `PRD.md`
**범위:** Phase 1 (카테고리별 자동 발행)

---

## 1. 문서 목적 및 범위

* AIBC Phase 1의 아키텍처를 정의한다.
* **카테고리별 독립 발행**과 **REST 트리거(repository_dispatch)**를 포함한다.
* 배포 대상은 Jekyll 기반 GitHub Pages이며, 운영은 GitHub Actions + REST 병행한다.

---

## 2. 시스템 컨텍스트

### 2.1 외부 시스템

* **데이터 소스**: 공개 지표/기관 데이터/API
* **LLM API**: Writer Agent의 기사 작성
* **GitHub Actions**: 카테고리별 스케줄 실행
* **GitHub Pages**: 정적 사이트 호스팅
* **Azure Functions**: REST 발행 엔드포인트

### 2.2 내부 사용자

* **운영자**: 실패 알림 확인, 데이터 소스 관리, 정책/가드레일 수정

---

## 3. 핵심 요구사항 매핑

### 3.1 기능 요구사항

* 카테고리별 Collector → Writer → Publisher 파이프라인 독립 실행
* GitHub Actions cron 스케줄 또는 REST로 즉시 발행
* 발행 실패 시 **부분 발행 금지**
* Quality Gate 불통과 시 발행 중단

### 3.2 품질 및 편집 가드레일

* 1 포스트 = 1 뉴스
* 2~4문장, 출처 최소 1개
* 금칙어 금지, 수치 포함 시 기준시점/발표일 표기

---

## 4. 상위 아키텍처

### 4.1 구성 요소

1) **Scheduler (GitHub Actions)**
   * 카테고리별 스케줄 실행
   * 실패 시 알림 전송

2) **REST Trigger (Azure Functions)**
   * HTTP 요청으로 repository_dispatch 트리거
   * 멱등성 보장

3) **Collector Agent**
   * 카테고리별 데이터 수집

4) **Writer Agent**
   * 수집 결과 → 마크다운 본문 생성

5) **Quality Gate**
   * 문장 수/금칙어/출처/기준시점 검증

6) **Publisher Agent**
   * Front Matter 생성
   * 파일명 생성
   * `_posts`에 저장
   * Git 커밋/푸시

---

## 5. 상세 설계

### 5.1 Collector

**카테고리별 분리**
- MarketCollector
- WeatherCollector
- LifestyleCollector
- HeadlineCollector (추후 확장)

### 5.2 Writer

* 2~4문장 구성
* 중립적 보도체 유지
* 수치 포함 시 기준시점/발표일 명시

### 5.3 Quality Gate

* 카테고리별 규칙 적용
* 문장 수, 금칙어, 출처, 기준시점 검사

### 5.4 Publisher

* Front Matter 생성
* 파일명 규칙 적용: `YYYY-MM-DD-<category>-<slug>.md`
* 멱등성 검사 (기본 skip, force 시 overwrite)
* Git 커밋/푸시 수행

---

## 6. 실행 및 스케줄링

### 6.1 GitHub Actions

* 카테고리별 워크플로
* 각 워크플로는 CATEGORY 환경 변수로 필터 실행

### 6.2 REST API

* `POST /api/publish`
* `category`, `run_date`, `force`, `idempotency_key` 지원
* REST는 **repository_dispatch 트리거** 역할만 수행
* 실제 발행/커밋은 Actions에서 처리

---

## 7. 저장 구조

```
.
├─ _posts/
│  └─ YYYY-MM-DD-<category>-<slug>.md
├─ data/
│  ├─ collector/YYYY-MM-DD.json
│  └─ quality/YYYY-MM-DD.json
├─ logs/
│  └─ YYYY-MM-DD.log
├─ src/
│  ├─ collector/
│  ├─ writer/
│  ├─ quality/
│  └─ publisher/
└─ .github/workflows/
   └─ daily-brief-*.yml
```

---

## 8. 운영 및 모니터링

* 단계별 로그 기록
* GitHub Actions 실패 시 이슈 생성
* REST 호출은 멱등성 키로 중복 방지

---

## 9. 결정 사항 요약

* 카테고리별 독립 발행 구조
* Actions/REST 병행 지원 (REST는 repository_dispatch 트리거)
* 커밋/푸시는 Actions에서 수행
* 멱등성은 파일명 규칙 + Actions 재실행 정책으로 보장
