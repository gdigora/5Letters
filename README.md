# 5Letters - Russian Word Search Bot

A Telegram bot and CLI tool for finding 5-letter Russian words, perfect for Wordle helpers.

## Features

- 🔍 Smart search with flexible parameter order
- 📱 Telegram bot (no commands needed, just send your search)
- 💻 Terminal CLI for local usage
- 🎯 Supports Wordle-style filters: gray/yellow/green letters
- 📊 Results sorted by word frequency
- 🚀 Lightweight (only 2 Python dependencies)

## Project Structure

```
5Letters/
├── core/                    # Core library
│   ├── lexicon.py          # Load words from lexicon
│   ├── parser.py           # Parse user input
│   ├── search.py           # Filter words
│   └── __init__.py         # Package interface
├── examples/
│   └── cli.py              # Terminal version
├── data/
│   └── lexicon_ru_5.jsonl.gz  # 193KB word database
├── bot.py                   # Telegram bot (entry point)
├── requirements.txt         # Dependencies
├── .env.sample             # Environment template
└── README.md
```

## Search Syntax

The search syntax is flexible - **order doesn't matter**:

- `-абв` — Gray letters (excluded, not in word)
- `+где` — Yellow letters (required, in word but position unknown)
- `_а___` — Pattern (green, 5 characters with `_` for unknown)
- `1а5б` — Antipattern (position + forbidden letters there)

### Examples

1. Find words with "к" and "и", without "н", "з", "ф":
   ```
   +ки -нзф
   ```

2. Find words where 1st letter is "а", has "к" and "и":
   ```
   _а___ +ки -нзф
   ```

3. Find words with "к" and "и", where position 2 can't be "к":
   ```
   +ки -нзф 2к
   ```

4. Full example:
   ```
   -нзф +ки _а___ 2к
   ```

## Installation

### Prerequisites

- Python 3.12+
- pip

### Local Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd 5Letters
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.sample .env
   # Edit .env and add your TELEGRAM_TOKEN
   ```

## Usage

### Telegram Bot

1. **Run locally:**
   ```bash
   python bot.py
   ```

2. **Send messages to your bot:**
   - `/start` - Welcome message
   - `/help` - Syntax help
   - Any other message - Search query (e.g., `+ки -нзф`)

### CLI Version

```bash
# Basic search
python examples/cli.py +ки -нзф

# With pattern
python examples/cli.py -нзф +ки _а___ 2к

# Custom sorting
python examples/cli.py +ки -нзф --sort freq
python examples/cli.py +ки -нзф --sort alpha
```

## Deployment to Render.com

### Step 1: Prepare Your Repository

1. **Initialize git (if not already done):**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: 5Letters bot"
   ```

2. **Push to GitHub:**
   ```bash
   # Create repo on GitHub, then:
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### Step 2: Deploy on Render.com

1. **Create a new Web Service:**
   - Go to [Render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure the service:**
   - **Name:** `5letters-bot` (or your choice)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python bot.py`
   - **Instance Type:** `Free` (sufficient)

3. **Add Environment Variables:**
   - Click "Environment" tab
   - Add variable:
     - **Key:** `TELEGRAM_TOKEN`
     - **Value:** `<your-bot-token-from-botfather>`

4. **Deploy:**
   - Click "Create Web Service"
   - Wait for deployment to complete
   - Check logs to confirm bot is running

### Step 3: Test Your Bot

1. Open Telegram
2. Find your bot (@your_bot_username)
3. Send `/start` to begin
4. Send search queries like `+ки -нзф`

## Development

### Core Library API

```python
from core import load_lexicon, get_search_params, filter_words

# Load lexicon
words, freq_map = load_lexicon('data/lexicon_ru_5.jsonl.gz')

# Parse user input
params = get_search_params('+ки -нзф _а___')

# Filter words
results, stats = filter_words(
    words,
    params['must_have'],
    params['excluded'],
    params['pattern'],
    params['antipattern_constraints']
)
```

### Running Tests

```bash
# Test CLI
python examples/cli.py +ки -нзф

# Test bot locally
python bot.py
# Then test in Telegram
```

## Technical Details

- **No Docker:** Uses Render.com's native Python support
- **Lexicon:** Pre-built 5-letter Russian word database (193KB)
- **Dependencies:** Only `python-telegram-bot` and `python-dotenv`
- **Deployment:** Simple `pip install` + `python bot.py`
- **Word Frequency:** Sorted by Zipf scores for better results

## Troubleshooting

### Bot not responding
- Check Render.com logs for errors
- Verify `TELEGRAM_TOKEN` is set correctly
- Ensure lexicon file exists in `data/` directory

### "Lexicon file not found"
- Make sure `data/lexicon_ru_5.jsonl.gz` is committed to git
- Check file is included in deployment

### Local testing fails
- Install dependencies: `pip install -r requirements.txt`
- Create `.env` file with valid token
- Run from project root: `python bot.py`

## License

MIT License

## Author

Created for Wordle enthusiasts 🎮
