import streamlit as st
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import ExcelAnalyzer 
import pandas as pd

def main():
    # ページ設定 - アプリケーションのタイトルとレイアウトを設定
    st.set_page_config(
        page_title="医療記録分析システム",
        page_icon="🏥",
        layout="wide"  # 画面を広く使用
    )

    st.title("医療記録分析システム")

    # サイドバーの設定 - 分析に必要な基本設定を行うエリア
    with st.sidebar:
        st.header("設定")
        # LLMサーバーの設定
        llm_server_url = st.text_input(
            "LLMサーバーURL",
            value="http://localhost:8000/v1",
            help="OpenAI互換のLLMサーバーのURLを入力してください。デフォルトはローカルホストです。"
        )
        
        # テンプレートファイルの設定
        template_path = st.text_input(
            "テンプレートファイルパス",
            value="templates/prompt_templates.json",
            help="分析テンプレートのJSONファイルパスを入力してください。分析の種類や方法を定義します。"
        )

    # メインコンテンツエリア
    # Excelファイルのアップロード機能
    uploaded_file = st.file_uploader(
        "医療記録Excelファイルをアップロード", 
        type=['xlsx'],
        help="分析対象の医療記録データをExcelファイル形式でアップロードしてください。"
    )

    if uploaded_file is not None:
        # ExcelAnalyzerのインスタンスを作成 - 分析エンジンの初期化
        analyzer = ExcelAnalyzer(
            llm_server_url=llm_server_url,
            template_path=template_path
        )

        # アップロードされたファイルを一時保存して読み込む
        with open("temp.xlsx", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if analyzer.load_excel("temp.xlsx"):
            st.success("ファイルの読み込みが完了しました")

            # データプレビュー - アップロードされたデータの確認
            st.subheader("データプレビュー")
            st.write("アップロードされたデータの最初の数行を表示します")
            st.dataframe(analyzer.df.head())

            # 分析オプションの設定
            st.subheader("分析オプション")
            
            col1, col2 = st.columns(2)
            
            # 分析テンプレートの選択
            with col1:
                selected_templates = st.multiselect(
                    "実行する分析を選択",
                    options=analyzer.templates.keys(),
                    default=list(analyzer.templates.keys()),
                    format_func=lambda x: analyzer.templates[x]["name"],
                    help="実行したい分析の種類を選択してください。複数選択可能です。"
                )

            # 特定の患者IDの選択
            with col2:
                sample_id = st.selectbox(
                    "サンプルIDを選択（オプション）",
                    options=["すべて"] + list(analyzer.df["ID"].unique()),
                    help="特定の患者のデータのみを分析する場合は、該当のIDを選択してください。"
                )

            # 分析実行ボタンと処理
            if st.button("分析を実行", type="primary", help="選択した分析を開始します"):
                with st.spinner("分析を実行中..."):
                    # 選択された各テンプレートに対して分析を実行
                    for template_key in selected_templates:
                        progress_text = f"{analyzer.templates[template_key]['name']}の分析中..."
                        st.write(progress_text)
                        analyzer.analyze_with_template(template_key)

                    # 分析結果の保存
                    analyzer.save_results("analyzed_results.xlsx")
                    
                    # 分析結果の表示
                    st.subheader("分析結果")
                    result_df = analyzer.df
                    if sample_id != "すべて":
                        result_df = result_df[result_df["ID"] == sample_id]
                    
                    st.write("分析結果の一覧を表示します")
                    st.dataframe(result_df)

                    # 結果のダウンロード機能
                    with open("analyzed_results.xlsx", "rb") as f:
                        st.download_button(
                            label="分析結果をダウンロード",
                            data=f,
                            file_name="analyzed_results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            help="分析結果をExcelファイルとしてダウンロードできます"
                        )

            # 個別の医療記録テキスト表示
            if sample_id != "すべて":
                st.subheader(f"ID: {sample_id} の医療記録")
                st.write("選択された患者の医療記録の詳細を表示します")
                combined_texts = analyzer.get_combined_texts(sample_id)
                if combined_texts:
                    st.text_area(
                        "医療記録", 
                        combined_texts[sample_id], 
                        height=300,
                        help="選択された患者の全ての医療記録を時系列で表示します"
                    )

if __name__ == "__main__":
    main() 