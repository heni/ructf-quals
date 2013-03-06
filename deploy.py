#!/usr/bin/env python2

import argparse
import os, errno
import stat
import sys
import shutil
from shutil import Error, copy2, copystat
from zipfile import ZipFile, ZIP_DEFLATED
from contextlib import closing
import ConfigParser


SVN_DIR_NAME = '.svn' # Directory to be excluded till import
CHECKERS_ORDER = ('xml', 'py', 'ext')

# Subdirs for export
LIBQUEST_DIRNAME = 'libquest'
STATIC_DIRNAME = 'static'

# Config file to create
CFG_FILENAME = 'questserver.cfg'
CFG_TEMPLATE = 'questserver.cfg.template'
TASK_CFG_FILENAME = 'tasks.cfg'

### Variables to for config file
srv_name = "http://quals2011.ructf.org"
base_path = "/"
base_url = "%(srv_name)s%(base_path)s"
log_dir = "/var/log/qserver"
workers = 10
open_all = "yes"

backup_dir = "backup"
backup_savefile = "state.bin"
backup_savecount = 50


class Task(object):
    def __init__(self, full_path,
                 name=None,
                 category=None,
                 score=None,
                 relative_path=None,
                 checker=None,
                 checker_type=None):
        self.full_path = full_path
        self.name = name
        self.category = category
        self.score = score
        self.relative_path = relative_path
        self.checker = checker
        self.checker_type = checker_type

    def __str__(self):
        return ", ".join(["{0}: '{1}'".format(k.capitalize(), v) for k, v in self.__dict__.items() if v])


class QuestServerCheckers(object):
    def _scan_path(self, path):
        tasks = []
        for task_name in os.listdir(path):
            full_task_path = os.path.join(path, task_name)
            # Skipping all garbage in directory
            if not os.path.isdir(full_task_path):
                continue
            tasks.append(Task(full_task_path, name=task_name, relative_path=task_name))
        return tasks

    def _script_quest_finder(self, checker_type, task):
        full_checker_path = os.path.join(task.full_path, task.name)
        if os.path.exists(full_checker_path):
            return (checker_type, task.name)
        return None


    def _extention_finder(self, checker_type, task):
        checker_file = task.name + '.' + checker_type
        full_checker_path = os.path.join(task.full_path, checker_file)
        if os.path.exists(full_checker_path):
            return (checker_type, checker_file)
        return None

    def scan_for_checkers(self):
        self.tasks = self._scan_path(self.path)

        tasks_with_checkers = []
        for task in self.tasks:
            found = False
            for checker_type in CHECKERS_ORDER:
                checker = self.checkers_finders[checker_type]
                checkertype_checkerfile = checker(checker_type, task)
                if checkertype_checkerfile:
                    (task.checker_type, task.checker) = checkertype_checkerfile
                    tasks_with_checkers.append(task)
                    found = True
                    break
            if not found:
                print ">>>> Can't find checker in '{0}', skipping".format(task.full_path)
        self.tasks = tasks_with_checkers

    def __init__(self, path):
        self.path = path

        self.checkers_finders = {
            'xml': self._extention_finder,
            'py': self._extention_finder,
            'ext': self._script_quest_finder,
        }


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


def copytree(src, dst, symlinks=False, ignore=None):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    mkdir_p(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                copy2(srcname, dstname)
                # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            print "!!!!1"
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.extend(err.args[0])
    try:
        copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error, errors


def parse_args():
    parser = argparse.ArgumentParser(description='Deploy RuCTF Quals')
    parser.add_argument('src_dir', metavar='src_dir', type=str, help='Source dir to deploy')
    parser.add_argument('dst_dir', metavar='dst_dir', type=str, help='Destination dir to deploy')

    args = parser.parse_args()
    return args


def svn_export_ignore_svn_path(path, names):
    if SVN_DIR_NAME not in names:
        return []

    for name in names:
        if name != SVN_DIR_NAME:
            continue

        full_path = os.path.join(path, name)
        if os.path.isdir(full_path):
            return SVN_DIR_NAME


def svn_export(src_dir, dst_dir):
    print "== Copy '%s' -> '%s'" % (src_dir, dst_dir)
    shutil.copytree(src_dir, dst_dir, ignore=svn_export_ignore_svn_path)


def make_scripts_executable(qac):
    files_x = []
    for task in qac.tasks:
        if task.checker_type != 'ext':
            continue
        full_filename = os.path.join(task.full_path, task.checker)
        mode = os.stat(full_filename)[0]
        print mode
        mode = (mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        print mode
        os.chmod(full_filename, mode)
        files_x.append(full_filename)
    return files_x


def compress_zip(path):
    (path_to_zip, zip_filename) = os.path.split(path)
    with closing(ZipFile(zip_filename, 'w', ZIP_DEFLATED)) as zip_file_fn:
        for root, dirs, files in os.walk(path):
            for fn in files:
                full_fn = os.path.join(root, fn)
                zfn = full_fn[len(path) + len(os.sep):]
                zip_file_fn.write(full_fn, zfn)
    shutil.rmtree(path)
    shutil.move(zip_filename, path_to_zip)


def compress_zips(dst_dir):
    dirs_to_compress = []
    for root, dirs, files in os.walk(dst_dir):
        for one_dir in dirs:
            if one_dir.endswith('.zip'):
                full_path = os.path.join(root, one_dir)
                dirs_to_compress.append(full_path)

    for dtc in dirs_to_compress:
        compress_zip(dtc)
    return dirs_to_compress


def make_cfgfile(qac, cfg_filename):
    cp = ConfigParser.RawConfigParser()
    #cp.add_section('DEFAULT')

    if os.path.exists(CFG_TEMPLATE):
        cp.read(CFG_TEMPLATE)
    else:
        cp.set('DEFAULT', 'srv_name', srv_name)
        cp.set('DEFAULT', 'base_path', base_path)
        cp.set('DEFAULT', 'base_url', base_url)
        cp.set('DEFAULT', 'log_dir', log_dir)
        cp.set('DEFAULT', 'workers', workers)
        cp.set('DEFAULT', 'open_all', open_all)

        cp.add_section('backup')
        cp.set('backup', 'dir', backup_dir)
        cp.set('backup', 'savefile', backup_savefile)
        cp.set('backup', 'savecount', backup_savecount)

    with open(cfg_filename, 'w') as out_fn:
        cp.write(out_fn)


def make_task_config(qac, tasks_filename, libquest_dir):
    cp = ConfigParser.RawConfigParser()
    categories = set(t.category for t in qac.tasks)
    cp.set('DEFAULT', 'categories', ':'.join(map(str, categories)))

    for category in categories:
        cp.add_section(str(category))
        cp.set(category, 'name', str(category))
        category_dir = libquest_dir
        if category is not None:
            category_dir = os.path.join(category_dir, str(category))
        cp.set(category, 'dir', category_dir)

    pseudo_price = 1
    for task in qac.tasks:
        if task.category is None:
            print "!!!! Task {0} at '{1}' has no category".format(task.name, task.full_path)
        task_id = "q{0}".format(pseudo_price)
        checker_path = os.path.join(task.relative_path, task.checker)
        value = "{0}:{1}".format(task.checker_type, checker_path)
        cp.set(str(task.category), task_id, value)
        pseudo_price += 1
    with open(tasks_filename, 'w') as out_fn:
        cp.write(out_fn)


def make_static_dir(qac, static_dir):
    static_dirs = []
    static_dir = os.path.join(static_dir, '')
    os.mkdir(static_dir)
    for task in qac.tasks:
        full_path = os.path.join(task.full_path, STATIC_DIRNAME)

        if not os.path.isdir(full_path):
            continue

        copytree(full_path, static_dir)
        static_dirs.append(full_path)
    return static_dirs


def main():
    args = parse_args()

    src_dir = args.src_dir
    dst_dir = args.dst_dir

    dst_dir_libquest = os.path.join(dst_dir, LIBQUEST_DIRNAME)

    if not os.path.isdir(src_dir):
        print >> sys.stderr, "%s does not exists or not directory" % src_dir
        sys.exit(1)

    if os.path.exists(dst_dir):
        print >> sys.stderr, "%s already exists" % dst_dir
        sys.exit(2)

    print "== Deployng '%s' to '%s'" % (src_dir, dst_dir)
    svn_export(src_dir, dst_dir_libquest)

    print "== Scaning for checkers"
    qac = QuestServerCheckers(dst_dir_libquest)
    qac.scan_for_checkers()

    print "== Found tasks:"
    for task in qac.tasks:
        print str(task)

    print "== Making executable:"
    if os.name != 'posix':
        print "(Skipped because not POSIX OS)"
    else:
        files_x = make_scripts_executable(qac)
        print "\n".join(files_x)

    print "== Compress zips:"
    zips = compress_zips(dst_dir_libquest)
    print "\n".join(zips)

    print "== Make static dir:"
    static_dir = os.path.join(dst_dir, STATIC_DIRNAME)
    static_dirs = make_static_dir(qac, static_dir)
    print "\n".join(static_dirs)

    print "== Make cfg_file"
    cfg_path = os.path.join(dst_dir, CFG_FILENAME)
    make_cfgfile(qac, cfg_path)

    print "== Make tasks config file"
    task_config_path = os.path.join(dst_dir, TASK_CFG_FILENAME)
    make_task_config(qac, task_config_path, LIBQUEST_DIRNAME)
    print cfg_path

if __name__ == "__main__":
    main()