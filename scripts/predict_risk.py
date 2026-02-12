#!/usr/bin/env python3
import psycopg2
import joblib
import pandas as pd

print("🧠 PRÉDICTION DU RISQUE PAR IP")
print("="*50)

# Charger le modèle ML
try:
    clf = joblib.load('../models/classifier.pkl')
    print("✅ Modèle chargé")
except:
    print("❌ Modèle non trouvé - Exécute d'abord train_model.py")
    exit()

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="honeypot",
    user="honeyadmin",
    password="HoneySecure2026!"
)
cursor = conn.cursor()

# Analyser les IPs
df = pd.read_sql("""
    SELECT 
        src_ip,
        COUNT(*) as attempt_count,
        COUNT(DISTINCT password) as password_diversity,
        COUNT(DISTINCT EXTRACT(HOUR FROM timestamp)) as hours_active,
        SUM(CASE WHEN event_type = 'cowrie.login.success' THEN 1 ELSE 0 END) as success_count,
        SUM(CASE WHEN event_type = 'cowrie.login.failed' THEN 1 ELSE 0 END) as fail_count
    FROM events
    WHERE risk_level IS NULL OR risk_level = ''
    GROUP BY src_ip
""", conn)

print(f"📊 {len(df)} IPs à analyser...")

if len(df) > 0:
    # Créer les features
    df['success_rate'] = df['success_count'] / (df['attempt_count'] + 1)
    df['fail_rate'] = df['fail_count'] / (df['attempt_count'] + 1)
    df['is_brute_force'] = (df['attempt_count'] > 10).astype(int)
    df['is_password_spray'] = (df['password_diversity'] < 3).astype(int)
    
    features = ['attempt_count', 'password_diversity', 'hours_active', 
                'success_rate', 'fail_rate', 'is_brute_force', 'is_password_spray']
    X = df[features]
    
    # Prédire
    predictions = clf.predict(X)
    probabilities = clf.predict_proba(X)
    
    # Mettre à jour la base
    for idx, row in df.iterrows():
        risk = "HIGH" if predictions[idx] == 1 else "LOW"
        confidence = max(probabilities[idx]) * 100
        
        cursor.execute(
            "UPDATE events SET risk_level = %s WHERE src_ip = %s AND (risk_level IS NULL OR risk_level = '')",
            (risk, row['src_ip'])
        )
        print(f"  {row['src_ip']}: {risk} RISK (confiance: {confidence:.1f}%)")

conn.commit()
print(f"\n✅ Niveaux de risque mis à jour !")

# Stats
cursor.execute("SELECT risk_level, COUNT(*) FROM events GROUP BY risk_level")
print("\n📊 RÉPARTITION DES RISQUES :")
for risk, count in cursor.fetchall():
    print(f"  {risk}: {count} événements")

cursor.close()
conn.close()
