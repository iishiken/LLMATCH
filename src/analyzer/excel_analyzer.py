# 必要なライブラリのインポート
import pandas as pd
from typing import List, Optional, Dict
from openai import OpenAI
from time import sleep
import json
import numpy as np

class ExcelAnalyzer:
    """
    医療テキストデータの分析を行うクラス。
    Excelファイルから医療記録を読み込み、LLMを使用して様々な情報を抽出・分析する。
    """
    def __init__(self, llm_server_url: str = "http://localhost:8000", template_path: str = None):
        """
        Parameters:
        - llm_server_url: OpenAI互換のvLLMサーバーのURL（デフォルトはlocalhost:8000）
        - template_path: プロンプトテンプレートのJSONファイルパス
        """
        self.file_path = None  # file_pathは後でload_excelで設定する
        self.df = None
        self.column_mapping = {
            'id_column': 'ID',
            'date_column': 'day',
            'text_column': 'text'
        }
        
        # OpenAIクライアントの初期化（vLLMサーバーに接続）
        self.client = OpenAI(
            api_key="EMPTY",
            base_url=f"{llm_server_url}"
        )
        
        # デフォルトのモデル名を設定
        self.model_name = "Qwen/Qwen2.5-72B-Instruct-GPTQ-Int4"
        
        # プロンプトテンプレートの保存用辞書
        self.templates: Dict = {}
        if template_path:
            self.load_templates(template_path)

    def set_column_mapping(self, id_column: str, date_column: str, text_column: str):
        """列名のマッピングを設定する"""
        self.column_mapping = {
            'id_column': id_column,
            'date_column': date_column,
            'text_column': text_column
        }

    def _validate_data(self) -> bool:
        """データが読み込まれているかを確認"""
        if self.df is None:
            print("エラー: データが読み込まれていません")
            return False
        return True

    def load_excel(self, file_path: str) -> bool:
        """Excelファイルを読み込み、必須列の存在チェックを行う"""
        self.file_path = file_path
        try:
            self.df = pd.read_excel(self.file_path)
            
            # 必須列の存在チェック
            missing_columns = [col for col in self.column_mapping.values() if col not in self.df.columns]
            if missing_columns:
                print(f"エラー: 以下の必須列が見つかりません: {', '.join(missing_columns)}")
                print(f"必要な列名: {', '.join(self.column_mapping.values())}")
                return False
                
            print("ファイルの読み込みが完了しました")
            return True
            
        except FileNotFoundError:
            print(f"エラー: ファイル '{self.file_path}' が見つかりません")
            return False
        except Exception as e:
            print(f"エラー: ファイルの読み込み中にエラーが発生しました: {str(e)}")
            return False

    def display_data_info(self):
        """データの基本情報（行数、列一覧）を表示"""
        if not self._validate_data():
            return
            
        print(f"データ行数: {len(self.df)}")
        print("\n列一覧:")
        for col in self.df.columns:
            print(f"- {col}")

    def _combine_texts_by_id(self) -> dict:
        """同一IDの自由記載を日付順に結合する"""
        if not self._validate_data():
            return {}

        # 日付列を日付型に変換
        self.df[self.column_mapping['date_column']] = pd.to_datetime(self.df[self.column_mapping['date_column']])
        
        # IDでグループ化し、日付でソート
        combined_texts = {}
        for id_val in self.df[self.column_mapping['id_column']].unique():
            group = self.df[self.df[self.column_mapping['id_column']] == id_val].sort_values(self.column_mapping['date_column'])
            texts = [f"[{row[self.column_mapping['date_column']].strftime('%Y-%m-%d')}]\n{row[self.column_mapping['text_column']]}" 
                    for _, row in group.iterrows()]
            combined_texts[id_val] = "\n\n".join(texts)
        
        return combined_texts

    def get_combined_texts(self, id_value: Optional[str] = None) -> Dict[str, str]:
        """
        IDごとにまとめられたテキストを取得する
        
        Parameters:
        - id_value: 特定のIDのテキストのみを取得する場合に指定（省略可）
        
        Returns:
        - Dict[str, str]: {ID: まとめられたテキスト} の形式の辞書
        """
        combined_texts = self._combine_texts_by_id()
        
        if id_value is not None:
            if id_value in combined_texts:
                return {id_value: combined_texts[id_value]}
            print(f"警告: ID '{id_value}' が見つかりません")
            return {}
            
        return combined_texts


    def load_templates(self, template_path: str) -> bool:
        """プロンプトテンプレートをJSONファイルから読み込む"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
                
            # テンプレートの形式を検証
            required_keys = {"name", "analysis_type", "system_prompt"}
            for key, template in self.templates.items():
                missing_keys = required_keys - set(template.keys())
                if missing_keys:
                    print(f"警告: テンプレート '{key}' に必要なキーが不足しています: {missing_keys}")
                    return False
                    
            print(f"テンプレートを読み込みました（{len(self.templates)}件）")
            return True
            
        except FileNotFoundError:
            print(f"エラー: テンプレートファイル '{template_path}' が見つかりません")
            return False
        except json.JSONDecodeError:
            print(f"エラー: テンプレートファイルのJSON形式が不正です")
            return False
        except Exception as e:
            print(f"テンプレートの読み込みに失敗しました: {str(e)}")
            return False

    def analyze_with_template(self, template_key: str, progress_callback=None) -> dict:
        """指定されたテンプレートを使用して分析を実行"""
        if template_key not in self.templates:
            print(f"エラー: テンプレート '{template_key}' が見つかりません")
            return {"success": False, "error": "テンプレートが見つかりません"}

        template = self.templates[template_key]
        result = self.analyze_with_llm(
            question=template["name"],
            analysis_type=template["analysis_type"],
            system_prompt=template["system_prompt"],
            progress_callback=progress_callback
        )
        
        return {
            "success": result,
            "template_name": template["name"],
            "analysis_type": template["analysis_type"]
        }

    def analyze_with_llm(self, question: str, analysis_type: str = "extract", system_prompt: Optional[str] = None, progress_callback=None) -> bool:
        """LLMを使用して自由記載を分析し、結果を新しい列として追加"""
        if not self._validate_data():
            return False

        column_name = f"分析結果_{question[:10]}"
        default_value = False if analysis_type == "binary" else "N/A"
        
        try:
            combined_texts = self._combine_texts_by_id()
            results = {}
            
            total_items = len(combined_texts)
            for i, (id_val, text) in enumerate(combined_texts.items(), 1):
                try:
                    response = self._call_openai_api(text, question, analysis_type, system_prompt)
                    result = self._parse_llm_response(response) if analysis_type == "binary" else response.strip()
                    results[id_val] = result
                    
                    if progress_callback:
                        # int64型をint型に変換してからJSONシリアライズ可能な形式に変換
                        callback_id = int(id_val) if isinstance(id_val, (np.int64, np.int32)) else id_val
                        progress_callback(i, total_items, {"ID": callback_id, "結果": result})
                        
                    sleep(0.5)  # API制限対策
                except Exception as e:
                    print(f"警告: ID {id_val} の分析中にエラーが発生: {str(e)}")
                    results[id_val] = default_value

            self.df[column_name] = self.df[self.column_mapping['id_column']].map(results).fillna(default_value)
            print(f"分析が完了しました。新しい列 '{column_name}' が追加されました。")
            return True

        except Exception as e:
            print(f"エラー: LLM分析中にエラーが発生しました: {str(e)}")
            return False

    def _get_default_system_prompt(self, analysis_type: str) -> str:
        """分析タイプに応じたデフォルトのシステムプロンプトを返す"""
        if analysis_type == "binary":
            return "与えられたテキストに対して質問に答えてください。回答は 'はい' または 'いいえ' でお願いします。"
        return """
        与えられたテキストから情報を抽出してください。
        - 回答は抽出した情報のみを簡潔に返してください
        - 情報が見つからない場合は 'N/A' と返してください
        - 説明や追加のコメントは不要です
        - 複数の情報がある場合は、最新の情報を返してください
        """

    def _call_openai_api(self, text: str, question: str, analysis_type: str, system_prompt: Optional[str] = None) -> str:
        """OpenAI互換のvLLMサーバーを呼び出してテキスト分析を実行"""
        try:
            system_prompt = system_prompt or self._get_default_system_prompt(analysis_type)

            # テキストが長すぎる場合は最新部分のみ使用
            max_length = 4000
            if len(text) > max_length:
                text = text[-max_length:]
                print("警告: テキストが長すぎるため、最新の部分のみを使用します")

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"テキスト: {text}\n\n質問: {question}"}
            ]

            completion = self.client.chat.completions.create(
                model=self.model_name,  # インスタンス変数のモデル名を使用
                messages=messages,
                temperature=0.7,
                max_tokens=512
            )
            
            return completion.choices[0].message.content.strip()

        except Exception as e:
            raise Exception(f"API呼び出し中にエラーが発生: {str(e)}")

    def _parse_llm_response(self, response: str) -> bool:
        """LLMの応答をブール値に変換"""
        return response.lower().startswith('はい')

    def get_matching_rows(self, column_name: str) -> pd.DataFrame:
        """指定された列でTrueとなっている行を抽出"""
        if not self._validate_data():
            return pd.DataFrame()

        if column_name not in self.df.columns:
            print(f"エラー: 列 '{column_name}' が見つかりません")
            return pd.DataFrame()

        return self.df[self.df[column_name] == True]

    def save_results(self, output_path: str = None) -> bool:
        """分析結果をExcelファイルとして保存"""
        if not self._validate_data():
            return False

        try:
            # 出力パスの設定
            if output_path is None:
                file_name = self.file_path.rsplit('.', 1)[0]
                output_path = f"{file_name}_analyzed.xlsx"

            # 分析結果の列を特定
            analysis_columns = [col for col in self.df.columns if col.startswith('分析結果_')]
            if not analysis_columns:
                print("警告: 分析結果の列が見つかりません")
                return False

            # IDごとに結合したテキストを取得
            combined_texts = self._combine_texts_by_id()
            
            # 新しいデータフレームを作成（ID、結合テキスト、分析結果のみ）
            result_df = pd.DataFrame()
            result_df[self.column_mapping['id_column']] = list(combined_texts.keys())
            result_df['text'] = [combined_texts[id_val] for id_val in result_df[self.column_mapping['id_column']]]
            
            # 分析結果の列を追加
            for col in analysis_columns:
                # 各IDに対応する分析結果を取得（最初の行の値を使用）
                result_df[col] = result_df[self.column_mapping['id_column']].apply(
                    lambda id_val: self.df[self.df[self.column_mapping['id_column']] == id_val][col].iloc[0] 
                    if not self.df[self.df[self.column_mapping['id_column']] == id_val][col].empty else None
                )
            
            # 保存と結果表示
            result_df.to_excel(output_path, index=False)
            print(f"分析結果を '{output_path}' に保存しました")
            self._display_analysis_summary(analysis_columns)
            return True

        except Exception as e:
            print(f"エラー: ファイルの保存中にエラーが発生しました: {str(e)}")
            return False

    def _display_analysis_summary(self, analysis_columns: List[str]):
        """分析結果の概要を表示"""
        print("\n分析結果の概要:")
        for col in analysis_columns:
            if self.df[col].dtype == bool:
                true_count = self.df[col].sum()
                total_count = len(self.df)
                percentage = (true_count / total_count) * 100
                print(f"- {col}:")
                print(f"  該当件数: {true_count}/{total_count} ({percentage:.1f}%)")
            else:
                value_counts = self.df[col].value_counts()
                na_count = self.df[col].isna().sum() + (self.df[col] == 'N/A').sum()
                print(f"- {col}:")
                print(f"  総データ数: {len(self.df)}")
                print(f"  ユニークな値の数: {len(value_counts)}")
                print(f"  未検出(N/A)の数: {na_count}")
                if len(value_counts) > 0:
                    print("  主な抽出結果:")
                    for value, count in value_counts.head(5).items():
                        print(f"    - {value}: {count}件")

    def get_available_models(self) -> List[str]:
        """
        LLMサーバーで利用可能なモデル一覧を取得する

        Returns:
            List[str]: 利用可能なモデル名のリスト
        """
        try:
            response = self.client.models.list()
            return [model.id for model in response.data]
        except Exception as e:
            print(f"モデル一覧の取得に失敗しました: {str(e)}")
            return []

    def set_model(self, model_name: str):
        """
        使用するモデルを設定する

        Parameters:
            model_name (str): 使用するモデルの名前
        """
        self.model_name = model_name