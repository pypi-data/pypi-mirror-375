#!/usr/bin/env python3

'''list Files or Directories - an alternative to ls find tree du grep wc nl ...

 ┌─────┬──────┬────────────────────────────────────────────────────────┐
 │ VAR │ TYPE │                       CONTENT                          │
 ├─────┼──────┼────────────────────────────────────────────────────────┤
 │  i  │ int  │ line count (-W only)                                   │
 │  b  │ str  │ file's permission bits '-rwxrwxrwx' or 'lrwxrwxrwx'    │
 │  l  │ int  │ number of links pointing to this file                  │
 │  u  │ str  │ file's user name                                       │
 │  g  │ str  │ file's group name                                      │
 │  s  │ int  │ file's size in bytes                                   │
 │  h  │ str  │ file's size as human-readable number                   │
 │  t  │ str  │ file's last modification time 'YYYY-mm-dd HH:MM:SS'    │
 │  n  │ int  │ file's nesting = number of '/' in path minus one       │
 │  m  │ int  │ file's multiplicity = number of homonym files          │
 │  c  │ int  │ number of charcaters in file                           │
 │  w  │ int  │ number of words in file                                │
 │  x  │ int  │ max line length in file                                │
 │  y  │ int  │ number of lines in file                                │
 │  d  │ str  │ directory (always ending with '/')                     │
 │  f  │ str  │ filename                                               │
 │  e  │ str  │ filename extension (always starting with '.')          │
 │  p  │ str  │ path %d%f = directory + filename                       │
 │  q  │ str  │ '->' if file is a link else ''                         │
 │  r  │ str  │ target if file is a link else ''                       │
 │  K  │ int  │ 1024      (-F only)                                    │
 │  M  │ int  │ 1024 ** 2 (-F only)                                    │
 │  G  │ int  │ 1024 ** 3 (-F only)                                    │
 │  T  │ int  │ 1024 ** 4 (-F only)                                    │
 │  P  │ int  │ 1024 ** 5 (-F only)                                    │
 │  E  │ int  │ 1024 ** 6 (-F only)                                    │
 │  Z  │ int  │ 1024 ** 7 (-F only)                                    │
 │  Y  │ int  │ 1024 ** 8 (-F only)                                    │
 └─────┴──────┴────────────────────────────────────────────────────────┘

                               Figure a. File Variables

 ┌─────┬──────┬────────────────────────────────────────────────────────┐
 │ VAR │ TYPE │                       CONTENT                          │
 ├─────┼──────┼────────────────────────────────────────────────────────┤
 │  i  │ int  │ line count (-W only)                                   │
 │  b  │ str  │ dir's permission bits 'drwxrwxrwx'                     │
 │  l  │ int  │ number of links pointing to dir                        │
 │  u  │ str  │ dir's user name                                        │
 │  g  │ str  │ dir's group name                                       │
 │  s  │ int  │ tot size in bytes of dir's files                       │
 │  h  │ str  │ tot size of dir's files as human-readable number       │
 │  t  │ str  │ max last mod time of dir's files 'YYYY-mm-dd_HH:MM:SS' │
 │  n  │ int  │ dir's nesting = number of '/' in path minus one        │
 │  m  │ int  │ tot number of dir's files                              │
 │  c  │ int  │ tot number of characters in dir's files                │
 │  w  │ int  │ tot number of words in dir's files                     │
 │  x  │ int  │ max line length in dir's files                         │
 │  y  │ int  │ tot number of lines in dir's files                     │
 │  d  │ str  │ directory (always ending with '/')                     │
 │  f  │ str  │ ''                                                     │
 │  e  │ str  │ ''                                                     │
 │  p  │ str  │ directory (always ending with '/')                     │
 │  q  │ str  │ ''                                                     │
 │  r  │ str  │ ''                                                     │
 │  K  │ int  │ 1024      (-D only)                                    │
 │  M  │ int  │ 1024 ** 2 (-D only)                                    │
 │  G  │ int  │ 1024 ** 3 (-D only)                                    │
 │  T  │ int  │ 1024 ** 4 (-D only)                                    │
 │  P  │ int  │ 1024 ** 5 (-D only)                                    │
 │  E  │ int  │ 1024 ** 6 (-D only)                                    │
 │  Z  │ int  │ 1024 ** 7 (-D only)                                    │
 │  Y  │ int  │ 1024 ** 8 (-D only)                                    │
 └─────┴──────┴────────────────────────────────────────────────────────┘

                               Figure b. - Dir Variables

Examples:

    $ ffdd '~/.*' # list hidden files only
    $ ffdd '~/[!.]*' # list unhidden files only
    $ ffdd -r -F 'M<=s<2*M' # list files big at least 1 MB but less than 2 MB
    $ ffdd -r -F 'M<=s<2*M' -d # list dirs having files big at least 1 MB but less than 2 MB
    $ ffdd -r -D 'M<=s<2*M' -d # list dirs big at least 1 MB but less than 2 MB
    $ ffdd -F 'b[0]=="-"' # list files only, not links
    $ ffdd -F 'b/"-*"' # list files only, not links (another way) 
    $ ffdd -F 'm>1' -Sfd  # list groups of homonym files
    $ ffdd -F '"2014"<=t<"2018"' # list files saved in years 2014-2017
    $ ffdd -F 't/"201[4-7]*"' # list files saved in years 2014-2017 (another way)
    $ ffdd -L '^*#*&(def *,* def *,class *,* class *)' '*.py'
    $    # show 'def' and 'class' statements in Python files, excluding commented lines 
    $ ffdd -L '*' -j4 - <xyz.py >nnnn-xyz.py # create a copy with numbered lines

For details about YARE (Yet Another Regular Expression), see:

    https://pypi.org/project/libyare

'''

__version__ = '0.0.0'

