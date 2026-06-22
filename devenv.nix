{ pkgs, ... }:

{
  languages.python = {
    enable = true;
    package = pkgs.python312;
    venv = {
      enable = true;
      requirements = ./requirements.txt;
    };
  };

  packages = [ pkgs.git ];

  env.WIKI_CACHE_DIR = ".cache";

  enterShell = ''
    if ! python -c "import en_core_web_sm" >/dev/null 2>&1; then
      echo "Downloading spaCy en_core_web_sm model..."
      python -m spacy download en_core_web_sm
    fi
  '';

  scripts.wiki-build.exec = ''python3 build_graph.py "$@"'';
  scripts.wiki-serve.exec = ''python3 server.py "$@"'';
  scripts.wiki-test.exec  = ''python3 -m pytest tests/ "$@"'';
}
