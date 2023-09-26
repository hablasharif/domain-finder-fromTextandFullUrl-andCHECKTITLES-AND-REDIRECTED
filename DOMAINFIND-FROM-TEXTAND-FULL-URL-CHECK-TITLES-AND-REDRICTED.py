import streamlit as st
import re
from urllib.parse import urlparse
import requests
import random
from bs4 import BeautifulSoup

# Define a list of User-Agent strings
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko'
]

# Define a function to randomly select a User-Agent
def get_random_user_agent():
    return random.choice(user_agents)

# Define a function to extract and sort domains and main domains from text using regular expressions
def extract_and_sort_domains(text):
    # Regular expression pattern to match domains with various TLDs, subdomains, and URL schemes
    domain_pattern = r"(https?://)?([a-zA-Z0-9.-]+(\.[a-zA-Z]{2,}))|www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    
    # Find all domain matches in the input text
    domains = re.findall(domain_pattern, text)
    
    # Extract, add "https://" if not present, and sort the unique domains
    sorted_domains = sorted(set(domain[0] + domain[1] if domain[0] else 'https://' + domain[1] for domain in domains))
    
    # Extract and sort the unique main domains
    main_domains = sorted(set(urlparse(domain).netloc for domain in sorted_domains))
    
    return sorted_domains, main_domains

# Define a function to fetch the title of a web page with a random User-Agent and handle getaddrinfo failed errors
def get_page_title(url):
    try:
        headers = {'User-Agent': get_random_user_agent()}  # Randomly select a User-Agent
        response = requests.get(url, headers=headers, allow_redirects=True, verify=False)  # Add verify=False to ignore SSL certificate verification
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title_tag = soup.title
        if title_tag:
            return title_tag.string.strip(), response.url
        else:
            return "Title not available", response.url
    except requests.exceptions.RequestException as e:
        # Handle getaddrinfo failed error
        if "getaddrinfo failed" in str(e):
            return "Failed to establish a connection to the domain", url
        return "Title not available", str(e)

# Streamlit app title
st.title("Domain Extractor, Sorter, and Title Checker App")

# Input text area for user input
input_text = st.text_area("Enter text:")

if input_text:
    # Extract and sort domains and main domains from the input text
    sorted_domains, main_domains = extract_and_sort_domains(input_text)
    
    # Filter out invalid domains
    sorted_domains = [domain for domain in sorted_domains if not domain.startswith('https://39267-jawan.html')]
    
    # Display the total number of domains
    st.write(f"Total Valid Domains Found: {len(sorted_domains)}")
    
    # Display domain titles
    st.header("Domain Titles:")
    for domain in sorted_domains:
        # Use alt.text to create clickable links
        st.markdown(f"[{domain}]({domain})", unsafe_allow_html=True)
        
        # Fetch and display the title of the web page
        title, redirect_url = get_page_title(domain)
        st.write(f"Title: {title}")
    
    # Display redirected domains
    st.header("Redirected Domains:")
    for domain in sorted_domains:
        # Check if the URL had any redirects
        title, redirect_url = get_page_title(domain)
        if domain != redirect_url:
            st.markdown(f"[{redirect_url}]({redirect_url})", unsafe_allow_html=True)
