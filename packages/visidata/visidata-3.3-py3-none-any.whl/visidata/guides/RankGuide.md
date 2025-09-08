# Ranking

Ranking assigns numeric ranks to rows based on column values. VisiData provides two ranking approaches: sheet-wide ranking and group-based ranking.

## Sheet-wide ranking

[:keys]addcol-sheetrank[/] ranks all rows across the entire sheet.

Navigate to the column to rank by and execute [:keys]addcol-sheetrank[/]. A new column appears with ranks, where 1 indicates the best value.

**Example:**
```
Name   | Salary | Salary_rank
Alice  | 95000  | 1
Bob    | 85000  | 2
Carol  | 70000  | 3
```

## Group-based ranking

[:keys]addcol-aggregate[/] with [:code]rank[/] aggregator ranks rows within groups defined by key columns.

1. Set key columns with [:keys]![/] (defines groups)
2. Navigate to the column to rank by
3. Execute [:keys]addcol-aggregate[/] 
4. Select [:code]rank[/] aggregator

**Example with Department as key column:**
```
Name   | Department  | Salary | Salary_rank
Alice  | Engineering | 95000  | 1
Bob    | Engineering | 85000  | 2
Carol  | Sales       | 70000  | 1
Dave   | Sales       | 65000  | 2
```

Alice and Carol both receive rank 1 as the highest earners in their respective departments.

## Sort direction

Ranking follows the current sort direction of the column:
- Ascending sort: lower values get better ranks
- Descending sort: higher values get better ranks

## Usage patterns

**Global comparison:** Use [:keys]addcol-sheetrank[/] to find overall leaders across all data.

**Category comparison:** Use [:keys]addcol-aggregate[/] + [:code]rank[/] to find leaders within each group defined by key columns.

**Multiple groupings:** Set multiple key columns before group ranking for complex categorization.
