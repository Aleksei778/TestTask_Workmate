import argparse
from logs_analyzer import HandlersReport


def main():
    parser = argparse.ArgumentParser(description='Django log analyzer')
    parser.add_argument('logfiles', nargs='+', help='Logs paths')
    parser.add_argument('--report', required=True, help='Name of report')

    args = parser.parse_args()

    analyzers = []
    for filepath in args.logfiles:
        t = HandlersReport()
        t.process_log_file(file_path=filepath)
        analyzers.append(t)
    print(analyzers)
    analyzers[0].merge_other_handler(analyzers[1])
    for i in range(1, len(analyzers) - 1):
        analyzers[0].merge_other_handler(analyzers[i])
        print(analyzers[0].handlers)
    
    print(analyzers[0])
    print(analyzers[0].print_info())

if __name__ == "__main__":
    main()