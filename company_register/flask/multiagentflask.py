from flask import Flask, request, jsonify
from pymongo import MongoClient
import google.generativeai as genai
from duckduckgo_search import DDGS
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# RAG-specific imports
from llama_index.core import (
    VectorStoreIndex,
    ServiceContext,
    load_index_from_storage,
    StorageContext,
    Document
)
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.groq import Groq

# Load environment variables
load_dotenv()
app = Flask(__name__)

# Configure MongoDB
MONGO_URI = "###################################"
client = MongoClient(MONGO_URI)
db = client.test
interaction_collection = db.adinteractions

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

# Configure RAG components
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = Groq(model="llama-3.2-1b-preview", api_key=os.getenv("GROQ_API_KEY"))
service_context = ServiceContext.from_defaults(embed_model=embed_model, llm=llm)

class MarketResearchAgent:
    def __init__(self, domain: str):
        self.domain = domain
        self.ddgs = DDGS()
        
    def gather_market_insights(self) -> List[Dict]:
        query = f"{self.domain} market trends latest innovations advertising strategy"
        search_results = list(self.ddgs.text(query, max_results=5))
        
        formatted_results = []
        for result in search_results:
            formatted_results.append({
                "title": result.get("title", "No Title"),
                "content": result.get("body", "No Content"),
                "source": result.get("link", "No Source")
            })
        
        return formatted_results

class RAGAnalysisAgent:
    def __init__(self, json_data: List[Dict]):
        self.json_data = json_data
        
    def prepare_documents(self) -> List[Document]:
        documents = []
        for entry in self.json_data:
            text_representation = f"""
            Company ID: {entry['companyName']}
            Industry: {entry['domain']}
            Ad ID: {entry['adId']}
            Position: {entry['position']}
            Hover Time (sec): {entry['hoverTime']}
            Hover Count: {entry['hoverCount']}
            Clicks: {entry['clicks']}
            Impressions: {entry['impressions']}
            Click-Through Rate (CTR): {round(entry['clicks'] / entry['impressions'] * 100, 2)}%
            """
            documents.append(Document(text=text_representation))
        return documents

    def create_or_load_index(self, documents: List[Document], storage_path: str = "./ad_storage"):
        try:
            storage_context = StorageContext.from_defaults(persist_dir=storage_path)
            index = load_index_from_storage(storage_context, service_context=service_context)
        except:
            text_splitter = SentenceSplitter(chunk_size=600, chunk_overlap=100)
            nodes = text_splitter.get_nodes_from_documents(documents)
            index = VectorStoreIndex.from_documents(
                documents,
                service_context=service_context
            )
            index.storage_context.persist(persist_dir=storage_path)
        return index

    def analyze_data(self) -> str:
        documents = self.prepare_documents()
        index = self.create_or_load_index(documents)
        query_engine = index.as_query_engine(service_context=service_context)
        
        analysis_query = """
        Analyze the advertising data and provide insights on:
        1. Best performing ad positions
        2. Engagement patterns
        3. Click-through rate trends
        4. Key performance indicators
        5. Recommendations for improvement
        """
        
        response = query_engine.query(analysis_query)
        return str(response)

class StrategyGenerationAgent:
    def __init__(self, market_research: List[Dict], rag_analysis: str, budget: float):
        self.market_research = market_research
        self.rag_analysis = rag_analysis
        self.budget = budget
        
    def generate_strategy(self) -> str:
        # Format market research for prompt
        market_insights = "\n".join([
            f"Source: {item['title']}\nInsight: {item['content'][:200]}..."
            for item in self.market_research
        ])
        
        prompt = f"""
        Create a comprehensive digital marketing strategy based on:

        MARKET RESEARCH:
        {market_insights}

        DATA ANALYSIS:
        {self.rag_analysis}

        BUDGET: ${self.budget:,.2f}

        Provide a strategic plan that includes:
        1. Key Market Opportunities
        2. Tactical Recommendations
        3. Budget Allocation Strategy
        4. Implementation Timeline
        5. Expected Outcomes
        
        Format the response in clear sections without special characters.
        """
        
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error in strategy generation: {str(e)}"

class BudgetOptimizer:
    def __init__(self, interaction_data: pd.DataFrame):
        self.data = interaction_data
        
    def calculate_roi(self) -> Dict[str, float]:
        self.data['revenue'] = self.data['clicks'] * 2.5
        self.data['cost'] = self.data['impressions'] * 0.01
        self.data['roi'] = (self.data['revenue'] - self.data['cost']) / self.data['cost']
        return {
            row['adId']: row['roi'] 
            for _, row in self.data.iterrows()
        }
    
    def optimize_budget(self, total_budget: float) -> Dict[str, float]:
        roi_per_ad = self.calculate_roi()
        total_roi = sum(roi_per_ad.values())
        return {
            ad_id: (roi / total_roi) * total_budget
            for ad_id, roi in roi_per_ad.items()
        }

class IntegratedMarketingAgent:
    def __init__(self, data: pd.DataFrame, domain_topic: str, total_budget: float):
        self.data = data
        self.domain = domain_topic
        self.budget = total_budget
        self.budget_optimizer = BudgetOptimizer(self.data)
        
    def generate_comprehensive_strategy(self) -> Dict[str, Any]:
        try:
            # 1. Market Research Agent
            market_agent = MarketResearchAgent(self.domain)
            market_insights = market_agent.gather_market_insights()
            
            # 2. RAG Analysis Agent
            rag_agent = RAGAnalysisAgent(self.data.to_dict('records'))
            rag_analysis = rag_agent.analyze_data()
            
            # 3. Strategy Generation Agent (Gemini)
            strategy_agent = StrategyGenerationAgent(market_insights, rag_analysis, self.budget)
            final_strategy = strategy_agent.generate_strategy()
            
            # 4. Budget Optimization
            budget_allocation = self.budget_optimizer.optimize_budget(self.budget)
            
            # Prepare final output
            output = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "domain": self.domain,
                "total_budget": self.budget,
                "market_research": market_insights,
                "data_analysis": rag_analysis,
                "budget_allocation": {
                    str(k): float(v) for k, v in budget_allocation.items()
                },
                "final_strategy": final_strategy,
                "metrics": {
                    "average_ctr": float(self.data['clicks'].sum() / self.data['impressions'].sum() * 100),
                    "average_hover_time": float(self.data['hoverTime'].mean()),
                    "total_impressions": int(self.data['impressions'].sum()),
                    "total_clicks": int(self.data['clicks'].sum())
                }
            }
            
            return output
            
        except Exception as e:
            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "status": "error",
                "error_message": str(e)
            }

@app.route('/generate-strategy', methods=['POST'])
def generate_strategy():
    try:
        data = request.get_json()
        domain = data.get('domain')
        # budget = float(data.get('budget', 50000))
        budget=50000
        
        if not domain:
            return jsonify({
                "error": "Missing required parameter: domain"
            }), 400
            
        # Fetch data from MongoDB
        interactions = list(interaction_collection.find({}, {'_id': 0}))
        if not interactions:
            return jsonify({
                "error": "No interaction data found in database"
            }), 404
            
        df = pd.DataFrame(interactions)
        agent = IntegratedMarketingAgent(df, domain, budget)
        results = agent.generate_comprehensive_strategy()
        return jsonify(results)
        
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500

if __name__ == "__main__":
    try:
        client.admin.command('ping')
        print("Successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        exit(1)
        
    app.run(debug=True, port=9000)
