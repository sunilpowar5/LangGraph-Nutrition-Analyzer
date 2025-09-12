import streamlit as st
from PIL import Image
import uuid
from graph import calorie_graph

st.title("🥗 Food Calories and Proteins Analyzer")

# --- Step 0: Ensure a unique thread_id per user session ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# --- Track if initial analysis is done ---
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

# --- Keep uploaded image and bytes in session ---
if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None
if "image_bytes" not in st.session_state:
    st.session_state.image_bytes = None
if "mime" not in st.session_state:
    st.session_state.mime = None

# --- Step 1: Upload image & analysis ---
uploaded_file = st.file_uploader("Upload a food image", type=["jpg", "jpeg", "png"])

# Only process new upload
if uploaded_file is not None and st.session_state.uploaded_image is None:
    image = Image.open(uploaded_file)
    st.session_state.uploaded_image = image
    st.image(image, caption="Uploaded Food Image", width="content")
    
    # Convert image to bytes and store
    uploaded_file.seek(0)
    st.session_state.image_bytes = uploaded_file.read()
    st.session_state.mime = uploaded_file.type

    with st.spinner("Analyzing..."):
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        result_state = calorie_graph.invoke(
            {"image_bytes": st.session_state.image_bytes, "mime": st.session_state.mime},
            config=config
        )
    
    st.subheader("Nutrition Analysis")
    st.write(result_state.get("result", "No result."))

    # Mark analysis as done and save last result
    st.session_state.analysis_done = True
    st.session_state.last_result = result_state.get("result")

# Show uploaded image if already uploaded (prevents disappearance)
elif st.session_state.uploaded_image is not None:
    st.image(st.session_state.uploaded_image, caption="Uploaded Food Image", width="content")

# --- Step 2: Follow-up questions (only after analysis) ---
if st.session_state.analysis_done:
    user_question = st.text_input("Ask a follow-up question (e.g., 'You missed an item')")

    if st.button("Get Response") and user_question:
        with st.spinner("Thinking..."):
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            result_state = calorie_graph.invoke(
                {
                    "user_query": user_question,
                    "result": st.session_state.last_result  # Use previous analysis
                },
                config=config
            )

        st.subheader("Updated Analysis")
        st.write(result_state.get("user_result", "No response."))

        # Update last result for next follow-up
        st.session_state.last_result = result_state.get("user_result")

# --- Reset option ---
if st.button("Start New Session"):
    st.session_state.thread_id = str(uuid.uuid4())
    st.session_state.analysis_done = False
    st.session_state.last_result = None
    st.session_state.uploaded_image = None
    st.session_state.image_bytes = None
    st.session_state.mime = None
    st.success("New session started ✅")
