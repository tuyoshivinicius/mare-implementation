# test_integration_project

Projeto MARE CLI para engenharia de requisitos automatizada.

## Começando

1. Configure suas chaves de API LLM em `.env` (copie de `.env.template`)
2. Edite `input/requirements.md` com seus requisitos reais
3. Execute o pipeline: `mare run`
4. Verifique status: `mare status`
5. Exporte resultados: `mare export markdown`

## Estrutura do Projeto

- `input/` - Requisitos de entrada e user stories
- `output/` - Especificações e relatórios gerados
- `.mare/` - Configuração e workspace do MARE CLI
- `templates/` - Templates personalizados para formatação de saída

## Template: basic
## Provedor LLM: openai

Para mais informações, visite: https://github.com/manus-ai/mare-cli
