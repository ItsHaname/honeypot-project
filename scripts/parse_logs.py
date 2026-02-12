#!/usr/bin/env python3
import json
import psycopg2
from pathlib import Path

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="honeypot",
    user="honeyadmin",
    password="HoneySecure2026!"
)
cursor = conn.cursor()

# Parser les logs Cowrie
cowrie_logs = Path("../logs/cowrie/cowrie.json")

if cowrie_logs.exists():
    print(f"📁 Fichier de logs trouvé : {cowrie_logs}")
    print(f"📊 Taille du fichier : {cowrie_logs.stat().st_size} octets")
    
    with open(cowrie_logs) as f:
        count = 0
        for line in f:
            try:
                event = json.loads(line)
                # Capturer les tentatives de connexion (succès ET échecs)
                if event.get('eventid') in ['cowrie.login.failed', 'cowrie.login.success']:
                    cursor.execute(
                        """INSERT INTO events 
                        (src_ip, event_type, username, password, honeypot_type) 
                        VALUES (%s, %s, %s, %s, %s)""",
                        (event['src_ip'], 
                         event.get('eventid'), 
                         event.get('username', ''), 
                         event.get('password', ''), 
                         'cowrie')
                    )
                    count += 1
                    if count % 10 == 0:  # Affiche tous les 10 événements
                        print(f"  → {count} événements insérés...")
            except Exception as e:
                # Ignorer les lignes mal formatées
                pass
    
    conn.commit()
    print(f"\n✅ TOTAL : {count} événements insérés dans PostgreSQL")
    
    # Vérifier le nombre total dans la base
    cursor.execute("SELECT COUNT(*) FROM events")
    total = cursor.fetchone()[0]
    print(f"📊 Total dans la base : {total} événements")
    
else:
    print("❌ Fichier de logs non trouvé !")
    print(f"🔍 Checherché : {cowrie_logs.absolute()}")

cursor.close()
conn.close()
