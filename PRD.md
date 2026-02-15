# [PRD] AI Broadcasting Channel (AIBC)

**작성일:** 2026-01-25  
**최종 수정:** 2026-02-15  
**작성자:** Project Owner  
**상태:** Draft (Phase 1)

---

## 1. 프로젝트 개요

AIBC는 공개 데이터를 수집하여 AI가 **중립적 뉴스 형식**으로 정리하고,
**카테고리별로 독립적으로 발행되는 자동 뉴스 채널**입니다.

본 서비스는 다음을 목표로 한다:
- 정리형 뉴스 전달
- GitHub 기반 경량 운영
- 카테고리별 독립 발행 구조
- GitHub Actions + REST API 병행 발행
- 유연한 편성 구성 지원

**카테고리(한글 표기):** 정치, 경제, 사회, 세계, 기술, 문화, 스포츠, 연예, 생활, 날씨  
**내부 키(영문):** politics, economy, society, world, tech, culture, sports, entertainment, life, weather

---

## 2. 발행 구조 원칙

### 2.1 발행 단위
- **1 포스트 = 1 뉴스**
- **카테고리별 독립 실행**
- 하루 여러 건 발행 가능

### 2.2 카테고리 독립성
각 카테고리는:
- 독립된 스케줄을 가질 수 있음
- 독립된 Collector를 사용
- 독립적으로 성공/실패
- 다른 카테고리에 영향 없음

### 2.3 스케줄 정책
- 스케줄은 고정이 아닌 **구성 가능한 설정 값**
- 카테고리별로 다른 실행 시간 설정 가능
- GitHub Actions cron을 통해 관리
- REST API는 시간과 무관하게 즉시 발행 가능

> 편성표는 운영 정책이며, 시스템 구조의 제약 조건이 아니다.

---

## 3. 콘텐츠 정책

### 3.1 뉴스 구조
각 뉴스는 다음을 포함합니다:
- 제목(18~26자, 카테고리 포함)
- 입력 시각 표기 (YYYY.MM.DD HH:MM)
- 기자 표기는 AI 모델명 (예: GPT-5.2)
- 2~4문장 본문
- 출처 최소 1개
- 수치 포함 시 기준시점 또는 발표일 명시
- 중립적 보도체
- 금칙어 금지
- (선택) 대표 이미지 (WEBP 권장, 최대 1200px)

---

## 4. 발행 경로

AIBC는 두 가지 발행 경로를 지원합니다.

### 4.1 GitHub Actions 기반 발행
- 카테고리별 워크플로 구성 가능
- 각 워크플로는 특정 카테고리만 처리
- 스케줄은 cron 설정으로 구성
- 실패는 카테고리 단위로 격리

### 4.2 REST API 기반 발행
- Azure Function에서 HTTP 요청 수신
- 특정 카테고리만 발행 가능
- 멱등성 보장
- **REST는 repository_dispatch 트리거(리모컨 역할)**
- 실제 발행/커밋/배포는 GitHub Actions가 수행

---

## 5. 멱등성 정책

### 5.1 파일명 규칙
`YYYY-MM-DD-<category>-<slug>.md`

### 5.2 slug 규칙
- economy → symbol 기반
- weather → city 기반
- 기타 → title slug + short hash

### 5.3 중복 정책
- 동일 파일 존재 시 기본 **skip**
- `force=true` 요청 시 **overwrite 허용**

---

## 6. 시스템 구성

### 6.1 Collector
카테고리별 Collector 분리:
- WeatherCollector
- MarketCollector
- LifestyleCollector
- HeadlineCollector (추후)

### 6.2 Writer
- JSON → 뉴스 본문 생성
- 2~4문장 구성
- 기준시점 자동 보강
- 중립적 보도체 유지

### 6.3 Quality Gate
카테고리별 개별 검증:
- 문장 수
- 금칙어
- 출처 존재
- 수치 포함 시 날짜 명시

### 6.4 Publisher
- Front Matter 생성
- 파일명 생성
- 멱등성 검사
- Git 커밋/푸시

---

## 7. REST API 설계

`POST /api/publish`

Request:
```json
{
  "run_date": "2026-02-15",
  "category": "economy",
  "force": false
}
```

---

## 8. 운영 원칙

- 카테고리별 독립 실행
- 일부 카테고리 실패 허용
- 스케줄은 유연하게 조정 가능
- REST 실행과 Actions 실행 간 충돌 방지

---

## 9. 요약

AIBC는 **공개 데이터 기반의 중립적 뉴스 정리 채널**이며,
카테고리별 독립 발행 구조와 Actions/REST 병행 발행을 통해
안정적이고 유연한 운영을 목표로 합니다.
