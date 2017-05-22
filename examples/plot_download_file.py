from download import download
import matplotlib.pyplot as plt

url = "https://img.memesuper.com/ebb84f51fc79439a237cbaf8913f838d_best-jokes-continues-homer-simpson-woohoo-meme_788-500.jpeg"

path = download(url, 'wohoo.gif', './downloaded/', replace=True)
im = plt.imread(path)
plt.imshow(im)
