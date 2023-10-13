# SaaSProjectHunter
 
SaaSProjectHunter is the solution for easily searching projects/companies/users across multiple services (SaaS). It eliminates the need for manual checks of each service during pentesting/OSINT. SaaSProjectHunter interacts with the endpoints/APIs of various services to perform the search and has a modular structure to create separate modules to request sources separately.
 
## Installation
 
1. Clone the repository:
```
git clone https://github.com/Onsec-io/SaaSProjectHunter.git
```
 
2. Install the required packages:
```
pip install -r requirements.txt
```
 
3. Run the project:
```
python app.py --help
```
 
## Example 
It is recommended to run a check of all modules with the `-c all` option before using the program for its intended purpose, as the services may have changed their work logic since the code was published this, in turn,  may require  some corrections  in the module code.
 
To get a list of available modules, run the program with the `-l` (`--list`) parameter.

The utility has the functionality to generate a list of words based on your input, such as a list of sites: `python app.py -g google.com domains.google`
Output:
```
google-com youtube.com youtube google_com googlecom youtubecom youtube_com youtube-com google.com google
```
 
A list of strings that will be used as parameters when calling the services must be prepared to use the tool. You can enumerate words with a space in the `-s` (`--string`) parameter or specify the path to a file in the `-w` (`--wordlist`) parameter.
 
An example of how to run the program:
```commandline
python app.py -s google logstash octocat
python app.py -w wordlist.txt
```
 
To gain a better understanding of the tool's workings, you can run the tool with the `-v` (`--verbose`) parameter. Running with the `-vv` parameter is only recommended for debugging purposes. A full list of available parameters can be accessed by calling the help using the `-h` (`--help`) option.
 
 
### An example of the program's output:
```
python app.py -s google logstash octocat
---------------  --------------------------------------------------
DockerHubSearch  https://hub.docker.com/search?q=octocat
DockerHubSearch  https://hub.docker.com/search?q=logstash
DockerHubSearch  https://hub.docker.com/search?q=google
DockerHubUsers   https://hub.docker.com/v2/users/logstash
DockerHubUsers   https://hub.docker.com/v2/users/google
GithubPages      https://octocat.github.io/
GithubPages      https://google.github.io/
PostmanSearch    https://www.postman.com/search?q=google
PostmanSearch    https://www.postman.com/search?q=logstash
AmazonS3Sites    http://google.s3-website.ap-south-1.amazonaws.com/
GetOutline       https://google.getoutline.com/
readthedocs      https://google.readthedocs.io/
AmazonS3Bucket   https://s3.amazonaws.com/octocat
AmazonS3Bucket   https://s3.amazonaws.com/logstash
AmazonS3Bucket   https://s3.amazonaws.com/google
Jira             https://logstash.jira.com/
Atlassian        https://google.atlassian.net/
Slack            https://octocat.slack.com/
Slack            https://logstash.slack.com/
Slack            https://google.slack.com/
GithubUsers      https://github.com/octocat
GithubUsers      https://github.com/logstash
GithubUsers      https://github.com/google
---------------  --------------------------------------------------
```
 
## List of modules
- [x] AWS S3 (Bucket, Website)
- [x] Alibaba Cloud Object Storage
- [x] Atlassian
- [x] Bitbucket (Users/Company)
- [x] Deskpro
- [x] DigitalOcean Spaces Object Storage
- [x] DockerHub (Users, Search)
- [x] GetOutline
- [x] GitLab (Users, Groups)
- [x] Github (Users, Search)
- [x] Github Gist (gist.github.com)
- [x] Github Pages (github.io)
- [x] Google Cloud Storage Buckets
- [x] JIRA
- [x] Kayako
- [x] Linode Object Storage
- [x] OVH Cloud Object Storage
- [x] Postman (Users, Search)
- [x] ReadTheDocs
- [x] Salesforce
- [x] Scaleway Object Storage
- [x] SearchCode
- [x] Slack
- [x] SwaggerHub (Users, Query)
- [x] Tilda
- [x] Vultr Object Storage
- [x] Youtrack
- [x] Zendesk
- [x] Zoho (Desk, Wiki)
- [x] Azure (Cloud, Container, BLOB, etc)
 
 
## Contributing
 
We welcome contributions from the community. If you want to contribute, please fork the repository and submit a pull request with your changes.
 
Please, refrain from making any modifications outside of the `modules` folder in the project. You can utilize three asynchronous functions to create tasks for target queries:
- `async_requests(urls)` - a simple function that polls the URLs from the given list and returns a list of responses from the services;
- `async_requests_over_datasets(datasets)` - where `datasets` is a dictionary where the key is the `UUID` of the request and the value is `the request parameters`. An example structure of `datasets` is: `{'UNIQUE-UUID': {'url': 'https://<company>.example.com/<project>', 'method': 'post', 'cookies': "{'key': 'value'}"}}`. This function returns a two-dimensional array consisting of the UUID of the original request and the response to the request;
- `async_nslookup(domains)` - this function performs DNS lookups for a list of domains. It will return a simple list of domains for which an A record was successfully obtained.
 
 
## License
 
This project is released under the Apache License 2.0.
