# 🎯 Bumphunter Analyzer Engine

**Identify and expose exploitative join patterns in online poker**  
A streamlined, Python-based system for uncovering **potential bumphunting behavior** through time-based analysis and user profiling.

---

## 🚀 Overview

The Bumphunter Analyzer Engine processes poker session data to highlight cases where players repeatedly join tables shortly after others — a classic signal of **predatory behavior**. Designed for analysts and integrity teams, this engine helps you:

- Detect suspicious joins within a user-defined time window  
- Build profiles of frequent **hunters** and **targets**  
- Quantify behavior using a score system that factors in frequency, percentage, and consistency  
- Output everything in a self-contained, interactive **HTML report**

---

## 📦 Features

- ✅ **Fast Detection** of join patterns based on session timestamps
- 📊 **User Profiling** with individual target/hunter breakdowns
- 🔢 **Scoring Model** (100 points total):
  - Join Frequency → up to **40 pts**
  - Join Percentage → up to **30 pts**
  - Target Consistency → up to **30 pts**
- 📄 **JSON Exports** for further inspection or downstream systems
- 🌐 **HTML Report**: plug-and-play, lightweight, and compresses your data for fast rendering

---

## 🔧 Requirements

- Python **3.8+**
- `pandas`
- `numpy`

Install dependencies via pip:

```bash
pip install pandas numpy
