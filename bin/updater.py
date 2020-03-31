from apitizer import data_updater
import json

if __name__ == "__main__":
    with open('config/config.json') as f:
        config = json.load(f)

    updater = data_updater.Updater(config)
    updater.update()
