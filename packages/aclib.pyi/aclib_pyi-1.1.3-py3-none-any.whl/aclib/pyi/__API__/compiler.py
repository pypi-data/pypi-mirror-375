from __future__ import annotations

import os, glob, re, platform, tempfile, hashlib, base64, json, shutil
from distutils.dir_util import remove_tree, copy_tree

from .const import DIR_COMPILED
from .colorstr import *

__all__ = ['compile']

def matchpath(*globexps: str, root='', onlyfile=False, onlydir=False) -> list[str]:
    if onlyfile and onlydir: raise TypeError(
        'can not set onlyfile and onlydir at the same time')
    paths = set()
    for expression in globexps:
        paths.update(glob.glob(os.path.join(root, expression), recursive=True))
    if onlyfile:
        paths = filter(os.path.isfile, paths)
    if onlydir:
        paths = filter(os.path.isdir, paths)
    return sorted(map(lambda p: os.path.join(root, os.path.relpath(p, root)), paths))

def unicodeOf(string: str) -> str:
    return ''.join(char.encode('unicode-escape').decode() if ord(char) > 256 else char for char in string)

def unicode_stringcode(stringcode_match: re.Match):
    stringcode = stringcode_match.group(0)
    if not stringcode.startswith('f'):
        return unicodeOf(stringcode)
    fstring = stringcode
    # 查找f-string中的expression part
    breakpoints = [0]
    start = end = brackCount = 0
    for i,char in enumerate(fstring):
        if char == '{':
            brackCount += 1
            if brackCount==1: start=i
            if brackCount==2 and fstring[i-1] == '{': brackCount=0
        if char == '}':
            if brackCount==1:
                end=i+1
                breakpoints += [start, end]
            if brackCount!=0: brackCount -= 1
    breakpoints.append(len(fstring))

    newstr = ''
    for i in range(0, len(breakpoints), 2):
        fir, sec = breakpoints[i], breakpoints[i+1]
        newstr += unicodeOf(fstring[fir:sec])
        if i+2<len(breakpoints): newstr += fstring[sec:breakpoints[i+2]]
    return newstr

def calc_file_hash(filepath: str) -> str:
    if not os.path.isfile(filepath):
        return ''
    with open(filepath, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def get_log(logfile: str) -> dict[str, str]:
    if not os.path.isfile(logfile):
        return {}
    with open(logfile, 'rb') as f:
        try:
            return json.loads(base64.b64decode(f.read()).decode())
        except:
            return {}

def save_log(logfile: str, log: dict[str, str]):
    with open(logfile, 'wb') as f:
        f.write(base64.b64encode(json.dumps(log).encode()))

def remove_pycaches(tempdir: str):
    for pycache in matchpath('**/__pycache__', root=tempdir, onlydir=True):
        remove_tree(pycache)

def compile(srcdir: str, dstdir: str = DIR_COMPILED, exclude_scripts: list[str] = None, dst_replace_confirm=True) -> str:
    """exclude_scripts is a list of glob expressions whose root equals srcdir."""

    dstdir = dstdir or 'compiled'
    exclude_scripts = exclude_scripts or []
    language_level = platform.python_version().split(".")[0]
    stringcode_pattern = 'f?((["\']{3})|(["\']))[\\s\\S]*?(?<!\\\\)\\1|#[\\s\\S]+?(?=\n|$)'

    with tempfile.TemporaryDirectory(dir='') as tempdir:
        copy_tree(srcdir, tempdir)
        remove_pycaches(tempdir)
        _all_pyfiles = matchpath('**/*.py', root=tempdir, onlyfile=True)
        _exclude_pyfiles = matchpath(*exclude_scripts, root=tempdir, onlyfile=True)
        compiling_pyfiles = sorted(set(_all_pyfiles) - set(_exclude_pyfiles))
        old_builds = matchpath('**/build', '**/build/*', root=tempdir, onlydir=True)

        logfile = f'.pyd.log'
        log = get_log(f'{dstdir}/{logfile}')
        for pyfile in compiling_pyfiles:
            print(redstr(f'\nCompiling script {os.path.abspath(pyfile.replace(tempdir, srcdir, 1))} {"-"*30}> '))

            pyhash = calc_file_hash(pyfile)
            loghash = log.get(pyhash, '')
            builtpath = pyfile.replace(tempdir, dstdir, 1) + 'd'
            if loghash and loghash == calc_file_hash(builtpath):
                print(yellowstr(f'Already compiled: using {os.path.abspath(builtpath)}'))
                shutil.copy2(builtpath, pyfile + 'd')
                os.remove(pyfile)
                continue

            with open(pyfile, 'r', encoding='utf8') as f:
                srccode = f.read()
            with open(pyfile, 'w', encoding='utf8') as f:
                f.write(re.sub(stringcode_pattern, unicode_stringcode, srccode))
            for i in range(3):
                extcode = os.system(f'cythonize -i -{language_level} {pyfile}')
                if extcode == 0: break
            if extcode != 0:
                print(redstr(f'Compile failed: {os.path.abspath(pyfile.replace(tempdir, srcdir, 1))}'))
                raise SystemExit(extcode)

            pydir, pyname = os.path.split(pyfile)
            pydfile = matchpath(f'{pyname[:-3]}.cp*.pyd', root=pydir, onlyfile=True)[0]
            os.rename(pydfile, pyfile + 'd')
            os.remove(pyfile)
            os.remove(pyfile[0:-2] + 'c')
            log[pyhash] = calc_file_hash(pyfile + 'd')
        save_log(f'{tempdir}/{logfile}', log)

        build_dirs = matchpath('**/build', '**/build/*', root=tempdir, onlydir=True)
        for buildlib in set(build_dirs) - set(old_builds):
            if os.path.exists(buildlib):
                remove_tree(buildlib)

        if os.path.exists(dstdir):
            if dst_replace_confirm:
                reply = input(yellowstr(f'Distdir "{os.path.abspath(dstdir)}" exists, it will be replaced, continue?(y/n): '))
                if reply != 'y':
                    return print('compile canceled') or ''
            remove_tree(dstdir)
        copy_tree(tempdir, dstdir)
        print(greenstr(f'Compiled project: {os.path.abspath(dstdir)}'))
        return dstdir
