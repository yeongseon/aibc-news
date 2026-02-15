from typing import Dict, Any, List, Tuple


class SimpleWriter:
    def write(self, collector_payload: Dict[str, Any]) -> Tuple[str, str]:
        run_date = collector_payload["date"]
        items: List[Dict[str, Any]] = collector_payload["items"]

        lines = []

        for idx, item in enumerate(items, start=1):
            title = item["title"]
            facts = item.get("facts", [])
            fact_text = "· ".join(facts) if facts else "핵심 변화 요약"

            sentence_1 = (
                f"{title} 소식입니다. {fact_text} 흐름이 확인됐으며, 발표일 {run_date} 기준으로 정리했습니다."
            )
            sentence_2 = (
                "관련 지표는 단기 변동이 가능해 추이를 점검해야 하며, 정책 및 수요 변화와의 연계도 살펴볼 필요가 있습니다."
            )
            sentence_3 = (
                "관계 기관 발표에 따르면 핵심 방향은 안정적 운영이며, 추가 세부 내용은 후속 공지에서 확인될 예정입니다."
            )

            paragraph = f"{idx}) {sentence_1} {sentence_2} {sentence_3}"
            lines.append(paragraph)
            lines.append("")

        body = "\n".join(lines).strip() + "\n"
        summary = "핵심 이슈 요약"
        return body, summary
