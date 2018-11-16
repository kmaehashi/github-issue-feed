FROM python:3
RUN pip3 install pygithub feedgen
COPY github_issue_feed.py /
