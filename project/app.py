import streamlit as st
from PIL import Image
import uuid
from graph import calorie_graph  

st.set_page_config(page_title="Food Calories & Proteins Analyzer", layout="wide")
st.title("Food Calories and Proteins Analyzer")

# Initialize session state
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "mime" not in st.session_state:
    st.session_state.mime = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Add result to the history eg:user and text
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False
if "nutrition_result" not in st.session_state:
    st.session_state.nutrition_result = None

# Upload image
uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    uploaded_file.seek(0)
    new_image_bytes = uploaded_file.read()

    # Analyze image Only if it's a new image
    if st.session_state.image_bytes != new_image_bytes:
        st.session_state.uploaded_image = Image.open(uploaded_file)
        st.session_state.image_bytes = new_image_bytes
        st.session_state.mime = uploaded_file.type
        st.session_state.analysis_done = False
        st.session_state.chat_history = []

        # Invoking the graph
        with st.spinner("Analyzing..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result_state = calorie_graph.invoke(
                {"image_bytes": st.session_state.image_bytes, "mime": st.session_state.mime},
                config=config
            )

        initial_result = result_state.get("result", "No result.")

        # Save the results in session state
        st.session_state.analysis_done = True
        st.session_state.nutrition_result = initial_result
        st.session_state.chat_history.append(("system", "Nutrition Analysis"))
        st.session_state.chat_history.append(("assistant", initial_result))

# Show uploaded image
if st.session_state.uploaded_image is not None:
    st.image(st.session_state.uploaded_image, caption="Uploaded Food Image", width="content")

# Show chat history
if st.session_state.chat_history:
    for role, msg in st.session_state.chat_history:
        if role == "user":
            st.markdown(f"**Q: {msg}**")
        elif role == "assistant":
            st.write(msg)
        elif role == "system":
            st.markdown(f"### {msg}")

# Follow-up questions
if st.session_state.analysis_done:
    user_question = st.text_input("Ask a follow-up questions ")

    if st.button("Get Response") and user_question:
        st.session_state.chat_history.append(("user", user_question))

        with st.spinner("Thinking..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            followup_result = calorie_graph.invoke(
                {
                    "user_query": user_question,
                    "previous_result": st.session_state.nutrition_result  
                },
                config=config
            )

        # Get response
        followup_text = followup_result.get("user_result") or "No response."

        st.session_state.chat_history.append(("assistant", followup_text))
        st.rerun()

# Reset session
if st.button("Start New Session"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.uploaded_image = None
    st.session_state.image_bytes = None
    st.session_state.mime = None
    st.session_state.chat_history = []
    st.session_state.analysis_done = False
    st.session_state.nutrition_result = None
    st.success("New session started")