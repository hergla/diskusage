# diskusage
Disk Usage 

Collect files information from directory and show top usage.

1. Largest directories by size.
2. Directories by count of files.
3. Largest files
4. Oldest files

Can create Excel file with collected information.
Can create html file with a sunburst representation.


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


