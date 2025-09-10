import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Union

from lifecycle_msgs.srv import ChangeState, GetAvailableTransitions, GetState
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.node import Node
from rich.markup import escape
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Label, RichLog, Static


@dataclass
class LifecycleData:
    """Data class to store lifecycle node information.
    
    Attributes:
        is_lifecycle: Whether the node is a lifecycle node
        get_lifecycle_client: Client for getting lifecycle state
        change_lifecycle_client: Client for changing lifecycle state
        get_transition_client: Client for getting available transitions
        current_lifecycle_id: Current lifecycle state ID
        state_changed: Whether the state has changed since last check
    """
    is_lifecycle: bool
    get_lifecycle_client: Optional[Callable]
    change_lifecycle_client: Optional[Callable]
    get_transition_client: Optional[Callable]
    current_lifecycle_id: Optional[int] = None
    state_changed: bool = False

class LifecycleWidget(Container):
    """Widget for displaying ROS node information."""

    DEFAULT_CSS = """
        .hidden {
            display: none;
        }
        #lifecycle-state {
            height: 1fr;
            max-height: 30%;
        }
        #lifecycle-transition-buttons > Button {
            margin: 0 1;
            padding: 0 2;
            height: 3;
            min-width: 10;

            background: black;
            color: white;
            border: round white;
        }
        #lifecycle-transition-buttons > Button:hover {
            background: white;
            color: black;
        }
        #lifecycle-transition-buttons > Button:focus {
            border: heavy white;
        }
    """

    def __init__(self, ros_node: Node, **kwargs: Any) -> None:
        """Initialize the LifecycleWidget.
        
        Args:
            ros_node: The ROS node instance for communication
            **kwargs: Additional keyword arguments passed to the parent Container
        """
        super().__init__(**kwargs)
        self.ros_node = ros_node
        self.rich_log = RichLog(wrap=True, highlight=True, markup=True, id="lifecycle-state", max_lines=1000)
        self.transition_log = RichLog(wrap=True, highlight=True, markup=True, id="lifecycle-transition", max_lines=1000)
        self.lifecycle_dict: dict[str, list[str]] = {}
        
        self.selected_node_data = None
        self.current_node_full_name = None

    def compose(self) -> ComposeResult:
        """Compose the widget layout.
        
        Returns:
            ComposeResult: A generator yielding widget components
        """
        yield self.rich_log
        with Vertical(id="lifecycle-transitions"):
            yield Label("Available Lifecycle Transitions:")
            yield Horizontal(id="lifecycle-transition-buttons")

    def on_mount(self) -> None:
        """Handle the widget mount event.
        
        Sets up periodic interval to update lifecycle display and hides transitions section initially.
        """
        self.trans_section: Vertical = self.query_one("#lifecycle-transitions", Vertical)
        self.trans_section.add_class("hidden") 
        self.set_interval(0.3, self.update_display)

    async def update_transition_buttons(self) -> None:
        """Update the available transition buttons for the current lifecycle node.
        
        Fetches available transitions and creates buttons for each one.
        """
        node_name = self.selected_node_data.full_name.lstrip('/')
        for button in self.query("#lifecycle-transition-buttons > Button"):
            button.remove()

        transitions = await asyncio.to_thread(self.get_available_transitions)
        if transitions:
            for transition in transitions:
                self.query_one("#lifecycle-transition-buttons").mount(
                    Button(transition.transition.label, id=f"{node_name}-transition-button-{transition.transition.id}")
                )

    async def update_display(self) -> None:
        """Update the lifecycle information display.
        
        Shows lifecycle state and available transitions for the selected node.
        Updates are skipped if no node is selected or if the node is shutdown.
        """
        node_listview = self.app.query_one("#node-listview")
        if node_listview.selected_node_name is None:
            return

        self.selected_node_data = node_listview.node_listview_dict["/"+node_listview.selected_node_name]

        if self.selected_node_data is None:
            self.rich_log.clear()
            self.rich_log.write("[red]Please select a node first.[/]")
            return

        if self.selected_node_data.status != "green":
            self.rich_log.clear()
            self.rich_log.write("[red]The selected node is not running.[/]")
            return

        if self.selected_node_data.full_name == self.current_node_full_name:
            data = self.lifecycle_dict.get(self.selected_node_data.full_name, None)
            if data and not data.state_changed:
                return

        self.rich_log.clear()
        self.current_node_full_name = self.selected_node_data.full_name
        if self.selected_node_data.full_name not in self.lifecycle_dict:
            self.create_lifecycle_data()

        self.trans_section.add_class("hidden")
        if not self.lifecycle_dict[self.selected_node_data.full_name].is_lifecycle:
            return self.rich_log.write(f"[red]Node '{self.selected_node_data.full_name}' does not support lifecycle management.[/]")
        
        self.trans_section.remove_class("hidden")
        info_lines = await asyncio.to_thread(self.get_lifecycle_state)
        self.rich_log.write("\n".join(info_lines))

        await self.update_transition_buttons()

    def create_lifecycle_data(self) -> None:
        """Create lifecycle clients for the selected node.
        
        Checks if the node is a lifecycle node and creates appropriate service clients.
        """
        node = self.selected_node_data.node_name
        namespace = self.selected_node_data.namespace

        is_lifecycle = False
        try:
            srvs = self.ros_node.get_service_names_and_types_by_node(node, namespace)
            for srv in srvs:
                if "lifecycle_msgs/srv/GetState" in srv[1]:
                    is_lifecycle = True
                    break
        except Exception:
            is_lifecycle = False
            
        if is_lifecycle:
            try:
                self.lifecycle_dict[self.selected_node_data.full_name] = \
                    LifecycleData(is_lifecycle=True,
                                get_lifecycle_client=self.ros_node.create_client(GetState, f"{self.selected_node_data.full_name}/get_state", callback_group=ReentrantCallbackGroup()),
                                change_lifecycle_client=self.ros_node.create_client(ChangeState, f"{self.selected_node_data.full_name}/change_state", callback_group=ReentrantCallbackGroup()),
                                get_transition_client=self.ros_node.create_client(GetAvailableTransitions, f"{self.selected_node_data.full_name}/get_available_transitions", callback_group=ReentrantCallbackGroup()))
            except Exception:
                self.lifecycle_dict[self.selected_node_data.full_name] = \
                    LifecycleData(is_lifecycle=False,
                                get_lifecycle_client=None,
                                change_lifecycle_client=None,
                                get_transition_client=None)
        else:
            self.lifecycle_dict[self.selected_node_data.full_name] = \
                LifecycleData(is_lifecycle=False,
                            get_lifecycle_client=None,
                            change_lifecycle_client=None,
                            get_transition_client=None)

    def get_lifecycle_state(self) -> List[str]:
        """Get the current lifecycle state of the selected node.
        
        Returns:
            List[str]: A list of formatted strings containing lifecycle state information
        """
        """If the node is a lifecycle node, get its state."""
        try:
            full_name = self.selected_node_data.full_name
            
            lifecycle_client = self.lifecycle_dict[full_name].get_lifecycle_client
            if not lifecycle_client or not hasattr(lifecycle_client, 'handle') or lifecycle_client.handle is None:
                return [f"[red]Lifecycle client for {full_name} is invalid[/]"]
                
            if not lifecycle_client.wait_for_service(timeout_sec=1.0):
                return [f"[red]Lifecycle service for {full_name} is not available[/]"]

            req = GetState.Request()
            try:
                future = lifecycle_client.call_async(req)
                self.ros_node.executor.spin_until_future_complete(future, timeout_sec=3.0)
                if not future.done() or future.result() is None:
                    return [f"[red]Failed to get lifecycle state for {full_name}[/]"]

                current = future.result().current_state
                if self.lifecycle_dict[full_name].current_lifecycle_id != current.id:
                    self.lifecycle_dict[full_name].state_changed = True
                    self.lifecycle_dict[full_name].current_lifecycle_id = current.id
                else:
                    self.lifecycle_dict[full_name].state_changed = False

                info_lines = []
                info_lines.append(f"[cyan]Lifecycle State for[/] [yellow]{escape(full_name)}: [/]")
                info_lines.append(f"  {current.label}[{current.id}]")
                return info_lines
            except Exception:
                return [f"[red]Failed to get lifecycle state for {full_name}[/]"]
        except Exception:
            return [f"[red]Error accessing lifecycle data[/]"]

    def get_available_transitions(self) -> Optional[Any]:
        """Get available transitions for the current lifecycle node.
        
        Returns:
            Optional[Any]: Available transitions or None if unable to retrieve
        """
        try:
            full_name = self.selected_node_data.full_name
            
            get_transition_client = self.lifecycle_dict[full_name].get_transition_client
            if not get_transition_client.wait_for_service(timeout_sec=1.0):
                return None

            while not get_transition_client.wait_for_service(timeout_sec=1.0):
                self.ros_node.get_logger().info('Waiting for lifecycle transition service to become available...')

            request = GetAvailableTransitions.Request()
            future = get_transition_client.call_async(request)
            self.ros_node.executor.spin_until_future_complete(future, timeout_sec=5.0)
            if not future.done() or future.result() is None:
                return None

            transitions = future.result().available_transitions
            return transitions
        except Exception:
            return None

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events for lifecycle transitions.
        
        Args:
            event: The button press event containing the transition ID
        """
        transition_id = int(event.button.id.split("-")[-1])
        await asyncio.to_thread(self.trigger_transition, transition_id)

    def trigger_transition(self, transition_id: int) -> None:
        """Trigger a lifecycle transition.
        
        Args:
            transition_id: The ID of the transition to trigger
        """
        try:
            full_name = self.selected_node_data.full_name
            
            self.log(f"Triggering transition {transition_id} for {full_name}")

            change_lifecycle_client = self.lifecycle_dict[full_name].change_lifecycle_client
            if not change_lifecycle_client.wait_for_service(timeout_sec=1.0):
                return None

            request = ChangeState.Request()
            request.transition.id = transition_id
            future = change_lifecycle_client.call_async(request)

            self.ros_node.executor.spin_until_future_complete(future, timeout_sec=5.0)
            if not future.done() or future.result() is None:
                self.log(f"Failed to change lifecycle state for {full_name}")
                return None
            if not future.result().success:
                return None

            self.log(f"Transition {transition_id} for {full_name} completed successfully")
            self.get_lifecycle_state()
        except Exception as e:
            self.log(f"Error triggering transition: {e}")