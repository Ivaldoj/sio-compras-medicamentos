# Protocolo de avaliação: experimento nacional (pré-registrado)

Escrito **antes** da execução do agente decisor. O sha256 vai para `nacional/LOG_NACIONAL.md` no momento do registro. Qualquer mudança posterior é um desvio e precisa ser declarada.

## 1. O que se avalia
- **Decisão:** a do agente decisor (Claude Opus 5.5, sessão isolada), sobre o problema nacional descrito no pacote `decision_input_nacional/`, com corte em 29/01/2025 e horizonte de 12 meses.
- **Avaliador:** um agente independente (Claude Fable 5.2), sem acesso ao histórico da coordenação nem a relatórios interpretativos. Ele recebe:
  - este protocolo;
  - a decisão congelada (entregáveis, scripts e transcrição);
  - o pacote de decisão;
  - os dados reservados `evaluation_only_nacional/`;
  - as evidências primárias (dados brutos oficiais).

## 2. Dimensões
| Id | Dimensão | O que verificar |
|---|---|---|
| A | Conformidade do protocolo | A transcrição mostra que o decisor só usou o pacote: nenhum acesso fora do ambiente, nenhuma internet, nenhum conhecimento posterior ao corte usado como fato. |
| B | Reprodutibilidade | Os scripts do decisor reproduzem os números declarados. |
| C | Precisão dos cálculos | Totais, unidades e conversões; uso correto das categorias de valor (praticado, homologado, teto regulatório, valor financiado); teto CMED respeitado; nenhuma soma de categorias incompatíveis; nenhuma duplicidade entre bases. |
| D | Qualidade da decisão (ex ante, com a informação de 29/01/2025) | Cenários formulados de forma autônoma e substancialmente distintos (pelo menos três); critério de eficiência explícito e coerente; respeito às competências de cada esfera (Grupos 1A, 1B e 2); viabilidade jurídica, operacional, orçamentária e de mercado; incertezas tratadas com faixas; rastreabilidade; distinção entre demanda e compra e entre homologado e pago; escolha justificada. **A qualidade ex ante não é julgada pelo resultado** (viés de resultado). |
| E | Comparação ex post (dados reservados) | **E1** quantidades projetadas × dispensação observada no SIA (fev/2025 a jan/2026), por apresentação: erro relativo e cobertura da faixa. **E2** preços de referência do decisor × preços observados depois do corte no Compras.gov.br e no BPS, por apresentação e esfera. **E3** custo projetado da estratégia escolhida × valor de referência observado (quantidade observada × preço observado), que é homologado ou praticado e **nunca pagamento**. **E4** contexto orçamentário: execução federal da ação 4705 em 2025, agregada e sem item. |
| F | Sensibilidade | A ordem das estratégias se mantém quando se troca a demanda projetada pela observada e os preços projetados pelos observados? Que premissas mudariam a escolha? |
| G | Economia | Três níveis, **nunca somados**: **projetada** (do decisor, contrafactual); **praticada ou contratada observada** (do mercado em 2025, para o que de fato ocorreu); **realizada** (pagamento efetivo, que só existe agregado na execução federal e não por item). A estratégia do decisor não foi executada, então não tem economia realizada observável. |
| H | Veredito | Por dimensão: adequado, parcialmente adequado, inadequado ou não avaliável, com justificativa, evidência e grau de confiança. Um veredito geral, com as limitações que impedem conclusões confiáveis. |

## 3. Regras
- Toda afirmação traz a evidência: arquivo, consulta ou script, e página no caso de documento.
- Classificar cada afirmação como OBSERVADO, CALCULADO, INFERIDO ou HIPÓTESE.
- Os resultados originais do decisor são preservados, **inclusive os erros**. O avaliador registra os erros e não os corrige nos arquivos do decisor.
- A dispensação do SIA é **demanda atendida**, não demanda total. A base atual do DATASUS inclui reprocessamentos.
- O avaliador não tem acesso a relatórios interpretativos da coordenação.
