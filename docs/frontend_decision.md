# HostelWise AI: Frontend Architecture Decision

This document reviews the frontend architecture of **HostelWise AI** and records the design decision between a Streamlit dashboard and a React/Vite web application.

---

## 🔍 Frontend Audit & Findings

*   **Current State**: The repository contains a single frontend application located in the `/frontend/` directory, built entirely using **Streamlit** with Plotly visualizations.
*   **Alternative Consideration**: A React/Vite single-page application (SPA) was considered for its custom layout flexibility and advanced client-side state management.
*   **Result**: We have designated **Streamlit** as the primary production frontend for the HostelWise AI system. No duplicate or legacy web frontends exist in the repository.

---

## ⚙️ Rationale for Streamlit

1.  **Python-Native Ecosystem**:
    *   HostelWise AI relies heavily on data science libraries (Pandas, NumPy, Scikit-Learn) and GPU-accelerated engines (NVIDIA RAPIDS cuDF). 
    *   Streamlit allows us to write the frontend entirely in Python, facilitating direct in-process fallbacks. If the FastAPI backend container goes offline, the Streamlit app can import the services and database models directly, maintaining 100% operational capability.
2.  **Rapid Visualization Prototyping**:
    *   Using Plotly inside Streamlit (`st.plotly_chart`) enables high-performance interactive charting with minimal boilerplate code, compared to setting up Tailwind, Chart.js, or Recharts in React.
3.  **Low Latency & Simplicity**:
    *   Streamlit's execution model naturally aligns with time-series forecasting and RAG-based chatbot sessions. The state is maintained on the server-side, reducing the overhead of managing complex Redux or Context API states in React.
4.  **Hackathon Pitch Velocity**:
    *   For a data analytics and cloud-native challenge, speed-to-insight and visual elegance are paramount. Streamlit's built-in components and layout widgets allow us to construct a premium dashboard in a fraction of the time required for a full JS build.

---

## 🛠️ Reorganization Decisions

*   **Primary Frontend**: `/frontend/app.py` (Streamlit Dashboard).
*   **Visualizations**: Isolated in `/frontend/charts/plotly_charts.py` to prevent code pollution in the main entry point.
*   **UI Components**: Isolated in `/frontend/components/ui_blocks.py` for card layouts and metrics.
*   **Legacy Components**: Any unused HTML templates or scratch scripts have been removed to keep the repository clean and professional.
