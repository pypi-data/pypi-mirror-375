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

## 📝 Applied from patch "patch-2025-09-07T17:28:10.py"

@kawa_tool(
    outputs={'post_id': str, 'platform': str, 'post_date': date, 'content': str, 'user_id': str, 'likes': float, 'shares': float, 'comments': float}
)
def social_media_feeds_generator():
    from datetime import date, timedelta
    fake = Faker()
    platforms = ['Twitter', 'Reddit', 'LinkedIn']
    nasdaq_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NFLX', 'NVDA', 'PYPL', 'ADBE', 'INTC', 'CSCO', 'PEP', 'AVGO', 'TXN', 'QCOM', 'COST', 'SBUX', 'AMD', 'INTU', 'BKNG', 'GILD', 'MDLZ', 'ISRG', 'ADP', 'REGN', 'VRTX', 'LRCX', 'ATVI', 'FISV', 'MRNA', 'DXCM', 'CHTR', 'KLAC', 'NXPI', 'MELI', 'ORLY', 'CTAS', 'MNST', 'WDAY']
    
    advice_templates = [
        "Just analyzed {}'s quarterly earnings and the numbers look solid. Revenue up {}% YoY, margins expanding. I'm increasing my position by {}%. Also watching {} as a complementary play in the same sector. The technical indicators are showing strong momentum for both stocks. Target price for {} is ${} based on DCF analysis.",
        
        "Market correction incoming! Time to trim positions in overvalued names like {} and {}. I'm taking profits on {}% of my {} holdings and rotating into defensive plays. {} looks vulnerable with P/E at {}x while {} offers better value at current levels. Cash is king right now, keeping {}% in money market funds.",
        
        "Breaking: {} just announced a major partnership with a Fortune 500 company. This could be a game-changer for their cloud division. I'm seeing similar patterns in {} and {} - all three are positioned to benefit from the digital transformation trend. My allocation: {}% {}, {}% {}, {}% {}. Stop losses set at {}% below entry.",
        
        "Fed meeting tomorrow and I'm positioning for volatility. {} has shown resilience during rate hike cycles historically. Adding {} and {} to my portfolio as inflation hedges. These companies have pricing power and strong balance sheets. Expecting {}% upside in {} over next 6 months based on analyst upgrades.",
        
        "Sector rotation happening now! Money flowing out of growth into value. {} and {} are getting hammered unfairly - their fundamentals remain strong. I'm buying the dip on both. {} revenue guidance of ${}B for next quarter seems conservative. Technical support at ${} for {} looks solid.",
        
        "AI revolution is real and {} is leading the charge. Their GPU demand is through the roof. Also bullish on {} and {} as they integrate AI into their core products. Portfolio allocation: {}% in AI leaders, {}% in AI adopters. Risk management: position sizing based on volatility - {} gets {}% allocation due to higher beta.",
        
        "Earnings season strategy: Playing {} beat with options - buying calls expiring in 3 weeks. {} has beaten estimates for 8 straight quarters. Also watching {} and {} for potential surprises. Historical analysis shows {}% chance of post-earnings pop for stocks with similar patterns. Risk: {}% of portfolio max per trade.",
        
        "Supply chain issues finally easing for {}. Their margins should expand significantly in Q{}. Similar story for {} and {} - all three should benefit from normalized logistics costs. I'm targeting a {}% gain by year-end. {} specifically could see ${}+ if they execute their cost reduction plan.",
        
        "Dividend aristocrat {} just raised their payout by {}% - 25th consecutive year of increases. Adding this to my retirement portfolio along with {} and {}. These three provide a blended yield of {}% with solid coverage ratios. {} trades at only {}x forward earnings, significant discount to peers.",
        
        "Biotech breakout! {} FDA approval odds looking strong based on Phase 3 data. Stock could double if approved. Also watching {} and {} in the same therapeutic area. Diversifying risk across all three - {}% in each. Binary events like FDA approvals require careful position sizing. Max {}% portfolio exposure.",
        
        "Energy transition play: {} is dominating the EV charging infrastructure space. Partnering with {} for battery tech and {} for software integration. This trifecta could generate massive synergies. {} revenue could hit ${}B by 2026. Technical breakout above ${} would confirm bullish thesis.",
        
        "Consumer discretionary under pressure but {} showing relative strength. Their brand loyalty and pricing power are unmatched. Similar dynamics for {} and {} - all three have moats that competitors can't easily replicate. Dollar-cost averaging into all three over next 3 months. Target allocation: {}% total in consumer leaders.",
        
        "Cloud computing growth accelerating post-pandemic. {} Azure revenue up {}% QoQ, {} showing similar trends. Adding {} as a pure-play beneficiary. These three control {}% of global cloud market. {} trading at discount to growth rate - PEG ratio of only {}. Expecting re-rating higher.",
        
        "Semiconductor shortage creating winners and losers. {} inventory management has been exceptional while {} struggles with supply constraints. Also bullish on {} for their manufacturing efficiency. {} margins expanding to {}% vs industry average of {}%. Sector consolidation could drive further upside.",
        
        "Social media advertising spending rebounding strongly. {} revenue per user hitting new highs, {} engagement metrics improving. Even {} showing signs of stabilization after recent challenges. Digital ad spend projected to grow {}% annually through 2027. {} could see ${}+ stock price if they capture fair share.",
        
        "Healthcare innovation accelerating with AI integration. {} diagnostic tools showing {}% accuracy improvement, {} drug discovery platform cutting development time by {}%. Also watching {} for their telemedicine expansion. Combined addressable market exceeds ${}B. {} fundamentals support ${} fair value.",
        
        "Financial services disruption continuing with {} leading digital transformation. Their mobile banking adoption up {}% YoY while traditional banks lose market share. {} and {} showing similar digital-first strategies. Fintech sector trading at discount - {}% below 52-week highs despite strong fundamentals.",
        
        "Cybersecurity demand surging after recent breach incidents. {} revenue guidance raised for third consecutive quarter, {} winning major enterprise contracts. {} acquisition strategy creating comprehensive security platform. Industry growth rate of {}% annually supports premium valuations. {} target price: ${}.",
        
        "Renewable energy momentum building with new federal incentives. {} solar installations up {}% QoQ, {} wind projects accelerating globally. {} battery storage technology becoming cost-competitive with traditional grid infrastructure. Clean energy ETF allocation: {}% solar, {}% wind, {}% storage solutions.",
        
        "E-commerce penetration still has room to grow in emerging markets. {} international expansion strategy gaining traction, {} logistics network providing competitive advantage. {} payment processing volumes up {}% in developing countries. Long-term demographic trends support continued digital adoption. Combined upside potential: {}% over 24 months.",
        
        "Streaming wars intensifying but {} content strategy creating subscriber stickiness. {} gaming integration driving engagement while {} ad-supported tier improving unit economics. Media landscape consolidation could benefit market leaders. {} free cash flow turning positive in Q{}, supporting ${} price target based on DCF model.",
        
        "Autonomous vehicle timeline accelerating with {} Level 4 testing showing promising results. {} sensor technology and {} mapping data creating comprehensive ecosystem. Regulatory approval still key catalyst but technology readiness improving rapidly. Market size could reach ${}T by 2030. Risk-adjusted position sizing recommended.",
    ]
    
    data = []
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    
    for i in range(10000):
        post_id = f"post_{i+1:05d}"
        platform = np.random.choice(platforms)
        post_date = fake.date_between_dates(date_start=start_date, date_end=end_date)
        user_id = f"user_{np.random.randint(1, 101):03d}"
        
        # Generate content with realistic financial advice
        template = np.random.choice(advice_templates)
        
        # Count placeholders and fill them appropriately
        placeholder_count = template.count('{}')
        
        if placeholder_count > 0:
            fill_values = []
            stocks_used = []
            
            for j in range(placeholder_count):
                # Determine what type of placeholder this might be based on context
                if j < 6:  # First few are likely stocks
                    if j == 0 or np.random.random() < 0.7:  # Primary stock or high chance of new stock
                        stock = np.random.choice([s for s in nasdaq_stocks if s not in stocks_used[-2:]])
                        stocks_used.append(stock)
                        fill_values.append(stock)
                    else:  # Might reuse a recent stock
                        fill_values.append(np.random.choice(stocks_used) if stocks_used else np.random.choice(nasdaq_stocks))
                else:
                    # Fill with appropriate numbers based on context
                    if 'revenue up' in template.lower() or 'up' in template.lower():
                        fill_values.append(str(np.random.randint(5, 45)))
                    elif 'position' in template.lower() or '%' in template.lower():
                        fill_values.append(str(np.random.randint(5, 25)))
                    elif '$' in template.lower() or 'price' in template.lower():
                        fill_values.append(str(np.random.randint(50, 500)))
                    elif 'quarter' in template.lower() or 'q' in template.lower():
                        fill_values.append(str(np.random.randint(1, 4)))
                    elif 'billion' in template.lower() or 'b' in template.lower():
                        fill_values.append(str(np.random.randint(5, 50)))
                    elif 'ratio' in template.lower():
                        fill_values.append(f"{np.random.uniform(0.5, 3.0):.1f}")
                    else:
                        fill_values.append(str(np.random.randint(10, 100)))
            
            try:
                content = template.format(*fill_values)
            except:
                content = template.replace('{}', np.random.choice(nasdaq_stocks))
        else:
            content = template
        
        # Platform-specific engagement metrics with more realistic distributions
        if platform == 'Twitter':
            base_engagement = np.random.lognormal(3, 1.2)
            likes = max(1, base_engagement * np.random.uniform(0.8, 1.5))
            shares = max(0, base_engagement * np.random.uniform(0.1, 0.3))
            comments = max(0, base_engagement * np.random.uniform(0.05, 0.2))
        elif platform == 'Reddit':
            base_engagement = np.random.lognormal(4, 1.5)
            likes = max(1, base_engagement * np.random.uniform(0.5, 2.0))
            shares = max(0, base_engagement * np.random.uniform(0.2, 0.5))
            comments = max(0, base_engagement * np.random.uniform(0.3, 0.8))
        else:  # LinkedIn
            base_engagement = np.random.lognormal(2.5, 1)
            likes = max(1, base_engagement * np.random.uniform(0.6, 1.2))
            shares = max(0, base_engagement * np.random.uniform(0.05, 0.15))
            comments = max(0, base_engagement * np.random.uniform(0.1, 0.25))
        
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
        ('INTU', 'Intuit Inc.', 'Technology', 180000, 65.1, 0.68, 1.2),
        ('BKNG', 'Booking Holdings Inc.', 'Consumer Discretionary', 150000, 22.8, 0.0, 1.3),
        ('GILD', 'Gilead Sciences Inc.', 'Healthcare', 95000, 15.4, 4.12, 0.7),
        ('MDLZ', 'Mondelez International Inc.', 'Consumer Staples', 105000, 19.6, 2.35, 0.6),
        ('ISRG', 'Intuitive Surgical Inc.', 'Healthcare', 125000, 68.2, 0.0, 1.1),
        ('ADP', 'Automatic Data Processing Inc.', 'Technology', 110000, 28.9, 2.03, 0.8),
        ('REGN', 'Regeneron Pharmaceuticals Inc.', 'Healthcare', 85000, 12.7, 0.0, 0.9),
        ('VRTX', 'Vertex Pharmaceuticals Inc.', 'Healthcare', 115000, 24.3, 0.0, 1.0),
        ('LRCX', 'Lam Research Corporation', 'Technology', 95000, 18.5, 1.32, 1.6),
        ('ATVI', 'Activision Blizzard Inc.', 'Communication Services', 75000, 25.1, 0.47, 0.9),
        ('FISV', 'Fiserv Inc.', 'Technology', 85000, 22.8, 0.0, 1.1),
        ('MRNA', 'Moderna Inc.', 'Healthcare', 45000, 8.2, 0.0, 1.8),
        ('DXCM', 'DexCom Inc.', 'Healthcare', 55000, 45.7, 0.0, 1.3),
        ('CHTR', 'Charter Communications Inc.', 'Communication Services', 65000, 12.4, 0.0, 1.2),
        ('KLAC', 'KLA Corporation', 'Technology', 75000, 19.8, 1.05, 1.4),
        ('NXPI', 'NXP Semiconductors NV', 'Technology', 70000, 16.3, 2.89, 1.5),
        ('MELI', 'MercadoLibre Inc.', 'Consumer Discretionary', 85000, 55.2, 0.0, 1.9),
        ('ORLY', "O'Reilly Automotive Inc.", 'Consumer Discretionary', 65000, 24.6, 0.0, 1.0),
        ('CTAS', 'Cintas Corporation', 'Industrials', 45000, 32.1, 1.08, 1.1),
        ('MNST', 'Monster Beverage Corporation', 'Consumer Staples', 55000, 28.7, 0.0, 0.8),
        ('WDAY', 'Workday Inc.', 'Technology', 65000, 42.3, 0.0, 1.2)
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


## 📝 Applied from patch "patch-2025-09-07T17:28:56.py"

user_profiles_relationship = model.create_relationship(
    name='User Profiles',
    dataset=user_profiles_dataset,
    link={'user_id': 'user_id'}
)

user_profiles_relationship.add_column(
    name='username',
    aggregation='FIRST',
    new_column_name='username',
)

user_profiles_relationship.add_column(
    name='follower_count',
    aggregation='FIRST',
    new_column_name='follower_count',
)

user_profiles_relationship.add_column(
    name='verified_status',
    aggregation='FIRST',
    new_column_name='verified_status',
)

user_profiles_relationship.add_column(
    name='account_age_years',
    aggregation='FIRST',
    new_column_name='account_age_years',
)

user_profiles_relationship.add_column(
    name='finance_experience_years',
    aggregation='FIRST',
    new_column_name='finance_experience_years',
)

user_profiles_relationship.add_column(
    name='education_level',
    aggregation='FIRST',
    new_column_name='education_level',
)

user_profiles_relationship.add_column(
    name='professional_background',
    aggregation='FIRST',
    new_column_name='professional_background',
)

user_profiles_relationship.add_column(
    name='previous_accuracy_score',
    aggregation='FIRST',
    new_column_name='previous_accuracy_score',
)

user_profiles_relationship.add_column(
    name='engagement_rate',
    aggregation='FIRST',
    new_column_name='engagement_rate',
)


## 📝 Applied from patch "INITIAL SCRIPT"


## 📝 Applied from patch "INITIAL SCRIPT"


## 📝 Applied from patch "INITIAL SCRIPT"




app.publish()
