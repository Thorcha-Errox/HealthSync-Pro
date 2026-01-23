# 🏥 HealthSync: Intelligent Inventory Command Center

> **Eliminating the "Last Mile" supply chain crisis in public health with Snowflake & AI.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://streamlit.io)
[![Snowflake](https://img.shields.io/badge/Built%20With-Snowflake-29B5E8?style=flat&logo=Snowflake)](https://www.snowflake.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

---

## 📖 Table of Contents
- [The Problem](#-the-problem)
- [The Solution](#-the-solution)
- [Key Features & Screenshots](#-key-features--screenshots)
- [How It Works (Architecture)](#-how-it-works-architecture)
- [Technology Stack](#-technology-stack)
- [Installation & Setup](#-installation--setup)
- [Future Roadmap](#-future-roadmap)

---

## 🚨 The Problem
In public health, a stock-out isn't just a logistical error; it is a patient denied critical care. 

Hospitals and NGOs often struggle with:
1.  **Fragmented Data:** Inventory logs live in disconnected spreadsheets or physical registers.
2.  **Reactive Management:** Procurement teams only realize supplies are low when shelves are already empty.
3.  **Waste & Expiry:** Without visibility into "burn rates," some clinics hoard medicine while others run dry.

## 💡 The Solution
**HealthSync** is a unified **Inventory Command Center** that transforms reactive chaos into proactive intelligence. 

By ingesting daily stock logs into **Snowflake**, we use **Dynamic Tables** to automatically calculate burn rates, lead times, and critical thresholds. The data is visualized in a **Streamlit** dashboard that acts as a "Single Source of Truth," allowing procurement officers to spot risks across hundreds of locations instantly.

---

## 📸 Key Features & Screenshots

### 1. The "God's Eye" View (Heatmap)
Instantly visualize stock health across the entire network. The heatmap uses a color-coded scale (Red = Critical, Green = Healthy) to highlight locations that need immediate attention.
* **Active Locations:** See how many sites are reporting.
* **KPI Cards:** Track total SKUs and active critical alerts at a glance.

![Dashboard Overview](assets/dashboard_overview.png) 


### 2. Risk Analysis & Predictive Modeling
We don't just show current stock; we calculate **"Days Remaining"**. 
* **Top Risks:** A bar chart showing items with the lowest coverage (e.g., "IV Set has only 1.1 days left").
* **Alert Distribution:** A breakdown of how much of your inventory is in the "Danger Zone."

![Risk Analysis](assets/risk_analysis.png)


### 3. Actionable Procurement Desk
Data is useless without action. The Procurement Desk automatically generates a **Prioritized Reorder List**.
* **Visual Stock Levels:** Progress bars show stock depth.
* **Smart Reorder Qty:** The system suggests exactly how much to buy to reach safe levels.
* **One-Click Export:** Download a CSV formatted for immediate use by procurement teams.

![Procurement Desk](assets/procurement_desk.png)

---

## ⚙️ How It Works (Architecture)

The system follows a modern **ELT (Extract, Load, Transform)** architecture entirely within the Snowflake Data Cloud.

1.  **Ingestion (Data Loading):**
    * Daily stock logs (Location, Item, Received, Issued) are loaded into the `DAILY_STOCK_LOGS` table.
2.  **Transformation (The Brain):**
    * **Snowflake Dynamic Tables** run continuously in the background.
    * They calculate `Avg Daily Usage`, `Lead Time`, and `Days Remaining` automatically.
    * Logic: `Status = CRITICAL` if `Days Remaining < Lead Time`.
3.  **Visualization (The Face):**
    * **Streamlit in Snowflake** queries the processed metrics.
    * The app uses **Altair** for rendering interactive charts and theme-aware CSS for a premium UI.

---

## 🛠 Technology Stack
* **Database:** Snowflake Data Cloud (Warehouses, Databases, Schemas)
* **Data Pipelines:** Snowflake Dynamic Tables (Automated SQL transformations)
* **Frontend Application:** Streamlit (Python-based Web App)
* **Visualization:** Altair & Pandas
* **Language:** Python 3.8+ & SQL

---

## 🚀 Installation & Setup

### Prerequisites
* A Snowflake Account.
* Python installed locally (for testing) or access to Streamlit in Snowflake.

### Step 1: Database Setup
Run the `setup.sql` script (found in this repo) in a Snowflake Worksheet to create the necessary tables and dummy data.

```sql
-- Example command from setup.sql
CREATE OR REPLACE DATABASE HEALTH_INVENTORY_DB;
...