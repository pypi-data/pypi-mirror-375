# -*- coding: utf-8 -*-
"""
Module for combining xlizard and SourceMonitor metrics
"""
from typing import Dict, List, Optional

class CombinedMetrics:
    def __init__(self, xlizard_data, sm_metrics: Optional[Dict] = None):
        self.xlizard = xlizard_data
        self.sourcemonitor = sm_metrics or {
            'comment_percentage': 0,
            'max_block_depth': 0,
            'pointer_operations': 0,
            'preprocessor_directives': 0,
            'logical_operators': 0,
            'conditional_statements': 0,
            'lines_of_code': 0,
            'comment_lines': 0,
            'total_lines': 0
        }
        
    @property
    def filename(self):
        return self.xlizard.filename
        
    @property
    def functions(self):
        return self.xlizard.function_list
        
    @property
    def basename(self):
        return self.xlizard.filename.split('/')[-1]
        
    @property
    def dirname(self):
        dirs = self.xlizard.filename.split('/')[:-1]
        return '/'.join(dirs) if dirs else "Project Files"
        
    @property
    def comment_percentage(self):
        return self.sourcemonitor.get('comment_percentage', 0)
        
    @property
    def max_block_depth(self):
        return self.sourcemonitor.get('max_block_depth', 0)
        
    @property
    def pointer_operations(self):
        return self.sourcemonitor.get('pointer_operations', 0)
        
    @property
    def preprocessor_directives(self):
        return self.sourcemonitor.get('preprocessor_directives', 0)
        
    @property
    def logical_operators(self):
        return self.sourcemonitor.get('logical_operators', 0)
        
    @property
    def conditional_statements(self):
        return self.sourcemonitor.get('conditional_statements', 0)
        
    @property
    def lines_of_code(self):
        return self.sourcemonitor.get('lines_of_code', 0)
        
    @property
    def comment_lines(self):
        return self.sourcemonitor.get('comment_lines', 0)
        
    @property
    def total_lines(self):
        return self.sourcemonitor.get('total_lines', 0)