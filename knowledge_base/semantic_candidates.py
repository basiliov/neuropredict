"""Conservative proposals from literal sentence context, never verified evidence."""
import re
from evidence_db import QUERIES
from dataclasses import dataclass
PERCENT=re.compile(r"(?<![\w.])(\d{1,3}(?:[.,]\d{1,3})?)\s*(%|percent\b)",re.I)
POP=re.compile(r"\b(?:patients|people|participants) with multiple sclerosis\b|\bmultiple sclerosis patients\b",re.I)
ENDPOINTS={"prevalencia":re.compile(r"\bprevalence\b",re.I),"incidencia":re.compile(r"\bincidence\b",re.I),"riesgo":re.compile(r"\brisk\b",re.I)}
TERMS={"uveitis_intermedia":re.compile(r"\bintermediate uveitis\b",re.I),"periflebitis_retiniana":re.compile(r"\bretinal periphlebitis\b",re.I),"bandas_oligoclonales":re.compile(r"\boligoclonal bands?\b",re.I),"lesiones_infratentoriales":re.compile(r"\binfratentorial lesions?\b",re.I),"oct_gcipl":re.compile(r"\b(?:GCIPL|RNFL)\b",re.I)}
def propose(abstract):
    result=[]
    for sentence in re.split(r"(?<=[.!?])\s+(?=[A-Z(])",abstract):
        for m in PERCENT.finditer(sentence):
            val=float(m.group(1).replace(",","."))
            if not 0<=val<=100:continue
            result.append({"literal":m.group(0),"source_sentence":sentence,"variable_candidates":[k for k,p in TERMS.items() if p.search(sentence)],"population_candidate":"patients with MS" if POP.search(sentence) else None,"outcome_candidates":[k for k,p in ENDPOINTS.items() if p.search(sentence)],"status":"candidate_unverified","requires_manual_review":True})
    return result
