# /icp: encuentra a tu cliente ideal (skill gratuita de We Make Tools)

**Español abajo, English below.**

## Qué es

Una skill para Claude que te hace una entrevista corta sobre tu negocio y te entrega un PDF con tu **North Star**:
a quién le vendes, con qué requisitos, quién NO es tu cliente, dónde encontrarlo, cómo compra y un plan de 30 días.
Usa el método de mejores clientes de Alex Hormozi (top 20 por ciento, calificadores compartidos, prueba de
separación) reforzado con el canon B2B. Si todavía no tienes clientes, te guía para elegir el mercado y validarlo.

Tus respuestas no salen de tu computadora ni de tu sesión de Claude. El PDF se genera localmente, sin instalar nada:
solo hace falta Python 3.8 o superior, que claude.ai ya trae y que casi toda computadora tiene.

## Cómo instalarla

**Descarga** [`icp.zip`](https://github.com/stevenwemaketools/icp-skill/raw/main/dist/icp.zip) (es la carpeta `icp/` de este repositorio, comprimida).

**claude.ai (recomendado).** Ajustes, Capacidades, Skills: sube el archivo `icp.zip`. Activa "Code execution and
file creation" si no está activo. Una vez subida, la skill también aparece en la app de escritorio de Claude y en
Claude Code con la misma cuenta.

**Claude Code (manual).** Copia la carpeta `icp/` a `~/.claude/skills/icp/` y reinicia la sesión. Aparece como `/icp`.

```sh
git clone https://github.com/stevenwemaketools/icp-skill.git && cp -r icp-skill/icp ~/.claude/skills/icp
```

**App de escritorio de Claude.** Misma cuenta que claude.ai: no hay que hacer nada más.

## Cómo usarla

Escribe: **"quiero definir mi cliente ideal"** (o "/icp" en Claude Code). Responde una pregunta por turno, 10 a 14
en total si ya tienes clientes, 8 a 10 si no. Al final confirmas tu North Star y recibes `icp.pdf` y `icp.md`.
Si tienes prisa, escribe "dame el resultado ya": la skill marca lo que falta como "Por confirmar".

## Qué sigue

- Descubre qué procesos de tu negocio ya pueden operar con agentes: https://wemake.tools
- ¿Construimos el motor que encuentra a este cliente por ti? Agenda 30 minutos: https://api.leadconnectorhq.com/widget/booking/7imvEOkx8vkO0SgUNdaB

---

## What it is

A Claude skill that runs a short interview about your business and gives you a PDF with your **North Star**: who you
sell to, with which requirements, who is NOT your customer, where to find them, how they buy, and a 30-day plan. It
uses Alex Hormozi's best-customer method (top 20 percent, shared qualifiers, separation test) hardened with the B2B
canon. No customers yet? It walks you through choosing a market and validating it.

Your answers never leave your computer or your Claude session. The PDF is generated locally with nothing to install:
Python 3.8 or newer, which claude.ai already has and almost every computer does.

## Install

**Download** [`icp.zip`](https://github.com/stevenwemaketools/icp-skill/raw/main/dist/icp.zip) (the `icp/` folder of this repository, zipped).

**claude.ai (recommended).** Settings, Capabilities, Skills: upload `icp.zip`. Turn on "Code execution and file
creation" if it is off. Once uploaded, the skill also shows up in the Claude desktop app and in Claude Code on the
same account.

**Claude Code (manual).** Copy the `icp/` folder to `~/.claude/skills/icp/` and restart the session. It appears as `/icp`.

```sh
git clone https://github.com/stevenwemaketools/icp-skill.git && cp -r icp-skill/icp ~/.claude/skills/icp
```

**Claude desktop app.** Same account as claude.ai: nothing else to do.

## Use

Type: **"help me define my ideal customer"** (or "/icp" in Claude Code). Answer one question per turn, 10 to 14 in
total if you already have customers, 8 to 10 if not. At the end you confirm your North Star and get `icp.pdf` and
`icp.md`. In a hurry? Say "give me the result now" and the skill marks what is missing as "To confirm".

## What's next

- Find out which of your processes can already run on agents: https://wemake.tools
- Want the engine that finds this customer for you? Book 30 minutes: https://api.leadconnectorhq.com/widget/booking/7imvEOkx8vkO0SgUNdaB

Source: https://github.com/stevenwemaketools/icp-skill. MIT License, 2026 We Make Tools. On Windows the interpreter may be `python` instead of `python3`.
