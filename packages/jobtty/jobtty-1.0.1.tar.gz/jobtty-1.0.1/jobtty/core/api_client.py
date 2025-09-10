"""
API client for integrating with job board services
"""

import requests
import time
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

from .config import JobttyConfig
from .display import console, show_error

class JobttyAPI:
    """Unified API client for all job board integrations"""
    
    def __init__(self):
        self.config = JobttyConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Jobtty.io/1.0.0 Terminal Job Board'
        })
        
        # API endpoints
        self.endpoints = self.config.get_api_endpoints()
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1.0  # seconds
    
    def _rate_limit(self, source: str):
        """Apply rate limiting per source"""
        if source in self.last_request_time:
            elapsed = time.time() - self.last_request_time[source]
            if elapsed < self.min_request_interval:
                time.sleep(self.min_request_interval - elapsed)
        
        self.last_request_time[source] = time.time()
    
    def _make_request(self, source: str, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make authenticated API request with error handling"""
        self._rate_limit(source)
        
        base_url = self.endpoints.get(source)
        if not base_url:
            raise ValueError(f"Unknown source: {source}")
        
        # Ensure proper URL construction
        if not base_url.endswith('/'):
            base_url += '/'
        url = urljoin(base_url, endpoint)
        
        # Add authentication if available
        headers = {}
        auth_token = self.config.get_auth_token(source)
        if auth_token:
            headers['Authorization'] = f'Bearer {auth_token}'
        
        try:
            response = self.session.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            console.print(f"[dim red]API Error ({source}): {str(e)}[/dim red]")
            return None
    
    def search_jobs(self, source: str, search_params: Dict) -> List[Dict]:
        """Search jobs from JobTTY API (single source of truth)"""
        
        if source != "jobtty":
            # For backward compatibility, redirect all sources to jobtty
            source = "jobtty"
        
        endpoint = 'jobs'
        jobs_data = self._make_request(source, endpoint, search_params)
        if jobs_data:
            return self._normalize_jobtty_jobs(jobs_data.get('jobs', []))
        
        return []
    
    
    def _normalize_jobtty_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """Normalize Jobtty.io job data to standard format"""
        normalized = []
        
        for job in jobs:
            # Handle company field - could be string or dict
            company = job.get('company')
            if isinstance(company, dict):
                company_name = company.get('name', 'Unknown Company')
            else:
                company_name = str(company) if company else 'Unknown Company'
            
            # Handle salary field  
            salary = job.get('salary') or job.get('salary_range', '')
            
            # Handle posted date
            posted_date = ''
            if job.get('posted_at'):
                posted_date = job.get('posted_at').split('T')[0]
            elif job.get('created_at'):
                posted_date = job.get('created_at').split('T')[0]
            
            normalized.append({
                'id': job.get('id'),
                'title': job.get('title', 'Untitled Job'),
                'company': company_name,
                'location': job.get('location', 'N/A'),
                'salary': salary,
                'type': 'Full-time',  # Default for now
                'remote': job.get('remote', False) or ('remote' in job.get('location', '').lower()),
                'posted_date': posted_date,
                'description': job.get('description', ''),
                'requirements': job.get('requirements', ''),
                'url': job.get('url', ''),
                # Premium fields
                'premium': job.get('premium', False),
                'featured': job.get('featured', False),
                'company_logo_ascii': job.get('company_logo_ascii', ''),
                'source_site': job.get('source_site', 'jobtty')
            })
        
        return normalized
    
    
    def get_job_details(self, job_id: int) -> Optional[Dict]:
        """Get detailed information for a specific job from JobTTY API"""
        
        job_data = self._make_request('jobtty', f'jobs/{job_id}')
        if job_data:
            return self._normalize_jobtty_jobs([job_data])[0]
        
        return None
    
    def apply_to_job(self, job_id: int, application_data: Dict) -> Dict:
        """Submit job application"""
        
        if not self.config.is_authenticated():
            raise Exception("Authentication required")
        
        auth_token = self.config.get_auth_token('jobtty')
        if not auth_token:
            raise Exception("No authentication token available")
        
        try:
            response = requests.post(
                'https://jobtty.io/api/v1/applications',
                json={
                    'job_id': job_id,
                    'message': application_data.get('cover_letter', ''),
                    'cv_file_url': application_data.get('cv_file_url')
                },
                headers={'Authorization': f'Bearer {auth_token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Application failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def get_user_applications(self) -> List[Dict]:
        """Get user's job applications"""
        if not self.config.is_authenticated():
            return []
        
        try:
            auth_token = self.config.get_auth_token('jobtty')
            response = requests.get('https://jobtty.io/api/v1/applications', 
                headers={'Authorization': f'Bearer {auth_token}'}, timeout=10)
            
            if response.status_code == 200:
                return response.json().get('applications', [])
            else:
                return []
        except requests.exceptions.RequestException:
            return []