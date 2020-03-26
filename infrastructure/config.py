import toml


def get_config(config_path):
    with open(config_path) as config_file:
        config = toml.loads(config_file.read())
        return config
