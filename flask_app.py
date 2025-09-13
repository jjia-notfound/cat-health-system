from flask import (
    Flask, render_template, request, redirect,
    url_for, jsonify, send_file
)
from werkzeug.utils import secure_filename
import pandas as pd
import os
from datetime import datetime
from cat_health_system_flask import CatHealthSystem

app = Flask(__name__)
app.secret_key = 'cat-health-system-2025'

# 配置
UPLOAD_FOLDER = 'cat_data/uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB限制

# 确保目录存在
os.makedirs('cat_data/profiles', exist_ok=True)
os.makedirs('cat_data/records', exist_ok=True)
os.makedirs('cat_data/avatars', exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 初始化系统
health_system = CatHealthSystem()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """主页"""
    profiles = health_system.load_cat_profiles()
    total_records = 0
    for profile in profiles:
        cat_data = health_system.load_cat_data(profile['name'])
        if not cat_data.empty:
            total_records += len(cat_data)
    
    return render_template('index.html', 
                         cats=profiles, 
                         total_cats=len(profiles),
                         total_records=total_records)

@app.route('/create_cat', methods=['GET', 'POST'])
def create_cat():
    """创建猫咪"""
    if request.method == 'POST':
        cat_name = request.form['cat_name'].strip()
        if cat_name:
            # 处理头像上传
            avatar_path = None
            if 'avatar' in request.files:
                file = request.files['avatar']
                if file and file.filename != '':
                    filename = secure_filename(file.filename)
                    avatar_path = os.path.join('cat_data/avatars', f"{cat_name}_{filename}")
                    file.save(avatar_path)
            
            health_system.save_cat_profile(cat_name, avatar_path)
            return redirect(url_for('cat_detail', cat_name=cat_name))
    
    return render_template('create_cat.html')

@app.route('/cat/<cat_name>')
def cat_detail(cat_name):
    """猫咪详情页"""
    cat_data = health_system.load_cat_data(cat_name)
    profiles = health_system.load_cat_profiles()
    profile = next((p for p in profiles if p['name'] == cat_name), None)
    
    return render_template('cat_detail.html', 
                         cat_name=cat_name, 
                         cat_data=cat_data,
                         profile=profile)

@app.route('/upload_data/<cat_name>', methods=['GET', 'POST'])
def upload_data(cat_name):
    """上传数据"""
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], filename
                )
                file.save(file_path)
                
                # 读取CSV数据
                data_df = pd.read_csv(file_path)
                health_system.save_cat_data(cat_name, data_df)
                
                return redirect(url_for('cat_detail', cat_name=cat_name))
        
        # 处理手动输入的数据
        data = {
            'Date': [request.form['date']],
            'Water(ml)': [float(request.form['water'])],
            'Food(g)': [float(request.form['food'])],
            'Urination': [int(request.form['urination'])],
            'Defecation': [int(request.form['defecation'])],
            'Vomiting': [int(request.form['vomiting'])],
            'Diarrhea': [int(request.form['diarrhea'])],
            'Weight(kg)': [float(request.form['weight'])],
            'CatID': [cat_name]
        }
        
        new_data = pd.DataFrame(data)
        
        # 合并现有数据
        existing_data = health_system.load_cat_data(cat_name)
        if not existing_data.empty:
            combined_data = pd.concat(
                [existing_data, new_data], 
                ignore_index=True
            )
        else:
            combined_data = new_data
            
        health_system.save_cat_data(cat_name, combined_data)
        return redirect(url_for('cat_detail', cat_name=cat_name))
    
    return render_template('upload_data.html', cat_name=cat_name)

@app.route('/add_record/<cat_name>', methods=['POST'])
def add_record(cat_name):
    """手动添加记录"""
    try:
        data = request.json
        new_record = pd.DataFrame([{
            'Date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
            'Water(ml)': float(data['water']),
            'Food(g)': float(data['food']),
            'Urination': int(data['urination']),
            'Defecation': int(data['defecation']),
            'Vomiting': int(data['vomiting']),
            'Diarrhea': int(data['diarrhea']),
            'Weight(kg)': float(data['weight'])
        }])
        
        existing_data = health_system.load_cat_data(cat_name)
        if existing_data.empty:
            combined_data = new_record
        else:
            combined_data = pd.concat([existing_data, new_record], ignore_index=True)
        
        health_system.save_cat_data(cat_name, combined_data)
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/delete_data/<cat_name>', methods=['POST'])
def delete_data(cat_name):
    """删除数据"""
    try:
        health_system.save_cat_data(cat_name, pd.DataFrame())
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/detect/<cat_name>')
def detect_disease(cat_name):
    """疾病检测"""
    cat_data = health_system.load_cat_data(cat_name)
    
    if cat_data.empty:
        return render_template('detect_result.html', 
                             cat_name=cat_name, 
                             error='暂无数据记录')
    
    risk_results = health_system.predict_disease_risk(cat_data)
    health_system.save_detection_record(cat_name, risk_results)
    return render_template('detect_result.html', 
                         cat_name=cat_name, 
                         risk_results=risk_results)

@app.route('/records/<cat_name>')
def view_records(cat_name):
    """查看检测记录"""
    records = health_system.load_detection_records(cat_name)
    cat_data = health_system.load_cat_data(cat_name)
    return render_template('records.html', 
                         cat_name=cat_name, 
                         records=records,
                         data=cat_data)

@app.route('/delete_cat/<cat_name>', methods=['POST'])
def delete_cat(cat_name):
    """删除猫咪"""
    try:
        health_system.delete_cat(cat_name)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/export/<cat_name>')
def export_data(cat_name):
    """导出数据"""
    cat_data = health_system.load_cat_data(cat_name)
    if cat_data.empty:
        return "暂无数据"
    
    output = io.BytesIO()
    cat_data.to_csv(output, index=False)
    output.seek(0)
    
    return send_file(
        io.BytesIO(output.getvalue()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{cat_name}_data.csv'
    )

if __name__ == '__main__':
    import socket
    import sys
    
    def find_free_port(start_port=8000):
        """查找可用端口"""
        port = start_port
        while True:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('0.0.0.0', port))
                    return port
            except OSError:
                port += 1
                if port > 9000:  # 设置上限避免无限循环
                    raise RuntimeError("无法找到可用端口")
    
    # 只在第一次启动时检测端口
    if 'port' not in locals():
        port = find_free_port(8000)
        print(f"🚀 应用启动成功！")
        print(f"📱 访问地址：http://localhost:{port}")
        print(f"🌐 网络地址：http://0.0.0.0:{port}")
        print(f"⚡ 按 Ctrl+C 停止服务")
        print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)