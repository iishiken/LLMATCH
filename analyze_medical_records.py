import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import ExcelAnalyzer

def main():
    # サンプルデータのパスを指定
    sample_data_path = "data/sample_data.xlsx"
    
    # ExcelAnalyzerのインスタンスを作成
    analyzer = ExcelAnalyzer(
        llm_server_url="http://localhost:8000/v1",
        template_path="templates/prompt_templates.json"
    )
    
    # サンプルデータの読み込み
    if not analyzer.load_excel(sample_data_path):
        print(f"エラー: {sample_data_path} の読み込みに失敗しました")
        return
    
    # データの基本情報を表示
    analyzer.display_data_info()
    
    # 各テンプレートを使用して分析を実行
    templates_to_analyze = [
        "cancer_diagnosis",
        "cancer_stage",
        "diagnostic_test",
        "first_treatment",
        "chemotherapy_info",
        "surgery_type",
        "special_notes"
    ]
    
    for template_key in templates_to_analyze:
        print(f"\n{template_key}の分析を開始します...")
        analyzer.analyze_with_template(template_key)
    
    # 分析結果を保存
    analyzer.save_results("analyzed_results.xlsx")

if __name__ == "__main__":
    main() 