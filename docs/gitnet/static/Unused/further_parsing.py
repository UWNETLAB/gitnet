# Python sccript for adding images to the html files in a reproducible way.
import os
import subprocess as subprocess
import sys
import glob
import fileinput

find = '<h1>Index</h1>'
replace = '<br>\n<br>\n<br>\n<img src="static/gitnet.png" height="250" width="250"/>'

files = glob.glob('gitnet/*.html')
for file in files:
    with fileinput.FileInput(file, inplace=True) as html_file:
        for line in html_file:
            print(line.replace(find, replace), end='')

files = glob.glob('gitnet/gitnet_tests/*.html')
for file in files:
    with fileinput.FileInput(file, inplace=True) as html_file:
        for line in html_file:
            print(line.replace(find, replace), end='')


##############################################################################################
# Currently unused, looking for a way to integrate the networkslab website and documentation.
# Problem is that adding this html code seems to slow the website down considerably.
# Also there is not an efficient way to update it everytime a new static site is generated with hugo.


doctype = '<!doctype html>'
header = '''<!doctype html>
<html lang="en">

<head>
  <meta charset="utf-8" />
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">

  <meta name="author" content="Dr. John McLevey" />

  <meta name="generator" content="Hugo 0.15" />

  <link rel="alternate" href="http://networkslab.org/gitnet/index.xml" type="application/rss+xml" title="gitnet">
  <link rel="stylesheet" href="//maxcdn.bootstrapcdn.com/font-awesome/4.5.0/css/font-awesome.min.css" />
  <link rel="stylesheet" href="http://networkslab.org/gitnet/css/bootstrap.min.css" />
  <link rel="stylesheet" href="http://networkslab.org/gitnet/css/main.css" />
  <link rel="stylesheet" href="//fonts.googleapis.com/css?family=Lora:400,700,400italic,700italic" />
  <link rel="stylesheet" href="//fonts.googleapis.com/css?family=Open+Sans:300italic,400italic,600italic,700italic,800italic,400,300,600,700,800" />
  <link rel="stylesheet" href="http://networkslab.org/gitnet/css/pygment_highlights.css" />


  <meta property="og:title" content="gitnet" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="//" />
  <meta property="og:image" content="" />
'''

files = glob.glob('gitnet/*.html')
for file in files:
    with fileinput.FileInput(file, inplace=True) as html_file:
        for line in html_file:
            print(line.replace(doctype, header), end='')

body = '<body>'

navbar = '''<body>
<nav class="navbar navbar-default navbar-fixed-top navbar-custom">
  <div class="container-fluid">
    <div class="navbar-header">
      <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#main-navbar">
        <span class="sr-only">Toggle navigation</span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
        <span class="icon-bar"></span>
      </button>
      <a class="navbar-brand" href="http://networkslab.org/gitnet/">gitnet</a>
    </div>

    <div class="collapse navbar-collapse" id="main-navbar">
      <ul class="nav navbar-nav navbar-right">

          <li>
          <a title="Documentation" href="/gitnet/page/documentation/">Documentation</a>
  	      </li>

          <li>
          <a title="Tutorials" href="/gitnet/page/tutorials/">Tutorials</a>
  	      </li>

          <li>
          <a title="News" href="/gitnet/">News</a>
  	      </li>

          <li>
          <a title="About" href="http://www.johnmclevey.com/">About</a>
  	      </li>

      </ul>
    </div>

	<div class="avatar-container">
	  <div class="avatar-img-border">

	  </div>
	</div>

  </div>
</nav>'''

files = glob.glob('gitnet/*.html')
for file in files:
    with fileinput.FileInput(file, inplace=True) as html_file:
        for line in html_file:
            print(line.replace(body, navbar), end='')
