# LOG — experimento nacional (branch `reformulacao-nacional`)

## 25/11/2026 — preparação
- **Etapa 1-B** (diagnóstico, D-14): só o CEAF tem demanda nacional anterior ao corte. Por instrução dos coordenadores de executar sem paradas, a cesta passou a ser do CEAF (D-15).
- **Demanda.** TabNet SIA/SUS, grupo 06: procedimentos × UF, × mês e por total. Janelas:
  - processamento de nov/2023 a out/2024 (pacote);
  - nov/2022 a out/2023 (ano anterior, no pacote);
  - fev/2025 a jan/2026 (avaliação).
- **`n01_sia_cmed_candidatos.py`.** Vínculo SIA × CMED por regra:
  - princípio ativo, com associações e com um termo de sal a mais;
  - concentração, também por massa = concentração × volume, nos dois sentidos;
  - forma, aceitando "injetável" genérico.

  Resultado: 261 dos 303 procedimentos vinculados (os sem vínculo somam 3,6% da quantidade).
  - Defeitos achados e corrigidos durante o trabalho: teto por embalagem em vez de por unidade (bosentana, supositórios, adesivos) e biológicos sem vínculo por notação de concentração.
- **`n02_apresentacoes_catmat.py`.**
  - Procedimentos equivalentes (biossimilar e originador) agregados em apresentações.
  - Grupo de financiamento por correspondência textual com a RENAME 2024, Anexo III. Um defeito da janela de busca, que invadia a substância seguinte, foi corrigido. A coerência com o SIA (Grupo 1B ↔ valor aprovado > 0) é de 100%.
  - CATMAT pelo catálogo oficial, com equivalências de grafia registradas (eltrombopag/eltrombopague, mofetil/mofetila) e o erro de digitação "5O ML" corrigido.
  - Pesquisa de preço baixada para 159 CATMATs.
- **`n03_pacote_nacional.py`.**
  - Cesta = 50 apresentações de maior relevância econômica nacional (dispensação de 12 meses antes do corte × preço praticado mediano antes do corte), entre as 90 primeiras por teto. Critério de qualidade: teto CMED, pelo menos 5 preços compatíveis antes do corte, grupo identificado.
  - Resultado: 38 no Grupo 1A, 6 no 1B e 6 no 2; valor nacional estimado de R$ 11,1 bi por ano. Isso é compatível com a ação 4705 em 2024 (R$ 13,7 bi empenhados).
  - 20 candidatos foram excluídos por menos de 5 preços compatíveis ou falta de CATMAT vinculável (natalizumabe, rituximabe, certolizumabe e outros).
  - 112 verificações aprovadas: datas ≤ corte, nenhuma coluna de situação ou atualização, disjunção pacote × avaliação.
  - Um falso positivo da varredura foi resolvido renomeando a coluna "orçamento atualizado" (dotação do exercício) para `dotacao_final_exercicio`.

## Registro antes da decisão (25/11/2026 20:06)
```
d261bd6caf1bded6c0a00cdb672c927761987d88d31ca6a738cfe04bf105ec94  nacional/avaliacao/PROTOCOLO_AVALIACAO_NACIONAL.md
845323b48f2c595f77796bc7813897ecf20692a925fa88d7bd74a8630dff81d7  nacional/decisao/ENUNCIADO.md
519bd83d4906e8510e65bcb4a39e836d907504d9c7ca0fe4b090638828f6e42c  nacional/dados/decision_input_nacional/MANIFESTO.csv
```

## Execução (25/11/2026)
- **Decisor (Claude Opus 5.5, isolado):**
  - 45 chamadas de ferramenta, nenhuma violação (4 falsos positivos `dlog_*`);
  - prompt idêntico ao enunciado e entradas inalteradas;
  - recomendou E2, a compra nacional compartilhada.
  - Registros em `nacional/decisao/registro/`.
- **Avaliador com Fable 5.2:** falhou antes da primeira ação (API: "requires usage credits"); a auditoria registra 0 chamadas.
- **Avaliador com Claude Opus 5.5 (D-17):**
  - 81 chamadas, nenhuma violação (4 falsos positivos);
  - 3 acessos web, todos a planalto.gov.br;
  - decisão congelada intacta;
  - veredito: parcialmente adequado.
  - Registros em `nacional/avaliacao/registro/`.
- **Falhas do pacote apontadas pelo avaliador, reconferidas e confirmadas pela coordenação:**
  - `n03`: a lista de unidades sólidas aceita SUPOSITÓRIO (mesalazina 500 mg, AP052);
  - `n02`: o parser do grupo caiu na entrada de 0,5 g (imunoglobulina 5 g é 1A, p. 209).

  Não foram corrigidas nos arquivos congelados.
- **Entregas finais:** `nacional/RELATORIO_FINAL.md` e `nacional/SLIDES_26.md` (estrutura reconstruída, D-16).
