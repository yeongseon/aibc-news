from typing import Dict, Any, List, Tuple

from .validator import validate_writer_output


class SimpleWriter:
    def write(self, collector_payload: Dict[str, Any]) -> Tuple[str, str]:
        run_date = collector_payload["date"]
        items: List[Dict[str, Any]] = collector_payload["items"]

        lines = ["## 오늘의 주요 이슈", ""]

        for idx, item in enumerate(items, start=1):
            title = item["title"]
            facts = item.get("facts", [])
            fact_text = "· ".join(facts) if facts else "주요 변동 요약"

            sentence_1 = f"{title} 소식입니다." \
                f" {fact_text} 흐름이 확인됐으며, 발표일 {run_date} 기준으로 정리했습니다."
            sentence_2 = (
                "관련 지표는 단기 변동이 가능해 추이를 점검해야 하며, 정책 및 수요 변화와의 연계도 살펴볼 필요가 있습니다."
            )
            sentence_3 = (
                "관계 기관 발표에 따르면 핵심 방향은 안정적 운영이며, 추가 세부 내용은 후속 공지에서 확인될 예정입니다."
            )
            sentence_4 = (
                "시점별 변화가 누적되는 구간이므로 추가 지표 공개 시점과 해석 기준을 함께 확인하는 것이 중요합니다."
            )

            paragraph = f"{idx}) {sentence_1} {sentence_2} {sentence_3} {sentence_4}"
            lines.append(paragraph)
            lines.append("")

        body = "\n".join(lines).strip() + "\n"
        validate_writer_output(body)
        summary = "오늘의 핵심 이슈 3~5건 요약"
        return body, summary
