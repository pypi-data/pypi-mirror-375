from kywy.client.kawa_client import KawaClient
from kywy.client.kawa_decorators import kawa_tool
from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from faker import Faker

kawa = KawaClient.load_client_from_environment()

app = kawa.app(
    application_name='Tweet Trust Analysis',
    sidebar_color='#1e3a8a',
)

# -- DATA SECTION: start

@kawa_tool(
    outputs={'tweet_id': str, 'user_id': str, 'content': str, 'retweet_count': float, 'like_count': float, 'reply_count': float, 'created_date': datetime, 'is_verified': float, 'follower_count': float}
)
def tweet_data_generator():
    fake = Faker()
    data = []
    
    for i in range(500):
        tweet_id = f"tweet_{i:04d}"
        user_id = f"user_{np.random.randint(1, 101):03d}"
        content = fake.text(max_nb_chars=280)
        retweet_count = np.random.exponential(50) if np.random.random() > 0.3 else np.random.exponential(5)
        like_count = np.random.exponential(100) if np.random.random() > 0.3 else np.random.exponential(10)
        reply_count = np.random.exponential(20) if np.random.random() > 0.3 else np.random.exponential(2)
        created_date = fake.date_time_between(start_date='-30d', end_date='now')
        is_verified = 1.0 if np.random.random() > 0.8 else 0.0
        follower_count = np.random.exponential(1000) if is_verified else np.random.exponential(100)
        
        data.append([tweet_id, user_id, content, retweet_count, like_count, reply_count, created_date, is_verified, follower_count])
    
    df = pd.DataFrame(data, columns=['tweet_id', 'user_id', 'content', 'retweet_count', 'like_count', 'reply_count', 'created_date', 'is_verified', 'follower_count'])
    return df

tweet_dataset = app.create_dataset(
    name='Tweet Data',
    generator=tweet_data_generator,
)

@kawa_tool(
    outputs={'user_id': str, 'username': str, 'account_age_days': float, 'total_tweets': float, 'avg_engagement_rate': float, 'has_profile_picture': float}
)
def user_data_generator():
    fake = Faker()
    data = []
    
    for i in range(100):
        user_id = f"user_{i+1:03d}"
        username = fake.user_name()
        account_age_days = np.random.exponential(365) + 30
        total_tweets = np.random.exponential(500) + 10
        avg_engagement_rate = np.random.beta(2, 5) * 10
        has_profile_picture = 1.0 if np.random.random() > 0.2 else 0.0
        
        data.append([user_id, username, account_age_days, total_tweets, avg_engagement_rate, has_profile_picture])
    
    df = pd.DataFrame(data, columns=['user_id', 'username', 'account_age_days', 'total_tweets', 'avg_engagement_rate', 'has_profile_picture'])
    return df

user_dataset = app.create_dataset(
    name='User Data',
    generator=user_data_generator,
)

@kawa_tool(
    outputs={'tweet_id': str, 'fact_check_score': float, 'source_credibility': float, 'misinformation_flag': float}
)
def fact_check_data_generator():
    fake = Faker()
    data = []
    
    for i in range(500):
        tweet_id = f"tweet_{i:04d}"
        fact_check_score = np.random.beta(3, 2) * 10
        source_credibility = np.random.beta(4, 2) * 10
        misinformation_flag = 1.0 if np.random.random() < 0.1 else 0.0
        
        data.append([tweet_id, fact_check_score, source_credibility, misinformation_flag])
    
    df = pd.DataFrame(data, columns=['tweet_id', 'fact_check_score', 'source_credibility', 'misinformation_flag'])
    return df

fact_check_dataset = app.create_dataset(
    name='Fact Check Data',
    generator=fact_check_data_generator,
)

model = app.create_model(
    dataset=tweet_dataset,
)

# -- DATA SECTION: end

# -- RELATIONSHIPS SECTION: start

user_rel = model.create_relationship(
    name='User Info',
    dataset=user_dataset,
    link={'user_id': 'user_id'}
)

user_rel.add_column(
    name='account_age_days',
    aggregation='FIRST',
    new_column_name='account_age_days',
)

user_rel.add_column(
    name='total_tweets',
    aggregation='FIRST',
    new_column_name='total_tweets',
)

user_rel.add_column(
    name='avg_engagement_rate',
    aggregation='FIRST',
    new_column_name='avg_engagement_rate',
)

user_rel.add_column(
    name='has_profile_picture',
    aggregation='FIRST',
    new_column_name='has_profile_picture',
)

fact_check_rel = model.create_relationship(
    name='Fact Check Info',
    dataset=fact_check_dataset,
    link={'tweet_id': 'tweet_id'}
)

fact_check_rel.add_column(
    name='fact_check_score',
    aggregation='FIRST',
    new_column_name='fact_check_score',
)

fact_check_rel.add_column(
    name='source_credibility',
    aggregation='FIRST',
    new_column_name='source_credibility',
)

fact_check_rel.add_column(
    name='misinformation_flag',
    aggregation='FIRST',
    new_column_name='misinformation_flag',
)

# -- RELATIONSHIPS SECTION: end

# -- VARIABLES SECTION: start

model.create_variable(
    name='Trust Threshold',
    kawa_type='decimal',
    initial_value=6.0,
)

model.create_variable(
    name='Engagement Weight',
    kawa_type='decimal',
    initial_value=0.3,
)

# -- VARIABLES SECTION: end

# -- METRICS SECTION: start

model.create_metric(
    name='engagement_score',
    formula="""
    ("retweet_count" + "like_count" + "reply_count") / ("follower_count" + 1) * 100
    """,
)

model.create_metric(
    name='user_credibility_score',
    formula="""
    CASE 
        WHEN "is_verified" = 1 THEN 8.5
        ELSE 
            CASE 
                WHEN "account_age_days" > 365 AND "total_tweets" > 100 AND "has_profile_picture" = 1 THEN 7.0
                WHEN "account_age_days" > 180 AND "total_tweets" > 50 THEN 5.5
                WHEN "account_age_days" > 90 THEN 4.0
                ELSE 2.0
            END
    END
    """,
)

model.create_metric(
    name='content_trust_score',
    formula="""
    CASE 
        WHEN "misinformation_flag" = 1 THEN 0.0
        ELSE ("fact_check_score" * 0.6) + ("source_credibility" * 0.4)
    END
    """,
)

model.create_metric(
    name='engagement_trust_factor',
    formula="""
    CASE 
        WHEN "engagement_score" > 10 THEN 0.8
        WHEN "engagement_score" > 5 THEN 0.9
        WHEN "engagement_score" > 1 THEN 1.0
        ELSE 0.7
    END
    """,
)

model.create_metric(
    name='overall_trust_score',
    formula="""
    ("user_credibility_score" * 0.4) + 
    ("content_trust_score" * 0.4) + 
    ("engagement_score" * "Engagement Weight") * "engagement_trust_factor"
    """,
)

model.create_metric(
    name='trust_category',
    formula="""
    CASE 
        WHEN "overall_trust_score" >= "Trust Threshold" THEN 'Highly Trusted'
        WHEN "overall_trust_score" >= ("Trust Threshold" - 2) THEN 'Moderately Trusted'
        WHEN "overall_trust_score" >= ("Trust Threshold" - 4) THEN 'Low Trust'
        ELSE 'Not Trusted'
    END
    """,
)

model.create_metric(
    name='trust_flag',
    formula="""
    CASE 
        WHEN "overall_trust_score" >= "Trust Threshold" THEN 1.0
        ELSE 0.0
    END
    """,
)

# -- METRICS SECTION: end

# -- DASHBOARD SECTION: start

main_page = app.create_page('Tweet Trust Analysis Dashboard')

explanation_col = main_page.create_section('Dashboard Overview', 1)
explanation_col.text_widget(
    html='<h2>Tweet Trust Analysis Dashboard</h2><p>This dashboard analyzes the trustworthiness of tweets based on multiple factors including user credibility, content verification, and engagement patterns.</p><p>The <strong>Trust Threshold</strong> variable determines the minimum score for a tweet to be considered trusted. Adjusting this value will impact the trust categorization and trusted tweet count widgets.</p><p>The <strong>Engagement Weight</strong> variable controls how much engagement metrics influence the overall trust score, affecting all trust-related calculations and visualizations.</p>'
)

col1, col2, col3 = main_page.create_section('Trust Metrics', num_columns=3)

col1.indicator_chart(
    title='Average Trust Score',
    indicator='overall_trust_score',
    aggregation='AVERAGE',
    source=model,
)

col2.indicator_chart(
    title='Trusted Tweets Count',
    indicator='trust_flag',
    aggregation='SUM',
    source=model,
)

col3.indicator_chart(
    title='Total Tweets Analyzed',
    indicator='tweet_id',
    aggregation='COUNT',
    source=model,
)

col1, col2 = main_page.create_section('Trust Distribution', num_columns=2)

col1.pie_chart(
    title='Trust Categories Distribution',
    labels='trust_category',
    values='tweet_id',
    aggregation='COUNT',
    show_values=True,
    show_labels=True,
    source=model,
)

col2.bar_chart(
    title='Trust Scores by Verification Status',
    x='is_verified',
    y='overall_trust_score',
    aggregation='AVERAGE',
    show_values=True,
    source=model,
)

col1, col2 = main_page.create_section('Engagement vs Trust', num_columns=2)

col1.scatter_chart(
    title='Engagement Score vs Overall Trust Score',
    granularity='tweet_id',
    x='engagement_score',
    y='overall_trust_score',
    color='is_verified',
    aggregation_color='FIRST',
    source=model,
)

col2.line_chart(
    title='Trust Score Evolution Over Time',
    x='created_date',
    y='overall_trust_score',
    aggregation='AVERAGE',
    time_sampling='DAY',
    area=True,
    source=model,
)

# -- DASHBOARD SECTION: end

app.publish()
