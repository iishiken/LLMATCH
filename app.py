import streamlit as st
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from analyzer import ExcelAnalyzer 
from data.data_generator import MedicalDataGenerator
import pandas as pd
import altair as alt

def display_analysis_summary_streamlit(analyzer, analysis_columns):
    """
    分析結果の概要をStreamlitで視覚的に表示する関数
    
    Parameters:
    - analyzer: ExcelAnalyzerのインスタンス
    - analysis_columns: 分析結果の列名リスト
    """
    st.subheader("分析結果の概要")
    
    for col in analysis_columns:
        with st.expander(f"📊 {col}", expanded=True):
            if analyzer.df[col].dtype == bool:
                # ブール型の列（バイナリ分析結果）の場合
                true_count = analyzer.df[col].sum()
                total_count = len(analyzer.df)
                percentage = (true_count / total_count) * 100
                
                # 進捗バーで表示
                st.metric(
                    label="該当件数", 
                    value=f"{true_count}/{total_count}",
                    delta=f"{percentage:.1f}%"
                )
                
                # チャートで表示
                chart_data = pd.DataFrame({
                    '結果': ['該当', '非該当'],
                    '件数': [true_count, total_count - true_count]
                })
                
                chart = alt.Chart(chart_data).mark_bar().encode(
                    x='結果',
                    y='件数',
                    color=alt.Color('結果', scale=alt.Scale(
                        domain=['該当', '非該当'],
                        range=['#1f77b4', '#d3d3d3']
                    ))
                ).properties(width=400)
                
                st.altair_chart(chart, use_container_width=True)
                
            else:
                # 文字列型の列（抽出・分類結果）の場合
                value_counts = analyzer.df[col].value_counts()
                na_count = analyzer.df[col].isna().sum() + (analyzer.df[col] == 'N/A').sum()
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("総データ数", f"{len(analyzer.df)}件")
                with col2:
                    st.metric("ユニークな値の数", f"{len(value_counts)}種類")
                with col3:
                    st.metric("未検出(N/A)の数", f"{na_count}件")
                
                if len(value_counts) > 0:
                    st.subheader("主な抽出結果")
                    
                    # 上位5件をテーブルで表示
                    top_results = pd.DataFrame({
                        '抽出結果': value_counts.head(5).index,
                        '件数': value_counts.head(5).values
                    })
                    st.table(top_results)
                    
                    # 円グラフで表示（上位5件+その他）
                    if len(value_counts) > 5:
                        pie_data = pd.DataFrame({
                            'カテゴリ': list(value_counts.head(5).index) + ['その他'],
                            '件数': list(value_counts.head(5).values) + [value_counts[5:].sum()]
                        })
                    else:
                        pie_data = pd.DataFrame({
                            'カテゴリ': value_counts.index,
                            '件数': value_counts.values
                        })
                    
                    pie_chart = alt.Chart(pie_data).mark_arc().encode(
                        theta='件数',
                        color='カテゴリ',
                        tooltip=['カテゴリ', '件数']
                    ).properties(width=400, height=400)
                    
                    st.altair_chart(pie_chart, use_container_width=True)

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
        
        # LLMプロバイダーの選択
        provider = st.selectbox(
            "LLMプロバイダー",
            options=["vllm", "openai", "gemini", "claude", "deepseek"],
            help="使用するLLMプロバイダーを選択してください"
        )
        
        # APIキーの入力（vllm以外の場合）
        api_key = None
        if provider != "vllm":
            # 環境変数名を取得
            env_var_name = ExcelAnalyzer.ENV_VAR_NAMES.get(provider)
            
            # デバッグ情報の表示
            st.write("### デバッグ情報")
            st.write(f"検索する環境変数名: {env_var_name}")
            
            # 環境変数の直接確認
            import subprocess
            try:
                result = subprocess.run(['echo', f"${env_var_name}"], capture_output=True, text=True)
                shell_env_value = result.stdout.strip()
                st.write(f"シェルでの環境変数の値: {shell_env_value if shell_env_value else '空または未設定'}")
            except Exception as e:
                st.write(f"シェルコマンドエラー: {str(e)}")

            # 環境変数の再読み込みを試みる
            try:
                import dotenv
                dotenv.load_dotenv(override=True)
            except Exception as e:
                st.write(f"環境変数再読み込みエラー: {str(e)}")
            
            # 現在の環境変数の状態を表示
            st.write(f"設定されている環境変数一覧:")
            env_vars = {k: v for k, v in os.environ.items() if k in ExcelAnalyzer.ENV_VAR_NAMES.values()}
            for k in env_vars.keys():
                env_value = os.environ.get(k, "")
                st.write(f"- {k}: {'設定済み' if env_value else '未設定'}")
            
            # 環境変数からAPIキーを取得（空文字列の場合はNoneとして扱う）
            env_api_key = os.environ.get(env_var_name, "").strip()
            st.write(f"環境変数から取得したAPIキーの長さ: {len(env_api_key) if env_api_key else 0}")
            
            if not env_api_key:
                env_api_key = None
                # シェルから直接取得を試みる
                try:
                    shell_cmd = f"echo ${env_var_name}"
                    shell_value = subprocess.check_output(shell_cmd, shell=True, text=True).strip()
                    if shell_value:
                        env_api_key = shell_value
                        st.write(f"シェルから直接APIキーを取得しました")
                except Exception as e:
                    st.write(f"シェルからの取得エラー: {str(e)}")
            
            st.info(f"""
            ### APIキーの設定方法
            1. 環境変数で設定（推奨）:
               - 環境変数名: `{env_var_name}`
               - 現在の状態: {'✅ 設定済み' if env_api_key else '❌ 未設定'}
            2. 直接入力（一時的）:
               - 下のテキストボックスに入力
            """)
            
            # 直接入力用のテキストボックス（環境変数が設定されている場合は非表示）
            if not env_api_key:
                api_key = st.text_input(
                    f"{provider.upper()}のAPIキー（任意）",
                    type="password",
                    help=f"環境変数 {env_var_name} が設定されていない場合のみ入力してください"
                )
            else:
                api_key = env_api_key
                st.success(f"環境変数 {env_var_name} からAPIキーを読み込みました")
            
            # APIキーが環境変数にもUIにも設定されていない場合は警告
            if not env_api_key and not api_key:
                st.warning(f"""
                APIキーが設定されていません。以下のいずれかの方法で設定してください：
                1. 環境変数 `{env_var_name}` を設定
                2. 上のテキストボックスに直接入力
                
                環境変数の設定方法:
                ```bash
                export {env_var_name}="your-api-key"
                ```
                
                現在の設定を確認:
                ```bash
                echo ${env_var_name}
                ```
                """)
        
        # LLMサーバーの設定（vllmの場合のみ表示）
        llm_server_url = None
        if provider == "vllm":
            llm_server_url = st.text_input(
                "LLMサーバーURL",
                value="http://10.240.59.247:8000/v1",
                help="OpenAI互換のLLMサーバーのURLを入力してください。デフォルトはwindows serverです。"
            )
        
        # 一時的なExcelAnalyzerインスタンスを作成してモデル一覧を取得
        try:
            temp_analyzer = ExcelAnalyzer(
                llm_server_url=llm_server_url,
                provider=provider,
                api_key=api_key  # 直接入力されたAPIキーを優先
            )
            available_models = temp_analyzer.get_available_models()

            # モデルの選択
            if available_models:
                selected_model = st.selectbox(
                    "使用するモデル",
                    options=available_models,
                    help="分析に使用するLLMモデルを選択してください"
                )
            else:
                st.error("利用可能なモデルを取得できませんでした")
                selected_model = temp_analyzer.model_name  # デフォルトモデルを使用
        except ValueError as e:
            st.error(str(e))
            st.stop()
        except Exception as e:
            st.error(f"エラーが発生しました: {str(e)}")
            st.stop()
        
        # テンプレートファイルの設定
        template_path = st.text_input(
            "テンプレートファイルパス",
            value="templates/prompt_templates.json",
            help="分析テンプレートのJSONファイルパスを入力してください。分析の種類や方法を定義します。"
        )

    # タブの作成 - 分析タブとテンプレート編集タブ
    tab1, tab2, tab3 = st.tabs(["分析実行", "テンプレート編集", "テストデータ生成"])
    
    with tab1:
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
                template_path=template_path,
                provider=provider,
                api_key=api_key
            )
            
            # 選択されたモデルを設定
            analyzer.set_model(selected_model)

            # アップロードされたファイルを一時保存して読み込む
            with open("temp.xlsx", "wb") as f:
                f.write(uploaded_file.getvalue())
            
            # 一時的にファイルを読み込んで列名を取得
            temp_df = pd.read_excel("temp.xlsx")
            columns = temp_df.columns.tolist()
            
            # 列の選択UI
            st.subheader("列の設定")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                id_column = st.selectbox(
                    "ID列を選択",
                    options=columns,
                    index=columns.index('ID') if 'ID' in columns else 0,
                    help="患者IDが格納されている列を選択してください"
                )
            
            with col2:
                date_column = st.selectbox(
                    "日付列を選択",
                    options=columns,
                    index=columns.index('day') if 'day' in columns else 0,
                    help="日付が格納されている列を選択してください"
                )
            
            with col3:
                text_column = st.selectbox(
                    "テキスト列を選択",
                    options=columns,
                    index=columns.index('text') if 'text' in columns else 0,
                    help="分析対象のテキストが格納されている列を選択してください"
                )
            
            # 列のマッピングを設定
            analyzer.set_column_mapping(id_column, date_column, text_column)
        
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
                        options=["すべて"] + list(analyzer.df[analyzer.column_mapping['id_column']].unique()),
                        help="特定の患者のデータのみを分析する場合は、該当のIDを選択してください。"
                    )

                # 分析実行ボタンと処理
                if st.button("分析を実行", type="primary", help="選択した分析を開始します"):
                    # 停止フラグの初期化
                    if 'stop_analysis' not in st.session_state:
                        st.session_state.stop_analysis = False

                    # プログレスバーの初期化
                    progress_bar = st.progress(0)
                    status_container = st.empty()
                    result_container = st.empty()
                    
                    # 停止ボタン
                    if st.button("分析を停止", type="secondary"):
                        st.session_state.stop_analysis = True
                        st.warning("分析を停止しています...")
                        return

                    with st.spinner("分析を実行中..."):
                        # 選択された各テンプレートに対して分析を実行
                        total_templates = len(selected_templates)
                        for i, template_key in enumerate(selected_templates):
                            if st.session_state.stop_analysis:
                                st.warning("分析が停止されました")
                                break

                            template_name = analyzer.templates[template_key]["name"]
                            status_container.write(f"進捗: {i+1}/{total_templates} - {template_name}の分析中...")
                            
                            # テンプレートごとの進捗を更新
                            progress = (i + 1) / total_templates
                            progress_bar.progress(progress)

                            # 分析実行時の詳細な進捗表示用のコンテナ
                            analysis_progress = st.empty()
                            analysis_result = st.empty()

                            def progress_callback(current_row, total_rows, result):
                                analysis_progress.write(f"🔄 {total_rows}件中{current_row}件目を処理中 ({(current_row/total_rows*100):.1f}%)")
                                if result:
                                    analysis_result.write(f"""
                                    **最新の分析結果:**
                                    ```json
                                    {json.dumps(result, ensure_ascii=False, indent=2)}
                                    ```
                                    """)

                            # コールバック関数を渡して分析を実行
                            result = analyzer.analyze_with_template(template_key, progress_callback=progress_callback)
                            
                            # 分析結果をリアルタイムで表示
                            with result_container.container():
                                st.write(f"✅ {template_name}の分析が完了")
                                # 最新の分析結果を表示
                                latest_col = [col for col in analyzer.df.columns if col.startswith('分析結果_')][-1]
                                st.dataframe(analyzer.df[[analyzer.column_mapping['id_column'], latest_col]].head())

                        if not st.session_state.stop_analysis:
                            # 分析結果の保存
                            status_container.write("分析結果を保存中...")
                            analyzer.save_results("analyzed_results.xlsx")
                            
                            # 分析結果の列を特定
                            analysis_columns = [col for col in analyzer.df.columns if col.startswith('分析結果_')]
                            
                            # 結合テキストを含む新しいデータフレームを読み込む
                            result_df = pd.read_excel("analyzed_results.xlsx")
                            
                            # プログレスバーを完了状態に
                            progress_bar.progress(1.0)
                            status_container.success("すべての分析が完了しました！")

                            # 分析結果の概要を表示
                            if analysis_columns:
                                # 全体の分析結果概要
                                if sample_id == "すべて":
                                    # 新しいExcelAnalyzerインスタンスを作成して結果データを設定
                                    summary_analyzer = ExcelAnalyzer(llm_server_url=llm_server_url, template_path=template_path)
                                    summary_analyzer.df = result_df
                                    display_analysis_summary_streamlit(summary_analyzer, analysis_columns)
                                else:
                                    # 特定IDの分析結果概要
                                    temp_df = result_df[result_df[analyzer.column_mapping['id_column']] == sample_id].copy()
                                    temp_analyzer = ExcelAnalyzer(llm_server_url=llm_server_url, template_path=template_path)
                                    temp_analyzer.df = temp_df
                                    
                                    st.subheader(f"ID: {sample_id} の分析結果概要")
                                    display_analysis_summary_streamlit(temp_analyzer, analysis_columns)
                            
                            # 分析結果の表示
                            st.subheader("分析結果データ")
                            if sample_id != "すべて":
                                result_df = result_df[result_df[analyzer.column_mapping['id_column']] == sample_id]
                            
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
                    
                    # 結合テキストがすでに保存されている場合はそれを使用
                    if 'result_df' in locals() and not result_df.empty and 'text' in result_df.columns:
                        sample_text = result_df.iloc[0]['text']
                        st.text_area(
                            "医療記録", 
                            sample_text, 
                            height=300,
                            help="選択された患者の全ての医療記録を時系列で表示します"
                        )
                    else:
                        # 従来の方法でテキストを取得
                        combined_texts = analyzer.get_combined_texts(sample_id)
                        if combined_texts:
                            st.text_area(
                                "医療記録", 
                                combined_texts[sample_id], 
                                height=300,
                                help="選択された患者の全ての医療記録を時系列で表示します"
                            )
    
    with tab2:
        st.header("プロンプトテンプレート編集")
        
        # テンプレートファイルの読み込み
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                templates = json.load(f)
            
            # テンプレートの選択
            template_keys = list(templates.keys())
            selected_template = st.selectbox(
                "編集するテンプレートを選択",
                options=template_keys,
                format_func=lambda x: templates[x]["name"],
                help="編集したいテンプレートを選択してください"
            )
            
            if selected_template:
                # 選択されたテンプレートの編集フォーム
                st.subheader(f"テンプレート: {templates[selected_template]['name']}")
                
                # テンプレートの各項目を編集するフォーム
                with st.form(key="template_edit_form"):
                    # テンプレートキー（変更不可）
                    st.text_input("テンプレートキー", value=selected_template, disabled=True)
                    
                    # 名前
                    template_name = st.text_input(
                        "名前", 
                        value=templates[selected_template]["name"],
                        help="テンプレートの表示名を入力してください"
                    )
                    
                    # 説明
                    template_description = st.text_input(
                        "説明", 
                        value=templates[selected_template].get("description", ""),
                        help="テンプレートの説明を入力してください"
                    )
                    
                    # 分析タイプ
                    template_analysis_type = st.selectbox(
                        "分析タイプ",
                        options=["extract", "classify", "summarize"],
                        index=["extract", "classify", "summarize"].index(templates[selected_template]["analysis_type"]),
                        help="分析の種類を選択してください"
                    )
                    
                    # システムプロンプト
                    template_system_prompt = st.text_area(
                        "システムプロンプト",
                        value=templates[selected_template]["system_prompt"],
                        height=300,
                        help="LLMに送信するシステムプロンプトを入力してください"
                    )
                    
                    # 保存ボタン
                    submit_button = st.form_submit_button(label="変更を保存", type="primary")
                    
                    if submit_button:
                        # テンプレートの更新
                        templates[selected_template]["name"] = template_name
                        templates[selected_template]["description"] = template_description
                        templates[selected_template]["analysis_type"] = template_analysis_type
                        templates[selected_template]["system_prompt"] = template_system_prompt
                        
                        # ファイルに保存
                        try:
                            with open(template_path, 'w', encoding='utf-8') as f:
                                json.dump(templates, f, ensure_ascii=False, indent=2)
                            st.success("テンプレートを保存しました")
                        except Exception as e:
                            st.error(f"テンプレートの保存に失敗しました: {str(e)}")
                
                # 新しいテンプレートの追加ボタン
                if st.button("新しいテンプレートを追加"):
                    st.session_state.add_new_template = True
                
                # 新しいテンプレート追加フォーム
                if st.session_state.get("add_new_template", False):
                    st.subheader("新しいテンプレートを追加")
                    with st.form(key="new_template_form"):
                        new_template_key = st.text_input(
                            "テンプレートキー（一意のID）", 
                            help="英数字とアンダースコアのみを使用してください"
                        )
                        
                        new_template_name = st.text_input(
                            "名前", 
                            help="テンプレートの表示名を入力してください"
                        )
                        
                        new_template_description = st.text_input(
                            "説明", 
                            help="テンプレートの説明を入力してください"
                        )
                        
                        new_template_analysis_type = st.selectbox(
                            "分析タイプ",
                            options=["extract", "classify", "summarize"],
                            help="分析の種類を選択してください"
                        )
                        
                        new_template_system_prompt = st.text_area(
                            "システムプロンプト",
                            height=300,
                            help="LLMに送信するシステムプロンプトを入力してください"
                        )
                        
                        add_button = st.form_submit_button(label="テンプレートを追加", type="primary")
                        
                        if add_button and new_template_key and new_template_name and new_template_system_prompt:
                            if new_template_key in templates:
                                st.error(f"テンプレートキー '{new_template_key}' は既に存在します")
                            else:
                                # 新しいテンプレートを追加
                                templates[new_template_key] = {
                                    "name": new_template_name,
                                    "description": new_template_description,
                                    "analysis_type": new_template_analysis_type,
                                    "system_prompt": new_template_system_prompt
                                }
                                
                                # ファイルに保存
                                try:
                                    with open(template_path, 'w', encoding='utf-8') as f:
                                        json.dump(templates, f, ensure_ascii=False, indent=2)
                                    st.success("新しいテンプレートを追加しました")
                                    st.session_state.add_new_template = False
                                except Exception as e:
                                    st.error(f"テンプレートの保存に失敗しました: {str(e)}")
                
                # テンプレート削除ボタン
                if st.button("このテンプレートを削除", type="secondary"):
                    st.session_state.confirm_delete = True
                    st.session_state.delete_template_key = selected_template
                
                # 削除確認ダイアログ
                if st.session_state.get("confirm_delete", False) and st.session_state.get("delete_template_key") == selected_template:
                    st.warning(f"テンプレート '{templates[selected_template]['name']}' を削除してもよろしいですか？")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("はい、削除します"):
                            # テンプレートを削除
                            del templates[selected_template]
                            
                            # ファイルに保存
                            try:
                                with open(template_path, 'w', encoding='utf-8') as f:
                                    json.dump(templates, f, ensure_ascii=False, indent=2)
                                st.success("テンプレートを削除しました")
                                st.session_state.confirm_delete = False
                                st.session_state.delete_template_key = None
                                st.rerun()  # ページを再読み込み
                            except Exception as e:
                                st.error(f"テンプレートの削除に失敗しました: {str(e)}")
                    with col2:
                        if st.button("いいえ、キャンセル"):
                            st.session_state.confirm_delete = False
                            st.session_state.delete_template_key = None
                            st.rerun()  # ページを再読み込み
                
        except FileNotFoundError:
            st.error(f"テンプレートファイル '{template_path}' が見つかりません")
        except json.JSONDecodeError:
            st.error(f"テンプレートファイルのJSON形式が不正です")
        except Exception as e:
            st.error(f"テンプレートの読み込みに失敗しました: {str(e)}")

    with tab3:
        st.header("テストデータ生成")
        
        # データ生成オプションの設定
        st.subheader("生成オプション")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_patients = st.number_input(
                "患者数",
                min_value=1,
                max_value=1000,
                value=50,
                help="生成する患者データの数を指定してください"
            )
        
        with col2:
            output_filename = st.text_input(
                "出力ファイル名",
                value="sample_data.xlsx",
                help="生成したデータを保存するExcelファイルの名前を指定してください"
            )
        
        # データ生成の実行
        if st.button("テストデータを生成", type="primary"):
            try:
                with st.spinner("データを生成中..."):
                    # ジェネレーターの初期化
                    generator = MedicalDataGenerator()
                    
                    # データの生成と保存
                    generator.save_to_excel(output_filename, num_patients=num_patients)
                    
                    # 生成したデータのプレビュー
                    df = pd.read_excel(output_filename)
                    
                    st.success(f"{num_patients}件のテストデータを生成し、{output_filename}に保存しました")
                    
                    # データの統計情報を表示
                    st.subheader("生成データの統計")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("総レコード数", len(df))
                    with col2:
                        st.metric("ユニーク患者数", df['ID'].nunique())
                    with col3:
                        st.metric("平均レコード数/患者", round(len(df) / df['ID'].nunique(), 1))
                    
                    # データプレビュー
                    st.subheader("データプレビュー")
                    st.dataframe(df.head())
                    
                    # ダウンロードボタン
                    with open(output_filename, "rb") as f:
                        st.download_button(
                            label="生成したデータをダウンロード",
                            data=f,
                            file_name=output_filename,
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    
                    # 詳細な統計情報
                    with st.expander("詳細な統計情報"):
                        # 日付の範囲
                        st.write("#### 日付範囲")
                        min_date = pd.to_datetime(df['day'].min())
                        max_date = pd.to_datetime(df['day'].max())
                        st.write(f"開始日: {min_date.strftime('%Y-%m-%d')}")
                        st.write(f"終了日: {max_date.strftime('%Y-%m-%d')}")
                        st.write(f"期間: {(max_date - min_date).days}日")
                        
                        # テキストの統計
                        st.write("#### テキスト統計")
                        text_lengths = df['text'].str.len()
                        st.write(f"平均文字数: {round(text_lengths.mean(), 1)}")
                        st.write(f"最小文字数: {text_lengths.min()}")
                        st.write(f"最大文字数: {text_lengths.max()}")
                        
                        # テキストサンプル
                        st.write("#### テキストサンプル")
                        sample_texts = df.sample(min(3, len(df)))['text'].tolist()
                        for i, text in enumerate(sample_texts, 1):
                            st.text_area(f"サンプル {i}", text, height=100)
            
            except Exception as e:
                st.error(f"データ生成中にエラーが発生しました: {str(e)}")
                st.write("エラーの詳細:")
                st.exception(e)

if __name__ == "__main__":
    # セッション状態の初期化
    if "add_new_template" not in st.session_state:
        st.session_state.add_new_template = False
    if "confirm_delete" not in st.session_state:
        st.session_state.confirm_delete = False
    if "delete_template_key" not in st.session_state:
        st.session_state.delete_template_key = None
        
    main() 