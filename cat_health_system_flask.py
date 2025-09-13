from datetime import datetime

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
import os
import json
import warnings

warnings.filterwarnings('ignore')

class CatHealthSystem:
    """猫咪健康系统核心类"""

    def __init__(self):
        self.data_dir = "cat_data"
        self.ensure_directories()
        self.load_disease_models()
        
    def ensure_directories(self):
        """确保必要的目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "profiles"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "records"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "avatars"), exist_ok=True)
        
    def load_disease_models(self):
        """加载疾病检测模型"""
        try:
            # 加载训练数据
            self.ckd_data = pd.read_csv('ckd.csv')
            self.normal_data = pd.read_csv('normal.csv')
            self.pancreatitis_data = pd.read_csv('pancreatitis.csv')
            self.parasite_data = pd.read_csv('parasite.csv')
            
            # 准备训练数据
            self.prepare_training_data()
            
        except Exception as e:
            print(f"加载疾病数据失败: {str(e)}")
            
    def prepare_training_data(self):
        """准备训练数据"""
        # 合并所有数据
        ckd_features = self.extract_features(self.ckd_data, 'CKD')
        normal_features = self.extract_features(self.normal_data, 'Normal')
        pancreatitis_features = self.extract_features(self.pancreatitis_data, 'Pancreatitis')
        parasite_features = self.extract_features(self.parasite_data, 'Parasite')
        
        # 合并特征
        all_features = pd.concat(
            [ckd_features, normal_features, pancreatitis_features, parasite_features],
            ignore_index=True
        )
        
        # 准备训练数据
        X = all_features.drop(['disease'], axis=1)
        y = all_features['disease']
        
        # 标准化
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        
        # 训练模型
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        self.feature_columns = X.columns.tolist()
        
    def extract_features(self, df, disease_label):
        """从原始数据中提取特征"""
        features = []
        
        for cat_id in df['CatID'].unique():
            cat_data = df[df['CatID'] == cat_id].copy()
            
            # 计算统计特征
            feature_dict = {
                'avg_water': cat_data['Water(ml)'].mean(),
                'avg_food': cat_data['Food(g)'].mean(),
                'avg_urination': cat_data['Urination'].mean(),
                'avg_defecation': cat_data['Defecation'].mean(),
                'avg_vomiting': cat_data['Vomiting'].mean(),
                'avg_diarrhea': cat_data['Diarrhea'].mean(),
                'avg_weight': cat_data['Weight(kg)'].mean(),
                'std_water': cat_data['Water(ml)'].std(),
                'std_food': cat_data['Food(g)'].std(),
                'weight_change': (
                    cat_data['Weight(kg)'].iloc[-1] - 
                    cat_data['Weight(kg)'].iloc[0]
                ),
                'disease': disease_label
            }
            features.append(feature_dict)
            
        return pd.DataFrame(features)
    
    def predict_disease_risk(self, cat_data):
        """预测疾病风险"""
        if cat_data.empty:
            return {}
            
        # 计算特征
        features = {
            'avg_water': cat_data['Water(ml)'].mean(),
            'avg_food': cat_data['Food(g)'].mean(),
            'avg_urination': cat_data['Urination'].mean(),
            'avg_defecation': cat_data['Defecation'].mean(),
            'avg_vomiting': cat_data['Vomiting'].mean(),
            'avg_diarrhea': cat_data['Diarrhea'].mean(),
            'avg_weight': cat_data['Weight(kg)'].mean(),
            'std_water': cat_data['Water(ml)'].std(),
            'std_food': cat_data['Food(g)'].std(),
            'weight_change': (
                    cat_data['Weight(kg)'].iloc[-1] - 
                    cat_data['Weight(kg)'].iloc[0]
                ) if len(cat_data) > 1 else 0
        }
        
        # 准备预测数据
        X_pred = pd.DataFrame([features])[self.feature_columns]
        X_pred_scaled = self.scaler.transform(X_pred)
        
        # 获取预测概率
        probabilities = self.model.predict_proba(X_pred_scaled)[0]
        
        # 疾病名称映射
        disease_names = {
            'CKD': '慢性肾病',
            'Normal': '正常',
            'Pancreatitis': '猫胰腺炎',
            'Parasite': '猫肠道寄生虫感染'
        }
        
        # 计算风险概率（排除正常情况）
        risk_probabilities = {}
        for i, prob in enumerate(probabilities):
            disease_name = self.model.classes_[i]
            if disease_name != 'Normal':
                chinese_name = disease_names.get(disease_name, disease_name)
                risk_probabilities[chinese_name] = float(prob * 100)
        
        return risk_probabilities
    
    def save_cat_profile(self, cat_name, avatar_path=None):
        """保存猫咪档案"""
        profile = {
            'name': cat_name,
            'created_date': datetime.now().isoformat(),
            'avatar_path': avatar_path if avatar_path else None
        }
        
        profile_path = os.path.join(
            self.data_dir, "profiles", f"{cat_name}.json"
        )
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=2)
    
    def load_cat_profiles(self):
        """加载所有猫咪档案"""
        profiles = []
        profiles_dir = os.path.join(self.data_dir, "profiles")
        
        if os.path.exists(profiles_dir):
            for filename in os.listdir(profiles_dir):
                if filename.endswith('.json'):
                    with open(os.path.join(profiles_dir, filename), 'r', encoding='utf-8') as f:
                        profile = json.load(f)
                        profiles.append(profile)
        
        return profiles
    
    def save_cat_data(self, cat_name, data_df):
        """保存猫咪数据"""
        data_path = os.path.join(self.data_dir, "records", f"{cat_name}.csv")
        data_df.to_csv(data_path, index=False)
    
    def load_cat_data(self, cat_name):
        """加载猫咪数据"""
        data_path = os.path.join(self.data_dir, "records", f"{cat_name}.csv")
        if os.path.exists(data_path):
            try:
                # 检查文件是否为空
                if os.path.getsize(data_path) == 0:
                    return pd.DataFrame()
                
                # 尝试读取CSV文件
                df = pd.read_csv(data_path)
                # 检查是否有列数据
                if df.empty or len(df.columns) == 0:
                    return pd.DataFrame()
                return df
            except (pd.errors.EmptyDataError, pd.errors.ParserError):
                # 处理空文件或格式错误
                return pd.DataFrame()
        return pd.DataFrame()
    
    def save_detection_record(self, cat_name, risk_results):
        """保存检测记录"""
        record = {
            'date': datetime.now().isoformat(),
            'cat_name': cat_name,
            'risk_results': risk_results
        }
        
        records_path = os.path.join(
            self.data_dir, "detection_records.json"
        )
        
        # 加载现有记录
        if os.path.exists(records_path):
            with open(records_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
        else:
            records = []
        
        # 添加新记录
        records.append(record)
        
        # 保存记录
        with open(records_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
    
    def load_detection_records(self, cat_name):
        """加载检测记录"""
        records_path = os.path.join(self.data_dir, "detection_records.json")
        
        if not os.path.exists(records_path):
            return []
        
        with open(records_path, 'r', encoding='utf-8') as f:
            all_records = json.load(f)
        
        # 过滤特定猫咪的记录
        cat_records = [r for r in all_records if r['cat_name'] == cat_name]
        return cat_records
    
    def clear_detection_records(self, cat_name):
        """清空检测记录"""
        records_path = os.path.join(self.data_dir, "detection_records.json")
        
        if os.path.exists(records_path):
            with open(records_path, 'r', encoding='utf-8') as f:
                records = json.load(f)
            
            # 移除该猫咪的记录
            records = [r for r in records if r['cat_name'] != cat_name]
            
            with open(records_path, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
    
    def delete_cat(self, cat_name):
        """删除猫咪档案"""
        # 删除档案
        profile_path = os.path.join(self.data_dir, "profiles", f"{cat_name}.json")
        if os.path.exists(profile_path):
            os.remove(profile_path)
        
        # 删除数据
        data_path = os.path.join(self.data_dir, "records", f"{cat_name}.csv")
        if os.path.exists(data_path):
            os.remove(data_path)
        
        # 清空检测记录
        self.clear_detection_records(cat_name)