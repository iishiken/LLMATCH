from excel_analyzer import ExcelAnalyzer

def main():
    # アナライザーの初期化
    analyzer = ExcelAnalyzer(
        file_path="sample_data.xlsx",
        llm_server_url="http://localhost:8000",
        template_path="prompt_templates.json"
    )
    
    # ファイルの読み込み
    if not analyzer.load_excel():
        return

    # テンプレートを使用した分析
    analyzer.analyze_with_template("cancer_diagnosis")   # がん診断名の抽出
    analyzer.analyze_with_template("cancer_stage")       # ステージ情報の抽出
    analyzer.analyze_with_template("important_dates")    # 重要日付の抽出
    analyzer.analyze_with_template("diagnostic_test")    # 診断検査の抽出
    analyzer.analyze_with_template("first_treatment")    # 初回治療情報の抽出
    analyzer.analyze_with_template("chemotherapy_info")  # 抗がん剤治療情報の抽出
    analyzer.analyze_with_template("surgery_type")       # 術式の抽出
    analyzer.analyze_with_template("special_notes")      # 特記事項の抽出

    # 結果の保存
    analyzer.save_results()

if __name__ == "__main__":
    main() 