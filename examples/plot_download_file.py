from download import download
import matplotlib.pyplot as plt
import pandas as pd

url = "https://ndownloader.figshare.com/files/7010681"
path = download(url, 'boulder-precip.csv', './downloaded/', replace=True)
data = pd.read_csv('./downloaded/boulder-precip.csv')
ax = data.plot('DATE', 'PRECIP')
ax.set(title="Precipitation over time in Boulder, CO")
plt.setp(ax.get_xticklabels(), rotation=45)
plt.tight_layout()
plt.show()
