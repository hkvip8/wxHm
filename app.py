import os
import time
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from PIL import Image

app = Flask(__name__)
app.secret_key = 'wxHm_secure_key_2026' # 建议生产环境修改此密钥

# --- 配置中心 ---
UPLOAD_BASE = 'uploads'
ADMIN_PASSWORD = 'admin123'  # 管理后台密码
EXPIRE_DAYS = 7             # 微信群码有效天数

# 确保上传根目录存在
if not os.path.exists(UPLOAD_BASE):
    os.makedirs(UPLOAD_BASE)

def get_active_qr(group_name):
    """
    获取指定群组下最新且未过期的二维码
    同时执行过期物理文件的清理
    """
    group_path = os.path.join(UPLOAD_BASE, group_name)
    if not os.path.exists(group_path):
        return None
    
    # 筛选支持的图片格式
    files = [f for f in os.listdir(group_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not files:
        return None
    
    # 按修改时间从新到旧排序
    files.sort(key=lambda x: os.path.getmtime(os.path.join(group_path, x)), reverse=True)
    
    now = time.time()
    active_file = None
    
    for filename in files:
        path = os.path.join(group_path, filename)
        file_age_days = (now - os.path.getmtime(path)) / (24 * 3600)
        
        if file_age_days < EXPIRE_DAYS:
            # 找到第一个（也就是最新的）有效文件
            if not active_file:
                active_file = filename
        else:
            # 自动清理物理磁盘上的过期文件
            try:
                os.remove(path)
            except Exception as e:
                print(f"清理文件失败: {e}")
                
    return active_file

# --- 用户端路由 ---
@app.route('/group/<group_name>')
def group_page(group_name):
    qr_file = get_active_qr(group_name)
    timestamp = int(time.time() * 1000)
    return render_template('index.html', group_name=group_name, qr_file=qr_file, timestamp=timestamp)

# --- 管理端：主界面与上传 ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # 获取所有群组文件夹列表
    existing_groups = [d for d in os.listdir(UPLOAD_BASE) if os.path.isdir(os.path.join(UPLOAD_BASE, d))]
    existing_groups.sort() # 字母排序
    
    if request.method == 'POST':
        pwd = request.form.get('password')
        group_input = request.form.get('group_name', '').strip()
        file = request.files.get('file')
        
        # 1. 验证密码
        if pwd != ADMIN_PASSWORD:
            flash("密码验证失败，请重新输入！")
            return redirect(url_for('admin'))
        
        # 2. 处理上传
        if group_input and file:
            group_dir = os.path.join(UPLOAD_BASE, group_input)
            if not os.path.exists(group_dir):
                os.makedirs(group_dir)
            
            try:
                # 使用 Pillow 处理图片并转为 WebP
                img = Image.open(file)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                new_filename = f"qr_{int(time.time())}.webp"
                save_path = os.path.join(group_dir, new_filename)
                
                # 转换并保存
                img.save(save_path, "WEBP", quality=80)
                flash(f"成功：群组【{group_input}】已更新，图片已自动优化为 WebP。")
            except Exception as e:
                flash(f"错误：图片转换失败 - {str(e)}")
            
            return redirect(url_for('admin'))
            
    return render_template('admin.html', groups=existing_groups)

# --- 管理端：删除群组 ---
@app.route('/admin/delete/<group_name>', methods=['POST'])
def delete_group(group_name):
    pwd = request.form.get('password')
    if pwd != ADMIN_PASSWORD:
        flash("权限不足：密码错误")
        return redirect(url_for('admin'))
    
    group_path = os.path.join(UPLOAD_BASE, group_name)
    if os.path.exists(group_path):
        shutil.rmtree(group_path)
        flash(f"群组【{group_name}】及其所有内容已物理删除。")
    return redirect(url_for('admin'))

# --- 管理端：重命名群组 ---
@app.route('/admin/rename', methods=['POST'])
def rename_group():
    pwd = request.form.get('password')
    old_name = request.form.get('old_name')
    new_name = request.form.get('new_name', '').strip()
    
    if pwd != ADMIN_PASSWORD:
        flash("权限不足：密码错误")
        return redirect(url_for('admin'))
    
    if old_name and new_name:
        old_path = os.path.join(UPLOAD_BASE, old_name)
        new_path = os.path.join(UPLOAD_BASE, new_name)
        
        if os.path.exists(new_path):
            flash("失败：新群组名称已存在。")
        elif os.path.exists(old_path):
            os.rename(old_path, new_path)
            flash(f"成功：已将【{old_name}】重命名为【{new_name}】。")
            
    return redirect(url_for('admin'))

# --- 静态资源服务 ---
@app.route('/uploads/<group_name>/<filename>')
def serve_qr(group_name, filename):
    return send_from_directory(os.path.join(UPLOAD_BASE, group_name), filename)

# --- 根目录跳转（可选） ---
@app.route('/')
def home():
    return "WeChat LiveCode System is Running. Please visit /admin to manage."

if __name__ == '__main__':
    # 建议生产环境使用 gunicorn 启动
    app.run(host='0.0.0.0', port=8092, debug=True)