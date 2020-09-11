import os
import re
import shutil
from config import get_config, create_config_from_obj, create_error_log
from PIL import Image
import datetime

CONFIG = dict()

class Media(object):
    def __init__(self, config_name = 'config.json'):
        self.config_name = config_name
        self.CONFIG = get_config(self.config_name)
        self.image_formats = self.CONFIG['media_formats']['images']
        self.video_formats = self.CONFIG['media_formats']['videos']
        self.file_formats = self.CONFIG['media_formats']['files']
        self.posts_path = self.CONFIG['posts_path']
        self.post_formats = self.CONFIG['post_formats']
        self.media_directory = self.CONFIG['media_directory']
        self.media_dist_directory = self.CONFIG['media_dist_directory']

    def get_media_from_paths(self, post_path):
        #Убираем последний слеш /
        try:
            src_files = os.listdir(post_path['src_path'][:-1])
            src_medias = list(filter(self.media_filter, src_files))
            src_images = list(filter(self.image_filter, src_files))
        except:
            self.error_log('Can\'t find source dir')
            src_medias = None
            src_images = None
        
        try:
            dst_files = os.listdir(post_path['dst_path'][:-1])
            dst_medias = list(filter(self.media_filter, dst_files))
        except:
            self.error_log('Can\'t find distanation dir for comparing media files')
            dst_medias = None     
                
        return [src_medias, dst_medias, src_images]

    #TODO: буферизация в json
    def get_media_paths(self):
        categories = os.listdir(self.posts_path)

        data = list()

        for cat in categories:
            years = os.listdir(self.posts_path + '/' + cat)
            cat_path = cat.split('-')[1]

            if years:
                for year in years:
                    news = os.listdir(self.posts_path + '/' + cat + '/' + year)

                    for post in news:
                        folder_name = list(filter(lambda x: x.endswith(tuple(self.post_formats)), os.listdir(self.posts_path + '/' + cat + '/' + year + '/' + post)))[0].split('.')[0]
                        
                        post_path = { 
                            'src_path': self.posts_path + '/' + cat + '/' + year + '/' + post + '/' + self.media_directory + '/',
                            'dst_path': self.posts_path.replace('\\_posts', '') + '/' + self.media_dist_directory + '/' + cat_path + '/' + year + '/' + folder_name + '/'
                        }
                        data.append(post_path)

        self.media_data_paths = data
        return data

    def are_files_converted(self, post):
        images_without_webp = list(filter(lambda x: not x.endswith('.webp') and re.match(r'^\d{1,2}t?p?\.', x), self.get_media_from_paths(post)[2]))
        images_without_webp = [el.split('.')[0] for el in images_without_webp]
        images_with_webp = list(filter(lambda x: x.endswith('.webp')  and re.match(r'^\d{1,2}t?p?\.', x), self.get_media_from_paths(post)[2]))
        images_with_webp = [el.split('.')[0] for el in images_with_webp]

        if images_without_webp == images_with_webp:
            return True
        return False

    def are_files_released(self, post):
        medias = self.get_media_from_paths(post)
        return False if not medias[1] or list(set(medias[0]) ^ set(medias[1])) else True

    def error_log(self, message):
        msg = str(datetime.datetime.today().strftime("%Y-%m-%d")) + ' [' + str(datetime.datetime.today().strftime("%H:%M:%S")) + ']:\t' + str(message) + '\n'
        create_error_log(msg)

    def convert_2_webp(self, post):
        medias = self.get_media_from_paths(post)[2]
        for file in medias:
            try:
                image = Image.open(post['src_path'] + file)
                image = image.convert('RGB')
                image.save((post['src_path'] + file).rsplit('.', 1)[0] + '.webp', 'webp')

            except Exception as e:
                print(e)     
                self.error_log(str(e) + 'Can\'t convert images to .webp')

    def convert_all_images(self, data):
        if not data:
            data = self.media_data_paths

        for post in data:
            #Проверяем: конвертированы ли файлы внутри, если да, то пропускаем итерацию
            if self.are_files_converted(post):
                continue

            self.convert_2_webp(post)

    def release_media_files(self, data):
        if not data:
            data = self.media_data_paths

        for post in data:
            #Проверяем: перемещены ли файлы в релиз, если да, то пропускаем итерацию
            if self.are_files_released(post):
                continue

            if not self.are_files_converted(post):
                self.convert_2_webp(post)

            for file in self.get_media_from_paths(post)[0]:
                src_path = post['src_path'] + file
                dst_path = post['dst_path'] + file

                try:
                    shutil.copy(src_path, dst_path)
                except IOError as io_err:
                    print('distanation path was not found.. ' + str(io_err))
                    print('Creating new path.. ')
                    self.error_log('Distanation path was not found, trying to create folder..')
                    try:
                        os.makedirs(os.path.dirname(dst_path))
                        shutil.copy(src_path, dst_path)
                        self.error_log('Success. Folder Created')
                    except:
                        print('Can\'t copy files to distanation folder') 
                        self.error_log('Error. Files wasn\'t copied') 

    def image_filter(self, string):
        if not string:
            return None
        
        if re.match(r'^\d{1,2}t?p?\.', string): # equal to "[0-99]" + "('' || 't' || 'p')" + "."
            for image_format in list(set(self.image_formats) - set('.webp')):
                if image_format in string:
                    return 1
            return 0
        
        return None

    def media_filter(self, string):
        if not string:
            return None

        if re.match(r'^\d{1,2}t?p?\.', string): # equal to "[0-99]" + "('' || 't' || 'p')" + "."
            for media_format in self.image_formats + self.video_formats + self.file_formats:
                if media_format in string:
                    return 1
            return 0
        
        return None


if __name__ == "__main__":
    obj = Media()
    obj.get_media_paths()
    obj.convert_all_images(None)
    obj.release_media_files(None)
