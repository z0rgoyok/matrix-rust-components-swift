#!/usr/bin/env python3
"""Подготовить Swift package и архив из проверенной сборки нашего Matrix SDK."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def git(directory, *args):
    return subprocess.check_output(['git', '-C', str(directory), *args], text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    sdk = args.sdk.resolve()
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-tich\.\d+)?', args.version):
        parser.error('Версия должна иметь вид 26.10.21')
    if git(sdk, 'remote', 'get-url', 'origin') != 'https://github.com/z0rgoyok/matrix-rust-sdk.git':
        parser.error('Источник SDK должен быть нашим форком')
    if git(sdk, 'status', '--porcelain', '--untracked-files=no'):
        parser.error('В SDK есть незакоммиченные изменения')
    revision = git(sdk, 'rev-parse', 'HEAD')
    subprocess.run(['git', '-C', str(sdk), 'merge-base', '--is-ancestor', revision,
                    'origin/tich/main'], check=True)
    generated = sdk / 'bindings/apple/generated'
    receipt = json.loads((generated / 'tich-build.json').read_text())
    if receipt['source_sha'] != revision:
        parser.error('Квитанция сборки не соответствует исходникам SDK')
    for relative, expected in receipt['files'].items():
        if hashlib.sha256((generated / relative).read_bytes()).hexdigest() != expected:
            parser.error('Содержимое SDK изменилось после сборки')
    output = ROOT / '.automate' / args.version
    output.mkdir(parents=True, exist_ok=True)
    archive = output / 'MatrixSDKFFI.xcframework.zip'
    subprocess.run(['ditto', '-c', '-k', '--keepParent',
                    str(generated / 'MatrixSDKFFI.xcframework'), str(archive)], check=True)
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    target = ROOT / 'Sources/MatrixRustSDK'
    for old in target.glob('*.swift'):
        old.unlink()
    for source in (generated / 'swift').glob('*.swift'):
        shutil.copy2(source, target / source.name)
    manifest = (ROOT / 'Package.swift').read_text()
    manifest = re.sub(r'let checksum = "[^"]+"', 'let checksum = "' + checksum + '"', manifest)
    manifest = re.sub(r'let version = "[^"]+"', 'let version = "' + args.version + '"', manifest)
    manifest = manifest.replace('github.com/element-hq/matrix-rust-components-swift/',
                                'github.com/z0rgoyok/matrix-rust-components-swift/')
    (ROOT / 'Package.swift').write_text(manifest)
    receipt.update({'version': args.version, 'archive_sha256': checksum,
                    'sdk_repository': 'https://github.com/z0rgoyok/matrix-rust-sdk'})
    (ROOT / 'tich-source.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'version': args.version, 'source_sha': revision,
                      'archive': str(archive), 'sha256': checksum}, indent=2))


if __name__ == '__main__':
    main()
