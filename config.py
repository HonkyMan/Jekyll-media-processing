import json

default_config = {
    'posts_path': '<path_to_media_dir_inside_posts_folder', 
    'media_directory': '_backstage',
    'media_dist_directory': 'images',
    'media_formats': {
        'images': [
            '.jpg', '.png', '.webp', '.jpeg', '.gif'
        ],
        'videos': [
            '.mp4'
        ],
        'files':[
            '.xlsx', '.zip'
        ]
    },
    'post_formats': [
        '.html', '.md'
    ]
}

def create_config(config_name, config):
    try:
        with open(config_name, 'w') as f:
            json.dump(config, f)
    except:
        print('Can\'t open file for writing')

def get_config(config_name):
    try:
        with open(config_name, 'r') as f:
            return json.load(f)
    except:
        print('Config_file: "' + config_name + '" can\'t be found')
        return None

def create_config_from_obj(config_name, obj):
    try:
        with open(config_name, 'w') as f:
            json.dump(obj, f)
    except:
        print('Can\'t open file for writing')

def create_error_log(message):
    try:
        with open('error_logs.txt', 'w') as f:
            f.write(message)
    except:
        print('Can\'t open file for writing logs')


if __name__ == "__main__":
    create_config('config.json', default_config)