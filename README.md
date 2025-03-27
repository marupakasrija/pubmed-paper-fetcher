# PubMed Paper Fetcher - README

## Project Overview

PubMed Paper Fetcher is a specialized command-line tool designed to identify and extract research papers from PubMed where at least one author is affiliated with a pharmaceutical or biotech company. This tool addresses the challenge of efficiently identifying industry-authored research among the vast repository of academic publications.

## Motivation

The intersection of academic and industrial research is crucial for understanding:

- How pharmaceutical companies contribute to scientific knowledge
- Which research areas are receiving industry attention and funding
- Potential collaborations between academia and industry
- Trends in industry-sponsored research over time

Manually identifying such papers is time-consuming and error-prone. This tool automates the process, allowing researchers, analysts, and industry professionals to quickly gather relevant data.

## Prerequisites

Before using the tool, ensure you have the following dependencies installed:

- Python 3.8+
- Poetry (for dependency management)
- Internet connection (to access PubMed API)

You can install Poetry using:

```shell
pip install poetry
```

## Setup Guide

Follow these steps to set up and run the tool:

1. Clone the repository:
   ```shell
   git clone https://github.com/marupakasrija/pubmed-paper-fetcher.git
   cd pubmed-paper-fetcher
   ```

2. Install dependencies using Poetry:
   ```shell
   poetry install
   ```

3. Activate the virtual environment:
   ```shell
   poetry shell
   ```

4. Run the tool with a sample query:
   ```shell
   poetry run get-papers-list "oncology AND immunotherapy" -f immuno_companies.csv
   ```

## How It Works

### Technical Approach

The tool follows a systematic approach to identify and process papers:

1. **Query Execution**: Leverages the PubMed API (via Entrez) to search for papers matching user-specified criteria
2. **Metadata Retrieval**: Fetches detailed information for each paper, including author affiliations
3. **Affiliation Analysis**: Applies heuristic algorithms to identify non-academic authors
4. **Company Identification**: Extracts company names from author affiliations
5. **Data Structuring**: Organizes the findings into a structured format
6. **Output Generation**: Produces a CSV file with comprehensive information

### Affiliation Detection Algorithm

The core of the tool is its algorithm for distinguishing between academic and industry affiliations:

1. **Keyword-Based Classification**:
   - Academic indicators: "university", "college", "institute", "hospital", etc.
   - Industry indicators: "pharma", "biotech", "inc", "corp", "ltd", etc.

2. **Contextual Analysis**:
   - Examines the structure and context of affiliation strings
   - Identifies company names within complex affiliation texts
   - Handles variations in how companies are represented

3. **Email Domain Analysis**:
   - Uses email domains as supplementary evidence
   - Corporate email domains often indicate industry affiliation

4. **Pattern Recognition**:
   - Recognizes common patterns in how affiliations are formatted
   - Handles international variations in institution naming

### Data Processing Pipeline

The tool implements a robust data processing pipeline:

1. **Input Processing**: Validates and normalizes user queries
2. **API Interaction**: Manages connections to PubMed with error handling and retry logic
3. **XML Parsing**: Extracts structured data from PubMed's XML responses
4. **Affiliation Processing**: Applies the detection algorithm to identify relevant authors
5. **Data Enrichment**: Adds additional context and metadata
6. **Output Formatting**: Generates clean, consistent CSV output

## Use Cases

### Pharmaceutical Competitive Intelligence

Analysts can track which companies are publishing in specific therapeutic areas:

```shell
poetry run get-papers-list "oncology AND immunotherapy" -f immuno_companies.csv
```

### Academic-Industry Collaboration Analysis

Researchers can identify potential industry partners based on publication patterns:

```shell
poetry run get-papers-list "CRISPR AND gene therapy" -f gene_therapy_industry.csv
```

### Regulatory and Policy Research

Policy makers can analyze industry research output in regulated areas:

```shell
poetry run get-papers-list "drug safety AND pharmacovigilance" -f safety_research.csv
```

### Investment Research

Financial analysts can track publication trends to inform investment decisions:

```shell
poetry run get-papers-list "artificial intelligence AND drug discovery" -f ai_pharma.csv
```

### Scientific Trend Analysis

Track how industry research focus evolves over time:

```shell
poetry run get-papers-list "precision medicine AND (\"2018/01/01\"[PDAT] : \"2023/12/31\"[PDAT])" -f precision_med_trend.csv
```

## Technical Implementation

### Python Implementation

The Python implementation uses:

- **Object-Oriented Design**: Clean separation of concerns with well-defined classes
- **Type Hints**: Comprehensive type annotations for better code quality
- **Functional Components**: Pure functions for data transformation steps
- **Error Handling**: Robust exception handling throughout the codebase
- **Logging**: Detailed logging for debugging and monitoring

# An Easy approach developed only for you!

A Python package to fetch research papers from **PubMed** with ease.

## Installation
Since the package is hosted on **TestPyPI**, install it using:

```bash
pip install -i https://test.pypi.org/simple/ pubmed-paper-fetcher-sriworkshere
```

## Usage

### 1. Import the package
```python
from pubmed_paper_fetcher import fetch_paper
```

### 2. Fetch a paper by keyword
```python
paper = fetch_paper("Deep Learning in Medical Imaging")
print(paper)
```

### 3. Fetch multiple papers
```python
papers = fetch_paper(["Neural Networks", "AI in Healthcare"])
for p in papers:
    print(p)
```

## Features
✅ Fetch papers from **PubMed**  
✅ Retrieve metadata (title, authors, abstract, etc.)  
✅ Support for multiple queries  

## Who Can Use This?
- **Researchers**: Quickly find relevant papers.  
- **Students**: Get references for assignments.  
- **Developers**: Build research-based applications.  

### Report Document available at - [Google Docs](https://docs.google.com/document/d/1_Irma1DhyIuqMwpJiORkZIEOsJ07d1uzAg2CW5-ygVw/edit?usp=sharing)
