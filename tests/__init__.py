import os
from coverage import Coverage


def teardown():
    if os.environ['run_coverage'] == 'True':
        coverage = Coverage(data_file='*')
        coverage.combine(['coverage_reports'],True)
        coverage.html_report()
