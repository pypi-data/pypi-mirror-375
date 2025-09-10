
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, model_validator
from stkweight.core import plot_weight_candlestick_daily_full_range_with_volume
from fastapi import FastAPI, UploadFile, File, HTTPException, Response
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.responses import HTMLResponse
from typing import List, Optional
import pandas as pd
import io
import os


# TODO ADD
app = FastAPI(
    title="LLM Service",
    description="Provides an OpenAI-compatible API for custom large language models.",
    version="1.0.1",
)

# --- Configure CORS ---
# ! Add this section !
# Define allowed origins. Be specific in production!
# Example: origins = ["http://localhost:3000", "https://your-frontend-domain.com"]
origins = [
    "*", # Allows all origins (convenient for development, insecure for production)
    # Add the specific origin of your "别的调度" tool/frontend if known
    # e.g., "http://localhost:5173" for a typical Vite frontend dev server
    # e.g., "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Specifies the allowed origins
    allow_credentials=True, # Allows cookies/authorization headers
    allow_methods=["*"],    # Allows all methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],    # Allows all headers (Content-Type, Authorization, etc.)
)
# --- End CORS Configuration ---




@app.get("/")
async def root():
    """ x """
    return {"message": "LLM Service is running."}


@app.post("/upload_csv/", summary="Upload a single CSV file")
async def upload_csv(file: UploadFile = File(..., description="The CSV file to upload.")):
    """
    Uploads a single CSV file, processes it using pandas,
    and returns a confirmation message with the number of rows.

    - **file**: The uploaded CSV file.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files (.csv) are allowed!")

    try:
        # 读取上传的文件内容
        contents = await file.read()
        
        # 将二进制内容解码为文本，通常使用 'utf-8'，
        # 如果遇到中文乱码问题，可以尝试 'gbk' 或 'latin-1'
        csv_data = io.StringIO(contents.decode('utf-8'))
        
        # 使用 pandas 读取 CSV
        df = pd.read_csv(csv_data,index_col=0)
        df.columns = [i.strip() for i in df.columns]
        
        # 打印 DataFrame 的前几行，或进行其他处理（例如保存到数据库）
        print(f"Received CSV file: {file.filename}")
        print("DataFrame head:")
        print(df.head())
        
        ma_config_daily = [
        {'period': 5, 'price_col': 'EveningWeight', 'color': 'blue'},
        {'period': 10, 'price_col': 'MorningWeight', 'color': 'purple'}
        ]
        files = "tests/resources/temp_analyse.html"
        plot_weight_candlestick_daily_full_range_with_volume(df, ma_configs=ma_config_daily, 
                                                             show_calorie_volume=True,
                                                             show = False,
                                                             file_path = files)
        

        return {
            "filename": file.filename,
            "message": "CSV uploaded and processed successfully!",
            "rows_count": len(df),
            "columns": list(df.columns)
        }
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=422, detail="Could not decode CSV file. Please ensure it's UTF-8 encoded or try another encoding.")
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="Uploaded CSV file is empty.")
    except Exception as e:
        # 更具体的异常处理，例如文件格式不正确
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {e}")


@app.get("/get_analyse/", summary="get analyse html")
async def get_analyse():

    files = "tests/resources/temp_analyse.html"
    with open(files,'r') as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == "__main__":
    # 这是一个标准的 Python 入口点惯用法
    # 当脚本直接运行时 (__name__ == "__main__")，这里的代码会被执行
    # 当通过 python -m YourPackageName 执行 __main__.py 时，__name__ 也是 "__main__"
    import argparse
    import uvicorn
    from .log import Log
    
    
    default=8008
    

    parser = argparse.ArgumentParser(
        description="Start a simple HTTP server similar to http.server."
    )
    parser.add_argument(
        'port',
        metavar='PORT',
        type=int,
        nargs='?', # 端口是可选的
        default=default,
        help=f'Specify alternate port [default: {default}]'
    )
    # 创建一个互斥组用于环境选择
    group = parser.add_mutually_exclusive_group()

    # 添加 --dev 选项
    group.add_argument(
        '--dev',
        action='store_true', # 当存在 --dev 时，该值为 True
        help='Run in development mode (default).'
    )

    # 添加 --prod 选项
    group.add_argument(
        '--prod',
        action='store_true', # 当存在 --prod 时，该值为 True
        help='Run in production mode.'
    )
    args = parser.parse_args()

    if args.prod:
        env = "prod"
    else:
        # 如果 --prod 不存在，默认就是 dev
        env = "dev"

    port = args.port
    if env == "dev":
        port += 100
        Log.reset_level('debug',env = env)
        reload = True
        app_import_string = f"{__package__}.server:app" # <--- 关键修改：传递导入字符串
    elif env == "prod":
        Log.reset_level('info',env = env)# ['debug', 'info', 'warning', 'error', 'critical']
        reload = False
        app_import_string = app
    else:
        reload = False
        app_import_string = app
    

    # 使用 uvicorn.run() 来启动服务器
    # 参数对应于命令行选项
    uvicorn.run(
        app_import_string,
        host="0.0.0.0",
        port=port,
        reload=reload  # 启用热重载
    )
