import pandas as pd
import random
from datetime import datetime, timedelta
import numpy as np

class MedicalDataGenerator:
    def __init__(self):
        # 基本的な診断名とその表記揺れ
        self.cancer_types = {
            "子宮体癌": ["子宮体がん", "子宮体部類内膜癌", "子宮内膜癌", "体部類内膜癌", "子宮体部癌"],
            "卵巣癌": ["卵巣がん", "卵巣腫瘍", "漿液性卵巣癌", "明細胞癌", "高異型度漿液性癌"],
            "子宮頸癌": ["子宮頸がん", "頸部扁平上皮癌", "子宮頚癌", "頚部腺癌", "子宮頸部癌"]
        }

        # 検査名とその表記揺れ
        self.diagnostic_tests = {
            "組織診": ["内膜組織診", "組織生検", "生検", "組織診断", "病理組織診断"],
            "細胞診": ["細胞診断", "細胞検査", "スメア", "細胞学的検査", "細胞病理診断"],
            "画像検査": ["MRI検査", "CT検査", "PET-CT", "超音波検査", "エコー"]
        }

        # 術式とその表記揺れ
        self.surgery_types = {
            "子宮全摘": ["子宮全摘出術", "子宮摘出術", "全摘術", "子宮全摘+両側付属器切除術"],
            "卵巣腫瘍摘出": ["卵巣摘出術", "付属器切除術", "腫瘍摘出術", "卵巣腫瘍切除術"],
            "広汎子宮全摘": ["広汎性子宮全摘術", "広汎子宮全摘出術", "拡大子宮全摘術"]
        }

        # 化学療法レジメンとその表記揺れ
        self.chemo_regimens = {
            "TC療法": ["TC", "パクリタキセル+カルボプラチン", "PTX+CBDCA"],
            "weekly PTX": ["毎週パクリタキセル", "weekly パクリタキセル", "wPTX"],
            "DC療法": ["DC", "ドセタキセル+カルボプラチン", "DTX+CBDCA"]
        }

        # 特記事項のパターン
        self.special_notes = [
            "抗凝固薬（{drug}）服用中",
            "心機能低下（EF {ef}%）あり",
            "糖尿病（HbA1c {hba1c}%）あり",
            "腎機能低下（Cr {cr} mg/dl）",
            "高度肥満（BMI {bmi}）"
        ]

    def _generate_date_sequence(self, start_date, num_records):
        """日付シーケンスを生成"""
        dates = []
        current_date = start_date
        for _ in range(num_records):
            dates.append(current_date)
            current_date += timedelta(days=random.randint(7, 30))
        return dates

    def _get_random_variant(self, base_term, variants):
        """基本用語とその表記揺れからランダムに選択"""
        all_variants = [base_term] + variants
        return random.choice(all_variants)

    def _generate_special_note(self):
        """特記事項をランダムに生成"""
        template = random.choice(self.special_notes)
        if "drug" in template:
            drugs = ["ワーファリン", "イグザレルト", "エリキュース", "プラザキサ"]
            return template.format(drug=random.choice(drugs))
        elif "ef" in template:
            return template.format(ef=random.randint(30, 55))
        elif "hba1c" in template:
            return template.format(hba1c=round(random.uniform(6.5, 10.0), 1))
        elif "cr" in template:
            return template.format(cr=round(random.uniform(1.5, 3.0), 1))
        elif "bmi" in template:
            return template.format(bmi=round(random.uniform(30, 40), 1))

    def generate_patient_records(self, num_patients=50):
        """患者記録を生成"""
        records = []
        start_date = datetime(2023, 1, 1)

        for patient_id in range(1, num_patients + 1):
            # 各患者の記録数をランダムに決定
            num_records = random.randint(3, 7)
            dates = self._generate_date_sequence(start_date, num_records)
            
            # がんの種類をランダムに選択
            cancer_type = random.choice(list(self.cancer_types.keys()))
            cancer_variant = self._get_random_variant(cancer_type, self.cancer_types[cancer_type])
            
            # ステージ情報の生成
            stage = random.choice(["I", "II", "III", "IV"])
            sub_stage = random.choice(["A", "B", "C"])
            stage_text = f"Stage {stage}{sub_stage}"

            # 記録を生成
            for i, date in enumerate(dates):
                text = ""
                if i == 0:
                    # 初診時
                    test = self._get_random_variant("組織診", self.diagnostic_tests["組織診"])
                    text = f"{test}の結果、{cancer_variant}、{stage_text}と診断。"
                    if random.random() < 0.3:
                        text += f" {self._generate_special_note()}"
                
                elif i == 1:
                    # 治療方針
                    surgery = self._get_random_variant("子宮全摘", self.surgery_types["子宮全摘"])
                    approach = random.choice(["開腹", "腹腔鏡下"])
                    text = f"治療方針：{approach}{surgery}の方針。"
                    if random.random() < 0.3:
                        text += f" {self._generate_special_note()}"

                elif i == 2:
                    # 手術記録
                    surgery = self._get_random_variant("子宮全摘", self.surgery_types["子宮全摘"])
                    approach = random.choice(["開腹", "腹腔鏡下"])
                    blood_loss = random.randint(50, 1000)
                    duration = random.randint(120, 360)
                    text = f"手術記録：{approach}{surgery}施行。手術時間{duration}分、出血量{blood_loss}ml。"

                else:
                    # 術後経過
                    chemo = random.choice(list(self.chemo_regimens.keys()))
                    chemo_variant = self._get_random_variant(chemo, self.chemo_regimens[chemo])
                    text = f"術後化学療法として{chemo_variant}を開始。"
                    if random.random() < 0.3:
                        text += f" {self._generate_special_note()}"

                records.append({
                    "ID": patient_id,
                    "day": date.strftime("%Y-%m-%d"),
                    "text": text
                })

        return pd.DataFrame(records)

    def save_to_excel(self, filename="sample_data.xlsx", num_patients=50):
        """生成したデータをExcelファイルに保存"""
        df = self.generate_patient_records(num_patients)
        df.to_excel(filename, index=False)
        print(f"{len(df)}件のダミーデータを{filename}に保存しました") 