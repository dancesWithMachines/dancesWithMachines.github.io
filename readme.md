# dancesWithMachines

This is the source of [dancesWithMachines](dancesWithMachines.github.io) web page. The website is build with Jekyll.

## License

This website is build with [Jekyll](https://jekyllrb.com/docs/) and the theme used is [Serial Programmer](https://github.com/sharadcodes/jekyll-theme-serial-programmer) developed by [Sharad Raj](https://github.com/sharadcodes) licensed under MIT license. License can be found in the root of this repository.

Content of this website is the property of Mateusz Kusiak (Timax).

## Building

### Installing ruby 3.0.0 (Mac)

1. Install ruby 3.0 via homebrew.
   ```bash
   brew install ruby@3.0
   ```
   Note: MacOS comes with ruby preinstalled, but messing with default instance is not advised.
2. Add ruby path to `~/.bash_profile` (if using bash).
   ```bash
   # CUSTOM - Use brew provided ruby 3.0
   export PATH="/opt/homebrew/opt/ruby@3.0/bin:$PATH"
   ```
3. Source `~/.bash_profile`.
   ```bash
   source ~/.bash_profile
   ```
4. Install Jekyll and Bundler.
   ```bash
   gem install bundler jekyll
   ```

### Build and run the website locally

1. Download source files and go to the root of downloaded contents.
2. Install dependencies.
   ```bash
   bundle install
   ```
   Note: `webrick` might need to be installed manually.
   ```bash
   gem install webrick
   ```
3. Build and serve the website.
   ```bash
   bundle exec jekyll serve --livereload
   ```

## Styling

Here are few rules for post styling:

- No headers is fine for short posts;
- Use headers H2 and up, the biggest header should be post title;
- (Only) H2 headers should be followed by horizontal rule;
