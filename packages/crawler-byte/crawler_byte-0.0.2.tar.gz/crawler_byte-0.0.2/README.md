# 🚀 CrawlerByte

**Crawler Byte** is a Python package for recursively crawling directories, collecting file stats, and executing custom actions on each file.  
It’s perfect for building file search tools, batch processors, or custom directory explorers.

---

## 📦 Installation

```bash
$ pip install crawlerbyte
```




## Usage
crawl() takes three arguments
=> path (str), max_depth (int), function (callable)

``` python
from crawlerbyte.crawler import crawl
import os

# Set your target directory
base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def main():
    # Crawl the directory and run a custom action on each file
    result = crawl(base_dir, max_depth=1000, action=lambda f: f)
    print("Crawled Data:", result)

if __name__ == "__main__":
    main()
```