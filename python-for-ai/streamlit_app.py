import os
from dotenv import load_dotenv
from pathlib import Path

# Load credentials: prefer the `calling_llm/.env` alongside the notebook
base_dir = Path(__file__).parent
calling_env = base_dir / "calling_llm" / ".env"
if calling_env.exists():
    load_dotenv(dotenv_path=str(calling_env))
else:
    load_dotenv()

import streamlit as st

# Try to import Google GenAI client (matching the notebook). Fall back to OpenAI if not available.
genai = None
openai = None
client = None
try:
    from google import genai as _genai
    genai = _genai
    # If the library supports explicit configuration, pass the key from env
    try:
        if hasattr(genai, "configure") and os.environ.get("GOOGLE_API_KEY"):
            genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
    except Exception:
        pass
    client = genai.Client()
except Exception:
    genai = None

try:
    import openai as _openai
    openai = _openai
    if os.environ.get("OPENAI_API_KEY"):
        openai.api_key = os.environ.get("OPENAI_API_KEY")
except Exception:
    openai = None


def generate_recipe_google(ingredients, cuisine, diet, max_words=100):
    prompt = f"""
    Generate one food recipe using these ingredients: {', '.join(ingredients)}.
    Cuisine: {cuisine}
    Diet: {diet}
    Keep the recipe under {max_words} words. Provide a short title, ingredients list and simple steps.
    """
    if client is None:
        raise RuntimeError("Google GenAI client not available")
    # Prefer Chat.send_message when available to avoid AFC warnings with models.generate_content
    try:
        chat = getattr(client, "chat", None)
        if chat is not None and hasattr(chat, "send_message"):
            resp = chat.send_message(model="gemini-3.5-flash", input=prompt)
            return getattr(resp, "text", getattr(resp, "content", str(resp)))
    except Exception:
        # if chat usage fails, fall back to models.generate_content
        pass
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt,
    )
    return getattr(response, "text", str(response))


def generate_recipe_openai(ingredients, cuisine, diet, max_words=100):
    prompt = f"Generate one food recipe using these ingredients: {', '.join(ingredients)}. Cuisine: {cuisine}. Diet: {diet}. Keep under {max_words} words. Provide a short title, ingredients list and simple steps."
    if openai is None:
        raise RuntimeError("OpenAI client not available")
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens= max(150, int(max_words * 2)),
        temperature=0.8,
    )
    return res["choices"][0]["message"]["content"].strip()


def generate_recipe(ingredients, cuisine, diet, max_words=100):
    # Prefer Google GenAI when available (to mirror the notebook), otherwise OpenAI.
    if genai is not None and client is not None:
        return generate_recipe_google(ingredients, cuisine, diet, max_words)
    if openai is not None:
        return generate_recipe_openai(ingredients, cuisine, diet, max_words)
    raise RuntimeError("No LLM client available. Install and configure Google GenAI or OpenAI and set the appropriate API key.")


def main():
    st.set_page_config(page_title="Recipe Generator", layout="centered")
    st.title("Recipe Generator")
    st.write("Generate short recipes from a list of ingredients.")

    ingredients_input = st.text_input("Ingredients (comma-separated)", "eggs, milk, flour", key="ingredients_input")
    cuisine = st.selectbox("Cuisine", ["any", "Rwandan", "Chinese", "Indian", "Italian", "Mexican"])
    diet = st.selectbox("Diet", ["any", "vegan", "vegetarian", "meat"])
    max_words = st.slider("Max words", min_value=50, max_value=300, value=100)

    col1, col2 = st.columns([1, 1])
    with col1:
        generate = st.button("Generate Recipe")
    with col2:
        clear = st.button("Clear")

    if clear:
        # Clear the input field using session state so it works across Streamlit versions
        st.session_state["ingredients_input"] = ""
        return

    if generate:
        ingredients_text = st.session_state.get("ingredients_input", "")
        ingredients = [i.strip() for i in ingredients_text.split(",") if i.strip()]
        if not ingredients:
            st.error("Please provide at least one ingredient.")
            return
        with st.spinner("Generating recipe..."):
            try:
                recipe = generate_recipe(ingredients, cuisine, diet, max_words)
            except Exception as e:
                st.error(str(e))
                return
        st.subheader("Recipe")
        st.write(recipe)
        st.download_button("Download Recipe as .txt", recipe, file_name="recipe.txt")

    st.markdown("---")
    st.subheader("Notes")
    if genai is not None:
        st.write("Using Google GenAI client (from `google import genai`).")
    elif openai is not None:
        st.write("Using OpenAI API (from `openai`).")
    else:
        st.write("No LLM client found. Install `openai` or Google GenAI and set `OPENAI_API_KEY` or Google credentials.")


if __name__ == "__main__":
    main()
