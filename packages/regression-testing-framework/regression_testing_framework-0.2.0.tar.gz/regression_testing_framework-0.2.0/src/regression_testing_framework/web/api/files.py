"""
File browsing API endpoints for test runs.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from datetime import datetime

router = APIRouter()

def parse_test_report(report_path: str) -> Dict:
    """Parse a test_report.txt file and extract summary information."""
    if not os.path.exists(report_path):
        return {"error": "Report file not found"}
    
    try:
        with open(report_path, 'r') as f:
            content = f.read()
        
        # Extract test results
        passed_match = re.search(r'Tests passed: (\d+)/(\d+) \(([^)]+)\)', content)
        if passed_match:
            passed = int(passed_match.group(1))
            total = int(passed_match.group(2))
            percentage = passed_match.group(3)
        else:
            passed = total = 0
            percentage = "0%"
        
        # Extract individual test results
        tests = []
        test_section = re.search(r'Test Results:\n(.*?)\n\nLog Files:', content, re.DOTALL)
        if test_section:
            for line in test_section.group(1).strip().split('\n'):
                if ': ' in line and not line.startswith('  '):
                    test_name, status = line.split(': ', 1)
                    tests.append({
                        "name": test_name.strip(),
                        "status": status.strip()
                    })
        
        return {
            "passed": passed,
            "total": total,
            "failed": total - passed,
            "percentage": percentage,
            "tests": tests
        }
    except Exception as e:
        return {"error": f"Failed to parse report: {str(e)}"}

def get_run_summary(run_dir: str) -> Dict:
    """Get summary information for a test run directory."""
    run_path = Path(run_dir)
    
    if not run_path.exists():
        return {"error": "Run directory not found"}
    
    # Parse timestamp from directory name
    dir_name = run_path.name
    timestamp_match = re.match(r'run_(\d{8}_\d{6})', dir_name)
    if timestamp_match:
        timestamp_str = timestamp_match.group(1)
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
        except ValueError:
            timestamp = None
    else:
        timestamp = None
    
    # Count log files
    log_files = list(run_path.glob("*.log"))
    pass_files = [f for f in log_files if "_PASS.log" in f.name]
    fail_files = [f for f in log_files if "_FAIL.log" in f.name]
    
    # Try to parse test report
    report_path = run_path / "test_report.txt"
    report_data = parse_test_report(str(report_path))
    
    return {
        "name": dir_name,
        "timestamp": timestamp.isoformat() if timestamp else None,
        "log_files": len(log_files),
        "passed": len(pass_files) if "error" in report_data else report_data.get("passed", len(pass_files)),
        "failed": len(fail_files) if "error" in report_data else report_data.get("failed", len(fail_files)),
        "total": len(log_files) if "error" in report_data else report_data.get("total", len(log_files)),
        "percentage": report_data.get("percentage", f"{len(pass_files)}/{len(log_files)}" if log_files else "0/0"),
        "has_report": report_path.exists(),
        "report_data": report_data if "error" not in report_data else None
    }

@router.get("/runs", response_class=HTMLResponse)
async def list_test_runs(limit: int = 50):
    """List all test run directories with summary information."""
    test_runs_dir = Path("test_runs")
    
    if not test_runs_dir.exists():
        raise HTTPException(status_code=404, detail="Test runs directory not found")
    
    runs = []
    run_dirs = [d for d in test_runs_dir.iterdir() if d.is_dir() and d.name != "latest"]
    
    # Sort by timestamp (newest first)
    run_dirs.sort(key=lambda x: x.name, reverse=True)
    
    for run_dir in run_dirs[:limit]:
        summary = get_run_summary(str(run_dir))
        runs.append(summary)
    
    # Return HTML for HTMX
    if not runs:
        return HTMLResponse("""<div class="empty">No test runs found</div>""")
    
    html = '<div class="run-list">'
    for run in runs:
        timestamp_str = run.get('timestamp', '')
        timestamp_display = f'data-iso="{timestamp_str}"' if timestamp_str else ''
        
        html += f'''<div class="run-item" data-run-name="{run['name']}">
            <div class="run-header">
                <div class="run-name">{run['name']}</div>
                <div class="run-timestamp" {timestamp_display}>
                    {timestamp_str[:19].replace('T', ' ') if timestamp_str else 'Unknown'}
                </div>
            </div>
            <div class="run-stats">
                <div class="stat passed">✅ {run['passed']} passed</div>
                <div class="stat failed">❌ {run['failed']} failed</div>
                <div class="stat total">📊 {run['total']} total</div>
                <div class="stat">📁 {run['log_files']} files</div>
            </div>
        </div>'''
    html += '</div>'
    return HTMLResponse(html)

@router.get("/runs/{run_name}", response_class=HTMLResponse)
async def get_test_run_details(run_name: str):
    """Get detailed information about a specific test run."""
    run_path = Path("test_runs") / run_name
    
    if not run_path.exists():
        raise HTTPException(status_code=404, detail="Test run not found")
    
    summary = get_run_summary(str(run_path))
    
    # List all files in the directory
    files = []
    for file_path in run_path.iterdir():
        if file_path.is_file():
            files.append({
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "type": "log" if file_path.suffix == ".log" else "text" if file_path.suffix == ".txt" else "other",
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
    
    files.sort(key=lambda x: x["name"])
    
    # Return HTML for HTMX
    html = f'''<h3>📋 {run_name}</h3>
    <div class="summary-grid">
        <div class="summary-card">
            <div class="number">{summary['passed']}</div>
            <div class="label">Passed</div>
        </div>
        <div class="summary-card">
            <div class="number">{summary['failed']}</div>
            <div class="label">Failed</div>
        </div>
        <div class="summary-card">
            <div class="number">{summary['total']}</div>
            <div class="label">Total</div>
        </div>
        <div class="summary-card">
            <div class="number">{len(files)}</div>
            <div class="label">Files</div>
        </div>
    </div>'''
    
    if summary.get('report_data') and summary['report_data'].get('tests'):
        html += '<h4>Test Results</h4><div class="test-results">'
        for test in summary['report_data']['tests']:
            status_icon = '✅' if test['status'] == 'PASS' else '❌'
            html += f'<div class="test-result">{status_icon} <strong>{test["name"]}</strong>: {test["status"]}</div>'
        html += '</div>'
    
    if files:
        html += '<h4>📁 Files</h4><div class="file-list">'
        for file in files:
            size_str = f"{file['size']} bytes" if file['size'] < 1024 else f"{file['size']/1024:.1f} KB"
            html += f'''<div class="file-item" data-file-name="{file['name']}">
                <div>
                    <div class="file-name">{file['name']}</div>
                    <div class="file-meta">{size_str}</div>
                </div>
                <div class="file-type {file['type']}">{file['type']}</div>
            </div>'''
        html += '</div>'
    else:
        html += '<div class="empty">No files found</div>'
    
    return html

@router.get("/runs/{run_name}/files/{file_name}")
async def read_test_file(run_name: str, file_name: str):
    """Read the contents of a specific file in a test run."""
    file_path = Path("test_runs") / run_name / file_name
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    if not file_path.is_file():
        raise HTTPException(status_code=400, detail="Path is not a file")
    
    # Check file size to prevent reading huge files
    file_size = file_path.stat().st_size
    if file_size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=413, detail="File too large to read")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "name": file_name,
            "size": file_size,
            "content": content,
            "type": "log" if file_path.suffix == ".log" else "text" if file_path.suffix == ".txt" else "other"
        }
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not text-readable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@router.get("/summary", response_class=HTMLResponse)
async def get_overall_summary():
    """Get overall summary statistics across all test runs."""
    test_runs_dir = Path("test_runs")
    
    if not test_runs_dir.exists():
        return HTMLResponse("""<div class="empty">Test runs directory not found</div>""")
    
    run_dirs = [d for d in test_runs_dir.iterdir() if d.is_dir() and d.name != "latest"]
    
    total_runs = len(run_dirs)
    total_tests = 0
    total_passed = 0
    total_failed = 0
    recent_runs = []
    
    # Sort by timestamp and get recent runs
    run_dirs.sort(key=lambda x: x.name, reverse=True)
    
    for run_dir in run_dirs[:10]:  # Last 10 runs
        summary = get_run_summary(str(run_dir))
        recent_runs.append(summary)
        
        if "error" not in summary:
            total_tests += summary.get("total", 0)
            total_passed += summary.get("passed", 0)
            total_failed += summary.get("failed", 0)
    
    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
    
    # Return HTML for HTMX
    html = f'''<div class="summary-grid">
        <div class="summary-card">
            <div class="number">{total_runs}</div>
            <div class="label">Total Runs</div>
        </div>
        <div class="summary-card">
            <div class="number">{total_tests}</div>
            <div class="label">Total Tests</div>
        </div>
        <div class="summary-card">
            <div class="number">{total_passed}</div>
            <div class="label">Tests Passed</div>
        </div>
        <div class="summary-card">
            <div class="number">{total_failed}</div>
            <div class="label">Tests Failed</div>
        </div>
        <div class="summary-card">
            <div class="number">{success_rate:.1f}%</div>
            <div class="label">Success Rate</div>
        </div>
    </div>'''
    
    if recent_runs:
        html += '<h3>📅 Recent Runs</h3><div class="recent-runs">'
        for run in recent_runs[:5]:
            status_color = "#059669" if run['failed'] == 0 else "#dc2626" if run['passed'] == 0 else "#d97706"
            html += f'''<div style="display: flex; justify-content: space-between; padding: 8px; border-bottom: 1px solid #e5e7eb;">
                <span>{run['name']}</span>
                <span style="color: {status_color};">
                    {run['passed']}/{run['total']} ({run['percentage']})
                </span>
            </div>'''
        html += '</div>'
    
    return HTMLResponse(html)