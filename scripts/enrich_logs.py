#!/usr/bin/env python3
import psycopg2
import requests
import time

print("🌍 ENRICHISSEMENT DES LOGS - GÉOLOCALISATION")
print("="*50)

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="honeypot",
    user="honeyadmin",
    password="HoneySecure2026!"
)
cursor = conn.cursor()

# Récupérer les IPs sans pays
cursor.execute("""
    SELECT DISTINCT src_ip 
    FROM events 
    WHERE country IS NULL OR country = ''
""")
ips = cursor.fetchall()
print(f"📍 {len(ips)} IPs à géolocaliser...")

# Service de géolocalisation gratuit
count = 0
for (ip,) in ips:
    try:
        # Utiliser ip-api.com (gratuit, pas de clé)
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = response.json()
        
        if data['status'] == 'success':
            country_code = data['countryCode']
            
            # Mettre à jour la base
            cursor.execute(
                "UPDATE events SET country = %s WHERE src_ip = %s AND country IS NULL",
                (country_code, ip)
            )
            count += cursor.rowcount
            print(f"  ✅ {ip} → {country_code} ({data['country']})")
        else:
            # Si erreur, mettre 'UNKNOWN'
            cursor.execute(
                "UPDATE events SET country = 'UNK' WHERE src_ip = %s AND country IS NULL",
                (ip,)
            )
        
        time.sleep(0.1)  # Pour respecter les limites de l'API
        
    except Exception as e:
        print(f"  ❌ {ip}: {e}")

conn.commit()
print(f"\n✅ {count} IPs géolocalisées !")

# Afficher les statistiques par pays
print("\n📊 TOP 10 DES PAYS ATTAQUANTS :")
print("-"*50)
cursor.execute("""
    SELECT country, COUNT(*) as attacks 
    FROM events 
    WHERE country IS NOT NULL 
    GROUP BY country 
    ORDER BY attacks DESC 
    LIMIT 10
""")
for country, attacks in cursor.fetchall():
    print(f"  {country}: {attacks} attaques")

cursor.close()
conn.close()
