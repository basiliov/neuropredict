# NeuroPredict Knowledge Base (rama de integración v0.2)
Prototipo independiente en Python 3.10+ con biblioteca estándar, base SQLite y visor local. No contiene datos de pacientes. Los artículos de PubMed se guardan como **metadatos**, no como cifras verificadas.

## Windows
```powershell
py evidence_db.py init
py evidence_db.py sync --variable uveitis_intermedia --limit 20
py evidence_web.py
```
Abrir http://127.0.0.1:8765. Los artículos indexados se muestran por variable; únicamente los registros cuantitativos con `verified=1` podrían aparecer en el apartado de resultados. En esta versión no se extraen ni verifican automáticamente porcentajes.

La descarga v0.2 entregada en el chat incluye más funciones de curaduría y pruebas. Esta rama contiene el núcleo integrable y se propone para revisión, sin modificar la rama principal.
