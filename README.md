# NASA Earth Observatory Image of the Day RSS Feed

[![Valid RSS](assets/valid-rss-rogers.png)](https://validator.w3.org/feed/check.cgi?url=https%3A%2F%2Fgscermak.github.io%2Fnasa-earth-rss%2Ffeed.xml)

## Background and Motivation

The official NASA Earth Observatory Image of the Day RSS feed appeared to stop working in late September 2026. As a regular reader of Earth Observatory content through the start.me platform, I decided to develop an alternative RSS feed to restore access to this valuable Earth science resource. A subsequent check in November 2026 confirmed that the official feed remained nonfunctional within start.me. Other RSS readers were not tested.

## Project Overview

This independent, open-source project provides an alternative RSS feed for NASA Earth Observatory's Image of the Day. The feed includes the latest image and the five preceding images, along with their titles, descriptions, thumbnails, and links to the original NASA articles.

Developed using Python with the assistance of generative AI, the application uses GitHub Actions to automatically update the feed daily and GitHub Pages to make it publicly accessible.

The project demonstrates how human-AI collaboration, open-source software, and automated workflows can address a practical scientific information accessibility problem.

## Accessing the RSS Feed

The RSS feed is publicly available at:

https://gscermak.github.io/nasa-earth-rss/feed.xml

Copy this URL into an RSS reader, such as start.me, to receive the latest NASA Earth Observatory Image of the Day updates.

## Features

- Includes the latest Image of the Day and five preceding images.
- Provides image titles, descriptions, thumbnails, and article links.
- Automatically updates once a day.
- Uses the RSS 2.0 standard.
- Supports Media RSS thumbnails.
- Includes an Atom self-reference for improved interoperability.
- Performs internal RSS structural validation.
- Preserves the existing feed if generation or validation fails.
- Requires no dedicated server or paid hosting service under the current public repository configuration.
- Provides direct links to the original NASA content.
- Successfully validated using the W3C Feed Validation Service.
- Operationally verified using start.me.

## Application Architecture

The application consists of four primary components:

| Component | Purpose |
| --- | --- |
| Python | Retrieves and processes NASA Earth Observatory content. |
| RSS XML | Provides a standardized format for content syndication. |
| GitHub Actions | Automates daily RSS feed generation. |
| GitHub Pages | Hosts the publicly accessible RSS feed. |

The application uses the following Python packages:

| Package | Purpose |
| --- | --- |
| requests | Retrieves HTML content from NASA's website. |
| beautifulsoup4 | Parses HTML and extracts article metadata. |
| Python standard library | Processes dates, URLs, XML, file operations, and software testing. |

## Automated Workflow

1. GitHub Actions initiates the scheduled daily workflow.
2. The Python script retrieves NASA Earth Observatory content.
3. Candidate article URLs are identified.
4. Image metadata and article information are extracted.
5. Articles are sorted by publication date.
6. The six most recent valid candidate articles are selected.
7. The RSS feed is generated in a temporary XML file.
8. The temporary RSS file undergoes structural validation.
9. The existing feed.xml file is replaced following successful validation.
10. The updated file is committed to the GitHub repository.
11. GitHub Pages hosts the publicly accessible RSS feed.

The automated workflow is scheduled to run daily at 12:00 UTC (4 AM PST or 5 AM PDT). It can also be initiated manually through GitHub Actions.

## Repository Structure

```text
nasa-earth-rss/
├── .github/
│   └── workflows/
│       └── update-feed.yml
├── assets/
│   └── valid-rss-rogers.png
├── .gitignore
├── LICENSE
├── README.md
├── feed.xml
├── generate_feed.py
└── requirements.txt
```

| File | Description |
| --- | --- |
| generate_feed.py | Python application for generating and validating the RSS feed. |
| feed.xml | Generated RSS 2.0 feed. |
| requirements.txt | Required third-party Python packages. |
| update-feed.yml | GitHub Actions automation workflow. |
| valid-rss-rogers.png | Official W3C RSS validation badge. |
| .gitignore | Identifies files excluded from version control. |
| LICENSE | MIT software license. |
| README.md | Project documentation. |

## System Requirements

- Python 3.9 or later (intended compatibility; not tested across all versions).
- Git.
- Internet access.
- Python pip package manager.

The automated GitHub Actions workflow uses Python 3.12.

## Local Installation

Clone the GitHub repository:

```bash
git clone https://github.com/gscermak/nasa-earth-rss.git
cd nasa-earth-rss
```

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the required Python packages:

```bash
python -m pip install -r requirements.txt
```

## Local Execution

Generate the RSS feed:

```bash
python generate_feed.py
```

The application displays a summary of the generation process, including:

- Number of candidate article links.
- Number of valid candidate articles.
- Number of RSS items generated.
- Internal validation status.
- Article titles and publication dates.
- Article and image URLs.

The generated RSS feed is saved as:

```text
feed.xml
```

To examine the generated XML:

```bash
cat feed.xml
```

## Configuration

Application configuration parameters are defined near the beginning of generate_feed.py.

| Parameter | Purpose |
| --- | --- |
| SOURCE_URL | NASA Earth Observatory Image of the Day source page. |
| ARTICLE_PREFIX | Permitted NASA Earth Observatory article URL prefix. |
| FEED_URL | Canonical public URL of the generated RSS feed. |
| OUTPUT_FILE | Name and location of the generated RSS file. |
| MAX_ARTICLES | Maximum number of articles included in the feed. |
| REQUEST_TIMEOUT | HTTP request timeout in seconds. |
| MEDIA_NS | Media RSS XML namespace. |
| ATOM_NS | Atom XML namespace. |

Users hosting their own version of the RSS feed should modify FEED_URL to match their published feed address.

## Automated Deployment

The GitHub Actions workflow is defined in:

```text
.github/workflows/update-feed.yml
```

To deploy an independent instance of the application:

1. Fork the repository or create a new repository containing the application.
2. Update FEED_URL in generate_feed.py.
3. Enable GitHub Actions.
4. Ensure the workflow has permission to commit repository changes.
5. Enable GitHub Pages using the main branch and root directory.
6. Manually execute the workflow to verify successful operation.
7. Verify that GitHub Pages publishes the updated feed.
8. Validate the published RSS feed using the W3C Feed Validation Service.

The workflow includes concurrency protection and a 15-minute execution timeout.

## Quality Assurance and Validation

The application performs internal validation before replacing the existing RSS feed.

Validation checks include:

- XML parsing.
- RSS 2.0 version declaration.
- Required RSS channel elements.
- Required article metadata.
- Expected number of RSS items.
- Unique article identifiers.
- Media RSS thumbnail elements.
- Atom self-reference URL and content type.

### Functional Testing

The original and revised versions of the application were executed and their results compared on November 24, 2026.

Both versions identified 21 candidate articles and generated the same six RSS entries, including identical article titles, publication dates, article URLs, and image URLs.

The revised application successfully performed internal RSS structural validation and preserved the correct encoding of special characters in image URLs.

### Failure Recovery Testing

Two controlled failure recovery tests were conducted on November 24, 2026, to evaluate the reliability of the application.

Fault injection was used to deliberately introduce errors and evaluate the application's ability to detect failures, terminate gracefully, and preserve the existing RSS feed.

Neither test required modifications to the Python source code or installation of additional Python packages.

#### Test 1: Insufficient Article Availability

The MAX_ARTICLES configuration parameter was temporarily overridden to request 999 articles when only 21 valid candidate articles were available.

```bash
python3 - <<'PY'
import generate_feed

generate_feed.MAX_ARTICLES = 999

raise SystemExit(generate_feed.main())
PY
```

The application correctly detected the insufficient number of articles, reported an error, and terminated with an exit status of 1.

A SHA-256 checksum comparison confirmed that the existing RSS feed remained byte-for-byte identical.

| Test | Expected | Actual | Result |
| --- | --- | --- | --- |
| Requested articles | 999 | 999 | PASS |
| Available articles | Fewer than 999 | 21 | PASS |
| Insufficient article detection | Error reported | Error reported | PASS |
| Application exit status | 1 | 1 | PASS |
| Existing RSS feed | Unchanged | Unchanged | PASS |
| Checked temporary file | Absent | Absent | PASS |

#### Test 2: Simulated RSS Validation Failure

Python's built-in unittest.mock library was used to temporarily override the RSS validation function and simulate a validation failure.

```bash
python3 - <<'PY'
from unittest.mock import patch
import generate_feed

with patch.object(
    generate_feed,
    "validate_rss",
    side_effect=ValueError("Simulated RSS validation failure")
):
    raise SystemExit(generate_feed.main())
PY
```

The application successfully retrieved article metadata but encountered the simulated validation failure. It correctly reported the error and terminated with an exit status of 1.

A SHA-256 checksum comparison confirmed that the existing RSS feed remained byte-for-byte identical.

| Test | Expected | Actual | Result |
| --- | --- | --- | --- |
| Requested articles | 6 | 6 | PASS |
| Article retrieval | Successful | 21 valid articles | PASS |
| Simulated validation failure | Error reported | Error reported | PASS |
| Application exit status | 1 | 1 | PASS |
| Existing RSS feed | Unchanged | Unchanged | PASS |
| Matching temporary files remaining | None | None | PASS |

#### Feed Integrity Verification

The Linux sha256sum utility was used to verify that the existing RSS feed remained unchanged during both failure recovery tests.

Before each test, a checksum was calculated:

```bash
sha256sum feed.xml > /tmp/nasa-feed-checksum.txt
```

Immediately after each simulated application failure, the application exit status was examined:

```bash
echo $?
```

Both tests returned an exit status of 1, indicating unsuccessful application execution.

The checksum was then verified:

```bash
sha256sum -c /tmp/nasa-feed-checksum.txt
```

Both tests returned:

```text
feed.xml: OK
```

Following the validation failure test, the Linux find utility was used to check for matching temporary RSS files:

```bash
find . -maxdepth 1 -type f -name 'feed*.tmp'
```

No matching temporary files were found.

#### Failure Recovery Test Summary

Both failure recovery tests demonstrated that the application detects the tested failures, reports errors, terminates with a nonzero exit status, and preserves the existing RSS feed.

These safeguards are particularly important for an unattended application operating through an automated daily workflow.

The simulated validation failure tested the application's recovery mechanism rather than the correctness of individual XML validation rules. Temporary file checks were limited to the filenames and patterns examined during testing.

Reference:

https://docs.python.org/3/library/unittest.mock.html

### GitHub Actions Operational Testing

The revised application was deployed to GitHub on November 24, 2026.

The GitHub Actions workflow was manually executed to verify application functionality in the GitHub cloud environment.

The workflow completed successfully in 26 seconds.

| Workflow Step | Execution Time | Result |
| --- | ---: | --- |
| Set up job | 1 second | PASS |
| Checkout repository | 1 second | PASS |
| Set up Python | Less than 1 second | PASS |
| Install dependencies | 2 seconds | PASS |
| Generate RSS feed | 16 seconds | PASS |
| Commit updated feed | 2 seconds | PASS |
| Post-execution cleanup | 1 second | PASS |
| Overall workflow | 26 seconds | PASS |

The workflow successfully generated and committed an updated RSS feed.

One nonfatal workflow warning was reported. Its review remains a maintenance task.

### Independent RSS Validation

The locally generated RSS feed was independently validated on November 24, 2026, using the W3C Feed Validation Service and confirmed to be a valid RSS 2.0 feed.

The W3C recommendation to include an Atom self-reference was subsequently implemented.

Following deployment, the publicly accessible RSS feed was validated directly using its GitHub Pages URL.

The W3C Feed Validation Service returned:

> Congratulations! This is a valid RSS feed.

No errors or recommendations were displayed during the published feed validation.

[![Valid RSS](assets/valid-rss-rogers.png)](https://validator.w3.org/feed/check.cgi?url=https%3A%2F%2Fgscermak.github.io%2Fnasa-earth-rss%2Ffeed.xml)

Click the badge to independently validate the published RSS feed.

W3C Feed Validation Service:

https://validator.w3.org/feed/

### RSS Reader Acceptance Testing

The published RSS feed was tested using the start.me platform on November 24, 2026.

The feed operated successfully, confirming that the application addressed the original information accessibility problem that motivated its development.

### Quality Assurance Summary

| Test | Result |
| --- | --- |
| Original and revised application output comparison | PASS |
| Article metadata extraction | PASS |
| Special character URL encoding | PASS |
| Internal RSS structural validation | PASS |
| Local W3C RSS 2.0 validation | PASS |
| Atom self-reference generation | PASS |
| Insufficient article failure recovery | PASS |
| Simulated validation failure recovery | PASS |
| Existing feed integrity verification | PASS |
| Git whitespace validation | PASS |
| Git repository synchronization | PASS |
| GitHub deployment | PASS |
| Revised GitHub Actions execution | PASS |
| Automated RSS repository update | PASS |
| GitHub Pages public accessibility | PASS |
| Published W3C RSS validation | PASS |
| Published Atom self-reference validation | PASS |
| Published feed compatibility with start.me | PASS |

All primary functional and operational acceptance tests were successfully completed on November 24, 2026.

## Error Handling and Reliability

The application includes several safeguards:

- HTTP request timeouts.
- HTTP status error checking.
- Article metadata validation.
- Duplicate article detection.
- Special character encoding in image URLs.
- Publication date normalization.
- RSS structural validation.
- Temporary file generation.
- Replacement of the existing feed only after successful validation.
- Nonzero exit status when generation fails.

These safeguards reduce the likelihood of publishing an incomplete or invalid RSS feed.

The nonzero exit status also allows GitHub Actions to detect application failures and prevent subsequent commit and push operations under the configured workflow.

## Known Limitations

The application depends on the structure and metadata of NASA's Earth Observatory website. Changes to the website may require modifications to the Python script.

Article selection is based on discovered article links and publication metadata rather than an official Image of the Day application programming interface.

The application requires internet connectivity to retrieve NASA content.

The availability and accessibility of NASA-hosted imagery remain dependent on NASA's infrastructure.

Compatibility with every available RSS reader has not been independently tested.

Python package versions are not currently pinned to specific releases.

Failure recovery testing covered insufficient article availability and a simulated RSS validation failure. Other potential failure scenarios, including network interruptions, filesystem errors, and concurrent external modifications, have not been independently tested.

Although public feed accessibility and automated repository updates were verified, synchronization between the latest automated commit and the published GitHub Pages feed was not independently compared byte-for-byte.

## Scientific and Educational Value

NASA Earth Observatory provides valuable scientific information about Earth's atmosphere, oceans, land surfaces, ecosystems, climate, and natural hazards.

By providing an automated RSS feed, this project supports:

- Earth science education.
- Scientific information accessibility.
- Environmental awareness.
- Informal science communication.
- Lifelong learning.
- Public engagement with Earth observation science.

The application demonstrates how a relatively small amount of software can improve access to existing scientific information.

## Human-AI Collaboration

This application was developed collaboratively by Greg Cermak and OpenAI ChatGPT.

Generative AI assisted with:

- Application design.
- Python code development.
- HTML metadata extraction.
- RSS XML generation.
- Debugging and troubleshooting.
- URL encoding.
- GitHub Actions configuration.
- Code review and refinement.
- Software documentation.
- Interpretation of W3C validation results.
- Development of fault injection tests.
- Evaluation of failure recovery test results.
- Software reliability assessment.
- Git repository management.
- Operational acceptance testing.

The human developer established the project objectives, directed the development process, executed the software, evaluated results, and verified application functionality.

The project illustrates an applied approach to human-AI collaboration in scientific software engineering, emphasizing simplicity, transparency, maintainability, and validation.

The development process also demonstrates that generative AI can assist not only with software implementation but also with quality assurance, defensive programming, software testing, deployment, and technical documentation.

## Data Source and Attribution

All scientific articles, article summaries, and imagery referenced by the RSS feed originate from NASA Earth Observatory.

NASA Earth Observatory:

https://science.nasa.gov/earth/earth-observatory/

NASA Earth Observatory Image of the Day:

https://science.nasa.gov/earth/earth-observatory/image-of-the-day/

Original scientific content and imagery are attributed to NASA and the respective credited contributors.

Users should consult the original NASA articles for complete scientific descriptions, image credits, and applicable usage restrictions.

This project is independent and is not affiliated with, sponsored by, or endorsed by NASA.

## License

The original software and documentation are distributed under the MIT License.

See the [LICENSE](LICENSE) file for details.

The MIT License does not extend to NASA imagery, article summaries, third-party content referenced or distributed through the generated RSS feed, or the W3C validation badge. Such content remains subject to its applicable rights and usage conditions.

## Author

Greg Cermak

Developed collaboratively with OpenAI ChatGPT.

## Acknowledgments

- NASA Earth Observatory for providing publicly accessible Earth science information and imagery.
- GitHub for providing repository hosting, automated workflows, and web publication services.
- The World Wide Web Consortium (W3C) for providing the Feed Validation Service and RSS validation badge.
- The Python development community for providing software development and testing libraries.
- OpenAI ChatGPT for assistance with application development, testing, troubleshooting, deployment, and documentation.