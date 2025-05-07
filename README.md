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

📁 Usage
Simply drop your session log file into the project folder and run:

bash
Copy
Edit
python Analizer.py
The engine will:

Load your session data

Detect suspicious joins

Generate profile reports

Export clean JSON data

Produce an HTML report in output/

No command-line arguments. Just run it.

📄 Input File Format
The input must be a .csv or .tsv file containing the following columns:

Column Name	Description
tableId	Unique identifier for the table
tableName	(Optional) Display name of table
username	Player’s screen name
startSession	Session start timestamp (datetime)
endSession	Session end timestamp (datetime)
`	Type of poker game
limitType	Limit type (e.g., NLH, PLO)
smallBlind	Small blind amount
bigBlind	Big blind amount

🧠 The engine auto-detects delimiter type based on the file extension.

📂 Output
All results are saved to the output/ folder:

suspicious_joins.json

bumphunter_profiles.json

target_profiles.json

combined_data.json

bumphunter_report.html

🛠️ Configuration (Optional)
To adjust detection sensitivity or customize output paths, edit these constants at the bottom of Analizer.py:

python
Copy
Edit
INPUT_FILE = r"path\\to\\your\\file.csv"
OUTPUT_DIR = r"path\\to\\your\\output\\folder"
TEMPLATE_FILE = r"path\\to\\template.html"
💡 Ideal Use Cases
Game integrity audits

Bot/bumphunter detection

Analyst tooling in high-volume poker ecosystems

Visual presentations for security reviews

📣 Final Note
This tool isn’t just about flagging players — it’s about shining a light on behavioral trends that compromise the competitive nature of your platform. With clean profiling and intuitive reports, you're better equipped to take action that’s both justified and data-backed.

Let me know if you want to embed example screenshots or include a sample dataset 







