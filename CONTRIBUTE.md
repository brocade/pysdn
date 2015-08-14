# Contribute
If you want to contribute source code to pybvc then please read this document, it describes how to
contribute your code to pybvc.

## Why
Why would you want to contribute source code?
- You have a bug fix
- You have a new feature
- You have some ideas

## Will my contribution be accepted by the maintainer
Typically the answer to this question is, 'it depends':
- If you contribute a bug fix it is likely to be accepted ( create an issue first to be sure it is a bug and not already being worked on )
- If you contribute a new feature it may be accepted if it matches the goal of the project ( talk to us first )
- If you have ideas of a better way to write this project it may not be accepted ( talk to us first )

## How do I contribute (now that I have talked to you guys...or my change is small and I am sure you will accept it):

1. We use the Fork & Pull methdology for pull requests as described here:  https://help.github.com/articles/using-pull-requests/
    1. There is a good beginner video (by Ashley Grant) here as well: https://www.youtube.com/watch?v=M7ZYkjOWr6g
1. Fork this repository.
    1. Go to this repository's home page in Github and then in the top right corner find the 'Fork' button and click it.
1. Go to the newly forked repository's home page (in your Github account) and get its clone URL (on right margin)
1. On your laptop open a command window and clone your fork of the project
```bash
git clone <clone url of your fork of the project>
```
1. Change into the directory created
1. Set your local repo to track the original repository
```bash
git remote add upstream <clone url for the original project>
```
1. Never, Never, NEVER make changes in this master branch on your laptop.  It will always be your copy of the original project and never have changes you make.  You will make your changes in feature branches.  You may have only one feature branch or you may have multiples, depending on how many changes you are going to request be made to the original project.
1. Create a feature branch for each feature you will ask to be made to the original project.  For instance if you have a two bug fixes and a new feature then it would be cleanest to put each of those into its own feature branch.  That way if one of your pull requests takes a long time to resolve and get into the original project the other ones can still get in quickly.
```bash
git checkout -b <name of your feature branch>
```
1. That command will create the branch and move you into that branch.  Always double check which branch you are in...to avoid making changes in the wrong branch.
```bash
git branch
```
1. Send the new (local) feature branch to Github and connect that (remote) feature branch to this local branch
```bash
git push --all -u
```
1. If you are in the correct feature branch, then go ahead and make the changes to the source files that you want to make.
    1. Feel free to inform git about your changes to your local feature branch
    ```bash
    git add <filename>
    ```
    1. Feel free to commit your changes to your local feature branch
    ```bash
    git commit -m "A reasonable sentence describing your changes"
    ```
    1. Feel free to push your changes to your remote feature branch
    ```bash
    git push
    ```
1. Once you are happy with your changes run the unit tests to validate the system continues to work correctly (unit tests coming soon)
1. Once the unit tests work add, commit and push all your changes to your remote feature branch (see above)
1. Once all your changes are pushed you are ready to do a pull request 
1. Open your browser and go to your fork of the project (not the original), find your feature branch and do a compare and pull request
1. If the pull request is able to be merged automatically then go ahead and create the pull request
1. IF the pull request cannot be merged automatically then see 'How do I rebase?' below and then come back here and try again.


## How do I rebase?
1. Sometimes your pull request will be responded to with 'please rebase and try again'.  Basically this means that other changes (pull requests) have slipped in front of you and your request can no longer be merged automatically.  This section describes how to do this.
1. This works only if you Never, Never, NEVER make changes in your fork's master branch and only make changes in the feature branches.
1. In your console window in the forked project, change to the 'master' branch.
```bash
git checkout master
```
1. Now, 'rebase' your master to the upstream master branch of the original project (not your fork).  This basically will make your local master branch match exactly what is on the remote master of the original project.
```bash
git pull --rebase upstream master
```
1. Now, change back to your feature branch
``bash
git checkout <feature branch name>
```
1. Rebase your feature branch to your local master branch.  This will make your feature branch identical to your local master branch and then replay all of the changes you made on your feature branch on top of this.
```bash
git rebase master
```
1. Check the output of the last command.  Did you get CONFLICT messages?  If yes, then you need to open the files that had CONFLICT, look at them and figure out how to merge the conflicts.  The conflicts will be marked in the files.  The CONFLICT areas will begin with <<<<< and end with >>>>  In between these will be your original text and the text from the current project.   
1. Once you resolve all the conflicts and run the unit tests (coming soon)
1. Inform git about all the files you changed by doing a git add for each
```bash
git add <filename of files changed>
```
1. Let git know that you have completed fixing the CONFLICT and it should continue the rebase
```bash
git rebase --continue
```
1. Force push your changes
```bash
git push --force
```
1. You have rebased.  Go back to the previous section and try sending your pull again.

