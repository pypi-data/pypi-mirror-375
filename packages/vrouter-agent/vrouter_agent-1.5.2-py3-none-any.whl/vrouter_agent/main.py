from contextlib import asynccontextmanager
import sys
import argparse
from fastapi import FastAPI
from loguru import logger
import logging
import uvicorn

from vrouter_agent.core.db import init_db
from vrouter_agent.api import orders, transactions, tunnel_config, telemetry, root
from vrouter_agent.services.chain import Chain
from vrouter_agent.services.startup import initialize_services, shutdown_services
from vrouter_agent.utils.logger import InterceptHandler, format_record
import os
from vrouter_agent.core.config import settings

# Default configuration values
DEFAULT_LOG_FILE = "/var/log/vrouter-agent.log"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_LOG_LEVEL = "INFO"
VERSION = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.debug("Initializing database")
    init_db()
    
    # Initialize application services (stream listener, processor, etc.)
    logger.info("Initializing application services...")
    success = await initialize_services()
    if not success:
        logger.error("Failed to initialize application services")
        sys.exit(1)
    
    for route in app.routes:
        logger.info(f"Route: {route.path} - {route.name}")

    yield
    
    # Shutdown
    logger.info("Shutting down application services...")
    await shutdown_services()

app = FastAPI(
    title="VRouter Agent API",
    description="API for VRouter tunnel configuration and telemetry monitoring",
    version="1.0.0",
    contact={
        "name": "USDN vRouter Agent Server",
        "email": "support@usdatanetworks.com",
    },
    license_info={
        "name": "Private License",
    },
    lifespan=lifespan
)
app.include_router(root.router, tags=["root"])
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(tunnel_config.router, tags=["tunnel-config"])
app.include_router(telemetry.router, tags=["telemetry"])


def setup_logging(log_file: str, log_level: str):
    """Configure logging with the specified log file and level."""
    # set loguru format for root logger
    logging.getLogger().handlers = [InterceptHandler()]
    
    # Convert string log level to logging constant
    level_map = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    
    log_level_int = level_map.get(log_level.upper(), logging.INFO)
    
    # set format
    logger.configure(
        handlers=[
            {"sink": sys.stdout, "level": log_level_int, "format": format_record},
            {
                "sink": log_file,
                "rotation": "1 MB",
                "compression": "zip",
                "enqueue": True,
                "backtrace": True,
                "level": log_level_int,
                "format": format_record,
            },
        ]
    )




def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="VRouter Agent Server - API for VRouter tunnel configuration and telemetry monitoring",
        prog="vrouter-agent",
        epilog="For more information, visit: https://github.com/Unified-Sentinel-Data-Networks"
    )
    
    # Version option
    parser.add_argument(
        "--version", "-v",
        action="version",
        version=f"%(prog)s {VERSION}",
        help="Show version and exit"
    )
    
    # Server configuration options
    parser.add_argument(
        "--host",
        default=os.getenv("VRouterAgentHost", DEFAULT_HOST),
        help=f"Host to bind to (default: {DEFAULT_HOST}). Can also be set via VRouterAgentHost environment variable."
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=int(os.getenv("VRouterAgentPort", DEFAULT_PORT)),
        help=f"Port to bind to (default: {DEFAULT_PORT}). Can also be set via VRouterAgentPort environment variable."
    )
    
    # Logging configuration options
    parser.add_argument(
        "--log-file", "-l",
        default=os.getenv("VRouterAgentLogFile", DEFAULT_LOG_FILE),
        help=f"Log file path (default: {DEFAULT_LOG_FILE}). Can also be set via VRouterAgentLogFile environment variable."
    )
    parser.add_argument(
        "--log-level",
        default=os.getenv("VRouterAgentLogLevel", DEFAULT_LOG_LEVEL),
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help=f"Log level (default: {DEFAULT_LOG_LEVEL}). Can also be set via VRouterAgentLogLevel environment variable."
    )
    return parser.parse_args()


def start():
    """Start the VRouter Agent Server with command-line configuration."""
    args = parse_args()
    
    # Setup logging with the specified configuration
    setup_logging(args.log_file, args.log_level)

    logger.info("Starting vRouter Agent Server...")
    logger.info("************************")

    logger.info(f"Log file is saved to {args.log_file}")
    logger.info(f"Log level set to {args.log_level}")
    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info("************************")
    logger.info(settings.config.interfaces)
    logger.info(settings.config.multichain)
    
    # Basic multichain connectivity check - stream subscription for hostname and order_update is handled by startup services
    chain = Chain(chain=settings.config.multichain.chain, user=settings.config.global_.user)
    if not chain.is_running():
        logger.error(f"Multichain daemon for chain {settings.config.multichain.chain} is not running.")
        sys.exit(1)
    logger.info("Multichain daemon is running")
    
    uvicorn.run(
        "vrouter_agent.main:app", 
        host=args.host,
        port=args.port,
        reload=True,
        log_level=args.log_level.lower(),    
    )


if __name__ == "__main__":
    start()
