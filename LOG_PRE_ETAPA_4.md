# LOG — Pré-Etapa 4 (tratamento das limitações da Etapa 3)

23/11/2026. Data de corte mantida: 29/01/2025. Arquivos das Etapas 1–3 preservados. Os documentos 12–17 e o `LOG_ETAPA_3.md` não foram reescritos: o estado atual está no doc 18. Os scripts foram alterados de forma retrocompatível, e uma cópia dos produtos da Etapa 3 usados na comparação ficou no rascunho da sessão. Resultado consolidado em `docs/18_pre_etapa4_tratamento_lacunas.md`.

## 1. Diagnóstico inicial (por impacto no valor)
- Itens sem preço praticado: 100 (44,7% do valor). As insulinas em caneta somam 27%: item 196 (23,4%) e item 199 (3,6%).
- O item 199 não tinha nenhum candidato CMED: o token "regular" do nome impedia achar "INSULINA HUMANA".
- As 52 contratações PNCP ainda não baixadas cobriam menos de 1% do valor sem preço, porque a seleção era por CATMAT e os itens sem preço quase não têm CATMAT. Daí a seleção 2, por descrição.

## 2. ICMS da PB
- Cabeçalho da CMED de 06/01/2025 (já no projeto): manda usar a alíquota da UF de destino e aplicar desoneração aos produtos dos convênios do CONFAZ (Conv. 87/02).
- CONFAZ, Conv. ICMS 87/02 consolidado (`data/raw/complementares/icms_pb/`): isenção para a administração pública municipal; prorrogado até 30/04/2026 (Conv. 226/23); a PB é citada no §5º.
- SEFAZ-PB: Lei 6.379/96 consolidada em 02/10/2023, art. 11, I, com 20% desde 01/01/2024 (Lei 12.788/23); não há alíquota específica para medicamentos.
- Falhas de download:
  - RICMS-PB consolidado (versão de 15/04/2024): 4 tentativas encerradas pelo servidor (curl 56; um arquivo truncado de 91 KB foi descartado);
  - página da Lei 12.788 no site da SEFAZ-PB: HTML truncado, sem o texto.
- Regra implementada em `27_montar_pacotes.py` (`aliquota_icms_pb`, `base_aliquota_pb`, `aliquota_aplicavel_pb`); `consulta_agente.teto_cmed()` filtra a alíquota da PB por padrão.

## 3. Fontes novas e downloads
- **Compras.gov.br, dados abertos** (`scripts/29_comprasgov_precos.py`; cache em `data/raw/comprasgov/`, 348 MB):
  - PDMs da classe 6505: 1.901, em 4 páginas;
  - itens CATMAT de 523 PDMs;
  - pesquisa de preço para 653 CATMATs.
  - Sobre a API: `1_consultarMaterial` exige `tipo=codigoItemCatalogo`, e o filtro `dataCompraFim` não filtrou, então o recorte temporal é feito no script.
  - Para acelerar, rodaram três coletores em paralelo (ordem direta, inversa e a partir do meio) com gravação atômica no cache. O coletor direto terminou 649/649; o código de saída 1 foi de um `tail -2` encadeado, não da coleta.
  - Uma execução final pelo cache confirmou 653/653 sem erro.
- **PNCP:**
  - Seleção 2, por descrição: 29 contratações, com resultados só dos itens-alvo.
  - Retomada das 52 por CATMAT, com dois coletores (ordem direta e inversa).
  - Total: 95 de 95 contratações baixadas, 0 ilegíveis.
- **BNAFAR:** `16_bnafar_estoque.py 251340 202501` e `202412` voltaram 0 linhas, ou seja, sem posição histórica (registrado em `reports/manifest_fontes.csv`).
- **TCE-PB/SAGRES:** receitas de 2024 de Santa Luzia (`170_santa_luzia_receitas-2024.zip`), registradas no manifesto de fontes.

## 4. Defeitos de regra corrigidos (`scripts/padroniza.py`, 47 autotestes)
1. Contagem de recipientes com qualificador ("CT EST 50 AMP", "CX C/ 25 AMP", "CX C/5 AMP") e de blisters ("CT DISP 10 BL").
2. "CX 50 BL … X 350" (mais de 100 por blister) passa a ser ambíguo, não convertido.
3. "LIB MOD", "liberação modificada" e "liberação controlada" passam a ser modificador de liberação.
4. Nome do item do catálogo = 1º segmento da descrição (PDM "VITAMINA D" → COLECALCIFEROL).
5. Sal "hemifumarato".
6. "PRINCÍPIO ATIVO: ASSOCIADA COM".
7. Denominador comum em "50 mg + 12,5 mg/ml".
8. Busca na CMED ignora o tipo "regular" da insulina (a forma solução × suspensão decide); correção em `25_padronizacao_vinculos.py`.
9. Registros de teste da lista CMED ("EMPRESA DE TESTE") excluídos (`25_padronizacao_vinculos.py`).

Também:
- `mesmo_medicamento` e `nivel_catmat` foram movidos para `padroniza.py` e são usados pelos scripts 25, 26, 27 e 29;
- os downloads (26 e 29) passaram a gravar de forma atômica e a tolerar arquivos parciais no cache.

## 5. Verificação das conversões
- Checagem automática em todos os vínculos aceitos (colunas `verif_*`, `ressalva_recipiente` e `status` em `regras_conversao.csv`).
- Inspeção pelo assistente de 330 apresentações, uma por fator distinto nos 61 itens que somam 80% do valor (`reports/pre4_inspecao_conversoes_amostra.csv`): 4 erros, todos de padrão de texto e corrigidos na regra, e 3 ressalvas de recipiente.
- A validação humana continua pendente e o status diz isso explicitamente.

## 6. Integridade temporal: correções após a varredura de todas as colunas
- Removido do pacote `pncp_comparaveis_itens.situacao`: era a situação atual, com 1.874 itens "Homologado" sem resultado até o corte. **Vinha da Etapa 3.**
- `pncp_comparaveis_resultados.cancelado` passou a considerar só cancelamentos até o corte; os 63 marcados eram posteriores. **Vinha da Etapa 3.**
- Removidos `comprasgov…data_atualizacao_item` (45.871 registros atualizados após o corte) e o status e a data de atualização do catálogo.
- As cópias de auditoria estão em `data/processed/pre4/`.
- Teste de separação: a chave dos resultados PNCP passou a incluir `data_inclusao`. Um item tinha um resultado em 31/10/2024 (pacote) e um novo resultado em 12/05/2025 (avaliação), registros distintos.

## 7. Execução final
```
python -I -X utf8 scripts/padroniza.py                       # autotestes ok
python -I -X utf8 scripts/29_comprasgov_precos.py . catalogo # 274 de 334 itens com CATMAT no catálogo oficial
python -I -X utf8 scripts/29_comprasgov_precos.py . precos   # 653/653 pelo cache, 0 erros
python -I -X utf8 scripts/25_padronizacao_vinculos.py .
python -I -X utf8 scripts/26_pncp_comparaveis.py . consolidar
python -I -X utf8 scripts/29_comprasgov_precos.py . consolidar
python -I -X utf8 scripts/27_montar_pacotes.py .
python -I -X utf8 scripts/28_verificacoes.py .               # 108 PASSOU, 0 FALHOU
```
As saídas estão em `reports/pre4_*_stdout.txt`.

## 8. Números finais
- **CATMAT:** 227 com 1 código, 27 com vários, 14 parciais e 66 ausentes (36,0% do valor).
- **CMED:**
  - pares: 263 exatos, 4.613 compatíveis, 55 prováveis, 230 indeterminados e 15.265 incompatíveis;
  - teto disponível para 226 itens (77,8% do valor);
  - 210 vínculos aceitos com alerta.
- **Preço praticado:** disponível para 253 itens (62,6%), a conferir 25 (29,7%) e ausente 56 (7,7%).
- **Compras.gov.br:** 141.599 registros disponíveis, 87.287 posteriores e 3.128 indeterminados.
- **PNCP:** 84 contratações, 4.988 itens e 269 resultados disponíveis.
- **Estimativa × teto CMED:** 40 itens (38,9% do valor) com estimativa acima do teto; excedente de R$ 1.390.210,40.

## 9. Pendências
Ver doc 18, §12: validação humana das conversões; condições do Convênio 87/02 por produto e RICMS-PB; preço praticado de canetas de insulina; consumo, estoque e saldo de dotação (via LAI); 81 itens sem preço praticado compatível disponível (25 a conferir e 56 ausentes).

A Etapa 4 não foi iniciada.
