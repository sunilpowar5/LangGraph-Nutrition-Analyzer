import streamlit as st
from PIL import Image
import uuid
from graph import calorie_graph  # replace with your actual module

st.set_page_config(page_title="Food Calories & Proteins Analyzer", layout="wide")
st.title("🥗 Food Calories and Proteins Analyzer")

# --- Step 0: Initialize session state ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "mime" not in st.session_state:
    st.session_state.mime = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # stores all results for display

# --- Step 1: Upload image & initial analysis ---
uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    uploaded_file.seek(0)
    new_image_bytes = uploaded_file.read()

    # If first upload or new image
    if st.session_state.image_bytes != new_image_bytes:
        st.session_state.uploaded_image = Image.open(uploaded_file)
        st.session_state.image_bytes = new_image_bytes
        st.session_state.mime = uploaded_file.type
        st.session_state.analysis_done = False
        st.session_state.last_result = None
        st.session_state.chat_history = []

        # Display image
        st.image(st.session_state.uploaded_image, caption="Uploaded Food Image", use_column_width=True)

        # Analyze image
        with st.spinner("Analyzing..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result_state = calorie_graph.invoke(
                {"image_bytes": st.session_state.image_bytes, "mime": st.session_state.mime},
                config=config
            )

        initial_result = result_state.get("result", "No result.")
        st.subheader("Nutrition Analysis")
        st.write(initial_result)

        # Save in session state
        st.session_state.analysis_done = True
        st.session_state.last_result = initial_result
        st.session_state.chat_history.append(("Nutrition Analysis", initial_result))

# Show uploaded image if already uploaded
elif st.session_state.uploaded_image is not None:
    st.image(st.session_state.uploaded_image, caption="Uploaded Food Image", use_column_width=True)

# --- Step 2: Follow-up questions ---
if st.session_state.analysis_done:
    user_question = st.text_input("Ask a follow-up question (e.g., 'You missed an item')")

    if st.button("Get Response") and user_question:
        with st.spinner("Thinking..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            followup_result = calorie_graph.invoke(
                {
                    "user_query": user_question,
                    "result": st.session_state.last_result
                },
                config=config
            )

        followup_text = followup_result.get("user_result", "No response.")

        # Append to chat history
        st.session_state.chat_history.append((f"Q: {user_question}", followup_text))
        st.session_state.last_result = followup_text

# --- Step 3: Display chat history ---
for idx, (header, message) in enumerate(st.session_state.chat_history):
    st.subheader(header)
    st.write(message)

# --- Step 4: Reset session ---
if st.button("Start New Session"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.uploaded_image = None
    st.session_state.image_bytes = None
    st.session_state.mime = None
    st.session_state.last_result = None
    st.session_state.analysis_done = False
    st.session_state.chat_history = []
    st.success("New session started ✅")
