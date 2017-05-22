import os
import os.path as op
import numpy as np
from subprocess import check_output
from zipfile import ZipFile
import logging
import urllib

logger = logging.getLogger('download')


def download(url, name, root_destination='~/data/', zipfile=False,
             replace=False):
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
        print('Creating data folder...')
        os.makedirs(data_dir)

    if not op.isdir(temp_dir):
        print('Creating tmp folder...')
        os.makedirs(temp_dir)

    download_path = _convert_url_to_downloadable(url)

    # Now save to the new destination
    out_path = op.join(data_dir, name)
    if not op.isdir(op.dirname(out_path)):
        print('Creating path {} for output data'.format(out_path))
        os.makedirs(op.dirname(out_path))

    if replace is False and op.exists(out_path):
        print('Replace is False and data exists, so doing nothing. '
              'Use replace==True to re-download the data.')
    elif zipfile is True:
        print('Extracting zip file...')
        path_temp = op.join(temp_dir, name)
        _fetch_file(download_path, path_temp)
        myzip = ZipFile(path_temp)
        myzip.extractall(out_path)
        os.remove(path_temp)
    else:
        if len(name) == 0:
            raise ValueError('Cannot overwrite the root data directory')
        _fetch_file(download_path, out_path)
        print('Successfully moved file to {}'.format(out_path))
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
                hash_=None, timeout=10., verbose=False):
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
        Verbose level for the HTTP request.
    """
    # Adapted from NISL:
    # https://github.com/nisl/tutorial/blob/master/nisl/datasets.py
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
        logger.info('Downloading data from %s (%s)\n'
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
        fun(url, temp_file_name, initial_size, file_size, verbose)

        # check md5sum
        if hash_ is not None:
            logger.info('Verifying download hash.')
            md5 = md5sum(temp_file_name)
            if hash_ != md5:
                raise RuntimeError('Hash mismatch for downloaded file %s, '
                                   'expected %s but got %s'
                                   % (temp_file_name, hash_, md5))
        shutil.move(temp_file_name, file_name)
        if print_destination is True:
            logger.info('File saved as %s.\n' % file_name)
    except Exception:
        logger.error('Error while fetching file %s.'
                     ' Dataset fetching aborted.' % url)
        raise
