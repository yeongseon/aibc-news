# [Architecture] AI Broadcasting Channel (AIBC)

**작성일:** 2026-01-25
**최종 수정:** 2026-03-07
**기준 PRD:** `PRD.md`
**범위:** 현재 저장소 기준 Phase 1 발행 경로 (Ready News → Publisher → GitHub Pages)

---

## 1. 문서 목적 및 범위

* AIBC Phase 1의 현재 구현 아키텍처를 정의합니다.
* **Ready News 적재 후 발행**과 **REST 트리거(repository_dispatch)**를 포함합니다.
* 카테고리(한글): 정치, 경제, 사회, 세계, 기술, 문화, 스포츠, 연예, 생활, 날씨
* 배포 대상은 Jekyll 기반 GitHub Pages이며, 운영은 GitHub Actions + REST 병행합니다.

---

## 2. 시스템 컨텍스트

### 2.1 외부 시스템

* **콘텐츠 공급자**: Ready News JSON을 생성하는 외부 도구/운영 프로세스
* **GitHub Actions**: 카테고리별 스케줄 실행
* **GitHub Pages**: 정적 사이트 호스팅
* **Azure Functions**: REST 발행 엔드포인트

### 2.2 내부 사용자

* **운영자**: 실패 알림 확인, 데이터 소스 관리, 정책/가드레일 수정

---

## 3. 핵심 요구사항 매핑

### 3.1 기능 요구사항

* 날짜별 `data/ready-news/YYYY-MM-DD/*.json` 적재 후 발행
* GitHub Actions push/workflow_dispatch 또는 REST(repository_dispatch)로 발행
* 스키마 검증 실패 시 발행 중단
* 동일 파일명은 기본 skip, `force` 시 overwrite

### 3.2 품질 및 편집 가드레일

* 1 포스트 = 1 뉴스
* 출처 최소 1개
* `meta.input_at`, `meta.updated_at` 필수
* (선택) 대표 이미지

---

## 4. 상위 아키텍처

### 4.1 구성 요소

1) **Scheduler (GitHub Actions)**
   * 카테고리별 스케줄 실행
   * 실패 시 알림 전송

2) **REST Trigger (Azure Functions)**
   * HTTP 요청으로 repository_dispatch 트리거
   * 멱등성 보장

3) **Ready News Validator**
   * JSON 파일 로드
   * 필수 필드/카테고리/이미지 메타 검증

4) **Publisher Agent**
   * Front Matter 생성
   * 파일명 생성
   * `_posts`에 저장
   * Git 커밋/푸시

---

## 5. 상세 설계

### 5.1 Ready News Intake

* 입력 위치: `data/ready-news/YYYY-MM-DD/*.json`
* 단일 JSON 또는 `items` 배열 포맷 지원
* 카테고리 필터 적용 가능

### 5.2 Validation

* 필수 필드 검사: `date`, `category`, `title`, `summary`, `body`, `sources`, `meta.input_at`, `meta.updated_at`
* 스키마 버전 검사: `schema_version == 1.1`
* 생성 메타 검사: `generation.model`, `generation.reporter_id`, `generation.data_sources`
* 카테고리 허용값 검사
* `media.hero_image` 사용 시 `url`, `alt` 검사

### 5.3 Publisher

* Front Matter 생성
* 파일명 규칙 적용: `YYYY-MM-DD-HHMM-<category>-<slug>.md`
* 멱등성 검사 (기본 skip, force 시 overwrite)
* GitHub Actions에서 Git 커밋/푸시 수행

---

## 6. 실행 및 스케줄링

### 6.1 GitHub Actions

* `publish-article.yml`: push 기반 일괄 발행
* `publish-article-*.yml`: 카테고리별 수동 실행 및 `repository_dispatch` 발행

### 6.2 REST API

* `POST /api/publish`
* `category`, `run_date`, `force`, `idempotency_key` 지원
* REST는 **repository_dispatch 트리거** 역할만 수행
* 카테고리별 workflow가 조건부로 실행되어 실제 발행/커밋 수행

---

## 7. 저장 구조

```
.
├─ _posts/
│  └─ YYYY-MM-DD-HHMM-<category>-<slug>.md
├─ data/
│  └─ ready-news/YYYY-MM-DD/*.json
├─ src/
│  └─ publisher/
└─ .github/workflows/
   └─ publish-article-*.yml
```

---

## 8. 운영 및 모니터링

* GitHub Actions 실패 시 이슈 생성
* 발행 결과는 `_posts/`와 Actions artifact로 확인
* REST 호출은 `client_payload` 기반으로 카테고리별 workflow에 전달

---

## 9. 결정 사항 요약

* Ready News 적재 후 발행하는 구조
* Actions/REST 병행 지원 (REST는 repository_dispatch 트리거)
* 커밋/푸시는 Actions에서 수행
* 멱등성은 파일명 규칙 + `force` 정책으로 보장
