# AGENTS.md

このリポジトリでMCPサーバーとskillを開発するためのガイドです。

## 目的
- `mcp_servers/` にMCPサーバーを配置する
- `skills/` にAIエージェントから呼び出すskillを配置する

## ルール
1. MCPサーバーは原則Node.jsで作成する
2. skills配下の実行プログラムは原則Pythonで作成する
3. 各サーバー/skillはディレクトリを分け、自己完結する
4. README.mdに追加したコンポーネントの導入手順と使い方を記載する

## 推奨ディレクトリ
- `mcp_servers/nodejs/<server_name>/`
- `skills/python/<skill_name>/`

## 追加時チェック
- 追加したskillやサーバーがREADME.mdに反映されている
- 実行コマンドがローカルで動作する
