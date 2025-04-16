import argparse
from logs_analyzer import HandlersReport
import concurrent.futures as cf

def process_log_file(filepath: str):
    analyzer = HandlersReport()
    analyzer.process_log_file(file_path=filepath)
    return analyzer

def main():
    parser = argparse.ArgumentParser(description='Django log analyzer')
    parser.add_argument('logfiles', nargs='+', help='Logs paths')
    parser.add_argument('--report', required=True, help='Name of report')

    args = parser.parse_args()

    with cf.ProcessPoolExecutor() as executor:
        analyzers = list(executor.map(process_log_file, args.logfiles))

    main_analyzer = analyzers[0]
    for analyzer in analyzers[1:]:
        main_analyzer.merge_other_handler(analyzer)

    print(main_analyzer.print_info())

if __name__ == "__main__":
    main()