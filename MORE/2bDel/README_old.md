# TrainingWorkshop



---



## Cloning GitHub repo to Lightning.ai Studio: Recommended approach

Create the new Studio, then use its terminal:

```bash
cd /teamspace/studios/this_studio

git clone https://github.com/tlyim/TrainingWorkshop_dev.git .remote-copy
```

Copy the repository contents, including hidden files, into the Studio root while preserving Studio metadata:

```bash
cp -a .remote-copy/. .
```

Then remove the temporary clone:

```bash
rm -rf .remote-copy
```

Verify that the Git repository is now rooted at the Studio directory:

```bash
git status
git remote -v
```

The remote should show:

```text
https://github.com/tlyim/TrainingWorkshop_dev.git
```

## Important caveat

The command:

```bash
cp -a .remote-copy/. .
```

copies the repository’s `.git` directory into the Studio root. This is what makes the Studio root itself the Git working tree. It will overwrite files with the same names, but it will **not delete extra files** already present in the Studio root.

If you want the root to match the remote exactly while preserving Lightning metadata, use `rsync` instead:

```bash
rsync -a --delete \
  --exclude='.lightning_studio/' \
  .remote-copy/ .
```

Then verify:

```bash
git status
git remote -v
```

Do not use `--delete` unless you are certain that files not present in the remote repository should be removed.

## Best option for a new Studio

If it is acceptable for the project to live in a subdirectory, the safest option is simply:

```bash
cd /teamspace/studios/this_studio
git clone https://github.com/tlyim/TrainingWorkshop_dev.git project
cd project
```

This avoids modifying the Studio root. The limitation you observed is likely a limitation of the Lightning.ai Studio creation interface: it creates the Studio filesystem first, so the repository must initially be cloned into a directory inside it. Git itself does not require the repository to be cloned directly into the Studio root.

If the project must occupy the root, cloning to a temporary subdirectory and moving/copying the contents as above is a valid workaround.