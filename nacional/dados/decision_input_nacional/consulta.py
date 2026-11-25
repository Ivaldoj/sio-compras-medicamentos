"""Consultas ao pacote decision_input_nacional (DuckDB, leitura sob demanda). Só abre arquivos deste diretório.

Em Python:   import sys; sys.path.insert(0, "<raiz_do_pacote>"); import consulta as q; con = q.conectar()
             con.sql("SELECT * FROM cesta").df()
Na linha de comando:  python -I -X utf8 consulta.py "<SQL>"
Tabelas: cesta, demanda_uf, demanda_mes, recursos_federais, restricoes, precos_comprasgov, precos_bps, cmed_teto. Esquemas: DESCRIBE <tabela>.
"""
import glob, os, sys
import duckdb

RAIZ = os.path.dirname(os.path.abspath(__file__))


def conectar():
    con = duckdb.connect()
    for p in glob.glob(os.path.join(RAIZ, "*", "*.parquet")) + glob.glob(os.path.join(RAIZ, "*", "*.csv")):
        real = os.path.realpath(p)
        assert real.startswith(os.path.realpath(RAIZ) + os.sep)
        nome = os.path.splitext(os.path.basename(p))[0]
        leitor = "read_parquet" if p.endswith(".parquet") else "read_csv_auto"
        con.execute(f"CREATE VIEW {nome} AS SELECT * FROM {leitor}('{real.replace(os.sep, '/')}')")
    return con


if __name__ == "__main__":
    import pandas as pd
    pd.set_option("display.width", 250)
    print(conectar().sql(sys.argv[1]).df().to_string() if len(sys.argv) > 1 else __doc__)
