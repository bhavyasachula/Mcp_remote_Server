from fastmcp import FastMCP
import os
import sqlite3

""""Use a guaranteed writable location"""
DB_PATH = os.path.join(os.path.expanduser("~"), "Expense_db.db")

mcp = FastMCP(name="Expense_Tracker")

def init_db():
    with sqlite3.connect(DB_PATH) as c:
        c.execute("""
                    CREATE TABLE IF NOT EXISTS expense(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    amount INTEGER NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT DEFAULT '',
                    note TEXT DEFAULT '')""")
        c.commit()

init_db()

@mcp.tool()
def add_expense(date, amount, category, subcategory, note):
    """Add expenses into the database."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute(
            """INSERT INTO expense (date, amount, category, subcategory, note) VALUES (?, ?, ?, ?, ?)""",
            (date, amount, category, subcategory, note)
        )
        c.commit()
        return {
            "status": "ok",
            "row_id": cur.lastrowid
        }

@mcp.tool()
def list_expense(start_date, end_date):
    """List all expenses from the database within an inclusive date range."""
    with sqlite3.connect(DB_PATH) as c:
        cur = c.execute("""
        SELECT id, date, amount, category, subcategory, note
        FROM expense
        WHERE date BETWEEN ? AND ?
        ORDER BY date, id
        """, (start_date, end_date))
        cols = [col[0] for col in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

@mcp.tool()
def summarize(start_date, end_date, category=None):
    """Summarize expenses by category within an inclusive date range"""
    with sqlite3.connect(DB_PATH) as c:
        query = """
        SELECT category, SUM(amount) AS total_amount
        FROM expense
        WHERE date BETWEEN ? AND ?
        """
        params = [start_date, end_date]
        if category:
            query += " AND category = ?"
            params.append(category)
        query += " GROUP BY category ORDER BY category ASC"
        cur = c.execute(query, params)
        cols = [col[0] for col in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)