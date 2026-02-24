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
            self.columns = reader.fieldnames
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
    
    def execute_query(self, query: str) -> List[dict]:
        """
        Execute custom SQL-like query
        Format: select {columns} from {table} order by {column} ASC/DSC with {sort_algorithm}
        Example: select age, sex, school from t1 order by age ASC with bubble_sort
        """
        # 1. Remove any trailing periods or spaces from the end of the query
        query = query.strip().rstrip('.')
        
        # Parse the query using regex
        pattern = r'select\s+(.+?)\s+from\s+(\w+)\s+order\s+by\s+(\w+)\s+(ASC|DSC)\s+with\s+(\w+)'
        match = re.match(pattern, query, re.IGNORECASE)
        
        if not match:
            raise ValueError("Invalid query format. Use: select {columns} from {table} order by {column} ASC/DSC with {sort_algorithm}")
        
        columns_str, table, order_column, direction, sort_algorithm = match.groups()
        
        # 2. Parse columns and safely handle any extra commas (like "c1, c2, c3,")
        if columns_str.strip() == '*':
            selected_columns = self.columns
        else:
            # The 'if col.strip()' part prevents empty strings if there is a trailing comma
            selected_columns = [col.strip() for col in columns_str.split(',') if col.strip()]
        
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
        
        return result
    def export_to_csv_recursive(self, data: List[dict], filepath: str, index=0):
        """
        Export data to CSV using recursion
        Base case: when index reaches the length of data
        """
        if index == 0:
            # Write header on first call
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                if data:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
            # print(f"\nExporting to {filepath}...")
        
        # Base case: all rows written
        if index >= len(data):
            # print(f"Successfully exported {len(data)} records to {filepath}")
            return
        
        # Recursive case: write one row and recurse
        with open(filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[index].keys())
            writer.writerow(data[index])
        
        # Recurse to next row
        self.export_to_csv_recursive(data, filepath, index + 1)
    
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


def main():
    print("=== Memory Database running on OnlineGDB ===")
    
    db = MemoryDatabase()
    csv_file = "student-data.csv"
    
    # 1. Load the data
    try:
        db.load_csv(csv_file)
        print(f"Successfully loaded {csv_file}")
    except FileNotFoundError:
        print(f"\nERROR: Could not find '{csv_file}'.")
        print("Please click the 'Upload file' button in the top left of OnlineGDB to upload your CSV.")
        return

    # ==========================================================
    # TASK 1: Run the standard sorting algorithms (Req #4 & #6)
    # ==========================================================
    print("\n" + "="*70)
    print("TASK 1: RUNNING STANDARD SORTING ALGORITHMS")
    print("="*70)
    
    column_to_sort = "age"
    order = "ASC"
    algorithms = [
        "bubble_sort", 
        "insertion_sort", 
        "merge_sort", 
        "quick_sort"
    ]
    
    for algo in algorithms:
        print(f"\nRunning {algo.upper()} on column '{column_to_sort}' ({order})...")
        # This automatically runs the sort, tracks stats, and exports sorted_algo.csv
        db.run_sort(algo, column_to_sort, order)


    # ==========================================================
    # TASK 2: Execute Custom SQL Queries (Req #5)
    # ==========================================================
    print("\n\n" + "="*70)
    print("TASK 2: EXECUTING CUSTOM SQL QUERIES")
    print("="*70)
    
    queries = [
        "select * from t1 order by age ASC with bubble_sort.",
        "select school, sex, age, absences from t1 order by absences DSC with quick_sort.",
        "select age, studytime, failures, from t1 order by failures ASC with merge_sort"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\nExecuting SQL Query {i}:")
        print(f"  {query}")
        
        try:
            # Parse and execute the SQL
            result = db.execute_query(query)
            
            # Extract algorithm name to name the file
            pattern = r'with\s+(\w+)'
            match = re.search(pattern, query.strip().rstrip('.'))
            algo_name = match.group(1) if match else f"query_{i}"
            
            # Export the SQL results
            out_file = f"sorted_sql_{algo_name}.csv"
            db.export_to_csv_recursive(result, out_file)
            print(f" Exported {len(result)} records to {out_file} (Time: {db.stats[algo_name]['time']:.6f}s)")
            
        except Exception as e:
            print(f"Error executing query: {e}")
            
    print("\n All tasks complete! You now have both standard and SQL-sorted CSV files.")


if __name__ == "__main__":
    main()
