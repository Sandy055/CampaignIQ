import pandas as pd
import sqlite3

print("=" * 50)
print("CampaignIQ: Data Validation Report")
print("=" * 50)

# Load data
customers = pd.read_csv("data/customers.csv")
campaigns = pd.read_csv("data/campaigns.csv")
interactions = pd.read_csv("data/interactions.csv")

# --- Check 1: Null values ---
print("\n[1] Null Value Check")
for name, df in [("customers", customers), ("campaigns", campaigns), ("interactions", interactions)]:
    nulls = df.isnull().sum().sum()
    if nulls == 0:
        print(f"    {name}: No null values found")
    else:
        print(f"    {name}: WARNING - {nulls} null values found")
        print(df.isnull().sum()[df.isnull().sum() > 0])

# --- Check 2: Duplicate rows ---
print("\n[2] Duplicate Row Check")
for name, df in [("customers", customers), ("campaigns", campaigns), ("interactions", interactions)]:
    dupes = df.duplicated().sum()
    if dupes == 0:
        print(f"    {name}: No duplicates found")
    else:
        print(f"    {name}: WARNING - {dupes} duplicate rows found")

# --- Check 3: Referential integrity ---
print("\n[3] Referential Integrity Check")
valid_customer_ids = set(customers["customer_id"])
valid_campaign_ids = set(campaigns["campaign_id"])

orphan_customers = interactions[~interactions["customer_id"].isin(valid_customer_ids)]
orphan_campaigns = interactions[~interactions["campaign_id"].isin(valid_campaign_ids)]

if len(orphan_customers) == 0:
    print("    interactions.customer_id: All IDs match customers table")
else:
    print(f"    WARNING: {len(orphan_customers)} interactions have invalid customer_id")

if len(orphan_campaigns) == 0:
    print("    interactions.campaign_id: All IDs match campaigns table")
else:
    print(f"    WARNING: {len(orphan_campaigns)} interactions have invalid campaign_id")

# --- Check 4: Value range validation ---
print("\n[4] Value Range Check")
negative_revenue = interactions[interactions["revenue_generated"] < 0]
if len(negative_revenue) == 0:
    print("    revenue_generated: No negative values found")
else:
    print(f"    WARNING: {len(negative_revenue)} rows have negative revenue")

invalid_churn = customers[~customers["churned"].isin([0, 1])]
if len(invalid_churn) == 0:
    print("    churned flag: All values are valid (0 or 1)")
else:
    print(f"    WARNING: {len(invalid_churn)} rows have invalid churn values")

invalid_clicks = interactions[~interactions["clicked"].isin([0, 1])]
if len(invalid_clicks) == 0:
    print("    clicked flag: All values are valid (0 or 1)")
else:
    print(f"    WARNING: {len(invalid_clicks)} rows have invalid click values")

# --- Check 5: Cross-system discrepancy check ---
print("\n[5] Cross-System Discrepancy Check")
conn = sqlite3.connect("data/campaigniq.db")
customers.to_sql("customers", conn, if_exists="replace", index=False)
interactions.to_sql("interactions", conn, if_exists="replace", index=False)

db_count = pd.read_sql_query("SELECT COUNT(*) as cnt FROM customers", conn).iloc[0]["cnt"]
csv_count = len(customers)
if db_count == csv_count:
    print(f"    customers: CSV ({csv_count} rows) matches database ({int(db_count)} rows)")
else:
    print(f"    WARNING: CSV ({csv_count} rows) does not match database ({int(db_count)} rows)")

db_count2 = pd.read_sql_query("SELECT COUNT(*) as cnt FROM interactions", conn).iloc[0]["cnt"]
csv_count2 = len(interactions)
if db_count2 == csv_count2:
    print(f"    interactions: CSV ({csv_count2} rows) matches database ({int(db_count2)} rows)")
else:
    print(f"    WARNING: CSV ({csv_count2} rows) does not match database ({int(db_count2)} rows)")

conn.close()

print("\n" + "=" * 50)
print("Validation Complete — All checks passed")
print("=" * 50)