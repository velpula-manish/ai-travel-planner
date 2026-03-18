# 🌍 AI Travel Itinerary Planner

<div align="center">

![AI Travel Planner](https://img.shields.io/badge/AI-Travel%20Planner-764ba2?style=for-the-badge&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.38-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-LLaMA%203.1-orange?style=for-the-badge)
![Tavily](https://img.shields.io/badge/Tavily-Search-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

### 🚀 Live Demo
## 👉 [ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app](https://ai-travel-planner-h7f7ryewjbufa5tdvfewnu.streamlit.app)

*Your Personal AI Travel Agent — Powered by Groq + Tavily*

</div>

---

## 📸 Preview

| Light Mode | Dark Mode |
|---|---|
| ![Light](https://img.shields.io/badge/Theme-Light%20Mode-white?style=flat-square) | ![Dark](https://img.shields.io/badge/Theme-Dark%20Mode-black?style=flat-square) |

> Plan your perfect trip in seconds — AI searches the web in real-time and generates
> a complete day-by-day itinerary tailored to your budget, interests, and travel dates.

---

## ✨ Features

- 🤖 **AI-Powered Planning** — Uses Groq's LLaMA 3.1 to generate intelligent, personalized itineraries
- 🔍 **Real-Time Web Search** — Tavily searches the internet for the latest travel information
- 📅 **Day-by-Day Itinerary** — Detailed morning, afternoon and evening plans for every day
- 🏨 **Hotel Recommendations** — Budget-matched hotel suggestions with price ranges
- 🍽️ **Restaurant Picks** — Local food recommendations with must-try dishes
- 💰 **Multi-Currency Budget** — Supports INR ₹, USD $, EUR €, GBP £ with smart tier detection
- 💡 **Travel Tips** — Practical local tips, cultural etiquette and safety advice
- 🚗 **Transport Guide** — Local transport options with estimated costs
- 📥 **Download Itinerary** — Save your plan as a text file
- 🌗 **Dark/Light Mode** — Beautiful UI in any theme

---

## 🛠️ Tech Stack

| Technology | Purpose | Version |
|---|---|---|
| **Streamlit** | Web UI Framework | 1.38 |
| **Groq API** | LLM (LLaMA 3.1 8B) | Latest |
| **Tavily API** | Real-Time Web Search | 0.3.3 |
| **Python** | Backend Language | 3.10+ |

---

## 🏗️ Project Structure
```
ai-travel-planner/
│
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
└── README.md             # Project documentation
```

---

## ⚙️ How It Works
```
User Input
    ↓
Tavily searches the web for real-time travel info
    ↓
Groq LLaMA 3.1 processes + generates itinerary
    ↓
Streamlit displays beautiful formatted result
    ↓
User downloads or shares their plan
```

**Step-by-step flow:**
1. User enters destination, dates, budget and interests
2. Tavily API searches the web for current attractions, hotels and restaurants
3. Groq's LLaMA 3.1 model reads the search results and crafts a personalized itinerary
4. The result is displayed in a clean, structured format with all sections
5. User can download the itinerary as a text file

---

## 🚀 Run Locally

### Prerequisites
- Python 3.10+
- Groq API Key → [console.groq.com](https://console.groq.com)
- Tavily API Key → [tavily.com](https://tavily.com)

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/velpula-manish/ai-travel-planner.git
cd ai-travel-planner

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create secrets file
mkdir .streamlit
```

Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
TAVILY_API_KEY = "your_tavily_api_key_here"
```
```bash
# 4. Run the app
streamlit run app.py
```

Open 👉 `http://localhost:8501`

---

## ☁️ Deploy on Streamlit Cloud (FREE)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → Select your forked repo
4. Set **Main file path** to `app.py`
5. Click **"Advanced settings"** → Add secrets:
```toml
GROQ_API_KEY = "your_groq_api_key_here"
TAVILY_API_KEY = "your_tavily_api_key_here"
```
6. Click **"Deploy!"** — Live in 2-3 minutes! 🎉

---

## 🔑 Get Free API Keys

| Service | Link | Free Tier |
|---|---|---|
| **Groq** | [console.groq.com](https://console.groq.com) | ✅ Free — Fast LLaMA models |
| **Tavily** | [tavily.com](https://tavily.com) | ✅ Free — 1000 searches/month |

---

## 💡 Usage Guide
```
1. Open the app at the live link above
2. Enter your DESTINATION (e.g. "Arunachalam, India")
3. Set TRIP DURATION using the slider (1-14 days)
4. Choose your CURRENCY (₹ INR / $ USD / € EUR / £ GBP)
5. Type your BUDGET AMOUNT
6. Enter TRAVEL DATES
7. Set NUMBER OF TRAVELERS
8. Pick your INTERESTS (Food, History, Adventure etc.)
9. Add any SPECIAL REQUIREMENTS (optional)
10. Click 🚀 GENERATE MY TRAVEL ITINERARY!
11. Wait 30-60 seconds for AI to search & plan
12. Download your itinerary as a text file!
```

---

## 📊 Sample Output
```
🌍 DESTINATION OVERVIEW
Arunachalam is a sacred pilgrimage town in Tamil Nadu...

📅 DAY-BY-DAY ITINERARY
DAY 1 - ARRIVAL & SACRED EXPLORATION
- MORNING: Visit the Arunachaleswarar Temple...
- AFTERNOON: Girivalam Path walk around Arunachala Hill...
- EVENING: Dinner at Hotel Mayura...

🏨 HOTEL RECOMMENDATIONS
1. Hotel Arunachala — ₹2,500/night (~$35 USD)
2. Hotel Mayura — ₹3,500/night (~$49 USD)

💰 BUDGET BREAKDOWN
- Total Estimate: ₹22,825 (~$322 USD) for 2 travelers
```

---

## 🤝 Contributing

Contributions are welcome! Here's how:
```bash
# 1. Fork the repo
# 2. Create your feature branch
git checkout -b feature/AmazingFeature

# 3. Commit your changes
git commit -m 'Add AmazingFeature'

# 4. Push to the branch
git push origin feature/AmazingFeature

# 5. Open a Pull Request
```

---

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 👨‍💻 Author

**Velpula Manish**

[![GitHub](https://img.shields.io/badge/GitHub-velpula--manish-181717?style=flat-square&logo=github)](https://github.com/velpula-manish)

---

## 🙏 Acknowledgements

- [Groq](https://groq.com) — For blazing fast LLaMA inference
- [Tavily](https://tavily.com) — For real-time web search API
- [Streamlit](https://streamlit.io) — For the beautiful UI framework
- [LangChain](https://langchain.com) — For AI agent orchestration concepts

---

<div align="center">

**⭐ If you found this helpful, please star the repository! ⭐**

Built with ❤️ using Groq AI + Tavily + Streamlit

</div>
