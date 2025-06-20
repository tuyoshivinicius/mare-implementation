# my_project

MARE CLI project for automated requirements engineering.

## Getting Started

1. Configure your LLM API keys in `.env` (copy from `.env.template`)
2. Edit `input/requirements.md` with your actual requirements
3. Run the pipeline: `mare run`
4. Check status: `mare status`
5. Export results: `mare export markdown`

## Project Structure

- `input/` - Input requirements and user stories
- `output/` - Generated specifications and reports
- `.mare/` - MARE CLI configuration and workspace
- `templates/` - Custom templates for output formatting

## Template: basic
## LLM Provider: openai

For more information, visit: https://github.com/manus-ai/mare-cli
