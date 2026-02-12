#!/usr/bin/env python3
import psycopg2
from datetime import datetime, timedelta

print("🚫 BLACKLIST AUTOMATIQUE - IPs MALVEILLANTES")
print("="*50)

conn = psycopg2.connect(
    host="localhost",
    database="honeypot",
    user="honeyadmin",
    password="HoneySecure2026!"
)
cursor = conn.cursor()

# Détecter les IPs à haut risque
cursor.execute("""
    INSERT INTO blacklist (ip, reason)
    SELECT DISTINCT src_ip, 'HIGH_RISK: ' || COUNT(*) || ' tentatives, ' || 
                      COUNT(DISTINCT password) || ' mots de passe'
    FROM events
    WHERE timestamp > NOW() - INTERVAL '24 hours'
    GROUP BY src_ip
    HAVING COUNT(*) > 50 
       OR COUNT(DISTINCT password) > 20
       OR SUM(CASE WHEN event_type = 'cowrie.login.success' THEN 1 ELSE 0 END) > 5
    ON CONFLICT (ip) DO NOTHING
""")

blacklisted = cursor.rowcount
conn.commit()

print(f"🚫 {blacklisted} nouvelles IPs blacklistées !")

# Afficher la blacklist
print("\n📋 BLACKLIST ACTUELLE :")
cursor.execute("""
    SELECT ip, reason, added_at 
    FROM blacklist 
    ORDER BY added_at DESC 
    LIMIT 10
""")
for ip, reason, added in cursor.fetchall():
    print(f"  {ip}: {reason[:50]}... ({added})")

cursor.close()
conn.close()
