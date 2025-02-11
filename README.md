# 医療テキスト分析システム

## 概要
このシステムは、医療記録などの時系列テキストデータを分析し、重要な医療情報を自動抽出するツールです。

### 主な機能
1. **ダミーデータ生成機能**
   - 医療記録の特徴を再現した現実的なテストデータ
   - 表記揺れや時系列の流れを考慮
   - 診断名、検査結果、治療内容などの多様なパターン

2. **テキスト分析機能**
   - がんの診断名の抽出
   - 病期ステージ（TNM分類/Stage）の特定
   - 病理学的所見（組織型、分化度）の抽出
   - 治療内容（手術術式、化学療法レジメン）の分析
   - 重要日付の抽出
   - 特記事項の識別

3. **データ管理機能**
   - Excel形式での入出力
   - 患者IDごとの時系列データの統合
   - 分析結果の構造化保存

4. **カスタマイズ機能**
   - プロンプトテンプレートのカスタマイズ
   - 診療科別の分析ルールの設定
   - 出力形式の調整

### システムの特徴
- ローカルLLMサーバーによる高速・安全な処理で患者情報の外部流出を防止
- 医療現場で馴染みのあるExcel形式での入出力
  - 多くの医療機関で日常的に使用されている標準的なツール
  - 追加のソフトウェアインストールが不要
  - 直感的な操作でデータの確認・編集が可能
  - 既存の院内システムとの親和性が高い
- Jupyter Notebookによる対話的な分析環境
- 詳細な分析結果レポート機能

## 開発におけるエンジニアと医師の協力

このシステムの開発と改善には、医師とエンジニアの緊密な協力が不可欠です。両者の専門知識を組み合わせることで、より実用的で信頼性の高いシステムを実現できます。

### 協力のポイント

#### エンジニアの視点
- 安定したシステムの実装
- 効率的なデータ処理の実現
- 使いやすいインターフェースの設計
- 技術的な制約の説明

#### 医師の視点
- 必要な医療情報の特定
- 医療記録の特徴的な表現パターンの共有
- 臨床現場での使いやすさの評価
- 分析結果の医学的な妥当性確認

### 具体的な取り組み
- 定期的な意見交換
- ダミーの医療記録を用いたテスト
- 分析結果の共同レビュー
- 改善点の検討と実装

医師とエンジニアが互いの専門性を活かしながら協力することで、医療現場で本当に役立つシステムを作り上げることができます！

## ファイル構成
- `excel_analyzer.py`: メインの分析クラス
- `llm_server.py`: ローカルLLMサーバー（vLLM使用）
- `prompt_templates.json`: 分析用プロンプトテンプレート
- `test_excel_analyzer.py`: 使用例
- `requirements.md`: 詳細な要件定義

## セットアップ手順

### 1. 環境要件
- Python 3.8以上
- CUDA対応GPU（vLLM実行用）
- 十分なGPUメモリ（最低16GB推奨）

### 2. リポジトリのクローンとパッケージのインストール
```bash
# リポジトリのクローン
git clone https://github.com/yourusername/medical_text_analyzer.git
cd medical_text_analyzer

# パッケージのインストール
pip install -r requirements.txt
```

## 実行方法

### 1. コマンドラインでの実行

#### LLMサーバーの起動
```bash
# 別ターミナルで実行
python src/analyzer/llm_server.py
```

#### ダミーデータの生成
```bash
# データ生成の実行
python -m examples.test_data_generator
```

#### テキスト分析の実行
```bash
# 分析の実行
python -m examples.test_excel_analyzer
```

### 2. Jupyter Notebookでの実行

#### Jupyterの起動
```bash
jupyter notebook
```

#### ダミーデータ生成（medical_data_generator.ipynb）
1. `notebooks/medical_data_generator.ipynb` を開く
2. 各セルを順番に実行
3. 生成されたデータは `data/` ディレクトリに保存

#### テキスト分析（medical_text_analyzer.ipynb）
1. `notebooks/medical_text_analyzer.ipynb` を開く
2. LLMサーバーが起動していることを確認
3. 各セルを順番に実行して分析を実施

### 3. プロンプトテンプレートのカスタマイズ
`templates/prompt_templates.json` で分析ルールを定義します：

```json
{
    "cancer_diagnosis": {
        "name": "がん診断名抽出",
        "description": "テキストからがんの診断名を抽出",
        "system_prompt": "医療テキストから、がんの診断名を抽出してください。",
        "analysis_type": "extract"
    },
    "cancer_stage": {
        "name": "がんステージ抽出",
        "description": "がんのステージ情報を抽出",
        "system_prompt": "医療テキストから、TNM分類やStageなどのステージ情報を抽出してください。",
        "analysis_type": "extract"
    }
}
```

## 分析タイプ

### 1. 情報抽出モード（extract）
- 特定の情報を抽出（例：ステージ、サイズ）
- 出力形式は各テンプレートで規定
- 結果は文字列として保存
- 情報が見つからない場合は"N/A"

## 出力形式

### 1. Excelファイル
- 入力ファイル名 + "_analyzed.xlsx"
- 列の順序：
  1. 基本列（ID, day, text）
  2. 分析結果列（以下の順序）：
     - 分析結果_がん診断名（例："漿液性卵巣癌"）
     - 分析結果_ステージ（例："Stage IIIC"、"T3cN1M0"）
     - 分析結果_診断検査（例："検査名: 子宮内膜組織診, 実施日: 2023-01-10"）
     - 分析結果_初回治療（例："日付: 2023-02-01, 種類: 手術, 内容: 腹腔鏡下子宮全摘術"）
     - 分析結果_化学療法（例："開始日: 2023-02-15, レジメン: TC療法, 詳細: 3週毎"）
     - 分析結果_術式（例："腹腔鏡下子宮全摘+両側付属器切除術"）
     - 分析結果_特記事項（例："術後出血リスク高（抗凝固薬服用中）"）
  3. その他の列（元データに存在した追加列）

- 各分析結果列の特徴：
  - 情報が見つからない場合は "N/A" を格納
  - 複数の情報がある場合は最新のものを採用
  - 日付情報は 'YYYY-MM-DD' 形式で統一
  - 区切り文字として ", " を使用

### 2. 分析レポート
```
分析結果の概要:
- 分析結果_がん診断名:
   総データ数: 10
   ユニークな値の数: 3
   未検出(N/A)の数: 0
   主な抽出結果:
     - 子宮体部類内膜癌: 3件
     - 漿液性卵巣癌: 4件
     - 高異型度漿液性癌: 3件

- 分析結果_初回治療:
   総データ数: 10
   ユニークな値の数: 3
   未検出(N/A)の数: 0
   主な抽出結果:
     - 手術: 5件
     - 化学療法: 3件
     - 放射線治療: 2件
```

## エラーハンドリング

### 1. データ関連
- 列名の不一致
- ファイル不存在
- 必須列の欠損

### 2. LLM関連
- サーバー接続エラー
- テキスト長制限（4000文字）
- API呼び出しエラー

### 3. 結果関連
- 分析失敗時のフォールバック値
- 無効な出力の自動検出

## パフォーマンス最適化
- ID単位での処理によるAPI呼び出し削減
- 0.5秒の待機時間による制御
- 長文の自動トリミング（最新部分優先）

## 制限事項
1. 列名の制約
   - ID列: "ID"
   - 日付列: "day"
   - テキスト列: "text"

2. テキスト制限
   - 最大4000文字
   - 超過分は切り捨て

3. 環境要件
   - GPU必須
   - 十分なメモリ

## トラブルシューティング

### サーバー起動エラー
```bash
# GPUステータス確認
nvidia-smi
```

### 分析エラー
1. 列名の確認
2. テキスト長の確認
3. サーバー状態の確認

## ライセンス
- MITライセンス
- ELYZA-japanese-Llama-2-7bモデルのライセンスに準拠 

## システムの流れ
```mermaid
graph LR
    A[Excelファイル] --> B[ExcelAnalyzer]
    T[プロンプトテンプレート] --> B
    B --> C[データ前処理]
    C --> D[ID単位で結合]
    D --> E[LLMサーバー]
    E --> F[分析結果]
    F --> G[結果の保存]
    G --> H[分析済みExcel]
    G --> I[分析レポート]

    style A fill:#f9f,stroke:#333
    style T fill:#bbf,stroke:#333
    style E fill:#bfb,stroke:#333
    style H fill:#f9f,stroke:#333
    style I fill:#fdb,stroke:#333
``` 

## ディレクトリ構造
```
medical_text_analyzer/
├── src/
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── excel_analyzer.py
│   │   └── llm_server.py
│   └── data/
│       ├── __init__.py
│       └── data_generator.py
├── notebooks/
│   ├── medical_data_generator.ipynb   # ダミーデータ生成用
│   └── medical_text_analyzer.ipynb    # テキスト分析実行用
├── examples/
│   ├── test_data_generator.py        # データ生成のサンプルコード
│   └── test_excel_analyzer.py        # 分析実行のサンプルコード
├── data/                             # 生成されたデータの保存先
│   └── .gitkeep
├── templates/                        # プロンプトテンプレート
│   └── prompt_templates.json
├── .gitignore                        # Git除外設定
├── LICENSE                           # MITライセンス
├── requirements.txt                  # パッケージ依存関係
├── requirements.md                   # 詳細な要件定義
└── README.md                         # このファイル
```

各ディレクトリの役割：
- `src/`: ソースコード
  - `analyzer/`: 分析関連のコア機能
  - `data/`: データ生成関連の機能
- `notebooks/`: 対話的な分析用Jupyterノートブック
- `examples/`: 使用例とサンプルコード
- `data/`: 生成データの保存先
- `templates/`: プロンプトテンプレート

## 実行方法

### 1. コマンドライン実行
```bash
# ダミーデータの生成
python examples/test_data_generator.py

# テキスト分析の実行
python examples/test_excel_analyzer.py
```

### 2. Jupyter Notebook実行
```bash
# Jupyterの起動
jupyter notebook notebooks/

# 以下のノートブックが利用可能：
# - medical_data_generator.ipynb: ダミーデータの生成と確認
# - medical_text_analyzer.ipynb: テキスト分析の実行と結果確認
```

### 3. 対話的な分析（Jupyter Notebook）
医療テキストの分析を対話的に実行できるJupyter Notebookを提供しています：

1. ダミーデータ生成用ノートブック（medical_data_generator.ipynb）
   - データ生成パラメータの調整
   - 生成データの確認
   - データの統計情報の表示

2. テキスト分析用ノートブック（medical_text_analyzer.ipynb）
   - 段階的な分析実行
   - 結果の視覚的確認
   - 患者ごとの詳細表示

#### ノートブックの特徴
- 対話的なデータ確認
- 視覚的なフィードバック
- 柔軟なパラメータ調整
- 詳細な結果分析

#### 使用例
```python
# Notebookでの実行例
from src.analyzer.excel_analyzer import ExcelAnalyzer
from src.data.data_generator import MedicalDataGenerator

# データ生成
generator = MedicalDataGenerator()
generator.save_to_excel("data/sample_data.xlsx", num_patients=10)

# 分析実行
analyzer = ExcelAnalyzer(
    file_path="data/sample_data.xlsx",
    llm_server_url="http://localhost:8000",
    template_path="templates/prompt_templates.json"
)

# 結果の確認
analyzer.load_excel()
analyzer.analyze_with_template("cancer_diagnosis")
analyzer.save_results()
``` 

## データ形式

### 入力データ形式
Excelファイルを以下の形式で準備します：

| ID | day | text |
|----|-----|------|
| 1 | 2023-01-01 | "初診時所見：子宮体部類内膜癌 Stage IA。内膜生検の病理結果では、類内膜癌 Grade 1。MRIにて筋層浸潤は認めず。開腹子宮全摘術の方針とする。" |
| 1 | 2023-01-15 | "術前検査：胸部CT、腹部造影CTにて遠隔転移なし。血液検査にて貧血（Hb 9.8）あり、術前に貧血改善を要する。" |
| 1 | 2023-02-01 | "手術記録：腹腔鏡下子宮全摘+両側付属器切除術施行。手術時間2時間45分、出血量150ml。腹腔内に播種なし。術中合併症なし。" |

### データ統合例
同一患者（ID）の記録は時系列で統合されます：

ID: 1 
-----------------------------
- 2023-01-01: 初診時所見：子宮体部類内膜癌 Stage IA。内膜生検の病理結果では、類内膜癌 Grade 1。MRIにて筋層浸潤は認めず。開腹子宮全摘術の方針とする。
- 2023-01-15: 術前検査：胸部CT、腹部造影CTにて遠隔転移なし。血液検査にて貧血（Hb 9.8）あり、術前に貧血改善を要する。
- 2023-02-01: 手術記録：腹腔鏡下子宮全摘+両側付属器切除術施行。手術時間2時間45分、出血量150ml。腹腔内に播種なし。術中合併症なし。

### LLMへの入力テキスト
```
「初診時所見：子宮体部類内膜癌 Stage IA。内膜生検の病理結果では、類内膜癌 Grade 1。MRIにて筋層浸潤は認めず。開腹子宮全摘術の方針とする。
術前検査：胸部CT、腹部造影CTにて遠隔転移なし。血液検査にて貧血（Hb 9.8）あり、術前に貧血改善を要する。
手術記録：腹腔鏡下子宮全摘+両側付属器切除術施行。手術時間2時間45分、出血量150ml。腹腔内に播種なし。術中合併症なし。」
```

### 分析結果の例
```python
# 分析の実行例
from src.analyzer.excel_analyzer import ExcelAnalyzer

# アナライザーの初期化
analyzer = ExcelAnalyzer(
    file_path="data/sample_data.xlsx",
    llm_server_url="http://localhost:8000",
    template_path="templates/prompt_templates.json"
)

# データ読み込みと分析
analyzer.load_excel()
analyzer.analyze_with_template("cancer_diagnosis")   # がん診断名の抽出
analyzer.analyze_with_template("cancer_stage")       # ステージ情報の抽出

# 結果の保存
analyzer.save_results()
``` 