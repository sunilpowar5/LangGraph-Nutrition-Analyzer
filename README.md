# Food Calories & Proteins Analyzer

An AI-powered web application that analyzes food images to **detect food items, calculate calories & protein content, and answer nutrition-related questions**.  
Built with **LangGraph**, **Google Gemini**, **Nutritionix API**, and **Streamlit**.

---

##  Features

-  **Food Recognition** – Upload an image, and Gemini identifies visible food items.  
-  **Calorie & Protein Calculation** – Nutritionix API provides accurate nutrition facts.  
-  **Interactive Q&A** – Ask follow-up questions about the analysis (e.g., “How much protein is in the rice?”).  
-  **Wikipedia Integration** – Learn nutrition benefits of foods via Wikipedia.  
-  **Conversation Memory** – Keeps track of analysis and follow-up questions using `MemorySaver`.  
-  **Streamlit UI** – Simple, user-friendly interface.  

---

##  Tech Stack

- **[LangGraph](https://github.com/langchain-ai/langgraph)** – Workflow orchestration & memory.  
- **[Google Gemini](https://ai.google/)** – Vision + LLM for food recognition & reasoning.  
- **[Nutritionix API](https://developer.nutritionix.com/)** – Nutrition facts (calories, protein, etc.).  
- **[Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page)** – Extra nutrition knowledge.  
- **[Streamlit](https://streamlit.io/)** – Frontend for interaction.  

---

##  Project Structure

```
.
├── project/
│   ├── app.py           # Streamlit app (UI + session handling)
│   ├── graph.py         # LangGraph workflow (food detection, calories, chatbot)
│
├── .env.example         # Environment variables 
├── .gitignore           # Git ignore rules
├── .python-version      # Python version specification
├── pyproject.toml       # Project configuration and dependencies
├── README.md            # Project documentation
├── requirements.txt     # Python dependencies list
├── uv.lock              # Lockfile (for reproducible builds with uv)

```

---

##  Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/sunilpowar5/LangGraph-Nutrition-Analyzer.git
cd LangGraph-Nutrition-Analyzer
```

### 2️⃣ Create virtual environment & install dependencies
```bash
python -m venv .venv
source .venv/bin/activate   # Mac/Linux
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 3️⃣ Add environment variables
Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_google_gemini_api_key
NUTRITIONIX_APP_ID=your_nutritionix_app_id
NUTRITIONIX_API_KEY=your_nutritionix_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=LangGraph-Nutrition-Analyzer
```

### 4️⃣ Run the app
```bash
streamlit run app.py
```

---

##  Usage

1. Upload a **food image** (jpeg/jpg/png).  
2. The system **detects food items** and retrieves **calories & protein** info.  
3. Ask **follow-up questions** (e.g., “Is this meal healthy?” or “What’s the use of this meal?”).  
4. Start a **new session** anytime.  

---

##  Example Workflow

1. Upload image → 🍌 + 🥛 identified.  
2. Nutritionix fetch →  
   - Banana: 105 calories, 1.3g protein  
   - Milk: 103 calories, 8g protein  
   - **Total: 208 calories, 9.3g protein**  
3. Ask: “What are the benefits of milk?” → Answer fetched from Wikipedia.  

---

##  Roadmap

- [ ] Support multi-food image segmentation (bounding boxes).  
- [ ] Add more nutrition APIs for wider coverage.  
- [ ] Deploy on Streamlit Cloud / AWS.  
- [ ] Multi-user history & persistent storage.  

---

## Contributing

Contributions, issues, and feature requests are welcome!  
Feel free to open a PR or report a bug.  