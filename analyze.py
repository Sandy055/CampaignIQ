import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os

# --- Load CSVs ---
customers = pd.read_csv("data/customers.csv")
campaigns = pd.read_csv("data/campaigns.csv")
interactions = pd.read_csv("data/interactions.csv")

# --- Load into SQLite so we can run our SQL queries ---
conn = sqlite3.connect("data/campaigniq.db")
customers.to_sql("customers", conn, if_exists="replace", index=False)
campaigns.to_sql("campaigns", conn, if_exists="replace", index=False)
interactions.to_sql("interactions", conn, if_exists="replace", index=False)

print("✅ Data loaded into SQLite database")

# --- Run SQL Queries ---

# 1. Revenue per campaign
revenue_by_campaign = pd.read_sql_query("""
    SELECT 
        c.campaign_name, c.channel,
        COUNT(i.interaction_id) AS total_interactions,
        SUM(i.converted) AS total_conversions,
        ROUND(SUM(i.revenue_generated), 2) AS total_revenue,
        ROUND(AVG(i.revenue_generated), 2) AS avg_revenue_per_interaction
    FROM interactions i
    JOIN campaigns c ON i.campaign_id = c.campaign_id
    GROUP BY c.campaign_name, c.channel
    ORDER BY total_revenue DESC
""", conn)

# 2. Conversion rate by campaign
conversion_rate = pd.read_sql_query("""
    SELECT 
        c.campaign_name, c.channel,
        COUNT(i.interaction_id) AS total_interactions,
        SUM(i.converted) AS conversions,
        ROUND(100.0 * SUM(i.converted) / COUNT(i.interaction_id), 2) AS conversion_rate_pct
    FROM interactions i
    JOIN campaigns c ON i.campaign_id = c.campaign_id
    GROUP BY c.campaign_name, c.channel
    ORDER BY conversion_rate_pct DESC
""", conn)

# 3. Churn rate by segment
churn_by_segment = pd.read_sql_query("""
    SELECT 
        segment,
        COUNT(customer_id) AS total_customers,
        SUM(churned) AS churned_customers,
        ROUND(100.0 * SUM(churned) / COUNT(customer_id), 2) AS churn_rate_pct,
        ROUND(AVG(lifetime_value), 2) AS avg_lifetime_value
    FROM customers
    GROUP BY segment
    ORDER BY churn_rate_pct DESC
""", conn)

# 4. Revenue by region
revenue_by_region = pd.read_sql_query("""
    SELECT 
        cu.region,
        COUNT(DISTINCT i.customer_id) AS active_customers,
        SUM(i.converted) AS total_conversions,
        ROUND(SUM(i.revenue_generated), 2) AS total_revenue
    FROM interactions i
    JOIN customers cu ON i.customer_id = cu.customer_id
    GROUP BY cu.region
    ORDER BY total_revenue DESC
""", conn)

# 5. Monthly revenue trend
monthly_revenue = pd.read_sql_query("""
    SELECT 
        strftime('%Y-%m', interaction_date) AS month,
        COUNT(interaction_id) AS total_interactions,
        SUM(converted) AS total_conversions,
        ROUND(SUM(revenue_generated), 2) AS monthly_revenue
    FROM interactions
    GROUP BY month
    ORDER BY month ASC
""", conn)

conn.close()
print("✅ SQL queries executed successfully")

# --- Save query results ---
os.makedirs("outputs", exist_ok=True)
revenue_by_campaign.to_csv("outputs/revenue_by_campaign.csv", index=False)
conversion_rate.to_csv("outputs/conversion_rate.csv", index=False)
churn_by_segment.to_csv("outputs/churn_by_segment.csv", index=False)
revenue_by_region.to_csv("outputs/revenue_by_region.csv", index=False)
monthly_revenue.to_csv("outputs/monthly_revenue.csv", index=False)
print("✅ Query results saved to outputs/")

# --- Visualizations ---
sns.set_theme(style="whitegrid")
os.makedirs("outputs/charts", exist_ok=True)

# Chart 1: Revenue by Campaign
plt.figure(figsize=(12, 6))
sns.barplot(data=revenue_by_campaign, x="total_revenue", y="campaign_name", palette="Blues_d")
plt.title("Total Revenue by Campaign", fontsize=14, fontweight="bold")
plt.xlabel("Total Revenue ($)")
plt.ylabel("Campaign")
plt.tight_layout()
plt.savefig("outputs/charts/revenue_by_campaign.png")
plt.close()

# Chart 2: Conversion Rate by Campaign
plt.figure(figsize=(12, 6))
sns.barplot(data=conversion_rate, x="conversion_rate_pct", y="campaign_name", palette="Greens_d")
plt.title("Conversion Rate by Campaign (%)", fontsize=14, fontweight="bold")
plt.xlabel("Conversion Rate (%)")
plt.ylabel("Campaign")
plt.tight_layout()
plt.savefig("outputs/charts/conversion_rate.png")
plt.close()

# Chart 3: Churn Rate by Segment
plt.figure(figsize=(8, 5))
sns.barplot(data=churn_by_segment, x="segment", y="churn_rate_pct", palette="Reds_d")
plt.title("Churn Rate by Customer Segment (%)", fontsize=14, fontweight="bold")
plt.xlabel("Segment")
plt.ylabel("Churn Rate (%)")
plt.tight_layout()
plt.savefig("outputs/charts/churn_by_segment.png")
plt.close()

# Chart 4: Revenue by Region
plt.figure(figsize=(8, 5))
sns.barplot(data=revenue_by_region, x="region", y="total_revenue", palette="Purples_d")
plt.title("Total Revenue by Region", fontsize=14, fontweight="bold")
plt.xlabel("Region")
plt.ylabel("Total Revenue ($)")
plt.tight_layout()
plt.savefig("outputs/charts/revenue_by_region.png")
plt.close()

# Chart 5: Monthly Revenue Trend
plt.figure(figsize=(14, 5))
plt.plot(monthly_revenue["month"], monthly_revenue["monthly_revenue"], marker="o", color="steelblue", linewidth=2)
plt.title("Monthly Revenue Trend", fontsize=14, fontweight="bold")
plt.xlabel("Month")
plt.ylabel("Revenue ($)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/charts/monthly_revenue_trend.png")
plt.close()

print("✅ All charts saved to outputs/charts/")
print("\n📊 Summary Insights:")
print(f"   Top Campaign by Revenue: {revenue_by_campaign.iloc[0]['campaign_name']} (${revenue_by_campaign.iloc[0]['total_revenue']:,})")
print(f"   Highest Conversion Rate: {conversion_rate.iloc[0]['campaign_name']} ({conversion_rate.iloc[0]['conversion_rate_pct']}%)")
print(f"   Highest Churn Segment:   {churn_by_segment.iloc[0]['segment']} ({churn_by_segment.iloc[0]['churn_rate_pct']}%)")
print(f"   Top Revenue Region:      {revenue_by_region.iloc[0]['region']} (${revenue_by_region.iloc[0]['total_revenue']:,})")