# IBS Wellness Tracker 🧘

A production-grade Python/Streamlit application for tracking and managing IBS symptoms.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Open .env and add your OPENAI_API_KEY
   ```

3. **Run Application**
   ```bash
   streamlit run app.py
   ```

## 🏗️ Project Structure

- **`app.py`**: Main application interface and routing.
- **`config.py`**: Configuration settings and constants.
- **`data_manager.py`**: Handles data persistence (JSON).
- **`ai_analysis.py`**: Integration with OpenAI for insights.
- **`visualizations.py`**: Chart generation using Matplotlib.
- **`utils.py`**: Helper functions.
- **`data/`**: Stores user data (`ibs_data.json`).
- **`logs/`**: Application logs.

## 📚 Documentation

For a comprehensive guide on the architecture, usage, and development of this project, please refer to the [PROJECT_HANDOFF_PROMPT.md](PROJECT_HANDOFF_PROMPT.md) file included in this repository.

## 🌟 Features

- **Daily Logging**: Track symptoms, sleep, diet, stress, and more.
- **Analytics**: Visualize trends with interactive charts.
- **AI Insights**: Get personalized daily and weekly analysis powered by GPT-4.
- **Data Export**: Download your data as CSV or JSON.

## License

[Add License Here]
