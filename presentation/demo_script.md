# HostelWise AI: Video Demo Script

This script provides a step-by-step narration and action guide for recording the **HostelWise AI** hackathon demo video (Target: 3-5 minutes).

---

## 🎬 Act 1: Introduction & Problem (0:00 - 0:45)
*   **On-Screen Action**: Show the **Overview** tab of the Streamlit dashboard (`http://localhost:8501`). Hover over the KPI cards.
*   **Narration**:
    > "Hello, judges! Today we are excited to present **HostelWise AI**—the Smart Expense Intelligence System built specifically for college students living in hostels and PG accommodations. 
    > As a student, managing a monthly allowance is stressful. With dozens of small daily transactions across UPI, cash, and cards, it is incredibly easy to lose track of where your money is going, leading to budget overruns and financial anxiety. 
    > HostelWise AI solves this by combining cloud-native data warehousing, GPU-accelerated ETL, machine learning forecasting, and conversational AI to give students complete control over their financial health."

---

## 📈 Act 2: Ingestion & Analytics (0:45 - 1:30)
*   **On-Screen Action**: Click **Browse Files** in the sidebar. Select a sample CSV log. Click **Process Upload**. Watch the dashboard refresh with the new data.
*   **Narration**:
    > "Let’s start with data ingestion. A student can upload their transaction logs directly as a CSV. When a file is uploaded, our backend immediately archives the raw file in **Google Cloud Storage** and runs a GPU-accelerated ETL cleaning pipeline using **NVIDIA RAPIDS cuDF** to filter duplicates, standardize dates, and normalize categories.
    > In our **Expense Analytics** tab, the cleaned data is aggregated at scale. Students get interactive Plotly visualizations showing category breakdowns, payment distributions, and weekly spending velocity, helping them instantly identify their largest spending categories."

---

## 🔮 Act 3: ML Forecasting & Risk Scoring (1:30 - 2:30)
*   **On-Screen Action**: Click the **ML Spending Forecast** tab. Highlight the **Predicted Total Spend** card and the **Cumulative Spending Projection** chart. Then, click the **Risk & Recommendations** tab.
*   **Narration**:
    > "But we don’t just look backward. HostelWise AI uses machine learning to project where the student is heading. Under the **ML Spending Forecast** tab, we train a Ridge Regression model on cyclical temporal features to forecast spending for the next 30 days. 
    > Simultaneously, we fit a polynomial curve to the current month's cumulative daily spending to project the final month-end total.
    > This projection feeds into our **Multi-Factor Risk Scoring Engine**. Combining budget utilization, spending velocity, category spikes, and run-rate projections, we calculate a dynamic risk score from 0 to 100. If the risk is high, the system alerts the student and displays actionable savings recommendations, like substituting ride-hailing with public transit."

---

## 🤖 Act 4: Gemini AI Advisor (2:30 - 3:30)
*   **On-Screen Action**: Click the **Gemini AI Advisor** tab. Click the quick inquiry chip: *"Can I afford a ₹1500 purchase?"*. Watch the chat bubble populate with a detailed, numbers-backed response.
*   **Narration**:
    > "To make these insights truly accessible, we integrated the **Gemini AI Advisor**. Instead of analyzing complex charts, the student can simply ask questions in plain English. 
    > When a query is made, our backend builds a RAG context block containing the student's real-time financial telemetry (KPIs, forecasts, risk score, and recommendations) and injects it into Gemini 1.5 Flash. 
    > As you can see, when we ask *'Can I afford a ₹1500 purchase?'*, Gemini doesn't just say yes or no—it evaluates the remaining headroom, calculates the new projected risk score, and warns us of the potential budget impact. It's like having a personal financial coach in your pocket."

---

## ⚡ Act 5: NVIDIA RAPIDS Performance & Conclusion (3:30 - End)
*   **On-Screen Action**: Click the **RAPIDS Performance** tab. Show the bar chart displaying the **34x+ speedup**.
*   **Narration**:
    > "Finally, let's look at performance. When dealing with large-scale transaction histories across thousands of students, traditional CPU-bound Pandas struggles. 
    > By leveraging **NVIDIA RAPIDS cuDF**, we offload date parsing and group-by aggregations directly to GPU cores. Our benchmarks show a massive **34.7x speedup** on 1,000,000 transaction rows compared to CPU Pandas, reducing processing time from over 3 seconds to just 97 milliseconds.
    > HostelWise AI demonstrates how Google Cloud, NVIDIA RAPIDS, and Gemini can be combined to solve a real-world problem, delivering a scalable, serverless, and highly responsive decision-support application. Thank you!"
