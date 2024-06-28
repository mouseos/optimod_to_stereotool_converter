#!/usr/bin/env python3
import cgi
import cgitb
cgitb.enable()
import os
from orbf_to_sts import convert_optimod_to_stereotool

def print_download_link(file_name):
    print('<a href="{}" download>ダウンロードする</a>'.format(file_name))

def main():
    # このパスを適切な値に変更してください
    upload_directory = 'orbf/'

    # ヘッダーを出力
    print('Content-type: text/html\n')
    print("""<!doctype html>
<html>
<head>
    <meta charset="UTF-8">
    <title>変換完了</title>
    <!-- Materialize CSS を追加 -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
    <!-- Material Icons を追加 -->
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
</head>
<body>
    <!-- Materialize のナビゲーションバーを追加 -->
    <nav>
        <div class="nav-wrapper">
            <a href="#" class="brand-logo">orbf sts コンバーター</a>
        </div>
    </nav>
    <!-- レスポンシブ対応のために Materialize の container クラスを使用 -->
    <div class="container">
""")
    # フォームデータの取得
    form = cgi.FieldStorage()

    # ファイルがアップロードされたか確認
    if 'file' not in form:
        print('<h1>ファイルを選択してアップロードしてください。</h1>')
        return

    # アップロードされたファイルの情報を取得
    file_item = form['file']

    # アップロードされたファイルのパスを生成
    file_path = os.path.join(upload_directory, file_item.filename)

    # ファイルをサーバーに保存
    with open(file_path, 'wb') as f:
        f.write(file_item.file.read())

    # ファイルを変換
    converted_file_name = os.path.splitext(file_item.filename)[0] + '.sts'
    convert_optimod_to_stereotool(file_path, "opti.sts", os.path.join('sts', converted_file_name))

    # ダウンロードリンクを表示
    print('<h1>変換が完了しました。</h1>')
    print_download_link(os.path.join('sts/', converted_file_name))
    print("""</div>
    <!-- Materialize JavaScript を追加 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
</body>
</html>
""")
if __name__ == '__main__':
    main()
