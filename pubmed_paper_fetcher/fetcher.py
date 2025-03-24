"""Core functionality for fetching and processing PubMed papers."""

from typing import Dict, List, Optional, Set, Tuple, Any
import re
import logging
from dataclasses import dataclass
from Bio import Entrez
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set your email for Entrez
Entrez.email = "your.email@example.com"  # Replace with your email

@dataclass
class PaperAuthor:
    """Represents an author of a paper with their affiliation information."""
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    is_corresponding: bool = False
    is_non_academic: bool = False
    company: Optional[str] = None

@dataclass
class Paper:
    """Represents a research paper with its metadata."""
    pubmed_id: str
    title: str
    publication_date: str
    authors: List[PaperAuthor]
    
    @property
    def non_academic_authors(self) -> List[PaperAuthor]:
        """Return authors affiliated with non-academic institutions."""
        return [author for author in self.authors if author.is_non_academic]
    
    @property
    def company_affiliations(self) -> Set[str]:
        """Return unique company affiliations."""
        return {author.company for author in self.non_academic_authors if author.company}
    
    @property
    def corresponding_author_email(self) -> Optional[str]:
        """Return the email of the corresponding author if available."""
        for author in self.authors:
            if author.is_corresponding and author.email:
                return author.email
        return None

class PubMedFetcher:
    """Fetches and processes papers from PubMed."""
    
    # Keywords that indicate academic affiliations
    ACADEMIC_KEYWORDS = {
        'university', 'college', 'institute', 'school', 'academy', 'academia',
        'hospital', 'clinic', 'medical center', 'health center', 'faculty'
    }
    
    # Keywords that indicate pharmaceutical/biotech companies
    COMPANY_KEYWORDS = {
        'pharma', 'biotech', 'therapeutics', 'biosciences', 'laboratories',
        'inc', 'corp', 'llc', 'ltd', 'co', 'company', 'gmbh', 'ag', 'sa'
    }
    
    # Email pattern for extraction
    EMAIL_PATTERN = re.compile(r'[\w\.-]+@[\w\.-]+\.\w+')
    
    def __init__(self, debug: bool = False):
        """Initialize the fetcher with debug mode."""
        self.debug = debug
        if debug:
            logger.setLevel(logging.DEBUG)
    
    def search_papers(self, query: str, max_results: int = 100) -> List[str]:
        """
        Search for papers matching the query.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results to return
            
        Returns:
            List of PubMed IDs
        """
        logger.debug(f"Searching PubMed with query: {query}")
        try:
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            record = Entrez.read(handle)
            handle.close()
            
            if "IdList" not in record or not record["IdList"]:
                logger.warning(f"No results found for query: {query}")
                return []
            
            logger.debug(f"Found {len(record['IdList'])} papers")
            return record["IdList"]
        except Exception as e:
            logger.error(f"Error searching PubMed: {e}")
            raise
    
    def fetch_paper_details(self, pubmed_ids: List[str]) -> List[Paper]:
        """
        Fetch detailed information for the given PubMed IDs.
        
        Args:
            pubmed_ids: List of PubMed IDs to fetch
            
        Returns:
            List of Paper objects
        """
        if not pubmed_ids:
            return []
        
        logger.debug(f"Fetching details for {len(pubmed_ids)} papers")
        try:
            handle = Entrez.efetch(db="pubmed", id=",".join(pubmed_ids), retmode="xml")
            records = Entrez.read(handle)
            handle.close()
            
            papers = []
            for article in records["PubmedArticle"]:
                paper = self._parse_article(article)
                if paper and any(author.is_non_academic for author in paper.authors):
                    papers.append(paper)
            
            logger.debug(f"Processed {len(papers)} papers with non-academic authors")
            return papers
        except Exception as e:
            logger.error(f"Error fetching paper details: {e}")
            raise
    
    def _parse_article(self, article: Dict[str, Any]) -> Optional[Paper]:
        """
        Parse a PubMed article into a Paper object.
        
        Args:
            article: PubMed article data
            
        Returns:
            Paper object or None if parsing fails
        """
        try:
            article_data = article["MedlineCitation"]["Article"]
            pubmed_id = article["MedlineCitation"]["PMID"]
            
            # Extract title
            title = article_data.get("ArticleTitle", "")
            
            # Extract publication date
            pub_date = self._extract_publication_date(article_data)
            
            # Extract authors
            authors = self._extract_authors(article_data)
            
            return Paper(
                pubmed_id=pubmed_id,
                title=title,
                publication_date=pub_date,
                authors=authors
            )
        except KeyError as e:
            logger.warning(f"Missing key in article data: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error parsing article {pubmed_id if 'pubmed_id' in locals() else 'unknown'}: {e}")
            return None
    
    def _extract_publication_date(self, article_data: Dict[str, Any]) -> str:
        """Extract publication date from article data."""
        try:
            if "PubDate" in article_data.get("Journal", {}).get("JournalIssue", {}).get("PubDate", {}):
                pub_date = article_data["Journal"]["JournalIssue"]["PubDate"]
                
                # Handle different date formats
                if "Year" in pub_date:
                    year = pub_date.get("Year", "")
                    month = pub_date.get("Month", "")
                    day = pub_date.get("Day", "")
                    
                    if month and day:
                        return f"{year}-{month}-{day}"
                    elif month:
                        return f"{year}-{month}"
                    else:
                        return year
                elif "MedlineDate" in pub_date:
                    return pub_date["MedlineDate"]
            
            # Fallback to ArticleDate if available
            if "ArticleDate" in article_data and article_data["ArticleDate"]:
                article_date = article_data["ArticleDate"][0]
                year = article_date.get("Year", "")
                month = article_date.get("Month", "")
                day = article_date.get("Day", "")
                return f"{year}-{month}-{day}"
            
            return "Unknown"
        except Exception as e:
            logger.warning(f"Error extracting publication date: {e}")
            return "Unknown"
    
    def _extract_authors(self, article_data: Dict[str, Any]) -> List[PaperAuthor]:
        """Extract authors and their affiliations from article data."""
        authors = []
        
        if "AuthorList" not in article_data:
            return authors
        
        for author_data in article_data["AuthorList"]:
            if "LastName" not in author_data and "CollectiveName" not in author_data:
                continue
            
            # Extract author name
            if "CollectiveName" in author_data:
                name = author_data["CollectiveName"]
            else:
                last_name = author_data.get("LastName", "")
                fore_name = author_data.get("ForeName", "")
                name = f"{last_name}, {fore_name}" if fore_name else last_name
            
            # Extract affiliation
            affiliation = self._extract_affiliation(author_data)
            
            # Extract email
            email = self._extract_email(author_data, affiliation)
            
            # Check if corresponding author
            is_corresponding = False
            if "EqualContrib" in author_data and author_data["EqualContrib"] == "Y":
                is_corresponding = True
            
            # Check if non-academic and extract company name
            is_non_academic, company = self._check_non_academic(affiliation)
            
            authors.append(PaperAuthor(
                name=name,
                affiliation=affiliation,
                email=email,
                is_corresponding=is_corresponding,
                is_non_academic=is_non_academic,
                company=company
            ))
        
        return authors
    
    def _extract_affiliation(self, author_data: Dict[str, Any]) -> Optional[str]:
        """Extract affiliation from author data."""
        if "AffiliationInfo" in author_data:
            affiliations = []
            for affiliation_info in author_data["AffiliationInfo"]:
                if "Affiliation" in affiliation_info:
                    affiliations.append(affiliation_info["Affiliation"])
            return "; ".join(affiliations) if affiliations else None
        return None
    
    def _extract_email(self, author_data: Dict[str, Any], affiliation: Optional[str]) -> Optional[str]:
        """Extract email from author data or affiliation text."""
        # Try to find email in author data
        if "Identifier" in author_data:
            for identifier in author_data["Identifier"]:
                if identifier.attributes.get("Source") == "Email":
                    return identifier
        
        # Try to extract email from affiliation text
        if affiliation:
            email_match = self.EMAIL_PATTERN.search(affiliation)
            if email_match:
                return email_match.group(0)
        
        return None
    
    def _check_non_academic(self, affiliation: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Check if an affiliation is non-academic and extract company name.
        
        Args:
            affiliation: Affiliation text
            
        Returns:
            Tuple of (is_non_academic, company_name)
        """
        if not affiliation:
            return False, None
        
        affiliation_lower = affiliation.lower()
        
        # Check for academic keywords
        for keyword in self.ACADEMIC_KEYWORDS:
            if keyword in affiliation_lower:
                return False, None
        
        # Check for company keywords
        for keyword in self.COMPANY_KEYWORDS:
            if keyword in affiliation_lower:
                # Try to extract company name
                # This is a simple heuristic - in a real implementation, 
                # you might want to use NER or more sophisticated techniques
                words = affiliation.split(',')
                for word in words:
                    word = word.strip()
                    if any(kw in word.lower() for kw in self.COMPANY_KEYWORDS):
                        return True, word
                
                # If we can't extract a specific company name, return the full affiliation
                return True, affiliation
        
        return False, None
    
    def papers_to_dataframe(self, papers: List[Paper]) -> pd.DataFrame:
        """
        Convert papers to a pandas DataFrame.
        
        Args:
            papers: List of Paper objects
            
        Returns:
            DataFrame with paper information
        """
        data = []
        for paper in papers:
            non_academic_authors = ", ".join([author.name for author in paper.non_academic_authors])
            company_affiliations = ", ".join(paper.company_affiliations)
            
            data.append({
                "PubmedID": paper.pubmed_id,
                "Title": paper.title,
                "Publication Date": paper.publication_date,
                "Non-academic Author(s)": non_academic_authors,
                "Company Affiliation(s)": company_affiliations,
                "Corresponding Author Email": paper.corresponding_author_email or ""
            })
        
        return pd.DataFrame(data)
    
    def fetch_and_process(self, query: str, max_results: int = 100) -> pd.DataFrame:
        """
        Fetch and process papers based on the query.
        
        Args:
            query: PubMed search query
            max_results: Maximum number of results to return
            
        Returns:
            DataFrame with processed paper information
        """
        logger.info(f"Fetching papers for query: {query}")
        
        # Search for papers
        pubmed_ids = self.search_papers(query, max_results)
        
        if not pubmed_ids:
            logger.info("No papers found")
            return pd.DataFrame(columns=[
                "PubmedID", "Title", "Publication Date", 
                "Non-academic Author(s)", "Company Affiliation(s)", 
                "Corresponding Author Email"
            ])
        
        # Fetch paper details
        papers = self.fetch_paper_details(pubmed_ids)
        
        # Convert to DataFrame
        df = self.papers_to_dataframe(papers)
        
        logger.info(f"Found {len(df)} papers with non-academic authors")
        return df