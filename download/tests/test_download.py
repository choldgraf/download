from numpy.testing import assert_equal, assert_array_equal, assert_allclose
from nose.tools import (assert_true, assert_raises, assert_not_equal,
                        assert_not_in)
import os.path as op
import os
from download import download
from download.download import _fetch_file, sizeof_fmt, _TempDir

def _test_fetch(url):
    """Helper to test URL retrieval."""
    tempdir = _TempDir()

    archive_name = op.join(tempdir, "download_test")
    _fetch_file(url, archive_name, timeout=30., verbose=False,
                resume=False)
    assert_raises(Exception, _fetch_file, 'NOT_AN_ADDRESS',
                  op.join(tempdir, 'test'), verbose=False)
    resume_name = op.join(tempdir, "download_resume")
    # touch file
    with open(resume_name + '.part', 'w'):
        os.utime(resume_name + '.part', None)
    _fetch_file(url, resume_name, resume=True, timeout=30.,
                verbose=False)
    assert_raises(ValueError, _fetch_file, url, archive_name,
                  hash_='a', verbose=False)
    assert_raises(RuntimeError, _fetch_file, url, archive_name,
                  hash_='a' * 32, verbose=False)


def test_fetch_file_html():
    """Test file downloading over http."""
    _test_fetch('http://google.com')


def test_fetch_file_ftp():
    """Test file downloading over ftp."""
    _test_fetch('ftp://speedtest.tele2.net/1KB.zip')


def test_sizeof_fmt():
    """Test sizeof_fmt."""
    assert_equal(sizeof_fmt(0), '0 bytes')
    assert_equal(sizeof_fmt(1), '1 byte')
    assert_equal(sizeof_fmt(1000), '1000 bytes')
