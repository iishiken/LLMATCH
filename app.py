import streamlit as st
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import ExcelAnalyzer
import pandas as pd

def main():
    st.set_page_config(
        page_title="医療記録分析システム",
        page_icon="🏥",
        layout="wide"
    )

    st.title("医療記録分析システム")

    # サイドバーの設定
    with st.sidebar:
        st.header("設定")
        llm_server_url = st.text_input(
            "LLMサーバーURL",
            value="http://localhost:8000/v1",
            help="OpenAI互換のLLMサーバーのURLを入力してください"
        )
        
        template_path = st.text_input(
            "テンプレートファイルパス",
            value="templates/prompt_templates.json",
            help="分析テンプレートのJSONファイルパスを入力してください"
        )

    # メインコンテンツ
    uploaded_file = st.file_uploader("医療記録Excelファイルをアップロード", type=['xlsx'])

    if uploaded_file is not None:
        # ExcelAnalyzerのインスタンスを作成
        analyzer = ExcelAnalyzer(
            llm_server_url=llm_server_url,
            template_path=template_path
        )

        # ファイルを一時保存して読み込む
        with open("temp.xlsx", "wb") as f:
            f.write(uploaded_file.getvalue())
        
        if analyzer.load_excel("temp.xlsx"):
            st.success("ファイルの読み込みが完了しました")

            # データプレビュー
            st.subheader("データプレビュー")
            st.dataframe(analyzer.df.head())

            # 分析オプション
            st.subheader("分析オプション")
            
            col1, col2 = st.columns(2)
            
            with col1:
                selected_templates = st.multiselect(
                    "実行する分析を選択",
                    options=analyzer.templates.keys(),
                    default=list(analyzer.templates.keys()),
                    format_func=lambda x: analyzer.templates[x]["name"]
                )

            with col2:
                sample_id = st.selectbox(
                    "サンプルIDを選択（オプション）",
                    options=["すべて"] + list(analyzer.df["ID"].unique())
                )

            # 分析実行ボタン
            if st.button("分析を実行", type="primary"):
                with st.spinner("分析を実行中..."):
                    for template_key in selected_templates:
                        progress_text = f"{analyzer.templates[template_key]['name']}の分析中..."
                        st.write(progress_text)
                        analyzer.analyze_with_template(template_key)

                    # 結果の保存
                    analyzer.save_results("analyzed_results.xlsx")
                    
                    # 分析結果の表示
                    st.subheader("分析結果")
                    result_df = analyzer.df
                    if sample_id != "すべて":
                        result_df = result_df[result_df["ID"] == sample_id]
                    
                    st.dataframe(result_df)

                    # 結果のダウンロードボタン
                    with open("analyzed_results.xlsx", "rb") as f:
                        st.download_button(
                            label="分析結果をダウンロード",
                            data=f,
                            file_name="analyzed_results.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )

            # テキスト表示部分
            if sample_id != "すべて":
                st.subheader(f"ID: {sample_id} の医療記録")
                combined_texts = analyzer.get_combined_texts(sample_id)
                if combined_texts:
                    st.text_area("医療記録", combined_texts[sample_id], height=300)

if __name__ == "__main__":
    main() 