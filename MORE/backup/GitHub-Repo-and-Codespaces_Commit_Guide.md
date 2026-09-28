# GitHub Repo and Codespaces: Stage, Commit and Push Guide

## The concepts

To 'save' your work during the module, you need to understand the process of "saving" between Codespaces and your GitHub repo.

In essence:

- GitHub is where you **permanently save** your code (and data if it is relatively small)
- Codespaces is where you **do** your coding

To understand the steps in the 'saving' process between GitHub and Codespaces, you need to understand that these systems differentiate between:

- *Staging*: Selecting which specific file changes you intend to include in the next commit. *Commit*: Recording the staged files permanently into the local Git history, together with a descriptive message explaining the change.
- *Sync*: Transferring the committed changes from your Codespaces environment and the GitHub repository, ensuring both copies remain consistent.

These are sequential processes:

- Stage → Commit → Sync

In terms of file management, it helps to understand several differences between the two tools:

| | **GitHub** | **Codespaces** |
|---|---|---|
| **Concept** | Where you save your work, and record the 'audit trail' of the changes you made to it | The place where you will "do" your coding |
| **Storage capability** | Your **permanent** store for your work | Offers a **temporary** means of storing changes prior to saving them to GitHub |
| **What happens if I leave my Codespace idle for an extended period of time, or I merely close the browser tab where my Codespace sits in (but without taking an action to delete the Codespace)?** | No impact to the files in the repository | Your Codespace will go into sleep and may be reactivated at any time to resume the same state it was in when it went to sleep, including any changes that have not been committed or synced to the GitHub repo.<br><br>However, GitHub will automatically delete Codespaces in sleep after they have not been active for a number of days. Leaving changed files in a Codespace without committing and syncing them to the GitHub repo risks losing them permanently. Your files in the GitHub repo before those changes will remain untouched, even after those changes are lost. |
| **What happens if I delete the Codespace I was working on?** | All the files you have synchronised to GitHub are preserved | Some work may be lost if it wasn't synchronised to GitHub. |
| **Where is the content 'stored'?** | In the cloud | In the cloud |

## How to Commit and Sync your files

1. When you make changes to a file, you will see a blue dot on the **Source Control** icon (on the left-hand side menu).
2. Click on the **Source Control** icon to see which files have been changed.
3. Under **Changes**, it will display those files which have been changed and are waiting for you to select them to be committed to GitHub.
4. Select the file(s) that you want to save.
5. Type a message in the text field above the blue **Commit** button.
6. Press the blue **Commit** button, and click **Yes** on the pop-up message that will appear.
7. To 'save' the file back to GitHub, you **also** then need to press the blue **Sync Changes** button in the **Source Control** panel. Then click **OK** in the pop-up message that appears.
8. You should then see that the blue dot has disappeared from the **Source Control** icon to show that your Commit has been synchronised to GitHub.
9. You can then go back to your GitHub repo Files page to check that the repo has been updated.

## Multiple files

The difference between Staging and Committing will make more sense when you start working with multiple files at a time.

Having got the hang of committing one file, you can explore staging by creating two test files in a new temporary folder in your Codespace. Then play around with selecting only one file to stage at a time (using the '+' icon next to the file name in the **Source Control** list), then selecting **Commit & Sync** from the drop-down menu of the blue **Commit** button to just Commit that file.
