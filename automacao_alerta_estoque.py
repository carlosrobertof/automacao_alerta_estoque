import pandas as pd

# Ler arquivo
df = pd.read_csv("dados_estoque.csv", encoding="latin-1", sep=",")

# Calcular cobertura e giro
df["cobertura_dias"] = df["estoque"] / df["saida_media"]
df["giro_estoque"] = df["saida_media"] / df["estoque"].replace(0, pd.NA)

# Classificar status
df["status"] = df["cobertura_dias"].apply(
    lambda x: "Baixa cobertura" if x < 10 else "Saudável" if x <= 30 else "Excesso"
)

# Corrigir produtos com estoque zero
df.loc[df["estoque"] == 0, "status"] = "Ruptura"

# Classificar prioridade
df["prioridade"] = "Normal"
df.loc[df["status"] == "Ruptura", "prioridade"] = "Crítica"
df.loc[(df["status"] == "Baixa cobertura") & (df["giro_estoque"] >= 0.5), "prioridade"] = "Alta"
df.loc[(df["status"] == "Baixa cobertura") & (df["giro_estoque"] < 0.5), "prioridade"] = "Média"
df.loc[df["status"] == "Excesso", "prioridade"] = "Baixa"

# Arredondar valores
df["cobertura_dias"] = df["cobertura_dias"].round(2)
df["giro_estoque"] = df["giro_estoque"].fillna(0).round(4)

# Filtrar produtos críticos
df_criticos = df[df["prioridade"].isin(["Crítica", "Alta"])]
df_criticos = df_criticos.sort_values(by="cobertura_dias")

# Contagens para resumo
total_produtos = len(df)
qtd_ruptura = (df["status"] == "Ruptura").sum()
qtd_baixa = (df["status"] == "Baixa cobertura").sum()
qtd_excesso = (df["status"] == "Excesso").sum()
qtd_criticos = (df["prioridade"] == "Crítica").sum()

pct_ruptura = qtd_ruptura / total_produtos
pct_baixa = qtd_baixa / total_produtos

categoria_risco = df[df["status"].isin(["Ruptura", "Baixa cobertura"])]["categoria"].value_counts()

if len(categoria_risco) > 0:
    categoria_mais_critica = categoria_risco.index[0]
else:
    categoria_mais_critica = "Nenhuma"


# Montar resumo
resumo = f"""

ALERTA AUTOMÁTICO DE ESTOQUE
============================

Total de produtos analisados: {total_produtos}
Produtos em ruptura: {qtd_ruptura} ({pct_ruptura:.0%})
Produtos com baixa cobertura: {qtd_baixa} ({pct_baixa:.0%})
Produtos em excesso: {qtd_excesso}
Itens com prioridade crítica: {qtd_criticos}
Categoria com maior concentração de risco: {categoria_mais_critica}

RECOMENDAÇÃO:
- Priorizar reposição dos itens em ruptura
- Revisar produtos com baixa cobertura
- Reavaliar compras de itens com excesso
"""

# Exportar Excel
with pd.ExcelWriter("relatorio_estoque_tratado.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Base Tratada", index=False)
    df_criticos.to_excel(writer, sheet_name="Produtos Criticos", index=False)

# Salvar resumo em txt
with open("resumo_alerta.txt", "w", encoding="utf-8") as f:
    f.write(resumo)

# Mostrar no terminal
print(resumo)
print("Arquivos gerados com sucesso.")