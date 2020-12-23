# diskusage
Disk Usage 

Collect file information from directory recursive and show top usage.

1. Largest directories by size.
2. Directories by count of files.
3. Largest files
4. Oldest files

Can create Excel File with collected information.
Can create HTML File with sunburst representation (limited to 100).


```
./diskusage.py -h
usage: diskusage.py [-h] [-t TOP] [-w WRITECSV] [-r READCSV] [-x XLSX]
                    [-s HTML] [-p]
                    [directoy]

positional arguments:
  directoy              Directory to analyze. Default, current dir.

optional arguments:
  -h, --help            show this help message and exit
  -t TOP, --top TOP     Show the top <n> entries.
  -w WRITECSV, --writecsv WRITECSV
                        Write dataframe to CSV file
  -r READCSV, --readcsv READCSV
                        Read dataframe from CSV file. Don't scan directory
                        again.
  -x XLSX, --xlsx XLSX  Create Excel file.
  -s HTML, --html HTML  Create HTML file with sunburst animation.
  -p, --progress        show progress animation.
```

### Example output:
~~~
./PycharmProjects/diskusage/diskusage.py -w x.csv -s x.html -x x.xlsx -t 4 /usr

/Users/hergen/PycharmProjects/diskusage/diskusage.py
==============================================================================
Directory (notempty) sizes from /usr
==============================================================================
    
collecting  
Scanning took 0.37416335 seconds
Errors during collection: 0
Files analyzed: 24514
Total size: 1.306644344702363 GB

Top 4 directories by size:
---------------------------------------------------------------------
Directory                  Filecount    Size(MB)
-----------------------  -----------  ----------
/usr/bin                        1086      249.72
/usr/libexec                     269      189.95
/usr/sbin                        228      113.45
/usr/share/tokenizer/ja            5      111.96

Top 4 directories by count of files:
---------------------------------------------------------------------
Directory                                                                        Filecount    Size(MB)
-----------------------------------------------------------------------------  -----------  ----------
/usr/libexec/firmwarecheckers/eficheck/EFIAllowListShipping.bundle/allowlists         2453        1.97
/usr/share/man/man1                                                                   1854       49.18
/usr/share/zsh/5.8/functions                                                          1162        4
/usr/bin                                                                              1086      249.72

Largest files:
---------------------------------------------------------------------
realpath                              Size(MB)  mtime
----------------------------------  ----------  ----------
/usr/share/tokenizer/ja/matrix.bin       68.46  01.01.2020
/usr/share/tokenizer/ja/sys.dic          43.25  01.01.2020
/usr/libexec/apache2/libphp7.so          31.21  01.01.2020
/usr/share/icu/icudt66l.dat              28.75  01.01.2020

Oldest files (mtime):
---------------------------------------------------------------------
realpath                                                    Size(MB)  mtime
--------------------------------------------------------  ----------  ----------
/usr/local/aws-cli/botocore/data/personalize/debug_debug           0  01.01.1970
/usr/local/aws-cli/botocore/data/emr/debug_debug                   0  01.01.1970
/usr/local/aws-cli/botocore/data/sesv2/debug_debug                 0  01.01.1970
/usr/debug_debug                                                   0  01.01.1970

Summary:
              Remark                       Count
0  Scanned Directory                        /usr
1  Count Directories                        1856
2        Count Files                       24514
3    Total Size (GB)                        1.31
4  Collection Errors                           0
5      Creation Time  2020-12-23T17:25:45.384805


Creating Excel File -  Sheet: Summary - BySize - ByFilecount- LargeFiles - OldFiles - SunburstData - RawData 9.827475689 seconds.
Creating HTML file. 0.4460548529999997 seconds.
~~~

### Requirements

- Python 3.6
- numpy
- Pandas
- plotly with plotly.express (express included with 4.14)
- tabulate
- xlsxwriter

