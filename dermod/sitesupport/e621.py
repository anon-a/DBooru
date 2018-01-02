username = ""
domain = 'https://e621.net'
query = "fav:{}".format(username)
endpoint = "/post/index.json?tags={}".format(query)
paginator = "page={}"
empty_page = '\[\]$' # Must be regexp
slp = 0.5 # Defines delay between requests
params = '' # Additional API params

class Module:
    def __init__(self):
        self.tags = []
        self.ids = []
        self.img_links = []
        self.format = []
        self.height = []
        self.width = []

    def parse(self, string):
        string = string.split('"id":')[1:]
        self.ids = []
        self.form = []
        self.links = []
        self.tags = []
        self.height = []
        self.width = []
        for i in string:
            self.ids.append(i.split(',"')[0])
            self.tags.append(i.split('"tags":"')[1]\
            .split('",')[0]\
            .replace(" ", ', ')\
            .replace('_', ' '))
            k = i.split('"width":')[1]
            k = k.split(',')[0]
            self.width.append(k)
            k = i.split('"height":')[1]
            k = k.split(',')[0]
            self.height.append(k)
            k = i.split('","file_ext":"')[1]
            k = k.split('","preview_url')[0].split('","')[0]
            self.form.append(k)
            k = i.split('"file_url":"')[1]
            k = k.split('","file_ext":"')[0]
            self.links.append(k)
