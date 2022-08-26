# ptypysql
> A Python String SQL Formatter / Beautifier, built for PostgreSQL


## How to install

Clone the repository and run

`python setup.py install`

## How to use

Currently it only supports for SQL in string format as `"""..."""` (Not work with`"..."`), and wrap by a function `DB.fetch_*(`, e.g.,

`DB.fetch_all("""select * from table1 where id = 1""")`

You can format SQL queries in python script via the command line

`ptypysql sql.py`

or format all your SQL queries in all python scripts under the same directory via

`ptypysql *.py`

Or even format all your SQL queries in the project recursively use

`ptypysql -r "*.py"`

### Controlling maximum length line via truncation

The `ptypysql` will try to truncate too long lines based on the setting of max-line-length.

By default the maximum line length is 99.

You can control the maximum line length by:

`ptypysql sql.py --max-line-length=50`

### Usage with `pre-commit`

Add `ptypysql` as a hook to your `pre-commit` configuration to format your SQL files before commit, just add the following lines to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/snapADDY/ptypysql
    rev: master
    hooks:
    - id: ptypysql
```

If you want to install `ptypysql` locally and use that instead of using `pre-commit`'s default environment, set `repo: local` in your `.pre-commit-config.yaml` file:

```yaml
repos:
  - repo: local
    hooks:
    - id: ptypysql
      name: Pretty Python SQL
      language: system
      entry: ptypysql
      files: \.py$
```

or

```yaml
repos:
  - repo: local
    hooks:
    - id: ptypysql
      name: Pretty Python SQL
      language: system
      entry: ptypysql --max-line-length=50
      files: \.py$
```

for a custom maximum line length truncation of e.g. 50

### Usage in Python

You can easily format the SQL string with two parameters to set the maximum line length and add semicolon by:

```python
example_sql = """
WITH days AS (SELECT generate_series(date_trunc('day', now()) - '90 days'::interval, date_trunc('day', now()), '1 day'::interval) AS day)
select days.day as date, count(t1.id) count, count(t2.id) filter (where t2.id < 500)
from days full outer join (select * from t3 where accd between 1 and 64) t1 on t1.date = days.day
natural left join t2 on t2.enddate = days.day
group by days.day desc having days.day > 100 order by days.day desc
"""
```

```python
from ptypysql.core import format_sql
print(format_sql(example_sql, max_len=99, semicolon=True))
```

    WITH days AS (
        SELECT generate_series(
            date_trunc('day', now()) - '90 days'::interval,
            date_trunc('day', now()),
            '1 day'::interval
        ) AS day
    )
    SELECT days.day AS date,
        count(t1.id) AS count,
        count(t2.id) FILTER (
            WHERE t2.id < 500
        )
    FROM days
        FULL OUTER JOIN (
            SELECT *
            FROM t3
            WHERE accd BETWEEN 1 AND 64
        ) AS t1
            ON t1.date = days.day
        NATURAL LEFT JOIN t2
            ON t2.enddate = days.day
    GROUP BY days.day DESC
    HAVING days.day > 100
    ORDER BY days.day DESC;


You can also add `/*skip-formatter*/` to prevent from foramtting

```python
from ptypysql.format_file import format_sql_commands
print(format_sql_commands(
"""
/*skip-formatter*/
WITH days AS (SELECT generate_series(date_trunc('day', now()) - '90 days'::interval, date_trunc('day', now()), '1 day'::interval) AS day)
select days.day as date, count(t1.id) count, count(t2.id) filter (where t2.id < 500) 
from days full outer join (select * from t3 where accd between 1 and 64) t1 on t1.date = days.day
natural left join t2 on t2.enddate = days.day
group by days.day desc having days.day > 100 order by days.day desc;
"""
))
```

    /*skip-formatter*/
    WITH days AS (SELECT generate_series(date_trunc('day', now()) - '90 days'::interval, date_trunc('day', now()), '1 day'::interval) AS day)
    select days.day as date, count(t1.id) count, count(t2.id) filter (where t2.id < 500) 
    from days full outer join (select * from t3 where accd between 1 and 64) t1 on t1.date = days.day
    natural left join t2 on t2.enddate = days.day
    group by days.day desc having days.day > 100 order by days.day desc;
    


## Credit

This project makes use of and is based on:

- [SQL-formatter](https://github.com/PabloRMira/sql_formatter)
