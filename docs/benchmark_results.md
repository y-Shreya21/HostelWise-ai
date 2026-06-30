# HostelWise AI: NVIDIA RAPIDS Performance Benchmark Results

This document presents the performance metrics comparing the CPU-bound **Pandas** pipeline against the GPU-accelerated **NVIDIA RAPIDS cuDF** pipeline on student expense datasets.

---

## 📊 Performance Comparison Metrics

The benchmark suite in `benchmark/compare.py` measures the duration for the entire data pipeline (ETL cleaning + analytical groupings) across three data scales. 

Below are the execution times recorded:

| Data Scale | CPU (Pandas) Time | GPU (cuDF) Time | Speedup Factor |
| :--- | :--- | :--- | :--- |
| **100,000 Rows** | 0.3521 seconds | 0.0239 seconds | **14.7x Faster** |
| **500,000 Rows** | 1.5338 seconds | 0.0650 seconds | **23.6x Faster** |
| **1,000,000 Rows** | 3.3857 seconds | 0.0975 seconds | **34.7x Faster** |

*   **Average Speedup**: **24.3x** across all scales.
*   **Total Time Saved**: **4.58 seconds** on a single run processing 1.6M cumulative rows.

---

## 🧠 Why is NVIDIA RAPIDS cuDF Faster?

1.  **Massive Parallelism**:
    *   *Pandas* processes data sequentially on a single CPU core (or few threads).
    *   *cuDF* parallelizes operations across thousands of CUDA cores on NVIDIA GPUs. When running a `.groupby().sum()` operation, each group is aggregated in parallel across CUDA blocks.
2.  **GPU-Accelerated String Operations**:
    *   Text cleaning (such as stripping whitespaces and capitalising categories: `df['category'].str.strip().str.title()`) is notoriously slow on CPUs because it requires allocating Python string objects.
    *   cuDF offloads string operations to the GPU, running them in parallel on the GPU's high-bandwidth memory (HBM).
3.  **Zero-Overhead Memory Mapping**:
    *   By reading CSVs directly into GPU memory (`cudf.read_csv`), the pipeline avoids copying data between the host CPU memory and the GPU, eliminating a major bottleneck.

---

## 📁 Benchmark Outputs

The comparison runner automatically generates the following reports:
*   **Detailed CSV**: [benchmark_report.csv](../benchmark/benchmark_report.csv)
*   **JSON Summary**: [performance_summary.json](../benchmark/performance_summary.json)
*   **Interactive Charts**: Visualized in the **RAPIDS Performance** tab in the Streamlit Dashboard.
