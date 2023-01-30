from ever_photo import EverPhoto
from cloud189 import Clound189
from youdao import YouDao
from push import WeWorkPush


def parse_msg(item):
    result = []
    if type(item) is str:
        return item
        # result.append(item)
    elif type(item) is list:
        for msg in item:
            result.append(parse_msg(msg))
    elif type(item) is dict:
        result.append(f"{item['name']}: {item['value']}")
    return "\n".join(result)


def push_msg(msg_list):
    pusher = WeWorkPush()

    def push(content):
        pusher.send(f"{content}",
                    url="https://github.com/ZenLian/actions/actions")

    msg = parse_msg(msg_list)
    push(msg)
    print(f'[DEBUG] push message:\n{msg}')


def main():
    msg_list = []
    all = (EverPhoto, Clound189, YouDao)
    for v in all:
        try:
            msg = v.start()
            msg_list.append(f"「{v.NAME}」")
            msg_list.append(msg)
        except Exception as e:
            msg_list.append(f"「{v.NAME}」\n{e}")

    push_msg(msg_list)


if __name__ == "__main__":
    main()
