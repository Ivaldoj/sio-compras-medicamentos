# 04 — Recomendação

## Estratégia recomendada: E2. Compra nacional compartilhada para os itens 1B e 2, com os 1A mantidos na DLOG

**O que fazer, por bloco de itens** (detalhe por item em `plano_por_apresentacao.csv`):

1. **38 itens 1A e AP007:** o MS mantém a compra centralizada, conforme a PRC GM/MS 2/2017, art. 49.
   - Renovar com prioridade:
     - as atas DLOG de 2022 (AP047, AP071, AP078, AP084, AP085);
     - os 9 itens sem compra programática visível na base (AP004, AP005, AP010, AP022, AP030, AP035, AP049, AP063, AP082), confirmando primeiro como são comprados hoje.
   - Fonte única: negociar ou usar inexigibilidade abaixo do PMVG.
   - PDP: dispensa pela Lei 14.133, art. 75, XII [CP].
   - Entregas trimestrais às SES.
2. **11 itens 1B/2:** SRP nacional com o MS/DLOG como gerenciador e as 27 SES como participantes.
   - A SES assina o contrato e paga.
   - No 1B, o financiamento federal pelo SIA continua como está.
   - Lote nacional com cadastro de reserva.
   - Nos 7 itens de fonte única, negociação nacional de preço.
   - Os contratos estaduais vigentes servem de ponte até a ata entrar em vigor.
3. **Contingência:**
   - se uma ata nacional fracassar, as SES usam adesão emergencial à ata do MS, que fica fora do limite do §5º (art. 86, §7º), ou SRP regional (E3);
   - se faltar cobertura, adesão limitada a atas vigentes.

**Custo estimado da cesta:** R$ 6,25 bi (p05–p95: 5,73–6,93), em valor de contratação.
- Centralizados: R$ 5,28 bi.
- Descentralizados: R$ 0,98 bi (0,86–1,12).

**Economia potencial:** R$ 221 mi (159–298) no horizonte, contra o status quo E1. Em regime pleno, R$ 405 mi/ano (337–483). Ver `05_economia.md`.

## Justificativa

1. **Menor custo em toda a faixa entre as estratégias viáveis.** [CALC: `03_comparacao.csv`]
   - E2 economiza 18% dos gastos descentralizados no horizonte. E3 economiza 10%; E4, 5%.
   - Sem a transição, E2 chega a 34%.
2. **Evidência empírica direta.** [CALC]
   - O efeito volume-preço é negativo e estatisticamente distinto de zero nos dois segmentos (β ≈ −0,08; IC90 exclui zero) [`trabalho/elasticidade.csv`].
   - Onde o MS já compra nacionalmente, paga em mediana 0,29× o preço estadual [`trabalho/mc_resumo.txt`].
3. **Respeita as competências.** [OBS/INF]
   - Ninguém assume a aquisição de outra esfera: a SES continua compradora e pagadora dos 1B/2. O MS só gerencia a ata, o que a Lei 14.133 (art. 86) e o Decreto 11.462/2023 permitem.
   - Não depende da LOA 2025 nem de mudar a PRC 2/2017, o que derruba E4.
4. **O risco é administrável.**
   - A economia só se anula se a probabilidade de fracasso do certame passar de ~41% [CALC].
   - Cadastro de reserva, cotas e contratos estaduais como ponte reduzem a exposição a fornecedor único.
   - Nos itens de fonte única (7 de 11), a concentração já existe em qualquer estratégia [OBS: `cmed_laboratorios`=1]. Centralizar não cria esse risco; só aumenta o poder de negociação.

## O que mudaria a recomendação

| Condição | Efeito |
|---|---|
| Efeito volume ≈ 0 (β ≥ 0) nos itens 1B/2, por exemplo se o diferencial observado for só PDP ou negociação | E2 perde a vantagem de custo (`sensibilidade.csv`: economia 0). A escolha passaria a depender de gestão e risco, e E1 ou E3 se tornariam equivalentes |
| Probabilidade de fracasso ou atraso do certame nacional > ~40%, ou recurso administrativo que suspenda a ata | E1 ou E3 passam a ser melhores |
| Menos de cerca de metade das SES aceita participar da IRP | a economia cai proporcionalmente, porque o volume é menor (o efeito vai para o nível E3). Migrar para E3 nas regiões que aderirem |
| Transição muito lenta (ata só depois de out/2025, s<0,2) | economia no horizonte < R$ 80 mi; a recomendação continua, mas o ganho passa para 2026 |
| Grupos de financiamento errados (ex.: itens "1A" que na verdade são 2, ou AP007) | muda a esfera responsável e o conjunto de itens descentralizados; recalcular |
| Fornecedor dominante sem capacidade para o volume nacional | dividir em lotes regionais dentro do mesmo SRP (E2 com volume próximo ao de E3) |
| LOA 2025 com corte forte na ação 4705 | não muda a ordenação, porque E2 não aumenta gasto federal. Pode exigir priorizar 1A por criticidade |

## Verificações antes de executar

1. **Grupo de financiamento:** validar os 50 itens contra o Anexo III da RENAME 2024. Em especial AP007 (imunoglobulina, que aparece como 1B mas é comprada pelo MS) e os itens 1A sem compra DLOG.
2. **Vínculos CATMAT e apresentação:** conferir manualmente AP012 (45 mg × 90 mg) e os 6 itens com divergência BPS/Compras.gov (AP001, AP008, AP012, AP027, AP042, AP068), além de AP044 e AP041, cujos preços DLOG foram marcados como extremos.
3. **Atas e contratos vigentes:** levantar, por SES e no MS, as vigências e saldos, para definir o calendário de entrada de cada SES na ata nacional e evitar lacunas.
4. **Estoques e demanda reprimida:** pedir às SES os estoques em 31/01/2025 e as filas de processos deferidos não atendidos. Isso ajusta as quantidades (`plano_por_apresentacao.csv`, faixa baixa–alta).
5. **Mercado:** consultar fornecedores sobre capacidade para volume nacional; confirmar registro Anvisa vigente dos produtos e a situação CAP e Convênio 87/02 de cada um.
6. **Tetos:** aplicar o PMVG ou PF da lista CMED vigente na data do certame, com o ICMS da UF de destino.
7. **Governança:** pactuar na CIT o modelo de IRP nacional, o cronograma e as regras de cada SES (quantidades, local de entrega, contrapartida 1B); obter parecer jurídico do MS sobre o MS gerenciar ata de itens que não adquire.
8. **Orçamento:** quando a LOA 2025 sair, confirmar que a dotação da ação 4705 comporta os R$ 5,3 bi dos centralizados (38% do empenhado em 2024) e as transferências 1B.
