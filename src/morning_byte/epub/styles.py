"""CSS styles for the EPUB digest."""

# Beautiful, Kindle-optimized CSS
EPUB_CSS = """
/* Base typography */
body {
    font-family: Georgia, "Times New Roman", serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    color: #1a1a1a;
}

/* Headings */
h1 {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 2em;
    font-weight: 700;
    margin: 1em 0 0.5em 0;
    color: #111;
    border-bottom: 3px solid #e74c3c;
    padding-bottom: 0.3em;
}

h2 {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 1.5em;
    font-weight: 600;
    margin: 1.5em 0 0.5em 0;
    color: #222;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.2em;
}

h3 {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 1.2em;
    font-weight: 600;
    margin: 1em 0 0.3em 0;
    color: #333;
}

/* Paragraphs */
p {
    margin: 0.8em 0;
    text-align: justify;
}

/* Links */
a {
    color: #2980b9;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

/* Article cards */
.article {
    margin: 1.5em 0;
    padding: 1em;
    border-left: 4px solid #3498db;
    background: #f8f9fa;
    page-break-inside: avoid;
}

.article-title {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 1.1em;
    font-weight: 600;
    margin: 0 0 0.5em 0;
    line-height: 1.3;
}

.article-title a {
    color: #1a1a1a;
}

.article-meta {
    font-size: 0.85em;
    color: #666;
    margin: 0.5em 0;
}

.article-meta .source {
    font-weight: 600;
    color: #e74c3c;
}

.article-meta .score {
    color: #27ae60;
    font-weight: 600;
}

.article-meta .comments {
    color: #3498db;
}

.article-summary {
    font-size: 0.95em;
    color: #444;
    margin: 0.5em 0 0 0;
    font-style: italic;
}

.article-domain {
    font-size: 0.8em;
    color: #888;
}

/* Full article content */
.article-content {
    margin: 1em 0 0 0;
    font-size: 0.95em;
    color: #333;
    line-height: 1.7;
    border-top: 1px solid #ddd;
    padding-top: 1em;
}

.article-content p {
    margin: 0.8em 0;
}

.article-content h1,
.article-content h2,
.article-content h3,
.article-content h4 {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    margin: 1.2em 0 0.5em 0;
    color: #333;
    border: none;
}

.article-content h1 { font-size: 1.3em; }
.article-content h2 { font-size: 1.2em; }
.article-content h3 { font-size: 1.1em; }
.article-content h4 { font-size: 1em; }

.article-content ul,
.article-content ol {
    margin: 0.8em 0;
    padding-left: 1.5em;
}

.article-content li {
    margin: 0.4em 0;
}

.article-content blockquote {
    margin: 1em 0;
    padding: 0.5em 1em;
    border-left: 3px solid #ccc;
    background: #f5f5f5;
    font-style: italic;
    color: #555;
}

.article-content pre,
.article-content code {
    font-family: "Courier New", Courier, monospace;
    font-size: 0.9em;
    background: #f5f5f5;
    border-radius: 3px;
}

.article-content pre {
    padding: 1em;
    overflow-x: auto;
    margin: 1em 0;
}

.article-content code {
    padding: 0.2em 0.4em;
}

.article-content table {
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
}

.article-content th,
.article-content td {
    padding: 0.5em;
    border: 1px solid #ddd;
    text-align: left;
}

.article-content th {
    background: #f5f5f5;
    font-weight: 600;
}

/* Article separator */
.article-separator {
    border: none;
    border-top: 2px dashed #ddd;
    margin: 2em 0;
}

/* Section styling */
.section {
    margin: 2em 0;
}

.section-description {
    font-style: italic;
    color: #666;
    margin-bottom: 1em;
}

/* Cover page */
.cover {
    text-align: center;
    padding: 3em 1em;
    page-break-after: always;
}

.cover h1 {
    font-size: 2.5em;
    border: none;
    margin-bottom: 0.2em;
}

.cover .subtitle {
    font-size: 1.3em;
    color: #666;
    margin-bottom: 1em;
}

.cover .date {
    font-size: 1.5em;
    color: #333;
    margin: 1em 0;
}

.cover .stats {
    font-size: 1em;
    color: #888;
    margin-top: 2em;
}

/* Table of contents */
.toc {
    page-break-after: always;
}

.toc h2 {
    border: none;
    text-align: center;
}

.toc ul {
    list-style: none;
    padding: 0;
}

.toc li {
    margin: 0.8em 0;
    padding-left: 1em;
    border-left: 2px solid #ddd;
}

.toc a {
    color: #333;
}

.toc .count {
    color: #888;
    font-size: 0.9em;
}

/* Tags */
.tags {
    margin-top: 0.5em;
}

.tag {
    display: inline-block;
    font-size: 0.75em;
    background: #ecf0f1;
    color: #555;
    padding: 0.2em 0.5em;
    border-radius: 3px;
    margin-right: 0.3em;
}

/* Footer */
.footer {
    margin-top: 3em;
    padding-top: 1em;
    border-top: 1px solid #ddd;
    text-align: center;
    font-size: 0.85em;
    color: #888;
}

/* Responsive adjustments for e-readers */
@media screen and (max-width: 600px) {
    body {
        font-size: 1em;
    }

    .article {
        padding: 0.8em;
    }
}
"""
