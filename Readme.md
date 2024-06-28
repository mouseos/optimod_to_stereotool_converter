# optimod_to_stereotool_converter
ラジオ放送局用業務機器optimodオーディオプロセッサの設定ファイルを、一般向け配信用オーディオプロセッサソフトstereotool用設定ファイルに変換します。  
optimod 8300以降の5バンド機種のプリセットファイルをstereotool プリセットファイルに変換することができます。  
完全に同じ音にはなりませんが近い音にすることが可能です。  

## 使い方
### GUI
pythonが動作するウェブサーバーにアップロードしてindex.htmlにアクセスする
### 関数
convert_optimod_to_stereotool("入力optimod設定ファイル", "opti.sts", "出力ファイル名.sts")  
opti.stsは参考用ファイル