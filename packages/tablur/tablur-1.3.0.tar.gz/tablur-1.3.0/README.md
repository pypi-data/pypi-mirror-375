# tablur

<div align="center">
  <img src="https://raw.githubusercontent.com/durocodes/tablur/main/logo.png" width="400" />
</div>

a simple python library for creating beautifully formatted tables with box-drawing characters.

## features

- **simple interface**: use `tablur()` and `simple()` functions
- create tables with box-drawing characters (╭─╮│├┼┤┴╰)
- support for optional headers and footers
- automatic column width calculation
- four input formats: column-based, dictionary, list of dictionaries, and row-based
- returns formatted strings (no automatic printing)
- lightweight and blazingly fast

## installation

```bash
pip install tablur
```

## usage

### column-based format (default)

```python
from tablur import tablur

# data is defined as a list of tuples where each tuple contains `(column_name, column_data)`
data = [
    ("Name", ["Alice", "Bob", "Charlie"]),
    ("Age", [25, 30, 35]),
    ("City", ["New York", "London", "Tokyo"]),
    ("Salary", [50000, 60000, 70000]),
]

# using the `tablur` function
table = tablur(
    data,
    header="Employee Directory",
    footer="Total: 3 employees",
    chars=["╭", "╮", "╰", "╯", "├", "┤", "┬", "┴", "┼", "─", "│"] # this is the default, make sure you use this format
)
print(table)
```

output:

```
╭───────────────────────────────────╮
│        Employee Directory         │
├─────────┬─────┬──────────┬────────┤
│ Name    │ Age │ City     │ Salary │
├─────────┼─────┼──────────┼────────┤
│ Alice   │ 25  │ New York │ 50000  │
│ Bob     │ 30  │ London   │ 60000  │
│ Charlie │ 35  │ Tokyo    │ 70000  │
├─────────┴─────┴──────────┴────────┤
│        Total: 3 employees         │
╰───────────────────────────────────╯
```

### dictionary format

```python
from tablur import tablur

# data can also be a dictionary where keys are column names and values are lists of data
data = {
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["New York", "London", "Tokyo"],
    "Salary": [50000, 60000, 70000],
}

# using the `tablur` function with dictionary
table = tablur(
    data,
    header="Employee Directory",
    footer="Total: 3 employees"
)
print(table)
```

output:

```
╭───────────────────────────────────╮
│        Employee Directory         │
├─────────┬─────┬──────────┬────────┤
│ Name    │ Age │ City     │ Salary │
├─────────┼─────┼──────────┼────────┤
│ Alice   │ 25  │ New York │ 50000  │
│ Bob     │ 30  │ London   │ 60000  │
│ Charlie │ 35  │ Tokyo    │ 70000  │
├─────────┴─────┴──────────┴────────┤
│        Total: 3 employees         │
╰───────────────────────────────────╯
```

### list of dictionaries format

```python
from tablur import tablur

# data is a list of dictionaries where each dictionary represents a row
data = [
    {"Name": "Alice", "Age": 25, "City": "New York", "Salary": 50000},
    {"Name": "Bob", "Age": 30, "City": "London", "Salary": 60000},
    {"Name": "Charlie", "Age": 35, "City": "Tokyo", "Salary": 70000}
]

# using the `tablur` function with list of dictionaries
table = tablur(
    data,
    header="Employee Directory",
    footer="Total: 3 employees"
)
print(table)
```

output:

```
╭───────────────────────────────────╮
│        Employee Directory         │
├─────┬──────────┬─────────┬────────┤
│ Age │ City     │ Name    │ Salary │
├─────┼──────────┼─────────┼────────┤
│ 25  │ New York │ Alice   │ 50000  │
│ 30  │ London   │ Bob     │ 60000  │
│ 35  │ Tokyo    │ Charlie │ 70000  │
├─────┴──────────┴─────────┴────────┤
│        Total: 3 employees         │
╰───────────────────────────────────╯
```

> [!NOTE]
> When using list of dictionaries, columns appear in the order they first appear in the data. Missing keys in any dictionary will be filled with empty strings.

### row-based format

```python
from tablur import simple

# data is just a list of rows, where each row is a list of values
data = [
    ["Alice", 25, "New York"],
    ["Bob", 30, "London"],
    ["Charlie", 35, "Tokyo"]
]

# with simple, you can define the headers explicitly or not (they default to indices)
table = simple(data, headers=["Name", "Age", "City"])
print(table)
```

> [!NOTE]
> The `simple()` function also supports dictionary format and list of dictionaries, just like `tablur()`.

output:

```
╭─────────┬─────┬──────────╮
│ Name    │ Age │ City     │
├─────────┼─────┼──────────┤
│ Alice   │ 25  │ New York │
│ Bob     │ 30  │ London   │
│ Charlie │ 35  │ Tokyo    │
╰─────────┴─────┴──────────╯
```

### pandas support

tablur has built-in support for pandas DataFrames. you can pass a DataFrame directly to either `tablur()` or `simple()` functions.

```python
import pandas as pd
from tablur import tablur

df = pd.DataFrame({
    "Product": ["Laptop", "Mouse", "Keyboard", "Monitor"],
    "Price": [999.99, 29.99, 79.99, 299.99],
    "Stock": [15, 50, 30, 8],
    "Category": ["Electronics", "Accessories", "Accessories", "Electronics"]
})

table = tablur(df, header="Inventory Report", footer="Total: 4 products")
print(table)
```

output:

```
╭─────────────────────────────────────────╮
│            Inventory Report             │
├──────────┬────────┬───────┬─────────────┤
│ Product  │ Price  │ Stock │ Category    │
├──────────┼────────┼───────┼─────────────┤
│ Laptop   │ 999.99 │ 15    │ Electronics │
│ Mouse    │ 29.99  │ 50    │ Accessories │
│ Keyboard │ 79.99  │ 30    │ Accessories │
│ Monitor  │ 299.99 │ 8     │ Electronics │
├──────────┴────────┴───────┴─────────────┤
│            Total: 4 products            │
╰─────────────────────────────────────────╯
```

> [!NOTE]
> pandas is an optional dependency

## license

mit, you can do whatever you want with the code :D
