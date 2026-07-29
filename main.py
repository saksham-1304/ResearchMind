# main.py
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain, reviser_chain

console = Console()

def run_research_pipeline(topic: str) -> dict:
    state = {}
    
    console.print(Panel.fit(f"[bold cyan]ResearchMind Pipeline Activated[/bold cyan]\nTopic: [yellow]{topic}[/yellow]", border_style="cyan"))

    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
        
        # Step 1: Search
        task1 = progress.add_task("[cyan]Step 1: Search Agent gathering data...", total=None)
        search_agent = build_search_agent()
        search_result = search_agent.invoke({"input": f"Find recent, reliable and detailed information about: {topic}"})
        state["search_results"] = search_result['output']
        progress.update(task1, completed=100, description="[green]Step 1: Search Complete! ✓")
        
        # Step 2: Read/Scrape
        task2 = progress.add_task("[cyan]Step 2: Reader Agent scraping top resources...", total=None)
        reader_agent = build_reader_agent()
        reader_result = reader_agent.invoke({
            "input": f"Based on the following search results about '{topic}', pick the best URL and scrape it for deeper content.\n\nSearch Results:\n{state['search_results'][:1000]}"
        })
        state['scraped_content'] = reader_result['output']
        progress.update(task2, completed=100, description="[green]Step 2: Scraping Complete! ✓")
        
        # Step 3: Write Draft
        task3 = progress.add_task("[cyan]Step 3: Writer drafting initial report...", total=None)
        research_combined = f"SEARCH RESULTS:\n{state['search_results']}\n\nDETAILED SCRAPED CONTENT:\n{state['scraped_content']}"
        state["draft"] = writer_chain.invoke({"topic": topic, "research": research_combined})
        progress.update(task3, completed=100, description="[green]Step 3: Draft Complete! ✓")
        
        # Step 4: Critique
        task4 = progress.add_task("[cyan]Step 4: Critic evaluating draft...", total=None)
        state["feedback"] = critic_chain.invoke({"report": state['draft']})
        progress.update(task4, completed=100, description="[green]Step 4: Critique Generated! ✓")
        
        # Step 5: Revise
        task5 = progress.add_task("[cyan]Step 5: Reviser polishing final report...", total=None)
        state["final_report"] = reviser_chain.invoke({
            "topic": topic, 
            "report": state['draft'], 
            "feedback": state["feedback"]
        })
        progress.update(task5, completed=100, description="[green]Step 5: Final Report Ready! ✓")

    # Display Outputs
    console.print("\n[bold magenta]Critic's Feedback:[/bold magenta]")
    console.print(Panel(state['feedback'], border_style="magenta"))
    
    console.print("\n[bold green]Final Polished Report:[/bold green]")
    console.print(Panel(state['final_report'], border_style="green"))

    return state

if __name__ == "__main__":
    console.clear()
    topic_input = console.input("[bold yellow]Enter a research topic: [/bold yellow]")
    run_research_pipeline(topic_input)