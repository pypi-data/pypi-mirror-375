import csv
def generate_csv_report(data, filename='audit_report.csv'):
    if not data: return
    keys = data[0].keys()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for row in data: writer.writerow(row)
    print(f"Report saved as {filename}")