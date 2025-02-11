from excel_analyzer import ExcelAnalyzer

def main():
    # アナライザーの初期化（テンプレートファイルを指定）
    analyzer = ExcelAnalyzer(
        file_path="sample_data.xlsx",
        llm_server_url="http://localhost:8000",
        template_path="prompt_templates.json"
    )
    
    # ファイルの読み込み
    if not analyzer.load_excel():
        return

    # テンプレートを使用した分析
    analyzer.analyze_with_template("cancer_stage")  # ステージ情報の抽出
    analyzer.analyze_with_template("tumor_size")    # 腫瘍サイズの抽出
    analyzer.analyze_with_template("metastasis")    # 転移の有無の判定

    # 結果の保存
    analyzer.save_results()

if __name__ == "__main__":
    main() 