# AGENTS.md

## Agent skills

This repo is set up for [Matt Pocock's engineering skills](https://github.com/mattpocock/skills). The skills aren't vendored here; install them for your agent by following the [installation steps in that repo](https://github.com/mattpocock/skills#installation-30-second-setup). In Claude Code:

```bash
claude plugin install mattpocock-skills@claude-plugins-official
```

Skip that repo's `/setup-matt-pocock-skills` step: this repo's configuration is already committed below and in `docs/agents/`. Re-run it only to switch issue trackers or start over.

### Issue tracker

Issues are tracked in this repo's GitHub Issues, via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
