"""
UI分析器核心模块
负责UI层次结构解析和元素分析
"""

import asyncio
import base64
import io
import subprocess
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple
from PIL import Image

class UIAnalyzer:
    """UI分析器"""
    
    def __init__(self, device_manager):
        self.device_manager = device_manager
        
    async def capture_with_hierarchy(self, device_id: str) -> dict:
        """截图并获取UI层次结构"""
        device_manager = self.device_manager.get_device(device_id)
        if not device_manager:
            raise ValueError(f"设备 {device_id} 不存在")
        
        if not device_manager.is_connected:
            device_manager.connect()
        
        try:
            # 确保uiautomator2服务正常运行
            await self._ensure_device_ready(device_manager)
            
            # 获取截图
            screenshot_data = await self._take_screenshot(device_manager)
            
            # 获取UI层次结构
            hierarchy_data = await self._get_ui_hierarchy(device_manager)
            
            return {
                "success": True,
                "screenshot": screenshot_data,
                "hierarchy": hierarchy_data,
                "device_id": device_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "device_id": device_id
            }
    
    async def _ensure_device_ready(self, device_manager):
        """确保设备和uiautomator2服务准备就绪"""
        try:
            print("[FIX] 检查设备连接状态...")
            
            # 检查ADB连接
            if not device_manager.is_connected:
                print("[DEVICE]重新连接设备...")
                device_manager.connect()
            
            # 初始化或重启uiautomator2服务
            print("[FIX] 检查uiautomator2服务...")
            loop = asyncio.get_event_loop()
            
            # 尝试简单操作检查服务状态
            try:
                # 使用device.info获取设备信息来检查服务状态
                device_info = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: device_manager.device.info),
                    timeout=5.0
                )
                if device_info and 'display' in device_info:
                    print("[OK] uiautomator2服务正常")
                else:
                    raise Exception("服务响应异常")
            except (asyncio.TimeoutError, Exception) as e:
                print(f"[WARN]  uiautomator2服务异常: {e}")
                print("[PROC] 尝试重新连接设备...")
                
                try:
                    # 重新连接设备，让uiautomator2重新初始化
                    device_manager.disconnect()
                    await asyncio.sleep(2)  # 等待2秒
                    device_manager.connect()
                    print("[OK] 设备重新连接完成")
                except Exception as reconnect_error:
                    print(f"[WARN]  设备重新连接失败: {reconnect_error}")
                    # 继续尝试操作，可能服务仍然可用
            
        except Exception as e:
            print(f"[ERROR] 设备准备失败: {str(e)}")
            raise Exception(f"设备准备失败: {str(e)}")
    
    async def _take_screenshot(self, device_manager) -> str:
        """使用ADB获取设备截图"""
        return await self._adb_screenshot(device_manager)
    
    async def _adb_screenshot(self, device_manager) -> str:
        """使用ADB命令直接截图，避免uiautomator2超时问题"""
        try:
            device_id = device_manager.device_id
            print(f"[SCREENSHOT] 使用ADB截图: {device_id}")
            
            # 执行ADB截图命令
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, self._execute_adb_screencap, device_id),
                timeout=8.0  # 8秒超时
            )
            
            if result and len(result) > 0:
                # 转换为base64
                base64_str = base64.b64encode(result).decode('utf-8')
                print(f"[OK] ADB截图成功，大小: {len(base64_str)} 字符")
                return base64_str
            else:
                raise Exception("ADB截图返回空数据")
                
        except asyncio.TimeoutError:
            print(f"[ERROR] ADB截图超时 (8秒)")
            raise Exception("ADB截图超时，请检查设备连接")
        except Exception as e:
            print(f"[ERROR] ADB截图失败: {str(e)}")
            raise Exception(f"ADB截图失败: {str(e)}")
    
    def _execute_adb_screencap(self, device_id: str) -> bytes:
        """执行ADB截图命令"""
        try:
            result = subprocess.run([
                'adb', '-s', device_id, 'exec-out', 'screencap', '-p'
            ], capture_output=True, timeout=6)
            
            if result.returncode == 0 and result.stdout:
                print(f"[OK] ADB命令执行成功，截图大小: {len(result.stdout)} 字节")
                return result.stdout
            else:
                error_msg = result.stderr.decode('utf-8') if result.stderr else "未知错误"
                raise Exception(f"ADB截图命令失败: {error_msg}")
                
        except subprocess.TimeoutExpired:
            raise Exception("ADB截图命令超时")
        except Exception as e:
            raise Exception(f"执行ADB命令时错误: {str(e)}")
    
    async def _get_ui_hierarchy(self, device_manager) -> dict:
        """获取UI层次结构"""
        try:
            print(f"[TREE] 开始获取UI层次结构...")
            
            # 获取UI dump，设置超时
            loop = asyncio.get_event_loop()
            ui_xml = await asyncio.wait_for(
                loop.run_in_executor(None, device_manager.device.dump_hierarchy),
                timeout=15.0  # 15秒超时，UI dump通常比截图慢
            )
            print(f"[OK] UI dump获取成功，XML长度: {len(ui_xml)} 字符")
            
            # 解析XML
            if not ui_xml or ui_xml.strip() == "":
                raise Exception("UI dump返回空内容")
            
            root = ET.fromstring(ui_xml)
            print(f"[OK] XML解析成功，根节点: {root.tag}")
            
            # 转换为结构化数据
            hierarchy = self._parse_xml_node(root)
            print(f"[OK] UI层次结构转换成功")
            
            return hierarchy
            
        except asyncio.TimeoutError:
            print(f"[ERROR] UI层次结构获取超时 (15秒)")
            raise Exception("UI层次结构获取超时，请检查设备连接")
        except ET.ParseError as e:
            print(f"[ERROR] XML解析失败: {str(e)}")
            raise Exception(f"UI层次结构XML解析失败: {str(e)}")
        except Exception as e:
            print(f"[ERROR] 获取UI层次结构失败: {str(e)}")
            raise Exception(f"获取UI层次结构失败: {str(e)}")
    
    def _parse_xml_node(self, node: ET.Element) -> dict:
        """解析XML节点"""
        # 提取节点属性
        attrs = node.attrib
        
        # 解析边界坐标
        bounds = self._parse_bounds(attrs.get('bounds', ''))
        
        # 构建节点数据
        node_data = {
            'class': attrs.get('class', ''),
            'text': attrs.get('text', ''),
            'resource_id': attrs.get('resource-id', ''),
            'content_desc': attrs.get('content-desc', ''),
            'package': attrs.get('package', ''),
            'bounds': bounds,
            'checkable': attrs.get('checkable', 'false') == 'true',
            'checked': attrs.get('checked', 'false') == 'true',
            'clickable': attrs.get('clickable', 'false') == 'true',
            'enabled': attrs.get('enabled', 'true') == 'true',
            'focusable': attrs.get('focusable', 'false') == 'true',
            'focused': attrs.get('focused', 'false') == 'true',
            'scrollable': attrs.get('scrollable', 'false') == 'true',
            'long_clickable': attrs.get('long-clickable', 'false') == 'true',
            'password': attrs.get('password', 'false') == 'true',
            'selected': attrs.get('selected', 'false') == 'true',
            'displayed': attrs.get('displayed', 'true') == 'true',
            'index': int(attrs.get('index', '0')),
            'children': []
        }
        
        # 递归解析子节点
        for child in node:
            child_data = self._parse_xml_node(child)
            node_data['children'].append(child_data)
        
        return node_data
    
    def _parse_bounds(self, bounds_str: str) -> List[int]:
        """解析边界坐标字符串"""
        if not bounds_str:
            return [0, 0, 0, 0]
        
        try:
            # 格式: "[left,top][right,bottom]"
            bounds_str = bounds_str.replace('][', ',').replace('[', '').replace(']', '')
            coords = [int(x) for x in bounds_str.split(',')]
            return coords
        except:
            return [0, 0, 0, 0]
    
    def find_element_at_position(self, hierarchy: dict, x: int, y: int) -> Optional[dict]:
        """在层次结构中查找指定位置的元素"""
        def search_node(node: dict) -> Optional[dict]:
            if not node.get('bounds'):
                return None
            
            left, top, right, bottom = node['bounds']
            
            # 检查点击位置是否在当前节点范围内
            if left <= x <= right and top <= y <= bottom:
                # 优先检查子节点
                for child in node.get('children', []):
                    result = search_node(child)
                    if result:
                        return result
                
                # 如果子节点中没找到，返回当前节点
                return node
            
            return None
        
        return search_node(hierarchy)
    
    def get_element_path(self, hierarchy: dict, target_element: dict) -> List[dict]:
        """获取从根节点到目标元素的路径"""
        def find_path(node: dict, path: List[dict]) -> Optional[List[dict]]:
            current_path = path + [node]
            
            # 如果找到目标元素
            if node == target_element:
                return current_path
            
            # 在子节点中递归查找
            for child in node.get('children', []):
                result = find_path(child, current_path)
                if result:
                    return result
            
            return None
        
        return find_path(hierarchy, []) or []