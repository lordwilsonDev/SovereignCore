#!/usr/bin/env python3
"""
🤖 Micro-Agent Framework
=========================

Lightweight code-as-policy agent for local-first AI.
Inspired by smolagents and tiny-agent-framework patterns.

Features:
- @tool decorator for function registration
- Direct LLM bridge (no HTTP overhead)
- Hardware-aware execution
- Fault tree integration for safety
- Minimal dependencies

The agent is just a loop: observe → think → act → repeat.

Author: SovereignCore v4.0
"""

import json
import time
import re
import inspect
from functools import wraps
from dataclasses import dataclass, field
from typing import Dict, List, Callable, Any, Optional, Generator
from pathlib import Path

# =============================================================================
# TOOL REGISTRY
# =============================================================================

TOOL_REGISTRY: Dict[str, 'Tool'] = {}


@dataclass
class Tool:
    """A registered tool that the agent can use."""
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any]
    returns: str
    is_safe: bool = True  # Safe tools can be auto-executed


def tool(description: str = "", returns: str = "str", safe: bool = True):
    """
    Decorator to register a function as an agent tool.
    
    Usage:
        @tool("Search the web for information")
        def web_search(query: str) -> str:
            ...
    """
    def decorator(func: Callable) -> Callable:
        # Extract parameter info from function signature
        sig = inspect.signature(func)
        params = {}
        
        for name, param in sig.parameters.items():
            param_type = "any"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == str:
                    param_type = "string"
                elif param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list:
                    param_type = "array"
            
            params[name] = {
                "type": param_type,
                "required": param.default == inspect.Parameter.empty
            }
        
        # Create tool object
        tool_obj = Tool(
            name=func.__name__,
            description=description or func.__doc__ or "",
            func=func,
            parameters=params,
            returns=returns,
            is_safe=safe
        )
        
        TOOL_REGISTRY[func.__name__] = tool_obj
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper._tool = tool_obj
        return wrapper
    
    return decorator


# =============================================================================
# BUILT-IN TOOLS
# =============================================================================

@tool("Execute a shell command and return the output", safe=False)
def shell(command: str) -> str:
    """Execute a shell command."""
    import subprocess
    try:
        result = subprocess.run(
            command, shell=True,
            capture_output=True, text=True,
            timeout=30
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {e}"


@tool("Read the contents of a file", safe=True)
def read_file(path: str) -> str:
    """Read a file."""
    try:
        return Path(path).read_text()
    except Exception as e:
        return f"Error: {e}"


@tool("Write content to a file", safe=False)
def write_file(path: str, content: str) -> str:
    """Write to a file."""
    try:
        Path(path).write_text(content)
        return f"Successfully wrote to {path}"
    except Exception as e:
        return f"Error: {e}"


@tool("Get the current date and time", safe=True)
def get_time() -> str:
    """Get current time."""
    return time.strftime("%Y-%m-%d %H:%M:%S")


@tool("Get system thermal and power status", safe=True)
def get_system_status() -> str:
    """Get system hardware status."""
    try:
        from apple_sensors import AppleSensors
        sensors = AppleSensors()
        data = sensors.get_all()
        return json.dumps(data, indent=2)
    except ImportError:
        return "Sensors not available"
    except Exception as e:
        return f"Error: {e}"


@tool("Calculate a mathematical expression", safe=True)
def calculate(expression: str) -> str:
    """Evaluate a math expression safely."""
    import ast
    import operator
    
    # Safe operators
    ops = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg
    }
    
    def eval_expr(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.BinOp):
            return ops[type(node.op)](eval_expr(node.left), eval_expr(node.right))
        elif isinstance(node, ast.UnaryOp):
            return ops[type(node.op)](eval_expr(node.operand))
        else:
            raise ValueError(f"Unsupported: {node}")
    
    try:
        tree = ast.parse(expression, mode='eval')
        result = eval_expr(tree.body)
        return str(result)
    except Exception as e:
        return f"Error: {e}"


@tool("Search memories in the knowledge graph", safe=True)
def search_memory(query: str) -> str:
    """Search the knowledge graph."""
    try:
        from knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()
        results = kg.recall(query, limit=5)
        return json.dumps([r.to_dict() for r in results], indent=2)
    except ImportError:
        return "Knowledge graph not available"
    except Exception as e:
        return f"Error: {e}"


@tool("Store information in the knowledge graph", safe=True)
def remember(content: str, category: str = "general") -> str:
    """Store a memory."""
    try:
        from knowledge_graph import KnowledgeGraph
        kg = KnowledgeGraph()
        memory_id = kg.store(content, category)
        return f"Stored memory: {memory_id}"
    except ImportError:
        return "Knowledge graph not available"
    except Exception as e:
        return f"Error: {e}"


# =============================================================================
# AGENT CORE
# =============================================================================

@dataclass
class AgentConfig:
    """Agent configuration."""
    max_iterations: int = 10
    temperature: float = 0.7
    enable_safety: bool = True
    allow_unsafe_tools: bool = False
    verbose: bool = True


@dataclass
class AgentMessage:
    """A message in the conversation."""
    role: str  # "user", "assistant", "tool"
    content: str
    tool_name: Optional[str] = None
    tool_result: Optional[str] = None


class MicroAgent:
    """
    Minimalist agent that uses LLM to orchestrate tool calls.
    
    The agent loop:
    1. Receive task from user
    2. Think: Send task + tools to LLM
    3. Act: Execute tool calls from LLM response  
    4. Observe: Add tool results to context
    5. Repeat until done or max iterations
    """
    
    def __init__(self, config: AgentConfig = None):
        self.config = config or AgentConfig()
        self.history: List[AgentMessage] = []
        self.engine = None
        self.fault_tree = None
        self.sensors = None
        
        self._init_subsystems()
    
    def _init_subsystems(self):
        """Initialize subsystems."""
        # BitNet engine
        try:
            from bitnet_engine import BitNetEngine
            self.engine = BitNetEngine()
        except ImportError:
            pass
        
        # Fault tree
        try:
            from fault_tree import AgentFaultTree
            self.fault_tree = AgentFaultTree()
        except ImportError:
            pass
        
        # Sensors
        try:
            from apple_sensors import AppleSensors
            self.sensors = AppleSensors()
            if self.engine:
                self.engine.set_sensors(self.sensors)
            if self.fault_tree:
                self.fault_tree.set_sensors(self.sensors)
        except ImportError:
            pass
    
    def _get_tools_prompt(self) -> str:
        """Generate tools description for the prompt."""
        tools_desc = []
        
        for name, tool in TOOL_REGISTRY.items():
            if not tool.is_safe and not self.config.allow_unsafe_tools:
                continue
            
            params_desc = []
            for param_name, param_info in tool.parameters.items():
                req = "(required)" if param_info.get('required') else "(optional)"
                params_desc.append(f"    - {param_name}: {param_info['type']} {req}")
            
            tools_desc.append(
                f"- {name}: {tool.description}\n"
                f"  Parameters:\n" + '\n'.join(params_desc)
            )
        
        return "\n".join(tools_desc)
    
    def _build_prompt(self, task: str) -> str:
        """Build the full prompt for the LLM."""
        tools_prompt = self._get_tools_prompt()
        
        history_str = ""
        for msg in self.history[-5:]:  # Last 5 messages
            if msg.role == "tool":
                history_str += f"\n[Tool {msg.tool_name} returned: {msg.tool_result[:200]}...]"
            else:
                history_str += f"\n{msg.role.upper()}: {msg.content}"
        
        prompt = f"""You are a helpful AI agent with access to tools. To use a tool, respond with:
TOOL: tool_name
ARGS: {{"param": "value"}}

Available tools:
{tools_prompt}

When you have completed the task, respond with:
DONE: <your final answer>

{history_str}

USER: {task}
ASSISTANT:"""
        
        return prompt
    
    def _parse_response(self, response: str) -> tuple:
        """
        Parse LLM response for tool calls or final answer.
        
        Returns:
            (action_type, content)
            action_type: "tool", "done", or "continue"
        """
        response = response.strip()
        
        # Check for DONE
        if "DONE:" in response:
            answer = response.split("DONE:", 1)[1].strip()
            return ("done", answer)
        
        # Check for TOOL call
        tool_match = re.search(r'TOOL:\s*(\w+)', response)
        args_match = re.search(r'ARGS:\s*({.*?})', response, re.DOTALL)
        
        if tool_match:
            tool_name = tool_match.group(1)
            args = {}
            
            if args_match:
                try:
                    args = json.loads(args_match.group(1))
                except json.JSONDecodeError:
                    pass
            
            return ("tool", {"name": tool_name, "args": args})
        
        # No clear action, continue
        return ("continue", response)
    
    def _execute_tool(self, tool_name: str, args: Dict) -> str:
        """Execute a tool and return result."""
        if tool_name not in TOOL_REGISTRY:
            return f"Error: Unknown tool '{tool_name}'"
        
        tool = TOOL_REGISTRY[tool_name]
        
        # Safety check
        if not tool.is_safe and not self.config.allow_unsafe_tools:
            return f"Error: Tool '{tool_name}' is unsafe and not allowed"
        
        try:
            result = tool.func(**args)
            return str(result)
        except Exception as e:
            return f"Error executing {tool_name}: {e}"
    
    def _check_safety(self) -> tuple:
        """Check fault tree before action."""
        if not self.config.enable_safety or self.fault_tree is None:
            return (True, "Safety disabled")
        
        risk = self.fault_tree.risk_score()
        
        if risk.should_halt:
            return (False, risk.recommendation)
        
        return (True, f"Risk level: {risk.risk_level}")
    
    def run(self, task: str) -> Generator[str, None, None]:
        """
        Run the agent on a task.
        
        Yields status updates and final result.
        """
        if self.config.verbose:
            yield f"🤖 Starting task: {task}\n"
        
        # Safety check
        safe, msg = self._check_safety()
        if not safe:
            yield f"⚠️ Safety halt: {msg}\n"
            return
        
        # Add task to history
        self.history.append(AgentMessage(role="user", content=task))
        
        for iteration in range(self.config.max_iterations):
            if self.config.verbose:
                yield f"\n📍 Iteration {iteration + 1}/{self.config.max_iterations}\n"
            
            # Build prompt and get LLM response
            prompt = self._build_prompt(task)
            
            if self.engine is None:
                yield "❌ No inference engine available\n"
                return
            
            response_chunks = []
            for chunk in self.engine.generate(prompt):
                response_chunks.append(chunk)
                if self.config.verbose:
                    yield chunk
            
            full_response = ''.join(response_chunks)
            
            # Parse response
            action_type, content = self._parse_response(full_response)
            
            if action_type == "done":
                yield f"\n\n✅ Task complete: {content}\n"
                self.history.append(AgentMessage(role="assistant", content=content))
                return
            
            elif action_type == "tool":
                tool_name = content["name"]
                args = content["args"]
                
                if self.config.verbose:
                    yield f"\n🔧 Using tool: {tool_name}({json.dumps(args)})\n"
                
                # Execute tool
                result = self._execute_tool(tool_name, args)
                
                if self.config.verbose:
                    yield f"📤 Result: {result[:200]}...\n" if len(result) > 200 else f"📤 Result: {result}\n"
                
                # Add to history
                self.history.append(AgentMessage(
                    role="tool",
                    content=f"Called {tool_name}",
                    tool_name=tool_name,
                    tool_result=result
                ))
                
                # Log for hallucination detection
                if self.fault_tree:
                    self.fault_tree.log_output(result)
            
            else:
                # Continue - add response to history
                self.history.append(AgentMessage(role="assistant", content=content))
            
            # Safety check each iteration
            safe, msg = self._check_safety()
            if not safe:
                yield f"\n⚠️ Safety halt: {msg}\n"
                return
        
        yield f"\n⚠️ Max iterations ({self.config.max_iterations}) reached\n"
    
    def run_sync(self, task: str) -> str:
        """Run synchronously and return final result."""
        result = []
        for chunk in self.run(task):
            result.append(chunk)
        return ''.join(result)


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """Command-line interface for micro-agent."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Micro-Agent Framework')
    parser.add_argument('--task', type=str, help='Task to execute')
    parser.add_argument('--tools', action='store_true', help='List available tools')
    parser.add_argument('--unsafe', action='store_true', help='Allow unsafe tools')
    parser.add_argument('--no-safety', action='store_true', help='Disable safety checks')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    
    args = parser.parse_args()
    
    if args.tools:
        print("🔧 AVAILABLE TOOLS")
        print("=" * 50)
        for name, tool in TOOL_REGISTRY.items():
            safe_str = "✅" if tool.is_safe else "⚠️"
            print(f"  {safe_str} {name}: {tool.description}")
            for param, info in tool.parameters.items():
                print(f"       - {param}: {info['type']}")
        return
    
    config = AgentConfig(
        allow_unsafe_tools=args.unsafe,
        enable_safety=not args.no_safety
    )
    
    agent = MicroAgent(config)
    
    if args.interactive:
        print("🤖 Micro-Agent Interactive Mode")
        print("   Type 'quit' to exit, 'tools' to list tools")
        print("=" * 50)
        
        while True:
            try:
                task = input("\n👤 You: ").strip()
                
                if task.lower() == 'quit':
                    break
                elif task.lower() == 'tools':
                    for name in TOOL_REGISTRY:
                        print(f"  • {name}")
                    continue
                elif not task:
                    continue
                
                print("\n🤖 Agent:")
                for chunk in agent.run(task):
                    print(chunk, end='', flush=True)
                    
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
    
    elif args.task:
        for chunk in agent.run(args.task):
            print(chunk, end='', flush=True)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
