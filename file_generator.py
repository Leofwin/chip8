import settings


def generate_file():
    result = b""
    for i in range(3585):
        result += bytes("f", "utf-8")

    with open(settings.games_folder + "_test_file", 'wb') as f:
        f.write(result)


if __name__ == '__main__':
    generate_file()
