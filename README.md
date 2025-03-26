# 医療テキスト分析システム

streamlitによる直感的なUI作成
<img width="1030" alt="Image" src="https://github.com/user-attachments/assets/5695a8ae-3816-4e12-acc0-ab41d5404873" />

## 概要
このシステムは、医療記録の時系列テキストデータを分析し、がん診療に関する重要な医療情報を自動抽出するツールです。
直感的なWebインターフェースにより、簡単に分析を実行できます。

## 2つの使い方
![Image](https://github.com/user-attachments/assets/7c168fdd-e273-4e82-9156-2a8429e49f52)

## アプリのフロー
![Image](https://github.com/user-attachments/assets/a3c61cfa-9b3b-4717-8683-c5f9eb71388a)

## 主な機能

### 1. マルチLLMプロバイダー対応
- vLLM（ローカルLLMサーバー）
- OpenAI
- Google Gemini（Gemini 2.0 Flash Lite）
- Anthropic Claude
- Deepseek（Deepseek Chat）

### 2. Webインターフェース (`app.py`)
- Streamlitベースの使いやすいUI
- ドラッグ&ドロップでのファイルアップロード
- リアルタイムの進捗表示と分析状況の可視化
- 分析結果の詳細なビジュアライゼーション
  - 棒グラフ
  - 円グラフ
  - 進捗メーター
- 患者IDごとの詳細表示
- 分析テンプレートのカスタマイズ機能
- テストデータ生成機能

### 3. データ生成機能 (`src/data/data_generator.py`)
- がん診療に特化したダミーデータの生成(テスト実行用)
- 以下の情報を含むテキストデータを生成：
  - がん診断名（複数の表記揺れに対応）
  - ステージ情報
  - 診断検査情報
  - 手術記録
  - 化学療法情報
  - 特記事項（合併症、投薬情報など）

### 4. テキスト分析機能 (`src/analyzer/excel_analyzer.py`)
- Excel形式の医療記録からの情報抽出
- 患者IDごとの時系列データの統合
- カスタマイズ可能なプロンプトテンプレート
- 分析タイプ：(現在はextractのみ)
  - 抽出（extract）
  - 分類（classify）
  - 要約（summarize）
- 分析結果の自動保存とExcelエクスポート

## 使用方法

本システムは以下の2つの方法で利用できます：

### 1. Streamlit Cloud版
- https://llmatch-7mnc3rpgpcupdw5dgjpzf5.streamlit.app/ にアクセス
- Gemini Flash Lightがお試し用として即座に利用可能
- その他のLLMプロバイダー（OpenAI、Anthropic Claude、Deepseek）は要APIキー

### 2. ローカル実行版
- すべてのLLMプロバイダーに対応(要APIキー)
- vLLMサーバーの独自構築が可能
- GitHubからクローンして実行

### 1. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定
各LLMプロバイダーのAPIキーを設定：
```bash
export OPENAI_API_KEY="your-api-key"
export GOOGLE_API_KEY="your-api-key"
export ANTHROPIC_API_KEY="your-api-key"
export DEEPSEEK_API_KEY="your-api-key"
```



## データ形式

### 入力データ（必須列）
- `ID`: 患者ID
- `day`: 記録日（YYYY-MM-DD形式）
- `text`: 医療記録テキスト

## 制限事項
- テキストの最大長は4000文字（超過分は切り捨て）
- 日本語医療テキストの分析に特化
- Streamlitインターフェースは同時に複数のユーザーによる使用を想定していません

## ライセンス
Apache License 2.0

