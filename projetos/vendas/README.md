# Consolidação automática de vendas

Demonstração de portfólio de Rodrigo França. Todos os dados são fictícios.

## Problema
Uma loja recebe arquivos mensais de vendas e precisa juntar as informações, conferir duplicidades e preparar resumos.

## Solução
O script lê CSVs de um mesmo padrão, padroniza datas e nomes de produtos, calcula o total das vendas e gera resumos por mês e produto.
Duplicatas exatas por ID são removidas. Registros inválidos e IDs com informações divergentes são separados para revisão, sem desaparecer silenciosamente.

## Executar
Instale Python 3.10 ou superior, extraia o pacote e execute:

```bash
python consolidar.py
```

No Windows, também é possível usar `py consolidar.py`.
Não exige instalação de bibliotecas adicionais.
Os caminhos padrão são relativos ao script, independentemente da pasta de execução.

Para escolher outras pastas:

```bash
python consolidar.py --entrada minha_entrada --saida meu_resultado
```

## Entrada
CSV UTF-8, delimitador ponto e vírgula, com cabeçalho:
`id_venda;data;produto;quantidade;preco_unitario`.
Datas aceitas: dd/mm/aaaa e aaaa-mm-dd. Preço sem separador de milhar, com vírgula ou ponto decimal.
Uma linha representa uma venda de um produto. O ID deve ser único para essa linha.

## Saída
- vendas_consolidadas.csv: registros válidos, com total calculado.
- resumo_mensal.csv e resumo_produtos.csv: vendas, unidades e faturamento.
- duplicados.csv: cópias exatas removidas, com arquivo e linha.
- rejeitados.csv: registros que exigem revisão, com motivo.
- auditoria.json: contagens e faturamento para conferência.

Uma nova execução sobrescreve somente os arquivos de saída listados acima.
Os arquivos de entrada permanecem intactos. CSVs não contêm fórmulas nem atualização automática: execute novamente para atualizar os resultados.
No Excel, importe os CSVs com delimitador ponto e vírgula e decimal ponto para os resultados.

## Regras e limites
Em divergência de ID, a primeira ocorrência válida permanece e a seguinte vai para rejeitados. Os arquivos são lidos por nome, e suas linhas na ordem original.
Em um projeto real, a regra de conflitos deve ser acordada com o cliente.
Esta versão recebe CSV. Leitura nativa de XLSX, execução agendada, interface e integrações são extensões que precisam de escopo próprio.
Nenhum ganho de tempo ou receita de cliente real foi medido.

## Como apresentar
Abra Apresentacao_Portfolio.html no navegador e mostre a entrada e os resultados.
O texto do perfil está em Perfil_Rodrigo_Franca.md.
