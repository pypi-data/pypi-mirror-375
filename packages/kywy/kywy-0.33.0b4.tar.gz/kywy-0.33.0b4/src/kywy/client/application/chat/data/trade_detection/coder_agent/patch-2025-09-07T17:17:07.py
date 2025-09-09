# -- DATA SECTION: start

@kawa_tool(
    outputs={'feed_id': str, 'platform': str, 'post_date': datetime, 'content': str, 'user_id': str, 'engagement_score': float, 'post_type': str}
)
def social_media_feeds_generator():
    fake = Faker()
    data = []
    
    platforms = ['Twitter', 'Reddit', 'LinkedIn']
    nasdaq_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'CRM', 'PYPL', 'INTC', 'AMD', 'ORCL', 'ADBE', 'CSCO']
    
    advice_templates = [
        "Consider buying {stock} as it shows strong momentum with recent earnings beat",
        "Technical analysis suggests {stock} might hit resistance at current levels, consider taking profits",
        "Long-term outlook for {stock} remains bullish despite short-term volatility",
        "Options play: selling puts on {stock} at support level could be profitable",
        "Watch for {stock} breakout above {price} for potential upside to {target}",
        "Dividend investors should look at {stock} for consistent yield and growth",
        "Risk management: set stop loss for {stock} at {price} to protect downside",
        "Earnings season play: {stock} historically outperforms post-earnings",
        "Sector rotation favors {stock} in current market environment",
        "DCA strategy recommended for {stock} over next 3-6 months"
    ]
    
    for i in range(1000):
        feed_id = f"feed_{i+1:04d}"
        platform = fake.random_element(platforms)
        post_date = fake.date_time_between(start_date='-60d', end_date='now')
        user_id = f"user_{fake.random_int(1, 200):03d}"
        
        # Select 1-3 stocks for the advice
        num_stocks = fake.random_int(1, 3)
        selected_stocks = fake.random_elements(nasdaq_stocks, length=num_stocks, unique=True)
        
        # Create content with stock advice
        template = fake.random_element(advice_templates)
        if len(selected_stocks) == 1:
            stock = selected_stocks[0]
            price = fake.random_int(50, 500)
            target = price + fake.random_int(10, 100)
            content = template.format(stock=stock, price=price, target=target)
        else:
            stocks_text = ', '.join(selected_stocks)
            content = f"Portfolio allocation suggestion: {stocks_text}. " + fake.text(max_nb_chars=200)
        
        engagement_score = fake.random_int(10, 10000) if fake.random.random() > 0.3 else fake.random_int(1, 100)
        post_type = fake.random_element(['Analysis', 'Tip', 'Alert', 'Educational', 'Opinion'])
        
        data.append([feed_id, platform, post_date, content, user_id, float(engagement_score), post_type])
    
    df = pd.DataFrame(data, columns=['feed_id', 'platform', 'post_date', 'content', 'user_id', 'engagement_score', 'post_type'])
    return df

social_feeds_dataset = app.create_dataset(
    name='Social Media Feeds',
    generator=social_media_feeds_generator,
)

@kawa_tool(
    outputs={'stock_symbol': str, 'company_name': str, 'sector': str, 'market_cap': float, 'price': float, 'volume': float, 'beta': float, 'pe_ratio': float, 'dividend_yield': float, 'analyst_rating': str}
)
def nasdaq_stocks_generator():
    fake = Faker()
    data = []
    
    stocks_data = [
        ('AAPL', 'Apple Inc.', 'Technology'),
        ('MSFT', 'Microsoft Corporation', 'Technology'),
        ('GOOGL', 'Alphabet Inc.', 'Technology'),
        ('AMZN', 'Amazon.com Inc.', 'Consumer Discretionary'),
        ('TSLA', 'Tesla Inc.', 'Consumer Discretionary'),
        ('NVDA', 'NVIDIA Corporation', 'Technology'),
        ('META', 'Meta Platforms Inc.', 'Technology'),
        ('NFLX', 'Netflix Inc.', 'Communication Services'),
        ('CRM', 'Salesforce Inc.', 'Technology'),
        ('PYPL', 'PayPal Holdings Inc.', 'Financial Services'),
        ('INTC', 'Intel Corporation', 'Technology'),
        ('AMD', 'Advanced Micro Devices', 'Technology'),
        ('ORCL', 'Oracle Corporation', 'Technology'),
        ('ADBE', 'Adobe Inc.', 'Technology'),
        ('CSCO', 'Cisco Systems Inc.', 'Technology')
    ]
    
    for symbol, company, sector in stocks_data:
        market_cap = fake.random_int(100, 3000) * 1000000000  # In billions
        price = fake.random_int(50, 500) + fake.random.random()
        volume = fake.random_int(1000000, 100000000)
        beta = fake.random.random() * 2 + 0.5
        pe_ratio = fake.random_int(15, 50) + fake.random.random()
        dividend_yield = fake.random.random() * 3 if fake.random.random() > 0.3 else 0.0
        analyst_rating = fake.random_element(['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell'])
        
        data.append([symbol, company, sector, float(market_cap), float(price), float(volume), 
                    float(beta), float(pe_ratio), float(dividend_yield), analyst_rating])
    
    df = pd.DataFrame(data, columns=['stock_symbol', 'company_name', 'sector', 'market_cap', 'price', 
                                   'volume', 'beta', 'pe_ratio', 'dividend_yield', 'analyst_rating'])
    return df

nasdaq_stocks_dataset = app.create_dataset(
    name='NASDAQ Stocks',
    generator=nasdaq_stocks_generator,
)

@kawa_tool(
    outputs={'user_id': str, 'username': str, 'full_name': str, 'follower_count': float, 'following_count': float, 'account_age_years': float, 'verified_status': float, 'bio': str, 'trading_experience': str, 'credentials': str, 'success_rate': float, 'total_posts': float}
)
def social_media_users_generator():
    fake = Faker()
    data = []
    
    trading_experiences = ['Beginner', 'Intermediate', 'Advanced', 'Professional', 'Expert']
    credentials = ['None', 'CFA', 'Financial Advisor', 'Portfolio Manager', 'Investment Banker', 'Day Trader', 'Hedge Fund Manager']
    
    for i in range(200):
        user_id = f"user_{i+1:03d}"
        username = fake.user_name()
        full_name = fake.name()
        
        # Create realistic distributions for credibility factors
        trading_exp = fake.random_element(trading_experiences)
        credential = fake.random_element(credentials)
        
        # Adjust follower count based on experience and credentials
        base_followers = 100
        if trading_exp in ['Professional', 'Expert']:
            base_followers *= fake.random_int(5, 50)
        elif trading_exp == 'Advanced':
            base_followers *= fake.random_int(2, 20)
        elif credential in ['CFA', 'Portfolio Manager', 'Hedge Fund Manager']:
            base_followers *= fake.random_int(10, 100)
        
        follower_count = base_followers + fake.random_int(0, base_followers * 2)
        following_count = fake.random_int(50, min(2000, follower_count))
        account_age_years = fake.random.random() * 10 + 0.5
        verified_status = 1.0 if (credential != 'None' and fake.random.random() > 0.7) else 0.0
        
        bio = f"{trading_exp} trader specializing in {fake.random_element(['tech stocks', 'growth investing', 'value investing', 'options trading', 'swing trading'])}. {credential if credential != 'None' else 'Self-taught investor'}."
        
        # Success rate based on experience and credentials
        if trading_exp == 'Expert' and credential in ['CFA', 'Portfolio Manager', 'Hedge Fund Manager']:
            success_rate = fake.random_int(70, 90) + fake.random.random()
        elif trading_exp in ['Professional', 'Advanced']:
            success_rate = fake.random_int(60, 80) + fake.random.random()
        else:
            success_rate = fake.random_int(40, 70) + fake.random.random()
        
        total_posts = fake.random_int(10, 1000)
        
        data.append([user_id, username, full_name, float(follower_count), float(following_count), 
                    float(account_age_years), verified_status, bio, trading_exp, credential, 
                    float(success_rate), float(total_posts)])
    
    df = pd.DataFrame(data, columns=['user_id', 'username', 'full_name', 'follower_count', 'following_count', 
                                   'account_age_years', 'verified_status', 'bio', 'trading_experience', 
                                   'credentials', 'success_rate', 'total_posts'])
    return df

social_users_dataset = app.create_dataset(
    name='Social Media Users',
    generator=social_media_users_generator,
)

model = app.create_model(
    dataset=social_feeds_dataset,
)

# -- DATA SECTION: end

# -- RELATIONSHIPS SECTION: start

user_relationship = model.create_relationship(
    name='User Profile',
    dataset=social_users_dataset,
    link={'user_id': 'user_id'}
)

user_relationship.add_column(
    name='username',
    aggregation='FIRST',
    new_column_name='username',
)

user_relationship.add_column(
    name='follower_count',
    aggregation='FIRST',
    new_column_name='follower_count',
)

user_relationship.add_column(
    name='account_age_years',
    aggregation='FIRST',
    new_column_name='account_age_years',
)

user_relationship.add_column(
    name='verified_status',
    aggregation='FIRST',
    new_column_name='verified_status',
)

user_relationship.add_column(
    name='trading_experience',
    aggregation='FIRST',
    new_column_name='trading_experience',
)

user_relationship.add_column(
    name='credentials',
    aggregation='FIRST',
    new_column_name='credentials',
)

user_relationship.add_column(
    name='success_rate',
    aggregation='FIRST',
    new_column_name='success_rate',
)

user_relationship.add_column(
    name='total_posts',
    aggregation='FIRST',
    new_column_name='total_posts',
)

# -- RELATIONSHIPS SECTION: end

# -- VARIABLES SECTION: start

model.create_variable(
    name='Trust Threshold',
    kawa_type='decimal',
    initial_value=6.0,
)

model.create_variable(
    name='Experience Weight',
    kawa_type='decimal',
    initial_value=0.3,
)

# -- VARIABLES SECTION: end

# -- METRICS SECTION: start

model.create_metric(
    name='experience_score',
    formula="""
    CASE 
        WHEN "trading_experience" = 'Expert' THEN 10.0
        WHEN "trading_experience" = 'Professional' THEN 8.0
        WHEN "trading_experience" = 'Advanced' THEN 6.0
        WHEN "trading_experience" = 'Intermediate' THEN 4.0
        ELSE 2.0
    END
    """,
)

model.create_metric(
    name='credential_score',
    formula="""
    CASE 
        WHEN "credentials" = 'Hedge Fund Manager' THEN 10.0
        WHEN "credentials" = 'Portfolio Manager' THEN 9.0
        WHEN "credentials" = 'CFA' THEN 8.0
        WHEN "credentials" = 'Investment Banker' THEN 7.0
        WHEN "credentials" = 'Financial Advisor' THEN 6.0
        WHEN "credentials" = 'Day Trader' THEN 4.0
        ELSE 1.0
    END
    """,
)

model.create_metric(
    name='social_credibility_score',
    formula="""
    CASE 
        WHEN "verified_status" = 1 THEN 5.0
        WHEN "follower_count" > 10000 THEN 4.0
        WHEN "follower_count" > 1000 THEN 3.0
        WHEN "follower_count" > 500 THEN 2.0
        ELSE 1.0
    END + 
    CASE 
        WHEN "account_age_years" > 5 THEN 3.0
        WHEN "account_age_years" > 2 THEN 2.0
        WHEN "account_age_years" > 1 THEN 1.0
        ELSE 0.0
    END
    """,
)

model.create_metric(
    name='user_trust_score',
    formula="""
    ("experience_score" * "Experience Weight") + 
    ("credential_score" * 0.4) + 
    ("social_credibility_score" * 0.2) + 
    ("success_rate" * 0.1)
    """,
)

model.create_metric(
    name='post_trust_category',
    formula="""
    CASE 
        WHEN "user_trust_score" >= "Trust Threshold" THEN 'Highly Trusted'
        WHEN "user_trust_score" >= ("Trust Threshold" - 2) THEN 'Moderately Trusted'
        WHEN "user_trust_score" >= ("Trust Threshold" - 4) THEN 'Low Trust'
        ELSE 'Not Trusted'
    END
    """,
)

model.create_metric(
    name='trusted_post_flag',
    formula="""
    CASE 
        WHEN "user_trust_score" >= "Trust Threshold" THEN 1.0
        ELSE 0.0
    END
    """,
)

# -- METRICS SECTION: end
