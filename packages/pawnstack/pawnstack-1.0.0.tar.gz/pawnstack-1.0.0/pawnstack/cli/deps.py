"""
PawnStack 의존성 관리 CLI

의존성 상태 확인, 설치 가이드 제공
"""

from argparse import ArgumentParser
from pawnstack.cli.base import BaseCLI
from pawnstack.cli.dependencies import DependencyChecker, print_installation_guide


class DepsCLI(BaseCLI):
    """의존성 관리 CLI 명령어"""

    def get_arguments(self, parser: ArgumentParser):
        """명령어 인수 정의"""
        parser.description = "PawnStack 의존성 상태 확인 및 관리"
        parser.epilog = """
사용 예제:
  pawnstack deps                    # 전체 의존성 상태 확인
  pawnstack deps --check blockchain # 블록체인 의존성만 확인
  pawnstack deps --install aws      # AWS 의존성 설치 제안
  pawnstack deps --guide            # 설치 가이드 출력
        """

        parser.add_argument(
            '--check',
            type=str,
            choices=DependencyChecker.get_available_extras(),
            help='특정 extras 의존성 확인'
        )

        parser.add_argument(
            '--install',
            type=str,
            choices=DependencyChecker.get_available_extras(),
            help='특정 extras 설치 제안'
        )

        parser.add_argument(
            '--guide',
            action='store_true',
            help='설치 가이드 출력'
        )

        parser.add_argument(
            '--list-commands',
            action='store_true',
            help='명령어별 필요 의존성 목록 출력'
        )

        parser.add_argument(
            '--auto-install',
            action='store_true',
            help='자동 설치 확인 (사용자 입력 없이 설치)'
        )

    def run(self) -> int:
        """명령어 실행"""
        try:
            if self.args.guide:
                return self._show_installation_guide()

            if self.args.list_commands:
                return self._list_command_dependencies()

            if self.args.check:
                return self._check_specific_dependency()

            if self.args.install:
                return self._install_dependency()

            # 기본: 전체 의존성 상태 출력
            return self._show_dependency_status()

        except Exception as e:
            self.log_error(f"의존성 확인 중 오류 발생: {e}")
            return 1

    def _show_dependency_status(self) -> int:
        """전체 의존성 상태 출력"""
        self.log_info("PawnStack 의존성 상태를 확인합니다...")

        # 의존성 상태 테이블 출력
        DependencyChecker.print_dependency_status()

        # 요약 정보
        installed = DependencyChecker.get_installed_extras()
        missing = DependencyChecker.get_missing_extras()

        self.log_info(f"설치된 extras: {len(installed)}개")
        if installed:
            for extra in installed:
                self.log_success(f"  ✓ {extra}")

        if missing:
            self.log_warning(f"누락된 extras: {len(missing)}개")
            for extra in missing:
                self.log_warning(f"  ✗ {extra}")

            self.log_info("누락된 기능을 설치하려면 다음 명령어를 사용하세요:")
            missing_str = ','.join(missing)
            self.log_info(f"  pip install pawnstack[{missing_str}]")
        else:
            self.log_success("모든 선택적 의존성이 설치되어 있습니다!")

        return 0

    def _check_specific_dependency(self) -> int:
        """특정 의존성 확인"""
        extra = self.args.check
        self.log_info(f"'{extra}' 의존성을 확인합니다...")

        if DependencyChecker.check_dependencies([extra]):
            self.log_success(f"'{extra}' 의존성이 모두 설치되어 있습니다!")
            return 0
        else:
            self.log_error(f"'{extra}' 의존성이 누락되었습니다.")
            return 1

    def _install_dependency(self) -> int:
        """의존성 설치 제안"""
        extra = self.args.install
        self.log_info(f"'{extra}' 의존성 설치를 확인합니다...")

        if DependencyChecker.check_dependencies([extra]):
            self.log_success(f"'{extra}' 의존성이 이미 설치되어 있습니다!")
            return 0

        # 자동 설치 제안
        success = DependencyChecker.auto_install_suggestion(
            [extra],
            auto_confirm=self.args.auto_install
        )

        return 0 if success else 1

    def _show_installation_guide(self) -> int:
        """설치 가이드 출력"""
        print_installation_guide()
        return 0

    def _list_command_dependencies(self) -> int:
        """명령어별 필요 의존성 목록 출력"""
        from rich.table import Table

        table = Table(title="명령어별 필요 의존성", show_header=True, header_style="bold magenta")
        table.add_column("명령어", style="cyan", width=12)
        table.add_column("필요 Extras", style="yellow")
        table.add_column("설명", style="dim")

        command_deps = DependencyChecker.COMMAND_DEPENDENCIES

        # 의존성이 있는 명령어들
        for command, extras in command_deps.items():
            if extras:
                extras_str = ", ".join(extras)
                description = self._get_command_description(command)
                table.add_row(command, extras_str, description)

        # 의존성이 없는 명령어들 (기본 기능)
        basic_commands = [
            ("info", "시스템 정보 출력"),
            ("banner", "배너 생성"),
            ("server", "서버 리소스 모니터링"),
            ("top", "시스템 리소스 모니터링"),
            ("net", "네트워크 도구"),
            ("http", "HTTP 모니터링"),
            ("proxy", "프록시 리플렉터"),
            ("websocket", "WebSocket 연결"),
        ]

        for command, description in basic_commands:
            table.add_row(command, "[dim]없음[/dim]", description)

        self.log_info("PawnStack CLI 명령어별 의존성 요구사항:")
        from pawnstack.config.global_config import pawn
        pawn.console.print(table)

        return 0

    def _get_command_description(self, command: str) -> str:
        """명령어 설명 반환"""
        descriptions = {
            # 블록체인 관련
            'wallet': '블록체인 지갑 관리',
            'icon': 'ICON 블록체인 도구',
            'rpc': 'JSON-RPC 호출',
            'goloop': 'Goloop 네트워크 관리',
            'gs': 'Genesis 파일 생성 및 검증',

            # 클라우드 관련
            'aws': 'AWS 메타정보 조회',
            's3': 'AWS S3 도구',

            # 컨테이너 관련
            'docker': 'Docker 컨테이너 관리',
            'compose': 'Docker Compose 관리',

            # 모니터링 및 알림
            'mon': '시스템 모니터링 (Prometheus)',
            'noti': '알림 시스템 (Slack, Discord)',

            # 개발 도구
            'init': '애플리케이션 스캐폴딩',
            'inspect': '시스템 및 애플리케이션 검사',
            'metadata': '메타데이터 추출 및 관리',

            # 인프라 도구
            'snap': '스냅샷 생성 및 관리',
            'tf': 'Terraform 프로젝트 관리',

            # 보안 도구
            'scan_key': '키 스캔 및 보안 검사',
        }
        return descriptions.get(command, '추가 기능')


def main():
    """메인 함수"""
    cli = DepsCLI()
    return cli.main()


if __name__ == '__main__':
    exit(main())
