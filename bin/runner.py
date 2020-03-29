from apitizer import img_parser
import json


def main():
    with open('config/config.json') as f:
        config = json.load(f)

    parser = img_parser.ImageParser(config, url=config["url"])
    parser.fetch_image()
    parser.preprocess_image()
    parser.parse_image()

    print(parser.value)


if __name__ == "__main__":
    main()
