import os
from typing import Optional

def get_env_variable(var_name: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    获取环境变量
    
    Args:
        var_name: 环境变量名称
        default: 默认值
        required: 是否必需
        
    Returns:
        环境变量值或默认值
        
    Raises:
        ValueError: 如果必需的环境变量不存在
    """
    value = os.getenv(var_name, default)
    
    if required and value is None:
        raise ValueError(f"Required environment variable '{var_name}' is not set")
    
    return value

def load_environment_variables(env_file: str = ".env") -> None:
    """
    从.env文件加载环境变量
    
    Args:
        env_file: 环境文件路径
    """
    if not os.path.exists(env_file):
        return
    
    with open(env_file, 'r') as f:
        for line in f:
            # 跳过注释和空行
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # 解析键值对
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"\'')  # 移除引号
                
                # 设置环境变量
                os.environ[key] = value