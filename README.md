# NLP Political Scraper

This project is an NLP-based scraper that extracts political news articles and their associated comments from major news aggregators. It utilizes semantic analysis to determine the political leaning of both the articles and comments. This information was used to predict the outcome of the 2024 U.S. Presidential Election.

---

## 🚀 Features

- **Political News Scraping**: Scrapes political news articles and comments from popular news aggregators.
- **Semantic Analysis**: Analyzes the text of both articles and comments to determine their political leaning (liberal, conservative, neutral).
- **Real-time Updates**: Runs on a schedule, continuously fetching and analyzing new articles and comments.
- **Election Prediction**: Based on the political sentiment of articles and comments, helps predict the outcome of the 2024 U.S. Presidential Election.
- **Automated Pipeline**: Built using CRON jobs to automate scraping and analysis, ensuring up-to-date data for predictions.

---

## 🛠️ Technologies Used

- **Python**: Used for scraping, data processing, and implementing NLP models.
- **Playwright**: Automates the scraping of dynamic content from websites, simulating real user interactions.
- **JavaScript**: Used within Playwright to handle dynamic web pages and scrape real-time data.
- **Linux**: The application runs on a Linux server environment to ensure high efficiency and stability.
- **Docker**: Used to containerize the application for easier deployment and scalability.
- **CRON Jobs**: Scheduled tasks to run the scraper periodically, ensuring that data is collected and analyzed at regular intervals.
- **NLP (Natural Language Processing)**: For semantic analysis and sentiment detection of articles and comments, helping determine political leaning.

---

## 📊 Outcome and Predictions

The scraper collected and analyzed political articles and user comments from various sources to track trends and sentiment shifts. By applying semantic analysis to both articles and user comments, we were able to categorize them as liberal, conservative, or neutral. This data was then aggregated and used to predict the likely outcome of the 2024 U.S. Presidential Election based on public sentiment.

The analysis found that:
- **Conservative Leaning**: Predominantly articles from right-leaning news outlets and conservative comments.
- **Liberal Leaning**: Majority of content from left-leaning outlets and liberal comments.
- **Swing States**: States with a more evenly distributed political sentiment, potentially influencing key battleground states in the election.

---

## 💻 How it Works

1. **Scraping**:
    - The scraper uses Playwright, a JavaScript-based automation tool, to visit major political news aggregators.
    - It collects both the main article and user comments under each article.

2. **Text Preprocessing**:
    - The content of each article and comment is processed to remove noise such as HTML tags, special characters, and irrelevant words.
    
3. **Semantic Analysis**:
    - Using NLP techniques, each article and comment is analyzed for political sentiment and classified into categories like liberal, conservative, or neutral.
    - Sentiment analysis models are trained on a large corpus of labeled political data.

4. **Prediction Model**:
    - The overall sentiment of articles and comments is aggregated to predict the election outcome.
    - Data from various news outlets and user comments are continuously scraped and analyzed to track shifts in political sentiment over time.

5. **Cron Jobs**:
    - The scraping and analysis are automated using CRON jobs, ensuring the data is up-to-date and refreshed regularly.

---

## 🛠️ Installation and Setup

To run the NLP Political Scraper, follow these steps:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/xelathan/nlp_political_scraper.git
    ```

2. **Navigate to the project directory**:
    ```bash
    cd nlp-political-scraper
    ```

3. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

4. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5. **Run Docker**:
    If you want to run the scraper in a Docker container, use the following commands:
    ```bash
    docker build -t nlp-political-scraper .
    docker run -d nlp-political-scraper
    ```

6. **Set up CRON Jobs**:
    - Use CRON to schedule the scraper to run at regular intervals (e.g., every hour).
    - Example CRON job setup:
    ```bash
    0 * * * * /usr/bin/python3 /path/to/scraper.py
    ```

---
