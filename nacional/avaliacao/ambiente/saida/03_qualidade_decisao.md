# 03 — Qualidade da decisão ex ante (dimensão D): **parcialmente adequado** (confiança média)

Julgo só com a informação disponível em 29/01/2025. Os dados reservados não entram nesta seção, a não ser onde está indicado expressamente "ex post, só ilustrativo".

## 1. Requisitos do protocolo

| Requisito | Situação | Evidência |
|---|---|---|
| ≥3 cenários autônomos e substancialmente distintos | **Atendido.** Quatro estratégias avaliadas: E1 status quo, E2 SRP nacional compartilhado, E3 blocos regionais, E4 federalização. Mais sete descartadas com motivo (X1–X7). Mudam quem compra e quem paga, o volume agregado e a base normativa | `02_estrategias.md` [OBS] |
| Critério de eficiência explícito e coerente | **Atendido.** Menor custo esperado para a mesma cobertura, com filtro de viabilidade, risco de abastecimento não pior que o da linha de base e robustez. O custo é consolidado nas três esferas | `03_comparacao.md` §1; D06 [OBS] |
| Competências das esferas (1A, 1B, 2) | **Atendido.** 1A fica no MS. Em 1B e 2 a SES continua contratante e pagadora; o MS só gerencia a ata. E4, que muda a PRC 2/2017, foi corretamente barrada no filtro de viabilidade | `02_estrategias.md`; `restricoes.csv` [OBS] |
| Viabilidade jurídica, operacional, orçamentária e de mercado | **Atendido, com ressalva.** Matriz qualitativa por estratégia. A base jurídica de E2 está correta no mérito (ver §3) | `03_comparacao.md` §4 |
| Incertezas com faixas | **Atendido.** Monte Carlo com números aleatórios comuns, faixas de quantidade, preço, β e transição, e sensibilidade determinística | `03_estrategias.py`, `04_sensibilidade.py` [OBS] |
| Rastreabilidade | **Atendido.** Todo número tem script e todas as afirmações vêm classificadas. Exceção: "~751 mil frascos" | `02_calculos.csv` C20 |
| Distinção demanda × compra e homologado × pago | **Atendido.** Explícita e repetida: H01, D14; `05_economia.md` §5 define a medição da economia efetiva por pagamento | [OBS] |
| Escolha justificada | **Atendido.** `04_recomendacao.md`, com condições de reversão e verificações prévias | [OBS] |

## 2. Pontos fortes

1. **Detectou o erro de grupo de financiamento de AP007.**
   - O pacote marca a imunoglobulina 5 g como 1B. O decisor notou que o MS a compra de forma centralizada e que o SIA 1B financia R$ 0,03/unidade, e a tratou como centralizada (D07, H19) [OBS].
   - A RENAME 2024, Anexo III, **p. 209 do PDF**, confirma: a imunoglobulina humana 5 g é do **Grupo 1A** [OBS: `evidencias_primarias/rename/...pdf`, extraído por `trabalho/d01_rename.py`].
   - Os outros 11 itens não-1A conferem com o Anexo III:
     - 1B: leuprorrelina 3,75 mg (p. 174), eltrombopague (p. 199), mepolizumabe 100 mg/mL (p. 212), omalizumabe (p. 217);
     - 2: atorvastatina (p. 181), azatioprina (p. 182), calcitriol (p. 187), dapagliflozina (p. 197), mesalazina 500 mg LP e 800 mg (pp. 212–213) [OBS: `trabalho/d01_rename_trechos.txt`].
2. **Separação rigorosa das categorias de valor.** Teto CMED, valor SIA e orçamento não se somam ao preço homologado. O BPS fica só como conferência [OBS: `02_calculos.csv` C29].
3. **Contrafactual bem escolhido.** A referência é o preço estadual praticado, na mesma categoria e com a mesma quantidade. O teto CMED foi rejeitado como referência, o que evita inflar a economia [OBS: `05_economia.md` §1].
4. **Não usou o diferencial DLOG/estadual de 0,29 no valor central.** Ele mistura PDP e negociação. O decisor o deixou só como limite otimista [OBS].
5. **Separou o horizonte com transição do regime pleno**, sem somar os dois [OBS].

## 3. Viabilidade jurídica de E2: correta no mérito, com fundamento incompleto

- O decisor apoia E2 na Lei 14.133, arts. 82–86 (IRP com participantes) e no Decreto 11.462/2023.
- Conferi as normas (web, `registro_acessos.md`):
  - o caput do art. 86 da Lei 14.133 prevê a IRP para participação de "outros órgãos ou entidades";
  - o §8º veda que órgão federal adira a ata estadual;
  - o §7º dispensa a adesão emergencial a ata do MS do limite do §5º [OBS: planalto.gov.br, Lei 14.133];
  - o Decreto 11.462/2023 define no **art. 2º, VI, a "compra nacional"**: o gerenciador conduz o registro de preços para execução descentralizada de programa federal, com demanda indicada pelos entes federados beneficiados, e prevê a divulgação a estados e municípios no art. 7º, V [OBS: planalto.gov.br, Decreto 11.462].
- **Conclusão:** esse é o instrumento mais aderente a E2, e já existia antes do corte. O decisor não o citou, mas sua conclusão (juridicamente viável) se sustenta [INF].
- **Ressalva não tratada:** a "compra nacional" pressupõe **programa federal**. Nos itens do Grupo 2, financiados pelos estados, o enquadramento é discutível. Isso pede o parecer jurídico que o próprio decisor listou nas verificações [INF].

## 4. Fragilidades (com a informação de 29/01/2025)

### 4.1 O efeito volume foi aplicado a monopólios com preço uniforme entre SES (principal fragilidade)

- A economia de E2 vem de um β agregado por segmento (−0,08), estimado em 50 itens, aplicado a todos os 11 descentralizados.
- Os próprios dados do pacote mostram que, nos itens de fonte única do Grupo 1B, as SES já pagam um preço quase uniforme, independentemente do porte [CALC: `trabalho/d02_beta_por_item.py` → `trabalho/d02_beta_por_item.csv`, amostra e filtros do decisor]:

  | Item | CV do preço estadual (24m) | Compras estaduais a ±2% da mediana | β do próprio item |
  |---|---|---|---|
  | AP029 eltrombopague 50 mg | 0,044 | 55% | −0,002 |
  | AP060 eltrombopague 25 mg | 0,058 | 48% | −0,011 |
  | AP034 omalizumabe | 0,081 | 56% | −0,005 |

  Em AP027 (mepolizumabe), o valor de R$ 2.028,87 se repete em SES de vários portes (SP, PR, CE, RN, AL, DF). Isso sugere um preço negociado nacionalmente ou uma política comercial do fabricante, não um efeito volume [OBS: `precos_comprasgov`, inspeção de AP027].

- **Efeito na estimativa:** com o β de cada item (limitado a [IC90 inferior, 0]), a economia determinística de E2 no horizonte cai de **203 para 114 milhões** (−44%) [CALC: d02]. Os três itens acima respondiam por ~102 milhões dos 203.
- O decisor reconheceu qualitativamente que, nos itens de fonte única, "a economia depende de negociação, não de concorrência". Mesmo assim, aplicou a eles o β estatístico, em vez de tratá-los como cenário de negociação com faixa própria [OBS: `05_economia.md` §3].

### 4.2 Erro no ponto de equilíbrio do risco

O valor declarado é ~41%; o correto é ~70%. Conservador; ver `02_calculos.md` C14 [CALC].

### 4.3 Faixa de renovação dos 1A estreita demais

- A H11 supõe renovação entre −5% e +10% do último preço DLOG. O histórico do pacote já mostrava trocas de fornecedor e de modalidade (PDP) com saltos grandes:
  - AP002 adalimumabe: DLOG pagou 417,00 (Butantan, 2022), 141,05 (AbbVie, 2023) e 126,94 (Pfizer, 2024) [OBS: `precos_comprasgov`];
  - AP001 infliximabe: 658,99, depois 300,31.
- Os 39 itens centralizados respondem por **81%** do custo estimado (5,28 de 6,48 bi). Mesmo assim, a faixa total foi dominada pela quantidade, não pelo risco de preço de renovação [CALC: `mc_resumo.txt`].

### 4.4 O bloco 1A ficou sem alternativas quantificadas

- As "táticas" para os 1A (renovação, inexigibilidade, PDP) aparecem como comuns a todas as estratégias, sem custo nem faixa.
- Nos 9 itens 1A sem compra DLOG visível, o preço foi atribuído por hipótese (H18). O decisor pediu verificação, o que é correto, mas a decisão real de maior valor (81% do custo) ficou fora da comparação [INF].

### 4.5 Limite de crescimento (H03)

O teto de +30% para o crescimento anual foi declarado como risco para os itens em rampa (AP013, AP014, AP024, AP050), mas não entrou na faixa alta de quantidade (H05 soma só 10%) [OBS]. Ex post, só ilustrativo: AP050, AP014, AP024 e AP021 ficaram acima da faixa (`04_comparacao_ex_post.md`).

### 4.6 E2 contra E3 depende em parte da velocidade de transição suposta

- O decisor supõe 40–70% do volume sob a ata em E2 e 20–60% em E3 (H13, H14).
- Com a mesma transição (s=0,55), a vantagem de E2 sobre E3 cai de 97 para 58 milhões, mas não se inverte [CALC: `trabalho/f01_sensibilidade.py`, coluna `eco_E3_s055_mesma_transicao`].

### 4.7 Contaminação de AP052 não detectada

O item mistura registros de supositório (falha do pacote). O decisor leu a amplitude de preço como heterogeneidade entre compradores [CALC: `02_calculos.md` C23].

### 4.8 Riscos omitidos ou pouco explorados

1. A política comercial dos fabricantes de monopólio, que pode baixar ou subir preços para todos de uma vez, independentemente do arranjo de compra (§4.1).
2. A dependência de PDP e das trocas de fornecedor nos 1A (§4.3).
3. O enquadramento do Grupo 2 em "compra nacional" (§3).
4. A sobreposição de E2 com atas estaduais vigentes, que o decisor cita só como "ponte", sem quantificar.

## 5. Conclusão

- **Estrutura e direção:** a decisão é bem formulada, legal, respeita as competências, é transparente e trata as incertezas melhor do que o mínimo exigido. A recomendação de E2 segue o próprio critério do decisor e sobrevive às correções (ver `05_sensibilidade.md`).
- **Magnitude:** a principal fragilidade é a economia projetada. Ela depende de transferir um β agregado a itens monopolistas cujos preços, já em 29/01/2025, não variavam com o volume. A economia esperada é cerca de metade do valor anunciado.
- **Classificação:** "parcialmente adequado", com confiança média. O julgamento das fragilidades 4.1 e 4.3 depende de inferência sobre o mecanismo de formação de preço, não de um dado conclusivo.
