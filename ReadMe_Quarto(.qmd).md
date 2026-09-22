To render self-contained reveal.js-based html slides, use a command like the below:

```bash
quarto render Wk01_TheAnswer.qmd --to revealjs -M embed-resources:true
```

---

To install Quarto in the virtual Linux pc on Codespaces, 

- create a folder called `Downloads`
- open the terminal and run the commands below:

```bash
cd Downloads    # change to the folder Downloads

# Use wget to download the package file 
wget https://github.com/quarto-dev/quarto-cli/releases/download/v1.8.27/quarto-1.8.27-linux-amd64.deb

# Install the package using dpkg (requires sudo privileges):
sudo dpkg -i quarto-1.8.27-linux-amd64.deb

# If the installation reports missing dependencies, fix them with:
sudo apt-get install -f
```

After installation, you can verify by running `quarto --version`. If you encounter issues, ensure your system is up-to-date with `sudo apt update && sudo apt upgrade`.
