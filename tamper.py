# tamper.py - simulates an attacker editing the log database (for the demo)
import sqlite3

DB = "agent_logs.db"

with sqlite3.connect(DB, timeout=10.0) as c:
    row = c.execute("SELECT id FROM events WHERE risk='high' ORDER BY id LIMIT 1").fetchone()
    if row is None:
        print("No 'high' risk row found in agent_logs.db. Run an attack/alert scenario first.")
    else:
        c.execute("UPDATE events SET risk='low', alert='' WHERE id=?", (row[0],))
        c.commit()
        print(f"Row {row[0]} was modified: the alert was erased. Now click 'Verify log integrity' in the browser.")