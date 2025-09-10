#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# MCP 서버 초기화 시 가상환경 설정
def setup_environment():
    """MCP 서버 시작 시 가상환경 생성 및 패키지 설치"""
    venv_path = Path.home() / ".ki-aws-bedrock-agentcore-deployment-venv"
    
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
mcp = FastMCP()

@mcp.tool()
def run_local_test(
    agent_path: str,
    agent_filename: str
) -> dict:
    """
    가상환경에서 Strands Agent 로컬 테스트 실행 (실시간 스트리밍)
    
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
        
        print(f"🚀 가상환경에서 Agent 실행 시작: {agent_filename}")
        print(f"📁 경로: {agent_path}")
        print(f"🐍 Python: {python_path}")
        print("-" * 50)
        
        # Agent 실행 (실시간 출력)
        agent_file = Path(agent_path) / agent_filename
        process = subprocess.Popen(
            [str(python_path), str(agent_file)],
            cwd=agent_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        output_lines = []
        
        # 실시간 출력 스트리밍
        for line in iter(process.stdout.readline, ''):
            print(line.rstrip())  # 실시간 출력
            output_lines.append(line.rstrip())
        
        process.wait()
        
        print("-" * 50)
        print(f"✅ 실행 완료 (종료 코드: {process.returncode})")
        
        return {
            "status": "success" if process.returncode == 0 else "error",
            "output": "\n".join(output_lines),
            "return_code": process.returncode
        }
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
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
    AgentCore 배포 명령 실행 (실시간 스트리밍)
    
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
        
        print(f"🚀 AgentCore 배포 시작: {agent_filename}")
        print(f"📁 경로: {agent_path}")
        print("-" * 50)
        
        # agentcore configure 실행 (실시간 출력)
        print("⚙️ agentcore configure 실행 중...")
        configure_cmd = [str(agentcore_path), "configure", "-e", agent_filename]
        
        configure_process = subprocess.Popen(
            configure_cmd,
            cwd=agent_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 입력값 제공
        input_data = f"{iam_role_arn or ''}\n\n\n\n"
        configure_output = []
        
        configure_process.stdin.write(input_data)
        configure_process.stdin.close()
        
        for line in iter(configure_process.stdout.readline, ''):
            print(f"  {line.rstrip()}")
            configure_output.append(line.rstrip())
        
        configure_process.wait()
        
        if configure_process.returncode != 0:
            print("❌ agentcore configure 실패")
            return {
                "status": "error",
                "message": "agentcore configure 실패",
                "configure_output": "\n".join(configure_output)
            }
        
        print("✅ agentcore configure 완료")
        print("-" * 50)
        
        # agentcore launch 실행 (실시간 출력)
        print("🚀 agentcore launch 실행 중...")
        launch_cmd = [str(agentcore_path), "launch"]
        
        launch_process = subprocess.Popen(
            launch_cmd,
            cwd=agent_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        launch_output = []
        
        for line in iter(launch_process.stdout.readline, ''):
            print(f"  {line.rstrip()}")
            launch_output.append(line.rstrip())
        
        launch_process.wait()
        
        print("-" * 50)
        if launch_process.returncode == 0:
            print("✅ AgentCore 배포 완료!")
        else:
            print("❌ AgentCore 배포 실패")
        
        return {
            "status": "success" if launch_process.returncode == 0 else "error",
            "configure_output": "\n".join(configure_output),
            "launch_output": "\n".join(launch_output),
            "return_code": launch_process.returncode
        }
        
    except Exception as e:
        print(f"❌ 배포 중 오류: {str(e)}")
        return {
            "status": "error",
            "message": f"배포 중 오류: {str(e)}"
        }

def main():
    """MCP 서버 실행"""
    mcp.run()

if __name__ == "__main__":
    main()
