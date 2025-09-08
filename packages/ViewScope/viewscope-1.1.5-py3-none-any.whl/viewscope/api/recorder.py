"""
操作录制API路由
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..core.action_recorder import get_action_recorder, ActionRecorder

router = APIRouter()


class RecordingStartRequest(BaseModel):
    device_id: Optional[str] = None


class RecordingResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class ScriptGenerationRequest(BaseModel):
    script_type: str = "uiautomator2"


def get_recorder() -> ActionRecorder:
    """依赖注入：获取录制器实例"""
    return get_action_recorder()


@router.post("/recording/start", response_model=RecordingResponse)
async def start_recording(request: RecordingStartRequest, recorder=Depends(get_recorder)):
    """开始录制操作"""
    try:
        result = recorder.start_recording(request.device_id)
        
        return RecordingResponse(
            success=result["success"],
            message=result["message"],
            data={
                "session_id": result.get("session_id"),
                "start_time": result.get("start_time")
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"开始录制失败: {str(e)}"
        )


@router.post("/recording/stop", response_model=RecordingResponse)
async def stop_recording(recorder=Depends(get_recorder)):
    """停止录制操作"""
    try:
        result = recorder.stop_recording()
        
        return RecordingResponse(
            success=result["success"],
            message=result["message"],
            data={
                "session_id": result.get("session_id"),
                "action_count": result.get("action_count"),
                "duration": result.get("duration")
            }
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"停止录制失败: {str(e)}"
        )


@router.get("/recording/status", response_model=RecordingResponse)
async def get_recording_status(recorder=Depends(get_recorder)):
    """获取录制状态"""
    try:
        status_info = recorder.get_current_session_info()
        
        return RecordingResponse(
            success=True,
            message="获取状态成功",
            data=status_info
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取录制状态失败: {str(e)}"
        )


@router.post("/recording/generate_script")
async def generate_script(request: ScriptGenerationRequest, recorder=Depends(get_recorder)):
    """生成自动化脚本"""
    try:
        if not recorder.actions:
            return {
                "success": False,
                "message": "没有录制的操作可以生成脚本"
            }
        
        script_content = recorder.generate_script(request.script_type)
        session_info = recorder.get_current_session_info()
        
        return {
            "success": True,
            "message": f"脚本生成成功，共包含 {len(recorder.actions)} 个操作",
            "script_content": script_content,
            "script_type": request.script_type,
            "session_info": session_info
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"生成脚本失败: {str(e)}"
        )


@router.get("/recording/export_session")
async def export_session_data(recorder=Depends(get_recorder)):
    """导出录制会话数据"""
    try:
        session_data = recorder.export_session_data()
        
        return {
            "success": True,
            "message": "会话数据导出成功",
            "session_data": session_data
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导出会话数据失败: {str(e)}"
        )


@router.post("/recording/import_session")
async def import_session_data(session_data: Dict[str, Any], recorder=Depends(get_recorder)):
    """导入录制会话数据"""
    try:
        success = recorder.import_session_data(session_data)
        
        if success:
            return {
                "success": True,
                "message": "会话数据导入成功",
                "action_count": len(recorder.actions)
            }
        else:
            return {
                "success": False,
                "message": "会话数据导入失败"
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"导入会话数据失败: {str(e)}"
        )