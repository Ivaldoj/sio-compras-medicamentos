# Protocolo da avaliação independente da decisão da Etapa 4 (pré-registrado)

Registrado em 23/11/2026, **antes** de rodar `scripts/33_avaliacao.py`. O sha256 deste arquivo está no `LOG_PRE_ETAPA_5.md`. Qualquer mudança posterior nas regras precisa ser registrada como desvio.

## 1. Objetos
- **Decisão do agente:** os arquivos congelados em `etapa4/ambiente_decisor/saida/` e `trabalho/`. Não são alterados.
- **Decisão real (linha de base):** PE 04/2025, pregão eletrônico por item, menor preço, contratos de 12 meses e sem ata de registro de preços. Dados em `data/evaluation_only/`.
- **Pacotes:**
  - v1 (`data/decision_input/`), o que o agente viu;
  - v2 (`data/decision_input_v2/`), com a errata das falhas confirmadas, usado só como sensibilidade.

## 2. Quem avalia
A mesma sessão que preparou os dados. Ela **não é cega**: conhece desde a Etapa 2 o resultado agregado do PE 04/2025 (doc 11).

Mitigações:
- regras fixadas aqui antes do cálculo;
- todo número produzido por script;
- nenhuma nota ou veredito de mérito nesta preparação. A avaliação de mérito fica para a Etapa 5.

## 3. Dimensões e métricas

### A. Reprodutibilidade (`scripts/32_reproduz_agente.py`)
Rodar os scripts do agente na ordem declarada, em cópia, e comparar as saídas com as congeladas.

### B. Verificação dos cálculos do agente
- **B1** E1 = Σ quantidade × `preco_ref_unitario` do plano por item (central, baixo e alto).
- **B2** As economias declaradas conferem: E2 − E1 e R1 − E1.
- **B3** Nenhuma referência acima do teto máximo aplicável, quando há teto.
- **B4** Nenhum preço "a conferir" usado como referência central.
- **B5** O teto usado pelo agente é um dos tetos dos vínculos aceitos (exata ou compatível) na alíquota da PB.
- **B6** Uma única `categoria_valor` por referência.
- **B7** As contagens declaradas conferem: itens acima do teto, sem referência externa, a conferir, e a parte das canetas no excesso.
- **B8** Exclusividade ME/EPP: os itens marcados valem até R$ 80.000 (LC 123/2006, art. 48, I), pela estimativa do órgão e pela referência do agente.

### C. Comparação com os dados reservados (ex post)
- **C1** Preço por item: razão homologado / referência do agente.
  - Medidas: mediana; razão ponderada por valor; % dos itens dentro da faixa [baixo, alto]; % acima do alto.
  - Cortes: fonte da referência, sinalizações e insulinas.
- **C2** Totais: homologado × E1 (central e faixa) × R0 × R1.
- **C3** Mercado nacional depois do corte: mediana dos registros compatíveis com compra ou resultado em 2025 (BPS e Compras.gov.br) × referência do agente × homologado.
- **C4** Itens com preço homologado acima do teto CMED aplicável de jan/2025.
- **C5** Risco de deserto da referência do agente: itens em que o preço que o mercado aceitou para este comprador (homologado) ficou acima do limite alto do agente. Contagem e valor.
- **C6** Execução:
  - contratado × empenhado × pago no PE 04/2025;
  - gasto de 2025–2026 por licitação, incluindo o contrato de desconto sobre a CMED (PE 12/2024).
- **C7** Escopo: necessidades que ficaram fora do plano (PE 25/2025).

### D. Viabilidade
Dimensões jurídica, operacional, orçamentária e de mercado. Para cada uma: a evidência ex ante (pacote e normas verificadas) e a ex post (dados reservados). Sem nota.

### E. Sensibilidade da recomendação
As fórmulas do agente (`trabalho/20_estrategias.py`) são recalculadas com:
- **S1** pacote v2;
- **S2** teto a 20% para produtos do Convênio 87/02 (fator mediano 20%/0% dos demais produtos);
- **S3** insulinas humanas 196–199 fora da compra municipal (fornecimento centralizado do MS);
- **S4** preços E1 = homologados reais;
- **S5** preços E1 = mediana nacional de 2025, quando houver;
- **S6** itens sem referência externa precificados pela estimativa limitada ao teto;
- **S7** demanda = fração empenhada observada (SRP paga d × C; contrato fixo compromete C);
- **S8** S2 + S3 + S4 combinados.

**Critério de "altera a decisão":** E1 deixa de ter o menor custo entre E1, E2 e E4. E3 conta só como complemento, como o agente definiu.

### F. Economia, em três níveis que nunca se somam
- **F1 Projetada:** ex ante, do agente, contrafactual.
- **F2 Contratada:** ex post, da decisão real. R0 − homologado e R1 − homologado. Não é economia realizada.
- **F3 Realizada:** exige quantidades entregues e preços pagos por item, que não existem.
  - A estimativa por contrato, sob a hipótese de mix proporcional, é rotulada como estimativa.
  - A estratégia do agente não foi executada, então não tem economia realizada observável.

## 4. Fora do escopo
- Atribuir nota ou veredito ao agente.
- Alterar `etapa4/` ou `data/decision_input/`.
- Fornecer ao agente qualquer dado posterior ao corte.

## 5. Limitações conhecidas antes do cálculo
- **Avaliador não cego.**
- **Contrafactual:** as estratégias não adotadas não têm resultado observado.
- **Execução por item desconhecida:** só existe por contrato e fornecedor.
- **Viés do homologado:** ele resulta de um certame cujo preço máximo era a estimativa do órgão, que fica em mediana 2× acima do mercado. Isso tende a puxar o homologado para cima em relação ao que um E1 com referência saneada obteria. O E1 com referência saneada, por sua vez, pode ter itens desertos.
