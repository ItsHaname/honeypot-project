# Statistiques finales
print("\n📊 DISTRIBUTION FINALE RÉALISTE:")
print("-"*70)
print(f"{'Pays':4} | {'IPs':6} | {'Événements':10} | {'Moy/IP':7} | {'Min':5} | {'Max':6}")
print("-"*70)

cur.execute("""
    SELECT country, 
           COUNT(DISTINCT src_ip) as ips,
           COUNT(*) as events,
           ROUND(COUNT(*)::numeric / COUNT(DISTINCT src_ip), 1) as avg_per_ip,
           MIN(events_per_ip) as min_attacks,
           MAX(events_per_ip) as max_attacks
    FROM (
        SELECT country, src_ip, COUNT(*) as events_per_ip
        FROM events
        WHERE src_ip NOT LIKE '192.168.%'
        GROUP BY country, src_ip
    ) subq
    GROUP BY country
    ORDER BY events DESC
""")

for row in cur.fetchall():
    print(f"{row[0]:4} | {row[1]:6} | {row[2]:10} | {row[3]:6.1f} | {row[4]:5} | {row[5]:6}")

# Distribution des volumes (version corrigée sans la colonne 'volume')
print("\n📈 DISTRIBUTION DES VOLUMES D'ATTAQUES:")
print("-"*50)

cur.execute("""
    SELECT 
        CASE 
            WHEN attacks >= 1000 THEN '1000+   '
            WHEN attacks >= 500 THEN '500-999 '
            WHEN attacks >= 100 THEN '100-499 '
            WHEN attacks >= 50 THEN '50-99   '
            WHEN attacks >= 20 THEN '20-49   '
            WHEN attacks >= 10 THEN '10-19   '
            WHEN attacks >= 5 THEN '5-9     '
            ELSE '1-4     '
        END as volume_cat,
        COUNT(*) as nb_ips,
        SUM(attacks) as total_attacks
    FROM (
        SELECT src_ip, COUNT(*) as attacks
        FROM events
        WHERE src_ip NOT LIKE '192.168.%'
        GROUP BY src_ip
    ) stats
    GROUP BY volume_cat
    ORDER BY 
        CASE volume_cat
            WHEN '1000+   ' THEN 1
            WHEN '500-999 ' THEN 2
            WHEN '100-499 ' THEN 3
            WHEN '50-99   ' THEN 4
            WHEN '20-49   ' THEN 5
            WHEN '10-19   ' THEN 6
            WHEN '5-9     ' THEN 7
            ELSE 8
        END
""")

for row in cur.fetchall():
    print(f"{row[0]}: {row[1]:4} IPs, {row[2]:6} attaques")

cur.close()
conn.close()
