# wxHm (WeChat Group Live QR Code Manager)

**wxHm** 是一个轻量级、高性能的微信群活码管理系统。它解决了微信群二维码 7 天有效期限制的痛点，通过固定链接分发，后台动态更新二维码，并集成了 WebP 自动转换与全球 CDN 加速。

---

## ✨ 核心功能

* **多群组独立管理**：支持创建多个群组（如：技术群、福利群），每个群组拥有唯一的永久访问路径。
* **智能码源轮转**：自动识别群组目录下最新的二维码，无需手动删除旧码即可完成更新。
* **WebP 自动优化**：后端自动将上传的 JPG/PNG 图片转为 WebP 格式，大幅缩减文件体积。
* **全球 CDN 加速**：集成 `wsrv.nl` 图像处理引擎，支持分布式节点缓存与快速分发。
* **自动化清理机制**：系统自动扫描并物理删除超过 7 天的陈旧图片，保持服务器整洁。
* **3天免密管理**：管理员登录后密码自动在本地加密缓存 3 天，提升移动端维护体验。
* **动态视觉引导**：前端页面内置绿色扫描线动画，深度适配微信用户长按识别习惯。
* **强制去缓存策略**：URL 附加随机时间戳，彻底穿透微信内置浏览器的强缓存。

---

## 📅 变更记录 (Changelog)

### v1.2.0 (2026-01-07) - 当前版本

* **[Feature]** 引入 `wsrv.nl` CDN 图片处理，支持全球加速。
* **[Feature]** 强制 `base_url` 走 HTTPS 协议，适配 Cloudflare 生产环境。
* **[Fix]** 解决 `strict-origin-when-cross-origin` 导致的跨域加载问题。
* **[Fix]** 适配 `ProxyFix` 确保在 Nginx/CF 反代下能正确识别 Host。

### v1.1.0

* **[Feature]** 增加群组“重命名”与“一键删除”功能。
* **[Feature]** 实现管理员密码本地缓存 3 天逻辑。
* **[Optimization]** 增加 Pillow 库支持，实现上传自动转 WebP。

### v1.0.0

* **[Base]** 基础 Flask 架构发布，支持单群组活码展示与上传。

---

## 📂 项目结构

```text
wxHm/
├── app.py                # 后端核心逻辑 (Flask)
├── uploads/              # 二维码存储目录 (按群组划分)
├── templates/
│   ├── index.html        # 用户扫码展示页
│   └── admin.html        # 管理后台页
├── start.sh              # Linux 后台启动脚本
├── requirements.txt      # 依赖库清单
└── .gitignore            # Git 忽略配置

```

---

## 🚀 快速开始

### 1. 环境准备

```bash
git clone https://github.com/cooker/wxHm.git
cd wxHm
pip install -r requirements.txt

```

### 2. 配置修改

打开 `app.py`，修改 `ADMIN_PASSWORD` 为你的管理密码。

### 3. 一键启动

```bash
# Linux
chmod +x start.sh && ./start.sh

# Windows
python app.py

```

---

## 🛠️ 生产环境建议 (Cloudflare/Nginx)

1. **关闭 Hotlink Protection**：在 Cloudflare 的 Scrape Shield 中关闭防盗链，否则 CDN 无法抓取图片。
2. **HTTPS 强制**：在 Cloudflare 中开启 "Always Use HTTPS"。
3. **Referrer 策略**：本项目已内置 `no-referrer-when-downgrade`，以确保跨域抓取成功。

---

## 📜 许可证

本项目采用 [MIT License](https://www.google.com/search?q=LICENSE) 开源。

---

**项目地址**: [https://github.com/cooker/wxHm](https://github.com/cooker/wxHm)

如果你觉得这个项目有帮助，请给一个 **Star ⭐️**！
![](zsm.jpg)
---
