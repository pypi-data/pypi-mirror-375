# boostedprob

Utilities to compute "dominant tokens" and derive boosted probabilities from model log-probabilities.

## Install

- Locally (development editable install):

```bash
python -m pip install -e .
````

* From GitHub (example):

```bash
python -m pip install "git+https://github.com/yourusername/boostedprob.git"
```

## Example

```python
import torch
import boostedprob

# log_probs: shape [batch, seq_len, vocab]
# target: shape [batch, seq_len]
# (fill with your model outputs)

log_probs = torch.log_softmax(torch.randn(2, 4, 1000), dim=-1)
target = torch.randint(0, 1000, (2, 4))

scores = boostedprob.calculate_boostedprob(log_probs, target)
print(scores.shape)  # -> (2, 4)
```

## Build & publish

```bash
python -m pip install --upgrade build twine
python -m build
python -m twine upload dist/*
```

Or test first on TestPyPI (recommended).