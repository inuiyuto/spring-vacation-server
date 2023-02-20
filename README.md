# とりあえずしりとりのサーバの中身にしました。
これからいじっていけばよさそう、たぶん
追加の依存ライブラリのインストールだけお忘れ無く

# しりとり

## だいたいの動作方法
クライアントの参加人数として2人を想定しています。
まずサーバーをたてます。
~~~script
python run.py
~~~

次にクライアントとして
~~~script
npm start
~~~
してクライアントのページ(http://localhost:3000/)をふたつ開きます。
usernameを入力してjoinします。
二人ともusernameを入力するとしりとりが始まりますが、先にusernameを入力してjoinしたほうが先攻となります。
しりとりができますが、しりとりかどうか判定はしないので実質交互に文字を送り合っているだけです。


## 追加依存ライブラリ
flaskのほうは普通にpipでインストールできるはず
~~~script
pip install flask-socketio
pip install flask-cors
pip install eventlet
~~~

<br><br/>
Reactのほうは普通にnpmでインストールできるはず
~~~script
npm install socket.io-client
~~~
<br><br/>


## 通信プロトコル

1. 参加要請(クライアント -> サーバ)(参加時)
~~~JavaScript
    {
        "status": "requestJoin",
        "user": <username>
    }
~~~

2. 参加人数が2人になると開始通知(サーバ -> 全クライアント)
~~~JavaScript
    {
        "status": "informBeginning",
        "users": [
            "user": <username>
        ]
    }
~~~

3. しりとりの応答(クライアント -> サーバ)
~~~JavaScript
    {
        "status": "changeTurn",
		"nextWord": <nextWord>,
        "user": <username>
    }
~~~

4. しりとりの応答伝播(クライアント -> サーバ)
~~~JavaScript
    {
        "status": "changeTurn",
		"nextWord": <nextWord>,
        "user": <username>
    }
~~~
