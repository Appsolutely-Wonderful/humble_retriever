# Humble Retriever
A tool that will log in to humble bundle and retrieve a list of all humble
monthly games.

## Usage
1. Install dependencies with pip

`pip install -r requirements.txt`

2. Import and run! When logging in, humble sends a verification code. The script
will ask you to enter the code from your email or from 2FA app.

Run from script:
```python
from humble_retriever import HumbleRetriever
driver = HumbleRetriever()
game_list = driver.list_all_games(<your_username>, <your_password>)
```

Run from cli:
```bash
python humble_retriever.py
```
