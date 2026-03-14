#!/usr/bin/env python3
"""Agent Detector - Detect agent activity reliably without agent cooperation."""
import os, subprocess, json, time
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict

_AGENT_CONFIG = [
    {"id": "main", "name": "Alex", "emoji": "🦾", "role": "Main", "workspace": "workspace-dev"},
    {"id": "coding", "name": "ByteSmeden", "emoji": "⚒️", "role": "Coding", "workspace": "workspace-coding"},
    {"id": "architect", "name": "Archistrukt", "emoji": "🏗️", "role": "Architect", "workspace": "workspace-architect"},
    {"id": "ops", "name": "Orion", "emoji": "⭐", "role": "Ops", "workspace": "workspace-ops"},
    {"id": "tester", "name": "Testvakten", "emoji": "🧪", "role": "Tester", "workspace": "workspace-tester"},
]

@dataclass
class AgentStatus:
    id: str; name: str; emoji: str; role: str; workspace: str; status: str
    last_activity: str = None; last_activity_seconds: int = 0
    current_task: str = None; confidence: str = "high"
    def to_dict(self): return asdict(self)

class AgentDetector:
    def __init__(self, base="/home/bjwl/.openclaw"):
        self.base = Path(base).expanduser()
        self.idle_threshold = 120
        self._gateway_pid = None
    def _pid_exists(self, pid):
        try: os.kill(pid, 0); return True
        except: return False
    def get_gateway_pid(self):
        if self._gateway_pid and self._pid_exists(self._gateway_pid): return self._gateway_pid
        try:
            r = subprocess.run(["pgrep", "-f", "openclaw-gateway"], capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                for line in r.stdout.strip().splitlines():
                    if line.strip().isdigit():
                        self._gateway_pid = int(line.strip()); return self._gateway_pid
        except: pass
        try:
            r = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=3)
            for line in r.stdout.splitlines():
                if "openclaw-gateway" in line and "grep" not in line:
                    parts = line.split()
                    if len(parts) > 1:
                        try: self._gateway_pid = int(parts[1]); return self._gateway_pid
                        except: pass
        except: pass
        return None
    def get_gateway_cwd(self):
        pid = self.get_gateway_pid()
        if not pid: return None
        try:
            r = subprocess.run(["lsof", "-a", "-p", str(pid), "-d", "cwd"], capture_output=True, text=True, timeout=3)
            if r.returncode == 0:
                lines = r.stdout.strip().splitlines()
                for line in lines[1:]:
                    parts = line.split()
                    if len(parts) >= 9: return Path(parts[-1])
        except: pass
        try:
            cwd = os.readlink(f"/proc/{pid}/cwd")
            return Path(cwd)
        except: pass
        return None
    def get_memory_activity(self, agent_id):
        agent = next((a for a in _AGENT_CONFIG if a["id"] == agent_id), None)
        if not agent: return None
        memory_dir = self.base / agent["workspace"] / "memory"
        latest = 0
        if memory_dir.exists():
            try:
                for f in memory_dir.glob("*.md"):
                    mtime = f.stat().st_mtime
                    if mtime > latest: latest = mtime
            except: pass
        status_file = self.base / agent["workspace"] / ("cyberdeck/main_status.json" if agent_id=="main" else "main_status.json")
        status_data = None; status_time = 0
        if status_file.exists():
            try:
                status_time = status_file.stat().st_mtime
                with open(status_file) as f: status_data = json.load(f)
            except: pass
        if status_time > latest: latest = status_time
        if latest == 0: return None
        return {
            "last_activity": datetime.fromtimestamp(latest).strftime("%d %b %H:%M") if latest else None,
            "last_activity_seconds": int(time.time() - latest) if latest else 999999,
            "task": status_data.get("task") if status_data else None,
        }
    def get_agent_status(self, agent_id):
        agent = next((a for a in _AGENT_CONFIG if a["id"] == agent_id), None)
        if not agent:
            return AgentStatus(id=agent_id, name="Unknown", emoji="?", role="Unknown", workspace="unknown", status="unknown")
        gateway_cwd = self.get_gateway_cwd()
        cwd_active = gateway_cwd and agent["workspace"] in str(gateway_cwd)
        mem = self.get_memory_activity(agent_id) or {}
        last_secs = mem.get("last_activity_seconds", 999999)
        status = "idle"; confidence = "high"; task = None
        if cwd_active:
            status = "active"; confidence = "high"
            task = mem.get("task", "Active in gateway")
            last_secs = 0
            mem["last_activity"] = datetime.now().strftime("%H:%M")
            mem["last_activity_seconds"] = 0
        elif last_secs < self.idle_threshold:
            status = "active"; confidence = "medium"
            task = mem.get("task", "Recent activity")
        else:
            confidence = "medium" if last_secs < 600 else "low"
        return AgentStatus(
            id=agent["id"], name=agent["name"], emoji=agent["emoji"],
            role=agent["role"], workspace=agent["workspace"], status=status,
            last_activity=mem.get("last_activity"), last_activity_seconds=last_secs,
            current_task=task, confidence=confidence
        )
    def get_all_agents(self): return [self.get_agent_status(a["id"]).to_dict() for a in _AGENT_CONFIG]
    def get_active_agents(self): return [a for a in self.get_all_agents() if a["status"] == "active"]
    def get_summary(self):
        agents = self.get_all_agents()
        active = [a for a in agents if a["status"] == "active"]
        gateway_cwd = self.get_gateway_cwd()
        current_owner = None
        if gateway_cwd:
            for a in _AGENT_CONFIG:
                if a["workspace"] in str(gateway_cwd): current_owner = a["id"]; break
        return {
            "timestamp": datetime.now().strftime("%H:%M"),
            "gateway_pid": self.get_gateway_pid(),
            "gateway_cwd": str(gateway_cwd) if gateway_cwd else None,
            "current_owner": current_owner,
            "active_count": len(active),
            "active_agents": active,
            "all_agents": agents,
        }

_detector = None
def get_detector():
    global _detector
    if _detector is None: _detector = AgentDetector()
    return _detector
def get_all_agents(): return get_detector().get_all_agents()
def get_active_agents(): return get_detector().get_active_agents()
def get_summary(): return get_detector().get_summary()

if __name__ == "__main__":
    d = AgentDetector()
    print("=== Agent Detector ===")
    print(f"Gateway PID: {d.get_gateway_pid()}")
    print(f"Gateway CWD: {d.get_gateway_cwd()}")
    print()
    for aid in ["main", "ops", "coding", "architect", "tester"]:
        s = d.get_agent_status(aid)
        print(f"{s.emoji} {s.name}: {s.status.upper()} (confidence: {s.confidence})")
    print(f"\nActive agents: {len(d.get_active_agents())}")
