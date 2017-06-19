"""Utilities to download a file. Heavily copied from MNE-python."""
import os
import os.path as op
from subprocess import check_output
import urllib
from zipfile import ZipFile
from tqdm import tqdm
import logging
from math import log, ceil
import time
import sys
import shutil


def download(url, name, root_destination='~/data/', zipfile=False,
             replace=False, verbose=True):
    """Download a URL.

    This will download a file and store it in a '~/data/` folder,
    creating directories if need be. It will also work for zip
    files, in which case it will unzip all of the files to the
    desired location.

    Parameters
    ----------
    url : string
        The url of the file to download. This may be a dropbox
        or google drive "share link", or a regular URL. If it
        is a share link, then it should point to a single file and
        not a folder. To download folders, zip them first.
    name : string
        The name / path of the file for the downloaded file, or
        the folder to zip the data into if the file is a zipfile.
    root_destination : string
        The root folder where data will be downloaded.
    zipfile : bool
        Whether the URL points to a zip file. If yes, it will be
        unzipped to ``root_destination/<name>``.
    replace : bool
        If True and the URL points to a single file, overwrite the
        old file if possible.
    verbose : bool
        Whether to print download status to the screen.

    Returns
    -------
    out_path : string
        A path to the downloaded file (or folder, in the case of
        a zip file).
    """
    # Make sure we have directories to dump files
    data_dir = op.expanduser(root_destination)
    temp_dir = op.join(data_dir, 'tmp')
    if not op.isdir(data_dir):
        if verbose:
            tqdm.write('Creating data folder...')
        os.makedirs(data_dir)

    if not op.isdir(temp_dir):
        if verbose:
            tqdm.write('Creating tmp folder...')
        os.makedirs(temp_dir)

    download_path = _convert_url_to_downloadable(url)

    # Now save to the new destination
    out_path = op.join(data_dir, name)
    if not op.isdir(op.dirname(out_path)):
        if verbose:
            tqdm.write('Creating path {} for output data'.format(out_path))
        os.makedirs(op.dirname(out_path))

    if replace is False and op.exists(out_path):
        if verbose:
            tqdm.write('Replace is False and data exists, so doing nothing. '
                       'Use replace==True to re-download the data.')
    elif zipfile is True:
        if verbose:
            tqdm.write('Extracting zip file...')
        path_temp = op.join(temp_dir, name)
        _fetch_file(download_path, path_temp, verbose=verbose)
        myzip = ZipFile(path_temp)
        myzip.extractall(out_path)
        os.remove(path_temp)
    else:
        if len(name) == 0:
            raise ValueError('Cannot overwrite the root data directory')
        _fetch_file(download_path, out_path, verbose=verbose)
        tqdm.write('Successfully moved file to {}'.format(out_path))
    return out_path


def _convert_url_to_downloadable(url):
    """Convert a url to the proper style depending on its website."""

    if 'drive.google.com' in url:
        raise ValueError('Google drive links are not currently supported')
        # For future support of google drive
        file_id = url.split('d/').split('/')[0]
        base_url = 'https://drive.google.com/uc?export=download&id='
        out = '{}{}'.format(base_url, file_id)
    elif 'dropbox.com' in url:
        if 'www' not in url:
            raise ValueError('If using dropbox, must give a link w/ "www" in it')
        out = url.replace('www.dropbox.com', 'dl.dropboxusercontent.com')
    elif 'github.com' in url:
        out = url.replace('github.com', 'raw.githubusercontent.com')
        out = out.replace('blob/', '')
    else:
        out = url
    return out

def _fetch_file(url, file_name, print_destination=True, resume=True,
                hash_=None, timeout=10., verbose=True):
    """Load requested file, downloading it if needed or requested.

    Parameters
    ----------
    url: string
        The url of file to be downloaded.
    file_name: string
        Name, along with the path, of where downloaded file will be saved.
    print_destination: bool, optional
        If true, destination of where file was saved will be printed after
        download finishes.
    resume: bool, optional
        If true, try to resume partially downloaded files.
    hash_ : str | None
        The hash of the file to check. If None, no checking is
        performed.
    timeout : float
        The URL open timeout.
    verbose : bool
        Whether to print download status.
    """
    # Adapted from NISL and MNE-python:
    # https://github.com/nisl/tutorial/blob/master/nisl/datasets.py
    # https://martinos.org/mne
    if hash_ is not None and (not isinstance(hash_, string_types) or
                              len(hash_) != 32):
        raise ValueError('Bad hash value given, should be a 32-character '
                         'string:\n%s' % (hash_,))
    temp_file_name = file_name + ".part"
    try:
        # Check file size and displaying it alongside the download url
        u = urllib.request.urlopen(url, timeout=timeout)
        u.close()
        # this is necessary to follow any redirects
        url = u.geturl()
        u = urllib.request.urlopen(url, timeout=timeout)
        try:
            file_size = int(u.headers.get('Content-Length', '1').strip())
        finally:
            u.close()
            del u
        if verbose:
            tqdm.write('Downloading data from %s (%s)\n'
                        % (url, sizeof_fmt(file_size)))

        # Triage resume
        if not os.path.exists(temp_file_name):
            resume = False
        if resume:
            with open(temp_file_name, 'rb', buffering=0) as local_file:
                local_file.seek(0, 2)
                initial_size = local_file.tell()
            del local_file
        else:
            initial_size = 0
        # This should never happen if our functions work properly
        if initial_size > file_size:
            raise RuntimeError('Local file (%s) is larger than remote '
                               'file (%s), cannot resume download'
                               % (sizeof_fmt(initial_size),
                                  sizeof_fmt(file_size)))

        scheme = urllib.parse.urlparse(url).scheme
        fun = _get_http if scheme in ('http', 'https') else _get_ftp
        fun(url, temp_file_name, initial_size, file_size, verbose, ncols=80)

        # check md5sum
        if hash_ is not None:
            if verbose:
                tqdm.write('Verifying download hash.')
            md5 = md5sum(temp_file_name)
            if hash_ != md5:
                raise RuntimeError('Hash mismatch for downloaded file %s, '
                                   'expected %s but got %s'
                                   % (temp_file_name, hash_, md5))
        shutil.move(temp_file_name, file_name)
        if print_destination is True:
            tqdm.write('File saved as %s.\n' % file_name)
    except Exception:
        raise RuntimeError('Error while fetching file %s.'
                           ' Dataset fetching aborted.' % url)


def _get_ftp(url, temp_file_name, initial_size, file_size, verbose_bool,
             ncols=80):
    """Safely (resume a) download to a file from FTP."""
    # Adapted from: https://pypi.python.org/pypi/fileDownloader.py
    # but with changes

    parsed_url = urllib.parse.urlparse(url)
    file_name = os.path.basename(parsed_url.path)
    server_path = parsed_url.path.replace(file_name, "")
    unquoted_server_path = urllib.parse.unquote(server_path)

    data = ftplib.FTP()
    if parsed_url.port is not None:
        data.connect(parsed_url.hostname, parsed_url.port)
    else:
        data.connect(parsed_url.hostname)
    data.login()
    if len(server_path) > 1:
        data.cwd(unquoted_server_path)
    data.sendcmd("TYPE I")
    data.sendcmd("REST " + str(initial_size))
    down_cmd = "RETR " + file_name
    assert file_size == data.size(file_name)
    progress = tqdm(total=file_size, initial=initial_size, desc='file_sizes',
                    ncols=ncols, unit='B', unit_scale=True)

    # Callback lambda function that will be passed the downloaded data
    # chunk and will write it to file and update the progress bar
    mode = 'ab' if initial_size > 0 else 'wb'
    with open(temp_file_name, mode) as local_file:
        def chunk_write(chunk):
            return _chunk_write(chunk, local_file, progress)
        data.retrbinary(down_cmd, chunk_write)
        data.close()

def _get_http(url, temp_file_name, initial_size, file_size, verbose_bool,
              ncols=80):
    """Safely (resume a) download to a file from http(s)."""
    # Actually do the reading
    req = urllib.request.Request(url)
    if initial_size > 0:
        req.headers['Range'] = 'bytes=%s-' % (initial_size,)
    try:
        response = urllib.request.urlopen(req)
    except Exception:
        # There is a problem that may be due to resuming, some
        # servers may not support the "Range" header. Switch
        # back to complete download method
        tqdm.write('Resuming download failed (server '
                   'rejected the request). Attempting to '
                   'restart downloading the entire file.')
        del req.headers['Range']
        response = urllib.request.urlopen(req)
    total_size = int(response.headers.get('Content-Length', '1').strip())
    if initial_size > 0 and file_size == total_size:
        tqdm.write('Resuming download failed (resume file size '
                   'mismatch). Attempting to restart downloading the '
                   'entire file.')
        initial_size = 0
    total_size += initial_size
    if total_size != file_size:
        raise RuntimeError('URL could not be parsed properly')
    mode = 'ab' if initial_size > 0 else 'wb'
    progress = tqdm(total=total_size, initial=initial_size, desc='file_sizes',
                    ncols=ncols, unit='B', unit_scale=True)

    chunk_size = 8192  # 2 ** 13
    with open(temp_file_name, mode) as local_file:
        while True:
            t0 = time.time()
            chunk = response.read(chunk_size)
            dt = time.time() - t0
            if dt < 0.005:
                chunk_size *= 2
            elif dt > 0.1 and chunk_size > 8192:
                chunk_size = chunk_size // 2
            if not chunk:
                break
            local_file.write(chunk)
            progress.update(len(chunk))

def md5sum(fname, block_size=1048576):  # 2 ** 20
    """Calculate the md5sum for a file.

    Parameters
    ----------
    fname : str
        Filename.
    block_size : int
        Block size to use when reading.

    Returns
    -------
    hash_ : str
        The hexadecimal digest of the hash.
    """
    md5 = hashlib.md5()
    with open(fname, 'rb') as fid:
        while True:
            data = fid.read(block_size)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def _chunk_write(chunk, local_file, progress):
    """Write a chunk to file and update the progress bar."""
    local_file.write(chunk)
    progress.update(len(chunk))


def sizeof_fmt(num):
    """Turn number of bytes into human-readable str.

    Parameters
    ----------
    num : int
        The number of bytes.

    Returns
    -------
    size : str
        The size in human-readable format.
    """
    units = ['bytes', 'kB', 'MB', 'GB', 'TB', 'PB']
    decimals = [0, 0, 1, 2, 2, 2]
    if num > 1:
        exponent = min(int(log(num, 1024)), len(units) - 1)
        quotient = float(num) / 1024 ** exponent
        unit = units[exponent]
        num_decimals = decimals[exponent]
        format_string = '{0:.%sf} {1}' % (num_decimals)
        return format_string.format(quotient, unit)
    if num == 0:
        return '0 bytes'
    if num == 1:
        return '1 byte'
