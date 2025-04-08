# Minimal Extra Cost Path Finder for Binary String Transitions

This project provides a Python solution for finding a path through a directed graph given a binary string input. Each three-bit segment of the string represents a transition: the first two bits are an input, and the third bit is the required output. The goal is to traverse the graph such that every two-bit input produces the specified one-bit output, while minimizing any additional modifications to the graph.

![image](https://github.com/user-attachments/assets/f2b0b893-1b6e-4193-9084-f9c88243b8de)

## Problem Overview

We are given a set of nodes with pre-defined one-way transition paths. Each transition is defined by a two-bit input and produces a one-bit output. For example, one of the nodes is defined as:

- **S0**:
  - `01`: goes to **S1** with output `1`
  - `11`: goes to **S1** with output `0`
  - `10`: goes to **S2** with output `0`

The problem allows you to:
1. Create an **extra transition** if the required input does not exist or produces the wrong output.
2. Create an **extra node** if necessary.

The **extra cost** is calculated as the sum of:
- The number of extra transitions (each extra transition adds a cost of 1), and 
- The number of extra nodes created (each extra node also adds a cost of 1).

Your objective is to compute a path that processes the entire binary string (of length 3*n) with the minimum extra cost.

## Algorithm Description

The solution uses a **depth-first search (DFS) with memoization** to explore all possible paths. The state in the DFS includes:
- **Current Index**: 3-bit segment (triplet) we are processing.
- **Current Node**: The current position in the graph.
- **Extra Transitions**: A set of extra transitions that have been added, stored as a dictionary (converted to a frozenset for caching).
- **New Node Count**: The count of extra nodes created.

At each DFS step, the algorithm:
1. **Checks for a Defined Transition**: If the current node has a pre-defined transition for the given input that outputs the required value, the algorithm follows that path.
2. **Reuses an Extra Transition**: If an extra transition was added earlier for this input and its output matches the requirement, it is reused.
3. **Creates an Extra Transition**: If no valid transition exists (or if a defined transition produces a wrong output), the algorithm can add:
   - An extra transition to an existing node (cost = 1), or
   - An extra transition that goes to a newly created node (cost = 2, 1 for the transition + 1 for the new node).
  
Memoization (using `lru_cache`) optimizes the search by caching results for already-visited states.

## Usage

### Requirements
- **Python 3.x**

_No external libraries are required; this solution uses only Python's standard libraries._

### Running the Code
1. Save the code in a file, for example `path_finder.py`.
2. Open a terminal and navigate to the directory containing the file.
3. Run the script with:
   
   ```bash
   python path_finder.py
   
The code includes a test example. You can change the list by modifying the test_strs variable in the __main__ block. Underlining in the binary strings is not required.

#### Example node-and-path declaration
```python3
# Pre-defined transitions for the 4 given nodes.
# Format: node: { two-bit input : (destination, output) }
DEFINED_TRANSITIONS = {
    'S0': {'01': ('S1', '1'), '11': ('S1', '0'), '10': ('S2', '0')},
    'S1': {'01': ('S3', '1')},
    'S2': {'00': ('S3', '1'), '11': ('S1', '0'), '10': ('S3', '0')},
    'S3': {'01': ('S0', '1')}
}
```

#### Example binary string
```python3
test_strs = [
        "001_010_010_101_100_001_110_110",
        "111_010_000_100_110_101_110_000",
    ]
```

#### Example Output
```
------------------------------
Testing case 1:
001_010_010_101_100_001_110_110

Extra Cost = 5
Extra Path = 4
Extra Node = 1
Path:
S1 --(00/1)--> N1 (extra, new node)
N1 --(01/0)--> N1 (extra)
N1 --(01/0)--> N1
N1 --(10/1)--> S0 (extra)
S0 --(10/0)--> S2
S2 --(00/1)--> S3
S3 --(11/0)--> S3 (extra)
S3 --(11/0)--> S3
```
This output indicates that the minimum extra cost to process the input string is 5, achieved by adding 4 extra transitions and an extra node.

## Code Structure
- `DEFINED_TRANSITIONS`: Contains the predefined transitions for nodes `S0`, `S1`, `S2`, and `S3`.

- `dfs` Function: Implements the DFS with memoization, tracking state parameters such as the current step, current node, extra transitions, and the new node count.

- `solve` Function: Processes the given binary string, calls the DFS, and prints the results.

- `__main__` Block: Entry point for testing the algorithm with a sample binary string.

## License 
This project is provided "as is" without any warranty. You are free to use it for educational or personal purposes.

## Author
Tang, You-Zeng. (Email: christang426849@gmail.com)
