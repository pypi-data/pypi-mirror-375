from kywy.client.kawa_client import KawaClient
from kywy.client.kawa_decorators import kawa_tool
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from faker import Faker

kawa = KawaClient.load_client_from_environment()

app = kawa.app(
    application_name='Social Media Financial Advice Analytics',
    sidebar_color='#1a472a',
)

# -- DATA SECTION: start

@kawa_tool(
    outputs={'post_id': str, 'platform': str, 'post_date': date, 'content': str, 'user_id': str, 'likes': float, 'shares': float, 'comments': float}
)
def social_media_feeds_generator():
    fake = Faker()
    platforms = ['Twitter', 'Reddit', 'LinkedIn']
    nasdaq_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA', 'PYPL', 'ADBE', 'INTC', 'CSCO', 'PEP', 'AVGO', 'TXN', 'QCOM', 'COST', 'SBUX', 'AMD', 'INTU']
    
    advice_templates = [
        "Consider buying {} as it shows strong quarterly growth",
        "Time to sell {} before the market correction hits",
        "Hold onto {} for long-term gains, fundamentals are solid",
        "Watch out for {} earnings report next week, could be volatile",
        "Diversify with {} and {} for balanced portfolio",
        "{} is undervalued right now, perfect entry point",
        "Avoid {} until the regulatory issues are resolved",
        "Strong buy signal on {} based on technical analysis",
        "Portfolio allocation: 40% {}, 30% {}, 30% cash",
        "Exit {} positions before quarterly results"
    ]
    
    data = []
    for i in range(300):
        post_id = f"post_{i+1:04d}"
        platform = np.random.choice(platforms)
        post_date = fake.date_between(start_date='-365d', end_date='today')
        user_id = f"user_{np.random.randint(1, 101):03d}"
        
        # Generate content with stock advice
        template = np.random.choice(advice_templates)
        if '{}' in template:
            if template.count('{}') == 1:
                stock = np.random.choice(nasdaq_stocks)
                content = template.format(stock)
            elif template.count('{}') == 2:
                stocks = np.random.choice(nasdaq_stocks, 2, replace=False)
                content = template.format(stocks[0], stocks[1])
            else:
                stocks = np.random.choice(nasdaq_stocks, 3, replace=False)
                content = template.format(stocks[0], stocks[1], stocks[2])
        else:
            content = template
            
        # Platform-specific engagement metrics
        if platform == 'Twitter':
            likes = np.random.exponential(50)
            shares = np.random.exponential(10)
            comments = np.random.exponential(5)
        elif platform == 'Reddit':
            likes = np.random.exponential(100)
            shares = np.random.exponential(20)
            comments = np.random.exponential(15)
        else:  # LinkedIn
            likes = np.random.exponential(30)
            shares = np.random.exponential(5)
            comments = np.random.exponential(8)
            
        data.append([post_id, platform, post_date, content, user_id, likes, shares, comments])
    
    df = pd.DataFrame(data, columns=['post_id', 'platform', 'post_date', 'content', 'user_id', 'likes', 'shares', 'comments'])
    return df

@kawa_tool(
    outputs={'stock_symbol': str, 'company_name': str, 'sector': str, 'market_cap': float, 'pe_ratio': float, 'dividend_yield': float, 'beta': float, 'price': float, 'volume': float, 'analyst_rating': str}
)
def nasdaq_stocks_generator():
    fake = Faker()
    
    stocks_data = [
        ('AAPL', 'Apple Inc.', 'Technology', 3000000, 28.5, 0.52, 1.2),
        ('GOOGL', 'Alphabet Inc.', 'Technology', 1800000, 22.1, 0.0, 1.1),
        ('MSFT', 'Microsoft Corporation', 'Technology', 2800000, 32.4, 0.68, 0.9),
        ('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary', 1500000, 45.2, 0.0, 1.3),
        ('TSLA', 'Tesla Inc.', 'Consumer Discretionary', 800000, 65.8, 0.0, 2.1),
        ('META', 'Meta Platforms Inc.', 'Technology', 900000, 18.9, 0.0, 1.4),
        ('NFLX', 'Netflix Inc.', 'Communication Services', 200000, 35.7, 0.0, 1.2),
        ('NVDA', 'NVIDIA Corporation', 'Technology', 2200000, 78.4, 0.09, 1.8),
        ('PYPL', 'PayPal Holdings Inc.', 'Financial Services', 80000, 42.1, 0.0, 1.5),
        ('ADBE', 'Adobe Inc.', 'Technology', 220000, 41.2, 0.0, 1.1),
        ('INTC', 'Intel Corporation', 'Technology', 180000, 12.8, 1.53, 0.8),
        ('CSCO', 'Cisco Systems Inc.', 'Technology', 210000, 16.4, 2.84, 0.9),
        ('PEP', 'PepsiCo Inc.', 'Consumer Staples', 240000, 25.1, 2.81, 0.6),
        ('AVGO', 'Broadcom Inc.', 'Technology', 550000, 19.8, 1.88, 1.2),
        ('TXN', 'Texas Instruments Inc.', 'Technology', 160000, 21.5, 2.75, 1.0),
        ('QCOM', 'QUALCOMM Inc.', 'Technology', 190000, 16.2, 2.23, 1.3),
        ('COST', 'Costco Wholesale Corporation', 'Consumer Staples', 280000, 38.9, 0.57, 0.8),
        ('SBUX', 'Starbucks Corporation', 'Consumer Discretionary', 120000, 28.4, 2.11, 1.1),
        ('AMD', 'Advanced Micro Devices Inc.', 'Technology', 220000, 52.3, 0.0, 1.9),
        ('INTU', 'Intuit Inc.', 'Technology', 180000, 65.1, 0.68, 1.2)
    ]
    
    ratings = ['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']
    
    data = []
    for symbol, name, sector, base_market_cap, base_pe, base_dividend, base_beta in stocks_data:
        market_cap = base_market_cap * np.random.uniform(0.8, 1.2)
        pe_ratio = base_pe * np.random.uniform(0.9, 1.1)
        dividend_yield = base_dividend * np.random.uniform(0.8, 1.2)
        beta = base_beta * np.random.uniform(0.9, 1.1)
        price = np.random.uniform(50, 500)
        volume = np.random.exponential(1000000)
        analyst_rating = np.random.choice(ratings, p=[0.15, 0.35, 0.35, 0.1, 0.05])
        
        data.append([symbol, name, sector, market_cap, pe_ratio, dividend_yield, beta, price, volume, analyst_rating])
    
    df = pd.DataFrame(data, columns=['stock_symbol', 'company_name', 'sector', 'market_cap', 'pe_ratio', 'dividend_yield', 'beta', 'price', 'volume', 'analyst_rating'])
    return df

@kawa_tool(
    outputs={'user_id': str, 'username': str, 'follower_count': float, 'verified_status': float, 'account_age_years': float, 'finance_experience_years': float, 'education_level': str, 'professional_background': str, 'previous_accuracy_score': float, 'engagement_rate': float}
)
def user_profiles_generator():
    fake = Faker()
    
    education_levels = ['High School', 'Bachelor', 'Master', 'PhD', 'CFA', 'MBA']
    backgrounds = ['Financial Analyst', 'Portfolio Manager', 'Day Trader', 'Investment Advisor', 'Retail Investor', 'Hedge Fund Manager', 'Financial Blogger', 'Economics Professor', 'Bank Executive', 'Fintech Entrepreneur']
    
    data = []
    for i in range(100):
        user_id = f"user_{i+1:03d}"
        username = fake.user_name()
        
        # Professional users have more followers and credibility
        is_professional = np.random.choice([0, 1], p=[0.7, 0.3])
        
        if is_professional:
            follower_count = np.random.lognormal(10, 1.5)
            verified_status = np.random.choice([0, 1], p=[0.3, 0.7])
            account_age_years = np.random.uniform(3, 15)
            finance_experience_years = np.random.uniform(5, 25)
            education_level = np.random.choice(['Master', 'PhD', 'CFA', 'MBA'], p=[0.3, 0.2, 0.3, 0.2])
            professional_background = np.random.choice(['Financial Analyst', 'Portfolio Manager', 'Investment Advisor', 'Hedge Fund Manager', 'Economics Professor', 'Bank Executive'], p=[0.2, 0.2, 0.2, 0.1, 0.15, 0.15])
            previous_accuracy_score = np.random.uniform(0.6, 0.9)
            engagement_rate = np.random.uniform(0.05, 0.15)
        else:
            follower_count = np.random.lognormal(7, 1)
            verified_status = np.random.choice([0, 1], p=[0.9, 0.1])
            account_age_years = np.random.uniform(1, 8)
            finance_experience_years = np.random.uniform(0, 10)
            education_level = np.random.choice(['High School', 'Bachelor', 'Master'], p=[0.2, 0.5, 0.3])
            professional_background = np.random.choice(['Day Trader', 'Retail Investor', 'Financial Blogger', 'Fintech Entrepreneur'], p=[0.3, 0.4, 0.2, 0.1])
            previous_accuracy_score = np.random.uniform(0.3, 0.7)
            engagement_rate = np.random.uniform(0.01, 0.08)
            
        data.append([user_id, username, follower_count, verified_status, account_age_years, finance_experience_years, education_level, professional_background, previous_accuracy_score, engagement_rate])
    
    df = pd.DataFrame(data, columns=['user_id', 'username', 'follower_count', 'verified_status', 'account_age_years', 'finance_experience_years', 'education_level', 'professional_background', 'previous_accuracy_score', 'engagement_rate'])
    return df

social_media_dataset = app.create_dataset(
    name='Social Media Financial Feeds',
    generator=social_media_feeds_generator,
)

nasdaq_stocks_dataset = app.create_dataset(
    name='NASDAQ Stocks Data',
    generator=nasdaq_stocks_generator,
)

user_profiles_dataset = app.create_dataset(
    name='User Profiles',
    generator=user_profiles_generator,
)

model = app.create_model(
    dataset=social_media_dataset,
)

# -- DATA SECTION: end

# -- RELATIONSHIPS SECTION: start

# -- RELATIONSHIPS SECTION: end

# -- VARIABLES SECTION: start

# -- VARIABLES SECTION: end

# -- METRICS SECTION: start

# -- METRICS SECTION: end

# -- DASHBOARD SECTION: start

# -- DASHBOARD SECTION: end

app.publish()
