#!/usr/bin/env python3
"""
PawnStack File 도구

파일 처리 및 관리 유틸리티
"""

import os
import sys
import json
import asyncio
from typing import Union, Any, List
from argparse import ArgumentParser

from pawnstack import __version__
from pawnstack.config.global_config import pawn
from pawnstack.cli.base import FileBaseCLI
from pawnstack.cli.banner import generate_banner
from pawnstack.utils.file import (
    NullByteRemover, Tail, check_path, check_file_overwrite, get_file_path,
    open_json, open_yaml_file, write_json, write_yaml
)

# 모듈 메타데이터
__description__ = 'File processing and management utilities'

__epilog__ = (
    "File processing and management utilities for various tasks.\n\n"
    "Usage examples:\n"
    "  1. Remove null bytes from files:\n\tpawns file nullbyte --input file1.txt file2.txt\n\n"
    "  2. Monitor log files:\n\tpawns file tail --input /var/log/app.log --filters ERROR WARNING\n\n"
    "  3. Check file information:\n\tpawns file info --input example.txt\n\n"
    "  4. Convert file formats:\n\tpawns file convert --input data.json --output data.yaml --format yaml\n\n"
    "For more details, use the -h or --help flag."
)


class NullByteCLI(FileBaseCLI):
    """NullByte CLI"""
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        self.get_common_file_arguments(parser)
        parser.add_argument('--chunk-size', type=int, default=1024*1024, 
                          help='Chunk size for processing files (default: 1MB)')
        parser.add_argument('--replace-with', type=str, default='', 
                          help='String to replace null bytes with (default: empty)')
    
    def run(self) -> int:
        """NullByte CLI 실행"""
        input_files = getattr(self.args, 'input', [])
        if not input_files:
            self.log_error("No input files specified")
            return 1
        
        # Convert to list if single file
        if isinstance(input_files, str):
            input_files = [input_files]
        
        chunk_size = getattr(self.args, 'chunk_size', 1024*1024)
        replace_with = getattr(self.args, 'replace_with', '').encode('utf-8') if getattr(self.args, 'replace_with', '') else None
        
        try:
            remover = NullByteRemover(
                file_paths=input_files,
                chunk_size=chunk_size,
                replace_with=replace_with
            )
            remover.run()
            return 0
        except Exception as e:
            self.log_error(f"Error processing files: {e}")
            return 1


class TailCLI(FileBaseCLI):
    """Tail CLI"""
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        self.get_common_file_arguments(parser)
        parser.add_argument('--filters', type=str, nargs='*', default=[],
                          help='Filters for log lines (regex patterns)')
        parser.add_argument('--async-mode', action='store_true',
                          help='Enable asynchronous mode for tail')
        parser.add_argument('--follow', action='store_true',
                          help='Follow file changes (default for tail)')
    
    def run(self) -> int:
        """Tail CLI 실행"""
        input_files = getattr(self.args, 'input', [])
        if not input_files:
            self.log_error("No input files specified")
            return 1
        
        # Convert to list if single file
        if isinstance(input_files, str):
            input_files = [input_files]
        
        filters = getattr(self.args, 'filters', [])
        async_mode = getattr(self.args, 'async_mode', False)
        
        try:
            # Simple callback function to print lines
            def print_line(line):
                print(line)
            
            tail = Tail(
                log_file_paths=input_files,
                filters=filters,
                callback=print_line,
                async_mode=async_mode
            )
            
            # Run the tail command
            tail.follow()
            return 0
        except KeyboardInterrupt:
            self.log_info("Tail monitoring stopped by user")
            return 0
        except Exception as e:
            self.log_error(f"Error in tail monitoring: {e}")
            return 1


class InfoCLI(FileBaseCLI):
    """Info CLI"""
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        self.get_common_file_arguments(parser)
        parser.add_argument('--detailed', action='store_true',
                          help='Show detailed file information')
    
    def run(self) -> int:
        """Info CLI 실행"""
        input_files = getattr(self.args, 'input', [])
        if not input_files:
            self.log_error("No input files specified")
            return 1
        
        # Convert to list if single file
        if isinstance(input_files, str):
            input_files = [input_files]
        
        detailed = getattr(self.args, 'detailed', False)
        
        for file_path in input_files:
            if not os.path.exists(file_path):
                self.log_warning(f"File not found: {file_path}")
                continue
            
            if detailed:
                info = get_file_path(file_path)
                info.update(check_path(file_path, detailed=True))
                
                # Add file size
                try:
                    info["size"] = os.path.getsize(file_path)
                except Exception:
                    info["size"] = "Unknown"
                
                # Add modification time
                try:
                    info["modified"] = os.path.ctime(file_path)
                except Exception:
                    info["modified"] = "Unknown"
                
                # Show detailed info
                self.log_info(f"File Information: {file_path}")
                for key, value in info.items():
                    print(f"  {key}: {value}")
            else:
                file_type = check_path(file_path)
                print(f"{file_path}: {file_type}")
        
        return 0


class ConvertCLI(FileBaseCLI):
    """Convert CLI"""
    
    def get_arguments(self, parser: ArgumentParser):
        """인수 정의"""
        self.get_common_file_arguments(parser)
        parser.add_argument('--from-format', choices=['json', 'yaml', 'csv'],
                          help='Input format (auto-detected if not specified)')
    
    def run(self) -> int:
        """Convert CLI 실행"""
        input_file = getattr(self.args, 'input', None)
        output_file = getattr(self.args, 'output', None)
        from_format = getattr(self.args, 'from_format', None)
        to_format = getattr(self.args, 'format', 'json')
        
        if not input_file:
            self.log_error("No input file specified")
            return 1
        
        if not output_file:
            self.log_error("No output file specified")
            return 1
        
        # Auto-detect input format if not specified
        if not from_format:
            extension = os.path.splitext(input_file)[1].lower()
            if extension in ['.json']:
                from_format = 'json'
            elif extension in ['.yaml', '.yml']:
                from_format = 'yaml'
            elif extension in ['.csv']:
                from_format = 'csv'
            else:
                self.log_error(f"Unable to auto-detect format for file: {input_file}")
                return 1
        
        # Check if output file already exists
        if not check_file_overwrite(output_file):
            return 1
        
        try:
            # Read input file
            if from_format == 'json':
                data = open_json(input_file)
            elif from_format == 'yaml':
                data = open_yaml_file(input_file)
            elif from_format == 'csv':
                self.log_error("CSV import not yet implemented")
                return 1
            else:
                self.log_error(f"Unsupported input format: {from_format}")
                return 1
            
            # Write output file
            if to_format == 'json':
                write_json(output_file, data)
                self.log_success(f"Converted {input_file} ({from_format}) to {output_file} ({to_format})")
            elif to_format == 'yaml':
                write_yaml(output_file, data)
                self.log_success(f"Converted {input_file} ({from_format}) to {output_file} ({to_format})")
            elif to_format == 'csv':
                self.log_error("CSV export not yet implemented")
                return 1
            else:
                self.log_error(f"Unsupported output format: {to_format}")
                return 1
            
            return 0
            
        except Exception as e:
            self.log_error(f"Error converting file: {e}")
            return 1


def get_arguments(parser: ArgumentParser):
    """인수 정의 (레거시 호환)"""
    # 파일 처리 명령어에 대한 하위 파서 생성
    subparsers = parser.add_subparsers(dest='file_command', help='File processing commands')
    
    # NullByte 명령어
    nullbyte_parser = subparsers.add_parser('nullbyte', help='Remove null bytes from files')
    NullByteCLI().get_arguments(nullbyte_parser)
    
    # Tail 명령어
    tail_parser = subparsers.add_parser('tail', help='Monitor log files')
    TailCLI().get_arguments(tail_parser)
    
    # Info 명령어
    info_parser = subparsers.add_parser('info', help='Show file information')
    InfoCLI().get_arguments(info_parser)
    
    # Convert 명령어
    convert_parser = subparsers.add_parser('convert', help='Convert file formats')
    ConvertCLI().get_arguments(convert_parser)


def main():
    """메인 함수 (레거시 호환)"""
    # 명령줄 인수 파싱
    import argparse
    parser = argparse.ArgumentParser(description=__description__, epilog=__epilog__, formatter_class=argparse.RawDescriptionHelpFormatter)
    get_arguments(parser)
    args = parser.parse_args()
    
    # 설정 초기화
    pawn.set(
        PAWN_LOGGER=dict(
            log_level="INFO",
            stdout_level="INFO",
            stdout=True,
            use_hook_exception=True,
            show_path=False,
        ),
        PAWN_CONSOLE=dict(
            redirect=True,
            record=True,
        ),
        app_name='file',
        args=args,
    )
    
    # 배너 출력
    banner = generate_banner(
        app_name="File",
        author="PawnStack Team",
        version=__version__,
        font="graffiti"
    )
    print(banner)
    
    # 명령어 실행
    file_command = getattr(args, 'file_command', 'info')
    
    if file_command == 'nullbyte':
        cli = NullByteCLI(args)
        return cli.run()
    elif file_command == 'tail':
        cli = TailCLI(args)
        return cli.run()
    elif file_command == 'info':
        cli = InfoCLI(args)
        return cli.run()
    elif file_command == 'convert':
        cli = ConvertCLI(args)
        return cli.run()
    else:
        print(f"Unknown command: {file_command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())