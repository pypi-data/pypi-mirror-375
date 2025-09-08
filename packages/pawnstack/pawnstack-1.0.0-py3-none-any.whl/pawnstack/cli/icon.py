"""
PawnStack ICON 블록체인 도구

ICON 네트워크 상호작용 및 모니터링
"""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from argparse import ArgumentParser

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import AsyncBaseCLI
from pawnstack.cli.banner import generate_banner
from pawnstack.http_client.client import HttpClient

# 모듈 메타데이터
__description__ = 'ICON blockchain network interaction and monitoring tool'

__epilog__ = (
    "ICON blockchain network interaction and monitoring tool.\n\n"
    "Usage examples:\n"
    "  1. Get block info:\n\tpawns icon --rpc https://ctz.solidwallet.io/api/v3 --block latest\n\n"
    "  2. Monitor block height:\n\tpawns icon --rpc https://ctz.solidwallet.io/api/v3 --monitor --interval 5\n\n"
    "  3. Get transaction info:\n\tpawns icon --rpc https://ctz.solidwallet.io/api/v3 --tx 0x123...\n\n"
    "  4. Check balance:\n\tpawns icon --rpc https://ctz.solidwallet.io/api/v3 --balance hx123...\n\n"
    "For more details, use the -h or --help flag."
)


@dataclass
class IconRPCRequest:
    """ICON RPC 요청 데이터"""
    method: str
    params: Dict[str, Any]
    id: int = 1
    jsonrpc: str = "2.0"


class IconCLI(AsyncBaseCLI):
    """ICON CLI"""

    def __init__(self, args=None):
        super().__init__(args)
        self.http_client = HttpClient()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []

    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        parser.add_argument('--rpc', type=str, help='ICON RPC endpoint URL',
                          default='https://ctz.solidwallet.io/api/v3')

        # 조회 명령어
        parser.add_argument('--block', type=str, help='Get block info (block number or "latest")')
        parser.add_argument('--tx', type=str, help='Get transaction info by hash')
        parser.add_argument('--balance', type=str, help='Get ICX balance for address')
        parser.add_argument('--score', type=str, help='Get SCORE info by address')

        # 모니터링
        parser.add_argument('--monitor', action='store_true', help='Enable continuous monitoring mode')
        parser.add_argument('-i', '--interval', type=float, help='Monitoring interval in seconds (default: 10)', default=10)

        # 추가 옵션
        parser.add_argument('--timeout', type=float, help='Request timeout in seconds (default: 30)', default=30)
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done without actual requests')

        parser.add_argument('--log-level', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                          help='Logging level (default: INFO)', default="INFO")

    def setup_config(self):
        """설정 초기화"""
        args = self.args
        app_name = 'icon'

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
            app_name="ICON",
            author="PawnStack Team",
            version=__version__,
            font="graffiti"
        )
        print(banner)

    async def send_rpc_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """ICON RPC 요청 전송"""
        rpc_url = getattr(self.args, 'rpc', 'https://ctz.solidwallet.io/api/v3')
        timeout = getattr(self.args, 'timeout', 30.0)

        request_data = IconRPCRequest(
            method=method,
            params=params or {},
            id=self.request_count + 1
        )

        start_time = time.time()

        try:
            response = await self.http_client.post(
                rpc_url,
                json=request_data.__dict__,
                timeout=timeout,
                headers={'Content-Type': 'application/json'}
            )

            response_time = time.time() - start_time
            self.request_count += 1
            self.response_times.append(response_time)

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "result": result,
                    "response_time": response_time,
                    "method": method
                }
            else:
                self.error_count += 1
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "response_time": response_time,
                    "method": method
                }

        except Exception as e:
            self.error_count += 1
            return {
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time,
                "method": method
            }

    def format_icx_value(self, hex_value: str) -> str:
        """ICX 값 포맷팅 (hex to decimal)"""
        try:
            if hex_value.startswith('0x'):
                decimal_value = int(hex_value, 16)
                icx_value = decimal_value / (10 ** 18)  # ICX는 18 decimals
                return f"{icx_value:.6f} ICX"
            return hex_value
        except:
            return hex_value

    def format_block_info(self, block_data: Dict[str, Any]) -> str:
        """블록 정보 포맷팅"""
        if 'result' not in block_data:
            return str(block_data)

        block = block_data['result']

        info = []

        # 안전한 정수 변환
        try:
            height = block.get('height', '0x0')
            if isinstance(height, str) and height.startswith('0x'):
                height_int = int(height, 16)
            else:
                height_int = int(height) if height else 0
            info.append(f"Block Height: {height_int}")
        except (ValueError, TypeError):
            info.append(f"Block Height: {block.get('height', 'N/A')}")

        info.append(f"Block Hash: {block.get('block_hash', 'N/A')}")
        info.append(f"Previous Hash: {block.get('prev_block_hash', 'N/A')}")

        try:
            timestamp = block.get('time_stamp', '0x0')
            if isinstance(timestamp, str) and timestamp.startswith('0x'):
                timestamp_int = int(timestamp, 16)
            else:
                timestamp_int = int(timestamp) if timestamp else 0
            info.append(f"Timestamp: {timestamp_int}")
        except (ValueError, TypeError):
            info.append(f"Timestamp: {block.get('time_stamp', 'N/A')}")

        tx_list = block.get('confirmed_transaction_list', [])
        info.append(f"Transaction Count: {len(tx_list) if tx_list else 0}")

        return "\n".join(info)

    def format_transaction_info(self, tx_data: Dict[str, Any]) -> str:
        """트랜잭션 정보 포맷팅"""
        if 'result' not in tx_data:
            return str(tx_data)

        tx = tx_data['result']

        info = []
        info.append(f"Transaction Hash: {tx.get('txHash', 'N/A')}")

        try:
            block_height = tx.get('blockHeight', '0x0')
            if isinstance(block_height, str) and block_height.startswith('0x'):
                height_int = int(block_height, 16)
            else:
                height_int = int(block_height) if block_height else 0
            info.append(f"Block Height: {height_int}")
        except (ValueError, TypeError):
            info.append(f"Block Height: {tx.get('blockHeight', 'N/A')}")

        info.append(f"From: {tx.get('from', 'N/A')}")
        info.append(f"To: {tx.get('to', 'N/A')}")
        info.append(f"Value: {self.format_icx_value(tx.get('value', '0x0'))}")
        info.append(f"Status: {tx.get('status', 'N/A')}")

        return "\n".join(info)

    async def get_block_info(self, block_id: str) -> Dict[str, Any]:
        """블록 정보 조회"""
        if block_id == "latest":
            return await self.send_rpc_request("icx_getLastBlock")
        else:
            try:
                # 숫자인 경우 hex로 변환
                if block_id.isdigit():
                    block_height = hex(int(block_id))
                else:
                    block_height = block_id

                return await self.send_rpc_request("icx_getBlockByHeight", {"height": block_height})
            except ValueError:
                return {"success": False, "error": f"Invalid block ID: {block_id}"}

    async def get_transaction_info(self, tx_hash: str) -> Dict[str, Any]:
        """트랜잭션 정보 조회"""
        return await self.send_rpc_request("icx_getTransactionByHash", {"txHash": tx_hash})

    async def get_balance(self, address: str) -> Dict[str, Any]:
        """잔액 조회"""
        return await self.send_rpc_request("icx_getBalance", {"address": address})

    async def get_score_info(self, address: str) -> Dict[str, Any]:
        """SCORE 정보 조회"""
        return await self.send_rpc_request("icx_getScoreApi", {"address": address})

    def display_result(self, result: Dict[str, Any]):
        """결과 출력"""
        if not result.get('success', False):
            pawn.console.log(f"[red]❌ Error: {result.get('error', 'Unknown error')}[/red]")
            return

        method = result.get('method', '')
        response_time = result.get('response_time', 0)

        pawn.console.log(f"[green]✅ {method} completed in {response_time:.3f}s[/green]")

        # 결과 데이터 표시
        data = result.get('result', {})

        if method == "icx_getLastBlock" or method == "icx_getBlockByHeight":
            pawn.console.log(f"📦 Block Information:")
            pawn.console.log(self.format_block_info(data))
        elif method == "icx_getTransactionByHash":
            pawn.console.log(f"📄 Transaction Information:")
            pawn.console.log(self.format_transaction_info(data))
        elif method == "icx_getBalance":
            balance = data.get('result', '0x0')
            pawn.console.log(f"💰 Balance: {self.format_icx_value(balance)}")
        elif method == "icx_getScoreApi":
            pawn.console.log(f"📋 SCORE API:")
            pawn.console.log(json.dumps(data.get('result', {}), indent=2))
        else:
            pawn.console.log(json.dumps(data, indent=2))

    async def monitor_network(self):
        """네트워크 모니터링"""
        interval = getattr(self.args, 'interval', 10.0)

        pawn.console.log(f"🚀 Starting ICON network monitoring")
        pawn.console.log(f"📡 RPC Endpoint: {getattr(self.args, 'rpc', 'https://ctz.solidwallet.io/api/v3')}")
        pawn.console.log(f"⏱️  Interval: {interval}s")

        try:
            while True:
                result = await self.get_block_info("latest")

                if result.get('success'):
                    block_data = result.get('result', {}).get('result', {})

                    try:
                        height_hex = block_data.get('height', '0x0')
                        if isinstance(height_hex, str) and height_hex.startswith('0x'):
                            height = int(height_hex, 16)
                        else:
                            height = int(height_hex) if height_hex else 0
                    except (ValueError, TypeError):
                        height = 0

                    tx_list = block_data.get('confirmed_transaction_list', [])
                    tx_count = len(tx_list) if tx_list else 0

                    pawn.console.log(f"📦 Block #{height} - {tx_count} txs - {result['response_time']:.3f}s")
                else:
                    pawn.console.log(f"[red]❌ Failed to get block info: {result.get('error')}[/red]")

                # 통계 출력
                if self.request_count > 0:
                    success_rate = ((self.request_count - self.error_count) / self.request_count * 100)
                    avg_time = sum(self.response_times) / len(self.response_times)
                    pawn.console.log(f"📊 Stats: {self.request_count} requests, {success_rate:.1f}% success, avg: {avg_time:.3f}s")

                await asyncio.sleep(interval)

        except KeyboardInterrupt:
            self.log_info("ICON monitoring stopped by user")

    async def run_async(self) -> int:
        """ICON CLI 실행"""
        self.setup_config()
        self.print_banner()

        # 드라이 런 모드
        if getattr(self.args, 'dry_run', False):
            pawn.console.log("[DRY RUN] Would connect to ICON network")
            return 0

        # 모니터링 모드
        if getattr(self.args, 'monitor', False):
            await self.monitor_network()
            return 0

        # 개별 명령어 실행
        if getattr(self.args, 'block', None):
            result = await self.get_block_info(self.args.block)
            self.display_result(result)
        elif getattr(self.args, 'tx', None):
            result = await self.get_transaction_info(self.args.tx)
            self.display_result(result)
        elif getattr(self.args, 'balance', None):
            result = await self.get_balance(self.args.balance)
            self.display_result(result)
        elif getattr(self.args, 'score', None):
            result = await self.get_score_info(self.args.score)
            self.display_result(result)
        else:
            self.log_error("Please specify an action (--block, --tx, --balance, --score, or --monitor)")
            return 1

        return 0


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    cli = IconCLI()
    cli.get_arguments(parser)


def main():
    """메인 함수 (레거시 호환)"""
    cli = IconCLI()
    return cli.main()


if __name__ == '__main__':
    import sys
    sys.exit(main())
