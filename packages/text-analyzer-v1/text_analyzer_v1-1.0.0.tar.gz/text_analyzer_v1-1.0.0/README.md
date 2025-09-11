# Text Analyzer

A simple Python package for analyzing text and providing statistics.

## Installation

```bash
pip install text-analyzer
```

## Usage

```python
from text_analyzer import analyze_text

stats = analyze_text("Hello world. This is a test.")
print(stats)
# {'word_count': 6, 'sentence_count': 2, 'character_count': 27, 'average_word_length': 4.0}
```

## Function

- `analyze_text(text)`: Returns a dictionary with word count, sentence count, character count, and average word length.

## License

MIT License
