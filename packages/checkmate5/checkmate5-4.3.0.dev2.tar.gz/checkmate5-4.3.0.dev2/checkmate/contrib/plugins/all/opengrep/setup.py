from .analyzer import OpengrepAnalyzer
from .issues_data import issues_data

analyzers = {
    'opengrep':
        {
            'name': 'opengrep',
            'title': 'opengrep',
            'class': OpengrepAnalyzer,
            'language': 'all',
            'issues_data': issues_data,
        },
}
