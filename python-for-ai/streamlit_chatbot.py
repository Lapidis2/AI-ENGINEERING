import os
from dotenv import load_dotenv
from pathlib import Path
import streamlit as st

# Load .env from calling_llm if present
base_dir = Path(__file__).parent
calling_env = base_dir / "calling_llm" / ".env"
if calling_env.exists():
    load_dotenv(dotenv_path=str(calling_env))
else:
    load_dotenv()

genai = None
client = None
try:
    from google import genai as _genai
    genai = _genai
    # Initialize client with key if available
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
except Exception:
    genai = None


def send_to_genai(conversation):
    """Send conversation (list of dicts) to GenAI and return reply text."""
    if client is None:
        raise RuntimeError("Google GenAI client not available. Check calling_llm/.env for GOOGLE_API_KEY")
    # Prefer chat.send_message when available
    try:
        chat = getattr(client, "chat", None)
        if chat is not None and hasattr(chat, "send_message"):
            # Convert conversation to a single string input or messages if supported
            # Here we join user/model parts into a single input for simplicity
            joined = []
            for turn in conversation:
                role = turn.get("role")
                texts = [p.get("text", "") for p in turn.get("parts", [])]
                joined.append(f"{role}: {' '.join(texts)}")
            prompt = "\n".join(joined) + "\nmodel:"
            resp = chat.send_message(model="gemini-3.6-flash", input=prompt)
            return getattr(resp, "text", getattr(resp, "content", str(resp)))
    except Exception:
        pass
    # Fallback to models.generate_content with the conversation structure
    response = client.models.generate_content(model="gemini-3.6-flash", contents=conversation)
    return getattr(response, "text", str(response))


def main():
    st.set_page_config(page_title="Chatbot with Memory", layout="centered")
    st.title("Chatbot with Memory")

    if "conversation" not in st.session_state:
        # Initialize with a greeting like the notebook
        st.session_state.conversation = [
            {"role": "user", "parts": [{"text": "Hi my name is peter"}]}]
        # Optionally get an initial reply
        try:
            reply = send_to_genai(st.session_state.conversation)
        except Exception:
            reply = "(no reply — check GOOGLE_API_KEY)"
        st.session_state.conversation.append({"role": "model", "parts": [{"text": reply}]})

    # Display conversation
    for turn in st.session_state.conversation:
        role = turn.get("role")
        text = "\n".join([p.get("text", "") for p in turn.get("parts", [])])
        if role == "user":
            st.info(f"You: {text}")
        else:
            st.success(f"Bot: {text}")

    # Define callback to handle sending so we can safely update session_state
    def _send_callback():
        user_input_val = st.session_state.get("user_msg", "").strip()
        if not user_input_val:
            st.session_state["send_error"] = "Please enter a message."
            return
        # clear any previous send error
        st.session_state.pop("send_error", None)
        st.session_state.conversation.append({"role": "user", "parts": [{"text": user_input_val}]})
        try:
            reply = send_to_genai(st.session_state.conversation)
        except Exception as e:
            st.session_state["send_error"] = f"Error: {e}"
            return
        st.session_state.conversation.append({"role": "model", "parts": [{"text": reply}]})
        # clear the input
        st.session_state["user_msg"] = ""

    # Input widget and button using callback
    st.text_input("Your message", key="user_msg")
    st.button("Send", on_click=_send_callback)

    # If the callback stored an error, show it
    if st.session_state.get("send_error"):
        st.error(st.session_state.get("send_error"))


if __name__ == "__main__":
    main()
