import os


class ExceptionFiles:

    def __init__(self, exception_files: list = None):
        if exception_files is None:
            exception_files = []
        self.__files = exception_files

    def get_exceptions(self):
        return self.__files

    def __add__(self, other):
        return ExceptionFiles(
            self.__files +
            [file for file in other._ExceptionFiles__files if file not in self.__files]
        )


class UnnecessaryFiles:

    def __init__(self, file_formats: list = None, patterns: dict = None):
        if file_formats is None:
            file_formats = []
        if patterns is None:
            patterns = {
                'startswith': [],
                'endswith': [],
                'includes': []
            }
        self.__file_formats = file_formats
        self.__patterns = patterns

    def __add__(self, other):
        temp_patterns = {key: (value + [pattern for pattern in other._UnnecessaryFiles__patterns[key]
                               if pattern not in value]) for (key, value) in self.__patterns.items()}
        return UnnecessaryFiles(
            self.__file_formats +
            [file for file in other._UnnecessaryFiles__file_formats if file not in self.__file_formats],
            temp_patterns
        )

    def get_file_format(self):
        return self.__file_formats

    def get_file_patterns(self, position: str):
        return self.__patterns[position]


class CompileUnnecessaryFile:

    def __init__(self, path: str):
        self.__STARTING_DIR, self.name = os.path.split(path)
        self.__compile_count = 0
        self.__exception_files = []
        self.__compiled_data = {
            'file_formats': [],
            'patterns': {
                'startswith': [],
                'endswith': [],
                'includes': []
            }
        }

    def compile_(self):
        self.__exception_files = []
        self.__compiled_data['file_formats'] = []
        for key in self.__compiled_data['patterns'].keys():
            self.__compiled_data['patterns'][key] = []

        with open(self.name) as read_file:
            data = read_file.read().strip()
            lines = data.splitlines()

        for line in lines:
            line = line.strip()

            if line.startswith('#') or not len(line):
                continue
            elif '#' in line:
                line = line[:line.find('#')]

            if line.startswith('!/'):
                self.__exception_files.append(line[2:])

            elif not line.startswith('*'):
                if line.startswith('/'):
                    self.__compiled_data['file_formats'].append(line[:-1])
                else:
                    self.__compiled_data['file_formats'].append(line[:-1])
                if line.endswith('*'):
                    self.__compiled_data['pattern']['startswith'].append(
                        line[:-1])
            else:
                if line.startswith('*.'):
                    self.__compiled_data['file_formats'].append(line[2:])
                elif line.endswith('*'):
                    self.__compiled_data['pattern']['includes'].append(
                        line[1:-1])
                else:
                    self.__compiled_data['pattern']['endswith'].append(
                        line[:-1])

        self.__compile_count += 1

    @property
    def exception_files(self):
        if self.__compile_count <= 0:
            self.compile_()
        return ExceptionFiles(
            self.__exception_files
        )

    @property
    def unnecessary_files(self):
        if self.__compile_count <= 0:
            self.compile_()
        return UnnecessaryFiles(
            self.__compiled_data['file_formats'],
            self.__compiled_data['patterns']
        )


class DirCleaner:

    __read_file_formats = ['.unnecessary']

    def __init__(self, path: str = None, new_read_files: list[str] = None):
        if path is None:
            path = os.getcwd()
        if new_read_files is not None:
            self.__read_file_formats += new_read_files
        self.__STARTING_DIR = path

        self.__exception_files = ExceptionFiles()
        self.__unnecessary_files = UnnecessaryFiles()

    def check_is_read_files_exists(self):
        dir_objects = os.listdir(self.__STARTING_DIR)

        if not any([any([file.endswith(file_format) for file_format in self.__read_file_formats]) for file in dir_objects if os.path.isfile(file)]):
            self.show_notification(
                f"No any *{', '.join(self.__read_file_formats)} available\n in {self.__STARTING_DIR}")
            exit()

    def show_notification(self, message: str):
        file = open("dir_cleaner.exceptions", 'w')
        file.write(message)
        file.close()

        full_path = os.path.join(self.__STARTING_DIR, file.name)
        os.startfile(full_path)
        import time
        time.sleep(2)
        os.remove(full_path)

    def read_unnecessary_file_formats(self):
        self.check_is_read_files_exists()
        dir_objects = os.listdir(self.__STARTING_DIR)

        for dir_object in dir_objects:
            if os.path.isfile(dir_object) and any([dir_object.endswith(file_format) for file_format in self.__read_file_formats]):
                compiled_file_data = CompileUnnecessaryFile(
                    os.path.join(self.__STARTING_DIR, dir_object))
                self.__exception_files += compiled_file_data.exception_files
                self.__unnecessary_files += compiled_file_data.unnecessary_files

    def cleanup_dir(self, path: str = None):
        if path is None:
            path = self.__STARTING_DIR
        dir_objects = os.listdir(path)

        for dir_object in dir_objects:
            dir_object_filepath = os.path.join(path, dir_object)

            if os.path.isfile(dir_object_filepath) and self.is_deletable(dir_object, path):
                os.remove(dir_object_filepath)
            elif os.path.isdir(dir_object_filepath):
                self.cleanup_dir(dir_object_filepath)

    def is_deletable(self, file_name: str, path: str):
        full_path = os.path.join(path, file_name)
        relative_path = os.path.relpath(full_path, self.__STARTING_DIR)
        pattern_getting_function = self.__unnecessary_files.get_file_patterns

        if file_name in self.__exception_files.get_exceptions():
            return False

        elif any([file_name.endswith(file_format) for file_format in self.__unnecessary_files.get_file_format()]) \
                or any([(file_name.startswith(pattern) or relative_path.startswith(pattern)) for pattern in pattern_getting_function('startswith')]) \
                or any([(file_name.endswith(pattern) or relative_path.endswith(pattern)) for pattern in pattern_getting_function('endswith')]) \
                or any([(pattern in file_name or pattern in relative_path) for pattern in pattern_getting_function('includes')]):
            return True
        return False


if __name__ == '__main__':
    MAIN_DIRECTORY = os.getcwd()

    dir_cleaner = DirCleaner(MAIN_DIRECTORY)
    dir_cleaner.read_unnecessary_file_formats()
    dir_cleaner.cleanup_dir()
