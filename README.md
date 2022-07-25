# IoT

LINE から Raspberri Pi 経由でエアコンを制御

## デモ

https://user-images.githubusercontent.com/63896499/180638108-60df99a0-b94c-489d-9904-701a673b13a0.mp4

## システム構成

![diagram](https://user-images.githubusercontent.com/63896499/180638396-5e9530c6-d86d-4bfd-b92b-6e770a000c3f.png)

- LINE
- LINE Messaging API
- Google Apps Script
- Beebotte
- Raspberry Pi Zero WH

## システムフロー

![flow](https://user-images.githubusercontent.com/63896499/180638416-f5897c63-2b53-4f99-9e07-5ea4a006c97b.png)

1. LINE からのメッセージを LINE Messaging API を利用して Google Apps Script で取得
2. 取得したデータを MQTT Broker である Beebotte に HTTP POST で Publish
3. Raspberry Pi で Beebotte からデータを Subscribe
4. Raspberry Pi から LINE Messaging API を利用してリプライメッセージを送信

## 回路図

![circuit](https://user-images.githubusercontent.com/63896499/180638420-d119c1fc-b4d3-48ce-be83-30a76bf4844c.png)

- 赤外線 LED
  - エアコンへ信号を送信
- 赤外線リモコン受信モジュール
  - エアコンのリモコンから送出される信号の学習 (運用後は不要)
- LED
  - エアコンの ON / OFF にあわせて点灯 / 消灯

## 使用パーツ

- Raspberry Pi Zero WH
- 赤色 LED (OSR5JA3Z74A)
- 赤外線リモコン受信モジュール (PL-IRM0101-3)
- 赤外線 LED (OSI3CA5111A)
- 抵抗 1kΩ [×2]
- ブレッドボード
- ジャンパーワイヤー [適量]

## 作成手順

1. LINE Messaging API 用の LINE Bot を作成
   - メッセージ「ON」で電源 ON、「OFF」で電源 OFF
   - Option: リッチメニューを作成
2. LINE Messaging API からメッセージを取得するための Google Apps Script を作成
   - https://github.com/mikiya1130/IoT/blob/master/gas.js
     - 15 行目のトークンを Beebotte で発行したものに書き換える
     - 25 行目のエンドポイント URL の形式は `"https://api.beebotte.com/v1/data/publish/<topic>"` なので必要に応じて書き換える
       - topic は Beebotte の場合 `<Channel Name>/<Resource name>`
3. Google Apps Script でデプロイしたアプリの URL を LINE Messaging API の Webhook URL に登録
4. Beebotte でチャンネルを作成
   - Channel Name: IoT, Resource name: line_bot
5. Raspberry Pi の `/home/pi/` にリポジトリをクローン
   - `$ git clone git@github.com:mikiya1130/IoT.git ~/IoT && cd ~/IoT`
   - 絶対パスでハードコーディングしているため、クローン先に注意
6. `.env.template` をコピーして `.env` を作成し、Beebotte のトークン・トピックと LINE のアクセストークンを設定
7. プログラム実行に必要なモジュールをインストール
   - `$ pip3 install -r requirements.txt`
8. エアコンのリモコンから送出される信号の学習プログラム irrp.py の実行に必要なサービス pigpiod を起動
   - `$ sudo systemctl enable pigpiod && sudo systemctl start pigpiod`
   - enable は必要に応じて
9. エアコンのリモコンから送出される ON / OFF 信号を `power:on` / `power:off` として学習し `codes` に保存
   - `$ python3 irrp.py -r -g23 -f codes power:on power:off --no-confirm --post 130`
   - 信号が長い場合発信に失敗するので分割する
     - `power:on` → `power:on:1`, `power:on:2`, `power:on:3`
     - `power:off` → `power:off:1`, `power:off:2`, `power:off:3`
     - 参考：[ラズパイでエアコン対応の赤外線学習リモコンを pigpioライブラリを使って作る方法、Goodbye LIRC](http://www.neko.ne.jp/~freewing/raspberry_pi/raspberry_pi_gpio_pigpio_ir_remote_control/)
     - 上記通り分割しなかった場合、`main.py` 54行目・62行目のコマンドを書き換える
10. LINE からの ON / OFF メッセージを Subscribe してエアコンを ON / OFF するプログラムの実行
   - `$ python3 main.py`
   - Option: Raspberry Pi 起動時に自動実行
     - `$ sudo ln iot.service /etc/systemd/system/iot.service && sudo systemctl enable iot.service && sudo systemctl start iot.service`

## 参考サイト

- [プログラミング初心者でも無料で簡単にLINE BOTが作れるチュートリアル](https://note.com/tatsuaki_w/n/nfed622429f4a)
- [LINEで自作IoTデバイス[スマートロック・リモコン]を操作する（市販品も可）](https://jorublog.site/line-bot-smarthome-control/)
- [RaspberryPi zero WH・LINE API・heroku・Beebotteを使ってエアコンを遠隔操作する【ソフトウェア編】](https://qiita.com/2019Shun/items/c055d56f948aba99d758)
- [beebotteの使い方メモ.md](https://gist.github.com/yoggy/28196ba084f9c406c75967289fbb3dca)
- [Beebotteを使ってLINEメッセージでLEDをON/OFFする(その１）Beebotteの設定](https://note.com/khe00716/n/n8064e6484037)
- [Beebotteを使ってLINEメッセージでLEDをON/OFFする(その2）LINEリッチメニューからGASの設定](https://note.com/khe00716/n/n9eef7f5caadb)
- [Beebotteを使ってLINEメッセージでLEDをON/OFFする(その3）LINEリッチメニューからRaspberryPiのLEDを点灯](https://note.com/khe00716/n/nba6860513ff7)
- [ラズパイで外部からエアコンの電源を入れてみる その１](https://bsblog.casareal.co.jp/archives/5010)
- [ラズパイで外部からエアコンの電源を入れてみる その２](https://bsblog.casareal.co.jp/archives/5891)
- [ラズパイでエアコン対応の赤外線学習リモコンを pigpioライブラリを使って作る方法、Goodbye LIRC](http://www.neko.ne.jp/~freewing/raspberry_pi/raspberry_pi_gpio_pigpio_ir_remote_control/)

## 素材利用

- https://icons8.jp/
- https://icon-icons.com/
- https://svgporn.com/
- [https://qiita.com/2019Shun/items/c055d56f948aba99d758#付録aline-botにリッチメニューを実装する](https://qiita.com/2019Shun/items/c055d56f948aba99d758#%E4%BB%98%E9%8C%B2aline-bot%E3%81%AB%E3%83%AA%E3%83%83%E3%83%81%E3%83%A1%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%92%E5%AE%9F%E8%A3%85%E3%81%99%E3%82%8B)

## 回路図作成

- https://www.tinkercad.com/
