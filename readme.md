# bespoke-ijp

This repository is used for documents / code / notes related to the controller and software of the IEB bespoke inkjet printing rig. 
## Folder Structure
| Folder       |  Description  | 
| -------------| -------------|
| `/application`      | Code for the application/GUI |
| `/embedded`      | Code for the uSteppers |
| `/docs`      | Documentation |



## Tasks
- Open tasks are listed  in the [Github Issue Tracker](https://github.com/oxfordcontrol/OxVentControl/issues) and the [Projects board](https://github.com/oxfordcontrol/OxVentControl/projects)
- Please assign yourself to the tasks if you are working on them and keep them updated
- Please close the issue if it is resolved. Also reference the commit that fixed the issue.


## Workflow - Basics 
#### How do I get a copy of this repo?
- Install **Git**: https://help.github.com/en/github/getting-started-with-github/set-up-git
- Open up a terminal / command prompt and clone this repository: `git clone git@github.com:oxfordcontrol/OxVentControl.git` which will give you a local copy of the master branch in the repository

#### Do I have to use a terminal?
- You can also use Git GUIs, e.g. https://desktop.github.com/ or https://www.gitkraken.com/

#### How do I keep my local copy updated?
- If you are on the master branch you can type `git pull`

#### How can I add / submit my changes?
- **The master master branch is protected, so you will have to create a separate branch and open a pull request.**
- The `master` branch should always reflect the newest agreed on version of the repository
- Make sure you branch off the latest state of master, i.e. on master type `git pull` or use `git fetch`
- To create a new branch use: `git checkout -b [branchname]`, e.g. `git checkout -b mg/new_branch`
- Make changes to files / add new files
- Take a look at the summary of changed files: `git status` 
- Add the new files to be tracked: `git add .` (to add all new files) or `git add code.m` (to add specific file)
- Commit the new changes (this creates a snapshot of repository state): `git commit -m "Change parameter gamma to 0.5"`
- Copy your new local branch with the new commits to the Github repository: `git push -u origin mg/new_branch`

- **Before your changes can be merged:** Make sure that you integrate the changes on `master` that others might have added in the meantime. This can be achieved by pulling the `master` changes to yout machine and then *merging* or preferably *rebasing* your commits onto the latest `master` version. See [here](https://gist.github.com/blackfalcon/8428401#keeping-current-with-the-master-branch) for a more detailed explanation.
- On https://github.com/oxfordcontrol/OxVentControl/ click on `Pull requests` -> `New Pull Request`. 
- Select `base:master` and `compare:mg/new_branch`
- All the changes can then be discussed in that pull request before they are approved and added to the master branch.
#### Useful git commands:
- https://rogerdudler.github.io/git-guide/
- https://confluence.atlassian.com/bitbucketserver/basic-git-commands-776639767.html
- http://ohshitgit.com/

## Workflow - Making Git collaboration easier 
A few steps everyone should take to make collaboration with Git easier:

#### Commit early and often
One commit should reflect one meaningful change to the code. Especially if we work on lots of different things at the same time, it is helpful if we create one meaningful commit for each significant change to the code. Notice that you don't have to commit all current changes at the same time. If you changed something in `A.cpp` and something different in `B.cpp`, you can do:
```bash
git add A.cpp
git commit -m "Fixed printing in A."
git add B.cpp
git commit -m "Changed parameters in B."
```
#### Combine temporary commits / clean up your history
If your recent 4 commits look like this `Fixed ABC`, `Work in progress`, `Working version` `Ups small fix` and you want to open a pull request to add this to the code you should first combine these commits into one commit. This can be done with an interactive  `git rebase`. To select the last 4 commits to squash, type:
```bash
git rebase -i HEAD~4
```
This should open an editor and show something like this:
```bash
pick d94e78 Fixed ABC     --- older commit
pick 4e9baa Work in progress
pick afb581 Working version  
pick 643d0e Ups small fix --- newer commit
```
Pick the oldest commit and squash the other ones into it by editing the file and saving it like this:
```bash
pick d94e78 Fixed ABC     --- older commit
s 4e9baa Work in progress
s afb581 Working version  
s 643d0e Ups small fix --- newer commit
```
You can then write a commit message for this combined commit. Combining commits can be very powerful, **but keep in mind that this rewrites the git history. Therefore never use the rebase on a remote branch where you know that other people rely on your history.**

[More info](https://www.internalpointers.com/post/squash-commits-into-one-git)

#### Write meaningful commit messages
<img src="https://imgs.xkcd.com/comics/git_commit_2x.png" alt="drawing" width="400"/>

Commit messages should make it easy to understand what particular change the commit implements. For more complex cases it can be helpful to write more than one sentence. To do that use the commit command without the message flag:
```bash
git commit
```
your default editor will open and you can write a longer form commit message. If you don't like the default editor you can set another one with:
```bash
git config --global core.editor "vim"
```

Follow the 7 rules of a great Git commit message

1. Separate subject from body with a blank line
2. Limit the subject line to 50 characters
3. Capitalize the subject line
4. Do not end the subject line with a period
5. Use the imperative mood in the subject line
6. Wrap the body at 72 characters
7. Use the body to explain what and why vs. how

[from here](https://chris.beams.io/posts/git-commit/)

#### Visualise the git tree before you merge
In order to not cause chaos with merges, it is helpful to take a look at the git commit tree and see where you currently are with your branch and where the branch you want to merge into currently is. You can either use a software package like [Gitkraken](https://www.gitkraken.com/) or alternatively use the command-line with:
```bash
git log --graph --decorate --oneline
```
If this is too long to remember you can create a Git Alias. On Unix systems type:
```bash
vim ~/.gitconfig
```
and add the line
```
[alias]
  gr = git log --graph --decorate --oneline
```
to the file.
#### Integrate the latest changes before opening a PR
If you are on the branch `my_fix` and want to open a PR to merge into `target_branch`, double-check if in the meantime any other changes happened on `target_branch` that might cause problems. To integrate the latest changes checkout the target branch:
```bash
git checkout target_branch
git pull origin target_branch
git checkout my_fix
```
To integrate the changes you can either `rebase` or `merge`. Rebasing is the cleaner way of the two as it doesn't introduce new merge commits. It essentially replays all of your new commits in `my_fix` onto the latest commit of `target_branch`. In some cases this will not go smoothly and you'll have to fix the conflicts as the commits are applied. **Again note that the rebase will rewrite history, so only do that if you know nobody else relies on the commits that will be rewritten**.

[Merging vs. Rebasing](https://www.atlassian.com/git/tutorials/merging-vs-rebasing)
