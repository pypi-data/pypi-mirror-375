"""
Job search commands for Jobtty.io
"""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm

from ..core.display import console, create_jobs_table, show_job_details, show_error, show_success
from ..core.api_client import JobttyAPI
from ..core.config import JobttyConfig
from ..core.saved_searches import save_current_search

config = JobttyConfig()
api = JobttyAPI()

@click.command()
@click.argument('query', required=False)
@click.option('--remote', is_flag=True, help='Remote jobs only')
@click.option('--location', help='Job location filter')
@click.option('--salary', help='Minimum salary (e.g., 80k, 120000)')
@click.option('--company', help='Filter by company name')
@click.option('--limit', default=20, help='Number of results to show')
@click.option('--source', help='Search specific source (thamesai, flutter_pl, flutter_london)')
@click.option('--save', '-s', is_flag=True, help='💾 Save this search for notifications')
@click.option('--notify', is_flag=True, help='🔔 Enable instant notifications (default: true)')
@click.option('--name', help='Custom name for saved search')
@click.option('--frequency', type=click.Choice(['instant', 'hourly', 'daily', 'weekly']), default='instant', help='Notification frequency')
def search_jobs(query, remote, location, salary, company, limit, source, save, notify, name, frequency):
    """
    🔍 Search for jobs across all platforms
    
    Examples:
    jobtty search "python developer"
    jobtty search "flutter" --remote --salary 80k
    jobtty search --location "London" --company "Google"
    jobtty search "rails developer" --save --notify  # 🚀 REVOLUTIONARY: Save & get terminal notifications!
    jobtty search "flutter" -s --frequency hourly     # Save with hourly notifications
    """
    
    if not query:
        query = Prompt.ask("🔍 Enter search query", default="python developer")
    
    # Show search parameters
    console.print(f"\n[bold bright_cyan]Searching for:[/bold bright_cyan] {query}")
    if remote:
        console.print("🏠 Remote jobs only")
    if location:
        console.print(f"📍 Location: {location}")
    if salary:
        console.print(f"💰 Min salary: {salary}")
    if company:
        console.print(f"🏢 Company: {company}")
    
    console.print()
    
    # Build search parameters
    search_params = {
        "query": query,
        "remote": remote,
        "location": location or config.get('location'),
        "salary_min": parse_salary(salary) if salary else config.get('salary_min'),
        "company": company,
        "limit": limit
    }
    
    # JobTTY uses single source now
    
    # Search JobTTY API (single source)
    all_jobs = []
    
    with console.status("Searching jobs...", spinner="dots"):
        try:
            jobs = api.search_jobs('jobtty', search_params)
            for job in jobs:
                job['source'] = 'jobtty'
            all_jobs = jobs
        except Exception as e:
            console.print(f"[dim red]Search failed: {str(e)}[/dim red]")
    
    if not all_jobs:
        show_error("No jobs found matching your criteria")
        return
    
    # Sort by relevance/date
    all_jobs.sort(key=lambda x: x.get('posted_date', ''), reverse=True)
    all_jobs = all_jobs[:limit]
    
    # Display results
    console.print(f"\n[bold bright_green]Found {len(all_jobs)} jobs:[/bold bright_green]\n")
    
    jobs_table = create_jobs_table(all_jobs)
    console.print(jobs_table)
    
    # Handle saved search
    if save or notify:
        save_search_with_options(query, remote, location, salary, company, source, notify, name, frequency)
    
    # Interactive job selection
    console.print(f"\n💡 Type [bold]jobtty show <job-id>[/bold] to view details")
    console.print(f"💡 Type [bold]jobtty save <job-id>[/bold] to bookmark")

@click.command()
@click.argument('job_id', type=int)
@click.option('--details', is_flag=True, help='Show full job details')
@click.option('--apply', is_flag=True, help='Apply to this job')
def show_job(job_id, details, apply):
    """
    👁️  Show detailed job information
    
    Examples:
    jobtty show 42
    jobtty show 42 --apply
    """
    
    try:
        job = api.get_job_details(job_id)
        
        if not job:
            show_error(f"Job {job_id} not found")
            return
        
        show_job_details(job)
        
        # Only prompt for apply if --apply flag wasn't used and we're in interactive mode
        if apply:
            apply_to_job(job)
        elif not apply:
            # Check if we're in interactive mode before prompting
            try:
                import sys
                if sys.stdin.isatty():
                    response = Prompt.ask("\n🚀 Would you like to apply?", choices=['y', 'n'], default='n')
                    if response == 'y':
                        apply_to_job(job)
                else:
                    # Non-interactive mode, just show the job details
                    console.print("\n💡 Use [bold]jobtty show <job-id> --apply[/bold] to apply to this job")
            except (EOFError, KeyboardInterrupt):
                # Handle input errors gracefully
                console.print("\n💡 Use [bold]jobtty show <job-id> --apply[/bold] to apply to this job")
            
    except Exception as e:
        show_error(f"Failed to fetch job details: {str(e)}")

def apply_to_job(job):
    """Apply to a job through the terminal"""
    console.print(f"\n[bold bright_yellow]📝 Applying to: {job['title']}[/bold bright_yellow]")
    
    if not config.is_authenticated():
        console.print("🔐 You need to login first")
        if Confirm.ask("Login now?"):
            # Redirect to auth
            pass
        return
    
    # Collect application data
    cover_letter = Prompt.ask(
        "Cover letter (optional)", 
        default="I am interested in this position and would like to discuss further."
    )
    
    try:
        result = api.apply_to_job(job['id'], {
            'cover_letter': cover_letter,
            'source': job.get('source')
        })
        
        show_success(f"✅ Application submitted successfully!")
        console.print(f"📧 Confirmation sent to your email")
        console.print(f"🆔 Application ID: {result.get('application_id')}")
        
    except Exception as e:
        show_error(f"Failed to submit application: {str(e)}")

@click.command()
@click.option('--saved', is_flag=True, help='Show saved/bookmarked jobs')
@click.option('--recent', is_flag=True, help='Show recent searches')
@click.option('--applied', is_flag=True, help='Show jobs you applied to')
def list_jobs(saved, recent, applied):
    """
    📋 List saved jobs, recent searches, or applications
    """
    
    if saved:
        show_saved_jobs()
    elif recent:
        show_recent_searches()
    elif applied:
        show_applied_jobs()
    else:
        # Default to recent jobs
        show_recent_searches()

def show_saved_jobs():
    """Show user's saved/bookmarked jobs"""
    saved_jobs = config.get('saved_jobs', [])
    
    if not saved_jobs:
        console.print("📝 No saved jobs yet")
        console.print("💡 Use [bold]jobtty save <job-id>[/bold] to bookmark jobs")
        return
    
    console.print(f"[bold bright_cyan]📚 Your Saved Jobs ({len(saved_jobs)}):[/bold bright_cyan]\n")
    
    for job_id in saved_jobs:
        try:
            job = api.get_job_details(job_id)
            console.print(f"🔖 [{job_id}] {job['title']} at {job['company']}")
        except:
            console.print(f"❌ [{job_id}] Job no longer available")

def show_recent_searches():
    """Show recent search history"""
    search_history = config.get('search_history', [])
    
    if not search_history:
        console.print("🔍 No recent searches")
        return
    
    console.print("[bold bright_cyan]🕐 Recent Searches:[/bold bright_cyan]\n")
    
    for i, search in enumerate(search_history[-10:], 1):
        console.print(f"{i}. {search}")

def show_applied_jobs():
    """Show jobs user has applied to"""
    if not config.is_authenticated():
        show_error("You need to login to see your applications")
        return
    
    try:
        applications = api.get_user_applications()
        
        if not applications:
            console.print("📄 No applications yet")
            return
        
        console.print(f"[bold bright_cyan]📨 Your Applications ({len(applications)}):[/bold bright_cyan]\n")
        
        app_table = Table(show_header=True, header_style="bold magenta")
        app_table.add_column("Job", style="bright_cyan", width=25)
        app_table.add_column("Company", style="bright_yellow", width=20)
        app_table.add_column("Status", style="bright_green", width=12)
        app_table.add_column("Applied", style="dim", width=12)
        
        for app in applications:
            status_style = "green" if app['status'] == 'approved' else "yellow"
            app_table.add_row(
                app['job_title'][:24],
                app['company'][:19],
                f"[{status_style}]{app['status']}[/{status_style}]",
                app['applied_date']
            )
        
        console.print(app_table)
        
    except Exception as e:
        show_error(f"Failed to fetch applications: {str(e)}")

@click.command()
@click.argument('job_id', type=int)
def save_job(job_id):
    """
    🔖 Save/bookmark a job for later
    """
    saved_jobs = config.get('saved_jobs', [])
    
    if job_id in saved_jobs:
        console.print(f"📌 Job {job_id} is already saved")
        return
    
    saved_jobs.append(job_id)
    config.set('saved_jobs', saved_jobs)
    
    show_success(f"🔖 Job {job_id} saved successfully!")
    console.print("💡 Use [bold]jobtty list --saved[/bold] to see all saved jobs")

def save_search_with_options(query, remote, location, salary, company, source, notify, name, frequency):
    """Save current search with notification options"""
    
    # Build search options
    search_options = {
        "query": query,
        "location": location,
        "remote": remote,
        "min_salary": parse_salary(salary) if salary else None,
        "company": company,
        "source": source,
        "notify": True if notify else True,  # Default to true
        "name": name or f"Search for {query}",
        "frequency": frequency,
        "scope": "all"
    }
    
    # Save the search
    search_id = save_current_search(query, search_options)
    
    console.print(f"\n🎉 [bold bright_green]Search saved![/bold bright_green]")
    console.print(f"📝 Search ID: [cyan]{search_id}[/cyan]")
    console.print(f"🔔 Notifications: [yellow]{frequency}[/yellow]")
    console.print(f"\n[bold bright_yellow]🚀 REVOLUTIONARY FEATURE ACTIVATED![/bold bright_yellow]")
    console.print(f"[dim]You'll now get job notifications directly in your terminal while coding![/dim]")
    console.print(f"\n💡 Manage searches: [bold]jobtty searches list[/bold]")

def parse_salary(salary_str: str) -> int:
    """Parse salary string to integer"""
    if not salary_str:
        return 0
    
    # Remove common characters
    clean = salary_str.lower().replace('k', '000').replace(',', '').replace('£', '').replace('$', '')
    
    try:
        return int(clean)
    except ValueError:
        return 0

@click.command()
@click.argument('job_id')
@click.option('--quick', is_flag=True, help='Skip confirmation prompts')
def apply_job(job_id, quick):
    """
    🚀 Quick apply to a job (used from notifications)
    """
    
    try:
        job = api.get_job_details(job_id)
        
        if not job:
            show_error(f"Job {job_id} not found")
            return
        
        console.print(f"\n[bold bright_yellow]🚀 Quick Apply:[/bold bright_yellow] {job['title']} at {job.get('company', 'Unknown')}")
        
        if not quick:
            if not Confirm.ask("Continue with application?"):
                console.print("❌ Application cancelled")
                return
        
        # Use existing apply function
        apply_to_job(job)
        
        # Record action for analytics
        from ..core.saved_searches import SavedSearchManager
        manager = SavedSearchManager()
        manager.record_user_action(job_id, "applied")
        
    except Exception as e:
        show_error(f"Failed to apply: {str(e)}")

@click.command()
@click.argument('job_id')
@click.option('--reason', help='Dismissal reason for analytics')
def dismiss_job(job_id, reason):
    """
    👎 Dismiss a job notification (mark as not interested)
    """
    
    try:
        # Record dismissal action
        from ..core.saved_searches import SavedSearchManager
        manager = SavedSearchManager()
        manager.record_user_action(job_id, f"dismissed:{reason or 'not_interested'}")
        
        show_success(f"📝 Job {job_id} marked as not interested")
        console.print("💡 This helps improve your future notifications")
        
    except Exception as e:
        show_error(f"Failed to dismiss: {str(e)}")

# Commands are registered in cli.py