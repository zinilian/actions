from ever_photo import EverPhoto
from push import WeWorkPush


def main():
    pusher = WeWorkPush()

    def push(title, content):
        pusher.send(f"{title}\n{content}",
                    url="https://github.com/ZenLian/actions/actions")

    EverPhoto.start(push)


if __name__ == "__main__":
    main()
