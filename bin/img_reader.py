from apitizer import img_parser
import json

if __name__ == "__main__":
    with open('config/config.json') as f:
        config = json.load(f)

    Parser = img_parser.ImageParser(config)

    results = Parser.get_results()

    for key, value in results.items():
        print(f"%22s: \t%s" % (key, value))
