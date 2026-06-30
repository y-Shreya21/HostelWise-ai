# HostelWise AI: Hackathon Pitch Deck Outline

This outline provides a slide-by-slide structure for pitching **HostelWise AI** to the Google Cloud + NVIDIA Data Analytics Challenge judging panel.

---

## 🎬 Slide 1: Title Slide
*   **Visual**: Sleek dark background with the logo: **💸 HostelWise AI**.
*   **Headline**: Smart Expense Intelligence System for Students.
*   **Subtitle**: Empowering student budgeting with Google Cloud, NVIDIA RAPIDS, and Gemini AI.
*   **Presenter Info**: [Your Name/Team Name].

---

## 🚨 Slide 2: The Problem
*   **Visual**: Graphics showing student financial anxiety, a chaotic spreadsheet, or overlapping budget alerts.
*   **Talking Points**:
    *   Hostel and PG students struggle with allowance management.
    *   High volume of micro-transactions ( UPI snacks, travel, recharges) leads to "leaky wallets".
    *   Existing tools are static, manual, and backward-looking. They don't answer: *"Will I make it to the end of the month?"*

---

## 💡 Slide 3: The Solution (HostelWise AI)
*   **Visual**: Mockup of the dashboard showing the Overview tab and the Gemini Advisor.
*   **Talking Points**:
    *   An end-to-end predictive budgeting system designed specifically for students.
    *   **Proactive Forecasting**: Tells you where you are heading, not just where you went.
    *   **Interactive AI Coaching**: A conversational assistant that knows your financial state and guides your decisions.

---

## 🏗️ Slide 4: System Architecture
*   **Visual**: Block diagram showing Streamlit -> FastAPI -> cuDF/Ridge Engine -> BigQuery/GCS/SQLite.
*   **Talking Points**:
    *   Decoupled, modular services.
    *   **Offline-first capability**: Seamless local fallback to SQLite if cloud connectivity is disabled.
    *   Microservice-ready, deployable via Docker and GKE.

---

## ☁️ Slide 5: Google Cloud Integration
*   **Visual**: Cloud Storage and BigQuery icons.
*   **Talking Points**:
    *   **Google Cloud Storage**: Raw CSV uploads are archived securely as blobs.
    *   **Google BigQuery**: Act as our analytical data warehouse, storing transaction histories and budgets.
    *   **Analytical Views**: Optimized SQL views (`view_monthly_summary`, etc.) aggregate data at scale, ready for Looker Studio dashboards.

---

## ⚡ Slide 6: NVIDIA RAPIDS Acceleration
*   **Visual**: Bar chart showing CPU (Pandas) vs. GPU (cuDF) execution times (100K, 500K, 1M rows).
*   **Talking Points**:
    *   ETL data cleaning and aggregations are offloaded to GPU cores using **NVIDIA cuDF**.
    *   Delivers a **34.7x speedup** on 1,000,000 transaction rows.
    *   Enables real-time, zero-latency dashboard refreshes even under massive data volumes.

---

## 🔮 Slide 7: Forecasting & Risk Models
*   **Visual**: Graph of cumulative spending projection vs. budget limit line.
*   **Talking Points**:
    *   **Time-Series Forecasting**: Ridge Regression model trained on cyclical sine/cosine day-of-week and day-of-month features.
    *   **Multi-Factor Risk Score (0-100)**: Aggregates budget utilization, spending velocity, category-specific spikes, and polynomial run-rate projections.

---

## 🤖 Slide 8: Gemini AI Financial Advisor
*   **Visual**: Chat bubble interface showing the RAG context block and Gemini's response.
*   **Talking Points**:
    *   Uses **Gemini 1.5 Flash** to provide personalized, context-aware financial coaching.
    *   Ingests the student's real-time telemetry (KPIs, forecasts, risk score, active savings recommendations).
    *   Answers complex inquiries: *"Can I afford a ₹1500 purchase this month?"*

---

## 📈 Slide 9: Impact & Scalability
*   **Visual**: Key impact metrics (e.g., Average Savings: 15-20% per student, Zero Budget Overruns).
*   **Talking Points**:
    *   Real-world utility: Solves a genuine bottleneck in student life.
    *   Scalable: Can be easily white-labeled for universities or student housing providers.
    *   Cost-effective: Thin client, serverless backend, and local caching.

---

## 🏁 Slide 10: Conclusion & Future Scope
*   **Visual**: Summary points and team photo/thank you.
*   **Talking Points**:
    *   HostelWise AI demonstrates a complete integration of GCP, NVIDIA RAPIDS, and Gemini.
    *   **Future Scope**: Automatic SMS/WhatsApp transaction scraping, group expense sharing (hostel room splits), and automated savings transfers.
    *   Thank you! Open for questions.
