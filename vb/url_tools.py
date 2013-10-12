import urlparse


def strip_url(url, num=-1):
    """strip_url(url) returns url with query removed, e.g.,
    strip_url('https://www.google.com/search?q=url+parse') ==
                                        'http://www.google.com/search'
    
    strip_url(url, num) returns url with only num directories in path, e.g.,
    strip_url('http://ekstrabladet.dk/flash/udland/article28591.ece', 1) ==
                                            'http://ekstrabladet.dk/flash'
    """
    url = urlparse.urlparse(url)
    if num == -1:
        return urlparse.urlunparse((url.scheme, url.netloc,
                                    url.path, '', '', ''))
    else:
        path = url.path.replace('/', ' ').split()
        path = '/'.join(path[:num])
        return urlparse.urlunparse((url.scheme, url.netloc
                                    path, '', '', ''))

def strip_urls(urls, num=-1):
    for url in urls:
        yield strip_url(url, num)
