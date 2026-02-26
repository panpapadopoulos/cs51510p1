#!/usr/bin/env python3
"""
Memory Database with Doubly Linked List
Supports: Bubble Sort, Insertion Sort, Merge Sort, Quick Sort
Custom SQL-like query language
"""

import csv
import re
import time
import copy
from typing import List, Optional, Any
import argparse
import sys
import resource
import os
import subprocess
import threading

sys.setrecursionlimit(1000000)


class Node:
    """Node in doubly linked list"""
    def __init__(self, data: dict):
        self.data = data
        self.next: Optional['Node'] = None
        self.prev: Optional['Node'] = None


class DoublyLinkedList:
    """Doubly Linked List implementation for database storage"""
    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.size = 0
    
    def append(self, data: dict):
        """Add a new node at the end"""
        new_node = Node(data)
        if not self.head:
            self.head = self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.size += 1
    
    def to_list(self) -> List[dict]:
        """Convert linked list to Python list"""
        result = []
        current = self.head
        while current:
            result.append(current.data)
            current = current.next
        return result
    
    def from_list(self, data_list: List[dict]):
        """Build linked list from Python list"""
        self.head = self.tail = None
        self.size = 0
        for item in data_list:
            self.append(item)
    
    def clear(self):
        """Clear the list"""
        self.head = self.tail = None
        self.size = 0


class MemoryDatabase:
    """Main database class with sorting capabilities"""
    
    def __init__(self):
        self.data = DoublyLinkedList()
        self.columns = []
        self.stats = {
            'bubble_sort': {'time': 0, 'comparisons': 0},
            'insertion_sort': {'time': 0, 'comparisons': 0},
            'merge_sort': {'time': 0, 'comparisons': 0},
            'quick_sort': {'time': 0, 'comparisons': 0}
        }
        self._peak_mem = 0
        self._monitoring = False
    
    def load_csv(self, filepath: str):
        """Load data from CSV file into the doubly linked list"""
        # print(f"Loading data from {filepath}...")
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            self.columns = reader.fieldnames or []
            for row in reader:
                self.data.append(row)
        # print(f"Loaded {self.data.size} records with {len(self.columns)} columns")
        # print(f"Columns: {', '.join(self.columns)}\n")
    
    def _compare_values(self, val1, val2, ascending=True):
        """Compare two values, handling numeric and string types"""
        self.stats[self._current_sort]['comparisons'] += 1

        try:
            v1 = float(val1)
            v2 = float(val2)
        except:
            v1 = str(val1)
            v2 = str(val2)

        if ascending:
            return v1 > v2
        else:
            return v1 < v2
    
    # BUBBLE SORT
    def bubble_sort(self, data_list: List[dict], column: str, ascending=True) -> List[dict]:
        """Bubble sort implementation"""
        self._current_sort = 'bubble_sort'
        arr = list(data_list)
        n = len(arr)
        
        for i in range(n):
            swapped = False
            for j in range(0, n - i - 1):
                if self._compare_values(arr[j][column], arr[j + 1][column], ascending):
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
                    swapped = True
            if not swapped:
                break
        
        return arr
    
    # INSERTION SORT
    def insertion_sort(self, data_list: List[dict], column: str, ascending=True) -> List[dict]:
        """Insertion sort implementation"""
        self._current_sort = 'insertion_sort'
        arr = list(data_list)
        
        for i in range(1, len(arr)):
            key = arr[i]
            j = i - 1
            
            while j >= 0 and self._compare_values(arr[j][column], key[column], ascending):
                arr[j + 1] = arr[j]
                j -= 1
            arr[j + 1] = key
        
        return arr
    
    # MERGE SORT
    def merge_sort(self, data_list: List[dict], column: str, ascending=True) -> List[dict]:
        """Merge sort implementation"""
        self._current_sort = 'merge_sort'
        arr = list(data_list)
        
        def merge(left, right):
            result = []
            i = j = 0
            
            while i < len(left) and j < len(right):
                if not self._compare_values(left[i][column], right[j][column], ascending):
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1
            
            result.extend(left[i:])
            result.extend(right[j:])
            return result
        
        def merge_sort_recursive(arr):
            if len(arr) <= 1:
                return arr
            
            mid = len(arr) // 2
            left = merge_sort_recursive(arr[:mid])
            right = merge_sort_recursive(arr[mid:])
            
            return merge(left, right)
        
        return merge_sort_recursive(arr)
    
    # QUICK SORT
    def quick_sort(self, data_list: List[dict], column: str, ascending=True) -> List[dict]:
        """Quick sort implementation"""
        self._current_sort = 'quick_sort'
        arr = list(data_list)
        
        def partition(low, high):
            pivot = arr[high][column]
            i = low - 1
            
            for j in range(low, high):
                if not self._compare_values(arr[j][column], pivot, ascending):
                    i += 1
                    arr[i], arr[j] = arr[j], arr[i]
            
            arr[i + 1], arr[high] = arr[high], arr[i + 1]
            return i + 1
        
        def quick_sort_recursive(low, high):
            if low < high:
                pi = partition(low, high)
                quick_sort_recursive(low, pi - 1)
                quick_sort_recursive(pi + 1, high)
        
        quick_sort_recursive(0, len(arr) - 1)
        return arr
    
    def execute_query(self, query: str):
        """
        Execute custom SQL-like query
        Format: select {columns} from {table} order by {column} ASC/DSC with {sort_algorithm}
        Example: select age, sex, school from t1 order by age ASC with bubble_sort
        """
        # Parse the query using regex
        q = query.strip()

        # allow trailing '.' or ';'
        q = re.sub(r'[.;]\s*$', '', q)

        # allow extra comma before FROM (assignment example sometimes has it)
        q = re.sub(r',\s*from\b', ' from', q, flags=re.IGNORECASE)

        pattern = r'^\s*select\s+(.+?)\s+from\s+(\w+)\s+order\s+by\s+(\w+)\s+(ASC|DSC|DESC)\s+with\s+(\w+)\s*$'
        match = re.match(pattern, q, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid query format. Use: select {columns} from {table} order by {column} ASC/DSC with {sort_algorithm}")
        
        columns_str, table, order_column, direction, sort_algorithm = match.groups()
        
        # Only one table supported (matches your assignment examples)
        if table.lower() != "t1":
            raise ValueError("Only table supported: t1")

        # Case-insensitive column support
        col_map = {c.lower(): c for c in self.columns}

        def normalize_col(name: str) -> str:
            key = name.strip().lower()
            return col_map.get(key, name.strip())
        
        # Parse columns
        if columns_str.strip() == '*':
            selected_columns = self.columns
        else:
            selected_columns = [normalize_col(col) for col in columns_str.split(',') if col.strip()]
        
        order_column = normalize_col(order_column)

        direction = direction.upper()
        if direction == "DESC":
            direction = "DSC"

        # Validate columns
        for col in selected_columns:
            if col not in self.columns:
                raise ValueError(f"Column '{col}' not found in database")
        
        if order_column not in self.columns:
            raise ValueError(f"Order column '{order_column}' not found in database")
        
        # Get sorting algorithm
        sort_methods = {
            'bubble_sort': self.bubble_sort,
            'insertion_sort': self.insertion_sort,
            'merge_sort': self.merge_sort,
            'quick_sort': self.quick_sort
        }
        
        sort_algorithm = sort_algorithm.lower()
        aliases = {
            "bubble": "bubble_sort",
            "bubblesort": "bubble_sort",
            "insertion": "insertion_sort",
            "insertionsort": "insertion_sort",
            "merge": "merge_sort",
            "mergesort": "merge_sort",
            "quick": "quick_sort",
            "quicksort": "quick_sort",
        }
        sort_algorithm = aliases.get(sort_algorithm, sort_algorithm)

        if sort_algorithm not in sort_methods:
            raise ValueError(f"Unknown sorting algorithm: {sort_algorithm}. Use: bubble_sort, insertion_sort, merge_sort, quick_sort")
        
        # Reset statistics
        self.stats[sort_algorithm] = {'time': 0, 'comparisons': 0}
        
        # Convert to list, sort, and convert back
        data_list = self.data.to_list()
        
        # print(f"\nExecuting query: {query}")
        # print(f"Sorting {len(data_list)} records by '{order_column}' ({direction}) using {sort_algorithm}...")
        
        ascending = direction.upper() == 'ASC'
        
        start_time = time.time()
        sorted_data = sort_methods[sort_algorithm](data_list, order_column, ascending)
        end_time = time.time()
        
        self.stats[sort_algorithm]['time'] = end_time - start_time
        
        # Filter columns
        result = []
        for row in sorted_data:
            filtered_row = {col: row[col] for col in selected_columns}
            result.append(filtered_row)
        
        # print(f"Sort completed in {self.stats[sort_algorithm]['time']:.6f} seconds")
        # print(f"Comparisons made: {self.stats[sort_algorithm]['comparisons']}")
        
        return result, sort_algorithm
    
    def export_to_csv_recursive(self, data: List[dict], filepath: str):
        """Export data to CSV using recursion (file opened once)."""
        if not data:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                pass
            return

        fieldnames = list(data[0].keys())

        def write_rows(i: int, writer):
            if i >= len(data):  # base case
                return
            writer.writerow(data[i])
            write_rows(i + 1, writer)  # recursive step

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            write_rows(0, writer)

    def _memory_usage_kb(self):
        pid = os.getpid()
        result = subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)])
        return int(result.strip())

    def _memory_monitor(self):
        self._peak_mem = self._memory_usage_kb()
        while self._monitoring:
            current = self._memory_usage_kb()
            if current > self._peak_mem:
                self._peak_mem = current
            time.sleep(0.001)

    def get_data_snapshot(self):
        return self.data.to_list()

    def run_sort(self, algorithm: str, order_column: str, direction: str):
        """Non-interactive runner method for script automation"""
        ascending = direction.upper() == 'ASC'

        sort_methods = {
            'bubble_sort': self.bubble_sort,
            'insertion_sort': self.insertion_sort,
            'merge_sort': self.merge_sort,
            'quick_sort': self.quick_sort
        }

        base_data = self.get_data_snapshot()

        # warmup
        sort_methods[algorithm](list(base_data), order_column, ascending)

        baseline = self._memory_usage_kb()

        self._monitoring = True
        monitor = threading.Thread(target=self._memory_monitor)
        monitor.start()

        start_time = time.time()
        result = sort_methods[algorithm](list(base_data), order_column, ascending)
        end_time = time.time()

        self._monitoring = False
        monitor.join()

        peak_sort_mem = self._peak_mem - baseline

        out_file = f"sorted_{algorithm}.csv"
        self.export_to_csv_recursive(result, out_file)

        print("\n--- PERFORMANCE ---")
        print("Algorithm:", algorithm)
        print("Time:", round(end_time - start_time, 6), "seconds")
        print("Peak Sort Memory:", peak_sort_mem, "KB")
    
    def print_sample(self, data: List[dict], n=10):
        """Print first n records"""
        print(f"\nFirst {min(n, len(data))} records:")
        print("-" * 80)
        for i, row in enumerate(data[:n]):
            print(f"Record {i+1}:")
            for key, value in row.items():
                print(f"  {key}: {value}")
            print()


def print_performance_stats(db: MemoryDatabase):
    """Print performance statistics"""
    print("\n" + "="*80)
    print("PERFORMANCE STATISTICS")
    print("="*80)
    for algo, stats in db.stats.items():
        if stats['time'] > 0:
            print(f"\n{algo.upper().replace('_', ' ')}:")
            print(f"  Time: {stats['time']:.6f} seconds")
            print(f"  Comparisons: {stats['comparisons']}")
            if stats['time'] > 0:
                print(f"  Comparisons/second: {stats['comparisons']/stats['time']:.2f}")

def print_sql_help():
    print("\nSQL-like Query Format:")
    print("  select <col1, col2, ... | *> from t1 order by <col> ASC|DSC with <algorithm>.")
    print("\nExamples:")
    print("  select age, sex from t1 order by age ASC with merge_sort.")
    print("  select age, sex, school, from t1 order by age DESC with quick.")
    print("\nAlgorithms:")
    print("  bubble_sort | bubble")
    print("  insertion_sort | insertion")
    print("  merge_sort | merge")
    print("  quick_sort | quick")
    print("Type 'q' to quit, 'help' to show this again.\n")
def main():
    db = MemoryDatabase()
    is_loaded = False
    
    while True:
        print("\n" + "="*50)
        print("         MEMORY DATABASE MAIN MENU")
        print("="*50)
        print("1. Load CSV file into Database")
        print("2. Run Standard Sorting Algorithm")
        print("3. Execute Custom SQL Query")
        print("4. Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-4): ").strip()
        
        # -----------------------------------------
        # OPTION 1: LOAD DATABASE
        # -----------------------------------------
        if choice == '1':
            filepath = input("Enter CSV filename [default: student-data.csv]: ").strip()
            if not filepath:
                filepath = "student-data.csv"
                
            try:
                db.data.clear()  
                db.load_csv(filepath)
                is_loaded = True
                print(f"\n✅ Successfully loaded {db.data.size} records from '{filepath}'.")
                print(f"Columns available: {', '.join(db.columns)}")
                
                # --- PREVIEW ADDED ---
                print("\nPreview (first 3 rows):")
                for row in db.get_data_snapshot()[:3]:
                    print(row)
                    
            except FileNotFoundError:
                print(f"\n❌ ERROR: Could not find file '{filepath}'. Please check the filename.")
        
        # -----------------------------------------
        # OPTION 2: STANDARD SORTING
        # -----------------------------------------
        elif choice == '2':
            if not is_loaded:
                print("\n❌ ERROR: Please load the database first (Option 1).")
                continue
            
            print("\n--- Select Sorting Algorithm ---")
            print("1. Bubble Sort")
            print("2. Insertion Sort")
            print("3. Merge Sort")
            print("4. Quick Sort")
            algo_choice = input("Choose algorithm (1-4): ").strip()
            
            algo_map = {'1': 'bubble_sort', '2': 'insertion_sort', '3': 'merge_sort', '4': 'quick_sort'}
            if algo_choice not in algo_map:
                print("\n❌ Invalid choice.")
                continue
            
            algo = algo_map[algo_choice]
            col = input("Enter column to sort by [default: age]: ").strip() or "age"
            
            if col not in db.columns:
                print(f"\n❌ ERROR: Column '{col}' does not exist.")
                continue
            
            order = input("Enter order (ASC/DSC) [default: ASC]: ").strip().upper() or "ASC"
            if order not in ["ASC", "DSC", "DESC"]:
                print("\n❌ Invalid order. Use ASC or DSC.")
                continue
            
            print(f"\nSorting {db.data.size} records using {algo.upper()}...")
            try:
                db.run_sort(algo, col, order)
                out_file = f"sorted_{algo}.csv"
                print(f"✅ Sorting complete! Check the generated '{out_file}'.")
                
                # --- PREVIEW ADDED ---
                # We read the first 3 lines directly from the newly created file!
                print("\nPreview (first 3 rows):")
                import csv
                with open(out_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for i, row in enumerate(reader):
                        if i >= 3: break
                        print(row)
                        
            except Exception as e:
                print(f"\n❌ Error during sorting: {e}")
                
        # -----------------------------------------
        # OPTION 3: CUSTOM SQL QUERY
        # -----------------------------------------
        elif choice == '3':
            if not is_loaded:
                print("\n❌ ERROR: Please load the database first (Option 1).")
                continue
            
            print("\n--- Execute Custom SQL Query ---")
            print("Format: select {columns} from t1 order by {column} ASC/DSC with {algorithm}.")
            print("Example: select age, sex from t1 order by absences ASC with merge_sort")
            query = input("\nDB> ").strip()
            
            if not query:
                continue
                
            try:
                result, algo_name = db.execute_query(query)
                out_file = f"sorted_sql_{algo_name}.csv"
                db.export_to_csv_recursive(result, out_file)
                
                print(f"\n✅ Exported {len(result)} records to '{out_file}'")
                print(f"⏱️ Time: {db.stats[algo_name]['time']:.6f} seconds")
                
                # --- PREVIEW ALREADY HERE ---
                print("\nPreview (first 3 rows):")
                for row in result[:3]:
                    print(row)
                    
            except Exception as e:
                print(f"\n❌ Error executing query: {e}")
                
        # -----------------------------------------
        # OPTION 4: EXIT
        # -----------------------------------------
        elif choice == '4':
            print("\nExiting Memory Database... Goodbye!")
            break
            
        else:
            print("\n❌ Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()