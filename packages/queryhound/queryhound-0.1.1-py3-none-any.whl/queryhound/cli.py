import argparse
import json
from datetime import datetime
from statistics import mean, median, quantiles
from collections import defaultdict
from tabulate import tabulate
import csv
import sys
import re


def parse_date(date_str):
    formats = [
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d"
    ]
    for fmt in formats:
        try:
            if fmt.endswith("%z") and "+00:00" not in date_str and "-" not in date_str[-6:]:
                date_str += "+00:00"
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}")


def parse_log_line(line):
    try:
        entry = json.loads(line)
        timestamp = entry.get("t", {}).get("$date")
        if timestamp:
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

        attr = entry.get("attr", {})
        ns = attr.get("ns")
        ms = attr.get("durationMillis") or attr.get("ms")
        query = attr.get("query") or attr.get("filter")
        plan = attr.get("planSummary")
        command = entry.get("msg", "")
        app_name = attr.get("appName", "")
        keys_examined = attr.get("keysExamined", 0)
        docs_examined = attr.get("docsExamined", 0)
        nreturned = attr.get("nreturned", 0)
        remote_ip = attr.get("remote", "")
        if remote_ip:
            remote_ip = remote_ip.split(":")[0]
        app_name_cleaned = re.sub(r" v[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+", "", app_name)
        app_name_cleaned = re.sub(r"\s*\(.*\)", "", app_name_cleaned)

        operation = "Unknown"
        if 'find' in command.lower():
            operation = "Find"
        elif 'insert' in command.lower():
            operation = "Insert"
        elif 'update' in command.lower():
            operation = "Update"
        elif 'delete' in command.lower():
            operation = "Delete"

        return {
            'timestamp': timestamp,
            'namespace': ns,
            'ms': ms,
            'query': query,
            'plan': plan,
            'command': command,
            'operation': operation,
            'app_name': app_name_cleaned,
            'keys_examined': keys_examined,
            'docs_examined': docs_examined,
            'nreturned': nreturned,
            'line': line.strip(),
            'remote_ip': remote_ip
        }

    except json.JSONDecodeError:
        return None


def is_within_date(timestamp, start_date, end_date):
    if not timestamp:
        return False
    if start_date and timestamp < start_date:
        return False
    if end_date and timestamp > end_date:
        return False
    return True


def process_log(file_path, args):
    results = defaultdict(lambda: {'ms_list': [], 'count': 0, 'plan': '', 'namespace': '', 'operation': '', 'app_name': '', 'keys_examined': 0, 'docs_examined': 0, 'nreturned': 0, 'remote_ip': ''})
    log_lines = []

    with open(file_path, 'r') as f:
        for line in f:
            if args.filter and not any(m.lower() in line.lower() for m in args.filter):
                continue

            entry = parse_log_line(line)
            if not entry:
                continue

            if not is_within_date(entry['timestamp'], args.start_date, args.end_date):
                continue
            if args.min_ms is not None and (entry['ms'] is None or entry['ms'] < args.min_ms):
                continue
            if args.scan and entry['plan'] != "COLLSCAN":
                continue
            if args.slow and (entry['ms'] is None or entry['ms'] < 100):
                continue
            if args.namespace and args.namespace != entry['namespace']:
                continue
            if entry['ms'] is None:
                continue
            if args.connections and entry['operation'] == "Connection":
                continue

            key = (entry['operation'], entry['plan'], entry['namespace'], str(entry['query']))
            results[key]['ms_list'].append(entry['ms'])
            results[key]['count'] += 1
            results[key]['plan'] = entry['plan']
            results[key]['namespace'] = entry['namespace']
            results[key]['operation'] = entry['operation']
            results[key]['app_name'] = entry['app_name']
            results[key]['keys_examined'] += entry['keys_examined']
            results[key]['docs_examined'] += entry['docs_examined']
            results[key]['nreturned'] += entry['nreturned']
            results[key]['remote_ip'] = entry['remote_ip']

            if args.filter:
                log_lines.append(entry['line'])

    return results, log_lines


def summarize_results(results, pvalue=None, include_pstats=False):
    table = []

    for (operation, plan, namespace, query), data in results.items():
        ms_list = data['ms_list']
        count = data['count']
        if not ms_list:
            continue

        row = [operation, plan]
        if pvalue and pvalue.lower() == 'p50':
            row.append(round(median(ms_list), 2))

        avg_ms = round(mean(ms_list), 2)
        row.append(avg_ms)
        row.extend([
            data['keys_examined'],
            data['docs_examined'],
            data['nreturned']
        ])

        if include_pstats or (pvalue and pvalue.lower() in ['p75', 'p90', 'p99']):
            try:
                q = quantiles(ms_list, n=100)
            except:
                q = []

            if include_pstats or (pvalue and pvalue.lower() == 'p75'):
                row.append(q[74] if len(q) > 74 else '-')
            if include_pstats or (pvalue and pvalue.lower() == 'p90'):
                row.append(q[89] if len(q) > 89 else '-')
            if include_pstats or (pvalue and pvalue.lower() == 'p99'):
                row.append(q[98] if len(q) > 98 else '-')

        row.extend([
            data['operation'],
            count,
            data['app_name']
        ])
        table.append(row)

    return table


def write_csv(output_file, data, headers):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(data)


def main():
    parser = argparse.ArgumentParser(description="QueryHound - MongoDB Log Filter Tool")
    parser.add_argument("logfile", help="Path to MongoDB JSON log file")
    parser.add_argument("--scan", action="store_true", help="Only show COLLSCAN queries")
    parser.add_argument("--slow", action="store_true", help="Only show slow queries (ms >= 100)")
    parser.add_argument("--start-date", type=str, help="Start date (ISO 8601 or 'YYYY-MM-DD')")
    parser.add_argument("--end-date", type=str, help="End date (ISO 8601 or 'YYYY-MM-DD')")
    parser.add_argument("--namespace", type=str, help="Filter by namespace (db.collection)")
    parser.add_argument("--min-ms", type=int, help="Minimum duration (ms)")
    parser.add_argument("--pstats", action="store_true", help="Include P75, P90, P99 stats")
    parser.add_argument("--pvalue", type=str, choices=['P50', 'P75', 'P90', 'P99'], help="Specify a specific p-stat to include")
    parser.add_argument("--output-csv", type=str, help="Write output to CSV")
    parser.add_argument("--filter", nargs='*', type=str, help="Search for lines containing any of the specified strings")
    parser.add_argument("--connections", action="store_true", help="Displays connection count")

    args = parser.parse_args()

    try:
        args.start_date = parse_date(args.start_date) if args.start_date else None
        args.end_date = parse_date(args.end_date) if args.end_date else None
    except ValueError as e:
        print(f"Date parsing error: {e}")
        sys.exit(1)

    try:
        results, log_lines = process_log(args.logfile, args)

        table = []
        headers = []

        if results and (args.scan or args.slow or args.pstats or args.pvalue):
            table = summarize_results(results, pvalue=args.pvalue, include_pstats=args.pstats)
            if table:
                headers = ["Operation", "Plan"]
                if args.pvalue and args.pvalue.lower() == 'p50':
                    headers.append("P50")
                headers += ["Avg ms", "Keys Examined", "Docs Examined", "NReturned"]
                if args.pstats or (args.pvalue and args.pvalue.lower() in ['p75', 'p90', 'p99']):
                    if args.pstats or (args.pvalue and args.pvalue.lower() == 'p75'):
                        headers.append("P75")
                    if args.pstats or (args.pvalue and args.pvalue.lower() == 'p90'):
                        headers.append("P90")
                    if args.pstats or (args.pvalue and args.pvalue.lower() == 'p99'):
                        headers.append("P99")
                headers += ["Operation Type", "Count", "App Name"]

                print("\nSummary Table:")
                print(tabulate(table, headers=headers, tablefmt="pretty"))

        if args.filter and log_lines:
            print("\nMatching Log Lines:")
            for line in log_lines:
                print(line)

        if args.output_csv and table:
            write_csv(args.output_csv, table, headers)

    except Exception as e:
        print(f"Error processing the log file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    
def run():
    main()