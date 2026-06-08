# charoro_mcp_and_sklills

よく利用する Claude Code / Codex / GitHub Copilot で使えるMCPサーバーとskillsを管理するリポジトリです。

## ディレクトリ構成

```text
/tmp/workspace/charoro/charoro_mcp_and_sklills
├── AGENTS.md
├── mcp_servers/
│   └── nodejs/
│       └── echo_server/
│           ├── package.json
│           └── src/index.js
└── skills/
    └── python/
        └── text_summary/
            ├── skill.py
            └── skill.yaml
```

- `mcp_servers/nodejs/`: Node.jsベースのMCPサーバー置き場
- `skills/python/`: Pythonベースのskill置き場

## MCPサーバー（Node.js）

### 1) セットアップ

```bash
cd /tmp/workspace/charoro/charoro_mcp_and_sklills/mcp_servers/nodejs/echo_server
npm install
```

### 2) 実行

```bash
npm start
```

標準入力に文字列を渡すと、JSON形式でそのまま返す最小サーバーです。

## skill（Python）

### 1) 実行

```bash
cd /tmp/workspace/charoro/charoro_mcp_and_sklills/skills/python/text_summary
python3 skill.py --max-lines 2 "これはテキスト要約スキルのサンプルです。複数行の入力でも使えます。"
```

### 2) インストール（Claude Code / Codex / GitHub Copilot向け）

各ツールの設定で、使いたいskillのディレクトリ（例: `skills/python/text_summary`）を参照する構成にします。

- skillの実行エントリ: `skill.py`
- メタデータ: `skill.yaml`

運用では、必要なskillディレクトリのみを選んで各エージェント側へ登録してください。

## 開発ガイド

開発時のルールは `/tmp/workspace/charoro/charoro_mcp_and_sklills/AGENTS.md` を参照してください。
