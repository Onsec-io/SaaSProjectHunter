# SaaSProjectHunter

SaaSProjectHunter is a comprehensive solution for searching projects, companies, and users across multiple SaaS services. It streamlines the process of pentesting and OSINT by eliminating the need for manual checks across each service. SaaSProjectHunter interacts with service endpoints and APIs to perform searches and is designed with a modular structure, allowing for the creation of separate modules to handle different data sources.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Onsec-io/SaaSProjectHunter.git
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Run the project:

```bash
python3 app.py --help

SaaSProjectHunter (developed by ONSEC.io)

usage: app.py [-h] [-g [GENERATOR ...]] [-m MODULE] [-t THREADS] [-u USER_AGENT] [-v] [-nc] [-p POSTFIX] [--limit LIMIT] [--proxies PROXIES] [--tag TAG] [-l | -c] [-w WORDLIST | -s STRINGS [STRINGS ...]]

Example usage: python3 app.py -s google logstash octocat -v

options:
  -h, --help            show this help message and exit
  -g [GENERATOR ...], --generator [GENERATOR ...]
                        Apply a generator to the wordlist.
  -m MODULE, --module MODULE
                        Specify the module name to run or check.
  -t THREADS, --threads THREADS
                        Set the number of concurrent threads. Defaults to twice the number of CPU cores.
  -u USER_AGENT, --user-agent USER_AGENT
                        Set the User-Agent string for HTTP requests.
  -v, --verbose         Increase output verbosity (e.g., -v for verbose, -vv for more verbose).
  -nc, --no-color       Disable colored output.
  -p POSTFIX, --postfix POSTFIX
                        Specify the file path for postfixes.
  --limit LIMIT         Set the maximum number of requests per module.
  --proxies PROXIES     Specify the file path for HTTP/SOCKS proxies.
  --tag TAG             Specify the tag for run only specific modules.
  -l, --list            Display a list of available modules and exit.
  -c, --check           Execute module checks and exit.
  -w WORDLIST, --wordlist WORDLIST
                        Specify the file path to the wordlist.
  -s STRINGS [STRINGS ...], --strings STRINGS [STRINGS ...]
                        Provide a list of strings separated by spaces.
```

## Example

It is recommended to run a check of all modules with the `-c` (`--check`) option before using the program for its intended purpose, as the services may have changed their work logic since the code was published this, in turn,  may require  some corrections  in the module code.

To get a list of available modules, run the program with the `-l` (`--list`) parameter.

The utility can generate a list of words based on your input, such as a list of sites: `python app.py -g google.com domains.google`
Output:

```bash
google-com youtube.com youtube google_com googlecom youtubecom youtube_com youtube-com google.com google
```

A list of strings that will be used as parameters when calling the services must be prepared to use the tool. You can enumerate words with a space in the `-s` (`--string`) parameter or specify the path to a file in the `-w` (`--wordlist`) parameter.

An example of how to run the program:

```bash
python app.py -s google logstash octocat
python app.py -w wordlist.txt
python app.py -s google.com -g
```

To gain a better understanding of the tool's workings, you can run the tool with the `-v` (`--verbose`) parameter. Running with the `-vv` parameter is only recommended for debugging purposes. A full list of available parameters can be accessed by calling the help using the `-h` (`--help`) option.

### An example of the program's output

```bash
python app.py -s google logstash octocat
---------------  --------------------------------------------------
AlibabaCloudS3   http://logstash.oss-cn-hangzhou.aliyuncs.com/
AlibabaCloudS3   http://google.oss-cn-hangzhou.aliyuncs.com/
AmazonS3Bucket   https://s3.amazonaws.com/octocat (Access Denied)
AmazonS3Bucket   https://s3.amazonaws.com/logstash (Access Denied)
AmazonS3Bucket   https://s3.amazonaws.com/google (Access Denied)
Atlassian        https://octocat.atlassian.net/
Atlassian        https://google.atlassian.net/
Azure            https://google.azurecr.io
Azure            https://google.database.windows.net
Azure            https://logstash.vault.azure.net
Azure            https://google.vault.azure.net
Azure            https://logstash.eastasia.cloudapp.azure.com
Azure            https://google.eastasia.cloudapp.azure.com
Azure            https://logstash.eastus.cloudapp.azure.com
Azure            https://google.eastus.cloudapp.azure.com
Azure            https://logstash.eastus2.cloudapp.azure.com
Azure            https://google.japaneast.cloudapp.azure.com
Azure            https://google.koreasouth.cloudapp.azure.com
Azure            https://google.southcentralus.cloudapp.azure.com
Azure            https://google.westcentralus.cloudapp.azure.com
Azure            https://logstash.westeurope.cloudapp.azure.com
Azure            https://google.westeurope.cloudapp.azure.com
Azure            https://logstash.westus2.azurecontainer.io
AzureStorage     https://logstash.blob.core.windows.net/<BRUTEFORCE>?restype=container&comp=list
AzureStorage     https://google.blob.core.windows.net/<BRUTEFORCE>?restype=container&comp=list
Bitbucket        https://bitbucket.org/octocat/
CodebergSearch   https://codeberg.org/explore/repos?only_show_relevant=false&q=octocat
CodebergSearch   https://codeberg.org/explore/organizations?q=google
CodebergSearch   https://codeberg.org/explore/repos?only_show_relevant=false&q=logstash
CodebergSearch   https://codeberg.org/explore/repos?only_show_relevant=false&q=google
CodebergSearch   https://codeberg.org/explore/users?q=google
CodebergSearch   https://codeberg.org/explore/organizations?q=octocat
DigitalOceanS3   https://google.sfo3.digitaloceanspaces.com
DockerHubSearch  https://hub.docker.com/search?q=octocat
DockerHubSearch  https://hub.docker.com/search?q=logstash
DockerHubSearch  https://hub.docker.com/search?q=google
DockerHubUsers   https://hub.docker.com/u/logstash
DockerHubUsers   https://hub.docker.com/u/google
GetOutline       https://google.getoutline.com/
GitLab           https://gitlab.com/google
GitLab           https://gitlab.com/logstash
GithubGist       https://gist.github.com/search?q=%22google%22
GithubGist       https://gist.github.com/search?q=%22octocat%22
GithubGist       https://gist.github.com/search?q=%22logstash%22
GithubPages      https://octocat.github.io/
GithubPages      https://google.github.io/
GithubSearch     https://github.com/search?q=%22octocat%22
GithubSearch     https://github.com/search?q=%22google%22
GithubSearch     https://github.com/search?q=%22logstash%22
GithubUsers      https://github.com/octocat
GithubUsers      https://github.com/logstash
GithubUsers      https://github.com/google
GoogleS3         https://logstash.storage.googleapis.com
Jira             https://logstash.jira.com/
LinodeS3         https://google.us-east-1.linodeobjects.com
NPMjs            https://www.npmjs.com/package/octocat
NPMjs            https://www.npmjs.com/package/logstash
NPMjs            https://www.npmjs.com/package/google
NPMsSearch       https://api.npms.io/v2/search?q=scope:google
NPMsSearch       https://api.npms.io/v2/search?q=author:google
NPMsSearch       https://api.npms.io/v2/search?q=octocat
NPMsSearch       https://api.npms.io/v2/search?q=logstash
NPMsSearch       https://api.npms.io/v2/search?q=google
OVHCloudS3       https://google.s3.de.io.cloud.ovh.net
PostmanSearch    https://www.postman.com/search?q=octocat
PostmanSearch    https://www.postman.com/search?q=logstash
PostmanSearch    https://www.postman.com/search?q=google
ReadTheDocs      https://google.readthedocs.io/
ScalewayS3       https://google.s3.nl-ams.scw.cloud
SearchCode       https://searchcode.com/?q=octocat
SearchCode       https://searchcode.com/?q=logstash
SearchCode       https://searchcode.com/?q=google
Slack            https://octocat.slack.com/
Slack            https://logstash.slack.com/
Slack            https://google.slack.com/
SwaggerHub       https://app.swaggerhub.com/search?query=octocat
SwaggerHub       https://app.swaggerhub.com/search?query=logstash
SwaggerHub       https://app.swaggerhub.com/search?query=google
Tilda            https://google.tilda.ws/
VultrS3          https://google.sgp1.vultrobjects.com
YouTrack         https://google.youtrack.cloud/
Zoho             https://google.wiki.zoho.com/
Zoho             https://google.zohodesk.com/
---------------  --------------------------------------------------
```

## List of modules

- [x] 3CX
- [x] Alibaba Cloud Object Storage
- [x] Atlassian
- [x] AWS S3 (Bucket, Website)
- [x] Azure (Cloud, Container, BLOB, Tenants, etc)
- [x] Bitbucket (Users/Company)
- [x] Codeberg
- [x] crt.sh (Domains, Search)
- [x] Deskpro
- [x] DigitalOcean Spaces Object Storage
- [x] DockerHub (Users, Search)
- [x] GetOutline
- [x] GhostIO (blogs on ghost.io)
- [x] Github (Users, Search)
- [x] Github Gist (gist.github.com)
- [x] Github Pages (github.io)
- [x] GitLab (Users, Groups)
- [x] Google Cloud Storage Buckets
- [x] GrayhatWarfare (buckets.grayhatwarfare.com)
- [x] JIRA
- [x] Kayako
- [x] Linode Object Storage
- [x] NPMjs (Packages, Users, Search)
- [x] OpenBuckets.io (buckets and files)
- [x] OVH Cloud Object Storage
- [x] Postman (Users, Search)
- [x] ReadTheDocs
- [x] Recruitee
- [x] RunKit (Packages, Notebooks, Users)
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

## Contributing

We welcome contributions from the community. If you want to contribute, please fork the repository and submit a pull request with your changes.

Please, refrain from making any modifications outside of the `modules` folder in the project. You can utilize three asynchronous functions to create tasks for target queries:

- `async_requests(urls)` - a simple function that polls the URLs from the given list and returns a list of responses from the services;
- `async_requests_over_datasets(datasets)` - where `datasets` is a dictionary where the key is the `UUID` of the request and the value is `the request parameters`. An example structure of `datasets` is: `{'UNIQUE-UUID': {'url': 'https://<company>.example.com/<project>', 'method': 'post', 'cookies': "{'key': 'value'}"}}`. This function returns a two-dimensional array consisting of the UUID of the original request and the response to the request;
- `async_nslookup(domains)` - this function performs DNS lookups for a list of domains. It will return a simple list of domains for which an A record was successfully obtained;
- `async_websocket(url, messages=[])` - this function establishes a websocket session, sends messages and return responses.

## License

This project is released under the Apache License 2.0.
