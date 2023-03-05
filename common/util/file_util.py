import os

from .typing_util import *
from .assert_util import any_match

_win_forbid_char = [char for char in '\\/:*?"<>|']


def fix_windir_name(dn: str, attr_char='_') -> str:
    """
    把文件夹名称变成win的合法文件夹名
    @param dn: 文件夹名称 dirname
    @param attr_char: 非法字符替换为
    @return: 合法文件夹名
    """
    if not any_match(dn, _win_forbid_char):
        return dn

    for char in _win_forbid_char:
        if char in dn:
            dn = dn.replace(char, attr_char)

    return dn


def fix_filepath(filepath: str, is_dir=True) -> str:
    """
    unix-style filepath
    """
    filepath = filepath.replace("\\", '/').replace("//", '/')

    if is_dir is not True:
        return filepath
    else:
        return filepath if filepath[-1] == '/' else filepath + '/'


def fix_suffix(suffix: str) -> str:
    """
    保证suffix以"."开头，如 .png
    """
    return suffix if suffix[0] == '.' else f'.{suffix}'


def mkdir_if_not_exists(dirpath: str):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)


def file_exists(filepath: str) -> bool:
    return os.path.exists(filepath)


def file_not_exists(filepath: str) -> bool:
    return not os.path.exists(filepath)


def path_last_seperator_index(filepath):
    return max(filepath.rfind("/"), filepath.rfind("\\"))


def of_file_name(filepath: str, trim_suffix=False) -> str:
    if trim_suffix is True:
        filepath = change_file_suffix(filepath, '')

    return filepath[path_last_seperator_index(filepath) + 1::]


def of_file_suffix(filepath: str, trim_comma=False) -> str:
    return filepath[filepath.rfind(".") + trim_comma:]


def suffix_equal(fp1, fp2):
    return of_file_suffix(fp1) == of_file_suffix(fp2)


def suffix_not_equal(fp1, fp2):
    return of_file_suffix(fp1) != of_file_suffix(fp2)


def change_file_name(filepath: str, new_name: str) -> str:
    index = path_last_seperator_index(filepath)
    return filepath[:index + 1] + new_name


def rename(src: str,
           new_name: str = None,
           new_dir: str = None,
           new_suffix: str = None,
           ):
    if file_not_exists(src):
        raise AssertionError(f'重命名文件的路径不存在: {src}')

    if new_name is None:
        new_name = of_file_name(src, trim_suffix=True)

    if new_dir is None:
        new_dir = src[:path_last_seperator_index(src) + 1]
    else:
        mkdir_if_not_exists(new_dir)

    if new_suffix is None:
        new_suffix = of_file_suffix(src)

    new_path = fix_filepath(new_dir) + new_name + new_suffix

    os.rename(src, new_path)


def change_file_suffix(filepath: str, new_suffix: str) -> str:
    if new_suffix == '':
        return filepath[:filepath.rfind(".")]

    return filepath[:filepath.rfind(".") + (new_suffix[0] != '.')] + new_suffix


def of_dir_path(filepath, mkdir=False):
    dirpath = os.path.dirname(filepath)
    if mkdir is True:
        mkdir_if_not_exists(dirpath)
    return dirpath


def create_file(filepath: str):
    f = open(filepath, 'w')
    f.close()


def files_of_dir(abs_dir_path: str) -> List[str]:
    abs_dir_path = fix_filepath(abs_dir_path)
    return [f'{abs_dir_path}{f_or_d}' for f_or_d in os.listdir(abs_dir_path)]


def accept_files_of_dir(abs_dir_path: str, acceptor: Callable[[str, str, int], None]):
    abs_dir_path = fix_filepath(abs_dir_path)
    for index, filename in enumerate(os.listdir(abs_dir_path)):
        acceptor(f'{abs_dir_path}{filename}', filename, index)


def backup_dir_to_zip(dirpath: str,
                      zippath: str,
                      zfile=None,
                      prefix: Optional[str] = None,
                      acceptor: Optional[Callable[[str], bool]] = None,
                      ):
    if zfile is None:
        import zipfile
        zfile = zipfile.ZipFile(zippath, 'w')

    for f in files_of_dir(dirpath):
        file_name = of_file_name(f)

        if prefix is not None:
            file_name = f'{prefix}/{file_name}'

        if os.path.isdir(f):
            if acceptor is None or acceptor(f) is not True:
                continue

            backup_dir_to_zip(f, zippath, zfile, file_name, acceptor)
            continue

        if acceptor is None or acceptor(f) is True:
            zfile.write(f, file_name)

    return zfile


def read_text(filepath, encoding='utf-8') -> str:
    with open(filepath, 'r', encoding=encoding) as f:
        return f.read()


def write_text(filepath, content, encoding='utf-8'):
    with open(filepath, 'w', encoding=encoding) as f:
        f.write(content)
