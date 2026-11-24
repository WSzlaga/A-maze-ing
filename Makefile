PYTHON = python3

.PHONY: install run debug build clean fclean lint

install:
	$(PYTHON) -m pip install flake8 mypy build

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

build:
	$(PYTHON) -m build

clean:
	rm -rf .mypy_cache
	find . -type d -name "__pycache__" -exec rm -rf {} +

fclean: clean
	rm -rf build dist *.egg-info mazegen.egg-info
	rm -f maze.txt

lint:
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs