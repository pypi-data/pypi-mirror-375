# textmode-env

### Overview
- **Environment ID**: `textmode-env`
- **Short description**: Multi-turn environment that wraps a local Textmode Fantasy Console and ROMs (e.g., Tetris). The model plays by sending one key per turn; the environment returns a compact observation of the screen.
- **Tags**: games, multi-turn, agent, exploration, tetris

### Datasets
- **Primary dataset(s)**: Inline single-prompt dataset instructing the agent to send one key per turn.
- **Source links**: Local codebase (`engine/console.py`, `roms/`).
- **Split sizes**: N/A (single inline prompt by default).

### Task
- **Type**: multi-turn
- **Parser**: none (raw messages)
- **Rubric overview**:
  - Score reward: normalized final score from the console.
  - Exploration reward: number of unique visual states visited based on hashing snapshot (`cols`, `rows`, `chars`), normalized by turns.

### Quickstart
Run an evaluation with default settings:

```bash
uv run vf-eval textmode-env
```

Configure model and sampling:

```bash
uv run vf-eval textmode-env \
  -m gpt-4.1-mini \
  -n 10 -r 2 -t 1024 -T 0.7 \
  -a '{"rom": "tetris", "max_turns": 256}'
```

Notes:
- Use `-a` / `--env-args` to pass environment-specific configuration as a JSON object.
- The agent must respond each turn with exactly one key: `up`, `down`, `left`, `right`, `enter`, or `quit`. JSON form `{ "key": "left" }` is also accepted.

### Environment Arguments

| Arg | Type | Default | Description |
| --- | ---- | ------- | ----------- |
| `rom` | str | `"tetris"` | Which ROM to boot: `"tetris"`, `"demo"`, or `"menu"` |
| `max_turns` | int | `256` | Maximum number of interaction turns per rollout |

### Metrics

| Metric | Meaning |
| ------ | ------- |
| `reward` | Weighted sum of rubric criteria (score + exploration) |
| `score_reward` | Normalized final score (`min(1.0, score/1000)`) |
| `exploration_reward` | Unique snapshot hashes per turn (`unique_states / max(10, turns)`) |
| `unique_states` | Count of unique visual states visited in the rollout |
