# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is the repository for the official website of House of Di Lorenzo Productions. It is currently a greenfield project: as of this writing it contains only a README and no source code, build tooling, tests, or framework configuration.

## Current State

- No package manager manifest (no `package.json`, `requirements.txt`, etc.), so there are no build, lint, or test commands yet.
- No web framework or static site generator has been chosen yet.
- The default branch is `main`.

## Guidance for Future Work

- When the site's technology stack is chosen and scaffolded (e.g., a static site, or a framework like Astro/Next.js), update this file with the actual build, dev-server, lint, and test commands, and describe the resulting project structure.
- Until then, do not assume any tooling exists — verify with the repository contents before running commands.
