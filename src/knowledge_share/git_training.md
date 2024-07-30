Git Training Session: Understanding Pull, Push, Fetch, and Branches

Introduction

Welcome to our Git training session! Today, we'll demystify some fundamental Git concepts: git pull, git push, git fetch, and the differences between local and remote branches. To make things easier, we'll use the analogy of a shared folder (remote repository) and your local PC (local repository).


The Basics of Git
Before diving into specific commands, let's recap what Git is:

Git: A version control system to track changes in your code.

Repository: A storage location for your code.

Local Repository: The copy of the repository on your local machine.

Remote Repository: The copy of the repository on a server (like GitHub, GitLab, etc.).

## Differences Between Local and Remote Branches
Local Branch: Your personal workspace where you can make changes without affecting others. Like a folder on your PC.
Remote Branch: The shared workspace where everyone's changes are stored. Like a shared folder on a network drive.

Understanding Branches
Local Branch: This is like a personal workspace on your PC where you make changes.

Remote Branch: This is like a shared folder on a server where everyone shares their changes.

Commands Overview


### git pull: Updates your local branch with changes from the remote branch.
Analogy: You check the shared folder for any updates your team members have added, and you copy those updates to your local folder.
Imagine two Windows Explorer windows side by side:

Left Window (Shared Folder - Remote Repository):

| Shared Folder   |
|-----------------|
| File1.txt       |
| File2.txt       |
| File3.txt       | <- New file added by a team member

Right Window (My PC - Local Repository):

| My Local Folder |
|-----------------|
| File1.txt       |
| File2.txt       |

After running git pull, the right window (local folder) updates to match the left window (shared folder):

Right Window (My PC - Local Repository):


| My Local Folder |
|-----------------|
| File1.txt       |
| File2.txt       |
| File3.txt       | <- Newly pulled file



### git push: Sends your local changes to the remote branch. AKA Sharing Your Changes
Analogy: You’ve made some changes in your local folder and now you want to share them with the team by updating the shared folder.
Example: git push origin main

Again, imagine two Windows Explorer windows side by side:

Left Window (Shared Folder - Remote Repository):

| Shared Folder   |
|-----------------|
| File1.txt       |
| File2.txt       |

Right Window (My PC - Local Repository):

| My Local Folder |
|-----------------|
| File1.txt       |
| File2.txt       |
| File3.txt       | <- New file I added

After running git push, the left window (shared folder) updates to match the right window (local folder):

Left Window (Shared Folder - Remote Repository):

| Shared Folder   |
|-----------------|
| File1.txt       |
| File2.txt       |
| File3.txt       | <- Newly pushed file


### git fetch: Gets the latest changes from the remote branch but doesn’t merge them into your local branch. AKA Checking for Updates
Analogy: Similar to refreshing a Windows folder to see what new files have been added, but without actually opening or copying those files into your folder. It updates your view of the remote repository without altering your local files.
Example: git fetch origin


git fetch
Imagine the same two Windows Explorer windows:

Visual for git fetch as a Folder Refresh
Imagine you have two Windows Explorer windows:

Left Window (Shared Folder - Remote Repository):

| Shared Folder   |
|-----------------|
| File1.txt       |
| File2.txt       |
| File3.txt       | <- New file added by a team member

Right Window (My PC - Local Repository Before Fetch):



| My Local Folder |
|-----------------|
| File1.txt       |
| File2.txt       |

After running git fetch, it's like your local folder has an internal note about the new file in the shared folder:

Right Window (My PC - Local Repository After Fetch):

|            My Local Folder            |
|---------------------------------------|
| File1.txt                             |
| File2.txt                             |
| (Aware of File3.txt in Shared Folder) |

However, git fetch updates your local repository's metadata to know about the new file in the remote repository. This isn't shown in the file explorer but is important for your Git operations.



Visuals for Git Commands





Additional Visuals for Branches
Local and Remote Branches
Remote Repository:


| Remote Repository        |
|--------------------------|
| main                     |
| feature/new-feature      |

Local Repository:




| Local Repository         |
|--------------------------|
| main                     |
| feature/new-feature      |

Each branch is like a different version of your project. You can switch between them, and they might contain different files or versions of files.

Putting It All Together
Start:

Your local and remote repositories are in sync.
Fetch:

You learn about changes in the remote repository without applying them.
Pull:

You apply those changes to your local repository.
Push:

You send your local changes to the remote repository.
