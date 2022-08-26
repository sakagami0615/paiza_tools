# **paiza_tools**

paiza の問題 (スキルチェック) に対して以下の2点を行なってくれるツールです。
+ 問題文の HTML テキストからPythonコード(main.py)を生成<br>
  ※ HTML テキストは手動でコピペする必要があります。
+ ローカルでのサンプルテストケース検証

ツールはpyinstallerで実行ファイルにしています。<br>
そのため、mac環境だとツールが実行されるまでに時間がかかりますがご了承ください。

## **How to install**

1. 本リポジトリをクローンする。
2. クローンしたリポジトリ内の下記フォルダをパス追加する。
   + Windows環境の場合 : [clone repo folder]/bin/windows
   + Mac環境の場合 : [clone repo folder]/bin/mac

## **How to use**

本ツールは下記のモードを指定して実行します。
+ `EnvGen`<br>
  問題文の HTML テキストから環境フォルダを作成します (main.py生成含む)。<br>
  実行前に、問題文のWebサイトからHTMLテキストをコピーしておく必要があります。<br>
  ※Chromeの場合は、ブラウザを右クリックし「ページのソースを表示」にて表示される
+ `CodeGen`<br>
  環境フォルダ内でmain.pyを生成します。<br>
  実行前に、問題文のWebサイトからHTMLテキストをコピーしておく必要があります。<br>
  ※Chromeの場合は、ブラウザを右クリックし「ページのソースを表示」にて表示される
+ `Test`<br>
  サンプルを使用して環境フォルダ内のmain.pyの出力が合っているか検証します。

各モードのコマンドは次節に記載しています。

### **EnvGen command**

Command:
```
paiza_tools gen
paiza_tools gen -w {Folder}
paiza_tools gen -w {Folder} -o {True|False}
```

Argument:
+ `-w` or `--workspace`<br>
  環境フォルダを生成するパスを設定します。<br>
  ※デフォルト : ./ (カレントフォルダ)
+ `-o` or `--overwrite`<br>
  環境フォルダの上書き有無を設定します。<br>
  Trueの場合、既に同問題の環境フォルダが存在する際は上書きします。<br>
  Falseの場合、既に同問題の環境フォルダが存在する際はエラー終了します。<br>
  ※デフォルト : False

### **CodeGen command**

Command:
```
paiza_tools codegen
paiza_tools codegen -w {Folder}
paiza_tools codegen -w {Folder} -o {True|False}
```

Argument:
+ `-w` or `--workspace`<br>
  環境フォルダを生成するパスを設定します。<br>
  ※デフォルト : ./ (カレントフォルダ)
+ `-o` or `--overwrite`<br>
  環境フォルダの上書き有無を設定します。<br>
  Trueの場合、既に同問題の環境フォルダが存在する際は上書きします。<br>
  Falseの場合、既に同問題の環境フォルダが存在する際はエラー終了します。<br>
  ※デフォルト : False

### **Test command**

Command:
```
paiza_tools.py test
paiza_tools.py test -w {Folder}
```

Argument:
+ `-w` or `--workspace`<br>
  環境フォルダを生成するパスを設定します。<br>
  ※デフォルト : ./ (カレントフォルダ)


## **補足事項**

### **生成する main.py の設定に関して**

生成する main.py の設定は下記2つファイルにて実施します。
+ `user_config.yaml`<br>
  configファイルでは以下の設定を記載します。
  + `main.py のテンプレートファイルのパス`<br>
    リポジトリからの相対パスを指定します。
  + `タブ文字`<br>
    スペースタブ か タブ文字 を指定することができます。
  + `標準入力取得用の処理コード`<br>
    標準入力でデータを取得する際のコードを指定します。<br>
    デフォルトのテンプレートで使用している自作関数(stdin_iter)のように一つずつ入力を取得できるようなコードである必要があります。<br>
    ※input関数だと1行づつ取得してしまうのでエラーとなります。
+ `templates/default.py`<br>
  main.py のデフォルトのテンプレートファイルです。<br>
  このファイルをカスタムすることでオリジナルのテンプレートを作成することも可能です。(あまり想定していませんが、、、)<br>
  ファイル名を変更した場合は、`user_config.yaml` 内の `テンプレートファイルのパス` を変更するのを忘れずに。<br>
  ※ main.py 作成にはjinja2のテンプレートエンジンを使用しています

## **Appendix**

### main.py 生成時にエラーが出る場合
私がWindows環境で実施しようとした際に、環境などはちゃんと用意しているのに、生成した main.py にRTEチェックで引っ掛かってしまった。<br>
調べたら、pythonコマンドが見つからないことで発生しており、ツール実行フォルダで仮想環境を作成 & アクティベートを実施することで解消できた。<br>
同問題が発生した際は、試してみてください。
```
python -m venv env
env/Scripts/activate
```

## **License**
MIT Licence

## **Author**
[sakagami0615](https://github.com/sakagami0615)
