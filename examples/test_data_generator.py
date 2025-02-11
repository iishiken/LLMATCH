# -*- coding: utf-8 -*-

from data.data_generator import MedicalDataGenerator

# ジェネレーターの初期化
generator = MedicalDataGenerator()

# 50人分のダミーデータを生成してExcelファイルに保存
generator.save_to_excel("sample_data.xlsx", num_patients=50) 