# HostelWise AI: Deployment Guide

This guide provides instructions for deploying **HostelWise AI** in both local containerized environments and production Google Cloud services (Cloud Run & Google Kubernetes Engine).

---

## 🐳 1. Local Containerized Deployment (Docker Compose)

The easiest way to run the entire stack locally in an isolated environment is using **Docker Compose**.

### Prerequisite
Ensure you have **Docker** and **Docker Compose** installed.

### Steps
1.  **Configure Environment**:
    Create a `.env` file in the root directory (based on `.env.example`).
2.  **Build and Start Containers**:
    ```bash
    docker-compose up --build
    ```
    This command builds the multi-stage Dockerfiles and starts:
    *   **FastAPI Backend**: Exposed at `http://localhost:8000`
    *   **Streamlit Frontend**: Exposed at `http://localhost:8501`
3.  **Stop Containers**:
    ```bash
    docker-compose down
    ```

---

## 🚀 2. Deploying to Google Cloud Run (Serverless)

For production deployment, the FastAPI backend can be hosted on **Google Cloud Run**, which provides serverless scaling and automatic HTTPS.

### Steps
1.  **Build and Push Backend Image to Artifact Registry**:
    ```bash
    # Create an Artifact Registry repository
    gcloud artifacts repositories create hostelwise-repo --repository-format=docker --location=us-central1
    
    # Configure Docker authentication
    gcloud auth configure-docker us-central1-docker.pkg.dev
    
    # Build and tag the backend image
    docker build -t us-central1-docker.pkg.dev/YOUR_PROJECT_ID/hostelwise-repo/backend:latest -f Dockerfile .
    
    # Push the image
    docker push us-central1-docker.pkg.dev/YOUR_PROJECT_ID/hostelwise-repo/backend:latest
    ```
2.  **Deploy the Container to Cloud Run**:
    ```bash
    gcloud run deploy hostelwise-backend \
      --image=us-central1-docker.pkg.dev/YOUR_PROJECT_ID/hostelwise-repo/backend:latest \
      --platform=managed \
      --region=us-central1 \
      --allow-unauthenticated \
      --set-env-vars="GEMINI_API_KEY=your_key,GCP_PROJECT=YOUR_PROJECT_ID,BIGQUERY_DATASET=hostelwise_ai_dataset,GCS_BUCKET_NAME=hostelwise-raw-expenses"
    ```
3.  **Update Frontend Backend URL**:
    Once deployed, Cloud Run will provide an HTTPS URL (e.g., `https://hostelwise-backend-xxxxx.run.app`). Set this as the `BACKEND_URL` in your frontend configuration.

---

## ☸️ 3. Deploying to Google Kubernetes Engine (GKE)

For orchestrating microservices at scale, the project can be deployed on a GKE cluster.

### A. GKE Cluster Creation
```bash
gcloud container clusters create hostelwise-cluster \
  --num-nodes=3 \
  --zone=us-central1-a \
  --machine-type=e2-medium
```

### B. Kubernetes Manifests
Create a file named `gke-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hostelwise-backend-deployment
spec:
  replicas: 2
  selector:
    matchLabels:
      app: hostelwise-backend
  template:
    metadata:
      labels:
        app: hostelwise-backend
    spec:
      containers:
      - name: backend
        image: us-central1-docker.pkg.dev/YOUR_PROJECT_ID/hostelwise-repo/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: GEMINI_API_KEY
          value: "your_gemini_key"
        - name: GCP_PROJECT
          value: "YOUR_PROJECT_ID"
---
apiVersion: v1
kind: Service
metadata:
  name: hostelwise-backend-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: hostelwise-backend
```

### C. Deploy to GKE
```bash
# Get cluster credentials
gcloud container clusters get-credentials hostelwise-cluster --zone=us-central1-a

# Deploy manifests
kubectl apply -f gke-deployment.yaml

# Monitor deployment and obtain external IP
kubectl get services hostelwise-backend-service
```
