import os
import markdown

from jinja2 import Environment, FileSystemLoader, PackageLoader


class render():

    def __init__(self, search_path, output, env):
        self.search_path = search_path
        self.output = output
        self.env = env
        self.template = env.get_template('block.html')

    def check(self):
        'check in folder for compiled files'
        l = self.load_files()
        for dirs, dpath, filename in os.walk('out'):
            for i in filename:
                if i in l:
                    l.remove(i)
        return l

    def to_html(self, data):
       md = markdown.Markdown(extensions=['meta'])
       return md.convert(data)

    def to_meta(self, data):
       'read meta header from file' 
       md = markdown.Markdown(extensions=['meta'])
       md.convert(data)
       return md.Meta

    def load_files(self, path):
        'store all files name from directory'
        files = []
        for dirs, dpath, filename in os.walk(path):
            for i in filename:
                files.append(i)
        return files

    def load_content(self, l):
        'read textbody of all files in "in" folder'
        with open(self.search_path+l, 'r') as f:
            return f.read()

    def load_order(self):
        'read order from meta header'
        files = self.load_files('in')
        meta = []
        order = dict()
        for index, i in enumerate(files):
            data = self.load_content(i) 
            meta.append(self.to_meta(data)) 
            order[int(meta[index]['order'][0])] = i[:-3]
        return order

    def build(self):
        'read files in order'
        metas= []
        order = self.load_order()
        for i in order:
            with open(self.output+order[i]+"html", "w") as f:
                print order[i]+"txt"
                data = self.load_content(order[i]+"txt")
                html = self.to_html(data)
                metas.append(self.to_meta(data)) 
                f.write(self.template.render(
                    base_template="template.html",
                    var=html,
                    ab=self.load_config()))

        self.build_links(metas, order)

    def load_config(self):
        conf = dict()
        with open("blog/config.txt") as f:
            for i in f:
                line = i.strip().split(':')
                conf[line[0]] = line[1]
        return conf

    def sort(self, order):
        "sort links based on order"
        li = []
        for i in sorted(order):
            li.append(order[i])
        return li

    def build_links(self, meta, orders):
        'compile index.html with links to the posts'
        titles = self.sort(orders)
        links = map(lambda x: "posts/"+x+"html", titles)
        with open("blog/index.html", "w") as g:
                g.write(self.template.render(
                    base_template="template.html", 
                    links=zip(links, meta), 
                    ab=self.load_config()))

def run():
    loader = FileSystemLoader(searchpath='templates', encoding="utf8")
    m = render('in/', 'blog/posts/',  Environment(loader=loader))
    m.build()

run()