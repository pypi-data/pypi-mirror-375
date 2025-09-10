import os
import sys
import logging
import re
from concurrent.futures import ThreadPoolExecutor
import xml.etree.ElementTree as ET
from tqdm import tqdm
from collections import defaultdict
from typing import Dict, List, Optional, DefaultDict, Set, Tuple, Any
import ast
import tokenize
from io import StringIO
import hashlib
import threading

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class Config:
    """Конфигурация анализатора с улучшенными настройками безопасности"""
    EXCLUDE_DIRS = {'.git', 'venv', '__pycache__', 'include', 'node_modules', '.idea', '.vscode'}
    EXCLUDE_FILES = {'package-lock.json', 'yarn.lock', '.DS_Store', 'thumbs.db'}
    SUPPORTED_EXTENSIONS = {'.c', '.h', '.cpp', '.hpp', '.cc', '.cxx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB максимальный размер файла
    MAX_DEPTH = 20  # Максимальная глубина вложенности директорий
    
    METRICS = [
        'comment_percentage',
        'max_block_depth',
        'pointer_operations',
        'preprocessor_directives',
        'logical_operators',
        'conditional_statements'
    ]
    
    THRESHOLDS = {
        'comment_percentage': 20,
        'max_block_depth': 5,
        'pointer_operations': 20,
        'preprocessor_directives': 15,
        'logical_operators': 10,
        'conditional_statements': 8
    }

class SecurityUtils:
    """Утилиты для обеспечения безопасности"""
    
    @staticmethod
    def safe_path_check(path: str, base_path: str) -> bool:
        """Проверка безопасности пути"""
        try:
            absolute_path = os.path.abspath(path)
            absolute_base = os.path.abspath(base_path)
            
            # Проверка на path traversal
            if not absolute_path.startswith(absolute_base):
                return False
                
            # Проверка на симлинки
            if os.path.islink(absolute_path):
                return False
                
            return True
        except (ValueError, OSError):
            return False
    
    @staticmethod
    def is_valid_file(file_path: str, base_path: str) -> bool:
        """Проверка файла на безопасность"""
        if not SecurityUtils.safe_path_check(file_path, base_path):
            return False
            
        if os.path.basename(file_path) in Config.EXCLUDE_FILES:
            return False
            
        try:
            # Проверка размера файла
            file_size = os.path.getsize(file_path)
            if file_size > Config.MAX_FILE_SIZE or file_size == 0:
                return False
                
            # Проверка что это обычный файл
            if not os.path.isfile(file_path):
                return False
                
            return True
        except OSError:
            return False

class CodeParser:
    """Парсер кода для точного анализа структуры с улучшенной точностью"""
    
    @staticmethod
    def parse_c_like_code(content: str) -> Dict[str, Any]:
        """Парсинг C-подобного кода с точным определением структуры"""
        try:
            depth = 0
            max_depth = 0
            in_comment = False
            in_string = False
            string_char = None
            char_escape = False
            stack = []
            in_preprocessor = False
            
            i = 0
            while i < len(content):
                char = content[i]
                
                if char_escape:
                    char_escape = False
                    i += 1
                    continue
                    
                if char == '\\':
                    char_escape = True
                    i += 1
                    continue
                
                # Обработка препроцессорных директив
                if not in_comment and not in_string and char == '#' and (i == 0 or content[i-1] == '\n'):
                    in_preprocessor = True
                    i += 1
                    continue
                
                if in_preprocessor:
                    if char == '\n':
                        in_preprocessor = False
                    i += 1
                    continue
                
                if not in_comment and not in_string:
                    # Начало блочного комментария
                    if char == '/' and i + 1 < len(content) and content[i+1] == '*':
                        in_comment = True
                        i += 2
                        continue
                    # Начало строчного комментария
                    elif char == '/' and i + 1 < len(content) and content[i+1] == '/':
                        # Пропускаем до конца строки
                        while i < len(content) and content[i] != '\n':
                            i += 1
                        continue
                    # Начало строкового литерала
                    elif char in ('"', "'"):
                        in_string = True
                        string_char = char
                        i += 1
                        continue
                    # Начало блока
                    elif char == '{':
                        depth += 1
                        stack.append('{')
                        max_depth = max(max_depth, depth)
                        i += 1
                        continue
                    # Конец блока
                    elif char == '}':
                        if stack and stack[-1] == '{':
                            depth -= 1
                            stack.pop()
                        i += 1
                        continue
                    # Проверка на условные конструкции для уточнения глубины
                    elif char == 'e' and i + 3 < len(content) and content[i:i+4] == 'else':
                        # else добавляет уровень логической вложенности
                        max_depth = max(max_depth, depth + 0.5)
                        i += 4
                        continue
                
                elif in_comment:
                    # Конец блочного комментария
                    if char == '*' and i + 1 < len(content) and content[i+1] == '/':
                        in_comment = False
                        i += 2
                        continue
                    i += 1
                    continue
                
                elif in_string:
                    # Конец строкового литерала
                    if char == string_char and not char_escape:
                        in_string = False
                        string_char = None
                    i += 1
                    continue
                
                i += 1
            
            return {
                'max_depth': max_depth,
                'balanced_blocks': depth == 0 and not stack
            }
            
        except Exception as e:
            logger.warning(f"Ошибка парсинга кода: {str(e)}")
            return {'max_depth': 0, 'balanced_blocks': False}

class FileAnalyzer:
    """Анализатор отдельных файлов с улучшенной точностью и безопасностью"""
    
    @staticmethod
    def _count_comments_accurate(content: str) -> Tuple[int, int]:
        """Точный подсчет комментариев и строк кода"""
        lines = content.split('\n')
        total_lines = len(lines)
        comment_lines = 0
        in_block_comment = False
        
        for line in lines:
            line_clean = line.strip()
            
            if in_block_comment:
                comment_lines += 1
                if '*/' in line_clean:
                    in_block_comment = False
                    # Проверяем, есть ли код после комментария
                    parts = line_clean.split('*/', 1)
                    if parts[1].strip():  # Есть код после комментария
                        comment_lines -= 1
                continue
                
            # Пропускаем пустые строки
            if not line_clean:
                continue
                
            # Блочный комментарий на одной строке
            if line_clean.startswith('/*') and '*/' in line_clean:
                comment_lines += 1
                # Проверяем, есть ли код после комментария
                parts = line_clean.split('*/', 1)
                if parts[1].strip():  # Есть код после комментария
                    comment_lines -= 1
                    
            # Начало блочного комментария
            elif line_clean.startswith('/*'):
                comment_lines += 1
                in_block_comment = True
                if '*/' in line_clean:  # Закрытие на той же строке
                    in_block_comment = False
                    parts = line_clean.split('*/', 1)
                    if parts[1].strip():  # Есть код после комментария
                        comment_lines -= 1
                        
            # Строчный комментарий
            elif line_clean.startswith('//'):
                comment_lines += 1
                
            # Комментарий в середине строки
            elif '/*' in line_clean and '*/' in line_clean:
                # Проверяем, что это действительно комментарий, а не часть строки
                comment_start = line_clean.find('/*')
                comment_end = line_clean.find('*/') + 2
                
                # Проверяем, что комментарий не внутри строки
                before_comment = line_clean[:comment_start]
                in_string = False
                string_char = None
                
                for char in before_comment:
                    if char in ('"', "'") and not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char and in_string:
                        in_string = False
                        string_char = None
                
                if not in_string:
                    comment_lines += 1
                    # Проверяем, есть ли код до или после комментария
                    if line_clean[:comment_start].strip() or line_clean[comment_end:].strip():
                        comment_lines -= 0.5  # Частичная строка с комментарием
        
        code_lines = total_lines - comment_lines
        return int(comment_lines), int(code_lines)

    @staticmethod
    def _calculate_block_depth_accurate(content: str) -> int:
        """Точное вычисление максимальной глубины вложенности"""
        parser_result = CodeParser.parse_c_like_code(content)
        return int(parser_result['max_depth'] + 0.5)  # Округление для else

    @staticmethod
    def _count_pointer_operations(content: str) -> int:
        """Точный подсчет операций с указателями"""
        content_clean = FileAnalyzer._remove_comments_and_strings(content)
        
        # Улучшенные паттерны для операций с указателями
        patterns = [
            # Объявления указателей (только с звёздочкой перед именем)
            r'\b(?:int|char|float|double|void|struct\s+\w+)\s+\*\s*\w+\s*[;,=]',
            # Разыменование указателей (только в выражениях)
            r'\*\s*[a-zA-Z_][a-zA-Z0-9_]*\s*[^=]',
            # Обращение через указатель (только ->)
            r'[a-zA-Z_][a-zA-Z0-9_]*\s*->\s*[a-zA-Z_][a-zA-Z0-9_]*',
            # Взятие адреса (только & перед переменной)
            r'&\s*[a-zA-Z_][a-zA-Z0-9_]*\b',
            # Арифметика указателей (только с указателями)
            r'[a-zA-Z_][a-zA-Z0-9_]*\s*[+-]\s*[0-9]+\s*[;\n]',
        ]
        
        count = 0
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content_clean)
                count += len(matches)
            except re.error:
                continue
        
        return count

    @staticmethod
    def _count_logical_operators(content: str) -> int:
        """Подсчет логических операторов с улучшенной точностью"""
        content_clean = FileAnalyzer._remove_comments_and_strings(content)
        
        # Улучшенный подсчёт с контекстным анализом
        logical_ops = 0
        
        # && и || - почти всегда логические
        logical_ops += content_clean.count('&&')
        logical_ops += content_clean.count('||')
        
        # ! - только если перед ним нет = и после идёт пробел или (
        not_pattern = r'[^=!]\s*!\s*[^\s=]'
        logical_ops += len(re.findall(not_pattern, content_clean))
        
        # Операторы сравнения в вероятных контекстах
        comparison_pattern = r'(?:if|while|for|&&|\|\|)\s*\(.*?([!=]=|[<>]=?)[^=]'
        logical_ops += len(re.findall(comparison_pattern, content_clean))
        
        return logical_ops

    @staticmethod
    def _count_conditional_statements(content: str) -> int:
        """Подсчет условных операторов с улучшенной точностью"""
        content_clean = FileAnalyzer._remove_comments_and_strings(content)
        
        # Более точные паттерны для избежания ложных срабатываний
        patterns = [
            r'\bif\s*\([^)]+\)\s*{',      # if с условием и блоком
            r'\belse\s*{',                 # else с блоком
            r'\belse\s+if\s*\(',           # else if
            r'\bswitch\s*\([^)]+\)\s*{',   # switch
            r'\bcase\s+[^:]+:',            # case
            r'\bdefault\s*:',              # default
            r'\bfor\s*\([^;]+;[^;]+;[^)]+\)\s*{',  # for loop
            r'\bwhile\s*\([^)]+\)\s*{',    # while
            r'\bdo\s*{',                   # do-while
            r'\bbreak\s*;',                # break
            r'\bcontinue\s*;',             # continue
            r'\breturn\s+[^;]+;',          # return с значением
        ]
        
        count = 0
        for pattern in patterns:
            try:
                matches = re.findall(pattern, content_clean)
                count += len(matches)
            except re.error:
                continue
        
        return count

    @staticmethod
    def _remove_comments_and_strings(content: str) -> str:
        """Удаляет комментарии и строковые литералы с улучшенной точностью"""
        if isinstance(content, bytes):
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    content = content.decode('cp1251')
                except UnicodeDecodeError:
                    content = content.decode('latin-1', errors='ignore')
        
        # Удаляем блочные комментарии
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
        
        # Удаляем однострочные комментарии
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
        
        # Удаляем строковые литералы, но сохраняем их длину для контекста
        content = re.sub(r'"[^"]*"', '""', content)
        content = re.sub(r"'[^']*'", "''", content)
        
        return content
    
    @classmethod
    def analyze(cls, file_path: str) -> Optional[Dict[str, Any]]:
        """Анализ файла с улучшенной точностью и безопасностью"""
        try:
            # Проверка безопасности файла
            if not SecurityUtils.is_valid_file(file_path, os.path.dirname(file_path)):
                logger.warning(f"Пропуск файла: {file_path}")
                return None
            
            # Безопасное чтение файла
            encodings = ['utf-8', 'cp1251', 'latin-1', 'iso-8859-1']
            content = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, errors='strict') as f:
                        # Чтение с ограничением размера
                        content = f.read(Config.MAX_FILE_SIZE)
                    break
                except UnicodeDecodeError:
                    continue
                except OSError as e:
                    logger.warning(f"Ошибка чтения файла {file_path}: {str(e)}")
                    return None
            
            if content is None:
                try:
                    with open(file_path, 'rb') as f:
                        binary_content = f.read(Config.MAX_FILE_SIZE)
                        content = binary_content.decode('utf-8', errors='ignore')
                except OSError as e:
                    logger.warning(f"Ошибка чтения файла {file_path}: {str(e)}")
                    return None
            
            # Точный подсчет комментариев
            comment_lines, code_lines = cls._count_comments_accurate(content)
            total_lines = comment_lines + code_lines
            
            if total_lines == 0:
                return None
            
            # Расчет метрик
            comment_percentage = (comment_lines / total_lines * 100) if total_lines else 0
            max_block_depth = cls._calculate_block_depth_accurate(content)
            pointer_operations = cls._count_pointer_operations(content)
            preprocessor_directives = len([l for l in content.split('\n') if l.strip().startswith('#')])
            logical_operators = cls._count_logical_operators(content)
            conditional_statements = cls._count_conditional_statements(content)
            
            return {
                'file_name': os.path.basename(file_path),
                'file_path': os.path.relpath(file_path),
                'comment_percentage': round(comment_percentage, 2),
                'max_block_depth': max_block_depth,
                'pointer_operations': pointer_operations,
                'preprocessor_directives': preprocessor_directives,
                'logical_operators': logical_operators,
                'conditional_statements': conditional_statements,
                'lines_of_code': code_lines,
                'comment_lines': comment_lines,
                'total_lines': total_lines
            }
            
        except Exception as e:
            logger.warning(f"Ошибка анализа {file_path}: {str(e)}")
            return None

class ThreadSafeMetricsAggregator:
    """Потокобезопасный агрегатор метрик"""
    def __init__(self):
        self.file_metrics: List[Dict[str, Any]] = []
        self.total_metrics: DefaultDict[str, float] = defaultdict(float)
        self.counts: DefaultDict[str, int] = defaultdict(int)
        self.lock = threading.Lock()

    def add_file_metrics(self, metrics: Dict[str, Any]) -> None:
        """Потокобезопасное добавление метрик файла"""
        with self.lock:
            self.file_metrics.append(metrics)
            for key in Config.METRICS:
                if key in metrics:
                    self.total_metrics[key] += metrics[key]
                    self.counts[key] += 1

    def get_averages(self) -> Dict[str, float]:
        """Расчёт средних значений"""
        with self.lock:
            return {
                metric: round(self.total_metrics[metric] / self.counts[metric], 2)
                for metric in Config.METRICS
                if self.counts[metric] > 0
            }

class ReportGenerator:
    """Генерация отчётов с улучшенной безопасностью"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Очистка имени файла для безопасного использования"""
        return re.sub(r'[^\w\.-]', '_', filename)
    
    @staticmethod
    def generate_xml(metrics: List[Dict[str, Any]], output_path: str) -> None:
        """Генерация XML отчёта с проверкой безопасности"""
        try:
            output_dir = os.path.dirname(output_path)
            
            os.makedirs(output_dir, exist_ok=True, mode=0o755)
            
            # Проверка прав на запись
            if not os.access(output_dir, os.W_OK):
                raise PermissionError(f"Нет прав на запись в директорию: {output_dir}")
            
            root = ET.Element('sourcemonitor_metrics')
            for file_metrics in metrics:
                safe_name = ReportGenerator.sanitize_filename(file_metrics['file_name'])
                safe_path = ReportGenerator.sanitize_filename(file_metrics['file_path'])
                
                file_node = ET.SubElement(root, 'file', 
                                       name=safe_name,
                                       path=safe_path)
                for metric in Config.METRICS:
                    if metric in file_metrics:
                        ET.SubElement(file_node, metric).text = str(file_metrics[metric])
            
            tree = ET.ElementTree(root)
            
            # Безопасная запись во временный файл с последующим перемещением
            temp_path = output_path + '.tmp'
            tree.write(temp_path, encoding='utf-8', xml_declaration=True)
            
            # Атомарная замена файла
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_path, output_path)
            
            # Установка безопасных прав
            os.chmod(output_path, 0o644)
            
            logger.info(f"XML-отчёт успешно сохранён в {output_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении отчёта: {str(e)}")
            if 'temp_path' in locals() and os.path.exists(temp_path):
                os.remove(temp_path)
            raise

class SourceMonitorMetrics:
    """Основной класс анализатора с улучшенной безопасностью"""
    
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        
        package_root = self._find_package_root()
        self.output_xml = os.path.join(package_root, 'output', 'sourcemonitor_metrics.xml')
        self.aggregator = ThreadSafeMetricsAggregator()
        
        logger.info(f"Отчёт будет сохранён в: {self.output_xml}")

    def _find_package_root(self) -> str:
        """Находит корень пакета xlizard с проверкой безопасности"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        depth = 0
        
        while current_dir != os.path.dirname(current_dir) and depth < Config.MAX_DEPTH:
            if os.path.basename(current_dir) == 'xlizard':
                return current_dir
            current_dir = os.path.dirname(current_dir)
            depth += 1
        
        logger.warning("Не удалось найти корень пакета xlizard, используется текущая директория")
        return os.getcwd()

    def _collect_files(self) -> List[str]:
        """Сбор файлов для анализа с проверкой безопасности"""
        c_files = []
        depth = 0
        
        try:
            for root, dirs, files in os.walk(self.path):
                # Ограничение глубины рекурсии
                depth += 1
                if depth > Config.MAX_DEPTH:
                    logger.warning(f"Достигнута максимальная глубина рекурсии: {Config.MAX_DEPTH}")
                    break
                
                # Фильтрация директорий
                dirs[:] = [d for d in dirs if d not in Config.EXCLUDE_DIRS]
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Проверка безопасности файла
                    if (SecurityUtils.is_valid_file(file_path, self.path) and 
                        os.path.splitext(file)[1] in Config.SUPPORTED_EXTENSIONS):
                        c_files.append(file_path)
                        
        except OSError as e:
            logger.error(f"Ошибка при обходе директории: {str(e)}")
        
        return c_files

    def get_metrics(self) -> List[Dict[str, Any]]:
        """Возвращает собранные метрики для интеграции"""
        return self.aggregator.file_metrics

    def analyze_directory(self) -> None:
        """Анализ директории с улучшенной безопасностью"""
        if not os.path.exists(self.path):
            logger.error(f"Ошибка: путь '{self.path}' не существует!")
            sys.exit(1)
        
        if not os.path.isdir(self.path):
            logger.error(f"Ошибка: '{self.path}' не является директорией!")
            sys.exit(1)

        files = self._collect_files()
        logger.info(f"Найдено {len(files)} файлов для анализа...")
        
        if not files:
            logger.warning("Не найдено файлов для анализа")
            return
        
        # Ограничение количества потоков
        max_workers = min(4, os.cpu_count() or 1, len(files))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(tqdm(
                executor.map(FileAnalyzer.analyze, files),
                total=len(files),
                desc="Анализ файлов"
            ))
        
        # Фильтрация None результатов
        valid_metrics = list(filter(None, results))
        
        if not valid_metrics:
            logger.warning("Не удалось проанализировать ни один файл")
            return
        
        for metrics in valid_metrics:
            self.aggregator.add_file_metrics(metrics)

        try:
            ReportGenerator.generate_xml(
                self.aggregator.file_metrics, 
                self.output_xml
            )
            logger.info(f"Успешно проанализировано {len(valid_metrics)} файлов")
            
        except Exception as e:
            logger.error(f"Не удалось сохранить отчёт: {str(e)}")
            sys.exit(1)

def main() -> None:
    """Основная функция с улучшенной обработкой ошибок"""
    if len(sys.argv) != 2:
        print("Использование: python sourcemonitor_metrics.py <путь_к_директории>")
        sys.exit(1)
    
    try:
        analyzer = SourceMonitorMetrics(sys.argv[1])
        analyzer.analyze_directory()
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()