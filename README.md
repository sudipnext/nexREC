# nexREC: Graph-Based Movie Recommendation Engine 🎬


## The Story Behind nexREC

nexREC was born out of a final-year academic project that took us on an incredible journey through the world of recommendation systems. What started as a simple idea evolved into a sophisticated graph-based recommendation engine that truly understands user preferences.

### The Journey

The path to building nexREC wasn't straightforward. We began by exploring traditional recommendation systems, diving deep into content-based filtering and collaborative filtering. However, we quickly realized that user preferences are incredibly diverse and complex - influenced by social circles, trends, and personal experiences.

This realization led us to explore Graph Neural Networks (GNNs), a less-researched but promising area that could capture these complex relationships. After countless sleepless nights, hundreds of research papers, and numerous experiments, we developed a system that could instinctively respond to user needs.

## Technical Implementation

### Core Technologies

- **Backend Framework**: Django & Django Rest Framework
- **Frontend**: Remix
- **Vector Database**: Milvus
- **Relational Database**: PostgreSQL
- **Machine Learning**: 
  - Sentence Transformers (SBERT)
  - PyTorch
  - PyTorch Geometric
- **Deployment**:
  - AWS Lightsail (Backend & Milvus)
  - Aiven Cloud (PostgreSQL)
  - HuggingFace (Models)
  - Vercel (Frontend)

### Model Architecture

We experimented with various GNN architectures including:
- SAGEConv
- GAT (Graph Attention Networks)
- GATv2

After extensive hyperparameter tuning and optimization, we achieved an RMSE loss between 0.94 and 1.21, which is quite solid considering real-world rating deviations and data skewness.

## Data Processing

The project involved processing approximately 10k movies with user reviews. We used PySpark for efficient data cleaning and processing, which was a significant challenge in itself. The data distribution analysis and sampling experiments were crucial in achieving our final results.

## Team

This project wouldn't have been possible without the incredible teamwork of:
- Basanta Shrestha
- Pawan Shah
- Suwash Shrestha

## Getting Started

### Prerequisites

- Python 3.8+
- PostgreSQL
- Milvus



## Acknowledgments

Special thanks to Sushan Kattel for the invaluable guidance in PySpark and data processing.

---

*Note: The deployed version is currently offline due to AWS billing considerations. We're working on making it available again soon!* 