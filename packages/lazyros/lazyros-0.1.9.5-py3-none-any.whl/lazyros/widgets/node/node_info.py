import asyncio
import subprocess
from typing import Any, Dict, List, Optional, Union

from rclpy.action import graph
from rclpy.node import Node
from rich.markup import escape
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container
from textual.widgets import RichLog, Static


class InfoViewWidget(Container):
    """Widget for displaying ROS node information."""

    DEFAULT_CSS = """
    InfoViewWidget {
        overflow-y: scroll;
    }
    """

    def __init__(self, ros_node: Node, **kwargs: Any) -> None:
        """Initialize the InfoViewWidget.
        
        Args:
            ros_node: The ROS node instance for communication
            **kwargs: Additional keyword arguments passed to the parent Container
        """
        super().__init__(**kwargs)
        self.ros_node = ros_node 
        self.rich_log = RichLog(wrap=True, highlight=True, markup=True, id="info-log", max_lines=1000)
        self.info_dict: dict[str, list[str]] = {}
        
        self.selected_node_data = None
        self.current_node_full_name = None

    def compose(self) -> ComposeResult:
        """Compose the widget layout.
        
        Returns:
            ComposeResult: A generator yielding widget components
        """
        yield Static("", id="node-info")
        
    def on_mount(self) -> None:
        """Handle the widget mount event.
        
        Sets up periodic interval to update node information.
        """
        self.set_interval(1, self.update_info) 
            
    async def update_info(self) -> None:
        """Update the node information display.
        
        Fetches information about the selected node and displays it.
        Updates are skipped if no node is selected or if the node is shutdown.
        """
        node_listview = self.app.query_one("#node-listview")
        
        view = self.query_one("#node-info", Static)
        if not node_listview.selected_node_name:
            view.update("[red]No node is selected yet.[/]")
            return
        self.selected_node_data = node_listview.node_listview_dict["/"+node_listview.selected_node_name]

        if self.selected_node_data is None:
            view.update("[red]No node is selected yet.[/]")
            return

        if self.selected_node_data.status != "green":
            view.update("[red]Selected node is shutdown.[/]")
            return

        if self.selected_node_data.full_name == self.current_node_full_name:
            return
        
        self.current_node_full_name = self.selected_node_data.full_name
        info_lines = await asyncio.to_thread(self.show_node_info)
        if info_lines:
            view.update(Text.from_markup("\n".join(info_lines)))


    def show_node_info(self) -> Optional[List[str]]:
        """Retrieve and format node information.
        
        Returns:
            Optional[List[str]]: A list of formatted strings containing node information,
                                or None if information could not be retrieved
        """
        node_data = self.selected_node_data
        if node_data.full_name in self.info_dict:
            return self.info_dict[node_data.full_name]

        full_name = node_data.full_name 
        node = self.selected_node_data.node_name
        namespace = self.selected_node_data.namespace
        
        pubs = self.ros_node.get_publisher_names_and_types_by_node(node, namespace)
        subs = self.ros_node.get_subscriber_names_and_types_by_node(node, namespace)
        service_servers = self.ros_node.get_service_names_and_types_by_node(node, namespace)
        service_clients = self.ros_node.get_client_names_and_types_by_node(node, namespace)
        action_servers = graph.get_action_server_names_and_types_by_node(self.ros_node, node, namespace) 
        action_clients = graph.get_action_client_names_and_types_by_node(self.ros_node, node, namespace) 

        info_lines = []
        info_lines.append(f"[bold cyan]Node:[/] [yellow]{escape(full_name)}[/]")

        info_lines.append(f"[bold cyan]Subscribers:[/]")
        for sub in subs:
            topic, type_list = sub
            info_lines.append(f"  [yellow]{escape(topic)}[/]: [green]{escape(', '.join(type_list))}[/]")

        info_lines.append(f"[bold cyan]Publishers:[/]")
        for pub in pubs:
            topic, type_list = pub
            info_lines.append(f"  [yellow]{escape(topic)}[/]: [green]{escape(', '.join(type_list))}[/]")

        info_lines.append(f"[bold cyan]Service Clients:[/]")
        for client in service_clients:
            service, type_list = client
            info_lines.append(f"  [yellow]{escape(service)}[/]: [magenta]{escape(', '.join(type_list))}[/]")

        info_lines.append(f"[bold cyan]Service Servers:[/]")
        for server in service_servers:
            service, type_list = server
            info_lines.append(f"  [yellow]{escape(service)}[/]: [magenta]{escape(', '.join(type_list))}[/]")

        info_lines.append(f"[bold cyan]Action Servers:[/]")
        for server in action_servers:
            action, type_list = server
            info_lines.append(f"  [yellow]{escape(action)}[/]: [blue]{escape(', '.join(type_list))}[/]")

        info_lines.append(f"[bold cyan]Action Clients:[/]")
        for client in action_clients:
            action, type_list = client
            info_lines.append(f"  [yellow]{escape(action)}[/]: [blue]{escape(', '.join(type_list))}[/]")

        self.info_dict[full_name] = info_lines
        return info_lines
