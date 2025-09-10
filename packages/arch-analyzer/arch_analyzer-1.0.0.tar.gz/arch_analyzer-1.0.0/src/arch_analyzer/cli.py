#!/usr/bin/env python3
"""
Architecture Analyzer CLI Tool

A command-line tool that uses Claude Code agents to analyze source code architecture
design quality across multiple dimensions.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import tempfile
import time
import shutil
import pkg_resources


class ArchAnalyzer:
    """Main analyzer class that orchestrates multiple Claude Code agents."""
    
    # Define all available agents with their types
    AGENTS = {
        'modularity': 'modularity-analyzer',
        'dependency': 'dependency-analyzer', 
        'coupling': 'coupling-analyzer',
        'abstraction': 'abstraction-analyzer',
        'complexity': 'complexity-analyzer',
        'standard': 'standard-analyzer',
        'testability': 'testability-analyzer',
        'performance': 'performance-analyzer',
        'security': 'security-analyzer'
    }
    
    def __init__(self, target_path: str = None, json_mode: bool = False, debug_mode: bool = False):
        """Initialize the analyzer with target path."""
        self.target_path = target_path or os.getcwd()
        self.results = {}
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.json_mode = json_mode
        self.debug_mode = debug_mode
        
    def _log(self, message: str, level: str = "info"):
        """Log message only if not in JSON mode."""
        if not self.json_mode:
            print(message)
            
    def _colored_text(self, text: str, color: str) -> str:
        """Return colored text for terminal output."""
        if self.json_mode:
            return text
            
        colors = {
            'red': '\033[91m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'blue': '\033[94m',
            'magenta': '\033[95m',
            'cyan': '\033[96m',
            'white': '\033[97m',
            'bold': '\033[1m',
            'reset': '\033[0m'
        }
        
        return f"{colors.get(color, '')}{text}{colors.get('reset', '')}"
        
    def _print_readable_results(self, results: Dict[str, Any], show_detailed: bool = False):
        """Print results in a readable format with colors."""
        if self.json_mode:
            return
            
        print("\n" + "="*80)
        print(self._colored_text("ARCHITECTURE ANALYSIS RESULTS", "bold"))
        print("="*80)
        
        # Show detailed results if requested or if no summary available
        if show_detailed or "summary" not in results:
            if "detailed_results" in results:
                for agent_name, agent_result in results["detailed_results"].items():
                    self._print_agent_result(agent_name, agent_result)
                
        # Print summary (if available)
        if "summary" in results:
            self._print_summary(results["summary"])
            
    def _print_agent_result(self, agent_name: str, result: Dict[str, Any]):
        """Print individual agent result."""
        domain = result.get('domain', agent_name)
        score = result.get('score', 'N/A')
        
        print(f"\n📊 {self._colored_text(domain.upper(), 'cyan')} (Score: {self._colored_text(str(score), 'bold')}/5.0)")
        print("-" * 60)
        
        # Good points
        good_value = result.get('good')
        if good_value:
            print(f"\n✅ {self._colored_text('优势', 'green')}:")
            if isinstance(good_value, str):
                print(f"   {self._colored_text(good_value, 'green')}")
            elif isinstance(good_value, list):
                for i, item in enumerate(good_value, 1):  # Show all items
                    print(f"   {i}. {self._colored_text(str(item), 'green')}")
            else:
                print(f"   {self._colored_text(str(good_value), 'green')}")
            
        # Issues
        if result.get('bad') and isinstance(result['bad'], list):
            print(f"\n❌ {self._colored_text('主要问题', 'red')}:")
            for i, issue in enumerate(result['bad'], 1):  # Show all issues
                if isinstance(issue, dict):
                    severity = issue.get('severity', 'medium')
                    issue_text = issue.get('issue', '')
                    severity_color = {'high': 'red', 'medium': 'yellow', 'low': 'white'}.get(severity, 'white')
                    print(f"   {i}. [{self._colored_text(severity.upper(), severity_color)}] {self._colored_text(issue_text, severity_color)}")
                    
        # Recommendations  
        if result.get('recommendations') and isinstance(result['recommendations'], list):
            print(f"\n💡 {self._colored_text('改进建议', 'yellow')}:")
            for i, rec in enumerate(result['recommendations'], 1):  # Show all recommendations
                if isinstance(rec, dict):
                    priority = rec.get('priority', 'medium')
                    action = rec.get('action', '')
                    priority_color = {'high': 'red', 'medium': 'yellow', 'low': 'white'}.get(priority, 'white')
                    print(f"   {i}. [{self._colored_text(priority.upper(), priority_color)}] {self._colored_text(action, 'white')}")
                    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print overall summary."""
        print(f"\n🎯 {self._colored_text('综合分析总结', 'bold')}")
        print("=" * 80)
        
        # Overall score
        score = summary.get('score', 'N/A')
        score_color = 'green' if isinstance(score, (int, float)) and score >= 3.5 else 'yellow' if isinstance(score, (int, float)) and score >= 2.5 else 'red'
        print(f"\n📈 总体评分: {self._colored_text(str(score), score_color)}/5.0")
        
        # Good summary
        good_value = summary.get('good')
        if good_value:
            print(f"\n✅ {self._colored_text('整体优势', 'green')}:")
            if isinstance(good_value, str):
                print(f"   {self._colored_text(good_value, 'green')}")
            elif isinstance(good_value, list):
                for i, item in enumerate(good_value, 1):  # Show all items
                    print(f"   {i}. {self._colored_text(str(item), 'green')}")
            else:
                print(f"   {self._colored_text(str(good_value), 'green')}")
            
        # Issues - show all
        if summary.get('bad') and isinstance(summary['bad'], list):
            print(f"\n❌ {self._colored_text('关键问题', 'red')}:")
            issues = summary['bad']
            
            for i, issue in enumerate(issues, 1):
                if isinstance(issue, dict):
                    severity = issue.get('severity', 'medium')
                    issue_text = issue.get('issue', '')
                    severity_color = {'high': 'red', 'medium': 'yellow', 'low': 'white'}.get(severity, 'white')
                    print(f"   {i}. [{self._colored_text(severity.upper(), severity_color)}] {self._colored_text(issue_text, severity_color)}")
                    
        # Recommendations - show all
        if summary.get('recommendations') and isinstance(summary['recommendations'], list):
            print(f"\n💡 {self._colored_text('改进建议', 'yellow')}:")
            recommendations = summary['recommendations']
            
            for i, rec in enumerate(recommendations, 1):
                if isinstance(rec, dict):
                    priority = rec.get('priority', 'medium')
                    action = rec.get('action', '')
                    priority_color = {'high': 'red', 'medium': 'yellow', 'low': 'white'}.get(priority, 'white')
                    print(f"   {i}. [{self._colored_text(priority.upper(), priority_color)}] {self._colored_text(action, 'white')}")
                    
        print("\n" + "="*80)
        
    def _run_claude_code_agents(self, selected_agents: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Run multiple Claude Code agents simultaneously and return parsed JSON results."""
        try:
            # Change to target directory for analysis
            original_cwd = os.getcwd()
            os.chdir(self.target_path)
            
            try:
                # Create comprehensive prompt to invoke all selected sub-agents
                agent_list = ", ".join([f"{agent_type}" for agent_type in selected_agents.values()])
                agent_names = ", ".join(selected_agents.keys())
                
                prompt = f"""使用以下子代理分析此代码库：{agent_list}

重要：将每个子代理返回的结果以原始JSON格式输出，完全按照子代理返回的格式。不要修改、重新格式化或添加任何注释到JSON输出中。每个子代理应该返回一个完整的JSON对象。

要运行的代理：{agent_names}

请运行每个子代理并直接输出它们的原始JSON结果，一个接一个。"""
                
                self._log(f"Running analysis with agents: {agent_names}")
                self._log("Executing Claude Code with multiple subagents...")
                
                # Run Claude Code with multiple sub-agents
                cmd = ['claude', '-p', prompt]
                
                # Execute the command
                start_time = time.time()
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=600  # 10 minute timeout for multiple agents
                )
                duration = time.time() - start_time
                
                if result.returncode != 0:
                    self._log(f"Warning: Multi-agent analysis failed with exit code {result.returncode}")
                    self._log(f"Error: {result.stderr}")
                    return {}
                    
                self._log(f"✓ Multi-agent analysis completed in {duration:.1f}s")
                
                # Debug: Save raw output for inspection
                if self.debug_mode:
                    debug_file = os.path.join(self.target_path, 'claude_debug_output.txt')
                    try:
                        with open(debug_file, 'w', encoding='utf-8') as f:
                            f.write("=== Claude Code Raw Output ===\n")
                            f.write(f"Command: {' '.join(cmd)}\n")
                            f.write(f"Duration: {duration:.1f}s\n")
                            f.write(f"Return Code: {result.returncode}\n")
                            f.write(f"Output Length: {len(result.stdout)} characters\n")
                            f.write("=== STDOUT ===\n")
                            f.write(result.stdout)
                            f.write("\n=== STDERR ===\n")
                            f.write(result.stderr)
                        self._log(f"Debug: Raw output saved to {debug_file}")
                    except Exception as e:
                        self._log(f"Debug: Failed to save output: {e}")
                        
                if not self.json_mode:
                    self._log(f"Debug: Raw output length: {len(result.stdout)} characters")
                    # Save first 500 characters for debugging
                    preview = result.stdout[:500].replace('\n', '\\n')
                    self._log(f"Debug: Output preview: {preview}...")
                
                # Parse the output to extract individual agent results
                return self._parse_multi_agent_output(result.stdout, selected_agents)
                    
            finally:
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            self._log(f"Warning: Multi-agent analysis timed out after 10 minutes")
            return {}
        except Exception as e:
            self._log(f"Error running multi-agent analysis: {e}")
            return {}
            
    def _parse_multi_agent_output(self, output_text: str, selected_agents: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Parse Claude Code output containing multiple agent results."""
        results = {}
        
        # Debug logging
        self._log(f"Debug: Parsing output for agents: {list(selected_agents.keys())}")
        
        # Try to extract JSON blocks from the output
        import re
        
        # Look for JSON blocks (might be wrapped in markdown code blocks)
        json_blocks = re.findall(r'```json\s*(.*?)\s*```', output_text, re.DOTALL)
        self._log(f"Debug: Found {len(json_blocks)} JSON code blocks")
        
        if not json_blocks:
            # Try to find JSON objects directly (more flexible pattern)
            json_pattern = r'\{(?:[^{}]|(?:\{[^{}]*\})*)*\}'
            json_blocks = re.findall(json_pattern, output_text, re.DOTALL)
            self._log(f"Debug: Found {len(json_blocks)} direct JSON objects")
            
        # Also try to find JSON objects that might span multiple lines with nested structures
        if not json_blocks:
            # More aggressive JSON detection
            lines = output_text.split('\n')
            current_json = ""
            brace_count = 0
            in_json = False
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('{'):
                    if not in_json:
                        current_json = ""
                        in_json = True
                    current_json += line + '\n'
                    brace_count += stripped.count('{') - stripped.count('}')
                elif in_json:
                    current_json += line + '\n'
                    brace_count += stripped.count('{') - stripped.count('}')
                    
                if in_json and brace_count == 0:
                    json_blocks.append(current_json.strip())
                    in_json = False
                    current_json = ""
                    
            self._log(f"Debug: Found {len(json_blocks)} JSON objects via line-by-line parsing")
        
        # Parse each JSON block and try to match with agents
        parsed_count = 0
        for i, json_text in enumerate(json_blocks):
            json_text = json_text.strip()
            if not json_text:
                continue
                
            try:
                json_data = json.loads(json_text)
                parsed_count += 1
                self._log(f"Debug: Successfully parsed JSON block {i+1}")
                
                # Try to identify which agent this result belongs to
                if isinstance(json_data, dict) and 'domain' in json_data:
                    domain = json_data['domain']
                    self._log(f"Debug: Found domain '{domain}' in JSON block {i+1}")
                    
                    # Find matching agent by domain
                    for agent_key, agent_type in selected_agents.items():
                        # Map domain names to agent keys
                        domain_mapping = {
                            '模块化': 'modularity',
                            '依赖方向': 'dependency',
                            '耦合与内聚': 'coupling',
                            '抽象层次': 'abstraction',
                            '复杂度': 'complexity',
                            '一致性与规范': 'standard',
                            '可测性': 'testability',
                            '性能与弹性': 'performance',
                            '安全与合规': 'security'
                        }
                        
                        if domain in domain_mapping and domain_mapping[domain] == agent_key:
                            results[agent_key] = json_data
                            self._log(f"✓ Parsed {agent_key} result with score: {json_data.get('score', 'N/A')}")
                            break
                    else:
                        self._log(f"Debug: No matching agent found for domain '{domain}'")
                else:
                    self._log(f"Debug: JSON block {i+1} missing 'domain' field or not a dict")
                    # Try to match by position if domain is missing
                    if parsed_count <= len(selected_agents):
                        agent_keys = list(selected_agents.keys())
                        if parsed_count - 1 < len(agent_keys):
                            agent_key = agent_keys[parsed_count - 1]
                            results[agent_key] = json_data
                            self._log(f"✓ Parsed {agent_key} result by position (no domain field)")
                
            except json.JSONDecodeError as e:
                self._log(f"Warning: Could not parse JSON block {i+1}: {e}")
                self._log(f"Debug: Problematic JSON preview: {json_text[:200]}...")
                continue
                
        self._log(f"Debug: Total parsed {parsed_count} JSON blocks, matched {len(results)} agents")
        
        # If no results were parsed, try alternative parsing
        if not results:
            self._log("Warning: No structured JSON results found, attempting alternative parsing...")
            # Fallback: look for any valid JSON and try to infer agent
            try:
                # Try to parse the entire output as JSON
                json_data = json.loads(output_text.strip())
                if isinstance(json_data, dict) and 'domain' in json_data:
                    # Single result
                    domain = json_data['domain']
                    for agent_key in selected_agents:
                        if domain in json_data.get('domain', ''):
                            results[agent_key] = json_data
                            break
            except:
                pass
                
        return results
    
    def _check_and_install_agents(self, force_install: bool = False) -> bool:
        """Check if all required agents are installed and install them if missing."""
        self._log("Checking Claude Code sub-agents installation...")
        
        # Use user-level Claude agents directory
        claude_agents_dir = Path.home() / '.claude' / 'agents'
        
        # Get agents from package resources
        try:
            # List all .md files in the agents package directory
            agents_package = 'arch_analyzer.agents'
            if pkg_resources.resource_exists(agents_package, ''):
                agent_names = [f for f in pkg_resources.resource_listdir(agents_package, '') 
                              if f.endswith('.md') and f != '__init__.py']
            else:
                self._log("Error: agents package not found")
                return False
                
            if not agent_names:
                self._log("Warning: No agent files found in package")
                return True
        except Exception as e:
            self._log(f"Error: Could not access agents package: {e}")
            return False
            
        # Create .claude/agents directory if it doesn't exist
        claude_agents_dir.mkdir(parents=True, exist_ok=True)
        
        if force_install:
            self._log("Force reinstalling all sub-agents...")
            agents_to_install = [name.replace('.md', '') for name in agent_names]
        else:
            # Check each required agent
            missing_agents = []
            for agent_name in agent_names:
                agent_base = agent_name.replace('.md', '')
                target_file = claude_agents_dir / agent_name
                
                if not target_file.exists():
                    missing_agents.append(agent_base)
                    
            if not missing_agents:
                self._log("✓ All sub-agents are already installed")
                return True
                
            self._log(f"Missing agents: {', '.join(missing_agents)}")
            self._log("Installing missing sub-agents...")
            agents_to_install = missing_agents
        
        # Copy agent files from package resources
        installed_count = 0
        agents_package = 'arch_analyzer.agents'
        for agent_name in agent_names:
            agent_base = agent_name.replace('.md', '')
            if agent_base in agents_to_install:
                target_file = claude_agents_dir / agent_name
                
                try:
                    # Read agent content from package resources
                    agent_content = pkg_resources.resource_string(agents_package, agent_name).decode('utf-8')
                    
                    # Write to target file
                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(agent_content)
                        
                    self._log(f"✓ {'Reinstalled' if force_install else 'Installed'} {agent_base}")
                    installed_count += 1
                except Exception as e:
                    self._log(f"✗ Failed to {'reinstall' if force_install else 'install'} {agent_base}: {e}")
                    
        if installed_count > 0:
            action = "reinstalled" if force_install else "installed"
            self._log(f"Successfully {action} {installed_count} sub-agents to {claude_agents_dir}")
            return True
        else:
            action = "reinstall" if force_install else "install"
            self._log(f"Failed to {action} any sub-agents")
            return False
    
    def _verify_agent_installation(self) -> bool:
        """Verify that Claude Code can access the installed agents."""
        try:
            # Try to run Claude Code with a simple command to check agent availability
            result = subprocess.run(
                ['claude', '--help'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self._log("Warning: Claude Code CLI not responding properly")
                return False
                
            self._log("✓ Claude Code CLI is accessible")
            return True
            
        except subprocess.TimeoutExpired:
            self._log("Warning: Claude Code CLI timeout")
            return False
        except Exception as e:
            self._log(f"Warning: Could not verify Claude Code: {e}")
            return False
            
    def _check_and_create_claude_md(self) -> bool:
        """Check if CLAUDE.md exists in target directory, create if missing."""
        claude_md_path = os.path.join(self.target_path, 'CLAUDE.md')
        
        if os.path.exists(claude_md_path):
            self._log("✓ CLAUDE.md already exists in target directory")
            return True
            
        self._log("CLAUDE.md not found, creating with Claude Code init...")
        
        try:
            # Change to target directory
            original_cwd = os.getcwd()
            os.chdir(self.target_path)
            
            try:
                # Run claude init command
                result = subprocess.run(
                    ['claude', '-p', '/init', '--dangerously-skip-permissions'],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    # Verify CLAUDE.md was created
                    if os.path.exists(claude_md_path):
                        self._log("✓ CLAUDE.md created successfully")
                        return True
                    else:
                        self._log("Warning: Claude init completed but CLAUDE.md not found")
                        return False
                else:
                    self._log(f"Warning: Claude init failed with exit code {result.returncode}")
                    self._log(f"Error: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_cwd)
                
        except subprocess.TimeoutExpired:
            self._log("Warning: Claude init timed out")
            return False
        except Exception as e:
            self._log(f"Error running Claude init: {e}")
            return False
            
    def _run_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """Run all selected agents using Claude Code's native multi-agent support."""
        self._log(f"\n=== Starting Claude Code multi-agent analysis ===")
        self._log(f"Agents to run: {', '.join(self.AGENTS.keys())}")
        
        # Use Claude Code's native multi-agent capability
        results = self._run_claude_code_agents(self.AGENTS)
        
        self._log(f"\n=== Multi-agent analysis completed ===")
        self._log(f"Successful: {len(results)}/{len(self.AGENTS)} agents")
                
        return results
        
    def _calculate_overall_score(self, results: Dict[str, Dict[str, Any]]) -> float:
        """Calculate the overall average score from all agent results."""
        scores = []
        for result in results.values():
            if 'score' in result and isinstance(result['score'], (int, float)):
                scores.append(float(result['score']))
                
        if not scores:
            return 0.0
            
        return round(sum(scores) / len(scores), 1)
        
    def _merge_issues_and_recommendations(self, results: Dict[str, Dict[str, Any]]) -> tuple:
        """Merge and deduplicate issues and recommendations from all agents."""
        all_bad = []
        all_recommendations = []
        
        # Collect all issues and recommendations
        for domain, result in results.items():
            if 'bad' in result and isinstance(result['bad'], list):
                for issue in result['bad']:
                    if isinstance(issue, dict):
                        all_bad.append({
                            'severity': issue.get('severity', 'medium'),
                            'issue': f"[{result.get('domain', domain)}] {issue.get('issue', '')}"
                        })
                    elif isinstance(issue, str):
                        # Handle string format issues
                        all_bad.append({
                            'severity': 'medium',
                            'issue': f"[{result.get('domain', domain)}] {issue}"
                        })
                    
            if 'recommendations' in result and isinstance(result['recommendations'], list):
                for rec in result['recommendations']:
                    if isinstance(rec, dict):
                        all_recommendations.append({
                            'priority': rec.get('priority', 'medium'), 
                            'action': f"[{result.get('domain', domain)}] {rec.get('action', '')}"
                        })
                    elif isinstance(rec, str):
                        # Handle string format recommendations
                        all_recommendations.append({
                            'priority': 'medium',
                            'action': f"[{result.get('domain', domain)}] {rec}"
                        })
        
        # Sort by severity/priority and limit to 10 items each
        severity_order = {'high': 0, 'medium': 1, 'low': 2}
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        
        all_bad.sort(key=lambda x: severity_order.get(x['severity'], 1))
        all_recommendations.sort(key=lambda x: priority_order.get(x['priority'], 1))
        
        return all_bad[:10], all_recommendations[:10]
        
    def _generate_summary_with_claude(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Use Claude Code to generate a comprehensive summary."""
        try:
            # Prepare the analysis data for Claude
            analysis_prompt = f"""
基于以上来自多个专业分析代理的架构分析结果，请提供一个综合总结，严格遵循以下JSON格式：

{{
  "score": x.x,
  "good": "整体优势的简要总结",
  "bad": [
    {{"severity": "high/medium/low", "issue": "问题描述"}}
  ],
  "recommendations": [
    {{"priority": "high/medium/low", "action": "改进建议描述"}}
  ]
}}

要求：
- 分数应该是所有代理分数的平均值：{self._calculate_overall_score(results)}
- good 应该用一句话总结主要的架构优势
- bad 应该列出最多10个最关键的问题，按严重性排序（合并相似问题）
- recommendations 应该列出最多10个最重要的改进措施，按优先级排序（合并相似建议）
- 专注于所有维度中最有影响力的发现
- 使用清晰、可执行的语言
- 所有输出内容必须使用中文
"""

            # Run Claude Code for summarization
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(analysis_prompt)
                prompt_file = f.name
                
            try:
                original_cwd = os.getcwd()
                os.chdir(self.target_path)
                
                # Read the prompt and pass it as argument to claude
                with open(prompt_file, 'r') as f:
                    prompt_content = f.read()
                
                cmd = ['claude', '-c', '-p', prompt_content]
                
                self._log("Generating comprehensive summary...")
                start_time = time.time()
                result = subprocess.run(
                    cmd,
                    capture_output=True, 
                    text=True,
                    timeout=300
                )
                duration = time.time() - start_time
                
                # Debug: Save raw output for inspection
                if self.debug_mode:
                    debug_file = os.path.join(self.target_path, 'claude_debug_output.txt')
                    try:
                        with open(debug_file, 'a', encoding='utf-8') as f:
                            f.write("\n\n=== Claude Code Summary Raw Output ===\n")
                            f.write(f"Command: {' '.join(cmd[:1])} [SUMMARY_PROMPT]\n")
                            f.write(f"Duration: {duration:.1f}s\n")
                            f.write(f"Return Code: {result.returncode}\n")
                            f.write(f"Output Length: {len(result.stdout)} characters\n")
                            f.write("=== STDOUT ===\n")
                            f.write(result.stdout)
                            f.write("\n=== STDERR ===\n")
                            f.write(result.stderr)
                            f.write("\n=== PROMPT CONTENT ===\n")
                            f.write(prompt_content)
                        self._log(f"Debug: Summary raw output appended to {debug_file}")
                    except Exception as e:
                        self._log(f"Debug: Failed to save summary output: {e}")
                
                if result.returncode == 0:
                    try:
                        summary = json.loads(result.stdout)
                        return summary
                    except json.JSONDecodeError:
                        # Try to extract JSON from the output
                        import re
                        json_match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
                        if json_match:
                            try:
                                summary = json.loads(json_match.group())
                                self._log("✓ Extracted JSON from Claude output successfully")
                                return summary
                            except json.JSONDecodeError:
                                pass
                        self._log("Warning: Could not parse summary JSON, using fallback")
                        
            finally:
                os.chdir(original_cwd)
                os.unlink(prompt_file)
                
        except Exception as e:
            self._log(f"Warning: Could not generate Claude summary: {e}")
            
        # Fallback to simple aggregation
        return self._generate_fallback_summary(results)
        
    def _generate_fallback_summary(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a fallback summary when Claude Code is not available."""
        score = self._calculate_overall_score(results)
        
        # Collect good points
        good_points = []
        for result in results.values():
            good_value = result.get('good')
            if good_value:
                # Handle both string and list formats
                if isinstance(good_value, str):
                    good_points.append(good_value)
                elif isinstance(good_value, list):
                    # If it's a list, join the items or take the first few
                    if good_value:
                        good_points.extend([str(item) for item in good_value[:2]])  # Limit to 2 items per agent
                        
        good_summary = "Architecture shows solid foundation" if good_points else "Architecture needs improvement"
        if len(good_points) > 1:
            good_summary = f"Strong points: {', '.join(good_points[:2])}"
            
        # Merge issues and recommendations
        bad_issues, recommendations = self._merge_issues_and_recommendations(results)
        
        return {
            'score': score,
            'good': good_summary,
            'bad': bad_issues,
            'recommendations': recommendations
        }
        
    def analyze(self, agents: List[str] = None, force_install: bool = False) -> Dict[str, Any]:
        """Run the complete architecture analysis using Claude Code's multi-agent capability."""
        self._log(f"Starting architecture analysis of: {self.target_path}")
        self._log(f"Analyzing with agents: {', '.join(agents or self.AGENTS.keys())}")
        
        # Filter agents if specific ones requested
        if agents:
            filtered_agents = {k: v for k, v in self.AGENTS.items() if k in agents}
        else:
            filtered_agents = self.AGENTS
            
        # Update the agents to run
        original_agents = self.AGENTS.copy()
        self.AGENTS = filtered_agents
        
        try:
            # Check and install required sub-agents before running analysis
            if not self._check_and_install_agents(force_install):
                self._log("Error: Failed to install required sub-agents")
                return {'error': 'Sub-agent installation failed'}
                
            if not self._verify_agent_installation():
                self._log("Warning: Could not verify Claude Code installation, proceeding anyway...")
            
            # Check if CLAUDE.md exists in target directory, create if missing
            if not self._check_and_create_claude_md():
                self._log("Error: Failed to create CLAUDE.md file")
                return {'error': 'CLAUDE.md creation failed'}
            
            # Run all selected agents using Claude Code's native capability
            agent_results = self._run_all_agents()
            
            if not agent_results:
                self._log("Error: No agents completed successfully")
                return {'error': 'No successful analysis results'}
            
            # Only generate summary if all agents are selected (not specific agents)
            if agents is None:
                # Generate comprehensive summary for complete analysis
                self._log("\n=== Generating Summary ===")
                summary = self._generate_summary_with_claude(agent_results)
                
                # Combine summary and detailed results
                final_result = {
                    'summary': summary,
                    'detailed_results': agent_results
                }
                
                self._log(f"\n=== Analysis Complete ===")
                self._log(f"Overall Score: {summary.get('score', 'N/A')}/5.0")
                self._log(f"Agents Completed: {len(agent_results)}/{len(filtered_agents)}")
            else:
                # Return only detailed results for specific agents
                final_result = {
                    'detailed_results': agent_results
                }
                
                self._log(f"\n=== Analysis Complete ===")
                self._log(f"Agents Completed: {len(agent_results)}/{len(filtered_agents)}")
            
            return final_result
            
        finally:
            # Restore original agents
            self.AGENTS = original_agents


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Analyze source code architecture using Claude Code agents'
    )
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to the codebase to analyze (default: current directory)'
    )
    parser.add_argument(
        '--agents',
        nargs='+',
        choices=list(ArchAnalyzer.AGENTS.keys()),
        help='Specific agents to run (default: all agents)'
    )
    parser.add_argument(
        '--output',
        '-o',
        help='Output file for JSON results (default: stdout)'
    )
    parser.add_argument(
        '--pretty',
        action='store_true',
        help='Pretty print JSON output'
    )
    parser.add_argument(
        '--list-agents',
        action='store_true',
        help='List available agents and exit'
    )
    parser.add_argument(
        '--force-install',
        action='store_true',
        help='Force reinstall all sub-agents from agents/ directory'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='JSON mode: output only JSON data without any process logs'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Debug mode: save Claude Code raw output to debug.txt for inspection'
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed results from each agent (default: summary only)'
    )
    
    args = parser.parse_args()
    
    # List agents if requested
    if args.list_agents:
        print("Available agents:")
        for key, agent_type in ArchAnalyzer.AGENTS.items():
            print(f"  {key}: {agent_type}")
        return 0
        
    # Validate path
    target_path = os.path.abspath(args.path)
    if not os.path.exists(target_path):
        print(f"Error: Path does not exist: {target_path}")
        return 1
        
    if not os.path.isdir(target_path):
        print(f"Error: Path is not a directory: {target_path}")
        return 1
        
    # Check for Claude Code availability
    try:
        subprocess.run(['claude', '--help'], 
                      capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        if not getattr(args, 'json', False):
            print("Error: Claude Code CLI is not available or not in PATH")
            print("Please install Claude Code first")
        else:
            print(json.dumps({"error": "Claude Code CLI is not available or not in PATH"}, ensure_ascii=False))
        return 1
        
    # Handle force install option
    if args.force_install:
        if not args.json:
            print("Force installing all sub-agents...")
        analyzer = ArchAnalyzer(target_path, json_mode=args.json)
        if analyzer._check_and_install_agents(force_install=True):
            if not args.json:
                print("✓ All sub-agents have been reinstalled")
        else:
            if not args.json:
                print("✗ Failed to reinstall sub-agents")
        return 0
    
    # Run analysis
    analyzer = ArchAnalyzer(target_path, json_mode=args.json, debug_mode=args.debug)
    results = analyzer.analyze(agents=args.agents)
    
    # Handle errors
    if 'error' in results:
        if args.json:
            json_output = json.dumps({"error": results['error']}, ensure_ascii=False)
            print(json_output)
        else:
            print(f"Analysis failed: {results['error']}")
        return 1
    
    # Output results
    if args.json or args.output:
        # JSON output mode - adjust structure based on agents selection and detailed flag
        if args.agents is not None:
            # For specific agents, output only detailed results without summary wrapper
            output_data = results.get('detailed_results', {})
        else:
            # For complete analysis, choose output based on --detailed flag
            if args.detailed:
                # Show full structure with summary and detailed results
                output_data = results
            else:
                # Show only summary by default
                output_data = results.get('summary', {})
        
        indent = 2 if args.pretty else None
        json_output = json.dumps(output_data, indent=indent, ensure_ascii=False)
        
        if args.output:
            try:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(json_output)
                if not args.json:
                    print(f"Results written to: {args.output}")
            except Exception as e:
                if args.json:
                    print(json.dumps({"error": f"Failed to write file: {e}"}, ensure_ascii=False))
                else:
                    print(f"Error writing to file: {e}")
                return 1
        else:
            # JSON mode - output JSON to stdout
            print(json_output)
    else:
        # Readable terminal output mode
        analyzer._print_readable_results(results, show_detailed=args.detailed)
        
    return 0


if __name__ == '__main__':
    sys.exit(main())