import os
from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    DirectoryTree,
    Button,
    Static,
    Input,
    Label,
)
from textual.screen import Screen
from textual.events import Mount

class FileBrowser(Screen):
    """A file browser screen for selecting files or directories."""
    
    BINDINGS = [("escape", "cancel", "Cancel")]
    
    def __init__(self, select_dir: bool = False, name: str | None = None, id: str | None = None, classes: str | None = None) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.select_dir = select_dir
        self.selected_path = None
        
    def compose(self) -> ComposeResult:
        yield Container(
            Static("📁 File Browser", classes="browser-title"),
            Horizontal(
                Button("⬆️ Up", id="up-dir", variant="default"),
                Button("🏠 Home", id="home-dir", variant="default"),
                Button("📂 Select Current Dir", id="select-current", variant="primary"),
                classes="browser-controls",
            ),
            Container(
                DirectoryTree(Path.cwd(), id="directory-tree"),
                classes="directory-container",
            ),
            Horizontal(
                Button("✅ Select", id="select-file", variant="primary"),
                Button("❌ Cancel", id="cancel", variant="default"),
                classes="browser-actions",
            ),
            classes="file-browser-container",
        )
    
    def on_mount(self) -> None:
        """Initialize the file browser."""
        directory_tree = self.query_one("#directory-tree", DirectoryTree)
        directory_tree.path = os.path.dirname(os.path.realpath(__file__))
        directory_tree.reload()
        directory_tree.focus()
        
        # Hide select current directory button if not in directory selection mode
        select_current_btn = self.query_one("#select-current", Button)
        if not self.select_dir:
            select_current_btn.display = False
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection."""
        if not self.select_dir:
            self.selected_path = event.path
            self.dismiss(self.selected_path)
    
    def on_directory_tree_directory_selected(self, event: DirectoryTree.DirectorySelected) -> None:
        """Handle directory selection."""
        if self.select_dir:
            self.selected_path = event.path
            self.dismiss(self.selected_path)
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        directory_tree = self.query_one("#directory-tree", DirectoryTree)
        
        if event.button.id == "up-dir":
            current_path = Path(directory_tree.path)
            parent_path = current_path.parent
            if parent_path != current_path:
                directory_tree.path = parent_path
                directory_tree.reload()
        
        elif event.button.id == "home-dir":
            home_path = Path.home()
            directory_tree.path = home_path
            directory_tree.reload()
        
        elif event.button.id == "select-current":
            if self.select_dir:
                current_path = Path(directory_tree.path)
                self.selected_path = current_path
                self.dismiss(self.selected_path)
        
        elif event.button.id == "select-file":
            # Get the currently highlighted/selected item
            highlighted_node = directory_tree.cursor_node
            if highlighted_node:
                node_path = highlighted_node.data.path
                if self.select_dir and node_path.is_dir():
                    self.selected_path = node_path
                    self.dismiss(self.selected_path)
                elif not self.select_dir and node_path.is_file():
                    self.selected_path = node_path
                    self.dismiss(self.selected_path)
        
        elif event.button.id == "cancel":
            self.dismiss(None)
    
    def action_cancel(self) -> None:
        """Cancel file selection."""
        self.dismiss(None)

