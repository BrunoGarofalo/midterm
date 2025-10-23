🧮 Python Calculator

Welcome to the Python Calculator!

⚙️ 1. ***Prerequisites***
🔹 **Install Git**

MacOS (Homebrew)

brew install git


Windows

Download and install Git for Windows
.
✅ Accept the default options during installation.

Verify Git:

git --version

🔹 **Configure Git Globals**
git config --global user.name "Your Name"
git config --global user.email "your_email@example.com"
git config --list

🔹 **Generate SSH Keys & Connect to GitHub**

Only once per machine.

- ssh-keygen -t ed25519 -C "your_email@example.com"
- eval "$(ssh-agent -s)"
- ssh-add ~/.ssh/id_ed25519


Copy your public key

Mac/Linux:

- cat ~/.ssh/id_ed25519.pub | pbcopy


Windows (Git Bash):

- cat ~/.ssh/id_ed25519.pub | clip


Add the key to GitHub: Settings → SSH & GPG Keys → New SSH Key

Test connection:

- ssh -T git@github.com

🧩 ***2. Clone the Repository***
- git clone <repository-url>
- cd <repository-directory>

🐍 ***3. Python Environment Setup***

Create and activate a virtual environment:

- python -m venv venv
### Mac/Linux
- source venv/bin/activate
### Windows
- venv\Scripts\activate


Install dependencies:

- pip install -r requirements.txt

🔧 ***# 4. Configuration***

⚙️ **Variable - Description - Default**

### Base Directories
1. CALCULATOR_LOG_DIR: Directory for log (Default = logs)
2. CALCULATOR_HISTORY_DIR: Directory for history files (Default = history)

### File names
3. CSV_CARETAKER_HISTORY_FILE: File name of CSV for history manual save (Default= caretaker_history.csv)
4. TXT_HISTORY_FILE: JSON file where calculations are saved for by autologging observer (Default = history_log.json)
5. LOG_HISTORY_FILE: TXT file where event logs are saved (Default = event_log.txt)
6. CSV_HISTORY_FILE: CSV file where autosave observer saves the each calculation (Defaul = history_log.csv) 

### CSV file columns
7. CSV_COLUMNS: Column names of CVS files (Default = timestamp,operation,operand1,operand2,result,instance_id)

### History Settings
8. CALCULATOR_MAX_HISTORY_SIZE: Max history entries	(Default = 100)
9. CALCULATOR_AUTO_SAVE: Auto-save history (Default=True)

### Calculation Settings
10. CALCULATOR_PRECISION: Decimal places in results (Default = 4)
11. CALCULATOR_MAX_INPUT_VALUE: Max allowed input (Default = 1000)
12. CALCULATOR_DEFAULT_ENCODING: File encoding (Default = utf-8)


▶️ ***5. Running the Calculator***
- python calculator_repl.py

Prompt Example:

👉 Select operation (type 'help' to list commands):

Type help to see commands:

🔑 Key	📌 Operation
A	Percentage
B	Modulo
C	Multiplication
D	Root
E	Absolute Difference
F	Integer Division
G	Addition
H	Subtraction
I	Division
J	Power
K	Display history
L	Clear history
M	Undo previous operation
N	Redo operation
O	Save history to CSV
P	Load history from CSV
Q	Exit


✨ ***6. Features***

🔄 Undo/Redo using the Memento pattern.

📂 History Tracking in memory & optional JSON/CSV persistence.

💾 Autosave configurable via .env.

🧮 Configurable Precision for results.

🚫 Input Validation for safe calculations.

👁️ Observer Pattern: logging & autosave notifications.


🧪 ***7. Testing***

Run unit tests:

- Minimum coverage set to 90%
- pytest tests/

📝 ***8. Notes***

❌ Clearing history deletes both in-memory and saved files. This is allowed if and only if user validates request

💾 Manual save exports the current history to CSV in CALCULATOR_HISTORY_DIR.

📂 Loading history only works if in-memory history is empty. If memory already has data, then the previous history will no be loaded

💡 9. ***Example Usage***
👉 Select operation (type 'help' to list commands): G or g for Addition
Enter first operand: 5
Enter second operand: 7
✅ Result of add with operands 5 and 7 = 12.0000

👉 Select operation: M --> Undo operation selected
↩️ Undo performed: 5 + 7 = 12.0000

👉 Select operation: N M --> Redo operation selected
↪️ Redo performed: 5 + 7 = 12.0000