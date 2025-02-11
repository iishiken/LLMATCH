# 医療テキスト分析システム

## 概要
このシステムは、医療記録などの時系列テキストデータを分析し、特定の情報（病期ステージ、腫瘍サイズなど）を自動抽出するツールです。ローカルのLLMサーバーを使用して、高速かつセキュアな分析を実現します。

## 特徴
- 同一患者（ID）の複数記録を時系列で統合
- カスタマイズ可能なプロンプトテンプレート
- ローカルLLMサーバーによる高速処理
- 詳細な分析結果レポート

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

### 2. パッケージのインストール
```bash
# 基本パッケージ
pip install pandas openpyxl requests

# LLM関連パッケージ
pip install vllm fastapi uvicorn
```

## 使用方法

### 1. データ準備
Excelファイルを以下の形式で準備します：

| ID | day | text |
|----|-----|------|
| 1 | 2023-01-01 | "初診時所見：子宮体部類内膜癌 Stage IA。内膜生検の病理結果では、類内膜癌 Grade 1。MRIにて筋層浸潤は認めず。開腹子宮全摘術の方針とする。" |
| 1 | 2023-01-15 | "術前検査：胸部CT、腹部造影CTにて遠隔転移なし。血液検査にて貧血（Hb 9.8）あり、術前に貧血改善を要する。" |
| 1 | 2023-02-01 | "手術記録：腹腔鏡下子宮全摘+両側付属器切除術施行。手術時間2時間45分、出血量150ml。腹腔内に播種なし。術中合併症なし。" |
| 2 | 2023-01-15 | "病理レポート：卵巣生検の結果、高異型度漿液性癌。腹水細胞診陽性。CT上、腹腔内播種、大網転移あり。Stage IIIC。" |
| 2 | 2023-02-15 | "化学療法開始。TC療法（パクリタキセル175mg/m2+カルボプラチンAUC5）。心エコーにてEF 48%と低下あり、心機能に留意して治療継続。" |
| 2 | 2023-03-15 | "化学療法2コース目実施。Grade 3の好中球減少を認め、G-CSF製剤使用。腹水は画像上改善傾向。" |
| 3 | 2023-03-01 | "紹介状要約：漿液性卵巣癌 T3cN1M0。腹部膨満を主訴に前医受診し、精査にて卵巣癌と診断。抗凝固薬（ワーファリン）服用中。" |
| 3 | 2023-03-15 | "術前カンファレンス記録：開腹手術の方針。抗凝固薬は術前5日前より休薬、ヘパリン置換の方針。輸血準備必要。" |
| 3 | 2023-04-01 | "手術記録：開腹卵巣腫瘍摘出術+大網切除術施行。手術時間4時間30分、出血量1200ml。RCC 4単位輸血。腫瘍は右卵巣原発、径18cm大。" |
| 3 | 2023-04-15 | "病理結果：High-grade serous carcinoma、大網転移陽性。腹水細胞診陽性。術後補助化学療法の方針とする。" |

**重要**: 列名は必ず `ID`, `day`, `text` としてください。

### 2. プロンプトテンプレートの準備
`prompt_templates.json`に分析ルールを定義します：
```json
{
    "cancer_stage": {
        "name": "がんステージ抽出",
        "description": "説明",
        "system_prompt": "抽出ルール...",
        "analysis_type": "extract"
    }
}
```

### 3. サーバーの起動
```bash
# ターミナル1で実行
python llm_server.py
```

### 4. 分析の実行
```python
from excel_analyzer import ExcelAnalyzer

# 初期化
analyzer = ExcelAnalyzer(
    file_path="data.xlsx",
    llm_server_url="http://localhost:8000",
    template_path="prompt_templates.json"
)

# データ読み込み
analyzer.load_excel()

# テンプレートを使用した分析
analyzer.analyze_with_template("cancer_stage")
analyzer.analyze_with_template("tumor_size")
analyzer.analyze_with_template("metastasis")

# 結果の保存
analyzer.save_results()
```

## 分析タイプ

### 1. 情報抽出モード（extract）
- 特定の情報を抽出（例：ステージ、サイズ）
- 結果は文字列として保存
- 情報が見つからない場合は"N/A"

### 2. 真偽判定モード（binary）
- はい/いいえで答えられる質問用
- 結果はTrue/Falseとして保存

## 出力形式

### 1. Excelファイル
- 入力ファイル名 + "_analyzed.xlsx"
- 列の順序：
  1. 基本列（ID, day, text）
  2. 分析結果列
  3. その他の列

### 2. 分析レポート
```
分析結果の概要:
- 分析結果_XXX:
  総データ数: 100
  ユニークな値の数: 5
  未検出(N/A)の数: 10
  主な抽出結果:
    - 値A: 30件
    - 値B: 25件
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