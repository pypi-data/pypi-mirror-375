"""
Command-line interface for Cost Katana
"""

import argparse
import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

try:
    from . import configure, create_generative_model, CostKatanaClient
    from .config import Config
    from .exceptions import CostKatanaError
except ImportError:
    # Handle case when running as script
    from cost_katana.config import Config
    from cost_katana.exceptions import CostKatanaError

console = Console()


def create_sample_config():
    """Create a sample configuration file"""
    sample_config = {
        "api_key": "dak_your_api_key_here",
        "base_url": "https://cost-katana-backend.store",
        "default_model": "gemini-2.0-flash",
        "default_temperature": 0.7,
        "default_max_tokens": 2000,
        "cost_limit_per_day": 50.0,
        "enable_analytics": True,
        "enable_optimization": True,
        "enable_failover": True,
        "model_mappings": {
            "gemini": "gemini-2.0-flash-exp",
            "claude": "anthropic.claude-3-sonnet-20240229-v1:0",
            "gpt4": "gpt-4-turbo-preview",
        },
        "providers": {
            "google": {"priority": 1, "models": ["gemini-2.0-flash", "gemini-pro"]},
            "anthropic": {
                "priority": 2,
                "models": ["claude-3-sonnet", "claude-3-haiku"],
            },
            "openai": {"priority": 3, "models": ["gpt-4", "gpt-3.5-turbo"]},
        },
    }
    return sample_config


def init_config(args):
    """Initialize configuration"""
    config_path = Path(args.config or "cost_katana_config.json")

    if config_path.exists() and not args.force:
        console.print(f"[yellow]Configuration file already exists: {config_path}[/yellow]")
        if not Confirm.ask("Overwrite existing configuration?"):
            return

    console.print("[bold blue]Setting up Cost Katana configuration...[/bold blue]")

    # Get API key
    api_key = Prompt.ask(
        "Enter your Cost Katana API key", default=args.api_key if args.api_key else None
    )

    # Get base URL
    base_url = Prompt.ask("Enter base URL", default="https://cost-katana-backend.store")

    # Get default model
    default_model = Prompt.ask(
        "Enter default model",
        default="gemini-2.0-flash",
        choices=["gemini-2.0-flash", "claude-3-sonnet", "gpt-4", "nova-pro"],
    )

    # Create configuration
    config_data = create_sample_config()
    config_data.update({"api_key": api_key, "base_url": base_url, "default_model": default_model})

    # Save configuration
    try:
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        console.print(f"[green]Configuration saved to: {config_path}[/green]")
        console.print("\n[bold]Next steps:[/bold]")
        console.print("1. Test the configuration: [cyan]cost-katana test[/cyan]")
        console.print("2. Start a chat session: [cyan]cost-katana chat[/cyan]")
        console.print("3. See available models: [cyan]cost-katana models[/cyan]")

    except Exception as e:
        console.print(f"[red]Failed to save configuration: {e}[/red]")
        sys.exit(1)


def test_connection(args):
    """Test connection to Cost Katana API"""
    try:
        config_path = args.config or "cost_katana_config.json"

        if Path(config_path).exists():
            configure(config_file=config_path)
        elif args.api_key:
            configure(api_key=args.api_key)
        else:
            console.print("[red]No configuration found. Run 'cost-katana init' first.[/red]")
            return

        console.print("[bold blue]Testing Cost Katana connection...[/bold blue]")

        # Test with a simple model
        model = create_generative_model("gemini-2.0-flash")
        response = model.generate_content(
            "Hello! Please respond with just 'OK' to test the connection."
        )

        console.print(
            Panel(
                f"[green]✓ Connection successful![/green]\n"
                f"Model: {response.usage_metadata.model}\n"
                f"Response: {response.text}\n"
                f"Cost: ${response.usage_metadata.cost:.4f}\n"
                f"Latency: {response.usage_metadata.latency:.2f}s",
                title="Test Results",
            )
        )

    except Exception as e:
        console.print(f"[red]✗ Connection failed: {e}[/red]")
        sys.exit(1)


def list_models(args):
    """List available models"""
    try:
        config_path = args.config or "cost_katana_config.json"

        if Path(config_path).exists():
            configure(config_file=config_path)
        elif args.api_key:
            configure(api_key=args.api_key)
        else:
            console.print("[red]No configuration found. Run 'cost-katana init' first.[/red]")
            return

        client = CostKatanaClient(config_file=config_path if Path(config_path).exists() else None)
        models = client.get_available_models()

        table = Table(title="Available Models")
        table.add_column("Model ID", style="cyan", no_wrap=True)
        table.add_column("Display Name", style="magenta")
        table.add_column("Provider", style="green")
        table.add_column("Type", style="yellow")

        for model in models:
            model_id = model.get("id", model.get("modelId", "Unknown"))
            name = model.get("name", model.get("displayName", model_id))
            provider = model.get("provider", "Unknown")
            model_type = model.get("type", "Text")

            table.add_row(model_id, name, provider, model_type)

        console.print(table)

    except Exception as e:
        console.print(f"[red]Failed to fetch models: {e}[/red]")
        sys.exit(1)


def start_chat(args):
    """Start an interactive chat session"""
    try:
        config_path = args.config or "cost_katana_config.json"

        if Path(config_path).exists():
            configure(config_file=config_path)
            config = Config.from_file(config_path)
        elif args.api_key:
            configure(api_key=args.api_key)
            config = Config(api_key=args.api_key)
        else:
            console.print("[red]No configuration found. Run 'cost-katana init' first.[/red]")
            return

        model_name = args.model or config.default_model

        console.print(
            Panel(
                f"[bold blue]Cost Katana Chat Session[/bold blue]\n"
                f"Model: {model_name}\n"
                f"Type 'quit' to exit, 'clear' to clear history",
                title="Welcome",
            )
        )

        model = create_generative_model(model_name)
        chat = model.start_chat()

        total_cost = 0.0

        while True:
            try:
                message = Prompt.ask("[bold cyan]You[/bold cyan]")

                if message.lower() in ["quit", "exit", "q"]:
                    break
                elif message.lower() == "clear":
                    chat.clear_history()
                    console.print("[yellow]Chat history cleared.[/yellow]")
                    continue
                elif message.lower() == "cost":
                    console.print(f"[green]Total session cost: ${total_cost:.4f}[/green]")
                    continue

                console.print("[bold green]Assistant[/bold green]: ", end="")

                with console.status("Thinking..."):
                    response = chat.send_message(message)

                console.print(response.text)

                # Show cost info
                total_cost += response.usage_metadata.cost
                console.print(
                    f"[dim]Cost: ${response.usage_metadata.cost:.4f} | "
                    f"Total: ${total_cost:.4f} | "
                    f"Tokens: {response.usage_metadata.total_tokens}[/dim]\n"
                )

            except KeyboardInterrupt:
                console.print("\n[yellow]Chat session interrupted.[/yellow]")
                break
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                continue

        console.print(f"\n[bold]Session Summary:[/bold]")
        console.print(f"Total Cost: ${total_cost:.4f}")
        console.print("Thanks for using Cost Katana!")

    except Exception as e:
        console.print(f"[red]Failed to start chat: {e}[/red]")
        sys.exit(1)


def get_prompt_from_args_or_file(args):
    """Get prompt from command line argument or file"""
    if hasattr(args, "prompt") and args.prompt:
        return args.prompt

    if hasattr(args, "file") and args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except FileNotFoundError:
            console.print(f"[red]Error: File '{args.file}' not found[/red]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error reading file: {e}[/red]")
            sys.exit(1)

    # Interactive input
    return Prompt.ask("Enter prompt to process")


def handle_sast_command(args):
    """Handle SAST subcommands"""
    if not args.sast_command:
        console.print("[red]Please specify a SAST subcommand. Use 'sast --help' for options.[/red]")
        return

    try:
        config_path = args.config or "cost_katana_config.json"

        if Path(config_path).exists():
            client = CostKatanaClient(config_file=config_path)
        elif args.api_key:
            client = CostKatanaClient(api_key=args.api_key)
        else:
            console.print(
                "[red]Error: No configuration found. Run 'cost-katana init' first or provide --api-key[/red]"
            )
            return

        if args.sast_command == "optimize":
            sast_optimize_command(client, args)
        elif args.sast_command == "compare":
            sast_compare_command(client, args)
        elif args.sast_command == "vocabulary":
            sast_vocabulary_command(client, args)
        elif args.sast_command == "telescope":
            sast_telescope_command(client, args)
        elif args.sast_command == "stats":
            sast_stats_command(client, args)
        elif args.sast_command == "showcase":
            sast_showcase_command(client, args)
        elif args.sast_command == "universal":
            sast_universal_command(client, args)

    except CostKatanaError as e:
        console.print(f"[red]SAST Error: {e}[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error: {e}[/red]")
        sys.exit(1)


def sast_optimize_command(client, args):
    """Handle SAST optimize command"""
    prompt = get_prompt_from_args_or_file(args)

    console.print("[blue]🧬 Optimizing with SAST...[/blue]")

    result = client.optimize_with_sast(
        prompt=prompt,
        language=args.language,
        cross_lingual=args.cross_lingual,
        preserve_ambiguity=args.preserve_ambiguity,
    )

    if result.get("success"):
        data = result["data"]

        # Display results
        console.print("\n[green]✅ SAST Optimization Complete[/green]")
        console.print("=" * 60)

        console.print(f"\n[cyan]Original Prompt:[/cyan]")
        console.print(Panel(data.get("originalPrompt", "N/A"), title="Original"))

        console.print(f"\n[cyan]Optimized Prompt:[/cyan]")
        console.print(Panel(data.get("optimizedPrompt", "N/A"), title="SAST Optimized"))

        # Metrics
        console.print(f"\n[cyan]📈 Optimization Metrics:[/cyan]")
        metrics_table = Table(show_header=True)
        metrics_table.add_column("Metric", style="cyan")
        metrics_table.add_column("Value", style="green")

        improvement = data.get("improvementPercentage", 0)
        tokens_saved = data.get("tokensSaved", 0)
        cost_saved = data.get("costSaved", 0)

        metrics_table.add_row("Token Reduction", f"{improvement:.1f}%")
        metrics_table.add_row("Tokens Saved", str(tokens_saved))
        metrics_table.add_row("Cost Saved", f"${cost_saved:.4f}")

        console.print(metrics_table)

        # SAST specific data
        if "metadata" in data and "sast" in data["metadata"]:
            sast_data = data["metadata"]["sast"]
            console.print(f"\n[magenta]🧬 SAST Analysis:[/magenta]")
            sast_table = Table(show_header=True)
            sast_table.add_column("Aspect", style="magenta")
            sast_table.add_column("Value", style="blue")

            sast_table.add_row(
                "Semantic Primitives",
                str(sast_data.get("semanticPrimitives", {}).get("totalVocabulary", 0)),
            )
            sast_table.add_row("Ambiguities Resolved", str(sast_data.get("ambiguitiesResolved", 0)))
            sast_table.add_row(
                "Universal Compatible", "✓" if sast_data.get("universalCompatibility") else "✗"
            )

            console.print(sast_table)

        # Save output if requested
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(data.get("optimizedPrompt", ""))
            console.print(f"\n[green]✅ Saved optimized prompt to: {args.output}[/green]")
    else:
        console.print(
            f"[red]❌ Optimization failed: {result.get('message', 'Unknown error')}[/red]"
        )


def sast_compare_command(client, args):
    """Handle SAST compare command"""
    prompt = get_prompt_from_args_or_file(args)

    console.print("[blue]⚖️ Comparing Traditional vs SAST...[/blue]")

    result = client.compare_sast_vs_traditional(prompt=prompt, language=args.language)

    if result.get("success"):
        data = result["data"]

        console.print("\n[green]✅ Comparison Complete[/green]")
        console.print("=" * 60)

        console.print(f"\n[cyan]📝 Input Text:[/cyan]")
        console.print(f'"{data.get("inputText", "")}"')

        # Comparison table
        comparison_table = Table(show_header=True, title="Traditional vs SAST Comparison")
        comparison_table.add_column("Metric", style="cyan")
        comparison_table.add_column("Traditional", style="yellow")
        comparison_table.add_column("SAST", style="magenta")
        comparison_table.add_column("Improvement", style="green")

        trad = data.get("traditionalCortex", {})
        sast = data.get("sastCortex", {})
        improvements = data.get("improvements", {})

        comparison_table.add_row(
            "Token Count",
            str(trad.get("tokenCount", 0)),
            str(sast.get("primitiveCount", 0)),
            f"{improvements.get('tokenReduction', 0):+.1f}%",
        )

        comparison_table.add_row(
            "Semantic Explicitness",
            f"{trad.get('semanticExplicitness', 0) * 100:.1f}%",
            f"{sast.get('semanticExplicitness', 0) * 100:.1f}%",
            f"{improvements.get('semanticClarityGain', 0) * 100:+.1f}%",
        )

        comparison_table.add_row(
            "Ambiguities",
            trad.get("ambiguityLevel", "N/A"),
            str(sast.get("ambiguitiesResolved", 0)) + " resolved",
            f"{improvements.get('ambiguityReduction', 0):+.1f}%",
        )

        console.print(comparison_table)

        recommended = data.get("metadata", {}).get("recommendedApproach", "unknown")
        console.print(f"\n[yellow]🎯 Recommended Approach: {recommended.upper()}[/yellow]")
    else:
        console.print(f"[red]❌ Comparison failed: {result.get('message', 'Unknown error')}[/red]")


def sast_vocabulary_command(client, args):
    """Handle SAST vocabulary command"""
    if args.search or args.category or args.language:
        console.print(f"[blue]📚 Searching SAST vocabulary...[/blue]")

        result = client.search_semantic_primitives(
            term=args.search, category=args.category, language=args.language, limit=args.limit
        )

        if result.get("success"):
            data = result["data"]
            console.print(
                f"\n[green]📚 Found {len(data.get('results', []))} semantic primitives[/green]"
            )

            for i, item in enumerate(data.get("results", []), 1):
                primitive = item["primitive"]
                console.print(f"\n[cyan]{i}. {primitive['baseForm']} ({primitive['id']})[/cyan]")
                console.print(f"   Category: {primitive['category']}")
                console.print(f"   Definition: {primitive['definition']}")
                console.print(f"   Relevance: {item['relevanceScore'] * 100:.1f}%")

                if primitive.get("synonyms"):
                    synonyms = primitive["synonyms"][:3]
                    console.print(
                        f"   Synonyms: {', '.join(synonyms)}{'...' if len(primitive['synonyms']) > 3 else ''}"
                    )
    else:
        console.print("[blue]📊 Getting SAST vocabulary statistics...[/blue]")

        result = client.get_sast_vocabulary_stats()

        if result.get("success"):
            data = result["data"]

            console.print(f"\n[green]📊 SAST Vocabulary Statistics[/green]")
            console.print(f"Total Primitives: [blue]{data.get('totalPrimitives', 0)}[/blue]")
            console.print(
                f"Average Translations: [cyan]{data.get('averageTranslations', 0):.1f}[/cyan]"
            )

            if "primitivesByCategory" in data:
                console.print("\n[yellow]📂 By Category:[/yellow]")
                for category, count in data["primitivesByCategory"].items():
                    console.print(f"  {category}: [blue]{count}[/blue]")

            if "coverageByLanguage" in data:
                console.print("\n[green]🌍 Language Coverage:[/green]")
                for lang, count in data["coverageByLanguage"].items():
                    console.print(f"  {lang.upper()}: [blue]{count}[/blue] terms")


def sast_telescope_command(client, args):
    """Handle SAST telescope demo command"""
    console.print("[blue]🔭 Running telescope ambiguity demonstration...[/blue]")

    result = client.get_telescope_demo()

    if result.get("success"):
        data = result["data"]
        explanation = data.get("explanation", {})
        stats = data.get("sastStats", {})

        console.print(f"\n[green]🔭 Telescope Ambiguity Demonstration[/green]")
        console.print("=" * 60)

        console.print(f"\n[cyan]📝 Original Sentence:[/cyan]")
        console.print(f'"{explanation.get("sentence", "")}"')

        console.print(f"\n[yellow]🤔 Ambiguity Type:[/yellow]")
        console.print(explanation.get("ambiguityType", ""))

        console.print(f"\n[cyan]💭 Possible Interpretations:[/cyan]")
        for i, interpretation in enumerate(explanation.get("interpretations", []), 1):
            console.print(f"  {i}. {interpretation}")

        console.print(f"\n[green]✅ SAST Resolution:[/green]")
        console.print(explanation.get("resolution", ""))

        console.print(f"\n[magenta]📊 SAST Performance:[/magenta]")
        perf_table = Table(show_header=True)
        perf_table.add_column("Metric", style="magenta")
        perf_table.add_column("Value", style="blue")

        perf_table.add_row("Ambiguities Resolved", str(stats.get("ambiguitiesResolved", 0)))
        perf_table.add_row("Semantic Accuracy", f"{stats.get('semanticAccuracy', 0) * 100:.1f}%")
        perf_table.add_row("Processing Time", f"{stats.get('averageProcessingTime', 0):.1f}ms")

        console.print(perf_table)


def sast_stats_command(client, args):
    """Handle SAST stats command"""
    console.print("[blue]📊 Fetching SAST performance statistics...[/blue]")

    result = client.get_sast_stats()

    if result.get("success"):
        data = result["data"]
        encoding = data.get("encoding", {})
        comparison = data.get("comparison", {})

        console.print(f"\n[green]📊 SAST Performance Statistics[/green]")
        console.print("=" * 60)

        console.print(f"\n[cyan]🧬 Encoding Performance:[/cyan]")
        enc_table = Table(show_header=True)
        enc_table.add_column("Metric", style="cyan")
        enc_table.add_column("Value", style="blue")

        total_encodings = encoding.get("totalEncodings", 0)
        successful = encoding.get("successfulEncodings", 0)
        success_rate = (successful / total_encodings * 100) if total_encodings > 0 else 0

        enc_table.add_row("Total Encodings", f"{total_encodings:,}")
        enc_table.add_row("Success Rate", f"{success_rate:.1f}%")
        enc_table.add_row("Ambiguities Resolved", f"{encoding.get('ambiguitiesResolved', 0):,}")
        enc_table.add_row("Avg Processing", f"{encoding.get('averageProcessingTime', 0):.2f}ms")
        enc_table.add_row("Semantic Accuracy", f"{encoding.get('semanticAccuracy', 0) * 100:.1f}%")

        console.print(enc_table)

        console.print(f"\n[magenta]⚖️ Comparison Performance:[/magenta]")
        comp_table = Table(show_header=True)
        comp_table.add_column("Metric", style="magenta")
        comp_table.add_column("Value", style="green")

        comp_table.add_row("Total Comparisons", f"{comparison.get('totalComparisons', 0):,}")
        comp_table.add_row(
            "SAST Wins",
            f"{comparison.get('sastWins', 0)} ({comparison.get('sastWinRate', 0):.1f}%)",
        )
        comp_table.add_row("Traditional Wins", str(comparison.get("traditionalWins", 0)))
        comp_table.add_row("Avg Improvement", f"{comparison.get('averageImprovement', 0):.1f}%")
        comp_table.add_row(
            "Ambiguity Resolution", f"{comparison.get('ambiguityResolutionRate', 0):.1f}%"
        )

        console.print(comp_table)


def sast_showcase_command(client, args):
    """Handle SAST showcase command"""
    console.print("[blue]🎯 Fetching SAST showcase...[/blue]")

    result = client.get_sast_showcase()

    if result.get("success"):
        data = result["data"]
        summary = data.get("summary", {})

        console.print(f"\n[green]🎯 SAST Showcase[/green]")
        console.print("=" * 60)

        # Summary stats
        summary_table = Table(show_header=True, title="SAST Summary Statistics")
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="green")

        summary_table.add_row("Total Examples", str(summary.get("totalExamples", 0)))
        summary_table.add_row(
            "Avg Token Reduction", f"{summary.get('averageTokenReduction', 0):.1f}%"
        )
        summary_table.add_row(
            "Universal Compatibility", f"{summary.get('universalCompatibility', 0) * 100:.0f}%"
        )
        summary_table.add_row(
            "Ambiguity Resolution", f"{summary.get('ambiguityResolutionRate', 0):.1f}%"
        )

        console.print(summary_table)

        # Show a few examples
        examples = data.get("examples", [])
        if examples:
            console.print(f"\n[cyan]📝 Example Comparisons:[/cyan]")
            for i, example in enumerate(examples[:3], 1):  # Show first 3 examples
                console.print(
                    f"\n[yellow]Example {i}: {example.get('category', 'Unknown')}[/yellow]"
                )
                console.print(f"Input: \"{example.get('input', '')}\"")

                improvements = example.get("improvements", {})
                console.print(
                    f"Token Reduction: [green]{improvements.get('tokenReduction', 0):.1f}%[/green]"
                )
                console.print(
                    f"Semantic Clarity: [blue]{improvements.get('semanticClarityGain', 0) * 100:.1f}%[/blue]"
                )


def sast_universal_command(client, args):
    """Handle SAST universal semantics test command"""
    languages = [lang.strip() for lang in args.languages.split(",")]

    console.print(
        f"[blue]🌍 Testing universal semantics for '{args.concept}' across {len(languages)} languages...[/blue]"
    )

    result = client.test_universal_semantics(concept=args.concept, languages=languages)

    if result.get("success"):
        data = result["data"]

        console.print(f"\n[green]🌍 Universal Test Results for: '{data.get('concept', '')}[/green]")
        console.print("=" * 60)

        unification_score = data.get("unificationScore", 0)
        is_universal = data.get("isUniversal", False)

        console.print(f"Unification Score: [blue]{unification_score * 100:.1f}%[/blue]")
        console.print(f"Universal Compatible: {'✓' if is_universal else '🔸 Partial'}")

        console.print(f"\n[cyan]🗣️ Translations:[/cyan]")
        translations = data.get("translations", {})
        for lang, translation in translations.items():
            console.print(f'  {lang.upper()}: "{translation}"')

        console.print(f"\n[magenta]🧬 SAST Representations:[/magenta]")
        representations = data.get("sastRepresentations", {})
        for lang, repr_data in representations.items():
            primitives_count = len(repr_data.get("primitives", {}))
            frame_type = repr_data.get("frameType", "unknown")
            console.print(f"  {lang.upper()}: {frame_type} frame ({primitives_count} primitives)")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Cost Katana - Unified AI interface with cost optimization"
    )
    parser.add_argument(
        "--config",
        "-c",
        help="Configuration file path (default: cost_katana_config.json)",
    )
    parser.add_argument("--api-key", "-k", help="Cost Katana API key")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize configuration")
    init_parser.add_argument("--force", action="store_true", help="Overwrite existing config")

    # Test command
    subparsers.add_parser("test", help="Test API connection")

    # Models command
    subparsers.add_parser("models", help="List available models")

    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Start interactive chat")
    chat_parser.add_argument("--model", "-m", help="Model to use for chat")

    # SAST commands
    sast_parser = subparsers.add_parser(
        "sast", help="SAST (Semantic Abstract Syntax Tree) operations"
    )
    sast_subparsers = sast_parser.add_subparsers(dest="sast_command", help="SAST commands")

    # SAST optimize command
    sast_optimize_parser = sast_subparsers.add_parser("optimize", help="Optimize prompt using SAST")
    sast_optimize_parser.add_argument("prompt", nargs="?", help="Prompt to optimize")
    sast_optimize_parser.add_argument("--file", "-f", help="File containing prompt to optimize")
    sast_optimize_parser.add_argument(
        "--language", "-l", default="en", help="Language for SAST processing"
    )
    sast_optimize_parser.add_argument("--model", "-m", default="gpt-4o-mini", help="Model to use")
    sast_optimize_parser.add_argument(
        "--cross-lingual", action="store_true", help="Enable cross-lingual mode"
    )
    sast_optimize_parser.add_argument(
        "--preserve-ambiguity", action="store_true", help="Preserve ambiguity for analysis"
    )
    sast_optimize_parser.add_argument("--output", "-o", help="Output file for results")

    # SAST compare command
    sast_compare_parser = sast_subparsers.add_parser(
        "compare", help="Compare traditional vs SAST optimization"
    )
    sast_compare_parser.add_argument("prompt", nargs="?", help="Prompt to compare")
    sast_compare_parser.add_argument("--file", "-f", help="File containing prompt")
    sast_compare_parser.add_argument("--language", "-l", default="en", help="Language for analysis")

    # SAST vocabulary command
    sast_vocab_parser = sast_subparsers.add_parser("vocabulary", help="Explore SAST vocabulary")
    sast_vocab_parser.add_argument("--search", "-s", help="Search term for primitives")
    sast_vocab_parser.add_argument("--category", "-c", help="Filter by category")
    sast_vocab_parser.add_argument("--language", "-l", help="Filter by language")
    sast_vocab_parser.add_argument("--limit", type=int, default=10, help="Limit results")

    # SAST demo commands
    sast_subparsers.add_parser("telescope", help="Telescope ambiguity demo")
    sast_subparsers.add_parser("stats", help="SAST performance statistics")
    sast_subparsers.add_parser("showcase", help="SAST showcase with examples")

    # SAST universal test command
    sast_universal_parser = sast_subparsers.add_parser("universal", help="Test universal semantics")
    sast_universal_parser.add_argument("concept", help="Concept to test universally")
    sast_universal_parser.add_argument(
        "--languages", default="en,es,fr", help="Comma-separated language codes"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Route to appropriate function
    if args.command == "init":
        init_config(args)
    elif args.command == "test":
        test_connection(args)
    elif args.command == "models":
        list_models(args)
    elif args.command == "chat":
        start_chat(args)
    elif args.command == "sast":
        handle_sast_command(args)


if __name__ == "__main__":
    main()
