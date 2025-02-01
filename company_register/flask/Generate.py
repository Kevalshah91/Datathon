from flask import Flask, request, jsonify
import json
import os
import requests
import pandas as pd
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class AdMetrics:
    ad_id: str
    company_name: str
    domain: str
    impressions: int
    clicks: int
    hover_time: float
    hover_count: int
    ad_position: str

    @property
    def ctr(self) -> float:
        return self.clicks / self.impressions if self.impressions else 0

    @property
    def engagement_score(self) -> float:
        return (self.hover_count / self.impressions) * self.hover_time if self.impressions else 0

class MarketTrendAgent:
    def __init__(self, news_api_key: str):
        self.news_api_key = news_api_key
        self.trends_cache = {}

    def analyze_market_trends(self, company_name: str) -> Dict:
        trends = self._fetch_company_trends(company_name)
        return {
            'trends': trends,
            'overall_market_sentiment': self._analyze_market_sentiment(trends),
            'emerging_opportunities': self._identify_opportunities(trends)
        }

    def _fetch_company_trends(self, company_name: str) -> List[Dict]:
        url = 'https://newsapi.org/v2/everything'
        query = f"{company_name} ecommerce technology trends"
        params = {'q': query, 'apiKey': '4906f8d7d4564a9188d4b04329522c88', 'sortBy': 'publishedAt', 'pageSize': 3}
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json().get('articles', [])
            return [{'title': a['title'], 'sentiment': self._analyze_sentiment(a['title'])} for a in articles]
        except Exception as e:
            print(f"Error fetching trends for {company_name}: {str(e)}")
            return []

    def _analyze_sentiment(self, text: str) -> str:
        positive_words = ['growth', 'increase', 'success', 'popular', 'rising']
        negative_words = ['decline', 'decrease', 'fall', 'drop', 'loss']
        text = text.lower()
        positive_count = sum(text.count(word) for word in positive_words)
        negative_count = sum(text.count(word) for word in negative_words)
        return 'positive' if positive_count > negative_count else 'negative' if negative_count > positive_count else 'neutral'

    def _analyze_market_sentiment(self, trends: List[Dict]) -> str:
        sentiments = [article['sentiment'] for article in trends]
        return 'Growing market conditions' if sentiments.count('positive') > sentiments.count('negative') else 'Competitive market conditions' if sentiments.count('negative') > sentiments.count('positive') else 'Stable market conditions'

    def _identify_opportunities(self, trends: List[Dict]) -> List[str]:
        opportunities = []
        if any(a['sentiment'] == 'positive' for a in trends):
            opportunities.append("Potential for market expansion")
            opportunities.append("Opportunity for increased digital presence")
        return opportunities

class CustomerBehaviorAgent:
    def analyze_behavior(self, ads_data: List[AdMetrics]) -> Dict:
        engagement_by_position = {}
        for ad in ads_data:
            if ad.ad_position not in engagement_by_position:
                engagement_by_position[ad.ad_position] = []
            engagement_by_position[ad.ad_position].append({'hover_time': ad.hover_time, 'hover_count': ad.hover_count, 'ctr': ad.ctr})

        return {position: {'avg_hover_time': sum(d['hover_time'] for d in data) / len(data), 'avg_hover_count': sum(d['hover_count'] for d in data) / len(data), 'avg_ctr': sum(d['ctr'] for d in data) / len(data)} for position, data in engagement_by_position.items()}

class MarketingStrategySystem:
    def __init__(self, news_api_key: Optional[str] = None):
        self.news_api_key = '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'
        self.market_agent = MarketTrendAgent(self.news_api_key) if self.news_api_key else None
        self.behavior_agent = CustomerBehaviorAgent()

    def analyze_campaign(self, json_data: List[Dict]) -> Dict:
        company_info = {'name': json_data[0]['companyName'], 'domain': json_data[0]['domain']}
        ads_data = [AdMetrics(ad['adId'], ad['companyName'], ad['domain'], ad['impressions'], ad['clicks'], ad['hoverTime'], ad['hoverCount'], ad['position']) for ad in json_data]
        behavior_analysis = self.behavior_agent.analyze_behavior(ads_data)
        market_analysis = self.market_agent.analyze_market_trends(company_info['name']) if self.market_agent else {}
        return {'company_info': company_info, 'behavior_analysis': behavior_analysis, 'market_analysis': market_analysis}

app = Flask(__name__)
strategy_system = MarketingStrategySystem()

@app.route('/analyze_campaign', methods=['POST'])
def analyze_campaign():
    try:
        ad_data = request.get_json()
        if not ad_data:
            return jsonify({"error": "Invalid input data"}), 400
        results = strategy_system.analyze_campaign(ad_data)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
