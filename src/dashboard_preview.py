import sqlite3
import pandas as pd

DB_FILE = "data/warehouse/medical_warehouse.db"

def run_analytics():
    conn = sqlite3.connect(DB_FILE)
    
    print("\n📊 --- WAREHOUSE KPI ANALYTICS OVERVIEW --- 📊")
    
    # Query 1: Total Messages and Performance by Channel
    print("\n1. Channel Performance (Total Volume & Engagement):")
    query_1 = """
        SELECT 
            channel, 
            COUNT(*) as total_messages, 
            SUM(views) as total_views, 
            SUM(forwards) as total_forwards
        FROM telegram_messages
        GROUP BY channel
        ORDER BY total_messages DESC;
    """
    df_channel = pd.read_sql_query(query_1, conn)
    print(df_channel.to_string(index=False))
    
    # Query 2: Top 3 Most Viewed Posts
    print("\n2. Top 3 Highest Performing Messages:")
    query_2 = """
        SELECT channel, date, views, SUBSTR(cleaned_text, 1, 60) as text_snippet
        FROM telegram_messages
        ORDER BY views DESC
        LIMIT 3;
    """
    df_top = pd.read_sql_query(query_2, conn)
    print(df_top.to_string(index=False))
    
    conn.close()

if __name__ == "__main__":
    run_analytics()