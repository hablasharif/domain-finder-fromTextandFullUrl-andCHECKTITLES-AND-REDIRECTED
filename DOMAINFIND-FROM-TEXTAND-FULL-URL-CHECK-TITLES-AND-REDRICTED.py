import streamlit as st
import re
from urllib.parse import urlparse
import requests
import random
from bs4 import BeautifulSoup
import io
import base64
import datetime

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
    domain_pattern = r"(https?://)?([a-zA-Z0-9.-]+(\.[a-zA-Z]{2,}))|www\.[a-zA-Z0.9.-]+\.[a-zA-Z]{2,}"
    
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

# Define the filename to save the data
filename = "domainslit.html"

# Initialize the list to store main domains and their titles
saved_domains = []

# Check if the previously saved file exists
try:
    with open(filename, "r", encoding="utf-8") as existing_file:
        # Parse the existing HTML file to retrieve the saved data
        soup = BeautifulSoup(existing_file, 'html.parser')
        extraction_date = soup.find('p', style='background-color: pink; padding: 5px;').text.strip()
        table = soup.find('table')
        rows = table.find_all('tr')[1:]  # Skip the header row
        for row in rows:
            columns = row.find_all('td')
            domain = columns[1].a['href']
            title = columns[2].text
            saved_domains.append((domain, title))
except FileNotFoundError:
    extraction_date = ""

# Streamlit app title
st.title("Domain Extractor, Sorter, and Title Checker App")

# Input text area for user input
input_text = st.text_area("Enter text:")

# Define a function to extract and sort domains and main domains from text using regular expressions
@ st.cache_data 
def extract_and_sort_domains(text):
    # Regular expression pattern to match domains with various TLDs, subdomains, and URL schemes
    domain_pattern = r"(https?://)?([a-zA-Z0-9.-]+(\.[a-zA-Z]{2,}))|www\.[a-zA-Z0.9.-]+\.[a-zA-Z]{2,}"

    # Find all domain matches in the input text
    domains = re.findall(domain_pattern, text)

    # Extract, add "https://" if not present, and sort the unique domains
    sorted_domains = sorted(set(domain[0] + domain[1] if domain[0] else 'https://' + domain[1] for domain in domains))

    # Extract and sort the unique main domains
    main_domains = sorted(set(urlparse(domain).netloc for domain in sorted_domains))

    return sorted_domains, main_domains

# Add a button to extract and display domain information
if st.button("Extract Domains"):
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

# Define a function to fetch the title of a web page with a random User-Agent and handle getaddrinfo failed errors
@ st.cache_data 
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

# Add a button to save the domains and titles to a file
if st.button("Save Domains and Titles"):
    # Get the current date and time in the specified format
    current_datetime = datetime.datetime.now().strftime("%d %B %Y : %I:%M %p %A")

    # Create an HTML file with the saved domains, titles, and extraction date
    with io.BytesIO() as file:
        file.write(b"<html>\n<head><title>Saved Domains and Titles</title></head>\n<body>\n")
        file.write(f'<p style="background-color: pink; padding: 5px;">Extraction Date: {current_datetime}</p>\n'.encode("utf-8"))
        file.write(b'<table style="border-collapse: collapse; width: 100%;">\n')
        file.write(b'<tr style="background-color: powderblue;"><th style="padding: 5px; text-align: left;">Serial</th><th style="padding: 5px; text-align: left;">Domain</th><th style="padding: 5px; text-align: left;">Title</th><th style="padding: 5px; text-align: left;">Extraction Date</th></tr>\n')

        # Iterate through the saved domains and add a serial number
        for idx, (domain, title) in enumerate(saved_domains, start=1):
            # Make the domain column link clickable in a new tab
            file.write(f'<tr style="background-color: {random.choice(["lightgray", "lightpink", "lightblue"])};"><td style="padding: 5px;">{idx}</td><td style="padding: 5px;"><a href="{domain}" target="_blank" rel="noopener noreferrer">{domain}</a></td><td style="padding: 5px;">{title}</td><td style="padding: 5px;">{current_datetime}</td></tr>\n'.encode("utf-8"))

        file.write(b'</table>\n</body>\n</html>')

        # Provide a download link for the saved file
        st.markdown(f'<a href="data:file/html;base64,{base64.b64encode(file.getbuffer()).decode()}" download="{filename}">Click to download</a>', unsafe_allow_html=True)

        # Save the HTML file
        with open(filename, "wb") as saved_file:
            saved_file.write(file.getbuffer())

# Display the download button after the code completes its extraction
if not input_text:
    st.write("Please enter some text to extract domains and titles.")
