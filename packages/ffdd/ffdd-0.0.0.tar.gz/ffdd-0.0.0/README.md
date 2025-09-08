```
usage: yals [-h] [-V] [-v] [-r] [-F FILES_IF] [-L LINE_PATTERN] [-i] [-m]
            [-j MATCH_COUNT] [-k LINE_COUNT] [-S SORT_BY] [-W OUTPUT_FORMAT]
            [-u HUMAN_WIDTH] [-N] [-n] [-d] [-a] [-t] [-D DIRS_IF]
            [path_files]

list Files or Directories - an alternative to ls find tree du grep wc nl ...

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

positional arguments:
  path_files            input [path/]file-pattern, default: './*', '-' = read
                        from stdin

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  -v, --verbose         print warning messages on stderr (default: warning
                        messages are lost)
  -r, --recursive       dive into subdirectories recursively (default: look at
                        the given directory only)
  -F FILES_IF, --files-if FILES_IF
                        Python boolean expression for selection of files,
                        default: 'True', domain: b l o g s u t m n z c w x y d
                        e f p q r K M G T P E Z Y, syntax: standard Python3
                        syntax plus the YARE match operators '/' (case-
                        sensitive) and '//' (case-insensitive)
  -L LINE_PATTERN, --line-pattern LINE_PATTERN
                        YARE pattern for line matching (default: '' = don't
                        read file lines)
  -i, --case-insensitive
                        -L match is case-insensitive (default: case-sensitive)
  -m, --case-multiple   -L match is case-multiple (default: case-sensitive)
  -j MATCH_COUNT, --match-count MATCH_COUNT
                        width of match count prefixed to matching lines,
                        default: 0 = no match count, domain: 0 1 2 3 4 5 6 7 8
                        9
  -k LINE_COUNT, --line-count LINE_COUNT
                        width of line count prefixed to matching lines,
                        default: 0 = no line count, domain: 0 1 2 3 4 5 6 7 8
                        9
  -S SORT_BY, --sort-by SORT_BY
                        keys for sorting of files or dirs, file mode default:
                        'df', dir mode default: 'd', domain: b l o g s u t m n
                        z c w x y d e f p q r B L O G S U T M N Z C W X Y D E
                        F P Q R, lowercase: ascending, uppercase: descending
  -W OUTPUT_FORMAT, --output-format OUTPUT_FORMAT
                        format of output lines of files or dirs, file mode
                        default: 'iblogsutmnzpqr' = '%i %b %l %o %g %s %u %t
                        %m %n %z %p %q %r', dir mode default: 'iblogsutmnzd' =
                        '%i %b %l %o %g %s %u %t %m %n %z %d', domain: i b l o
                        g s u t m n z c w x y d e f p q r I B L O G S U T M N
                        Z C W X Y D E F P Q R, lowercase = unquoted, uppercase
                        = quoted
  -u HUMAN_WIDTH, --human-width HUMAN_WIDTH
                        width of human-readable size (%u attribute), default:
                        6, domain: 5 6 7 8 9
  -N, --no-headers      do not write headers with attribute names
  -n, --no-lines        do not write matching lines selected by -L
  -d, --dirs-mode       run in dirs mode, group files by directory and print
                        directories, default: run in files mode, print files
  -a, --add-dir         add into each dir the values of the dir itself
  -t, --tot-dirs        totalize into parent dirs the values of son dirs
  -D DIRS_IF, --dirs-if DIRS_IF
                        Python boolean expression for selection of dirs,
                        default: 'True', domain: b l o g s u t m n z c w x y d
                        e f p q r K M G T P E Z Y, syntax: standard Python3
                        syntax plus the YARE match operators '/' (case-
                        sensitive) and '//' (case-insensitive)
```
