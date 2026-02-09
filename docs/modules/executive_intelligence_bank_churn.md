# Executive Intelligence – Bank Churn

## Objetivo do módulo
Este módulo fornece um fluxo completo para ingestão, governança, engenharia de features, predição de churn e resumo executivo direcionado a stakeholders. Ele foi desenhado para funcionar como um blueprint reutilizável no AION. 

## Onde entra o dataset
- O dataset CSV é consumido pelo **CsvDataSourceNode** (config `path` ou `uploaded_file_id`). 
- O fluxo exemplo utiliza `data/bank_churn.csv` como referência. 

## Colunas sensíveis e tratamento
As colunas abaixo são consideradas sensíveis e são tratadas pelo **PIIRedactionNode**:
- `Surname`: removida do dataset.
- `CustomerId`: mascarada via hash.

O node gera um relatório com tags de compliance (ex: `LGPD`, `PII_REDACTED`) para auditoria.

## Como treinar o modelo (modo treino)
O módulo pressupõe um modelo treinado e serializado (ex: `artifacts/model.pkl`). 
1. Prepare o dataset com as mesmas features usadas pelo **FeatureEngineeringBankChurnNode**.
2. Treine seu modelo localmente (ex: scikit-learn) com as colunas numéricas e os one-hot de `Geography` e `Gender`.
3. Salve o artefato em `artifacts/model.pkl` para uso no runtime.

## Como rodar o flow no runtime
1. Garanta que o dataset e o modelo existam nos caminhos configurados.
2. Execute o flow do exemplo:
   - `examples/executive_intelligence_bank_churn.flow.json`
3. O runtime executa o DAG sequencialmente e retorna:
   - dados sanitizados,
   - features,
   - probabilidades de churn,
   - fatores explicáveis,
   - e o executive brief.

## Limitações
- Resultados são probabilísticos e dependem do modelo treinado.
- A explicabilidade atual utiliza coeficientes/feature importance simples (não SHAP).
- O executive brief é gerado por template (não por LLM), evitando promessas excessivas.
