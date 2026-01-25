# [Architecture] AI Broadcasting Channel (AIBC)

**작성일:** 2026-01-25
**기준 PRD:** `PRD.md`
**범위:** Phase 1 (Daily Brief 자동화)

---

## 1. 문서 목적 및 범위

* 본 문서는 AIBC Phase 1의 상세 아키텍처를 정의한다.
* 데이터 수집 → 기사 작성 → 품질 검증 → 발행의 완전 자동화 파이프라인을 대상으로 한다.
* 배포 대상은 Jekyll 기반 GitHub Pages이며, 운영은 GitHub Actions로 스케줄링한다.

---

## 2. 시스템 컨텍스트

### 2.1 외부 시스템

* **데이터 소스**: 정부/기관 공개 데이터, 공식 발표, 지표 API, 기상청 등
* **LLM API**: Writer Agent의 기사 작성
* **GitHub Actions**: 스케줄 실행 및 자동 배포
* **GitHub Pages**: 정적 사이트 호스팅

### 2.2 내부 사용자

* **운영자**: 실패 알림 확인, 데이터 소스 관리, 정책/가드레일 수정

---

## 3. 핵심 요구사항 매핑

### 3.1 기능 요구사항

* Collector → Writer → Publisher 파이프라인을 100% 자동 실행
* 발행 시간: 매일 06:30 KST (허용 지연 ±30분)
* 발행 실패 시 부분 발행 금지
* 품질 검증(Quality Gate) 불통과 시 발행 중단

### 3.2 품질 및 편집 가드레일

* 700~1,000자, 3~5개 항목, 항목당 2~4문장
* 항목당 맥락/인사이트 2~3문장 포함
* 출처 최소 1개/항목, 전체 4개 이상
* 동일 출처 50% 초과 금지
* 금칙어 미포함, 과장 표현 배제, 수치/인용 기준시점 포함

---

## 4. 상위 아키텍처

### 4.1 구성 요소

1) **Scheduler (GitHub Actions)**
   * 매일 06:30 KST에 파이프라인 실행
   * 실패 시 알림 전송

2) **Collector Agent**
   * 외부 데이터 수집 및 구조화 JSON 생성

3) **Writer Agent**
   * Collector JSON을 기반으로 마크다운 기사 생성

4) **Quality Gate**
   * 길이/항목 수/출처/금칙어/수치 기준시점 확인

5) **Publisher Agent**
   * Front Matter 생성
   * Jekyll `_posts` 포맷으로 변환 후 커밋/푸시
   * 실패 처리 및 롤백

6) **Repository Storage**
   * `_posts` 내 데일리 브리핑 저장
   * 로그 및 실행 결과 기록

### 4.2 데이터 흐름 (개요)

```
Schedule (06:30 KST)
  -> Collector (외부 데이터 수집)
    -> Writer (기사 작성)
      -> Quality Gate (검증)
        -> Publisher (front matter + _posts commit/push)
          -> GitHub Pages 배포
```

---

## 5. 상세 설계

### 5.1 Collector Agent

**입력:** 없음 (내부 스케줄링)

**출력:** 구조화 JSON

* 헤드라인 3~5건, 시장 지표 2~3건, 날씨 1~2건, 생활 1건
* 각 항목에 출처 URL 포함
* 모든 항목은 `date` 기준으로 묶음

**출력 스키마 (Phase 1)**

```json
{
  "date": "YYYY-MM-DD",
  "items": [
    {
      "type": "headline|market|weather|lifestyle",
      "title": "...",
      "facts": ["...", "..."],
      "sources": [
        {"name": "기관/매체", "url": "https://...", "published_at": "YYYY-MM-DD"}
      ]
    }
  ]
}
```

**수집 실패 정책**

* 최대 2회 재시도, 10분 간격
* 실패 시 당일 발행 중단 및 알림

### 5.2 Writer Agent

**입력:** Collector JSON

**출력:** 마크다운 본문 (항목 3~5개)

**작성 규칙**

* 항목당 2~4문장
* 맥락/인사이트 2~3문장 자연스럽게 포함
* 수치/인용 시 발표일 또는 기준시점 명시
* 중립적 보도체, 과장/평가 표현 금지

**작성 실패 정책**

* 1회 재시도 후 실패 시 발행 중단

### 5.3 Quality Gate

**입력:** Writer 출력 마크다운 + Collector JSON

**검증 항목**

* 분량: 700~1,000자
* 항목 수: 3~5개
* 항목당 문장 수: 2~4문장
* 항목당 출처 >= 1개, 전체 출처 >= 4개
* 동일 출처 50% 초과 금지
* 금칙어 포함 여부
* 수치/인용 기준시점 명시 여부

**출력:** Pass/Fail + 실패 사유 목록

### 5.4 Publisher Agent

**역할**

* Front Matter 생성
* `_posts/YYYY-MM-DD-aibc-briefing.md` 생성
* Git 커밋 및 푸시
* 실패 시 이전 상태 유지

**Front Matter (Phase 1)**

```yaml
---
layout: post
title: "[AIBC 브리핑] YYYY-MM-DD 주요 이슈"
author: AIBC Desk
categories: [ News ]
date: YYYY-MM-DD
summary: "오늘의 핵심 이슈 3~5건 요약"
sources:
  - "기관/매체명 - URL"
---
```

**발행 실패 정책**

* 커밋/푸시 실패 시 롤백
* 실패 로그와 원인 저장
* 당일 브리핑 발행 금지

---

## 6. 실행 및 스케줄링

### 6.1 GitHub Actions

**스케줄:** 매일 06:30 KST (Cron: `30 21 * * *` UTC 전일)

**파이프라인 단계**

1. Checkout
2. Python 환경 구성
3. Collector 실행
4. Writer 실행
5. Quality Gate 실행
6. Publisher 실행 (성공 시에만)

### 6.2 실패 알림

* Collector/Writer/Publisher 실패 시 Actions 실패 알림
* Quality Gate 실패 시 당일 발행 중단 및 실패 사유 기록

---

## 7. 데이터 및 저장 구조

### 7.1 저장소 구조 (권장)

```
.
├─ _posts/
│  └─ YYYY-MM-DD-aibc-briefing.md
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
   └─ daily-brief.yml
```

### 7.2 실행 식별자

* 실행 ID: `YYYY-MM-DD`
* 동일 날짜 재실행 시 idempotent 처리

---

## 8. 보안 및 정책 준수

* API 키는 GitHub Secrets로 관리
* 출처가 불명확한 데이터는 수집 제외
* 직접 인용은 1~2문장 이내, 반드시 출처 표기
* 투자/의료/법률 조언 제공 금지

---

## 9. 테스트 및 검증 전략

* Collector: 소스별 단위 테스트 (스키마 검증 포함)
* Writer: 샘플 입력 기반 골든 테스트 (문장 수, 길이)
* Quality Gate: 규칙별 실패 케이스 테스트
* Publisher: dry-run 모드에서 파일 생성 검증

---

## 10. 운영 및 모니터링

* 로그: 단계별 처리 시간, 실패 사유 저장
* 지표: 성공률, 평균 처리 시간, 재시도 횟수
* 알림: GitHub Actions 실패 알림 채널 연동

---

## 11. 확장 고려사항 (Phase 2+)

* 주간/월간 요약 파이프라인 추가
* 데이터 분석/인사이트 전용 Writer 템플릿
* 유튜브/숏폼 자동 변환 단계 추가

---

## 12. 결정 사항 요약

* Phase 1은 GitHub Actions + Jekyll + GitHub Pages로 단일 파이프라인 운용
* 모든 발행은 Quality Gate 통과를 전제로 하며, 실패 시 부분 발행 금지
* Collector/Writer/Publisher 간 계약(JSON/Markdown) 고정
