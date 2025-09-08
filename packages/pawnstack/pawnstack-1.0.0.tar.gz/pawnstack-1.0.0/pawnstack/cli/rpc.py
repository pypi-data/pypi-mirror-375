"""
PawnStack RPC 도구

JSON-RPC 호출 및 테스트 도구
"""

import json
import asyncio
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from argparse import ArgumentParser

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import AsyncBaseCLI
from pawnstack.cli.banner import generate_banner
from pawnstack.http_client.client import HttpClient

# 모듈 메타데이터
__description__ = 'JSON-RPC client and testing tool'

__epilog__ = (
    "JSON-RPC client for testing and interacting with RPC services.\n\n"
    "Usage examples:\n"
    "  1. Simple RPC call:\n\tpawns rpc --url http://localhost:8080/rpc --method getInfo\n\n"
    "  2. RPC with parameters:\n\tpawns rpc --url http://localhost:8080/rpc --method transfer --params '{\"to\": \"hx123\", \"value\": \"1000\"}'\n\n"
    "  3. Batch RPC calls:\n\tpawns rpc --url http://localhost:8080/rpc --batch-file requests.json\n\n"
    "For more details, use the -h or --help flag."
)


@dataclass
class RPCConfig:
    """RPC 설정"""
    url: str = ""
    method: str = ""
    params: Dict[str, Any] = None
    timeout: float = 30.0
    batch_file: str = ""
    id: int = 1


class RPCCLI(AsyncBaseCLI):
    """RPC CLI"""

    def __init__(self, args=None):
        super().__init__(args)
        self.http_client = HttpClient()

    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        parser.add_argument('--url', type=str, help='RPC endpoint URL', required=True)
        parser.add_argument('--method', type=str, help='RPC method name')
        parser.add_argument('--params', type=str, help='RPC parameters in JSON format')
        parser.add_argument('--timeout', type=float, help='Request timeout (default: 30)', default=30.0)
        parser.add_argument('--batch-file', type=str, help='JSON file with batch RPC requests')
        parser.add_argument('--id', type=int, help='RPC request ID (default: 1)', default=1)

        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                          help='Logging level (default: INFO)', default="INFO")

    def setup_config(self):
        """설정 초기화"""
        args = self.args
        app_name = 'rpc'

        pawn.set(
            PAWN_LOGGER=dict(
                log_level=getattr(args, 'log_level', 'INFO'),
                stdout_level=getattr(args, 'log_level', 'INFO'),
                stdout=True,
                use_hook_exception=True,
                show_path=False,
            ),
            PAWN_CONSOLE=dict(
                redirect=True,
                record=True,
            ),
            app_name=app_name,
            args=args,
        )

    def print_banner(self):
        """배너 출력"""
        banner = generate_banner(
            app_name="RPC",
            author="PawnStack Team",
            version=__version__,
            font="graffiti"
        )
        print(banner)

    def create_config(self) -> RPCConfig:
        """설정 객체 생성"""
        params = None
        if hasattr(self.args, 'params') and self.args.params:
            try:
                params = json.loads(self.args.params)
            except json.JSONDecodeError as e:
                self.log_error(f"Invalid JSON in params: {e}")
                params = {}

        return RPCConfig(
            url=getattr(self.args, 'url', ''),
            method=getattr(self.args, 'method', ''),
            params=params,
            timeout=getattr(self.args, 'timeout', 30.0),
            batch_file=getattr(self.args, 'batch_file', ''),
            id=getattr(self.args, 'id', 1)
        )

    async def send_rpc_request(self, config: RPCConfig) -> Dict[str, Any]:
        """RPC 요청 전송"""
        request_data = {
            "jsonrpc": "2.0",
            "method": config.method,
            "id": config.id
        }

        if config.params:
            request_data["params"] = config.params

        try:
            response = await self.http_client.post(
                config.url,
                json=request_data,
                timeout=config.timeout,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "response": response.json(),
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": 0
            }

    async def send_batch_requests(self, config: RPCConfig) -> List[Dict[str, Any]]:
        """배치 RPC 요청 전송"""
        try:
            with open(config.batch_file, 'r') as f:
                batch_requests = json.load(f)

            if not isinstance(batch_requests, list):
                self.log_error("Batch file must contain a JSON array")
                return []

            results = []
            for i, request in enumerate(batch_requests):
                if not isinstance(request, dict):
                    self.log_error(f"Request {i} is not a valid JSON object")
                    continue

                # 기본값 설정
                if "jsonrpc" not in request:
                    request["jsonrpc"] = "2.0"
                if "id" not in request:
                    request["id"] = i + 1

                pawn.console.log(f"📤 Sending request {i+1}: {request.get('method', 'unknown')}")

                try:
                    response = await self.http_client.post(
                        config.url,
                        json=request,
                        timeout=config.timeout,
                        headers={'Content-Type': 'application/json'}
                    )

                    if response.status_code == 200:
                        results.append({
                            "request_id": i + 1,
                            "success": True,
                            "response": response.json()
                        })
                    else:
                        results.append({
                            "request_id": i + 1,
                            "success": False,
                            "error": f"HTTP {response.status_code}: {response.text}"
                        })

                except Exception as e:
                    results.append({
                        "request_id": i + 1,
                        "success": False,
                        "error": str(e)
                    })

            return results

        except FileNotFoundError:
            self.log_error(f"Batch file not found: {config.batch_file}")
            return []
        except json.JSONDecodeError as e:
            self.log_error(f"Invalid JSON in batch file: {e}")
            return []

    def display_response(self, result: Dict[str, Any]):
        """응답 결과 출력"""
        if result["success"]:
            response = result["response"]

            pawn.console.log("[green]✅ RPC Request Successful[/green]")

            if "result" in response:
                pawn.console.print("📋 Result:")
                pawn.console.print(json.dumps(response["result"], indent=2, ensure_ascii=False))

            if "error" in response:
                pawn.console.print("[red]❌ RPC Error:[/red]")
                pawn.console.print(json.dumps(response["error"], indent=2, ensure_ascii=False))

            pawn.console.print(f"🆔 Request ID: {response.get('id', 'N/A')}")

        else:
            pawn.console.log(f"[red]❌ Request Failed: {result['error']}[/red]")

    def display_batch_results(self, results: List[Dict[str, Any]]):
        """배치 결과 출력"""
        successful = sum(1 for r in results if r["success"])
        total = len(results)

        pawn.console.log(f"📊 Batch Results: {successful}/{total} successful")

        for result in results:
            request_id = result["request_id"]

            if result["success"]:
                response = result["response"]
                pawn.console.log(f"[green]✅ Request {request_id}: Success[/green]")

                if "error" in response:
                    pawn.console.print(f"  [red]RPC Error: {response['error']}[/red]")
                elif "result" in response:
                    # 결과가 너무 길면 요약만 표시
                    result_str = json.dumps(response["result"], ensure_ascii=False)
                    if len(result_str) > 100:
                        result_str = result_str[:100] + "..."
                    pawn.console.print(f"  Result: {result_str}")
            else:
                pawn.console.log(f"[red]❌ Request {request_id}: {result['error']}[/red]")

    async def run_async(self) -> int:
        """RPC CLI 실행"""
        self.setup_config()
        self.print_banner()

        config = self.create_config()

        if not config.url:
            self.log_error("RPC URL is required (--url)")
            return 1

        if config.batch_file:
            # 배치 모드
            pawn.console.log(f"📦 Processing batch file: {config.batch_file}")
            results = await self.send_batch_requests(config)
            self.display_batch_results(results)
        else:
            # 단일 요청 모드
            if not config.method:
                self.log_error("RPC method is required (--method)")
                return 1

            pawn.console.log(f"📤 Sending RPC request: {config.method}")
            result = await self.send_rpc_request(config)
            self.display_response(result)

        return 0


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = RPCCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = RPCCLI()
    return cli.main()


if __name__ == '__main__':
    import sys
    sys.exit(main())
