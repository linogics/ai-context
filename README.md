# ai-context

A [Claude Code](https://code.claude.com/docs/en/plugins) plugin marketplace by linogics. Each skill ships as its own plugin, so you install only the ones you want.

## Install

Add the marketplace once, then install any plugin from it:

```text
/plugin marketplace add linogics/ai-context
/plugin install d2-tala@linogics
```

On Claude Code 2.1.275 or later you can do both in one step:

```text
/plugin install d2-tala --marketplace linogics/ai-context
```

Update later with `/plugin marketplace update linogics`.

## Skills

| Plugin | What it does |
|--------|--------------|
| [d2-tala](plugins/d2-tala/skills/d2-tala/SKILL.md) | Writes and migrates [d2](https://d2lang.com) diagrams for the TALA layout engine. Boxes get hand-pinned positions on a 20px grid, equal sizes and straight, labeled edges. It renders every diagram to PNG and inspects it until the layout is clean. |

### d2-tala requirements

- Python 3 for the bundled render script.
- The `d2` binary on your `PATH`, or Docker. Without `d2` the script uses the `terrastruct/d2` image, which bundles TALA.
- TALA is open source, so no license key is needed and renders carry no watermark.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Security issues go through [SECURITY.md](SECURITY.md).

## License

[BSD 3-Clause](LICENSE)
