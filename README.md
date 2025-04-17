├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── file_indexer.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── main.js
│   │   ├── preload.js
│   │   ├── renderer/
│   │   │   ├── App.vue
│   │   │   └── components/
│   │   │       └── TimelineChart.vue
│   │   └── index.html
│   └── package.json
├── run.bat
└── README.md

1. 安装依赖
# 后端
pip install -r requirements.txt

# 前端
cd frontend
npm install

2. 开发模式运行
# 启动后端
uvicorn backend.main:app --reload

# 启动前端
cd frontend
npm run start

3. 生产打包
cd frontend
npm run build
electron-builder -mwl

4. 生成发布exe构建和发布步骤
安装打包工具
pip install pyinstaller
打包为独立EXE
pyinstaller build.spec --onefile --noconsole
生成安装包 创建 installer.nsi (NullSoft Installer脚本):
生成最终安装包
makensis installer.nsi

发布文件结构
conmod-se-tools/
├── LogAnalyzer.exe        # 主程序
├── backend/               # 后端文件
├── frontend/              # 前端文件
├── vcruntime140.dll       # 必要运行时
└── uninstall.exe          # 卸载程序