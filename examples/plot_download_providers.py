"""
Download from Dropbox, Google Drive, and Github
-----------------------------------------------

It's also possible to download files from Github, Google Drive, and Dropbox.
While you can go through a little extra effort to get a direct download link,
``download`` will try to make things a little bit easier for you.
"""
from download import download
import matplotlib.pyplot as plt
import os.path as op
import shutil as sh

###############################################################################
# You can simply find the link to your content on GitHub and give it directly
# to Download. It will try to be smart about converting the link where
# necessary.

url = "https://drive.google.com/file/d/0B8VZ4vaOYWZ3c3Y1c2ZQX01yREk/view?usp=sharing"
path = download(url, './downloaded/citation.png', replace=True)

fig, ax = plt.subplots()
im = plt.imread(path)
ax.imshow(im)
ax.set_axis_off()

###############################################################################
# The same works for Google Drive content.
#
# .. note:: Make sure your sharing options let any user access the file.

url = "https://github.com/choldgraf/download/blob/master/examples/data/citation.png"
path2 = download(url, './downloaded/citation2.png', replace=True)

fig, ax = plt.subplots()
im2 = plt.imread(path)
ax.imshow(im2)
ax.set_axis_off()

###############################################################################
# Dropbox links also work, though in this case ``download`` will use
# the ``requests`` library to download the file. This is because Dropbox
# requires cookies and requests is smart about handling this.

url = "https://www.dropbox.com/s/rlndt99tss65418/citation.png?dl=0"
path3 = download(url, './downloaded/citation3.png', replace=True)

fig, ax = plt.subplots()
im3 = plt.imread(path3)
ax.imshow(im)
ax.set_axis_off()

sh.rmtree('./downloaded')
plt.show()
