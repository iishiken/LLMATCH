import pandas as pd
from typing import List, Optional, Dict
import requests
from time import sleep
import json

class ExcelAnalyzer:
    def __init__(self, file_path: str, llm_server_url: str = "http://localhost:8000", template_path: str = None):
        self.file_path = file_path
        self.df: Optional[pd.DataFrame] = None
        self.required_columns = ['ID', 'day', 'text']  # 固定の列名
        self.llm_server_url = llm_server_url
        self.templates: Dict = {}
        if template_path:
            self.load_templates(template_path)

    def load_excel(self) -> bool:
        """Excelファイルを読み込み、必須列の存在チェックを行う"""
        try:
            self.df = pd.read_excel(self.file_path)
            
            # 必須列の存在チェック
            missing_columns = [col for col in self.required_columns if col not in self.df.columns]
            if missing_columns:
                print(f"エラー: 以下の必須列が見つかりません: {', '.join(missing_columns)}")
                print(f"必要な列名: {', '.join(self.required_columns)}")
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
        """データの基本情報を表示"""
        if self.df is not None:
            print(f"データ行数: {len(self.df)}")
            print("\n列一覧:")
            for col in self.df.columns:
                print(f"- {col}")

    def _combine_texts_by_id(self) -> dict:
        """同一IDの自由記載を日付順に結合する"""
        if self.df is None:
            return {}

        # 日付列を日付型に変換
        self.df['day'] = pd.to_datetime(self.df['day'])
        
        # IDでグループ化し、日付でソート
        combined_texts = {}
        for id_val in self.df['ID'].unique():
            group = self.df[self.df['ID'] == id_val].sort_values('day')
            
            # 日付付きで自由記載を結合
            texts = []
            for _, row in group.iterrows():
                date_str = row['day'].strftime('[%Y-%m-%d]')
                texts.append(f"{date_str}\n{row['text']}")
            
            combined_texts[id_val] = "\n\n".join(texts)
        
        return combined_texts

    def load_templates(self, template_path: str) -> bool:
        """プロンプトテンプレートを読み込む"""
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

    def analyze_with_template(self, template_key: str) -> bool:
        """テンプレートを使用して分析を実行"""
        if template_key not in self.templates:
            print(f"エラー: テンプレート '{template_key}' が見つかりません")
            return False

        template = self.templates[template_key]
        return self.analyze_with_llm(
            question=template["name"],
            analysis_type=template["analysis_type"],
            system_prompt=template["system_prompt"]
        )

    def analyze_with_llm(self, question: str, analysis_type: str = "extract", system_prompt: Optional[str] = None) -> bool:
        """
        LLMを使用して自由記載を分析し、結果を新しい列として追加する
        
        Parameters:
        - question: 分析のための質問
        - analysis_type: 分析タイプ ("binary" または "extract")
        - system_prompt: カスタムシステムプロンプト
        """
        if self.df is None:
            print("エラー: データが読み込まれていません")
            return False

        column_name = f"分析結果_{question[:10]}"
        
        try:
            # 同一IDの自由記載を結合
            combined_texts = self._combine_texts_by_id()
            
            # 分析結果を格納する辞書
            results = {}
            
            # 分析タイプに応じて初期値を設定
            if analysis_type == "binary":
                default_value = False
            else:
                default_value = "N/A"

            # ID単位で分析
            for id_val, text in combined_texts.items():
                try:
                    response = self._call_openai_api(text, question, analysis_type, system_prompt)
                    
                    if analysis_type == "binary":
                        result = self._parse_llm_response(response)
                    else:
                        result = response.strip()
                    
                    results[id_val] = result
                    
                    # API制限を考慮して少し待機
                    sleep(0.5)
                    
                except Exception as e:
                    print(f"警告: ID {id_val} の分析中にエラーが発生: {str(e)}")
                    results[id_val] = default_value

            # 結果をデータフレームに追加
            self.df[column_name] = self.df['ID'].map(results).fillna(default_value)

            print(f"分析が完了しました。新しい列 '{column_name}' が追加されました。")
            return True

        except Exception as e:
            print(f"エラー: LLM分析中にエラーが発生しました: {str(e)}")
            return False

    def _call_openai_api(self, text: str, question: str, analysis_type: str, system_prompt: Optional[str] = None) -> str:
        """ローカルLLMサーバーを呼び出す"""
        try:
            if system_prompt is None:
                if analysis_type == "binary":
                    system_prompt = "与えられたテキストに対して質問に答えてください。回答は 'はい' または 'いいえ' でお願いします。"
                else:
                    system_prompt = """
                    与えられたテキストから情報を抽出してください。
                    - 回答は抽出した情報のみを簡潔に返してください
                    - 情報が見つからない場合は 'N/A' と返してください
                    - 説明や追加のコメントは不要です
                    - 複数の情報がある場合は、最新の情報を返してください
                    """

            # テキストが長すぎる場合の処理
            max_length = 4000
            if len(text) > max_length:
                text = text[-max_length:]
                print("警告: テキストが長すぎるため、最新の部分のみを使用します")

            # APIリクエストの準備
            payload = {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"以下のテキストについて質問に答えてください。\n\nテキスト: {text}\n\n質問: {question}"}
                ],
                "temperature": 0.7,
                "max_tokens": 512
            }

            # APIリクエストの送信
            response = requests.post(
                f"{self.llm_server_url}/v1/chat/completions",
                json=payload
            )
            
            if response.status_code != 200:
                raise Exception(f"APIエラー: {response.status_code} - {response.text}")

            return response.json()["content"].strip()

        except Exception as e:
            raise Exception(f"API呼び出し中にエラーが発生: {str(e)}")

    def _parse_llm_response(self, response: str) -> bool:
        """LLMの応答をブール値に変換する"""
        return response.lower().startswith('はい')

    def get_matching_rows(self, column_name: str) -> pd.DataFrame:
        """指定された列でTrueとなっている行を抽出する"""
        if self.df is None:
            print("エラー: データが読み込まれていません")
            return pd.DataFrame()

        if column_name not in self.df.columns:
            print(f"エラー: 列 '{column_name}' が見つかりません")
            return pd.DataFrame()

        return self.df[self.df[column_name] == True]

    def save_results(self, output_path: str = None) -> bool:
        """分析結果をExcelファイルとして保存する"""
        if self.df is None:
            print("エラー: データが読み込まれていません")
            return False

        try:
            # 出力パスが指定されていない場合、元のファイル名に '_analyzed' を追加
            if output_path is None:
                file_name = self.file_path.rsplit('.', 1)[0]
                output_path = f"{file_name}_analyzed.xlsx"

            # 分析結果の列を特定（'分析結果_'で始まる列）
            analysis_columns = [col for col in self.df.columns if col.startswith('分析結果_')]
            
            if not analysis_columns:
                print("警告: 分析結果の列が見つかりません")
                return False

            # 列の並び順を整理（基本列 + 分析結果列）
            column_order = self.required_columns + analysis_columns
            remaining_columns = [col for col in self.df.columns if col not in column_order]
            column_order.extend(remaining_columns)

            # 指定した列順でデータフレームを保存
            self.df[column_order].to_excel(output_path, index=False)
            print(f"分析結果を '{output_path}' に保存しました")
            
            # 分析結果の概要を表示
            self._display_analysis_summary(analysis_columns)
            
            return True

        except Exception as e:
            print(f"エラー: ファイルの保存中にエラーが発生しました: {str(e)}")
            return False

    def _display_analysis_summary(self, analysis_columns: List[str]):
        """分析結果の概要を表示する"""
        print("\n分析結果の概要:")
        for col in analysis_columns:
            if self.df[col].dtype == bool:
                # 真偽値の場合
                true_count = self.df[col].sum()
                total_count = len(self.df)
                percentage = (true_count / total_count) * 100
                print(f"- {col}:")
                print(f"  該当件数: {true_count}/{total_count} ({percentage:.1f}%)")
            else:
                # 抽出された情報の場合
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