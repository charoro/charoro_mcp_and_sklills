# charoro_mcp_and_sklills

よく利用する Claude Code / Codex / GitHub Copilot で使えるMCPサーバーとskillsを管理するリポジトリです。

## ディレクトリ構成

```text
.
├── AGENTS.md
├── mcp_servers/
│   └── nodejs/
│       └── echo_server/
│           ├── package.json
│           └── src/index.js
└── skills/
    └── python/
        ├── text_summary/
        │   ├── skill.py
        │   └── skill.yaml
        └── pptx_from_markdown/
            ├── skill.py
            ├── skill.yaml
            ├── requirements.txt
            ├── sample_template.pptx
            └── sample_content.md
```

- `mcp_servers/nodejs/`: Node.jsベースのMCPサーバー置き場
- `skills/python/`: Pythonベースのskill置き場

## MCPサーバー（Node.js）

### 1) セットアップ

```bash
cd mcp_servers/nodejs/echo_server
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
cd skills/python/text_summary
python3 skill.py --max-lines 2 "これはテキスト要約スキルのサンプルです。複数行の入力でも使えます。"
```

### 2) インストール（Claude Code / Codex / GitHub Copilot向け）

各ツールの設定で、使いたいskillのディレクトリ（例: `skills/python/text_summary`）を参照する構成にします。

- skillの実行エントリ: `skill.py`
- メタデータ: `skill.yaml`

運用では、必要なskillディレクトリのみを選んで各エージェント側へ登録してください。

## skill: pptx_from_markdown（Python）

PPTXテンプレートとMarkdownファイルをもとに、テンプレートのデザインを維持したままPowerPointプレゼンテーションを生成するスキルです。

### 1) 依存ライブラリのインストール

```bash
cd skills/python/pptx_from_markdown
pip install -r requirements.txt
```

### 2) 実行

```bash
python3 skill.py \
  --template sample_template.pptx \
  --markdown sample_content.md \
  --output output.pptx
```

### 3) Markdownの書き方

| Markdown記法             | 生成されるスライド                        |
|--------------------------|-------------------------------------------|
| `# タイトル`             | タイトルスライド（1枚目推奨）             |
| `## セクション見出し`    | セクションヘッダースライド               |
| `### スライドタイトル`   | タイトル＋コンテンツスライド             |
| `- 箇条書き`             | 直前のスライドの箇条書きに追加           |
| 通常テキスト行           | 直前のスライドの本文に追加               |

サンプル（`sample_content.md`）:

```markdown
# プロジェクト進捗報告
2026年6月 / 開発チーム

## 概要

### プロジェクトの目的
- 社内業務の自動化推進
- AIエージェント活用による効率化
```

### 4) 独自テンプレートの使用

任意の `.pptx` ファイルをテンプレートとして指定できます。テンプレート内の既存スライドは削除され、Markdownの内容で新たにスライドが生成されます。スライドのデザイン・フォント・配色はテンプレートのスライドレイアウトが引き継がれます。

テンプレートに以下のレイアウト名があると自動的に使用されます（日本語名にも対応）：

- **タイトルスライド**: `Title Slide` / `タイトル スライド`
- **セクションヘッダー**: `Section Header` / `セクション見出し`
- **コンテンツスライド**: `Title and Content` / `タイトルとコンテンツ`

## 開発ガイド

開発時のルールは `./AGENTS.md` を参照してください。
