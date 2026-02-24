# Memory Database & Custom SQL Engine



An in-memory database built from scratch in Python. This project utilizes a custom Doubly Linked List data structure to store records loaded from a CSV file. It features four distinct sorting algorithms, a custom SQL-like parser for data querying, and recursive file exporting.

## 🟢 Live Demo
You can view and test the Python logic directly in your browser without any terminal setup:
**[Run on OnlineGDB](https://onlinegdb.com/qz1fPw1YHC)**

## 🚀 Features

* **Custom Data Structure:** Implements a true Doubly Linked List (`Node` and `DoublyLinkedList` classes) for underlying data storage.
* **Multiple Sorting Algorithms:** Includes from-scratch implementations of Bubble Sort, Insertion Sort, Merge Sort, and Quick Sort.
* **Custom SQL Query Parser:** Supports a custom SQL grammar to select specific columns, define sort order, and choose the sorting algorithm via Regex.
* **Recursive Export:** Writes sorted data back to CSV files using strict recursive functions (no iterative loops for file writing).
* **Performance Profiling:** Built-in tracking for execution time, algorithmic comparisons, and memory usage.

## 📋 Custom SQL Grammar

The database parses a specific, self-defined SQL syntax. 

**Standard Format:**
> `select {column_names} from {table} order by {column} ASC/DSC with {sorting_algorithm}`

**Supported Algorithms:** `bubble_sort`, `insertion_sort`, `merge_sort`, `quick_sort`

**Examples:**
```sql
-- Select all columns, sort by age ascending using bubble sort
select * from t1 order by age ASC with bubble_sort.

-- Select specific columns, sort by absences descending using quick sort
select school, sex, age, absences from t1 order by absences DSC with quick_sort.

-- Handles trailing commas and periods safely
select age, studytime, failures, from t1 order by failures ASC with merge_sort
```

## 🛠️ Setup and Installation

1. Clone the repository:
```bash
git clone [https://github.com/yourusername/memory-database.git](https://github.com/yourusername/memory-database.git)
cd memory-database
```

2. Ensure you have Python 3 installed. No external pip packages are required (uses standard libraries only).
3. Place your dataset (e.g., `student-data.csv`) in the root directory.

## 💻 Usage

To run the script locally and generate the sorted CSV outputs:
```bash
python3 main.py
```
This will automatically execute standard sorting across all algorithms, execute the custom SQL queries, and export the resulting `sorted_*.csv` files.

---

## 📊 Linux Performance Benchmarking Commands

This project includes support for heavy algorithmic benchmarking using native Linux performance commands. To measure CPU cycles, disk I/O, and memory page faults, run the script through the following tools:

**1. Overall System & CPU Time:**
```bash
/usr/bin/time -v python3 main.py
```

**2. Hardware CPU Cycles & Instructions:**
```bash
sudo perf stat -d python3 main.py
```

**3. System Call & Disk I/O Profiling:**
```bash
sudo strace -c python3 main.py
```

**4. Disk Read/Write Speeds:**
```bash
sudo pidstat -d -e python3 main.py
```
*(Note: To permanently allow `perf stat` without sudo, run: `echo -1 | sudo tee /proc/sys/kernel/perf_event_paranoid`)*

---

## 🤖 Automated Benchmarking Script (Bash)

To run all performance tests simultaneously and save the output, use the included `run_tests.sh` script:

```bash
#!/bin/bash

echo "====================================================="
echo "1. TIME COMMAND (CPU Time & RAM)"
echo "====================================================="
/usr/bin/time -v python3 main.py 

echo ""
echo "====================================================="
echo "2. PERF STAT (CPU Cycles & Instructions)"
echo "====================================================="
sudo perf stat -d python3 main.py 

echo ""
echo "====================================================="
echo "3. STRACE (Disk I/O and System Calls)"
echo "====================================================="
sudo strace -c python3 main.py 

echo ""
echo "====================================================="
echo "4. PIDSTAT (Disk Read/Write usage)"
echo "====================================================="
sudo pidstat -d -e python3 main.py 
```

**To execute the script:**
```bash
chmod +x run_tests.sh
./run_tests.sh | tee assignment_output.txt
```

## 📁 File Structure

* `main.py` - Core application containing the Linked List, sorting algorithms, and SQL Regex parser.
* `run_tests.sh` - Bash script for automated Linux performance benchmarking.
* `student-data.csv` - The input dataset.
* `sorted_*.csv` - The recursively exported output files (generated at runtime).