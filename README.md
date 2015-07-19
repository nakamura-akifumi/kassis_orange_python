kassis orange
====

kassis orange は、Webアプリ型の資料情報管理システムです。

## 概要 / Description

kassis orange は、2015年5月から開発をしているWebアプリ型の資料情報管理システムです。
いわゆる図書館情報管理システムです。
アプリケーション名は、カシスオレンジと読みます。先頭が k なのは歴史的な理由です。

基本操作は、SafariかChromeなどのウェブブラウザで行います。

データストレージにRiakを利用することでスキーマレスで柔軟なデータ構造を持ちます。Riakの特性としてスケールアウトしやすいこともあげられます。
全文検索に Solr 4 を利用しています。

他にもOSSですばらしいシステムがありますが、「多様性は善」ということで気にしないでください。
作ってみたかったんです...

## 状況とこれから / Status and Roadmap

準備中です。

## デモ / Demo

デモサイトは準備中です。

## 動作環境 / Requirement

サーバ側；
* OS: Mac OS X or Linux (recommended CentOS 7.1+)
* データ保存: Riak 2.1+ , PostgreSQL 9+
* その他: Python 3.4+ , Memcached 1.4+ , node.js 0.12+

クライアント側：
* Chrome か Safari の最新版

## 操作方法 / Usage

マニュアルを準備中です。

## インストール方法 / Install

インストール手順書と仮想環境イメージを準備中です。

## Contribution

forkして修正したらpull requestしてください。

## ライセンス / License

[AGPLv3](https://raw.githubusercontent.com/nakamura-akifumi/kassis_orange/master/LICENSE)

## 関わった人 / Author

企画、開発:
[Akifumi Nakamura](https://github.com/nakamura-akifumi)

ロゴとイラスト作成：
[Tomoko Shinozuka](http://www.sino-works.com/)



