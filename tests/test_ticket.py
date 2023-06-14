import sqlite3

def test_database_existence():
    # Connect to the SQLite database
    try:
        conn = sqlite3.connect("ticket.db")
        cursor = conn.cursor()
        conn.close()
        assert True
    except:
        assert False, "The database does not exist."

def test_database_table():
    # Connect to the SQLite database
    conn = sqlite3.connect("ticket.db")
    cursor = conn.cursor()

    # Check if the table "ticketInfo" exists
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table' AND name='ticketInfo';")
    table_exists = cursor.fetchone() is not None

    # Close the connection
    conn.close()

    # Assert that the table exists
    assert table_exists, "The table does not exist."
