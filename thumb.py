import os, glob
import random
import re
import string
import subprocess
import traceback
import shutil
from PIL import Image, ImageFont, ImageDraw
from moviepy.editor import VideoFileClip

def get_video_info(file_path):
    try:
        video = VideoFileClip(file_path)
        duration = video.duration
        resolution = video.size
        return duration, resolution
    except Exception as e:
        print("Erro ao obter informações do vídeo:", e)
        return None, None

def seconds_to_hhmmss(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))

def get_random_filename(ext):
    return ''.join([random.choice(string.ascii_lowercase) for _ in range(20)]) + ext

def create_thumbnail(filename):
    print('Processing:', filename)

    duration, resolution = get_video_info(filename)

    if duration is not None and resolution is not None:
        formatted_duration = seconds_to_hhmmss(duration)
        resolucao = f'{resolution[0]}x{resolution[1]}'
        duracao = f'{formatted_duration}'

    jpg_name = '%s.jpg' % filename
    if os.path.exists(jpg_name):
        print('Thumbnail assumed exists!')
        return

    _, ext = os.path.splitext(filename)
    random_filename = get_random_filename(ext)
    random_filename_2 = get_random_filename(ext)
    print('Rename as %s to avoid decode error...' % random_filename)
    try:
        print(random_filename)
        shutil.copyfile(filename, random_filename)
        
        frag = int(duration / 26)
        while len(glob.glob('*' + random_filename + '-5min.jpg')) < 26:
            proc = subprocess.call(['ffmpeg.exe', '-i', random_filename, '-vf', "fps=1/" + str(frag), '-vsync', 'vfr', '%02d-' + random_filename + '-5min.jpg'])

        os.remove(str(random_filename))
        # Tamanho da thumbnail
        thumbnail_width = 200  # Largura
        thumbnail_height = int(int(resolution[1]) * 200 / int(resolution[0]))#150  # Altura

        # Criar uma nova imagem para a thumbnail
        thumbnail = Image.new('RGB', (thumbnail_width * 5, thumbnail_height * 5 + 62), color='white')

        # Contador para controlar o índice da imagem atual
        index = 0

        # Lista para armazenar os nomes dos arquivos
        file_names = []

        # Loop sobre as imagens geradas pelo código
        tempo = 0
        for image_path in glob.glob('*' + random_filename + '-5min.jpg'):
            tempo += frag
            # Abre a imagem
            image = Image.open(image_path)

            # Redimensiona a imagem para o tamanho da thumbnail
            image.thumbnail((thumbnail_width, thumbnail_height))

            # Calcula a posição para colar a imagem na thumbnail
            x = (index % 5) * thumbnail_width
            y = (index // 5) * thumbnail_height + 62

            # Cola a imagem na posição calculada
            thumbnail.paste(image, (x, y))
            
            font = ImageFont.truetype("arial.ttf", 10)
            draw = ImageDraw.Draw(thumbnail)
            file_name = os.path.splitext(os.path.basename(image_path))[0]
            draw.text((x + 5, y), str(seconds_to_hhmmss(tempo)), fill="white", font=font)
            # Obtém o nome do arquivo e adiciona à lista
            file_name = os.path.splitext(os.path.basename(image_path))[0]
            file_names.append(file_name)

            # Incrementa o contador de índice
            index += 1

            # Para se chegamos ao máximo de 20 imagens
            if index >= 25:
                break

        # Desenha a faixa branca com o nome dos arquivos na parte inferior da thumbnail
        draw = ImageDraw.Draw(thumbnail)
        font = ImageFont.truetype("arial.ttf", 12)
        font2 = ImageFont.truetype("arial.ttf", 25)
        file_names_str = 'File Name: ' + str(filename) + '\nFile Size:    ' + str('{:,}'.format(int(os.path.getsize(filename)/1000))).replace(',','.') + 'Kb\nResolution: ' + str(resolucao) + '\nDuration:    ' + str(duracao)
        text_width, text_height = draw.textsize(file_names_str, font=font)
        file_names_str2 = 'Thumb by Ricardo Madela'
        text_width2, text_height2 = draw.textsize(file_names_str2, font=font)
        draw.rectangle((0, 0, thumbnail_width * 5, text_height + 5), fill="black")
        draw.text((10, 2), file_names_str, fill="white", font=font)
        draw.text(((thumbnail_width * 5 - text_width) / 2, 20), file_names_str2, fill="gray", font=font2)

        thumbnail.save(str(filename) + '.jpg')

        for lixo in glob.glob('*' + str(random_filename) + '*.*'):
            os.remove(lixo)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    for filename in glob.glob("*.*"):
        ext_regex = r"\.(mov|mp4|mpg|mov|mpeg|flv|wmv|avi|mkv|rmvb)$"
        if re.search(ext_regex, filename, re.IGNORECASE):
            create_thumbnail(filename)