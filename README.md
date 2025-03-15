# 医療テキスト分析システム

streamlitによる直感的なUI作成
<img width="1030" alt="Image" src="https://github.com/user-attachments/assets/5695a8ae-3816-4e12-acc0-ab41d5404873" />

## 概要
このシステムは、医療記録の時系列テキストデータを分析し、がん診療に関する重要な医療情報を自動抽出するツールです。
直感的なWebインターフェースにより、簡単に分析を実行できます。

## 主な機能

### 1. マルチLLMプロバイダー対応
- vLLM（ローカルLLMサーバー）
- OpenAI
- Google Gemini
- Anthropic Claude
- Deepseek

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
- 分析タイプ：
  - 抽出（extract）
  - 分類（classify）
  - 要約（summarize）
- 分析結果の自動保存とExcelエクスポート

## セットアップ

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

## 使用方法

### A. Webインターフェースでの実行（推奨）

1. Streamlitアプリケーションを起動：
```bash
streamlit run app.py
```

2. ブラウザで以下のURLにアクセス：
```
http://localhost:8501
```

3. Webインターフェースの使用手順：
   - LLMプロバイダーとモデルを選択
   - テンプレートファイルのパスを確認
   - 医療記録Excelファイルをアップロード
   - 分析したいテンプレートを選択
   - 「分析を実行」ボタンをクリック
   - 結果を確認し、必要に応じてダウンロード

### B. コマンドライン実行

#### 1. ダミーデータの生成
```bash
python examples/test_data_generator.py
```

#### 2. テキスト分析の実行
```bash
python analyze_medical_records.py
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
MIT License

