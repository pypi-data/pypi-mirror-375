pysolbase
============

Welcome to pysol

Copyright (C) 2013/2025 Laurent Labatut / Laurent Champagnac

pysolbase is a set of python helpers to ease development.

It is gevent (co-routines) based.

Usage
===============

Engage gevent monkey patching and setup default logger configuration:

`SolBase.voodoo_init()`

Initialize logging system (without engaging gevent) with default configuration (ie console logs - there is support for syslog and file logs).

`SolBase.logging_init("INFO")`

Re-initialize logging system (without engaging gevent):

`SolBase.logging_init("DEBUG", True)`

Millis helpers:

```
ms = SolBase.mscurrent()
do_something()
ms_elapsed = SolBase.msdiff(ms)
```

Date helpers

```
dt = SolBase.datecurrent()
do_something()
ms_elapsed = SolBase.datediff(dt)
```

Binary helpers

```
bin_buf = SolBase.unicode_to_binary('This is my text buffer', encoding='utf-8')
unicode_string = SolBase.binary_to_unicode(bin_buf, encoding='utf-8')
```

File helpers

```
FileUtility.append_text_to_file('/tmp/test.txt', 'This is my text buffer', 'utf-8')
bin_buf = FileUtility.file_to_binary('/tmp/test.txt')
unicode_string = FileUtility.file_to_text('/tmp/test.txt', 'utf-8')
```

Exception helper

```
try:
   a = None
   b = a + 1
except Exception as e:
   logger.warn("Ex=%s", SolBase.extostr(e))
```
