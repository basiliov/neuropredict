"""Two-person evidence verification, independent of clinical diagnosis."""
import sqlite3
from datetime import datetime,timezone
def init(db):
    existing={r[1] for r in db.execute("PRAGMA table_info(findings)")}
    for col in ("reviewer","reviewed_at","source_location"):
        if col not in existing: db.execute("ALTER TABLE findings ADD COLUMN "+col+" TEXT")
    db.execute("CREATE TABLE IF NOT EXISTS evidence_audit(id INTEGER PRIMARY KEY,finding_id INTEGER,event TEXT,actor TEXT,at TEXT,note TEXT)")
    db.commit()
def review(db, finding_id, reviewer, note, approve=True):
    row=db.execute("SELECT curator FROM findings WHERE id=?",(finding_id,)).fetchone()
    if not row: raise ValueError("Resultado inexistente")
    if not reviewer.strip() or not note.strip() or reviewer.casefold()==row[0].casefold(): raise ValueError("Revisor independiente y nota requeridos")
    stamp=datetime.now(timezone.utc).isoformat()
    with db:
        db.execute("UPDATE findings SET verified=?,reviewer=?,reviewed_at=? WHERE id=?",(int(approve),reviewer,stamp,finding_id))
        db.execute("INSERT INTO evidence_audit(finding_id,event,actor,at,note) VALUES(?,?,?,?,?)",(finding_id,"approved" if approve else "rejected",reviewer,stamp,note))
