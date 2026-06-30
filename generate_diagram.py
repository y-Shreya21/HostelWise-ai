# HostelWise AI - Process Flow Diagram Generator
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_process_flow_diagram():
    # Set up the figure (16:9 widescreen aspect ratio)
    fig, ax = plt.subplots(figsize=(16, 9))
    fig.patch.set_facecolor('#0b1120')  # Dark blue background
    ax.set_facecolor('#0b1120')
    
    # Hide axes
    ax.axis('off')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    
    # Title
    ax.text(8, 8.2, "HostelWise AI: End-to-End Process Flow", 
            color='#ffffff', fontsize=22, fontweight='bold', ha='center', va='center')
    ax.text(8, 7.7, "Google Cloud (BigQuery/GCS) + NVIDIA RAPIDS (cuDF) + Gemini 1.5 Flash", 
            color='#94a3b8', fontsize=14, style='italic', ha='center', va='center')
    
    # Define boxes [x, y, width, height, label, description, color]
    boxes = [
        {
            "x": 0.5, "y": 4.0, "w": 2.0, "h": 2.2, "title": "1. INGESTION",
            "desc": "• CSV Upload\n• Manual UPI Entry\n• Archive in GCS", "color": "#38bdf8"
        },
        {
            "x": 3.0, "y": 4.0, "w": 2.2, "h": 2.2, "title": "2. GPU ETL",
            "desc": "• NVIDIA cuDF\n• Remove Duplicates\n• Parse Timestamps\n• Normalize Category", "color": "#76b900"
        },
        {
            "x": 5.7, "y": 4.0, "w": 2.2, "h": 2.2, "title": "3. WAREHOUSE",
            "desc": "• Google BigQuery\n• Date Partitioning\n• Category Clustering\n• SQL Analytical Views", "color": "#f59e0b"
        },
        {
            "x": 8.4, "y": 4.0, "w": 2.2, "h": 2.2, "title": "4. ML ANALYTICS",
            "desc": "• Ridge Regression\n• Cyclical Time Vectors\n• 30-Day Forecast\n• 0-100 Risk Engine", "color": "#a855f7"
        },
        {
            "x": 11.1, "y": 4.0, "w": 2.0, "h": 2.2, "title": "5. GEMINI AI",
            "desc": "• Gemini 1.5 Flash\n• RAG Context Builder\n• Ingests Telemetry\n• Conversational Coach", "color": "#ec4899"
        },
        {
            "x": 13.6, "y": 4.0, "w": 1.9, "h": 2.2, "title": "6. DASHBOARD",
            "desc": "• Streamlit UI\n• Plotly Charts\n• Risk Gauges\n• Savings Advice", "color": "#06b6d4"
        }
    ]
    
    # Draw boxes
    for box in boxes:
        # Create rounded rectangle
        rect = patches.FancyBboxPatch(
            (box["x"], box["y"]), box["w"], box["h"],
            boxstyle="round,pad=0.1",
            linewidth=2, edgecolor=box["color"], facecolor='#1e293b',
            mutation_scale=0.4
        )
        ax.add_patch(rect)
        
        # Add title text
        ax.text(box["x"] + box["w"]/2, box["y"] + box["h"] - 0.3, box["title"],
                color=box["color"], fontsize=12, fontweight='bold', ha='center', va='center')
        
        # Add description text
        ax.text(box["x"] + 0.1, box["y"] + box["h"]/2 - 0.2, box["desc"],
                color='#e2e8f0', fontsize=9.5, ha='left', va='center', linespacing=1.4)
        
    # Draw arrows
    for i in range(len(boxes) - 1):
        start_x = boxes[i]["x"] + boxes[i]["w"] + 0.1
        start_y = boxes[i]["y"] + boxes[i]["h"]/2
        end_x = boxes[i+1]["x"] - 0.1
        end_y = boxes[i+1]["y"] + boxes[i+1]["h"]/2
        
        ax.annotate('', xy=(end_x, end_y), xytext=(start_x, start_y),
                    arrowprops=dict(arrowstyle="-|>", color='#475569', lw=2.5, mutation_scale=15))
        
    # Add a subtitle at the bottom indicating local fallback
    ax.text(8, 1.5, "🔄 Resilient Hybrid Storage: Local SQLite database acts as an offline-first fallback if GCP is unavailable.", 
            color='#94a3b8', fontsize=12, fontweight='bold', ha='center', va='center',
            bbox=dict(facecolor='#1e293b', edgecolor='#475569', boxstyle='round,pad=0.5'))
    
    plt.tight_layout()
    output_path = "process_flow_diagram.png"
    plt.savefig(output_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Success! Process flow diagram saved to {output_path}")

if __name__ == "__main__":
    generate_process_flow_diagram()
