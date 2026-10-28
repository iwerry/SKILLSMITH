# SKILLSMITH

**Build, inspect, validate, audit and package portable Agent Skills.**

**Created by Daniel Rodrigues** · [English](#english) · [Español](#español) · [Português](#português)

> SKILLSMITH is an open-source, English-first skill engineering toolkit. No model API key is required for the CLI. It scaffolds complete, editable Agent Skills and validates their packaging; it does not promise automatic runtime activation in every client.

## English

### Features
- Agent-facing creator skill in `skill-smith/SKILL.md`.
- Python standard-library CLI: `create`, `validate`, `audit`, `package`.
- Progressive disclosure: concise metadata, on-demand procedures, optional resources.
- YAML frontmatter checks, name/description limits, structure checks, basic secret detection.
- Trigger examples, negative boundaries, test cases and a 12-point quality review template.
- Reproducible ZIP packages with path-safety checks.
- English source, cross-platform guidance, no paid dependencies.

### Quick start

Requires Python 3.10+.

```bash
python -m skillsmith create --name cinematic-storyboard --purpose "Produces cinematic storyboards from a creative brief" --when "the user requests a shot list or visual storyboard" --output ./generated
python -m skillsmith validate ./generated/cinematic-storyboard
python -m skillsmith audit ./generated/cinematic-storyboard
python -m skillsmith package ./generated/cinematic-storyboard --output ./dist
python -m unittest discover -s tests -v
```

The generator creates an **editable starter**, not a claim of production quality. Replace its illustrative operational examples, verification criteria, trigger prompts and input/output schema with domain-specific requirements before distribution.

### Install the agent creator
Copy the `skill-smith/` directory to your agent's supported skill directory (for example `.claude/skills/skill-smith/` or a supported project skills directory). Read the host documentation before relying on automatic discovery. Alternatively provide `skill-smith/SKILL.md` explicitly as context. The CLI itself works independently of agent support.

### Structure
```text
SKILLSMITH/
├── skill-smith/SKILL.md
├── skillsmith/__init__.py
├── skillsmith/__main__.py
├── tests/test_cli.py
├── README.md
├── LICENSE
└── .gitignore
```

### Quality and security
The `audit` command is a **heuristic checklist**, not an LLM-based empirical performance measurement. `validate` handles a conservative YAML subset without third-party packages and may reject valid complex YAML; use the official `skills-ref` validator for broader spec conformance. ZIP creation excludes symlinks and rejects unsafe paths. Always review generated code and secrets manually. Skills are instructions, **not access-control boundaries**; enforce permissions in the runtime/tool gateway.

Documentation: [Agent Skills specification](https://agentskills.io/specification) · [Agent Skills reference repository](https://github.com/agentskills/agentskills).

## Español

**SKILLSMITH** es un creador y validador de habilidades para agentes de IA, desarrollado por **Daniel Rodrigues**. Los archivos internos se escriben en inglés para facilitar la portabilidad, mientras que esta guía ofrece español y portugués.

**Funciones:** crear estructuras con `SKILL.md`, validar metadatos, revisar calidad con 12 criterios y exportar archivos ZIP. No requiere servicios de pago para la CLI.

**Inicio rápido:**
```bash
python -m skillsmith create --name video-production --purpose "Plans video production workflows" --when "the user asks for a production plan" --output ./generated
python -m skillsmith validate ./generated/video-production
python -m skillsmith package ./generated/video-production --output ./dist
```

Personaliza las instrucciones, los ejemplos y las pruebas antes de publicar. La compatibilidad y la activación automática dependen de cada plataforma. Consulta la [especificación oficial](https://agentskills.io/specification).

## Português

O **SKILLSMITH** é um criador, validador, auditor e empacotador de Skills para agentes de IA, desenvolvido por **Daniel Rodrigues**. Os arquivos técnicos são escritos em inglês, e o README está disponível em três idiomas.

**Recursos:** criação de diretórios com `SKILL.md`, validação de metadados, auditoria orientativa com 12 critérios e exportação ZIP. A CLI não precisa de API paga.

**Comece agora:**
```bash
python -m skillsmith create --name video-production --purpose "Plans video production workflows" --when "the user asks for a production plan" --output ./generated
python -m skillsmith validate ./generated/video-production
python -m skillsmith audit ./generated/video-production
python -m skillsmith package ./generated/video-production --output ./dist
```

Revise e personalize os passos operacionais, os exemplos, as condições de acionamento e os testes antes de distribuir. A importação e o acionamento automático dependem do ambiente de execução. Consulte a [especificação oficial](https://agentskills.io/specification).

---

MIT License · Copyright (c) 2026 Daniel Rodrigues.
