# 🤖 Actions

Take use of github actions to _薅羊毛_.

## 🚀 Setup secrets

account info:

- `EVER_PHOTO_DATA`: EverPhoto account info, in format `mobile1,passwd1;mobile2,passwd2`
- `CLOUD189_ACCOUNTS`: CLOUD189 account info, in format `mobile1,passwd1;mobile2,passwd2`
- `YOUDAO_COOKIES`: YouDao cookies, different accounts seperated by `\n`
- microsoft_e5:
  - single client:
    - `MS_TOKEN`: refresh token
    - `MS_CLIENT_ID` and `MS_CLIENT_SECRET`
  - multi clients:
    - `MS_APP_NUM`: number of clients
    - `MS_TOKEN_{n}`, `MS_CLIENT_ID_{n}`, `MS_CLIENT_SECRET_{n}`: same as single
      client, where `{n}` is `1,2,3...`

message push:

- `WX_CORP_ID`
- `WX_APP_ID`
- `WX_APP_SECRET`

## ❤️ Credits

- [ICE99125/everphoto_checkin](https://github.com/ICE99125/everphoto_checkin)
- [Cluas/189checkin](https://github.com/Cluas/189checkin)
- [Sitoi/dailycheckin](https://github.com/Sitoi/dailycheckin)
