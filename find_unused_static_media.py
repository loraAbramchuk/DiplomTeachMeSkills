import os
import re

# Пути к папкам
STATIC_DIR = 'InformationService/static'
MEDIA_DIR = 'InformationService/media'
TEMPLATES_DIR = 'InformationService/templates'

def get_all_files(root_dir):
    file_paths = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if not file.startswith('.'):
                file_paths.append(os.path.relpath(os.path.join(root, file), root_dir))
    return set(file_paths)

def get_files_by_ext(root_dir, ext):
    result = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(ext):
                result.append(os.path.join(root, file))
    return result

def find_references_in_files(files, static_files, media_files):
    used_static = set()
    used_media = set()
    # Шаблоны Django
    static_pattern = re.compile(r"""static ['"]([^'"]+)['"]""")
    media_pattern = re.compile(r"""media/([^\s"']+)""")
    # JS/CSS прямые пути
    static_path_pattern = re.compile(r"""static/([^\s"']+)""")
    media_path_pattern = re.compile(r"""media/([^\s"']+)""")
    for file_path in files:
        with open(file_path, encoding='utf-8') as f:
            content = f.read()
            # Django templates
            for match in static_pattern.findall(content):
                norm = match.lstrip('/')
                if norm in static_files:
                    used_static.add(norm)
            for match in media_pattern.findall(content):
                norm = match.lstrip('/')
                if norm in media_files:
                    used_media.add(norm)
            # JS/CSS прямые пути
            for match in static_path_pattern.findall(content):
                norm = match.lstrip('/')
                if norm in static_files:
                    used_static.add(norm)
            for match in media_path_pattern.findall(content):
                norm = match.lstrip('/')
                if norm in media_files:
                    used_media.add(norm)
    return used_static, used_media

def main():
    static_files = get_all_files(STATIC_DIR)
    media_files = get_all_files(MEDIA_DIR)
    template_files = get_files_by_ext(TEMPLATES_DIR, '.html')
    js_files = get_files_by_ext(STATIC_DIR, '.js')

    # Анализ шаблонов и js-файлов
    used_static_tpl, used_media_tpl = find_references_in_files(template_files, static_files, media_files)
    used_static_js, used_media_js = find_references_in_files(js_files, static_files, media_files)

    used_static = used_static_tpl | used_static_js
    used_media = used_media_tpl | used_media_js

    unused_static = static_files - used_static
    unused_media = media_files - used_media

    print('Неиспользуемые static-файлы:')
    for f in sorted(unused_static):
        print(f'  {f}')
    print('\nНеиспользуемые media-файлы:')
    for f in sorted(unused_media):
        print(f'  {f}')

if __name__ == '__main__':
    main() 