class Search:
    def search(self, config, path):
        pathList = path.split('>>')
        try:
            for p in pathList:
                config = config[p]
        except KeyError:
            config = None
        return config


def search(config, path):
    s = Search()
    return s.search(config, path)
