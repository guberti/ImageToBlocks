from PIL import Image
import os, json

obj = []

for filename in os.listdir("textures"):
    path = os.path.join("textures", filename)
    im = Image.open(path)
    pix = im.load()

    avg_sum = [0, 0, 0]

    for i in range(0, im.size[0]):
        for k in range(0, im.size[1]):
            for j in range(0, 3):
                avg_sum[j] += pix[i,k][j]

    pixels = im.size[0] * im.size[1]
    for j in range(0, 3):
        avg_sum[j] /= pixels

    name = filename.split('.')[0]
    print name + " has average color " + str(avg_sum)

    obj.append([name, tuple(avg_sum)])

file = open('colors.json', 'w')
file.write(json.dumps(obj))