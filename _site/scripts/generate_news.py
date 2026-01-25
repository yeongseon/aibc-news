#!/usr/bin/env python3
"""
AIBC 뉴스룸 AI 뉴스 생성 스크립트
매일 자동으로 뉴스를 생성하고 Jekyll 포스트로 저장합니다.
"""

import os
import json
import datetime
import requests
from typing import List, Dict, Any
from pathlib import Path

class AINewsGenerator:
    def __init__(self):
        self.posts_dir = Path("_posts")
        self.posts_dir.mkdir(exist_ok=True)
        self.categories = ["기술", "생활", "날씨", "정책"]
        
    def generate_news_content(self, topic: str) -> Dict[str, Any]:
        prompt = f"""
        주제: {topic}
        한국어로 뉴스 기사를 작성해주세요:
        1. 제목 (간결하고 임팩트 있게)
        2. 요약 (2-3문장)
        3. 본문 (500-800자)
        4. 태그 (3-5개)
        """
        
        news_data = {
            "title": f"{topic}에 대한 AI 생성 뉴스",
            "excerpt": f"{topic} 관련 최신 소식을 AI가 요약했습니다.",
            "content": f"이곳에 {topic}에 대한 상세 내용이 들어갑니다...",
            "tags": [topic, "AI", "뉴스"],
            "category": self._get_category(topic)
        }
        
        return news_data
    
    def _get_category(self, topic: str) -> str:
        topic_lower = topic.lower()
        if any(keyword in topic_lower for keyword in ["ai", "기술", "소프트웨어", "하드웨어"]):
            return "기술"
        elif any(keyword in topic_lower for keyword in ["날씨", "기상", "미세먼지"]):
            return "날씨"
        elif any(keyword in topic_lower for keyword in ["정책", "법안", "정부"]):
            return "정책"
        else:
            return "생활"
    
    def create_jekyll_post(self, news_data: Dict[str, Any]) -> str:
        now = datetime.datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        timezone = "+0900"
        
        safe_title = news_data["title"].replace(" ", "-").replace(":", "")
        safe_title = "".join(c for c in safe_title if c.isalnum() or c in ["-", "_"])
        filename = f"{date_str}-{safe_title[:50]}.md"
        
        front_matter = f"""---
title: "{news_data['title']}"
date: {date_str} {time_str} {timezone}
categories:
  - 뉴스
  - {news_data['category']}
tags:
{chr(10).join(f'  - {tag}' for tag in news_data['tags'])}
excerpt: "{news_data['excerpt']}"
---

"""
        
        post_content = front_matter + news_data['content']
        
        post_content += """

---

*이 기사는 AIBC 뉴스룸 AI 시스템에 의해 자동 생성되었습니다.*
"""
        
        filepath = self.posts_dir / filename
        filepath.write_text(post_content, encoding='utf-8')
        
        return str(filepath)
    
    def fetch_trending_topics(self) -> List[str]:
        topics = [
            "인공지능 최신 동향",
            "클라우드 컴퓨팅 혁신",
            "사이버 보안 이슈",
            "블록체인 기술 발전",
            "메타버스 플랫폼",
            "전기차 시장 동향",
            "재생에너지 정책",
            "스마트시티 구축"
        ]
        return topics[:3]
    
    def run(self):
        print("🤖 AIBC 뉴스 생성 시작...")
        
        topics = self.fetch_trending_topics()
        created_posts = []
        
        for topic in topics:
            print(f"📰 주제: {topic}")
            news_data = self.generate_news_content(topic)
            filepath = self.create_jekyll_post(news_data)
            created_posts.append(filepath)
            print(f"✅ 포스트 생성: {filepath}")
        
        print(f"\n🎉 총 {len(created_posts)}개의 뉴스 포스트가 생성되었습니다!")
        
        self.update_site()
        
    def update_site(self):
        print("\n🔨 Jekyll 사이트 빌드 중...")
        os.system("bundle exec jekyll build")
        print("✅ 빌드 완료!")
        
        if os.environ.get("DEPLOY_ENABLED") == "true":
            print("🚀 GitHub Pages로 배포 중...")
            os.system("git add _posts/")
            os.system(f'git commit -m "자동 뉴스 업데이트: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}"')
            os.system("git push origin main")
            print("✅ 배포 완료!")

def main():
    generator = AINewsGenerator()
    generator.run()

if __name__ == "__main__":
    main()