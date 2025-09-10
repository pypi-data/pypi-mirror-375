#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# MCP 서버 초기화 시 가상환경 설정
def setup_environment():
    """MCP 서버 시작 시 가상환경 생성 및 패키지 설치"""
    venv_path = Path.home() / ".ki-aws-strands-agentcore-venv"
    
    if not venv_path.exists():
        print(f"Creating virtual environment at {venv_path}")
        subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
        
        # 가상환경의 pip 경로
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
        
        # 필요한 패키지 설치
        packages = [
            "strands-agents",
            "strands-agents-tools", 
            "bedrock-agentcore",
            "bedrock-agentcore-starter-toolkit"
        ]
        
        for package in packages:
            print(f"Installing {package}...")
            subprocess.run([str(pip_path), "install", package], check=True)
        
        print("Environment setup complete!")
    
    return venv_path

# 가상환경 설정
VENV_PATH = setup_environment()

# MCP 서버 생성
mcp = FastMCP(host="0.0.0.0", stateless_http=True)

@mcp.tool()
def run_local_test(
    agent_path: str,
    agent_filename: str
) -> dict:
    """
    가상환경에서 Strands Agent 로컬 테스트 실행
    
    Args:
        agent_path: Agent 파일이 있는 디렉토리 경로
        agent_filename: Agent 파일명 (예: "s3_bucket_query.py")
    
    Returns:
        dict: 테스트 실행 결과
    """
    try:
        # 가상환경 경로
        if os.name == 'nt':  # Windows
            python_path = VENV_PATH / "Scripts" / "python"
        else:  # Unix/Linux/macOS
            python_path = VENV_PATH / "bin" / "python"
        
        # Agent 실행
        agent_file = Path(agent_path) / agent_filename
        result = subprocess.run(
            [str(python_path), str(agent_file)],
            cwd=agent_path,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "stdout": result.stdout,
            "stderr": result.stderr,
            "return_code": result.returncode
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"로컬 테스트 실행 중 오류: {str(e)}"
        }

@mcp.tool()
def setup_agentcore_env(
    agent_path: str
) -> dict:
    """
    AgentCore 배포를 위한 환경 준비
    
    Args:
        agent_path: Agent 파일이 있는 디렉토리 경로
    
    Returns:
        dict: 환경 설정 결과
    """
    try:
        # agentcore-env 가상환경 생성
        agentcore_venv = Path(agent_path) / "agentcore-env"
        
        if not agentcore_venv.exists():
            subprocess.run([sys.executable, "-m", "venv", str(agentcore_venv)], check=True)
        
        # 가상환경의 pip 경로
        if os.name == 'nt':  # Windows
            pip_path = agentcore_venv / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            pip_path = agentcore_venv / "bin" / "pip"
        
        # AgentCore 패키지 설치
        packages = [
            "bedrock-agentcore",
            "strands-agents", 
            "bedrock-agentcore-starter-toolkit"
        ]
        
        for package in packages:
            subprocess.run([str(pip_path), "install", package], check=True)
        
        return {
            "status": "success",
            "message": "AgentCore 환경 준비 완료",
            "venv_path": str(agentcore_venv)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"환경 준비 중 오류: {str(e)}"
        }

@mcp.tool()
def run_agentcore_deploy(
    agent_path: str,
    agent_filename: str,
    iam_role_arn: str = None
) -> dict:
    """
    AgentCore 배포 명령 실행
    
    Args:
        agent_path: Agent 파일이 있는 디렉토리 경로
        agent_filename: Agent 파일명
        iam_role_arn: IAM 역할 ARN (선택사항)
    
    Returns:
        dict: 배포 결과
    """
    try:
        # agentcore-env 가상환경 경로
        agentcore_venv = Path(agent_path) / "agentcore-env"
        
        if os.name == 'nt':  # Windows
            agentcore_path = agentcore_venv / "Scripts" / "agentcore"
        else:  # Unix/Linux/macOS
            agentcore_path = agentcore_venv / "bin" / "agentcore"
        
        # agentcore configure 실행
        configure_cmd = [str(agentcore_path), "configure", "-e", agent_filename]
        configure_result = subprocess.run(
            configure_cmd,
            cwd=agent_path,
            capture_output=True,
            text=True,
            input=f"{iam_role_arn or ''}\n\n\n\n",  # IAM 역할, ECR, 의존성, 인증 기본값
            timeout=120
        )
        
        if configure_result.returncode != 0:
            return {
                "status": "error",
                "message": "agentcore configure 실패",
                "stderr": configure_result.stderr
            }
        
        # agentcore launch 실행
        launch_cmd = [str(agentcore_path), "launch"]
        launch_result = subprocess.run(
            launch_cmd,
            cwd=agent_path,
            capture_output=True,
            text=True,
            timeout=300  # 5분 타임아웃
        )
        
        return {
            "status": "success" if launch_result.returncode == 0 else "error",
            "configure_output": configure_result.stdout,
            "launch_output": launch_result.stdout,
            "launch_stderr": launch_result.stderr,
            "return_code": launch_result.returncode
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"배포 중 오류: {str(e)}"
        }

def main():
    """MCP 서버 실행"""
    mcp.run()

if __name__ == "__main__":
    main()
