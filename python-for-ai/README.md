# Recipe Generator Streamlit App

This Streamlit app generates short recipes from a list of ingredients. It mirrors code in `calling_llm/call-llm.ipynb` and supports Google GenAI (if installed and configured) or OpenAI as a fallback.

Run locally:

```bash
python -m pip install -r requirements.txt
# The app will attempt to load credentials from `calling_llm/.env` if present.
# You can also set `OPENAI_API_KEY` or other provider env vars as needed.
streamlit run streamlit_app.py
```

Notes:
- The original notebook uses `from google import genai` and `genai.Client()`.
 - If you want to use Google GenAI, install the `google-generativeai` client and provide credentials.
 - Place a `.env` with `GOOGLE_API_KEY=...` inside the `calling_llm` directory to mirror the notebook setup.
