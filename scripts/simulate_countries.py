#!/usr/bin/env python3
"""
🌍 SIMULATION DE GÉOLOCALISATION POUR DÉMO
À utiliser SEULEMENT pour la démonstration LinkedIn/prof
"""

import psycopg2
import random
from collections import Counter

print("🌍 SIMULATION DE GÉOLOCALISATION")
print("="*50)

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="honeypot",
    user="honeyadmin",
    password="HoneySecure2026!"
)
cursor = conn.cursor()

# Liste des pays avec leurs poids (réaliste)
COUNTRIES = [
    ('CN', 35),  # Chine 35%
    ('RU', 25),  # Russie 25%
    ('US', 20),  # USA 20%
    ('BR', 8),   # Brésil 8%
    ('IN', 5),   # Inde 5%
    ('VN', 3),   # Vietnam 3%
    ('ID', 2),   # Indonésie 2%
    ('TR', 1),   # Turquie 1%
    ('IR', 0.5), # Iran 0.5%
    ('KR', 0.5), # Corée 0.5%
]

# Récupérer toutes les IPs uniques sans pays
cursor.execute("""
    SELECT DISTINCT src_ip 
    FROM events 
    WHERE country IS NULL OR country = '' OR country = 'UNK'
""")
ips = cursor.fetchall()
print(f"📍 {len(ips)} IPs à géolocaliser...")

# Distribuer les pays selon les poids
country_pool = []
for country, weight in COUNTRIES:
    country_pool.extend([country] * int(weight * 10))

count = 0
for (ip,) in ips:
    # Simuler le pays
    country = random.choice(country_pool)
    
    # Mettre à jour la base
    cursor.execute(
        "UPDATE events SET country = %s WHERE src_ip = %s AND (country IS NULL OR country = '' OR country = 'UNK')",
        (country, ip)
    )
    count += cursor.rowcount

conn.commit()
print(f"\n✅ {count} IPs géolocalisées (simulation)")

# Afficher les résultats
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
    flag = {
        'CN': '🇨🇳', 'RU': '🇷🇺', 'US': '🇺🇸', 
        'BR': '🇧🇷', 'IN': '🇮🇳', 'VN': '🇻🇳',
        'ID': '🇮🇩', 'TR': '🇹🇷', 'IR': '🇮🇷', 'KR': '🇰🇷'
    }.get(country, '🌍')
    print(f"  {flag} {country}: {attacks} attaques")

# Stats
cursor.execute("SELECT COUNT(DISTINCT country) FROM events WHERE country IS NOT NULL")
nb_pays = cursor.fetchone()[0]
print(f"\n🌍 Total pays différents: {nb_pays}")

cursor.close()
conn.close()
