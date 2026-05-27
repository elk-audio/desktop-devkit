"""Main entry point for Mock Events GUI application."""

import os
import sys
from concurrent import futures

import grpc
from PySide6.QtWidgets import QApplication

from gui.main_window import MainWindow
from grpc_server.servicer import PinProxyServicer
from grpc_server.generated import sensei_rpc_pb2_grpc

# Server configuration constants
GRPC_SERVER_HOST = "0.0.0.0"
GRPC_SERVER_PORT = 50051


def start_grpc_server(servicer: PinProxyServicer, host: str, port: int):
    """Start gRPC server in a background thread."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sensei_rpc_pb2_grpc.add_SenseiControllerServicer_to_server(servicer, server)
    server.add_insecure_port(f"{host}:{port}")
    server.start()
    print(f"gRPC server started on {host}:{port}")
    return server


def main():
    """Main application entry point."""
    # Create servicer
    servicer = PinProxyServicer()

    # Start gRPC server
    grpc_server = start_grpc_server(servicer, GRPC_SERVER_HOST, GRPC_SERVER_PORT)

    # Clear Qt style override environment variable to prevent kvantum error
    os.environ.pop("QT_STYLE_OVERRIDE", None)

    # Create Qt application
    app = QApplication()
    app.setStyle("Fusion")

    # Create and show main window
    window = MainWindow(servicer, GRPC_SERVER_HOST, GRPC_SERVER_PORT)
    window.show()

    # Run Qt event loop
    exit_code = app.exec()

    # Cleanup
    print("Shutting down gRPC server...")
    grpc_server.stop(grace=2)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
