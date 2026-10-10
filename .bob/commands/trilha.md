---
description: Busca uma trilha DIO pela tecnologia e exibe um plano de estudos formatado
argument-hint: <tecnologia>
---

O usuário quer ver o plano de estudos da trilha DIO relacionada à tecnologia: **$1**

Siga os passos abaixo:

1. Leia o arquivo `dio_explorer/data/trilhas_dio.json`.
2. Encontre a trilha cujo campo `technology` contenha (de forma case-insensitive) o termo "$1". Se houver mais de uma correspondência, liste todas. Se nenhuma for encontrada, informe o usuário e sugira tecnologias disponíveis no arquivo.
3. Para cada trilha encontrada, exiba o plano de estudos no seguinte formato markdown:

---

## 📚 Plano de Estudos — <name>

| Campo         | Detalhe                  |
|---------------|--------------------------|
| 🏷️ Tecnologia | <technology>             |
| 🎯 Nível      | <level>                  |
| 📦 Módulos    | <modules> módulos        |
| ⭐ XP Total   | <total_xp> XP            |
| ♾️ Vitalício  | Sim / Não                |

### 🏅 Badges Disponíveis
Liste cada badge de `available_badges` como um item de lista com emoji 🎖️.

### 🗓️ Módulos do Plano de Estudos
Gere uma lista numerada de módulos fictícios e coerentes com a tecnologia e nível da trilha. A quantidade de itens deve ser igual ao valor do campo `modules`. Cada módulo deve ter um título descritivo e realista.

### 📺 Lives Incluídas
Liste cada live de `lives` com título e data formatada em pt-BR.

### 🏷️ Promoção Ativa
Exiba as informações de `promotions`: desconto, validade e descrição. Se `discount` for "0%", informe que não há promoção ativa.

---

Seja objetivo e use formatação markdown limpa e profissional.
