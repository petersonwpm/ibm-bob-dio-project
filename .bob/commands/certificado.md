---
description: Gera um certificado fictício em markdown com nome do usuário e trilha concluída
argument-hint: <nome-do-usuario> <trilha>
---

O usuário quer um certificado de conclusão. Nome: **$1** | Trilha: **$2**

Siga os passos abaixo:

1. Leia o arquivo `dio_explorer/data/trilhas_dio.json`.
2. Encontre a trilha cujo `name` ou `technology` contenha (case-insensitive) o termo "$2". Se não encontrar, use os dados fornecidos pelo usuário para gerar o certificado mesmo assim.
3. Gere a data de emissão como a data atual no formato brasileiro (DD de mês por extenso de AAAA).
4. Gere um código de verificação único no formato `DIO-XXXX-XXXX-XXXX` onde X são caracteres alfanuméricos aleatórios em maiúsculas.

### Formato de saída obrigatório:

---

```markdown
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║              🎓  CERTIFICADO DE CONCLUSÃO  🎓                    ║
║                        DIO — Digital Innovation One              ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  Certificamos que                                                ║
║                                                                  ║
║          ✨  <NOME DO USUÁRIO EM MAIÚSCULAS>  ✨                 ║
║                                                                  ║
║  concluiu com êxito a trilha de aprendizado:                     ║
║                                                                  ║
║          📚  <Nome completo da trilha>                           ║
║                                                                  ║
║  Tecnologia: <technology>                                        ║
║  Nível:      <level>                                             ║
║  Módulos:    <modules> módulos concluídos                        ║
║  XP obtido:  <total_xp> XP                                       ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  🏅 Badges conquistados:                                         ║
║     <liste cada badge da trilha com emoji 🎖️>                    ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  📅 Data de Emissão: <data atual por extenso>                    ║
║  🔐 Código de Verificação: <DIO-XXXX-XXXX-XXXX>                  ║
║  🌐 Verifique em: web.dio.me/certificate/<código>                ║
║                                                                  ║
║  ___________________________    ___________________________      ║
║  Assinatura do Instrutor          Diretor Acadêmico DIO          ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

Após o certificado, adicione uma seção:

## 🚀 Próximos Passos Recomendados
Sugira 3 trilhas complementares (baseadas nas trilhas do JSON) que o usuário pode fazer após concluir esta. Liste com nome, tecnologia e nível.

Seja criativo, profissional e comemorativo no tom.
