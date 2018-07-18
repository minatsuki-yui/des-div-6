import json
import base64
import io
from PIL import Image
# import shutil
import random
import math


# import sys


class Moe(object):
    def __init__(self):
        self.ori_img = None
        self.new_img = None
        self.output_img = None
        self.thumb = None
        self.avg_map = []
        self.base64_imgs = []
        self.imgs = []
        self.new_size = []
        self.from_imgs = []
        # self.new_name = 'new.jpg'
        self.db = 'data.json'
        self.count = 0
        self.finish_length = 0
        self.scale = 50

    def execute(self, big):
        self.ori_name = big
        self.loads_data()
        self.ori_img = self.open_img(big)
        self.make_thumb()
        self.scale_output()
        self.fill_small()
        self.prase_save()

    def scale_output(self):
        self.new_img = self.open_img('tmp.jpg')
        t = [30 * ii for ii in self.new_size]
        self.output_img = self.new_img.resize((t[0], t[1]))

    def loads_data(self):
        with open(self.db, 'r') as j:
            data = json.load(j)

        self.avg_map = data['avg_list']
        # print(self.avg_map)
        self.base64_imgs = data['imgs']
        self.imgs = {k: self.decode_img(v) for k, v in self.base64_imgs.items()}

    @staticmethod
    def decode_img(string):
        # msg = base64.b64decode(msg)

        buffer = io.BytesIO(base64.b64decode(string))
        img = Image.open(buffer)
        return img

    @staticmethod
    def open_img(path):
        return Image.open(path)

    @staticmethod
    def get_random():
        plus = [1, -1]
        return random.choice(plus) * random.randint(0, 2000) / 200

    def make_thumb(self):
        ori_size = self.ori_img.size
        print('origin: ', ori_size)
        self.new_size = [30 * (round(i / 2) // self.scale) for i in ori_size]
        self.thumb = self.ori_img.resize(self.new_size)
        print('new: ', self.new_size)
        self.thumb.save('tmp.jpg')
        # shutil.copy('tmp.jpg', self.new_name)

    @staticmethod
    def distance(color1, color2):
        return math.sqrt(sum([(e1 - e2) ** 2 for e1, e2 in zip(color1, color2)]))

    def best_match(self, sample):
        # print(self.small_map)
        by_distance = sorted(self.avg_map, key=lambda c: self.distance(c, sample))
        b = by_distance[0]
        # print(b)
        return [str(b[0]), str(b[1]), str(b[2])]

    def fill_small(self):
        big_data = list(self.new_img.getdata())
        # print(type(list(big_data)))

        # map(self.decide_each_small, big_data)
        self.finish_length = len(big_data)
        for each in big_data:
            self.decide_each_small(each)
        self.count = 0

    def decide_each_small(self, small):
        after_random = [gbr + self.get_random() for gbr in small]
        closestcolor = self.best_match(after_random)
        # print(closestcolor)
        i = self.imgs['_'.join(closestcolor)]
        self.from_imgs.append(i)
        # sys.stdout.write(f'decided {self.count} / {self.finish_length}')
        # sys.stdout.flush()
        print("\r")
        print(f'decided {self.count} / {self.finish_length}', end='', flush=True)
        self.count += 1

    def prase_save(self):
        x = 30
        y = 30
        ccc = 0
        print(self.new_size)
        print(self.output_img.size)

        for d in range(0, self.new_size[1]):
            for c in range(0, self.new_size[0]):
                box_tuple = (x * c, y * d, x * c + 30, y * d + 30)
                # box = self.new_img.crop(box_tuple)
                # bd = list(box.getdata())
                this_p = self.from_imgs[ccc]
                this = this_p.resize((30, 30))
                self.output_img.paste(this, box=box_tuple)
                print("\r")
                print(f'filled {self.count}', end='', flush=True)
                # sys.stdout.write(f'filled {self.count}')
                # sys.stdout.flush()
                self.count += 1
                ccc += 1

        self.output_img.save(self.ori_name.split('.')[0] + '_done.jpg')


if __name__ == '__main__':
    m = Moe()
    m.execute('example.jpg')
