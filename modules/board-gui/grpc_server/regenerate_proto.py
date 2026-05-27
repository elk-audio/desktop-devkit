#!/usr/bin/env python3
"""
Script to regenerate protobuf files from pin_events.proto
and automatically fix the import statement.
"""

import subprocess
import sys
from pathlib import Path


def run_protoc():
    """Run the protoc compiler to generate Python files."""
    print("Regenerating protobuf files...")

    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        "-I./sensei-grpc-api",
        "--python_out=grpc_server/generated",
        "--grpc_python_out=grpc_server/generated",
        "--pyi_out=grpc_server/generated",
        "sensei_rpc.proto"
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ Protobuf files generated successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running protoc: {e.stderr}", file=sys.stderr)
        return False


def create_init_file():
    """Create __init__.py in the generated directory to make it a package."""
    print("Creating __init__.py...")

    init_file = Path("grpc_server/generated/__init__.py")
    init_file.parent.mkdir(parents=True, exist_ok=True)

    if not init_file.exists():
        init_file.write_text("# Generated protobuf package\n")
        print("✓ __init__.py created")
    else:
        print("✓ __init__.py already exists")

    return True


def fix_import():
    """Fix the import statement in sensei_rpc_pb2_grpc.py."""
    print("Fixing import statement...")

    grpc_file = Path("grpc_server/generated/sensei_rpc_pb2_grpc.py")

    if not grpc_file.exists():
        print(f"✗ File not found: {grpc_file}", file=sys.stderr)
        return False

    content = grpc_file.read_text()

    # Replace the absolute import with a relative import
    old_import = "import sensei_rpc_pb2 as sensei__rpc__pb2"
    new_import = "from . import sensei_rpc_pb2 as sensei__rpc__pb2"

    if old_import in content:
        content = content.replace(old_import, new_import)
        grpc_file.write_text(content)
        print("✓ Import statement fixed")
        return True
    elif new_import in content:
        print("✓ Import statement already correct")
        return True
    else:
        print("⚠ Warning: Expected import statement not found", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    if not run_protoc():
        sys.exit(1)

    if not create_init_file():
        sys.exit(1)

    if not fix_import():
        sys.exit(1)

    print("\n✓ Protobuf regeneration complete!")


if __name__ == "__main__":
    main()
