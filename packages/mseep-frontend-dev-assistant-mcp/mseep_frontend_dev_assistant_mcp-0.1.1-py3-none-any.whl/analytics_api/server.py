"""
MCP Analytics API Server
简化版数据收集API
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from .models import UserRegister, UsageLog, ApiResponse
from .mcp_data_service import MCPDataService

app = FastAPI(
    title="MCP Analytics API",
    description="MCP工具使用数据收集和分析API",
    version="2.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局数据服务实例
data_service: Optional[MCPDataService] = None

async def get_data_service() -> MCPDataService:
    """获取数据服务实例"""
    global data_service
    if data_service is None:
        data_service = MCPDataService()
        await data_service.init_service()
    return data_service

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    print("🚀 MCP Analytics API 启动中...")
    try:
        await get_data_service()
        print("✅ 数据服务初始化完成")
    except Exception as e:
        print(f"❌ 数据服务初始化失败: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    global data_service
    if data_service:
        await data_service.close()
    print("📴 MCP Analytics API 已关闭")

@app.get("/", response_model=ApiResponse)
async def root():
    """API根路径"""
    return ApiResponse(
        status="success",
        message="MCP Analytics API v2.0 - 数据收集服务",
        data={
            "version": "2.0.0",
            "service": "mcp-analytics",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.get("/health")
async def health_check():
    """健康检查"""
    service = await get_data_service()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "connected"
    }

# 用户管理接口
@app.post("/api/users/register", response_model=ApiResponse)
async def register_user(
    user_data: UserRegister,
    service: MCPDataService = Depends(get_data_service)
):
    """注册用户"""
    try:
        result = await service.register_user(user_data.dict())
        return ApiResponse(
            status="success",
            message="用户注册成功",
            data=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MCP数据收集接口
@app.post("/api/mcp/record", response_model=ApiResponse)
async def record_mcp_call(
    usage_data: UsageLog,
    execution_time: Optional[float] = 0,
    success: Optional[bool] = True,
    error_message: Optional[str] = None,
    service: MCPDataService = Depends(get_data_service)
):
    """记录MCP工具调用"""
    try:
        result = await service.record_mcp_call(
            user_uuid=usage_data.user_uuid,
            tool_name=usage_data.tool_name,
            arguments=usage_data.arguments,
            execution_time=execution_time,
            success=success,
            error_message=error_message
        )
        
        return ApiResponse(
            status=result['status'],
            message=result['message'],
            data=result.get('data')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 分析报告接口
@app.get("/api/analytics/user/{user_uuid}", response_model=ApiResponse)
async def get_user_analytics(
    user_uuid: str,
    days: int = 30,
    service: MCPDataService = Depends(get_data_service)
):
    """获取用户分析报告"""
    try:
        analytics = await service.get_user_analytics(user_uuid, days)
        return ApiResponse(
            status="success",
            message="用户分析数据获取成功",
            data=analytics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics/team", response_model=ApiResponse)
async def get_team_analytics(
    department: Optional[str] = None,
    days: int = 30,
    service: MCPDataService = Depends(get_data_service)
):
    """获取团队分析报告"""
    try:
        analytics = await service.get_team_analytics(department, days)
        return ApiResponse(
            status="success",
            message="团队分析数据获取成功",
            data=analytics
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Git分析接口
@app.get("/api/git/status", response_model=ApiResponse)
async def get_git_status(
    service: MCPDataService = Depends(get_data_service)
):
    """获取当前git状态"""
    try:
        status = service.git_analyzer.get_status()
        repo_info = service.git_analyzer.get_repo_info()
        
        return ApiResponse(
            status="success",
            message="Git状态获取成功",
            data={
                "repository": repo_info,
                "status": status,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/git/commits", response_model=ApiResponse)
async def get_commit_history(
    days: int = 7,
    author: Optional[str] = None,
    service: MCPDataService = Depends(get_data_service)
):
    """获取提交历史"""
    try:
        commits = service.git_analyzer.get_commit_history(days, author)
        analysis = service.git_analyzer.analyze_commit_patterns(commits)
        
        return ApiResponse(
            status="success",
            message="提交历史获取成功",
            data={
                "commits": commits,
                "analysis": analysis,
                "period_days": days,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🔧 启动MCP Analytics API服务器...")
    uvicorn.run(
        "src.analytics_api.server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )