# -- RELATIONSHIPS SECTION: start

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

# -- RELATIONSHIPS SECTION: end
