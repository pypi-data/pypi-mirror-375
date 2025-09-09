"""
Interactive prompt functionality for agents.

This module provides interactive command-line functionality for agents,
extracted from the original AgentApp implementation to support the new DirectAgentApp.

Usage:
    prompt = InteractivePrompt()
    await prompt.prompt_loop(
        send_func=agent_app.send,
        default_agent="default_agent",
        available_agents=["agent1", "agent2"],
        prompt_provider=agent_app
    )
"""

from typing import Awaitable, Callable, Dict, List, Mapping, Optional, Protocol, Union

from mcp.types import Prompt, PromptMessage
from rich import print as rich_print
from rich.console import Console
from rich.table import Table

from fast_agent.agents.agent_types import AgentType
from fast_agent.types import PromptMessageExtended
from fast_agent.ui.enhanced_prompt import (
    _display_agent_info_helper,
    get_argument_input,
    get_enhanced_input,
    get_selection_input,
    handle_special_commands,
)
from fast_agent.ui.progress_display import progress_display
from fast_agent.ui.usage_display import collect_agents_from_provider, display_usage_report
from mcp_agent.mcp.mcp_aggregator import SEP

# Type alias for the send function
SendFunc = Callable[[Union[str, PromptMessage, PromptMessageExtended], str], Awaitable[str]]

# Type alias for the agent getter function
AgentGetter = Callable[[str], Optional[object]]


class PromptProvider(Protocol):
    """Protocol for objects that can provide prompt functionality."""

    async def list_prompts(
        self, server_name: Optional[str] = None, agent_name: Optional[str] = None
    ) -> Mapping[str, List[Prompt]]:
        """List available prompts."""
        ...

    async def apply_prompt(
        self,
        prompt_name: str,
        prompt_title: Optional[str] = None,
        arguments: Optional[Dict[str, str]] = None,
        agent_name: Optional[str] = None,
        as_template: bool = False,
        **kwargs,
    ) -> str:
        """Apply a prompt."""
        ...


class InteractivePrompt:
    """
    Provides interactive prompt functionality that works with any agent implementation.
    This is extracted from the original AgentApp implementation to support DirectAgentApp.
    """

    def __init__(self, agent_types: Optional[Dict[str, AgentType]] = None) -> None:
        """
        Initialize the interactive prompt.

        Args:
            agent_types: Dictionary mapping agent names to their types for display
        """
        self.agent_types: Dict[str, AgentType] = agent_types or {}

    async def prompt_loop(
        self,
        send_func: SendFunc,
        default_agent: str,
        available_agents: List[str],
        prompt_provider: Optional[PromptProvider] = None,
        default: str = "",
    ) -> str:
        """
        Start an interactive prompt session.

        Args:
            send_func: Function to send messages to agents
            default_agent: Name of the default agent to use
            available_agents: List of available agent names
            prompt_provider: Optional provider that implements list_prompts and apply_prompt
            default: Default message to use when user presses enter

        Returns:
            The result of the interactive session
        """
        agent = default_agent
        if not agent:
            if available_agents:
                agent = available_agents[0]
            else:
                raise ValueError("No default agent available")

        if agent not in available_agents:
            raise ValueError(f"No agent named '{agent}'")

        # Ensure we track available agents in a set for fast lookup
        available_agents_set = set(available_agents)

        result = ""
        while True:
            with progress_display.paused():
                # Use the enhanced input method with advanced features
                user_input = await get_enhanced_input(
                    agent_name=agent,
                    default=default,
                    show_default=(default != ""),
                    show_stop_hint=True,
                    multiline=False,  # Default to single-line mode
                    available_agent_names=available_agents,
                    agent_types=self.agent_types,  # Pass agent types for display
                    agent_provider=prompt_provider,  # Pass agent provider for info display
                )

                # Handle special commands - pass "True" to enable agent switching
                command_result = await handle_special_commands(user_input, True)

                # Check if we should switch agents
                if isinstance(command_result, dict):
                    if "switch_agent" in command_result:
                        new_agent = command_result["switch_agent"]
                        if new_agent in available_agents_set:
                            agent = new_agent
                            # Display new agent info immediately when switching
                            rich_print()  # Add spacing
                            await _display_agent_info_helper(agent, prompt_provider)
                            continue
                        else:
                            rich_print(f"[red]Agent '{new_agent}' not found[/red]")
                            continue
                    # Keep the existing list_prompts handler for backward compatibility
                    elif "list_prompts" in command_result and prompt_provider:
                        # Use the prompt_provider directly
                        await self._list_prompts(prompt_provider, agent)
                        continue
                    elif "select_prompt" in command_result and prompt_provider:
                        # Handle prompt selection, using both list_prompts and apply_prompt
                        prompt_name = command_result.get("prompt_name")
                        prompt_index = command_result.get("prompt_index")

                        # If a specific index was provided (from /prompt <number>)
                        if prompt_index is not None:
                            # First get a list of all prompts to look up the index
                            all_prompts = await self._get_all_prompts(prompt_provider, agent)
                            if not all_prompts:
                                rich_print("[yellow]No prompts available[/yellow]")
                                continue

                            # Check if the index is valid
                            if 1 <= prompt_index <= len(all_prompts):
                                # Get the prompt at the specified index (1-based to 0-based)
                                selected_prompt = all_prompts[prompt_index - 1]
                                # Use the already created namespaced_name to ensure consistency
                                await self._select_prompt(
                                    prompt_provider,
                                    agent,
                                    selected_prompt["namespaced_name"],
                                )
                            else:
                                rich_print(
                                    f"[red]Invalid prompt number: {prompt_index}. Valid range is 1-{len(all_prompts)}[/red]"
                                )
                                # Show the prompt list for convenience
                                await self._list_prompts(prompt_provider, agent)
                        else:
                            # Use the name-based selection
                            await self._select_prompt(prompt_provider, agent, prompt_name)
                        continue
                    elif "list_tools" in command_result and prompt_provider:
                        # Handle tools list display
                        await self._list_tools(prompt_provider, agent)
                        continue
                    elif "show_usage" in command_result:
                        # Handle usage display
                        await self._show_usage(prompt_provider, agent)
                        continue
                    elif "show_markdown" in command_result:
                        # Handle markdown display
                        await self._show_markdown(prompt_provider, agent)
                        continue

                # Skip further processing if:
                # 1. The command was handled (command_result is truthy)
                # 2. The original input was a dictionary (special command like /prompt)
                # 3. The command result itself is a dictionary (special command handling result)
                # This fixes the issue where /prompt without arguments gets sent to the LLM
                if (
                    command_result
                    or isinstance(user_input, dict)
                    or isinstance(command_result, dict)
                ):
                    continue

                if user_input.upper() == "STOP":
                    return result
                if user_input == "":
                    continue

            # Send the message to the agent
            result = await send_func(user_input, agent)

        return result

    async def _get_all_prompts(
        self, prompt_provider: PromptProvider, agent_name: Optional[str] = None
    ):
        """
        Get a list of all available prompts.

        Args:
            prompt_provider: Provider that implements list_prompts
            agent_name: Optional agent name (for multi-agent apps)

        Returns:
            List of prompt info dictionaries, sorted by server and name
        """
        try:
            # Call list_prompts on the provider
            prompt_servers = await prompt_provider.list_prompts(
                server_name=None, agent_name=agent_name
            )

            all_prompts = []

            # Process the returned prompt servers
            if prompt_servers:
                # First collect all prompts
                for server_name, prompts_info in prompt_servers.items():
                    if prompts_info and hasattr(prompts_info, "prompts") and prompts_info.prompts:
                        for prompt in prompts_info.prompts:
                            # Use the SEP constant for proper namespacing
                            all_prompts.append(
                                {
                                    "server": server_name,
                                    "name": prompt.name,
                                    "namespaced_name": f"{server_name}{SEP}{prompt.name}",
                                    "title": prompt.title or None,
                                    "description": prompt.description or "No description",
                                    "arg_count": len(prompt.arguments or []),
                                    "arguments": prompt.arguments or [],
                                }
                            )
                    elif isinstance(prompts_info, list) and prompts_info:
                        for prompt in prompts_info:
                            if isinstance(prompt, dict) and "name" in prompt:
                                all_prompts.append(
                                    {
                                        "server": server_name,
                                        "name": prompt["name"],
                                        "namespaced_name": f"{server_name}{SEP}{prompt['name']}",
                                        "title": prompt.get("title", None),
                                        "description": prompt.get("description", "No description"),
                                        "arg_count": len(prompt.get("arguments", [])),
                                        "arguments": prompt.get("arguments", []),
                                    }
                                )
                            else:
                                # Handle Prompt objects from mcp.types
                                all_prompts.append(
                                    {
                                        "server": server_name,
                                        "name": prompt.name,
                                        "namespaced_name": f"{server_name}{SEP}{prompt.name}",
                                        "title": prompt.title or None,
                                        "description": prompt.description or "No description",
                                        "arg_count": len(prompt.arguments or []),
                                        "arguments": prompt.arguments or [],
                                    }
                                )

                # Sort prompts by server and name for consistent ordering
                all_prompts.sort(key=lambda p: (p["server"], p["name"]))

            return all_prompts

        except Exception as e:
            import traceback

            from rich import print as rich_print

            rich_print(f"[red]Error getting prompts: {e}[/red]")
            rich_print(f"[dim]{traceback.format_exc()}[/dim]")
            return []

    async def _list_prompts(self, prompt_provider: PromptProvider, agent_name: str) -> None:
        """
        List available prompts for an agent.

        Args:
            prompt_provider: Provider that implements list_prompts
            agent_name: Name of the agent
        """
        console = Console()

        try:
            # Directly call the list_prompts function for this agent
            rich_print(f"\n[bold]Fetching prompts for agent [cyan]{agent_name}[/cyan]...[/bold]")

            # Get all prompts using the helper function
            all_prompts = await self._get_all_prompts(prompt_provider, agent_name)

            if all_prompts:
                # Create a table for better display
                table = Table(title="Available MCP Prompts")
                table.add_column("#", justify="right", style="cyan")
                table.add_column("Server", style="green")
                table.add_column("Prompt Name", style="bright_blue")
                table.add_column("Title")
                table.add_column("Description")
                table.add_column("Args", justify="center")

                # Add prompts to table
                for i, prompt in enumerate(all_prompts):
                    table.add_row(
                        str(i + 1),
                        prompt["server"],
                        prompt["name"],
                        prompt["title"],
                        prompt["description"],
                        str(prompt["arg_count"]),
                    )

                console.print(table)

                # Add usage instructions
                rich_print("\n[bold]Usage:[/bold]")
                rich_print("  • Use [cyan]/prompt <number>[/cyan] to select a prompt by number")
                rich_print("  • Or use [cyan]/prompts[/cyan] to open the prompt selection UI")
            else:
                rich_print("[yellow]No prompts available[/yellow]")
        except Exception as e:
            import traceback

            rich_print(f"[red]Error listing prompts: {e}[/red]")
            rich_print(f"[dim]{traceback.format_exc()}[/dim]")

    async def _select_prompt(
        self,
        prompt_provider: PromptProvider,
        agent_name: str,
        requested_name: Optional[str] = None,
        send_func: Optional[SendFunc] = None,
    ) -> None:
        """
        Select and apply a prompt.

        Args:
            prompt_provider: Provider that implements list_prompts and get_prompt
            agent_name: Name of the agent
            requested_name: Optional name of the prompt to apply
        """
        console = Console()

        try:
            # Get all available prompts directly from the prompt provider
            rich_print(f"\n[bold]Fetching prompts for agent [cyan]{agent_name}[/cyan]...[/bold]")

            # Call list_prompts on the provider
            prompt_servers = await prompt_provider.list_prompts(
                server_name=None, agent_name=agent_name
            )

            if not prompt_servers:
                rich_print("[yellow]No prompts available for this agent[/yellow]")
                return

            # Process fetched prompts
            all_prompts = []
            for server_name, prompts_info in prompt_servers.items():
                if not prompts_info:
                    continue

                # Extract prompts
                prompts: List[Prompt] = []
                if hasattr(prompts_info, "prompts"):
                    prompts = prompts_info.prompts
                elif isinstance(prompts_info, list):
                    prompts = prompts_info

                # Process each prompt
                for prompt in prompts:
                    # Get basic prompt info
                    prompt_name = prompt.name
                    prompt_title = prompt.title or None
                    prompt_description = prompt.description or "No description"

                    # Extract argument information
                    arg_names = []
                    required_args = []
                    optional_args = []
                    arg_descriptions = {}

                    # Get arguments list
                    if prompt.arguments:
                        for arg in prompt.arguments:
                            arg_names.append(arg.name)

                            # Store description if available
                            if arg.description:
                                arg_descriptions[arg.name] = arg.description

                            # Check if required
                            if arg.required:
                                required_args.append(arg.name)
                            else:
                                optional_args.append(arg.name)

                    # Create namespaced version using the consistent separator
                    namespaced_name = f"{server_name}{SEP}{prompt_name}"

                    # Add to collection
                    all_prompts.append(
                        {
                            "server": server_name,
                            "name": prompt_name,
                            "namespaced_name": namespaced_name,
                            "title": prompt_title,
                            "description": prompt_description,
                            "arg_count": len(arg_names),
                            "arg_names": arg_names,
                            "required_args": required_args,
                            "optional_args": optional_args,
                            "arg_descriptions": arg_descriptions,
                        }
                    )

            if not all_prompts:
                rich_print("[yellow]No prompts available for this agent[/yellow]")
                return

            # Sort prompts by server then name
            all_prompts.sort(key=lambda p: (p["server"], p["name"]))

            # Handle specifically requested prompt
            if requested_name:
                matching_prompts = [
                    p
                    for p in all_prompts
                    if p["name"] == requested_name or p["namespaced_name"] == requested_name
                ]

                if not matching_prompts:
                    rich_print(f"[red]Prompt '{requested_name}' not found[/red]")
                    rich_print("[yellow]Available prompts:[/yellow]")
                    for p in all_prompts:
                        rich_print(f"  {p['namespaced_name']}")
                    return

                # If exactly one match, use it
                if len(matching_prompts) == 1:
                    selected_prompt = matching_prompts[0]
                else:
                    # Handle multiple matches
                    rich_print(f"[yellow]Multiple prompts match '{requested_name}':[/yellow]")
                    for i, p in enumerate(matching_prompts):
                        rich_print(f"  {i + 1}. {p['namespaced_name']} - {p['description']}")

                    # Get user selection
                    selection = (
                        await get_selection_input("Enter prompt number to select: ", default="1")
                        or ""
                    )

                    try:
                        idx = int(selection) - 1
                        if 0 <= idx < len(matching_prompts):
                            selected_prompt = matching_prompts[idx]
                        else:
                            rich_print("[red]Invalid selection[/red]")
                            return
                    except ValueError:
                        rich_print("[red]Invalid input, please enter a number[/red]")
                        return
            else:
                # Show prompt selection UI
                table = Table(title="Available MCP Prompts")
                table.add_column("#", justify="right", style="cyan")
                table.add_column("Server", style="green")
                table.add_column("Prompt Name", style="bright_blue")
                table.add_column("Title")
                table.add_column("Description")
                table.add_column("Args", justify="center")

                # Add prompts to table
                for i, prompt in enumerate(all_prompts):
                    required_args = prompt["required_args"]
                    optional_args = prompt["optional_args"]

                    # Format args column
                    if required_args and optional_args:
                        args_display = f"[bold]{len(required_args)}[/bold]+{len(optional_args)}"
                    elif required_args:
                        args_display = f"[bold]{len(required_args)}[/bold]"
                    elif optional_args:
                        args_display = f"{len(optional_args)} opt"
                    else:
                        args_display = "0"

                    table.add_row(
                        str(i + 1),
                        prompt["server"],
                        prompt["name"],
                        prompt["title"] or "No title",
                        prompt["description"] or "No description",
                        args_display,
                    )

                console.print(table)
                prompt_names = [str(i + 1) for i in range(len(all_prompts))]

                # Get user selection
                selection = await get_selection_input(
                    "Enter prompt number to select (or press Enter to cancel): ",
                    options=prompt_names,
                    allow_cancel=True,
                )

                # Handle cancellation
                if not selection or selection.strip() == "":
                    rich_print("[yellow]Prompt selection cancelled[/yellow]")
                    return

                try:
                    idx = int(selection) - 1
                    if 0 <= idx < len(all_prompts):
                        selected_prompt = all_prompts[idx]
                    else:
                        rich_print("[red]Invalid selection[/red]")
                        return
                except ValueError:
                    rich_print("[red]Invalid input, please enter a number[/red]")
                    return

            # Get prompt arguments
            required_args = selected_prompt["required_args"]
            optional_args = selected_prompt["optional_args"]
            arg_descriptions = selected_prompt.get("arg_descriptions", {})
            arg_values = {}

            # Show argument info if any
            if required_args or optional_args:
                if required_args and optional_args:
                    rich_print(
                        f"\n[bold]Prompt [cyan]{selected_prompt['name']}[/cyan] requires {len(required_args)} arguments and has {len(optional_args)} optional arguments:[/bold]"
                    )
                elif required_args:
                    rich_print(
                        f"\n[bold]Prompt [cyan]{selected_prompt['name']}[/cyan] requires {len(required_args)} arguments:[/bold]"
                    )
                elif optional_args:
                    rich_print(
                        f"\n[bold]Prompt [cyan]{selected_prompt['name']}[/cyan] has {len(optional_args)} optional arguments:[/bold]"
                    )

                # Collect required arguments
                for arg_name in required_args:
                    description = arg_descriptions.get(arg_name, "")
                    arg_value = await get_argument_input(
                        arg_name=arg_name,
                        description=description,
                        required=True,
                    )
                    if arg_value is not None:
                        arg_values[arg_name] = arg_value

                # Collect optional arguments
                if optional_args:
                    for arg_name in optional_args:
                        description = arg_descriptions.get(arg_name, "")
                        arg_value = await get_argument_input(
                            arg_name=arg_name,
                            description=description,
                            required=False,
                        )
                        if arg_value:
                            arg_values[arg_name] = arg_value

            # Apply the prompt using generate() for proper progress display
            namespaced_name = selected_prompt["namespaced_name"]
            rich_print(f"\n[bold]Applying prompt [cyan]{namespaced_name}[/cyan]...[/bold]")

            # Get the agent directly for generate() call
            if hasattr(prompt_provider, "_agent"):
                # This is an AgentApp - get the specific agent
                agent = prompt_provider._agent(agent_name)
            else:
                # This is a single agent
                agent = prompt_provider

            try:
                # Use agent.apply_prompt() which handles everything properly:
                # - get_prompt() to fetch template
                # - convert to multipart
                # - call generate() for progress display
                # - return response text
                # Response display is handled by the agent's show_ methods, don't print it here

                # Fetch the prompt first (without progress display)
                prompt_result = await agent.get_prompt(namespaced_name, arg_values)

                if not prompt_result or not prompt_result.messages:
                    rich_print(
                        f"[red]Prompt '{namespaced_name}' could not be found or contains no messages[/red]"
                    )
                    return

                # Convert to multipart format
                from fast_agent.types import PromptMessageExtended

                multipart_messages = PromptMessageExtended.from_get_prompt_result(prompt_result)

                # Now start progress display for the actual generation
                progress_display.resume()
                try:
                    await agent.generate(multipart_messages, None)
                finally:
                    # Pause again for the next UI interaction
                    progress_display.pause()

                # Show usage info after the turn (same as send_wrapper does)
                if hasattr(prompt_provider, "_show_turn_usage"):
                    prompt_provider._show_turn_usage(agent_name)

            except Exception as e:
                rich_print(f"[red]Error applying prompt: {e}[/red]")

        except Exception as e:
            import traceback

            rich_print(f"[red]Error selecting or applying prompt: {e}[/red]")
            rich_print(f"[dim]{traceback.format_exc()}[/dim]")

    async def _list_tools(self, prompt_provider: PromptProvider, agent_name: str) -> None:
        """
        List available tools for an agent.

        Args:
            prompt_provider: Provider that implements list_tools
            agent_name: Name of the agent
        """
        console = Console()

        try:
            # Get agent to list tools from
            if hasattr(prompt_provider, "_agent"):
                # This is an AgentApp - get the specific agent
                agent = prompt_provider._agent(agent_name)
            else:
                # This is a single agent
                agent = prompt_provider

            rich_print(f"\n[bold]Fetching tools for agent [cyan]{agent_name}[/cyan]...[/bold]")

            # Get tools using list_tools
            tools_result = await agent.list_tools()

            if not tools_result or not hasattr(tools_result, "tools") or not tools_result.tools:
                rich_print("[yellow]No tools available for this agent[/yellow]")
                return

            # Create a table for better display
            table = Table(title="Available MCP Tools")
            table.add_column("#", justify="right", style="cyan")
            table.add_column("Tool Name", style="bright_blue")
            table.add_column("Title")
            table.add_column("Description")

            # Add tools to table
            for i, tool in enumerate(tools_result.tools):
                table.add_row(
                    str(i + 1),
                    tool.name,
                    tool.title or "No title",
                    tool.description or "No description",
                )

            console.print(table)

        except Exception as e:
            import traceback

            rich_print(f"[red]Error listing tools: {e}[/red]")
            rich_print(f"[dim]{traceback.format_exc()}[/dim]")

    async def _show_usage(self, prompt_provider: PromptProvider, agent_name: str) -> None:
        """
        Show usage statistics for the current agent(s) in a colorful table format.

        Args:
            prompt_provider: Provider that has access to agents
            agent_name: Name of the current agent
        """
        try:
            # Collect all agents from the prompt provider
            agents_to_show = collect_agents_from_provider(prompt_provider, agent_name)

            if not agents_to_show:
                rich_print("[yellow]No usage data available[/yellow]")
                return

            # Use the shared display utility
            display_usage_report(agents_to_show, show_if_progress_disabled=True)

        except Exception as e:
            rich_print(f"[red]Error showing usage: {e}[/red]")

    async def _show_markdown(self, prompt_provider: PromptProvider, agent_name: str) -> None:
        """
        Show the last assistant message without markdown formatting.

        Args:
            prompt_provider: Provider that has access to agents
            agent_name: Name of the current agent
        """
        try:
            # Get agent to display from
            if hasattr(prompt_provider, "_agent"):
                # This is an AgentApp - get the specific agent
                agent = prompt_provider._agent(agent_name)
            else:
                # This is a single agent
                agent = prompt_provider

            # Check if agent has message history
            if not hasattr(agent, "_llm") or not agent._llm:
                rich_print("[yellow]No message history available[/yellow]")
                return

            message_history = agent._llm.message_history
            if not message_history:
                rich_print("[yellow]No messages in history[/yellow]")
                return

            # Find the last assistant message
            last_assistant_msg = None
            for msg in reversed(message_history):
                if msg.role == "assistant":
                    last_assistant_msg = msg
                    break

            if not last_assistant_msg:
                rich_print("[yellow]No assistant messages found[/yellow]")
                return

            # Get the text content and display without markdown
            content = last_assistant_msg.last_text()

            # Display with a simple header
            rich_print("\n[bold blue]Last Assistant Response (Plain Text):[/bold blue]")
            rich_print("─" * 60)
            # Use console.print with markup=False to display raw text
            from fast_agent.ui import console

            console.console.print(content, markup=False)
            rich_print("─" * 60)
            rich_print()

        except Exception as e:
            rich_print(f"[red]Error showing markdown: {e}[/red]")
