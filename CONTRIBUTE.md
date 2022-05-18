# Contributing to this repository

Feedback and improvements are welcome on this repository.  If you have points you would like to discuss, please use [this repository's GitHub Issues](https://github.com/ajnelson-nist/gddrescue_mapfile_to_dfxml/issues).


## Branching

This repository follows "Git-Flow" as illustrated [here](https://nvie.com/posts/a-successful-git-branching-model/), with some laxness around "Feature branch" names.  In general, this means:

* Code and documentation in `main` will always be the latest release.
   - Non-release commits might be made against `main` for the purposes of programming Github interface elements (e.g. Issue and Pull Request templates).  Such commits will not trigger releases.
* Feature branches should be forked off of `develop`.
* Hotfix branches should be forked off of `main`.
* Releases will branch off of `develop`, and merge into `main` and `develop`.

For the most part, contributions should branch off of `develop` and have Pull Requests filed against `develop`.


## Reviewing

Contributions are automatically reviewed for code format and style matters, on Github and (if desired) locally, with [`pre-commit`](https://pre-commit.com/).  The `pre-commit` modules [used in this repository](.pre-commit-config.yaml) were selected to reduce `git diff` effects to only semantically-relevant changes.

If you do not have `pre-commit` installed in your Python environment, this repository builds a virtual environment whose sole purpose is housing and installing `pre-commit` hooks for the locally cloned repository instance.  `pre-commit` review can be run in a macOS or Linux environment by cloning this repository, `cd`'ing into it, and then running:

```bash
make
pre-commit run --all-files
```


## Testing

Before committing changes, developers are encouraged to use the `check` target of `make` to confirm effects.  That is, after editing, a developer should run from the repository's root:

```bash
make check
git status
```

`git status` should show files that changed, including automatically-generated results that are tracked in a "semi-static" fashion for the purposes of housing documentation and pre-run demonstration results in the repository.


### Building documentation

Some files in this repository are built with resources not necessary for most development tasks.  *Most contributors will likely not need to follow directions in this section.*

To re-build figures and documentation pages, [`pandoc`](https://pandoc.org/) and [`dot`](https://graphviz.org/) must be installed.

For example, a workflow to rebuild documentation on a fresh Ubuntu machine would be (after cloning this repository and `cd`'ing into its top directory ):

```bash
sudo apt install python3-venv graphviz make pandoc
make clean
make check
git status
```

`git status` is likely to show differences in generated SVG files.  *Please only commit these differences if they are semantically relevant*, e.g. changing figure connections or labels.  `git checkout -- .` will discard all uncommitted changes.
