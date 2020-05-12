import click


@click.argument('repo')
def main(repo):
    print(f'repo: {repo}')


if __name__ == "__main__":
    main()
