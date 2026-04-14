"""
API Endpoint for WebSentinel - Production Ready REST API
Allows programmatic access to testing capabilities
Includes WebSocket live streaming for real-time test progress
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, List, Set
import asyncio
import uuid
from pathlib import Path
from datetime import datetime
import json
import sys
import os

# Add project root to sys.path so local packages (browser_use, utils, core) resolve
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
os.chdir(str(_PROJECT_ROOT))

from browser_use.browser.browser import Browser, BrowserConfig
from browser_use.browser.context import BrowserContextConfig
from utils.model_provider import get_llm
from core.comprehensive_tester import ComprehensiveTester
from core.ultra_pdf_generator import UltraEnhancedPDFGenerator
from core.ai_analyzer import AIAnalyzer
from dotenv import load_dotenv

load_dotenv()


# ──────────────────────────────────────────────────────────────
# WebSocket Progress Streamer
# ──────────────────────────────────────────────────────────────

class ProgressStreamer:
    """
    Manages WebSocket connections per job and broadcasts progress events
    as JSON messages:  {"event": "...", "data": "...", "progress": 0-100}
    """

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, job_id: str, ws: WebSocket):
        await ws.accept()
        if job_id not in self._connections:
            self._connections[job_id] = set()
        self._connections[job_id].add(ws)

    def disconnect(self, job_id: str, ws: WebSocket):
        if job_id in self._connections:
            self._connections[job_id].discard(ws)
            if not self._connections[job_id]:
                del self._connections[job_id]

    async def broadcast(self, job_id: str, event: str, data: str, progress: int = 0):
        """Send a JSON event to all connected clients for a given job."""
        message = json.dumps({
            "event": event,
            "data": data,
            "progress": progress,
            "timestamp": datetime.now().isoformat()
        })
        dead: List[WebSocket] = []
        for ws in self._connections.get(job_id, set()):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(job_id, ws)


progress_streamer = ProgressStreamer()


# ──────────────────────────────────────────────────────────────
# FastAPI Application
# ──────────────────────────────────────────────────────────────

app = FastAPI(
    title="WebSentinel API",
    description="REST API for comprehensive website testing with WebSocket live streaming",
    version="1.1.0"
)

# Store test jobs
test_jobs = {}


class TestRequest(BaseModel):
    """Test request model"""
    url: HttpUrl
    task_description: Optional[str] = ""
    run_comprehensive_tests: bool = True
    headless: bool = True


class TestResponse(BaseModel):
    """Test response model"""
    job_id: str
    status: str
    message: str


class TestResult(BaseModel):
    """Test result model"""
    job_id: str
    status: str
    url: str
    test_results: Optional[Dict] = None
    pdf_path: Optional[str] = None
    json_path: Optional[str] = None
    error: Optional[str] = None


async def run_test_job(job_id: str, url: str, task: str, run_tests: bool, headless: bool):
    """Background job to run tests with progress streaming"""
    try:
        test_jobs[job_id]['status'] = 'running'
        await progress_streamer.broadcast(job_id, "status", "Test job started", 5)

        # Setup browser
        browser_config = BrowserConfig(
            headless=headless,
            chrome_remote_debugging_port=9222,
            extra_browser_args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        browser = Browser(config=browser_config)
        context_config = BrowserContextConfig()
        context = await browser.new_context(config=context_config)
        await progress_streamer.broadcast(job_id, "status", "Browser initialized", 15)

        # Navigate
        page = await context.get_current_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        except Exception as nav_error:
            error_str = str(nav_error).lower()
            await context.close()
            await browser.close()
            if 'net::err_name_not_resolved' in error_str or 'dns' in error_str:
                raise RuntimeError(f"DNS resolution failed for {url}. Check the URL spelling and your internet connection.")
            elif 'timeout' in error_str:
                raise RuntimeError(f"Connection timed out for {url}. The site may be down or very slow.")
            elif 'net::err_connection_refused' in error_str:
                raise RuntimeError(f"Connection refused by {url}. The server may be down.")
            else:
                raise RuntimeError(f"Failed to navigate to {url}: {nav_error}")

        await progress_streamer.broadcast(job_id, "status", f"Navigated to {url}", 25)

        # Run tests if requested
        results = None
        pdf_path = None
        json_path = None

        if run_tests:
            tester = ComprehensiveTester(url, context)
            await progress_streamer.broadcast(job_id, "status", "Running comprehensive tests...", 35)
            results = await tester.run_all_tests()
            results['task_description'] = (task or '').strip()
            results['agent_logs'] = [
                f"API job started for URL: {url}",
                f"Requested task: {(task or 'general health check').strip()}"
            ]
            await progress_streamer.broadcast(job_id, "status", "Tests completed", 55)

            # Save results
            json_path = tester.save_results('test_results')
            await progress_streamer.broadcast(job_id, "status", "Running AI analysis...", 65)

            # AI Analysis
            ai_analyzer = AIAnalyzer()
            ai_insights = await ai_analyzer.analyze_results(results)
            await progress_streamer.broadcast(job_id, "status", "AI analysis complete", 75)

            # Generate Enhanced PDF
            screenshots_dir = Path("agent_screenshots")
            await progress_streamer.broadcast(job_id, "status", "Generating PDF report...", 85)
            pdf_generator = UltraEnhancedPDFGenerator(
                results=results,
                screenshots_dir=screenshots_dir,
                ai_insights=ai_insights
            )
            pdf_path = pdf_generator.generate(f"report_{job_id}.pdf")
            await progress_streamer.broadcast(job_id, "status", "PDF report generated", 95)

        # Cleanup
        await context.close()
        await browser.close()

        # Update job
        test_jobs[job_id].update({
            'status': 'completed',
            'test_results': results,
            'pdf_path': pdf_path,
            'json_path': json_path
        })

        await progress_streamer.broadcast(job_id, "complete", "All tests completed successfully!", 100)

    except Exception as e:
        test_jobs[job_id].update({
            'status': 'failed',
            'error': str(e)
        })
        await progress_streamer.broadcast(job_id, "error", str(e), 0)


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "WebSentinel API",
        "version": "1.1.0",
        "endpoints": {
            "POST /api/test": "Submit a new test job",
            "GET /api/test/{job_id}": "Get test job status and results",
            "GET /api/test/{job_id}/pdf": "Download PDF report",
            "GET /api/test/{job_id}/json": "Download JSON results",
            "WS /ws/test/{job_id}": "WebSocket live progress stream",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/test", response_model=TestResponse)
async def create_test(request: TestRequest, background_tasks: BackgroundTasks):
    """Create a new test job"""
    job_id = str(uuid.uuid4())

    test_jobs[job_id] = {
        'status': 'pending',
        'url': str(request.url),
        'task': request.task_description,
        'created_at': datetime.now().isoformat()
    }

    # Start background task
    background_tasks.add_task(
        run_test_job,
        job_id,
        str(request.url),
        request.task_description,
        request.run_comprehensive_tests,
        request.headless
    )

    return TestResponse(
        job_id=job_id,
        status="pending",
        message="Test job created successfully. Connect to /ws/test/{job_id} for live progress."
    )


@app.get("/api/test/{job_id}", response_model=TestResult)
async def get_test_result(job_id: str):
    """Get test result by job ID"""
    if job_id not in test_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = test_jobs[job_id]

    return TestResult(
        job_id=job_id,
        status=job['status'],
        url=job['url'],
        test_results=job.get('test_results'),
        pdf_path=job.get('pdf_path'),
        json_path=job.get('json_path'),
        error=job.get('error')
    )


@app.get("/api/test/{job_id}/pdf")
async def download_pdf(job_id: str):
    """Download PDF report"""
    if job_id not in test_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = test_jobs[job_id]

    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Test not completed yet")

    pdf_path = job.get('pdf_path')
    if not pdf_path or not Path(pdf_path).exists():
        raise HTTPException(status_code=404, detail="PDF report not found")

    return FileResponse(
        pdf_path,
        media_type='application/pdf',
        filename=Path(pdf_path).name
    )


@app.get("/api/test/{job_id}/json")
async def download_json(job_id: str):
    """Download JSON results"""
    if job_id not in test_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = test_jobs[job_id]

    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Test not completed yet")

    json_path = job.get('json_path')
    if not json_path or not Path(json_path).exists():
        raise HTTPException(status_code=404, detail="JSON results not found")

    return FileResponse(
        json_path,
        media_type='application/json',
        filename=Path(json_path).name
    )


@app.delete("/api/test/{job_id}")
async def delete_test(job_id: str):
    """Delete a test job"""
    if job_id not in test_jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    del test_jobs[job_id]
    return {"message": "Job deleted successfully"}


# ──────────────────────────────────────────────────────────────
# WebSocket Endpoint for Live Progress
# ──────────────────────────────────────────────────────────────

@app.websocket("/ws/test/{job_id}")
async def websocket_test_progress(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for live test progress streaming.

    Connect to ws://host:port/ws/test/{job_id} after creating a test job.
    Messages are JSON objects: {"event": "status|complete|error", "data": "...", "progress": 0-100}
    """
    await progress_streamer.connect(job_id, websocket)
    try:
        # Send current status immediately
        if job_id in test_jobs:
            job = test_jobs[job_id]
            await websocket.send_text(json.dumps({
                "event": "connected",
                "data": f"Connected to job {job_id}. Status: {job['status']}",
                "progress": 0,
                "timestamp": datetime.now().isoformat()
            }))
        else:
            await websocket.send_text(json.dumps({
                "event": "error",
                "data": f"Job {job_id} not found",
                "progress": 0,
                "timestamp": datetime.now().isoformat()
            }))

        # Keep the connection alive until client disconnects
        while True:
            # Wait for any messages from client (e.g. ping)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"event": "pong"}))
    except WebSocketDisconnect:
        pass
    finally:
        progress_streamer.disconnect(job_id, websocket)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting WebSentinel API Server...")
    print("📡 API will be available at http://localhost:8000")
    print("📚 API documentation at http://localhost:8000/docs")
    print("🔌 WebSocket live streaming at ws://localhost:8000/ws/test/{job_id}")
    print()

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
