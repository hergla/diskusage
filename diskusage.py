#!/usr/bin/env python3

import argparse
import csv
from datetime import datetime
import os
import sys
from os.path import join
from timeit import Timer
import pandas as pd
import plotly.express as px
from tabulate import tabulate
from pathlib import PurePath, PureWindowsPath, PurePosixPath

pd.set_option('display.max_rows', None)
pd.options.display.float_format = '{:.2f}'.format

VERSION = "1.0.9"

'''
Pandas Dataframe -> 'directory', 'filename', 'size', 'mtime', 'atime', 'ctime', 'realpath'
'''

def run_time(func, *args, **kwargs):
    '''
    Mesuare runtime for function with args/kwargs
    '''
    returns = []

    def wrapped():
        returns.append(func(*args, **kwargs))

    timer = Timer(wrapped)
    delta = timer.timeit(1)
    return round(delta, 2), returns.pop()


def file_sizedir(sortby, count=16):
    '''
    Calculate count files and size per directory.
    '''
    filesInDir = df.groupby('directory').agg(
        {'filename': 'count',
         'size': 'sum'
         }).sort_values(by=[sortby], ascending=False)
    filesInDir['sizemb'] = filesInDir['size'].apply(lambda x: round(x / 1024 / 1024, 2))
    outdf = filesInDir.rename(columns={'filename': 'filecount'})
    return outdf.head(count)


def largest_files(count=16):
    '''
    :param count: number of largest files.
    :return: df with largest files
    '''
    largest = df[['realpath', 'sizemb', 'mtime', 'size']].nlargest(count, columns='size')
    return largest


def oldest_files(count=16):
    filt = df['filename'] == '_'   # remove our dummy entries
    oldest = df.drop(index=df[filt].index)
    oldest = oldest.sort_values(by='mtime', ascending=False)
    return oldest.tail(count)


def collect_data(path='.'):
    data = list()
    progress = 0
    error_count = 0
    progress_chars = ['|', '\\', '-', '/']
    print("collecting  ", end="", flush=True)
    for root, dirs, files in os.walk(path):
        if not files:  # need a dummy entry for sunburst.
            dtime = datetime.fromtimestamp(0)
            root = PureWindowsPath(root).as_posix()
            data.append((root, '_', 0, dtime, dtime, dtime))
        for file in files:
            progress += 1
            if not progress % 199 and showprogress:
                print(f'\b{progress_chars[progress % 4]}', end="")
                sys.stdout.flush()
            try:
                fileStat = os.lstat(join(root, file))
                mtime = datetime.fromtimestamp(fileStat.st_mtime)
                atime = datetime.fromtimestamp(fileStat.st_atime)
                ctime = datetime.fromtimestamp(fileStat.st_ctime)
                root = PureWindowsPath(root).as_posix()
                recode_file = file.encode('utf-8', errors='replace').decode()
                data.append((root, recode_file, fileStat.st_size, mtime, atime, ctime))
            except:
                error_count += 1
        if '.snapshot' in dirs:  # drop Netapp snapdir visible
            dirs.remove('.snapshot')
    print("")
    return data, error_count


def excel(df, excelfile):
    def set_num_format(workbook, colname):
        format_col = {
            'size': '#,##0.00',
            'sizemb': '#,##0.00',
            'filecount': '#,##0',
            'Count': '0',
            'default': ''
        }
        if not colname in format_col:
            colname = 'default'
        cell_format = workbook.add_format()
        cell_format.set_num_format(format_col[colname])
        return cell_format

    def auto_size_col(df, sheet_name, writer, reset_index=True):
        if reset_index:
            df.reset_index(level=0, inplace=True)
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        workbook = writer.book
        worksheet = writer.sheets[sheet_name]
        worksheet.freeze_panes(1, 0)
        for i, col in enumerate(df.columns):
            cell_format = set_num_format(workbook, col)
            column_len = max(df[col].astype(str).str.len().max() + 4, len(col) + 1)
            worksheet.set_column(i, i, width=column_len, cell_format=cell_format)

    def sunburst4excel(dfe):
        sep = '/'
        pe_max = 0
        data = []
        for dirx in dfe.directory:
            pe = dirx.split(sep)
            if len(pe) > pe_max:
                pe_max = len(pe)
        for i in dfe.itertuples():
            dirarr = i.directory.split(sep)
            a = pe_max - len(dirarr)
            dirarr += [""] * a
            dirarr.append(i.size)
            data.append(dirarr)
        return pd.DataFrame(data)

    try:
        print("Sheet: ", end="")
        with pd.ExcelWriter(excelfile, engine="xlsxwriter") as writer:
            print("Summary - ", end="", flush=True)
            auto_size_col(df_summary, sheet_name="Summary", writer=writer)
            print("BySize - ", end="", flush=True)
            df_fsd = file_sizedir(sortby='size', count=1000000)
            auto_size_col(df_fsd, sheet_name="BySize", writer=writer)
            print("ByFilecount- ", end="", flush=True)
            df_fcd = file_sizedir(sortby='filename', count=1000000)
            auto_size_col(df_fcd, sheet_name="ByFilecount", writer=writer)
            del df_fcd
            print("LargeFiles - ", end="", flush=True)
            df_lf = largest_files(count=1000000)[['realpath', 'sizemb', 'mtime']]
            df_lf.reset_index(drop=True, inplace=True)
            auto_size_col(df_lf, sheet_name="LargeFiles", writer=writer, reset_index=False)
            del df_lf
            print("OldFiles - ", end="", flush=True)
            df_of = oldest_files(count=1000000)[['mtime', 'atime', 'ctime', 'sizemb', 'realpath']]
            df_of.reset_index(drop=True, inplace=True)
            auto_size_col(df_of, sheet_name="OldFiles", writer=writer, reset_index=False)
            del df_of
            #print("SunburstData - ", end="", flush=True)
            #df_sunburst = sunburst4excel(df_fsd)
            #df_sunburst.to_excel(writer, sheet_name="SunburstData")
            #del df_sunburst
            #print("RawData", end="", flush=True)
            #df.to_excel(writer, sheet_name="RawData")
    except Exception as e:
        print("failed: ", end="")
        print(e)


def plotit(dfp, htmlfile):
    '''
    Create Sunburst with Plotly
    :param dfp:
    '''
    sep = '/'
    df_plot = dfp.groupby('directory').agg({"size": "sum",
                                            "sizemb": "sum",
                                            "filename": "count"}) #.sort_values(by='size', ascending=False)
    df_plot.reset_index(level=0, inplace=True)
    # !!! Test mit Daten von Windows
    # df_plot['directory'] = df_plot['directory'].str.replace('\\', '/')  # Kommt von Windows daher drehen

    df_plot['count_dirs'] = df_plot['directory'].apply(lambda x: len(x.split(sep)))
    #df_plot['parentdir'] = df_plot['directory'].apply(lambda x: os.path.split(x)[0] or "")
    df_plot['parentdir'] = df_plot['directory'].apply(lambda x: str(PurePosixPath(x).parent) or "")
    filt = (df_plot['directory'] == '.') & (df_plot['parentdir'] == '.')
    df_plot.loc[filt, 'parentdir'] = ''
    df_plot.rename(columns={'filename': 'filecount'}, inplace=True)
    df_plot.sort_values(by='count_dirs', ascending=False, inplace=True)
    #df_plot.to_csv("debug1.csv", index=False, sep='\t', quoting=csv.QUOTE_ALL)
    df_plot.set_index('directory', inplace=True)
    copy_df = df_plot.copy()
    for i in df_plot.itertuples():
        this_dir = i.Index
        parent_dir = i.parentdir
        old_size = copy_df.at[this_dir, 'size']
        try:
            old_size_parent = copy_df.at[parent_dir, 'size']
            new_size = old_size + old_size_parent
            copy_df.at[parent_dir, 'size'] = new_size
        except:     # root dir has no parent
            pass
    copy_df.reset_index(inplace=True)
    copy_df['sizemb'] = copy_df['size'].apply(lambda x: round(x/1024/1024, 2))
    df_plot = copy_df.sort_values(by='size', ascending=False).head(100)
    #df_plot.to_csv("debug.csv", index=False, sep='\t', quoting=csv.QUOTE_ALL)
    fig = px.sunburst(df_plot,
                      ids="directory",
                      labels="directory",
                      parents="parentdir",
                      names="directory",
                      values="size",
                      hover_data=['filecount', 'sizemb'],
                      branchvalues="total",
                      color='size',
                      color_continuous_scale='Greens',
                      )
    fig.update_layout(
        # grid= dict(columns=2, rows=3),
        margin=dict(t=0, l=0, r=0, b=0),
        width=1300, height=900
    )
    fig.write_html(htmlfile)


def parseArgs():
    HELP = {'top': 'Show the top <n> entries.',
            'writecsv': 'Write dataframe to CSV file',
            'readcsv': 'Read dataframe from CSV file. Don\'t scan directory again.',
            'excel': 'Create Excel file.',
            'html': 'Create HTML file with sunburst animation.',
            'progress': 'show progress animation.',
            }
    parser = argparse.ArgumentParser()
    parser.add_argument("directoy", nargs='?', help="Directory to analyze. Default, current dir.", default='.')
    parser.add_argument("-t", "--top", type=int, help=HELP['top'], default=16)
    parser.add_argument("-w", "--writecsv", type=str, help=HELP['writecsv'])
    parser.add_argument("-r", "--readcsv", type=str, help=HELP['readcsv'])
    parser.add_argument("-x", "--xlsx", type=str, help=HELP['excel'])
    parser.add_argument("-s", "--html", type=str, help=HELP['html'])
    parser.add_argument("-p", "--progress", action="store_true", help=HELP['progress'])
    # args=parser.parse_args(args=['/usr'])
    args = parser.parse_args()
    return args


"""
# Main
"""
if __name__ == '__main__':
    args = parseArgs()
    scandir = args.directoy
    readcsv = args.readcsv
    writecsv = args.writecsv
    excelfile = args.xlsx
    htmlfile = args.html
    top = args.top
    showprogress = args.progress
    createTime = datetime.isoformat(datetime.now())


    if not readcsv:
        realpath_to_scan = os.path.realpath(scandir)
    else:
        realpath_to_scan = 'CSV file'
    if not '__file__' in globals():
        prg = "developing"
    else:
        prg = os.path.realpath(__file__)
    print(f'''
    {prg}
    ==============================================================================
    Directory (notempty) sizes from {realpath_to_scan}
    ==============================================================================
    ''')
    error_count = 0

    if readcsv and os.path.exists(readcsv):
        print("Load data from CSV file.")
        parse_dates = ['mtime', 'atime', 'ctime']
        dtypes = {'directory': 'str', 'filename': 'str', 'size': 'float',
                  'mtime': 'str', 'atime': 'str', 'ctime': 'str',
                  'realpath': 'str', 'sizemb': 'float'}
        # df = pd.read_csv('/var/tmp/diskusage.csv', parse_dates=parse_dates, dtype=dtypes, sep='\t', header=0)
        runtime_csv, df = run_time(pd.read_csv, readcsv, parse_dates=parse_dates, dtype=dtypes, sep='\t', header=0)
        df['directory'] = df['directory'].apply(lambda x: PureWindowsPath(x).as_posix())
        df['realpath'] = df['realpath'].apply(lambda x: PureWindowsPath(x).as_posix())
        print(f"Loading CSV took {runtime_csv} seconds")
    else:
        # data, error_count = collect_data(path=scandir)
        runtime_collect, returns = run_time(collect_data, path=scandir)
        data = returns[0]
        error_count = returns[1]
        print(f"Scanning completed in {runtime_collect} seconds")
        print(f"Errors during collection: {error_count}")
        df = pd.DataFrame(data, columns=['directory', 'filename', 'size', 'mtime', 'atime', 'ctime'])
        # runtime_load_df, df = run_time(pd.DataFrame, data,
        #                               columns=['directory', 'filename', 'size', 'mtime', 'atime', 'ctime'])
        # print(f"Loadind Pandas took {runtime_load_df} seconds")
        data = []
        # Add realpath
        df['realpath'] = df.apply(lambda x: str(PurePosixPath(x.directory).joinpath(x.filename)), axis=1)
        # Add size in MiB
        df['sizemb'] = df['size'].apply(lambda x: round(x / 1024 / 1024, 2))
        if writecsv:
            df.to_csv(writecsv, index=False, sep='\t', quoting=csv.QUOTE_ALL, errors='replace')

    print()

    if htmlfile:
        print("Creating HTML file.", end="", flush=True)
        runtime, _ = run_time(plotit, df, htmlfile)
        print(f" {runtime} seconds.")

    print("Files analyzed: {}".format(len(df.index)))
    total_size = df['size'].sum()
    total_sizegb = total_size / 1024 / 1024 / 1024
    print(f"Total size: {total_sizegb} GB")
    print(f"\nTop {top} directories by size:")
    print("---------------------------------------------------------------------")
    print(tabulate(file_sizedir(sortby='size', count=top)[['filecount', 'sizemb']],
                   headers=['Directory', 'Filecount', 'Size(MB)']))

    print(f"\nTop {top} directories by count of files:")
    print("---------------------------------------------------------------------")
    print(tabulate(file_sizedir(sortby='filename', count=top)[['filecount', 'sizemb']],
                   headers=['Directory', 'Filecount', 'Size(MB)']))

    print("\nLargest files:")
    print("---------------------------------------------------------------------")
    largest = largest_files(count=top)
    largest['mtime'] = largest['mtime'].dt.strftime('%d.%m.%Y')
    print(tabulate(largest[['realpath', 'sizemb', 'mtime']],
                   showindex=False, headers=['realpath', 'Size(MB)', 'mtime']))

    print("\nOldest files (mtime):")
    print("---------------------------------------------------------------------")
    oldest = oldest_files(count=top)
    oldest['mtime'] = oldest['mtime'].dt.strftime('%d.%m.%Y')
    print(tabulate(oldest[['realpath', 'sizemb', 'mtime']],
                   showindex=False, headers=['realpath', 'Size(MB)', 'mtime']))

    count_files = len(df.index)
    x = df.pivot_table(index='directory', aggfunc='size')
    count_directories = len(x.index)

    summary = {
        'Remark': ['Scanned Directory', 'Count Directories', 'Count Files', 'Total Size (GB)', 'Collection Errors',
                   'Creation Time'],
        'Count': [scandir, count_directories, count_files, total_sizegb, error_count, createTime]}
    df_summary = pd.DataFrame(summary)
    print("\nSummary:")
    #print(df_summary)
    print()
    # Excel handling
    if excelfile:
        print(f"\nCreating Excel File -  ", end="")
        #excel(df, excelfile)
        runtime, _ = run_time(excel, df, excelfile)
        print(f" {runtime} seconds.")
    print()
    sys.exit(0)
