from IPython.core.magic import Magics, magics_class, line_magic, cell_magic
from IPython.core.display import HTML

import sqlite3
import requests
from html import escape


@magics_class
class ISQLite3(Magics):
    def __init__(self, shell):
        super().__init__(shell)
        self.conn = None
        self.conn = sqlite3.connect(":memory:", isolation_level=None)
        self.sql('', 'PRAGMA foreign_keys = ON')

    @line_magic
    def sql_open(self, line):
        line = line.strip()
        if line:
            if self.conn:
                self.conn.close()
                self.conn = None
            try:
                self.conn = sqlite3.connect(line, isolation_level=None)
                self.sql('', 'PRAGMA foreign_keys = ON')
            except sqlite3.DatabaseError as err:
                print(f"\x1b[31mError: {err}\x1b[0m")
        else:
            print("\x1b[31mError: missing filename\x1b[0m")

    @cell_magic
    def sql_script(self, line, cell):
        if not self.conn:
            print("\x1b[31mError: Not connected to any database\x1b[0m")
            return
        line = line.strip()
        if line:
            if "://" not in line:
                with open(line) as file:
                    script = file.read()
            else:
                with requests.get(line) as req:
                    script = req.text
            cursor = self.conn.cursor()
            try:
                cursor.executescript(script)
            except sqlite3.DatabaseError as err:
                print(f"\x1b[31mError: {err}\x1b[0m")
                return
            finally:
                cursor.close()
            print('Done!')
        elif cell.strip():
            cursor = self.conn.cursor()
            try:
                cursor.executescript(cell)
            except sqlite3.DatabaseError as err:
                print(f"\x1b[31mError: {err}\x1b[0m")
                return
            finally:
                cursor.close()
            print('Done!')
        else:
            print("\x1b[31mError: neither filename or URL supplied\x1b[0m")

    @cell_magic
    def sql(self, line, cell):
        if not self.conn:
            print("\x1b[31mError: Not connected to any database\x1b[0m")
            return
        cursor = self.conn.cursor()
        try:
            cursor.execute(cell)
            rows = cursor.fetchmany(101)
            description = cursor.description
        except sqlite3.DatabaseError as err:
            print(f"\x1b[31mError: {err}\x1b[0m")
            return
        except sqlite3.Warning as err:  # You can only execute one statement at a time.
            print(f"\x1b[31mError: {err}\x1b[0m")
            return
        finally:
            cursor.close()
        if len(rows) == 101:
            print("Showing only the first 100 rows")
        if description:
            html = '<table><thead><tr><th style="text-align: left">{}</th></tr></thead><tbody>'.format(
                '</th><th style="text-align: left">'.join(escape(col[0]) for col in description)
            )
            for row in rows[:100]:
                html += "<tr>"
                for cell in row:
                    if cell is None:
                        html += '<td></td>'
                    elif isinstance(cell, (int, float)):
                        html += '<td style="text-align: right">{}</td>'.format(cell)
                    else:
                        html += '<td style="text-align: left">{}</td>'.format(escape(str(cell)))
                html += "</tr>"
            html += "</tbody></table>"
            return HTML(html)
        print('Done!')


    @line_magic
    def sql_tables(self, line):
        return self.sql('', """\
SELECT name FROM sqlite_schema
WHERE type IN ("table", "view") AND name NOT LIKE "sqlite_%"
ORDER BY 1
""")

    @line_magic
    def sql_table(self, line):
        line = line.strip()
        if line:
            return self.sql('', """\
PRAGMA table_info("{}")
""".format(line.replace('"', '')))


def load_ipython_extension(ipython):
    ipython.register_magics(ISQLite3)
