from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Dict
import random

app = FastAPI(title="TenderAI API", version="1.0")

# Разрешаем запросы с любого домена
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TenderAnalyzer:
    def __init__(self):
        self.profit_factors = {
            'price': 0.3,
            'competition': 0.25, 
            'customer_reliability': 0.2,
            'deadline': 0.15,
            'prepayment': 0.1
        }
    
    def calculate_score(self, tender_data: Dict) -> float:
        """Наш уникальный алгоритм оценки тендера"""
        score = 0
        
        # Анализ цены (чем выше цена - тем лучше)
        price_score = min(tender_data.get('price', 0) / 1000000, 1.0)
        score += price_score * self.profit_factors['price']
        
        # Анализ конкуренции (чем меньше конкурентов - тем лучше)
        competition_score = 1.0 - min(tender_data.get('competitors', 10) / 20, 1.0)
        score += competition_score * self.profit_factors['competition']
        
        # Надежность заказчика (рандомная оценка для демо)
        customer_score = tender_data.get('customer_rating', 0.5)
        score += customer_score * self.profit_factors['customer_reliability']
        
        # Сроки выполнения (чем больше срок - тем лучше)
        deadline_score = min(tender_data.get('deadline_days', 30) / 90, 1.0)
        score += deadline_score * self.profit_factors['deadline']
        
        # Предоплата (чем больше предоплата - тем лучше)
        prepayment_score = tender_data.get('prepayment_percent', 0) / 100
        score += prepayment_score * self.profit_factors['prepayment']
        
        return round(score * 10, 2)

analyzer = TenderAnalyzer()

# Тестовые данные госзакупок (позже заменим реальными)
MOCK_TENDERS = [
    {
        "id": 1,
        "title": "Поставка оргтехники для Минобразования",
        "price": 2500000,
        "competitors": 3,
        "customer_rating": 0.8,
        "deadline_days": 60,
        "prepayment_percent": 30,
        "category": "Оборудование"
    },
    {
        "id": 2, 
        "title": "Ремонт помещений администрации",
        "price": 1500000,
        "competitors": 12,
        "customer_rating": 0.6,
        "deadline_days": 45,
        "prepayment_percent": 20,
        "category": "Строительство"
    },
    {
        "id": 3,
        "title": "Разработка программного обеспечения",
        "price": 5000000,
        "competitors": 5,
        "customer_rating": 0.9,
        "deadline_days": 90,
        "prepayment_percent": 50,
        "category": "IT"
    }
]

@app.get("/")
async def root():
    return {"message": "TenderAI API работает!", "status": "success"}

@app.get("/api/tenders")
async def get_tenders():
    """Получить список тендеров с AI-оценкой"""
    tenders_with_scores = []
    
    for tender in MOCK_TENDERS:
        score = analyzer.calculate_score(tender)
        tender_with_score = tender.copy()
        tender_with_score['ai_score'] = score
        tender_with_score['recommendation'] = "Рекомендуем" if score > 6.0 else "Рассмотреть" if score > 4.0 else "Не рекомендуется"
        tenders_with_scores.append(tender_with_score)
    
    # Сортируем по AI-оценке (лучшие первыми)
    tenders_with_scores.sort(key=lambda x: x['ai_score'], reverse=True)
    
    return {"tenders": tenders_with_scores}

@app.get("/api/analyze")
async def analyze_tender(price: int, competitors: int, deadline: int, prepayment: int = 0):
    """Проанализировать конкретный тендер"""
    tender_data = {
        "price": price,
        "competitors": competitors,
        "deadline_days": deadline,
        "prepayment_percent": prepayment,
        "customer_rating": 0.7  # Базовая оценка
    }
    
    score = analyzer.calculate_score(tender_data)
    
    return {
        "ai_score": score,
        "recommendation": "Рекомендуем" if score > 6.0 else "Рассмотреть" if score > 4.0 else "Не рекомендуется",
        "analysis": f"Оценка выгодности: {score}/10"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
