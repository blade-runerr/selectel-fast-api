from prometheus_client import Counter, Histogram

parse_runs_total = Counter(
    "parse_runs_total",
    "Total number of parse job runs",
    ["status"],
)
parse_errors_total = Counter(
    "parse_errors_total",
    "Total number of parse job errors",
)
parsed_vacancies_total = Counter(
    "parsed_vacancies_total",
    "Total number of newly created vacancies from parser",
)
parse_duration_seconds = Histogram(
    "parse_duration_seconds",
    "Duration of parse job execution",
)
