# dancesWithMachines

This is the source of [dancesWithMachines](dancesWithMachines.github.io) web page. The website is
build with Jekyll.

## License

This website is build with [Jekyll](https://jekyllrb.com/docs/) and the theme used is
[Serial Programmer](https://github.com/sharadcodes/jekyll-theme-serial-programmer) developed by
[Sharad Raj](https://github.com/sharadcodes) licensed under MIT license. License can be found in the
root of this repository.

Content of this website is the property of Mateusz Kusiak (Timax).

## Setting up local env

Note: This is handled by ansible automation.

### Installing ruby (Debian)

To install newest ruby, run the following commands.

```bash
sudo apt update
sudo apt install ruby-full
```

Check the ruby version via...

```bash
ruby -v
```

### Setting up PATH

Ruby installs gem locally at `/home/<user>/.local/share/gem/ruby/`, therefore the following needs to
be added to
`~/.bashrc` or `~/.zshrc`.:

```bash
export GEM_HOME="$(ruby -e 'print Gem.user_dir')"
export PATH="$GEM_HOME/bin:$PATH"
```

## Running locally

### Installing dependencies (gems)

Install project dependencies:

```bash
bundle install
```

If there are issues with installing gems (eg. outdated), run the following to update gems versions
to the newest.

```bash
bundle update
```

### Run server locally

Run the following command to start server locally for development.

```bash
bundle exec jekyll serve --livereload
```


## Styling

Here are few rules for post styling:

- No headers is fine for short posts;
- Use headers H2 and up, the biggest header should be post title;
- (Only) H2 headers should be followed by horizontal rule;
