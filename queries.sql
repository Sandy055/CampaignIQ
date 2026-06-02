-- =============================================
-- CampaignIQ: Marketing Analytics SQL Queries
-- =============================================

-- 1. Total revenue generated per campaign
SELECT 
    c.campaign_name,
    c.channel,
    COUNT(i.interaction_id) AS total_interactions,
    SUM(i.converted) AS total_conversions,
    ROUND(SUM(i.revenue_generated), 2) AS total_revenue,
    ROUND(AVG(i.revenue_generated), 2) AS avg_revenue_per_interaction
FROM interactions i
JOIN campaigns c ON i.campaign_id = c.campaign_id
GROUP BY c.campaign_name, c.channel
ORDER BY total_revenue DESC;

-- 2. Conversion rate by campaign
SELECT 
    c.campaign_name,
    c.channel,
    COUNT(i.interaction_id) AS total_interactions,
    SUM(i.converted) AS conversions,
    ROUND(100.0 * SUM(i.converted) / COUNT(i.interaction_id), 2) AS conversion_rate_pct
FROM interactions i
JOIN campaigns c ON i.campaign_id = c.campaign_id
GROUP BY c.campaign_name, c.channel
ORDER BY conversion_rate_pct DESC;

-- 3. Customer churn rate by segment
SELECT 
    segment,
    COUNT(customer_id) AS total_customers,
    SUM(churned) AS churned_customers,
    ROUND(100.0 * SUM(churned) / COUNT(customer_id), 2) AS churn_rate_pct,
    ROUND(AVG(lifetime_value), 2) AS avg_lifetime_value
FROM customers
GROUP BY segment
ORDER BY churn_rate_pct DESC;

-- 4. Revenue by customer region
SELECT 
    cu.region,
    COUNT(DISTINCT i.customer_id) AS active_customers,
    SUM(i.converted) AS total_conversions,
    ROUND(SUM(i.revenue_generated), 2) AS total_revenue
FROM interactions i
JOIN customers cu ON i.customer_id = cu.customer_id
GROUP BY cu.region
ORDER BY total_revenue DESC;

-- 5. Monthly revenue trend
SELECT 
    strftime('%Y-%m', interaction_date) AS month,
    COUNT(interaction_id) AS total_interactions,
    SUM(converted) AS total_conversions,
    ROUND(SUM(revenue_generated), 2) AS monthly_revenue
FROM interactions
GROUP BY month
ORDER BY month ASC;

-- 6. Top 10 highest value customers
SELECT 
    cu.customer_id,
    cu.customer_name,
    cu.segment,
    cu.region,
    cu.lifetime_value,
    cu.churned
FROM customers cu
ORDER BY lifetime_value DESC
LIMIT 10;