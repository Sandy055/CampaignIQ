import pandas as pd
import numpy as np
from faker import Faker
import random
import os

fake = Faker()
np.random.seed(42)
random.seed(42)

# --- Customers ---
n_customers = 500
customer_ids = [f"CUST_{i:04d}" for i in range(1, n_customers + 1)]

customers = pd.DataFrame({
    "customer_id": customer_ids,
    "customer_name": [fake.name() for _ in range(n_customers)],
    "email": [fake.email() for _ in range(n_customers)],
    "region": [random.choice(["North", "South", "East", "West"]) for _ in range(n_customers)],
    "segment": [random.choice(["Enterprise", "SMB", "Consumer"]) for _ in range(n_customers)],
    "signup_date": [fake.date_between(start_date="-3y", end_date="-6m") for _ in range(n_customers)],
})

# --- Campaigns ---
campaigns = pd.DataFrame({
    "campaign_id": [f"CAMP_{i:03d}" for i in range(1, 11)],
    "campaign_name": [
        "Spring Sale", "Email Blast Q1", "Referral Push", "Holiday Deals",
        "Re-engagement", "Summer Launch", "VIP Loyalty", "Product Upsell",
        "Win-back Q3", "Year End Promo"
    ],
    "channel": [random.choice(["Email", "Social", "Paid Search", "Referral"]) for _ in range(10)],
    "start_date": pd.date_range(start="2024-01-01", periods=10, freq="5W"),
    "budget": [random.randint(5000, 50000) for _ in range(10)],
})

# --- Interactions ---
n_interactions = 3000
interactions = pd.DataFrame({
    "interaction_id": [f"INT_{i:05d}" for i in range(1, n_interactions + 1)],
    "customer_id": [random.choice(customer_ids) for _ in range(n_interactions)],
    "campaign_id": [random.choice(campaigns["campaign_id"].tolist()) for _ in range(n_interactions)],
    "interaction_date": [fake.date_between(start_date="-2y", end_date="today") for _ in range(n_interactions)],
    "clicked": [random.choice([0, 1]) for _ in range(n_interactions)],
    "converted": [random.choice([0, 0, 0, 1]) for _ in range(n_interactions)],
    "revenue_generated": [round(random.uniform(0, 500), 2) for _ in range(n_interactions)],
})

# --- Churn flags ---
customers["churned"] = [random.choice([0, 0, 1]) for _ in range(n_customers)]
customers["lifetime_value"] = [round(random.uniform(100, 5000), 2) for _ in range(n_customers)]

# --- Save to CSV ---
os.makedirs("data", exist_ok=True)
customers.to_csv("data/customers.csv", index=False)
campaigns.to_csv("data/campaigns.csv", index=False)
interactions.to_csv("data/interactions.csv", index=False)

print("✅ Data generated successfully!")
print(f"   Customers: {len(customers)} rows")
print(f"   Campaigns: {len(campaigns)} rows")
print(f"   Interactions: {len(interactions)} rows")
