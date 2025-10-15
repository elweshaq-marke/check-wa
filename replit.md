# WhatsApp Number Checker API

## Overview

A comprehensive WhatsApp number verification system that allows checking if phone numbers are registered on WhatsApp. The system consists of three main components: a Node.js WhatsApp server using the Baileys library for WhatsApp connectivity, a Python FastAPI-based REST API for client interactions, and a Telegram bot for admin notifications. Additionally, a desktop GUI built with Flet provides an easy-to-use interface for managing the system.

The application enables users to verify WhatsApp number registration status, manage WhatsApp authentication sessions (upload existing or create new ones via pairing codes), and monitor system statistics in real-time. All operations are logged and reported to a designated Telegram admin account.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Multi-Component Architecture

The system uses a distributed architecture with three independent services that communicate via HTTP:

1. **WhatsApp Server (Node.js)** - Handles all WhatsApp protocol interactions
2. **API Server (Python/FastAPI)** - Provides REST endpoints and orchestrates requests
3. **Telegram Bot (Python)** - Provides admin interface and notifications
4. **Desktop GUI (Python/Flet)** - Optional local management interface

This separation allows each component to be scaled, maintained, and deployed independently. The API server acts as a gateway, forwarding requests to the WhatsApp server and handling response formatting.

### WhatsApp Integration Layer

**Technology**: Baileys library (@whiskeysockets/baileys v6.7.20)

The WhatsApp server manages all WhatsApp Web protocol interactions. It maintains persistent WebSocket connections to WhatsApp servers and handles authentication state. Session data is stored locally in the `auth_info_baileys` directory using multi-file authentication state management.

**Key Design Decisions**:
- **Multi-file auth state**: Credentials are split across multiple files rather than a single JSON file for better security and modularity
- **QR Code + Pairing Code support**: Dual authentication methods allow both QR scanning and phone-based pairing
- **Automatic reconnection**: Built-in connection recovery handles network interruptions without manual intervention
- **Session isolation**: Each session is stored in separate directories, allowing multi-session support

### API Layer Architecture

**Technology**: FastAPI (Python) with async/await patterns

The API server exposes RESTful endpoints for:
- Number verification (`/check`)
- Session management (`/upload-session`, `/create-session`)
- Statistics retrieval (`/stats`)
- Status monitoring (`/status`)

**Design Patterns**:
- **Proxy pattern**: API server forwards WhatsApp operations to the Node.js backend via HTTP
- **Async communication**: Uses aiohttp for non-blocking HTTP requests to WhatsApp server
- **Statistics aggregation**: In-memory stats tracking for real-time monitoring
- **Static file serving**: Includes web interface served from `/static`

**Why FastAPI**: Chosen for automatic API documentation (Swagger/OpenAPI), native async support for handling concurrent requests efficiently, and type validation via Pydantic models.

### Admin Notification System

**Technology**: python-telegram-bot library

Telegram integration provides real-time notifications to admin (Chat ID: 7011309417) for all system operations. The bot offers an interactive interface with inline keyboard buttons for common operations.

**Bot Commands**:
- `/start` - Main menu with operation buttons
- Inline callbacks for stats, number checking, session management, and status

**Design Decision**: Telegram was chosen over email/SMS for instant notifications, rich formatting support, and the ability to provide an interactive admin interface directly within the messaging app.

### Desktop GUI Component

**Technology**: Flet (Python-based Flutter wrapper)

Provides a cross-platform desktop application for:
- Starting/stopping servers
- Viewing real-time console logs
- Managing sessions through file uploads
- Monitoring system statistics

**Architecture**: The GUI spawns subprocess instances of the API and WhatsApp servers, capturing their stdout/stderr for display in the application console. This approach allows independent server lifecycle management.

### Session Management

WhatsApp authentication is handled through two mechanisms:

1. **Session Upload**: Users can upload pre-existing auth session directories (ZIP format)
2. **Pairing Code**: Users provide phone number to receive OTP-style pairing code

Sessions are stored in the `auth_info_baileys` directory structure:
```
auth_info_baileys/
├── creds.json          # Encryption keys and credentials
├── app-state-*.json    # WhatsApp state sync data
└── sender-key-*.json   # E2E encryption keys
```

### Process Management

**Run Scripts**: Multiple Python launcher scripts orchestrate component startup:
- `run.py` - Starts WhatsApp + API servers (no bot, no tunnel)
- `run_bot.py` - **Main launcher**: Starts all services (WhatsApp + API + Telegram Bot + Cloudflare Tunnel)
- `desktop_app.py` - Flet GUI that manages all components with tunnel support
- `telegram_bot.py` - Standalone Telegram bot server

**Process Monitoring**: Parent processes monitor child process health and automatically detect unexpected terminations.

### Statistics Tracking

In-memory statistics object tracks:
- Total number checks performed
- Registered vs not-registered counts
- Server uptime (from startup timestamp)
- Error counts

Statistics are reset on server restart (no persistent storage). This design prioritizes simplicity and real-time accuracy over historical data retention.

## External Dependencies

### Third-Party Services

1. **Telegram Bot API**
   - Bot Token: `7598031263:AAEnkrP-mQszjK9pStiLslCtOnKxAoS91UY`
   - Admin Chat ID: `7011309417`
   - Used for: Admin notifications and interactive bot interface
   - API Endpoint: `https://api.telegram.org/bot{token}/sendMessage`
   - Bot Features:
     - Interactive menu with inline buttons
     - Number checking
     - Session management (upload/create)
     - Real-time statistics
     - Server status monitoring

2. **Cloudflare Tunnel** (Automatic)
   - Tunnel ID: `bc9c6f68-4eb3-4a05-a9b3-0a7a842a71e1`
   - Fixed Hostname: **checkwa.elwe.qzz.io**
   - Token: `eyJhIjoiOGZiYzg1NDYzOGU2MjE4YWRjYWQwMWM5NDA3NDU3MjUiLCJ0IjoiYmM5YzZmNjgtNGViMy00YTA1LWE5YjMtMGE3YTg0MmE3MWUxIiwicyI6Ik9ETmhZMlV3TVRjdE16STFOUzAwTWpabUxXRXhOekV0TkdJd01UTm1aVGM1TnpoayJ9`
   - Purpose: Expose local API server to internet via secure tunnel
   - Automatically starts with `run_bot.py` and desktop app
   - Provides public HTTPS access without port forwarding

3. **WhatsApp Web Protocol**
   - Via Baileys library connection to WhatsApp servers
   - WebSocket-based real-time communication
   - End-to-end encryption handled by library

### NPM Dependencies

- **@whiskeysockets/baileys** (^6.7.20): WhatsApp Web API implementation
- **express** (^5.1.0): HTTP server framework for Node.js WhatsApp server
- **multer** (^2.0.2): File upload middleware for session uploads
- **qrcode-terminal** (^0.12.0): Terminal QR code rendering for authentication

### Python Dependencies

- **flet**: Cross-platform desktop GUI framework
- **fastapi**: Modern async web framework for APIs
- **uvicorn**: ASGI server for running FastAPI
- **python-telegram-bot**: Telegram Bot API wrapper
- **aiohttp**: Async HTTP client for API-to-WhatsApp communication
- **python-multipart**: Form data parsing for file uploads
- **qrcode**: QR code generation
- **pillow**: Image processing for QR codes

### Local File System Dependencies

- **auth_info_baileys/**: WhatsApp session storage directory
- **uploads/**: Temporary storage for uploaded session files
- **static/**: Web interface assets (HTML/CSS/JS)

### Network Architecture

**Local Communication**:
- WhatsApp Server: `localhost:3000`
- API Server: `localhost:5000`
- Inter-service communication via HTTP (no shared memory/databases)

**External Access** (automatic via tunnel):
- Fixed Public URL: **https://checkwa.elwe.qzz.io**
- SSL/TLS handled by Cloudflare
- Automatically starts with main launcher
- Original local ports remain unchanged
- Requires cloudflared binary installed

### No Database Dependency

The system operates entirely in-memory and file-based storage:
- Session data: File system (auth_info_baileys directory)
- Statistics: In-memory Python dictionaries
- No SQL or NoSQL database required

This design choice simplifies deployment and reduces infrastructure requirements, suitable for lightweight verification workloads.