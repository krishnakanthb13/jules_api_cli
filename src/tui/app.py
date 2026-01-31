from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Button, DataTable, Label
from textual.binding import Binding

from ..jules_client import get_client

class SessionList(Static):
    """Widget to display list of sessions."""
    
    def compose(self) -> ComposeResult:
        yield Label("Sessions", id="sessions-header")
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
            data = client.get("sessions", {"pageSize": 20})
            sessions = data.get("sessions", [])
            
            for s in sessions:
                table.add_row(
                    s.get("id"),
                    s.get("title", "Untitled"),
                    s.get("state"),
                    s.get("createTime", "")[:10]
                )
        except Exception as e:
            pass

class JulesTUI(App):
    """Jules API CLI Terminal UI."""
    
    CSS = """
    Screen {
        layout: horizontal;
    }
    
    #sidebar {
        width: 30%;
        height: 100%;
        background: $panel;
        border-right: solid $primary;
    }
    
    #content {
        width: 70%;
        height: 100%;
    }
    
    #sessions-header {
        text-align: center;
        background: $primary;
        color: $text;
        width: 100%;
        padding: 1;
    }
    
    DataTable {
        height: 100%;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(SessionList(), id="sidebar")
        yield Container(Label("Select a session to view details", id="placeholder"), id="content")
        yield Footer()

    def action_refresh(self) -> None:
        self.query_one(SessionList).load_sessions()

def run_tui():
    app = JulesTUI()
    app.run()
