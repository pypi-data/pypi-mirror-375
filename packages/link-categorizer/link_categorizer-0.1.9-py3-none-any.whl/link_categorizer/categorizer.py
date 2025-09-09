import re
from urllib.parse import urlparse

TEXT_MAX_LENGTH = 50

# Domain matchers: (category, regex pattern)
DOMAIN_MATCHERS = [
    ("blog", r"blog\..*"),
    ("blog", r"medium\.com$"),
    ("community", r"community\..*"),
    ("community", r"forum\..*"),
    ("developers", r"developers?\..*"),
    ("documentation", r"docs\..*"),
    ("e-commerce", r"amazon\.com$"),
    ("e-commerce", r"ebay\.com$"),
    ("jobs", r"teamtailor\.com$"),
    ("jobs", r"^(jobs\.|careers?\.).*"),
    ("jobs", r"job-boards\.greenhouse\.io"),
    ("newsletter", r"substack\.(com|net|app)$"),
    ("press", r"press\..*"),
    ("press", r"newsroom\..*"),
    ("reviews", r"trustpilot\.com"),
    ("podcast", r"podcasts?\..*"),
    ("social media", r"youtube\.com$"),
    ("social media", r"youtu.be$"),
    ("social media", r"discord(app)?\.com$|discord\.gg$"),
    ("social media", r"t\.me$|telegram\.(me|org)$"),
    ("social media", r"slack\.(com|net|app)$"),
    ("social media", r"reddit\.(com|net|app)$"),
    ("social media", r"pinterest\.(com|net|app)$"),
    ("social media", r"twitch\.(com|tv)$"),
    ("social media", r"(facebook|fb)\.com$"),
    ("social media", r"linkedin\.com"),
    ("social media", r"tiktok\.com$"),
    ("social media", r"twitter\.com$|www\.x\.com$|^x\.com$"),
    ("social media", r"instagram\.com$"),
    ("social media", r"snapchat\.com$"),
    ("support", r"support\..*"),
    ("code repository", r"github\.com$"),
    ("code repository", r"gitlab\.com$"),
    ("code repository", r"gitlab\..*"),
    ("code repository", r"bitbucket\.org$"),
    ("code repository", r"sourceforge\.net$"),
    ("code repository", r"codeberg\.org$"),
]

# Path matchers
PATH_MATCHERS = [
    ("about", r"about(-us|-company)?/?$"),
    ("accessibility", r"accessibility/?$"),
    ("advertise", r"(advertise|media)/?$"),
    ("affiliate", r"affiliates?/?$"),
    ("blog", r"(blog)/?$"),
    ("community", r"(community|forum|discussion|groups)/?$"),
    ("contact", r"contact(-us)?/?$"),
    ("cookie policy", r"cookie-?policy/?$"),
    ("developers", r"developers?/?$"),
    ("faq", r"(faqs?|frequently-asked-questions|help)/?$"),
    ("how it works", r"(how-it-works)/?$"),
    ("investor relations", r"(investor-relations|investors)/?$"),
    ("jobs", r"(jobs|careers?|work-with-us|opportunities|join-us|open-roles)/?$"),
    ("login", r"(login|sign-in)/?$"),
    ("news", r"(news|updates|announcements|newsroom)/?$"),
    ("newsletter", r"(newsletter|subscribe|email-signup)/?$"),
    ("press", r"(press|press-room|press-kit)/?$"),
    ("pricing", r"(pricing|plans|buy-now|pricing-and-plans)/?$"),
    ("privacy", r"(privacy-policy|privacy-notice|privacy)/?$"),
    ("podcast", r"(podcasts?)/?$"),
    ("privacy", r"(privacy-policy|privacy)/?$"),
    ("reviews", r"(testimonials|reviews|what-people-say)/?$"),
    ("services", r"(services|what-we-do|our-services)/?$"),
    ("signup", r"(signup|sign-up)/?$"),
    ("support", r"(support)/?$"),
    ("team", r"(team|our-team|meet-the-team)/?$"),
    ("terms", r"(terms-of-service|terms-and-conditions|terms-of-use|tos)/?$"),
    ("work", r"(work|projects|portfolio)/?$"),
]

# Text matchers
TEXT_MATCHERS = [
    ("about", r"about(\s+)?(us|our\s+company)?"),
    ("advertise", r"media\s+kit"),
    ("contact", r"^contact$|^contact us$"),
    ("developers", r"developers?$"),
    ("faq", r"faq|frequently\s+asked\s+questions"),
    ("home", r"^home$"),
    ("how it works", r"how\s+it\s+works"),
    ("investor relations", r"investor\s+relations"),
    ("login", r"^(log\s*in|sign\s*in)$"),
    ("jobs", r"^(jobs|careers|work\s*with\s*us|opportunities|join\s*us|open\s*roles)"),
    ("privacy", r"privacy\s+policy"),
    ("press", r"press\s+room"),
    ("press", r"press\s+release"),
    ("press", r"press\s+kit"),
    ("press", r"news\s+room"),
    ("register", r"^(register|sign\s*up)$"),
    ("security", r"security\s+policy"),
    ("security", r"responsible\s+disclosure"),
    ("security", r"bug\s+bounty"),
    ("security", r"bug\s+bounties"),
    ("security", r"security\s+reporting"),
    ("security", r"security\s+disclosure"),
    ("terms", r"terms\s+(of\s+service|and\s+conditions)"),
]

# Patterns to ignore completely
IGNORE_REGEXES = [
    r"javascript:",  # JavaScript pseudo-links
    r"void\(0\)",  # JavaScript void links
    r"#$",  # Empty anchors
    r"^#[^/]",  # Page fragment links
    r"/cdn-cgi/",  # Cloudflare internal paths
    r"/wp-content/cache/",  # WordPress cache
    r"/wp-admin/",  # WordPress admin
    r"google\.com/url\?",  # Google redirect links
    r"facebook\.com/sharer",  # Social sharing links
    r"twitter\.com/intent/tweet",  # Twitter share links
]


def deduplicate_links(links: list[dict[str, str]]) -> list[dict[str, str]]:
    """Remove duplicate links based on their URLs.

    Args:
        links: List of dictionaries containing link information

    Returns:
        List of dictionaries with duplicate URLs removed

    """
    seen_urls = set()
    unique_links = []

    for link in links:
        url = link.get("href", "")
        if url not in seen_urls:
            unique_links.append(link)
            seen_urls.add(url)

    return unique_links


# Repository platform patterns configuration
REPO_PLATFORM_PATTERNS: dict[str, dict[str, str | list[str] | None]] = {
    "github": {
        "domain_pattern": r"github\.com$",
        "repo_sections": r"/[^/]+/[^/]+/(issues|pulls?|commits?|releases?|wiki|settings|actions|security|graphs?|pulse|network|insights|deployments?)(/|$)",
        "repo_path": r"^/[^/]+/[^/]+/?$",
        "profile_paths": [r"^/orgs/[^/]+/?$", r"^/[^/]+/?$"],
    },
    "gitlab": {
        "domain_pattern": r"gitlab\.(com|.*)",
        "repo_sections": r"/[^/]+/[^/]+/-(issues|merge_requests|commits?|releases?|wikis?|settings|pipelines|deployments?)(/|$)",
        "repo_path": r"^/[^/]+/[^/]+/?$",
        "profile_paths": [r"^/[^/]+/?$"],
    },
    "bitbucket": {
        "domain_pattern": r"bitbucket\.org$",
        "repo_sections": r"/[^/]+/[^/]+/(issues|pulls?|commits?|downloads|wiki|settings|pipelines?)(/|$)",
        "repo_path": r"^/[^/]+/[^/]+/?$",
        "profile_paths": [r"^/[^/]+/?$"],
    },
    "sourceforge": {
        "domain_pattern": r"sourceforge\.net$",
        "repo_sections": None,  # SourceForge doesn't have standard repo subsections
        "repo_path": r"/projects/[^/]+/?$",
        "profile_paths": [r"/u/[^/]+/?$"],
    },
    "codeberg": {
        "domain_pattern": r"codeberg\.org$",
        "repo_sections": r"/[^/]+/[^/]+/(issues|pulls?|commits?|releases?|wiki|settings|actions?)(/|$)",
        "repo_path": r"^/[^/]+/[^/]+/?$",
        "profile_paths": [r"^/[^/]+/?$"],
    },
}


def match_repo_platform(path: str, patterns: dict[str, str | list[str] | None]) -> str | None:
    """Match a path against repository platform patterns.

    Args:
        path: The URL path to match
        patterns: Dictionary containing the platform's URL patterns

    Returns:
        Category string or None if no match
    """
    # Check repository subsections first (most specific)
    repo_sections = patterns["repo_sections"]
    if repo_sections and isinstance(repo_sections, str):
        if re.search(repo_sections, path, re.IGNORECASE):
            return "code repository"

    # Check if it's a repository path
    repo_path = patterns["repo_path"]
    if repo_path and isinstance(repo_path, str):
        if re.search(repo_path, path, re.IGNORECASE):
            return "code repository"

    # Check if it's a profile path
    profile_paths = patterns["profile_paths"]
    if profile_paths and isinstance(profile_paths, list):
        for profile_pattern in profile_paths:
            if re.search(profile_pattern, path, re.IGNORECASE):
                return "developer profile"

    return None


def categorize_code_repository_link(domain: str, path: str) -> str | None:
    """Categorize links from code repository platforms.

    Args:
        domain: The domain of the URL
        path: The path of the URL

    Returns:
        Category string or None if not applicable
    """
    # Check each platform configuration
    for _platform_name, patterns in REPO_PLATFORM_PATTERNS.items():
        domain_pattern = patterns["domain_pattern"]
        if isinstance(domain_pattern, str) and re.search(domain_pattern, domain, re.IGNORECASE):
            return match_repo_platform(path, patterns)

    return None


def categorize_links(links: list[dict[str, str]]) -> list[dict[str, str]]:
    """Categorize a list of links based on a set of patterns.

    Args:
        links: List of dictionaries containing 'url', 'text', and 'title'
               - url: The full URL of the link
               - text: The anchor text
               - title: The title attribute or page title

    Returns:
        List of dictionaries containing 'url', 'text', 'title', and 'category'
        - url: The full URL of the link
        - text: The anchor text
        - title: The title attribute or page title
        - category: The category of the link

    """
    links = deduplicate_links(links)
    categorized_links = []

    for link_info in links:
        category = categorize_link(link_info)
        if category:
            link_info["category"] = category
            categorized_links.append(link_info)

    return categorized_links


def categorize_link(link_info: dict[str, str]) -> str | None:  # noqa: C901, PLR0911, PLR0912
    """Categorize a link based on a set of patterns.

    Args:
        link_info: Dictionary containing 'url', 'text', and 'title'
                  - url: The full URL of the link
                  - text: The anchor text
                  - title: The title attribute or page title

    Returns:
        String containing the category or None if the link should be ignored

    """
    url = link_info.get("href", "")
    anchor_text = link_info.get("text", "").replace("\n", " ").strip()
    title = link_info.get("title", "").replace("\n", " ").strip()

    # Check ignore patterns first
    for pattern in IGNORE_REGEXES:
        if re.search(pattern, url, re.IGNORECASE):
            return "ignored"

    # Parse URL to extract domain and path
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path

    if parsed_url.scheme == "mailto":
        return "email"

    if parsed_url.scheme in ["tel", "fax"]:
        return "telephone"

    if parsed_url.scheme in ["sms"]:
        return "sms"

    if parsed_url.scheme in ["data"]:
        return "data"

    # Check domain matchers
    for category, pattern in DOMAIN_MATCHERS:
        if re.search(pattern, domain, re.IGNORECASE):
            # If it's a code repository domain, use specialized categorization
            if category == "code repository":
                repo_category = categorize_code_repository_link(domain, path)
                if repo_category:
                    return repo_category
            return category

    # Check path matchers
    for category, pattern in PATH_MATCHERS:
        if re.search(pattern, path, re.IGNORECASE):
            return category

    # Check title matchers
    if title and len(title) < TEXT_MAX_LENGTH:
        for category, pattern in TEXT_MATCHERS:
            if re.search(pattern, title, re.IGNORECASE):
                return category

    # Check anchor text matchers
    if anchor_text and len(anchor_text) < TEXT_MAX_LENGTH:
        for category, pattern in TEXT_MATCHERS:
            if re.search(pattern, anchor_text, re.IGNORECASE):
                return category

    # Check if it's just a home page (domain with no path or only /)
    if path in ["", "/"]:
        return "home"

    # If nothing matched
    return "unknown"
