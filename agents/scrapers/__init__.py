"""
ForceIA Scrapers — coleta de vagas públicas para Hiring Signal.

Usa httpx (padrão). Scrapy é opcional (`pip install scrapy`) para jobs mais pesados.
"""

from scrapers.job_boards import fetch_job_page, scrape_board, scrape_job_url

__all__ = ["fetch_job_page", "scrape_job_url", "scrape_board"]
