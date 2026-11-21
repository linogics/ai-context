# Contributing

## Add a skill

Every skill is its own plugin under `plugins/`:

```text
plugins/<name>/
  .claude-plugin/plugin.json
  skills/<name>/SKILL.md
  skills/<name>/scripts/...    (optional)
```

1. Create the folder above. `SKILL.md` needs `name` and `description` in its frontmatter.
2. Write `plugin.json` with `name`, `version` (start at `1.0.0`), `description`, `author` and `license`.
3. Add an entry to `.claude-plugin/marketplace.json` with `name`, `source` (`./plugins/<name>`) and `description`.
4. Add a row to the skills table in `README.md`.
5. Refer to bundled files as `${CLAUDE_SKILL_DIR}/scripts/...`, never as an absolute or home path. The install location differs per machine.

## Versions

Plugins use semver in `plugin.json`. Users only receive an update when the version changes, so bump it in every PR that changes a plugin:

- patch: wording fixes, small script fixes
- minor: new rules, options or scripts
- major: changed behavior that breaks how people use the skill

## Check before you push

```bash
claude plugin validate .
claude plugin validate plugins/<name>
```

CI runs the same checks on every push and pull request.

## Commits

Use [conventional commits](https://www.conventionalcommits.org), for example `feat(d2-tala): add dark theme rule`.
