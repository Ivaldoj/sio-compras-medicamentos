"""Lista esquemas e contagens de todas as tabelas/visões do pacote (via scripts/consulta_agente.py)."""
import sys; sys.path.insert(0, "scripts"); import consulta_agente as q
con = q.conectar()
for t in list(q.TABELAS) + list(q.VISOES):
    try:
        n = con.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
        print(f"\n=== {t} ({n} linhas)")
        for r in con.execute(f"DESCRIBE {t}").fetchall():
            print(f"  {r[0]}: {r[1]}")
    except Exception as e:
        print(f"\n=== {t}: ERRO {e}")
