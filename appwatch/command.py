from colored import fg, bg, attr

from datetime import datetime
import filecmp
import glob
import imp
import time
import os
import sys
import shutil

from django import apps
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand, CommandError

from watchdog.observers import Observer
from watchdog.events import (
    DirModifiedEvent,
    LoggingEventHandler,
    FileSystemEventHandler,
)

import os

from django.apps import apps


def django_apps_paths(subdir):
    paths = []
    for app in apps.get_app_configs():
        path = os.path.join(app.path, subdir)
        if os.path.isdir(path):
            paths.append(path)
    return paths


def sync_contents(source, destination):
    if not glob.glob(os.path.join(source, '*')):
        print(
            bg('purple_4a'),
            'No files found in',
            bg('black'),
            fg('pale_green_3a'),
            source,
            attr('reset'),
        )
        return

    report = filecmp.dircmp(source, destination)

    for missing in report.left_only:
        src = os.path.join(source, missing)

        # Skip dotfiles (emacs makes some)
        if src.split('/')[0].startswith('.'):
            continue

        dest = os.path.join(destination, missing)
        common = os.path.commonprefix([src, dest])
        src_display = src[len(common):]
        dest_display = dest[len(common):]

        if os.path.isfile(src):
            print(
                bg('purple_1b'),
                'Copy new file',
                bg('black'),
                fg('orange_1'),
                src_display,
                'to',
                dest_display,
                attr('reset'),
            )

            shutil.copyfile(src, dest)
        elif os.path.isdir(src):
            print(
                bg('purple_1b'),
                'Copy new directory',
                bg('black'),
                fg('pale_green_3a'),
                src_display,
                'to',
                dest_display,
                attr('reset'),
            )

            shutil.copytree(src, dest)
        else:
            print(
                bg('purple_4a'),
                'WTF is this file you poney?!',
                bg('black'),
                fg('pale_green_3a'),
                src,
                attr('reset'),
            )

    for changed in report.diff_files:
        src = os.path.join(source, changed)
        dest = os.path.join(destination, changed)

        print(
            bg('purple_4a'),
            'Copy changed file',
            bg('black'),
            fg('pale_green_3a'),
            src,
            'to',
            dest,
            attr('reset'),
        )
        shutil.copyfile(src, dest)

    for common in report.common_dirs:
        sync_contents(
            os.path.join(source, common),
            os.path.join(destination, common)
        )


def run(source, destination):
    dest = os.path.abspath(destination)
    print(
        bg('orange_1'),
        'Building:',
        bg('black'),
        fg('pale_green_3a'),
        '{} ({})'.format(destination, dest),
        attr('reset'),
    )

    if not os.path.exists(dest):
        print(
            bg('deep_pink_2'),
            'Making directory:',
            bg('black'),
            fg('pale_green_3a'),
            dest,
            attr('reset'),
        )
        os.makedirs(dest)

    for src in django_apps_paths(source):
        if os.path.isdir(src):
            sync_contents(src, dest)
        elif os.path.exists(src):
            print(
                bg('red_1'),
                'Exists but not a directory:',
                src,
                attr('reset'),
            )
    print()


class Handler(FileSystemEventHandler):
    def __init__(self, source, destination):
        self.source = source
        self.destination = destination

    def on_any_event(self, event):
        print(
            bg('red_1'),
            'Event',
            'at',
            datetime.now(),
            bg('black'),
            fg('medium_violet_red'),
            event,
            attr('reset'),
        )
        print(
            bg('red_1'),
            'For watchdog',
            bg('black'),
            fg('green'),
            self.source,
            attr('reset'),
        )
        sync_contents(self.source, self.destination)
        print()


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.observers = {}

        print()
        for arg in args:
            source, destination = arg.split(':')

            # Clear destination directories
            dest = os.path.abspath(destination)
            if os.path.exists(dest):
                print(
                    bg('red_1'),
                    'REMOVING:',
                    dest,
                    attr('reset'),
                )
                shutil.rmtree(dest)
                print()

            # Execute it first
            run(source, destination)

        for arg in args:
            source, destination = arg.split(':')
            # Add observers to execute it on file change
            for path in django_apps_paths(source):
                self.add_observer(path, destination)

        if not self.observers:
            print(
                bg('red_1'),
                'No path found !',
                attr('reset'),
            )
            sys.exit(1)

        # Start observers
        self.observe()

    def observe(self):
        print(
            bg('purple_4a'),
            'Watchdog start',
            bg('black'),
            fg('pale_green_3a'),
            attr('reset'),
        )

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            for observer in self.observers.values():
                observer.stop()
        for observer in self.observers.values():
            observer.join()

    def add_observer(self, source, destination):
        print(
            bg('purple_4a'),
            'Adding watchdog for:',
            bg('black'),
            fg('pale_green_3a'),
            source,
            'to',
            destination,
            attr('reset'),
        )

        self.observers[source] = Observer()
        self.observers[source].schedule(
            Handler(source, destination),
            source,
            recursive=True
        )
        self.observers[source].start()
