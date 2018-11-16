#!/usr/bin/env python

import argparse
import os
import pytz

from github import Github
from feedgen.feed import FeedGenerator


class IssueFeedGenerator(object):
    def __init__(self, conf):
        self._conf = conf

    def _get_repo(self):
        conf = self._conf
        gh = Github(conf.token, base_url=conf.github)
        return gh.get_repo('{}/{}'.format(conf.user, conf.repo))

    def _get_issues(self, repo):
        conf = self._conf
        return repo.get_issues(
            state=conf.state,
            labels=[repo.get_label(l) for l in conf.labels],
            sort=conf.sort,
        )

    def _get_feed(self):
        conf = self._conf

        repo = self._get_repo()

        fg = FeedGenerator()
        fg.id(repo.html_url)
        fg.title(conf.title)
        fg.link(href=repo.html_url)

        for issue in self._get_issues(repo):
            updated = issue.created_at if conf.sort == 'created' else issue.updated_at

            fe = fg.add_entry()
            fe.id(issue.html_url)
            fe.title(issue.title)
            fe.content(issue.body)
            fe.link(href=issue.html_url)
            fe.updated(updated.replace(tzinfo=pytz.UTC))

        return fg

    def to_atom(self):
        fg = self._get_feed()
        return fg.atom_str(pretty=True)



def parse_args():
    parser = argparse.ArgumentParser()

    # Feed configuration
    parser.add_argument('--title', type=str, default=None)

    # GitHub configuration
    parser.add_argument('--github', type=str, default='https://api.github.com')
    parser.add_argument('--user', type=str, required=True)
    parser.add_argument('--repo', type=str, required=True)
    parser.add_argument('--token', type=str, default=os.environ.get('GITHUB_ACCESS_TOKEN', None))

    # https://developer.github.com/v3/issues/#list-issues-for-a-repository
    parser.add_argument('--labels', type=str, default=None)
    parser.add_argument('--state', choices=['open', 'closed', 'all'], default='all')
    parser.add_argument('--sort', choices=['created', 'updated', 'comments'], default='created')
    # TODO support more

    conf = parser.parse_args()

    if conf.title is None:
        conf.title = 'GitHub Issues ({}/{})'.format(conf.user, conf.repo)

    if conf.labels is None:
        conf.labels = []
    else:
        conf.labels = conf.labels.split(',')

    return conf


def main():
    conf = parse_args()
    print(IssueFeedGenerator(conf).to_atom().decode())

if __name__ == '__main__':
    main()
