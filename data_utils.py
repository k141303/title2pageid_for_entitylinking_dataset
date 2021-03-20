import re

import csv
import json

class DataUtils(object):
    class JsonL(object):
        def load(file_path):
            with open(file_path, "r") as f:
                return [*map(json.loads, f)]

        def json_dumps(d):
            return json.dumps(d, ensure_ascii=False)

        @classmethod
        def save(cls, file_path, data):
            dumps = map(cls.json_dumps, data)
            with open(file_path, "w") as f:
                f.write("\n".join(dumps))

        def json_dumps_for_view(d):
            return json.dumps(d, ensure_ascii=False, indent=4, separators=(',', ': '))

        @classmethod
        def save_for_view(cls, file_path, data):
            dumps = map(cls.json_dumps_for_view, data)
            with open(file_path, "w") as f:
                f.write("\n".join(dumps))

    class Csv(object):
        def load(file_path, encoding="utf-8"):
            with open(file_path, 'r', encoding=encoding) as f:
                return [*csv.reader(f)]

class Title2Pageid(object):
    def __init__(self, titles_path, redirects_path):
        self.title2pageid = self._load_titles(titles_path)
        self.redirect2pageid = self._load_redirects(redirects_path)

    def _space2ub(self, title):
        return re.sub("\s", "_", title)

    def _load_titles(self, titles_path):
        data = DataUtils.JsonL.load(titles_path)
        return {self._space2ub(d["title"]):d["pageid"] for d in data}

    def _load_redirects(self, redirects_path):
        data = DataUtils.JsonL.load(redirects_path)
        return {self._space2ub(d["src"]["title"]): d["dst"]["pageid"] for d in data}

    def convert(self, title):
        title = title.strip()
        pageid = self.title2pageid.get(self._space2ub(title))
        if pageid is not None:
            return pageid

        pageid = self.redirect2pageid.get(self._space2ub(title))
        return pageid
