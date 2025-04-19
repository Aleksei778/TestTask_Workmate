import argparse
import concurrent.futures as cf
from typing import List
import os

from logs_analyzer import HandlersReport

def process_log_file(filedata):
    filepath, report_class = filedata
    analyzer = report_class()
    analyzer.process_log_file(file_path=filepath)
    return analyzer

def validate_file_paths(file_paths: List[str]) -> List[str]:
    missing_files = [f for f in file_paths if not os.path.exists(f)]
    return missing_files
        
def main():
    available_reports = {
        "handlers": HandlersReport
    }

    parser = argparse.ArgumentParser(description='Django log analyzer')
    parser.add_argument('logfiles', required=True, nargs='+', help='Logs paths')
    parser.add_argument('--report', required=True, choices=available_reports.keys(), help='Name of report')

    args = parser.parse_args()

    missing_files = validate_file_paths(args.logfiles)
    
    if missing_files:
        print(f"Следующие файлы не найдены: {", ".join(missing_files)}! Они не будут учитываться при обработке!")
        args.logfiles = [f for f in args.logfiles if f not in missing_files]

    report_class = available_reports[args.report]
    file_data = [(filepath, report_class) for filepath in args.logfiles]

    with cf.ProcessPoolExecutor() as executor:
        analyzers = list(executor.map(process_log_file, file_data))

    main_analyzer = analyzers[0]
    for analyzer in analyzers[1:]:
        main_analyzer.merge_results(analyzer)

    print(main_analyzer.generate_report())

if __name__ == "__main__":
    main()