import concurrent.futures
import subprocess
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Button, DataTable, Label, Markdown, ContentSwitcher, TabbedContent, TabPane
from textual.binding import Binding
from textual.message import Message

from rich.syntax import Syntax
from rich.table import Table

from ..jules_client import get_client

class SessionSelected(Message):
    """Message sent when a session is selected."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        super().__init__()

class SessionList(Static):
    """Widget to display list of sessions."""
    
    def compose(self) -> ComposeResult:
        yield Label("Sessions (Press Enter to view)", id="sessions-header")
        yield DataTable(id="sessions-table")

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Title", "State", "Created")
        table.cursor_type = "row"
        self.load_sessions()

    def load_sessions(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        
        try:
            client = get_client()
            data = client.get("sessions", {"pageSize": 30})
            sessions = data.get("sessions", [])
            
            for s in sessions:
                table.add_row(
                    s.get("id"),
                    s.get("title", s.get("name", "Untitled")),
                    s.get("state"),
                    s.get("createTime", "")[:10],
                    key=s.get("name") # Use full resource name as key
                )
        except Exception as e:
            pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.row_key:
            # event.row_key is session name "projects/.../sessions/UUID"
            # Extract UUID
            session_id = str(event.row_key.value).split("/")[-1]
            self.post_message(SessionSelected(session_id))

class SessionDetails(Static):
    """Details view for a session."""
    
    session_id: str = ""

    def compose(self) -> ComposeResult:
        with TabbedContent(initial="info"):
            with TabPane("Info", id="info"):
                yield Markdown("Select a session...", id="session-markdown")
            with TabPane("Activities", id="activalies"):
                yield DataTable(id="activities-table")
            with TabPane("Diff", id="diff"):
                yield ScrollableContainer(Static("Diff View (Requires Git)", id="diff-content"))

    def load_session(self, session_id: str) -> None:
        self.session_id = session_id
        client = get_client()
        
        # 1. Load Info
        try:
            data = client.get(f"sessions/{session_id}")
            md = f"""
# {data.get('title', 'Untitled')}
**ID**: {data.get('id')}
**State**: {data.get('state')}
**Prompt**:
{data.get('prompt')}
            """
            
            # Check for PR/Branch
            branch_name = None
            outputs = data.get("outputs", [])
            for out in outputs:
                pr = out.get("pullRequest", {})
                if pr.get("branchName"):
                    branch_name = pr.get("branchName")
                    md += f"\n**Branch**: `{branch_name}`"
            
            self.query_one("#session-markdown", Markdown).update(md)
            
            # 2. Load Diff asynchronously if branch exists
            if branch_name:
                self.load_diff(branch_name)
            else:
                self.query_one("#diff-content", Static).update("No branch associated with this session.")

        except Exception as e:
            self.query_one("#session-markdown", Markdown).update(f"Error loading session: {e}")

        # 3. Load Activities
        self.load_activities(session_id)

    def load_activities(self, session_id: str) -> None:
        table = self.query_one("#activities-table", DataTable)
        table.clear(columns=True)
        table.add_columns("Type", "Message")
        
        try:
            client = get_client()
            activities = list(client.paginate(f"sessions/{session_id}/activities", page_size=20))
            for act in activities:
                kind = act.get("type", "unknown")
                msg = "..."
                if "userMessage" in act:
                     msg = act["userMessage"].get("prompt", "")
                elif "agentMessage" in act:
                     msg = act["agentMessage"].get("prompt", "")
                elif "planGenerated" in act:
                     msg = "(Plan Generated)"
                
                table.add_row(kind, msg[:100])
        except:
             pass

    def load_diff(self, branch: str) -> None:
        """Fetch remote branch and show diff."""
        diff_widget = self.query_one("#diff-content", Static)
        diff_widget.update(f"Fetching diff for branch: {branch}...")
        
        def _fetch_diff():
            try:
                # git fetch
                subprocess.check_output(["git", "fetch", "origin", branch], stderr=subprocess.DEVNULL)
                # git diff main...origin/branch
                diff_output = subprocess.check_output(
                    ["git", "diff", f"main...origin/{branch}"], 
                    encoding="utf-8"
                )
                return diff_output
            except Exception as e:
                return f"Error fetching diff: {e}"

        def _update_ui(diff_text):
            if not diff_text.strip():
                diff_widget.update("No changes found.")
            else:
                syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
                diff_widget.update(syntax)

        # Basic async
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(_fetch_diff)
            # Blocking for simplest implementation in TUI, purely for demo
            # In a real async Textual app, checking future status or using work_manager is better
            try:
                res = future.result(timeout=5)
                _update_ui(res)
            except:
                diff_widget.update("Timeout fetching diff.")


class JulesTUI(App):
    """Jules API CLI Terminal UI."""
    
    CSS = """
    Screen {
        layout: horizontal;
    }
    
    #sidebar {
        width: 30%;
        height: 100%;
        background: $surface;
        border-right: solid $primary;
    }
    
    #content {
        width: 70%;
        height: 100%;
        padding: 1;
    }
    
    #sessions-header {
        text-align: center;
        background: $primary;
        color: $text;
        width: 100%;
        padding: 1;
        text-style: bold;
    }
    
    Markdown {
        padding: 1;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container(SessionList(), id="sidebar")
        yield Container(SessionDetails(), id="content")
        yield Footer()

    def action_refresh(self) -> None:
        self.query_one(SessionList).load_sessions()

    def on_session_selected(self, message: SessionSelected) -> None:
        self.query_one(SessionDetails).load_session(message.session_id)

def run_tui():
    app = JulesTUI()
    app.run()
