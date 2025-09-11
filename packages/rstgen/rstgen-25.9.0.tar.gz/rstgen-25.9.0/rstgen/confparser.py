# -*- coding: UTF-8 -*-
# Copyright 2022-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import io
from pathlib import Path
from configparser import ConfigParser, DEFAULTSECT

NONE_FORMATS = ['none', 'null']


class ConfigParser(ConfigParser):

    def getpath(self, section, option, *args, **kwargs) -> Path:
        value = self.get(section, option, *args, **kwargs)
        if value.startswith('path:'):
            return Path(value.split('path:')[1])
        raise ValueError(f'Not a path: {value}')

    def getnone(self, section, option, *args, **kwargs) -> None:
        value = self.get(section, option, *args, **kwargs)
        if value.lower() in NONE_FORMATS:
            return None
        raise ValueError(f'Not None: {value}')

    def stringify_set(self, section, option, value):
        if isinstance(value, Path):
            value = f"path:{value}"
        self.set(section, option, str(value))

    def parsed_get(self, section, option, *args, **kwargs):
        value = None
        try:
            value = self.getfloat(section, option, *args, **kwargs)
            _value = self.getint(section, option, *args, **kwargs)
            if value == _value:
                value = _value
        except ValueError:
            pass
        if value is None:
            for attr in ['getboolean', 'getpath', 'getnone', 'get']:
                try:
                    value = getattr(self, attr)(section, option, *args,
                                                **kwargs)
                    break
                except ValueError:
                    pass
        return value

    # The following patch is taken from https://bugs.python.org/issue1410680

    def update_file(self, fp, add_missing=True):
        """Update the specified configuration file to match the current
        configuration data.

        Ordering (including blank lines) and comments are preserved.

        Minor whitespace normalisation (that preceding continuation lines
        and inline comments) does occur.

        If add_missing is True, then new options are added to the end of
        sections (if a section is in a file twice, the last section will be
        used); new sections are added to the end of the file.  This
        does mean that if the configuration was read from multiple files,
        the file that is output to will contain the options from all of
        those files.  To avoid this, use add_missing=False, and update each
        of the input files.

        Default values are not added; nor are the __name__ options.
        """
        sections = {}
        current = io.StringIO()
        replacement = [current]
        sect = None
        opt = None
        written = []
        # Default to " = " to match write(), but use the most recent
        # separator found if the file has any options.
        vi = " = "
        while True:
            line = fp.readline()
            if not line:
                break
            # Comment or blank line?
            if line.strip() == '' or line[0] in '#;' or \
               (line.split(None, 1)[0].lower() == 'rem' and \
                line[0] in "rR"):
                current.write(line)
                continue
            # Continuation line?
            if line[0].isspace() and sect is not None and opt:
                if ';' in line:
                    # ';' is a comment delimiter only if it follows
                    # a spacing character
                    pos = line.find(';')
                    if line[pos - 1].isspace():
                        comment = line[pos - 1:]
                        # Get rid of the newline, and put in the comment.
                        current.seek(-1, 1)
                        current.write(comment + "\n")
                continue
            # A section header or option header?
            else:
                # Is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    # Remember the most recent section with this name,
                    # so that any missing options can be added to it.
                    if sect:
                        sections[sect] = current
                    sect = mo.group('header')
                    current = io.StringIO()
                    replacement.append(current)
                    if sect in self.sections():
                        current.write(line)
                    # So sections can't start with a continuation line:
                    opt = None
                # An option line?
                else:
                    mo = self.OPTCRE.match(line)
                    if mo:
                        opt, vi, value = mo.group('option', 'vi', 'value')
                        comment = ""
                        if vi in ('=', ':') and ';' in value:
                            # ';' is a comment delimiter only if it follows
                            # a spacing character
                            pos = value.find(';')
                            if value[pos - 1].isspace():
                                comment = value[pos - 1:]
                        opt = opt.rstrip().lower()
                        if self.has_option(sect, opt):
                            value = self.get(sect, opt)
                            # Fix continuations.
                            value = value.replace("\n", "\n\t")
                            current.write("%s%s%s%s\n" %
                                          (opt, vi, value, comment))
                            written.append((sect, opt))
        if sect:
            sections[sect] = current
        if add_missing:
            # Add any new sections.
            sects = [DEFAULTSECT]
            sects.extend(self.sections())
            sects = sorted(sects)
            for sect in sects:
                if sect == DEFAULTSECT:
                    opts = self._defaults.keys()
                else:
                    # Must use _section here to avoid defaults.
                    opts = self._sections[sect].keys()
                opts = sorted(opts)
                if sect in sections:
                    output = sections[sect] or current
                else:
                    output = current
                    output.write("[%s]\n" % (sect, ))
                    sections[sect] = None
                for opt in opts:
                    if opt != "__name__" and not (sect, opt) in written:
                        value = self.get(sect, opt)
                        # Fix continuations.
                        value = value.replace("\n", "\n\t")
                        output.write("%s%s%s\n" % (opt, vi, value))
                        written.append((sect, opt))
                output.write("\n")
        # Copy across the new file.
        fp.seek(0)
        fp.truncate()
        for sect in replacement:
            if sect is not None:
                fp.write(sect.getvalue())
        fp.write("\n")
