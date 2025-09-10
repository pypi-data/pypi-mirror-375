import os
import json
import re
from datetime import datetime
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, Grid, Center
from textual.events import Mount, Click
from textual.widgets import (
    Header,
    Footer,
    DirectoryTree,
    Button,
    Static,
    Markdown,
    ListView,
    ListItem,
    DataTable,
    Input,
    TextArea,
    Select,
)
from textual.screen import Screen
from pathlib import Path
from .core import slice_slides
from .file_browser import FileBrowser


def sanitize_id(text: str) -> str:
    """Sanitizes a string to be used as a Textual widget ID."""
    sanitized = re.sub(r"[^a-zA-Z0-9_-]", "_", text)
    if sanitized and sanitized[0].isdigit():
        sanitized = f"_{sanitized}"
    return sanitized


class EditorScreen(Screen):
    BINDINGS = [("escape", "cancel", "Cancel"), ("ctrl+s", "save", "Save")]

    def __init__(
        self,
        file_path: str,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.file_path = file_path
        self.original_content = ""

    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"✏️ Editing: {Path(self.file_path).name}", classes="title"),
            TextArea(id="editor-content", classes="editor-textarea"),
            Horizontal(
                Button("💾 Save", id="save-edit", variant="primary"),
                Button("❌ Cancel", id="cancel-edit", variant="default"),
                classes="button-container",
            ),
            classes="editor-container",
        )

    def on_mount(self) -> None:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                self.original_content = f.read()
            self.query_one("#editor-content", TextArea).text = self.original_content
        except Exception as e:
            self.notify(f"Error loading file: {str(e)}", severity="error")
            self.app.pop_screen()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-edit":
            self.save_content()
        elif event.button.id == "cancel-edit":
            self.action_cancel()

    def action_cancel(self) -> None:
        """Cancel editing"""
        self.app.exit()

    def save_content(self) -> None:
        """Save the edited content to the file"""
        new_content = self.query_one("#editor-content", TextArea).text
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            self.notify(f"File '{Path(self.file_path).name}' saved successfully!")

            # Update project preview if it exists in projects.json
            projects_data = {"projects": []}
            if os.path.exists("projects.json"):
                try:
                    with open("projects.json", "r") as f:
                        projects_data = json.load(f)
                except json.JSONDecodeError:
                    projects_data = {"projects": []}
            for project in projects_data.get("projects", []):
                if project["file_path"] == self.file_path:
                    project["preview"] = (
                        new_content[:100] + "..."
                        if len(new_content) > 100
                        else new_content
                    )
                    project["file_size"] = (
                        f"{os.path.getsize(self.file_path) / 1024:.2f} KB"
                    )
                    break

            with open("projects.json", "w") as f:
                json.dump(projects_data, f, indent=4)

            # # Refresh home screen if it's active
            # home_screen = self.app.get_screen("home")
            # if home_screen:
            #     home_screen.update_project_widgets()
            # self.app.pop_screen()
            
            self.app.exit()
        except Exception as e:
            self.notify(f"Error saving file: {str(e)}", severity="error")


class NewPresentationScreen(Screen):
    BINDINGS = [("escape", "cancel", "Cancel"), ("ctrl+s", "save", "Save")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Center(
            Container(
                Static("📝 Create New Presentation", classes="title"),
                Container(
                    Vertical(
                        Horizontal(  # Project Name row
                            Static("Project Name:", classes="label-right"),
                            Input(
                                placeholder="my_presentation",
                                id="file-name",
                                classes="input-with-label",
                            ),
                            classes="form-row",
                        ),
                        Horizontal(  # File path row
                            Static("File Path:", classes="label-right"),
                            Input(
                                placeholder="./my_presentation.md",
                                id="file-path",
                                classes="input-with-label",
                            ),
                            classes="form-row",
                        ),
                        classes="details-container",
                    ),
                ),
                Horizontal(
                    Button("💾 Save & Edit", id="save-edit", variant="primary"),
                    Button("❌ Exit", id="exit", variant="default"),
                    classes="button-container",
                ),
                classes="new-presentation-container",
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        """Set initial file path to current directory"""
        current_dir = os.getcwd()
        self.query_one("#file-path", Input).value = os.path.join(
            current_dir, "presentation.md"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "save-edit":
            self.save_and_edit_presentation()
        elif event.button.id == "exit":
            self.action_exit()

    def action_exit(self) -> None:
        """Exit presentation creation"""
        self.app.pop_screen()

    def save_and_edit_presentation(self) -> None:
        """Save the presentation and open in editor"""
        project_name = self.query_one("#file-name").value
        file_path = self.query_one("#file-path").value

        # Validate inputs
        if not project_name:
            self.notify("Project name cannot be empty!", severity="error")
            return

        if not file_path:
            self.notify("File path cannot be empty!", severity="error")
            return

        # Add .md extension if not present
        if not file_path.endswith(".md"):
            file_path += ".md"

        # Set default content
        content = f"# {project_name}\n\nYour presentation content here...\n\n---\n\n# Slide 2\n\nMore content..."

        try:
            # Create the file with initial content
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Get file info
            file_path_str = str(Path(file_path).resolve())
            file_size = f"{os.path.getsize(file_path_str) / 1024:.2f} KB"
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Create preview (first 100 characters)
            preview = content[:100] + "..." if len(content) > 100 else content

            # Load existing projects
            projects_data = {"projects": []}
            if os.path.exists("projects.json"):
                try:
                    with open("projects.json", "r") as f:
                        projects_data = json.load(f)
                except json.JSONDecodeError:
                    projects_data = {"projects": []}

            # Create new project entry
            new_project = {
                "file_name": Path(file_path).name,
                "file_path": file_path_str,
                "preview": preview,
                "created_at": created_at,
                "file_size": file_size,
                "theme": "default",
            }

            projects_data["projects"].append(new_project)

            # Save projects data
            with open("projects.json", "w") as f:
                json.dump(projects_data, f, indent=4)

            # Refresh home screen
            # home_screen = self.app.get_screen("home")
            # if home_screen:
            #     home_screen.projects = projects_data["projects"]
            #     home_screen.update_project_widgets()

            self.notify(f"Presentation '{project_name}' created successfully!")

            # Navigate to the EditorScreen for the newly created file
            self.app.push_screen(PresentationEngine(file_path_str))

        except Exception as e:
            self.notify(f"Error creating presentation: {str(e)}", severity="error")


class Home(Screen):
    BINDINGS = [
        ("o", "open_slide", "Open"),
        ("q", "quit", "Quit"),
        ("n", "new_presentation", "New"),
        ("e", "edit_project", "Edit"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.projects = []
        try:
            if os.path.exists("projects.json"):
                with open("projects.json") as f:
                    data = json.load(f)
                    if data and isinstance(data, dict) and "projects" in data:
                        self.projects = data["projects"]
                        self.projects = json.load(f).get("projects", [])
        except Exception:
            self.projects = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Container(
                Static("📽️ SlideDown", classes="sidebar-title"),
                ListView(
                    ListItem(Static("📂 Open File", classes="menu-item"), id="open"),
                    ListItem(
                        Static("🆕 New Presentation", classes="menu-item"), id="new"
                    ),
                    ListItem(Static("🚪 Quit", classes="menu-item"), id="quit"),
                    id="sidebar",
                    classes="sidebar-list",
                ),
                classes="sidebar-container",
            ),
            Container(
                Static("📚 Recent Presentations", classes="title-project-list"),
                Container(
                    id="recent-table",
                    classes="recent-projects-grid",
                ),
                classes="main-content",
            ),
            classes="main-layout",
        )
        yield Footer()
    def _create_project_widgets(self):
        project_cards = []
        if not self.projects:
            project_cards.append(
                Center(
                    Container(
                        Static(
                            "Create a new project to get started!",
                            classes="no-projects-message",
                        ),
                        Button(
                            "Create New Project",
                            id="no-projects-button",
                            classes="no-projects-button",
                        ),
                        classes="no-projects-container",
                    ),
                    classes="no-projects-center",
                )
            )
        else:
            for idx, project in enumerate(self.projects):
                unique_id = f"project-card-{idx}"
                project_cards.append(
                    Vertical(
                        Container(
                            Static(project["file_name"], classes="card-title"),
                            Static(project["created_at"], classes="card-date"),
                            Static(
                                project["preview"].split("\\n")[0],
                                classes="card-preview",
                            ),  # Display first line of preview
                            Horizontal(
                                Button(
                                    "Open", id=f"open-{idx}", classes="card-open-button"
                                ),
                                classes="card-actions",
                            ),
                            classes="card-info-container",
                        ),
                        classes="project-card",
                        id=unique_id,
                    )
                )
        return project_cards

    def action_new_presentation(self) -> None:
        """Create a new presentation"""
        self.app.push_screen(NewPresentationScreen())
    def on_mount(self) -> None:
        self.update_project_widgets()

    def update_project_widgets(self):
        try:
            if os.path.exists("projects.json"):
                with open("projects.json") as f:
                    self.projects = json.load(f).get("projects", [])
            else:
                self.projects = []
        except Exception:
            self.projects = []

        recent_table_container = self.query_one("#recent-table")
        recent_table_container.remove_children()
        recent_table_container.mount(*self._create_project_widgets())

    def on_click(self, event: Click) -> None:
        widget = event.widget
        while widget and not widget.has_class("project-card"):
            widget = widget.parent

        if widget and widget.id and widget.id.startswith("project-card-"):
            id_parts = widget.id.split("-", 2)
            if len(id_parts) >= 2:
                try:
                    idx = int(id_parts[1])
                    if 0 <= idx < len(self.projects):
                        original_file_path = self.projects[idx]["file_path"]
                        self.app.push_screen(PresentationEngine(original_file_path))
                except (ValueError, IndexError):
                    pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        # Handle the "Create New Project" button click
        if event.button.id == "no-projects-button":
            self.action_new_presentation()
        # Handle edit button clicks
        elif event.button.id and event.button.id.startswith("edit-"):
            try:
                idx = int(event.button.id.split("-")[1])
                if 0 <= idx < len(self.projects):
                    file_path = self.projects[idx]["file_path"]
                    self.app.push_screen(EditorScreen(file_path))
            except (ValueError, IndexError):
                pass
        # Handle open button clicks
        elif event.button.id and event.button.id.startswith("open-"):
            try:
                idx = int(event.button.id.split("-")[1])
                if 0 <= idx < len(self.projects):
                    file_path = self.projects[idx]["file_path"]
                    self.app.push_screen(PresentationEngine(file_path))
            except (ValueError, IndexError):
                pass

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item.id == "open":
            self.action_open_slide()
        elif event.item.id == "new":
            self.action_new_presentation()
        elif event.item.id == "edit":
            self.action_edit_project()
        elif event.item.id == "help":
            self.notify("Help feature coming soon!")
        elif event.item.id == "quit":
            self.action_quit()

    def action_open_slide(self) -> None:
        self.app.push_screen("file_browser")

    def action_new_presentation(self) -> None:
        self.app.push_screen(NewPresentationScreen())

    def action_edit_project(self) -> None:
        if self.projects:
            # Edit the most recent project
            file_path = self.projects[0]["file_path"]
            self.app.push_screen(EditorScreen(file_path))
        else:
            self.notify("No projects to edit!", severity="warning")

    def action_quit(self) -> None:
        self.app.exit()


class FileBrowser(Screen):
    BINDINGS = [("escape", "pop_screen", "Back")]

    def __init__(
        self,
        select_dir: bool = False,
        callback=None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.select_dir = select_dir
        self.callback = callback
        self.selected_path = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield DirectoryTree("./", id="dir-tree")
        yield Static("No file selected", id="status")
        yield Button(
            "Select" if self.select_dir else "Open",
            id="open",
            variant="primary",
            disabled=True,
        )
        yield Footer()

    def on_mount(self) -> None:
        self.selected_path = None

    def on_directory_tree_file_selected(
        self, event: DirectoryTree.FileSelected
    ) -> None:
        if not self.select_dir:
            self.selected_path = event.path
            self.query_one("#status").update(f"Selected: {event.path.name}")
            self.query_one("#open").disabled = False
        else:
            self.query_one("#status").update(
                f"Cannot select file in directory mode: {event.path.name}"
            )
            self.query_one("#open").disabled = True

    def on_directory_tree_directory_selected(
        self, event: DirectoryTree.DirectorySelected
    ) -> None:
        self.selected_path = event.path
        self.query_one("#status").update(f"Selected: {event.path.name}")
        self.query_one("#open").disabled = False

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "open" and self.selected_path:
            if self.select_dir and self.callback:
                self.callback(self.selected_path)
            elif not self.select_dir:
                file_path_str = str(self.selected_path)
                file_name = Path(file_path_str).name

                projects_data = {"projects": []}
                if os.path.exists("projects.json"):
                    try:
                        with open("projects.json", "r") as f:
                            projects_data = json.load(f)
                    except json.JSONDecodeError:
                        projects_data = {"projects": []}

                projects = projects_data.get("projects", [])
                project_exists = any(p["file_path"] == file_path_str for p in projects)

                if not project_exists:
                    try:
                        with open(file_path_str, "r", encoding="utf-8") as f:
                            content = f.read()
                            preview_content = (
                                content[:100] + "..." if len(content) > 100 else content
                            )
                    except Exception:
                        preview_content = "No preview available."

                    file_size = f"{os.path.getsize(file_path_str) / 1024:.2f} KB"
                    new_project = {
                        "file_name": file_name,
                        "file_path": file_path_str,
                        "preview": preview_content,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "file_size": file_size,
                        "theme": "default",
                    }
                    projects.append(new_project)

                    with open("projects.json", "w") as f:
                        json.dump({"projects": projects}, f, indent=4)

                    # home_screen = self.app.get_screen("home")
                    # home_screen.projects = projects
                    # home_screen.update_project_widgets()

                self.app.push_screen(PresentationEngine(file_path_str))


class PresentationEngine(Screen):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.slides = slice_slides(self.read_file_content())
        self.current_slide_index = 0

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("left", "prev_slide", "Previous Slide"),
        ("right", "next_slide", "Next Slide"),
        ("p", "play_button", "Play"),
        ("e", "edit", "Edit"),
    ]

    def on_mount(self) -> None:
        self.update_view(self.current_slide_index)

    def update_view(self, index: int) -> None:
        self.current_slide_index = index
        self.query_one("#slide-content").update(self.slides[self.current_slide_index])
        self.query_one("#slide-counter").update(
            f"{self.current_slide_index + 1}/{len(self.slides)}"
        )
        self.query_one("#prev-slide").disabled = self.current_slide_index == 0
        self.query_one("#next-slide").disabled = (
            self.current_slide_index == len(self.slides) - 1
        )

    def action_next_slide(self) -> None:
        if self.current_slide_index < len(self.slides) - 1:
            self.update_view(self.current_slide_index + 1)

    def action_prev_slide(self) -> None:
        if self.current_slide_index > 0:
            self.update_view(self.current_slide_index - 1)

    def action_edit(self) -> None:
        """Edit the current presentation"""
        self.app.push_screen(EditorScreen(self.file_path))

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Container(
                Static("Slides", classes="sidebar-title"),
                ListView(
                    id="sidebar",
                    classes="sidebar-list",
                    *[
                        ListItem(
                            Markdown(f"{slide}", classes="sidebar-item"),
                            id=f"slide-{idx}",
                        )
                        for idx, slide in enumerate(self.slides)
                    ],
                ),
                classes="sidebar-container",
            ),
            Container(
                Vertical(
                    Static(Path(self.file_path).name, classes="file-title"),
                    Markdown("", id="slide-content", classes="slide-content"),
                    classes="main-content",
                ),
                Container(
                    Static("", id="slide-counter", classes="slide-counter"),
                    Horizontal(
                        Button(
                            "Previous",
                            id="prev-slide",
                            variant="default",
                            disabled=True,
                        ),
                        Button("Next", id="next-slide", variant="primary"),
                        Button("Play", id="play", variant="primary"),
                        Button("Edit", id="edit", variant="default"),
                        classes="nav-buttons",
                    ),
                    classes="nav-container",
                ),
                classes="main-container",
            ),
            classes="main-layout",
        )
        yield Footer()

    def action_play_button(self) -> None:
        self.app.push_screen(PlayScreen(self.slides, self.current_slide_index))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "next-slide":
            self.action_next_slide()
        elif event.button.id == "prev-slide":
            self.action_prev_slide()
        elif event.button.id == "play":
            self.action_play_button()
        elif event.button.id == "edit":
            self.action_edit()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.id and event.item.id.startswith("slide-"):
            slide_index_str = event.item.id.split("-")[1]
            try:
                slide_index = int(slide_index_str)
                self.update_view(slide_index)
            except ValueError:
                pass

    def read_file_content(self):
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"


class PlayScreen(Screen):
    def __init__(self, slides: list[str], current_slide_index: int):
        super().__init__()
        self.slides = slides
        self.current_slide_index = current_slide_index

    BINDINGS = [
        ("escape", "pop_screen", "Back"),
        ("left", "prev_slide", "Previous Slide"),
        ("right", "next_slide", "Next Slide"),
    ]

    def compose(self) -> ComposeResult:
        yield Container(
            Markdown(
                self.slides[self.current_slide_index],
                id="play-slide-content",
                classes="play-slide-content",
            ),
            classes="play-screen-container",
        )

    def on_mount(self) -> None:
        
        self.update_view(self.current_slide_index)
        self.notify(
            "Slide controls:\n"
            "  - Left/Right arrow keys: Previous/Next slide\n"
            "  - Escape: Back to editor",
            timeout=3,
        )

    def update_view(self, index: int) -> None:
        self.current_slide_index = index
        self.query_one("#play-slide-content", Markdown).update(
            self.slides[self.current_slide_index]
        )

    def action_next_slide(self) -> None:
        if self.current_slide_index < len(self.slides) - 1:
            self.update_view(self.current_slide_index + 1)

    def action_prev_slide(self) -> None:
        if self.current_slide_index > 0:
            self.update_view(self.current_slide_index - 1)

    def action_pop_screen(self) -> None:
        self.app.pop_screen()


class SlideDownApp(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    
    /* Editor Screen */
    .editor-container {
        height: 1fr;
        max-width: 120;
        margin: 2 4;
        padding: 2 3;
        background: $surface;
        border: thick $primary;
        layout: vertical;
    }
    
    .editor-textarea {
        height: 1fr;
        width: 100%;
        margin: 1 0;
    }
    
    /* New Presentation Screen */
    .new-presentation-container {
        width: 90%;
        max-width: 80;
        height: auto;
        max-height: 90%;
        margin: 2;
        padding: 3;
        background: $surface;
        border: thick $primary;
        layout: vertical;
    }
    
    .title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 2;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }
    
    .section-title {
        text-style: bold;
        color: $secondary;
        margin: 1 0;
        padding-bottom: 1;
        border-bottom: solid $primary;
    }
    
    .details-container {
        margin-bottom: 2;
        layout: vertical;
    }
    
    .form-row {
        width: 100%;
        height: auto;
        margin-bottom: 1;
        align: left middle;
        layout: grid;
        grid-size: 2;
        grid-columns: 1fr 3fr;
        grid-gutter: 1;
    }
    .form-row .label-right {
        text-align: right;
        padding-right: 1;
        color: $text-muted;
    }
    .form-row .input-with-label {
        width: 100%;
    }
    .form-row .select {
        width: 100%;
    }
    .directory-input-container {
        column-span: 2;
        layout: grid;
        grid-size: 2;
        grid-columns: 3fr 1fr;
        grid-gutter: 1;
    }
    .directory-input-container Input {
        width: 100%;
    }
    .directory-input-container Button {
        width: 100%;
    }
    
    Input {
        width: 100%;
    }
    
    .select {
        width: 100%;
    }
    
    .slides-container {
        height: 1fr;
        margin-bottom: 2;
        min-height: 15;
    }
    
    .slides-textarea {
        height: 100%;
        width: 100%;
        border: solid $primary;
    }
    
    .directory-input-container {
        width: 100%;
    }
    
    .directory-input-container Input {
        width: 3fr;
    }
    
    .directory-input-container Button {
        width: 1fr;
    }
    
    .button-container {
        height: 18%;
        align: center middle;
    }
    
    /* Home Screen */
    .main-layout {
        height: 1fr;
        margin: 1 2;
    }
    
    .sidebar-container {
        width: 25%;
        height: 100%;
        background: $surface-darken-1;
        border-right: thick $primary;
        padding: 1;
    }
    
    .sidebar-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-bottom: 1;
        padding: 1 0;
        border-bottom: solid $primary;
    }
    
    .sidebar-list {
        height: 1fr;
    }
    
    .menu-item {
        padding: 1;
        margin-bottom: 1;
        background: $surface;
        border: solid $primary;
        color: $text;
    }
    
    .menu-item:hover {
        background: $primary-darken-1;
        color: $text;
    }
    
    .menu-item.selected {
        background: $primary;
        color: $text;
        text-style: bold;
    }
    
    .title-project-list {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 1 0;
        padding: 1 0;
        background: $surface-darken-1;
        border-bottom: solid $primary;
    }
    
    .main-content {
        height: 1fr;
        padding: 1;
    }
    
    .recent-projects-grid {
        layout: grid;
        grid-size: 4;
        grid-gutter: 2;
        width: 100%;
        height: 1fr;
        overflow-y: auto;
        padding: 2;
    }
    
    .project-card {
        border: solid $primary;
        background: $surface-darken-1;
        text-align: center;
        padding: 1;
        height: auto;
        min-height: 12;
        max-height: 20;
        overflow-y: auto;
    }
    .project-card:hover {
        background: $surface-darken-2;
        border: solid $surface;
    }
    
    .card-title {
        text-style: bold;
        color: $text;
        margin-bottom: 1;
        height: auto;
    }
    
    .card-date {
        color: $text-muted;
        margin-bottom: 1;
        height: auto;
    }
    .card-preview {
        color: $text-muted;
        text-align: left;
        padding: 0 1;
        height: 5;
        overflow-y: auto;
        text-overflow: ellipsis;
        margin-bottom: 1;
        
    }
    
    .card-actions {
        width: 100%;
        height: auto;
        align: center middle;
    }
    
    .card-like-button {
        color: $error;
        text-align: center;
        width: 3;
    }
    
    .edit-button {
        color: $warning;
        text-align: center;
        margin-left: 1;
        width: 3;
    }
    
    /* Presentation Engine */
    .file-title {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin: 1;
    }
    
    .slide-content {
        border: solid thick $primary;
        text-align: center;
        background: $surface;
        width: 100%;
        height: 90%;
        margin: 1 2;
    }
    
    .sidebar-item {
        border: solid blue;
    }
    
    .main-container {
        width: 75%;
        layout: vertical;
    }
    
    .nav-container {
        display: block;
        margin: 0 2;
        width: 100%;
        height: 15%;
    }
    
    .slide-counter {
        text-align: center;
        margin-bottom: 1;
    }
    
    .nav-buttons {
        width: 100%;
        height: auto;
    }
    
    /* Play Screen */
    .play-screen-container {
        width: 100%;
        height: 100%;
        align: center middle;
    }
    
    .play-slide-content {
        width: 100%;
        height: 100%;
        border: solid thick $primary;
        padding: 2;
        text-align: center;
        background: $surface;
    }
    .no-projects-center {
        height: 1fr;
        align: center middle;
    }

    .no-projects-container {
        
        padding: 3;
        background: $surface-darken-1;
        border: solid $primary;
        align: center middle;
        layout: vertical;
    }

    .no-projects-message {
        text-align: center;
        color: $text;
        margin-bottom: 2;
    }
 
        
    /* General */
    Button {
        margin: 0 1;
    }
    
 
    """

    def on_mount(self) -> None:
        self.install_screen(Home(), name="home")
        self.install_screen(FileBrowser(), name="file_browser")
        self.install_screen(NewPresentationScreen(), name="new_presentation")
        self.push_screen("home")


app = SlideDownApp().run()
if __name__ == "__main__":
    app()
