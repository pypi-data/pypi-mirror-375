import sqlite3

HTML_FILE = "test_summary.html"

def generate_summary():
    """Creates an HTML summary of test runs."""
    with sqlite3.connect("results.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT config_name, success, start_time, end_time, log_file, error_trace FROM test_runs")
        results = cursor.fetchall()
    
    with open(HTML_FILE, "w") as f:
        f.write("<html><head><title>Test Summary</title></head><body>")
        f.write("<h1>Test Summary</h1>")
        f.write("<table border='1'><tr><th>Config</th><th>Success</th><th>Start</th><th>End</th><th>Log</th><th>Error</th></tr>")
        
        for row in results:
            config, success, start, end, log_file, error = row
            error_text = f"<pre>{error}</pre>" if error else "None"
            f.write(f"<tr><td>{config}</td><td>{'✅' if success else '❌'}</td><td>{start}</td><td>{end}</td>")
            f.write(f"<td><a href='{log_file}' target='_blank'>Log</a></td><td>{error_text}</td></tr>")
        
        f.write("</table></body></html>")
    
    print(f"Summary written to {HTML_FILE}")

if __name__ == "__main__":
    generate_summary()
