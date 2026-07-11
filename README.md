# 🛢️ Brent Crude Oil Change-Point Analysis Platform

> **An end-to-end Bayesian time-series analytics platform for detecting structural breaks in Brent crude oil prices, powered by PyMC, Flask, React, and Tailwind CSS.**

---

## 📖 Overview

Oil prices rarely move because of supply and demand alone. Global crises, geopolitical conflicts, OPEC policy decisions, financial recessions, and pandemics can permanently change how the market behaves.

Traditional forecasting models assume that historical patterns remain stable over time. This project challenges that assumption by identifying **when** the statistical behavior of Brent crude oil fundamentally changes.

The platform combines **Bayesian statistical modeling** with a **full-stack interactive dashboard** to help analysts, researchers, and decision-makers explore over **35 years of Brent crude oil price history** and understand the impact of major global events.

---

## ✨ Key Features

* 📊 Analyze **9,011 daily Brent crude oil price records**
* 📅 Detect structural break points using **Bayesian Change-Point Analysis**
* 📈 Compare market behavior before and after significant events
* 🌍 Explore historical geopolitical and economic disruptions
* ⚡ Interactive React dashboard with responsive visualizations
* 🔍 Dynamic filtering across multiple historical periods
* 🛡️ Graceful fallback handling when optional datasets are unavailable

---

## 🎯 Project Objective

The primary objective is to detect significant structural changes in Brent crude oil prices and quantify their relationship with major global events.

Rather than relying solely on traditional forecasting techniques, the project answers questions such as:

* When did the market fundamentally change?
* Which historical events caused the largest structural shifts?
* How did average price behavior change before and after each event?
* Can Bayesian inference provide better insight than conventional trend analysis?

---

# 🏗️ Project Workflow

## Phase 1 — Data Collection & Preprocessing

Historical Brent crude oil spot prices were collected covering:

* **Period:** May 1987 – September 2022
* **Observations:** 9,011 daily records

### Data Preparation

* Parsed inconsistent date formats using intelligent mixed-format inference
* Removed invalid observations
* Calculated daily logarithmic returns

[
R_t=\ln\left(\frac{P_t}{P_{t-1}}\right)
]

Additional statistical measures included:

* Mean
* Standard deviation
* Skewness
* Kurtosis

---

## Phase 2 — Bayesian Change-Point Modeling

The project models Brent crude prices as a sequence of statistical regimes separated by unknown structural break points.

### Methodology

* Bayesian Inference
* Markov Chain Monte Carlo (MCMC)
* PyMC probabilistic modeling

Each regime estimates:

* Mean before change (μ₁)
* Mean after change (μ₂)
* Change-point (τ)

Model convergence was validated using the **Gelman-Rubin diagnostic (R-hat)** with values close to **1.0**, indicating reliable posterior estimates.

---

## Phase 3 — Flask REST API

A lightweight Flask backend powers the analytics engine.

### Available API Features

* Historical price retrieval
* Dynamic date filtering
* Event-based analysis
* 30-day impact window extraction
* Change-point retrieval

The backend also enables communication with the React frontend through secure CORS configuration.

---

## Phase 4 — Interactive Dashboard

The frontend was developed using **React.js** and **Tailwind CSS**.

Features include:

* Interactive time-series visualization
* Historical event explorer
* Responsive dashboard
* Change-point visualization
* Dynamic statistical summaries

---

# 🛠️ Tech Stack

### Data Science

* Python
* Pandas
* NumPy
* PyMC
* ArviZ
* Matplotlib

### Backend

* Flask
* Flask-CORS

### Frontend

* React.js
* Tailwind CSS
* Recharts

### Development Tools

* Git
* GitHub
* VS Code

---

# 🚧 Engineering Challenges Solved

### Dynamic File Path Resolution

Replaced hardcoded paths with `pathlib.Path` for cross-platform compatibility.

---

### Mixed Date Parsing

Resolved parsing failures caused by heterogeneous date formats by implementing Pandas' mixed-format parsing.

---

### React Case-Sensitivity Issue

Fixed module resolution errors caused by filename casing differences between operating systems.

---

### Fault-Tolerant API Design

Implemented graceful degradation so the dashboard continues functioning even when optional analysis files are unavailable.

---

# 📊 Project Structure

```text
brent-oil-change-point-analysis/
│
├── data/
│   ├── raw/
│   │   └── BrentOilPrices.csv
│   └── processed/
│       └── events.csv
│
├── results/
│   └── change_points.csv
│
├── dashboard/
│   ├── backend/
│   │   └── app.py
│   │
│   └── frontend/
│       ├── public/
│       └── src/
│           ├── App.js
│           ├── App.css
│           └── index.css
│
└── README.md
```

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone <repository-url>
cd brent-oil-change-point-analysis
```

---

## 2. Start the Backend

```bash
cd dashboard/backend

# Activate virtual environment
python app.py
```

The backend will run at:

```
http://127.0.0.1:5000
```

---

## 3. Start the Frontend

Open another terminal:

```bash
cd dashboard/frontend

npm install
npm start
```

The React dashboard will launch automatically in your browser.

---

# 📈 Dashboard Capabilities

* Historical Brent crude price visualization
* Bayesian change-point detection
* Global event impact analysis
* Dynamic time filtering
* Interactive statistical summaries
* Responsive design for desktop and mobile

---

# 💡 Future Improvements

* Multi-change-point Bayesian models
* Forecasting with Bayesian Structural Time Series
* Docker deployment
* PostgreSQL integration
* Authentication and user management
* Cloud deployment using AWS or Azure

---

# 👤 Author

**Yadeni Getu**

Data Science | Machine Learning | Full-Stack Development | Time-Series Analytics

If you found this project interesting, feel free to ⭐ the repository and connect with me on GitHub.
